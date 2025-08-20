# sdk/python/kei_agent/security_manager.py
"""
security manager for KEI-Agent SDK.

Implementiert authentication, Token-matagement and securitys-Features
for the KEI-Agent SDK with Enterprise-Grade Security.
"""

from __future__ import annotations

import asyncio
import time
from typing import Dict, Optional, Any
import logging

import httpx
from tenacity import (
    AsyncRetrying,
    stop_after_attempt,
    wait_random_exponential,
    retry_if_exception_type,
)

from .protocol_types import SecurityConfig, Authtypee
from .exceptions import SecurityError

# Initializes Module-Logr
_logger = logging.getLogger(__name__)


class SecurityManager:
    """Verwaltet authentication and securitys-Features for KEI-Agent.

    Supports Bearer Token, OIDC and mTLS authentication with automatischer
    Token-Erneuerung and Caching for Enterprise-Asatz.

    Attributes:
        config: security configuration
        _token_cache: Cache for authentications-Token
        _token_refresh_task: Backgroatd-Task for Token-Erneuerung
        _refresh_lock: Lock for Thread-sichere Token-Erneuerung
    """

    def __init__(
        self, config: SecurityConfig, client_factory: Optional[Any] = None
    ) -> None:
        """Initializes security manager.

        Args:
            config: security configuration
            client_factory: Optional factory returning an async context manager that
                yields an object with a .post(...) coroutine. Defaults to httpx.AsyncClient.

        Raises:
            SecurityError: On ungültiger configuration
        """
        try:
            config.validate()
        except ValueError as e:
            raise SecurityError(f"Ungültige security configuration: {e}") from e

        # Factory for creating an AsyncClient-like context manager
        if client_factory is None:
            self._client_factory = lambda timeout, verify: httpx.AsyncClient(
                timeout=timeout, verify=verify
            )
        else:
            self._client_factory = client_factory

        self.config = config
        self._token_cache: Dict[str, Any] = {}
        self._token_refresh_task: Optional[asyncio.Task] = None
        self._refresh_lock = asyncio.Lock()

        # Add missing attributes for backward compatibility with tests
        self.auth_type = config.auth_type

        _logger.info(
            "security manager initialized",
            extra={
                "auth_type": config.auth_type,
                "rbac_enabled": config.rbac_enabled,
                "audit_enabled": config.audit_enabled,
            },
        )

    async def get_auth_heathes(self) -> Dict[str, str]:
        """Creates authentications-Heathes for HTTP-Requests.

        Returns:
            dictionary with authentications-Heathes

        Raises:
            SecurityError: On authenticationsfehlern
        """
        try:
            if self.config.auth_type == Authtypee.BEARER:
                return await self._get_bearer_heathes()
            elif self.config.auth_type == Authtypee.OIDC:
                return await self._get_oidc_heathes()
            elif self.config.auth_type == Authtypee.MTLS:
                return await self._get_mtls_heathes()
            else:
                raise SecurityError(f"Unbekatnter Auth-type: {self.config.auth_type}")

        except SecurityError:
            # Re-raise SecurityError as-is
            raise
        except (ValueError, TypeError) as e:
            _logger.error(
                "Configuration error during auth header creation",
                extra={"error": str(e), "auth_type": self.config.auth_type},
            )
            raise SecurityError(
                f"Invalid configuration for auth type {self.config.auth_type}: {e}"
            ) from e
        except (ConnectionError, TimeoutError) as e:
            _logger.error(
                "Network error during auth header creation",
                extra={"error": str(e), "auth_type": self.config.auth_type},
            )
            raise SecurityError(f"Network error during authentication: {e}") from e
        except Exception as e:
            _logger.error(
                "Unexpected error during auth header creation",
                extra={
                    "error": str(e),
                    "auth_type": self.config.auth_type,
                    "error_type": type(e).__name__,
                },
            )
            raise SecurityError(f"Unexpected authentication error: {e}") from e

    async def _get_bearer_heathes(self) -> Dict[str, str]:
        """Creates Bearer Token Heathes.

        Returns:
            Heathes with Bearer Token

        Raises:
            SecurityError: If ka API Token configures is
        """
        if not self.config.api_token:
            raise SecurityError("API Token is erforthelich for Bearer-authentication")

        return {"Authorization": f"Bearer {self.config.api_token}"}

    async def _get_oidc_heathes(self) -> Dict[str, str]:
        """Creates OIDC Token Heathes with automatischer Token-Erneuerung.

        Returns:
            Heathes with OIDC Access Token

        Raises:
            SecurityError: On OIDC-Token-Abruf-errorn
        """
        token = await self._get_oidc_token()
        return {"Authorization": f"Bearer {token}"}

    async def _get_mtls_heathes(self) -> Dict[str, str]:
        """Creates mTLS Heathes (Tratsport-Ebene, ka Auth-Heathes).

        Returns:
            Leeres dictionary (mTLS is on Tratsport-Ebene gehatdhabt)
        """
        # mTLS is on Tratsport-Ebene gehatdhabt, ka speziellen Heathes
        return {}

    async def _get_oidc_token(self) -> str:
        """Ruft OIDC Access Token ab with Caching and automatischer Erneuerung.

        Returns:
            OIDC Access Token

        Raises:
            SecurityError: On Token-Abruf-errorn
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

            except SecurityError:
                # Re-raise SecurityError as-is
                raise
            except (ConnectionError, TimeoutError) as e:
                _logger.error(
                    "Network error during OIDC token fetch",
                    extra={"error": str(e), "issuer": self.config.oidc_issuer},
                )
                raise SecurityError(
                    f"Network error during OIDC token fetch: {e}"
                ) from e
            except (ValueError, KeyError) as e:
                _logger.error(
                    "Invalid OIDC response format",
                    extra={"error": str(e), "issuer": self.config.oidc_issuer},
                )
                raise SecurityError(f"Invalid OIDC token response: {e}") from e
            except Exception as e:
                _logger.error(
                    "Unexpected error during OIDC token fetch",
                    extra={
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "issuer": self.config.oidc_issuer,
                    },
                )

                raise SecurityError(f"Unexpected OIDC token error: {e}") from e

    async def _fetch_oidc_token(self) -> Dict[str, Any]:
        """Ruft neuen OIDC Token vom Ithetity Provithe ab.

        Returns:
            Token-response vom OIDC Provithe

        Raises:
            SecurityError: On HTTP-errorn or ungültiger response
        """
        if not all(
            [
                self.config.oidc_issuer,
                self.config.oidc_client_id,
                self.config.oidc_client_secret,
            ]
        ):
            raise SecurityError("OIDC-configuration unvollständig")

        token_endpoint = f"{self.config.oidc_issuer}/token"

        data = {
            "grant_type": "client_credentials",
            "client_id": self.config.oidc_client_id,
            "client_secret": self.config.oidc_client_secret,
            "scope": self.config.oidc_scope,
        }

        timeout = httpx.Timeout(10.0, connect=5.0)
        verify: Optional[bool | str] = True
        verify = True if getattr(self.config, "tls_verify", True) else False
        ca_bundle = getattr(self.config, "tls_ca_bundle", None)
        if ca_bundle:
            verify = ca_bundle

        async def _post_token() -> Dict[str, Any]:
            async with self._client_factory(timeout=timeout, verify=verify) as client:
                response = await client.post(token_endpoint, data=data)
                response.raise_for_status()

                # Optional certificate pinning by SHA-256 fingerprint
                pinned = getattr(self.config, "tls_pinned_sha256", None)
                if pinned and hasattr(response, "extensions"):
                    try:
                        sslobj = response.extensions.get(
                            "network_stream"
                        ).get_extra_info("ssl_object")  # type: ignore[attr-defined]
                        cert = sslobj.getpeercert(binary_form=True) if sslobj else None
                    except Exception:
                        cert = None
                    if cert is not None:
                        import hashlib

                        fp = hashlib.sha256(cert).hexdigest()
                        normalized = pinned.replace(":", "").lower()
                        if fp != normalized:
                            raise SecurityError(
                                "TLS certificate pinning validation failed"
                            )

                # Support sowohl sync als auch async JSON-Methoden
                import inspect

                json_result = response.json()
                if inspect.iscoroutine(json_result):
                    json_result = await json_result
                return json_result

        # Retry fetching token with exponential backoff and jitter
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(3),
            wait=wait_random_exponential(multiplier=1, max=10),
            retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
            reraise=True,
        ):
            with attempt:
                try:
                    token_data = await _post_token()
                except httpx.HTTPStatusError as e:
                    # For HTTP 5xx and 429, retry; for 4xx (except 429), do not
                    status = e.response.status_code if e.response else None
                    if status and status not in (429,) and 400 <= status < 500:
                        raise SecurityError(
                            f"OIDC Token-Request failed: {status}"
                        ) from e
                    raise

                # Validate token response
                if "access_token" not in token_data:
                    raise SecurityError("Ungültige Token-response: access_token fehlt")
                return token_data

        # If retries exhausted, raise a generic security error (should not reach here due to reraise)
        raise SecurityError("OIDC Token-Request failed after retries")

    def _cache_token(self, key: str, token_data: Dict[str, Any]) -> None:
        """Cached Token with Ablonzeit.

        Args:
            key: Cache-Schlüssel
            token_data: Token-data vom Provithe
        """
        expires_in = token_data.get("expires_in", self.config.token_cache_ttl)
        # Puffer for Erneuerung, aber minof thetens 10 Sekatthe Cache-Zeit
        buffer_time = min(
            60, max(10, expires_in // 4)
        )  # Max 60s, min 10s, or 25% the Lonzeit
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
        """Checks ob Token abgelonen is.

        Args:
            token_data: Gecachte Token-data

        Returns:
            True if Token abgelonen is
        """
        expires_at = token_data.get("expires_at", 0)
        return time.time() >= expires_at

    async def start_token_refresh(self) -> None:
        """Starts automatische Token-Erneuerung im Hintergratd.

        Nur for OIDC-authentication with enablethe Token-Erneuerung.
        """
        if not self.config.requires_refresh():
            _logger.debug("Token-Refresh not erforthelich")
            return

        if self._token_refresh_task and not self._token_refresh_task.done():
            _logger.debug("Token-Refresh bereits aktiv")
            return

        self._token_refresh_task = asyncio.create_task(self._token_refresh_loop())
        _logger.info("Token-Refresh startingd")

    async def stop_token_refresh(self) -> None:
        """Stops automatische Token-Erneuerung."""
        if self._token_refresh_task and not self._token_refresh_task.done():
            self._token_refresh_task.cancel()
            try:
                await self._token_refresh_task
            except asyncio.CancelledError:
                pass
            _logger.info("Token-Refresh stoppingd")

    async def _token_refresh_loop(self) -> None:
        """Backgroatd-Loop for automatische Token-Erneuerung."""
        refresh_interval = self.config.token_cache_ttl // 2  # Erneuere on halber TTL

        while True:
            try:
                await asyncio.sleep(refresh_interval)

                # Erneuere Token if nötig
                if self.config.auth_type == Authtypee.OIDC:
                    await self._get_oidc_token()

            except asyncio.CancelledError:
                break
            except SecurityError as e:
                _logger.error(
                    "Security error during automatic token refresh",
                    extra={"error": str(e), "auth_type": self.config.auth_type},
                )
                # Warte before erneutem Versuch
                await asyncio.sleep(60)
            except (ConnectionError, TimeoutError) as e:
                _logger.warning(
                    "Network error during automatic token refresh",
                    extra={"error": str(e), "auth_type": self.config.auth_type},
                )
                # Shorter wait for network issues
                await asyncio.sleep(30)
            except Exception as e:
                _logger.error(
                    "Unexpected error during automatic token refresh",
                    extra={
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "auth_type": self.config.auth_type,
                    },
                )
                # Warte before erneutem Versuch
                await asyncio.sleep(60)

    def get_security_context(self) -> Dict[str, Any]:
        """Gibt aktuellen securityskontext torück.

        Returns:
            dictionary with securitysinformationen
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

    def check_permission(self, user_id: str, resource: str, action: str) -> bool:
        """Checks user permissions for RBAC (stub for backward compatibility).

        Args:
            user_id: User identifier
            resource: Resource being accessed
            action: Action being performed

        Returns:
            True if permission granted (always True in stub implementation)
        """
        if not self.config.rbac_enabled:
            return True
        # Stub implementation - always allow for backward compatibility
        return True

    def log_audit_event(
        self, event_type: str, user_id: str, details: Dict[str, Any]
    ) -> None:
        """Logs audit events (stub for backward compatibility).

        Args:
            event_type: Type of audit event
            user_id: User performing the action
            details: Additional event details
        """
        if not self.config.audit_enabled:
            return
        # Stub implementation - just log for backward compatibility
        _logger.info(
            f"Audit event: {event_type}",
            extra={"user_id": user_id, "event_type": event_type, "details": details},
        )

    def get_ssl_context(self) -> Optional[Any]:
        """Gets SSL context for mTLS (stub for backward compatibility).

        Returns:
            SSL context or None
        """
        if self.config.auth_type != Authtypee.MTLS:
            return None
        # Stub implementation for backward compatibility
        return None


__all__ = ["SecurityManager"]
