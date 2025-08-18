# sdk/python/kei_agent/security_manager.py
"""
Security Manager für KEI-Agent SDK.

Implementiert Authentifizierung, Token-Management und Sicherheits-Features
für die KEI-Agent SDK mit Enterprise-Grade Security.
"""

from __future__ import annotations

import asyncio
import time
from typing import Dict, Optional, Any
import logging

import httpx

from protocol_types import SecurityConfig, AuthType
from exceptions import SecurityError

# Initialisiert Modul-Logger
_logger = logging.getLogger(__name__)


class SecurityManager:
    """Verwaltet Authentifizierung und Sicherheits-Features für KEI-Agent.

    Unterstützt Bearer Token, OIDC und mTLS Authentifizierung mit automatischer
    Token-Erneuerung und Caching für Enterprise-Einsatz.

    Attributes:
        config: Sicherheitskonfiguration
        _token_cache: Cache für Authentifizierungs-Token
        _token_refresh_task: Background-Task für Token-Erneuerung
        _refresh_lock: Lock für Thread-sichere Token-Erneuerung
    """

    def __init__(self, config: SecurityConfig) -> None:
        """Initialisiert Security Manager.

        Args:
            config: Sicherheitskonfiguration

        Raises:
            SecurityError: Bei ungültiger Konfiguration
        """
        try:
            config.validate()
        except ValueError as e:
            raise SecurityError(f"Ungültige Sicherheitskonfiguration: {e}") from e

        self.config = config
        self._token_cache: Dict[str, Any] = {}
        self._token_refresh_task: Optional[asyncio.Task] = None
        self._refresh_lock = asyncio.Lock()

        _logger.info(
            "Security Manager initialisiert",
            extra={
                "auth_type": config.auth_type,
                "rbac_enabled": config.rbac_enabled,
                "audit_enabled": config.audit_enabled,
            },
        )

    async def get_auth_headers(self) -> Dict[str, str]:
        """Erstellt Authentifizierungs-Headers für HTTP-Requests.

        Returns:
            Dictionary mit Authentifizierungs-Headers

        Raises:
            SecurityError: Bei Authentifizierungsfehlern
        """
        try:
            if self.config.auth_type == AuthType.BEARER:
                return await self._get_bearer_headers()
            elif self.config.auth_type == AuthType.OIDC:
                return await self._get_oidc_headers()
            elif self.config.auth_type == AuthType.MTLS:
                return await self._get_mtls_headers()
            else:
                raise SecurityError(f"Unbekannter Auth-Typ: {self.config.auth_type}")

        except Exception as e:
            _logger.error(
                "Fehler beim Erstellen der Auth-Headers",
                extra={"error": str(e), "auth_type": self.config.auth_type},
            )
            raise SecurityError(f"Auth-Header-Erstellung fehlgeschlagen: {e}") from e

    async def _get_bearer_headers(self) -> Dict[str, str]:
        """Erstellt Bearer Token Headers.

        Returns:
            Headers mit Bearer Token

        Raises:
            SecurityError: Wenn kein API Token konfiguriert ist
        """
        if not self.config.api_token:
            raise SecurityError(
                "API Token ist erforderlich für Bearer-Authentifizierung"
            )

        return {"Authorization": f"Bearer {self.config.api_token}"}

    async def _get_oidc_headers(self) -> Dict[str, str]:
        """Erstellt OIDC Token Headers mit automatischer Token-Erneuerung.

        Returns:
            Headers mit OIDC Access Token

        Raises:
            SecurityError: Bei OIDC-Token-Abruf-Fehlern
        """
        token = await self._get_oidc_token()
        return {"Authorization": f"Bearer {token}"}

    async def _get_mtls_headers(self) -> Dict[str, str]:
        """Erstellt mTLS Headers (Transport-Ebene, keine Auth-Headers).

        Returns:
            Leeres Dictionary (mTLS wird auf Transport-Ebene gehandhabt)
        """
        # mTLS wird auf Transport-Ebene gehandhabt, keine speziellen Headers
        return {}

    async def _get_oidc_token(self) -> str:
        """Ruft OIDC Access Token ab mit Caching und automatischer Erneuerung.

        Returns:
            OIDC Access Token

        Raises:
            SecurityError: Bei Token-Abruf-Fehlern
        """
        async with self._refresh_lock:
            # Prüfe Cache
            cached_token = self._token_cache.get("oidc_token")
            if cached_token and not self._is_token_expired(cached_token):
                return cached_token["access_token"]

            # Token erneuern
            try:
                token_data = await self._fetch_oidc_token()
                self._cache_token("oidc_token", token_data)
                return token_data["access_token"]

            except Exception as e:
                raise SecurityError(f"OIDC Token-Abruf fehlgeschlagen: {e}") from e

    async def _fetch_oidc_token(self) -> Dict[str, Any]:
        """Ruft neuen OIDC Token vom Identity Provider ab.

        Returns:
            Token-Response vom OIDC Provider

        Raises:
            SecurityError: Bei HTTP-Fehlern oder ungültiger Response
        """
        if not all(
            [
                self.config.oidc_issuer,
                self.config.oidc_client_id,
                self.config.oidc_client_secret,
            ]
        ):
            raise SecurityError("OIDC-Konfiguration unvollständig")

        token_endpoint = f"{self.config.oidc_issuer}/token"

        data = {
            "grant_type": "client_credentials",
            "client_id": self.config.oidc_client_id,
            "client_secret": self.config.oidc_client_secret,
            "scope": self.config.oidc_scope,
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(token_endpoint, data=data)
                response.raise_for_status()

                token_data = response.json()

                # Validiere Token-Response
                if "access_token" not in token_data:
                    raise SecurityError("Ungültige Token-Response: access_token fehlt")

                return token_data

            except httpx.HTTPStatusError as e:
                raise SecurityError(
                    f"OIDC Token-Request fehlgeschlagen: {e.response.status_code}"
                ) from e
            except httpx.RequestError as e:
                raise SecurityError(f"OIDC Token-Request Netzwerkfehler: {e}") from e

    def _cache_token(self, key: str, token_data: Dict[str, Any]) -> None:
        """Cached Token mit Ablaufzeit.

        Args:
            key: Cache-Schlüssel
            token_data: Token-Daten vom Provider
        """
        expires_in = token_data.get("expires_in", self.config.token_cache_ttl)
        # Puffer für Erneuerung, aber mindestens 10 Sekunden Cache-Zeit
        buffer_time = min(
            60, max(10, expires_in // 4)
        )  # Max 60s, min 10s, oder 25% der Laufzeit
        expires_at = time.time() + expires_in - buffer_time

        self._token_cache[key] = {
            **token_data,
            "expires_at": expires_at,
            "cached_at": time.time(),
        }

        _logger.debug(
            "Token gecacht",
            extra={"key": key, "expires_in": expires_in, "expires_at": expires_at},
        )

    def _is_token_expired(self, token_data: Dict[str, Any]) -> bool:
        """Prüft ob Token abgelaufen ist.

        Args:
            token_data: Gecachte Token-Daten

        Returns:
            True wenn Token abgelaufen ist
        """
        expires_at = token_data.get("expires_at", 0)
        return time.time() >= expires_at

    async def start_token_refresh(self) -> None:
        """Startet automatische Token-Erneuerung im Hintergrund.

        Nur für OIDC-Authentifizierung mit aktivierter Token-Erneuerung.
        """
        if not self.config.requires_refresh():
            _logger.debug("Token-Refresh nicht erforderlich")
            return

        if self._token_refresh_task and not self._token_refresh_task.done():
            _logger.debug("Token-Refresh bereits aktiv")
            return

        self._token_refresh_task = asyncio.create_task(self._token_refresh_loop())
        _logger.info("Token-Refresh gestartet")

    async def stop_token_refresh(self) -> None:
        """Stoppt automatische Token-Erneuerung."""
        if self._token_refresh_task and not self._token_refresh_task.done():
            self._token_refresh_task.cancel()
            try:
                await self._token_refresh_task
            except asyncio.CancelledError:
                pass
            _logger.info("Token-Refresh gestoppt")

    async def _token_refresh_loop(self) -> None:
        """Background-Loop für automatische Token-Erneuerung."""
        refresh_interval = self.config.token_cache_ttl // 2  # Erneuere bei halber TTL

        while True:
            try:
                await asyncio.sleep(refresh_interval)

                # Erneuere Token wenn nötig
                if self.config.auth_type == AuthType.OIDC:
                    await self._get_oidc_token()

            except asyncio.CancelledError:
                break
            except Exception as e:
                _logger.error(
                    "Fehler bei automatischer Token-Erneuerung", extra={"error": str(e)}
                )
                # Warte vor erneutem Versuch
                await asyncio.sleep(60)

    def get_security_context(self) -> Dict[str, Any]:
        """Gibt aktuellen Sicherheitskontext zurück.

        Returns:
            Dictionary mit Sicherheitsinformationen
        """
        return {
            "auth_type": self.config.auth_type,
            "rbac_enabled": self.config.rbac_enabled,
            "audit_enabled": self.config.audit_enabled,
            "token_refresh_enabled": self.config.token_refresh_enabled,
            "cached_tokens": list(self._token_cache.keys()),
            "refresh_task_active": self._token_refresh_task is not None
            and not self._token_refresh_task.done(),
        }


__all__ = ["SecurityManager"]
