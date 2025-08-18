# sdk/python/kei_agent/unified_client.py
"""
Unified KEI-Agent Client mit vollständiger Protokoll-Integration.

Integriert alle KEI-Protokolle (RPC, Stream, Bus, MCP) in einer einheitlichen API
für nahtlose Agent-Entwicklung mit Enterprise-Features.
"""

from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Callable, Awaitable

import httpx
import logging

from client import AgentClientConfig, KeiAgentClient
from models import Agent
from exceptions import KeiSDKError, ProtocolError, SecurityError
from tracing import TracingManager
from retry import RetryManager
from capabilities import CapabilityManager
from discovery import ServiceDiscovery
from utils import create_correlation_id

# Initialisiert Modul-Logger
_logger = logging.getLogger(__name__)


class ProtocolType(str, Enum):
    """Unterstützte KEI-Protokolle."""

    RPC = "rpc"
    STREAM = "stream"
    BUS = "bus"
    MCP = "mcp"
    AUTO = "auto"


class AuthType(str, Enum):
    """Unterstützte Authentifizierungstypen."""

    BEARER = "bearer"
    OIDC = "oidc"
    MTLS = "mtls"


@dataclass
class ProtocolConfig:
    """Konfiguration für Protokoll-Integration."""

    rpc_enabled: bool = True
    stream_enabled: bool = True
    bus_enabled: bool = True
    mcp_enabled: bool = True

    # Protokoll-spezifische Endpunkte
    rpc_endpoint: str = "/api/v1/rpc"
    stream_endpoint: str = "/api/v1/stream"
    bus_endpoint: str = "/api/v1/bus"
    mcp_endpoint: str = "/api/v1/mcp"

    # Auto-Protokoll-Auswahl
    auto_protocol_selection: bool = True
    protocol_fallback_enabled: bool = True


@dataclass
class SecurityConfig:
    """Sicherheitskonfiguration für KEI-Agent."""

    auth_type: AuthType = AuthType.BEARER
    api_token: Optional[str] = None

    # OIDC-Konfiguration
    oidc_issuer: Optional[str] = None
    oidc_client_id: Optional[str] = None
    oidc_client_secret: Optional[str] = None
    oidc_scope: str = "openid profile"

    # mTLS-Konfiguration
    mtls_cert_path: Optional[str] = None
    mtls_key_path: Optional[str] = None
    mtls_ca_path: Optional[str] = None

    # Sicherheits-Features
    rbac_enabled: bool = True
    audit_enabled: bool = True
    token_refresh_enabled: bool = True
    token_cache_ttl: int = 3600  # Sekunden


class SecurityManager:
    """Verwaltet Authentifizierung und Autorisierung."""

    def __init__(self, config: SecurityConfig):
        self.config = config
        self._token_cache: Optional[str] = None
        self._token_expires: Optional[datetime] = None
        self._refresh_task: Optional[asyncio.Task] = None

    async def get_auth_headers(self) -> Dict[str, str]:
        """Erstellt Authentifizierungs-Headers basierend auf Konfiguration.

        Returns:
            Dictionary mit Authentifizierungs-Headers

        Raises:
            SecurityError: Bei Authentifizierungsfehlern
        """
        try:
            if self.config.auth_type == AuthType.OIDC:
                token = await self._get_oidc_token()
                return {"Authorization": f"Bearer {token}"}
            elif self.config.auth_type == AuthType.MTLS:
                # mTLS wird auf Transport-Ebene gehandhabt
                return {}
            else:
                if not self.config.api_token:
                    raise SecurityError(
                        "API Token ist erforderlich für Bearer-Authentifizierung"
                    )
                return {"Authorization": f"Bearer {self.config.api_token}"}
        except Exception as e:
            raise SecurityError(f"Fehler bei Authentifizierung: {e}")

    async def _get_oidc_token(self) -> str:
        """Holt OIDC-Token mit Caching und automatischer Erneuerung.

        Returns:
            OIDC Access Token

        Raises:
            SecurityError: Bei OIDC-Fehlern
        """
        # Prüfe Cache
        if (
            self._token_cache
            and self._token_expires
            and datetime.now(timezone.utc) < self._token_expires
        ):
            return self._token_cache

        # Hole neuen Token
        if not all(
            [
                self.config.oidc_issuer,
                self.config.oidc_client_id,
                self.config.oidc_client_secret,
            ]
        ):
            raise SecurityError("OIDC-Konfiguration unvollständig")

        try:
            async with httpx.AsyncClient() as client:
                token_url = f"{self.config.oidc_issuer}/token"
                response = await client.post(
                    token_url,
                    data={
                        "grant_type": "client_credentials",
                        "client_id": self.config.oidc_client_id,
                        "client_secret": self.config.oidc_client_secret,
                        "scope": self.config.oidc_scope,
                    },
                )
                response.raise_for_status()

                token_data = response.json()
                self._token_cache = token_data["access_token"]
                expires_in = token_data.get("expires_in", 3600)
                self._token_expires = datetime.now(timezone.utc).replace(
                    second=0, microsecond=0
                ) + timedelta(seconds=expires_in - 60)  # 60s Puffer

                return self._token_cache

        except Exception as e:
            raise SecurityError(f"OIDC Token-Abruf fehlgeschlagen: {e}")

    async def start_token_refresh(self) -> None:
        """Startet automatische Token-Erneuerung."""
        if self.config.auth_type == AuthType.OIDC and self.config.token_refresh_enabled:
            self._refresh_task = asyncio.create_task(self._token_refresh_loop())

    async def stop_token_refresh(self) -> None:
        """Stoppt automatische Token-Erneuerung."""
        if self._refresh_task:
            self._refresh_task.cancel()
            try:
                await self._refresh_task
            except asyncio.CancelledError:
                pass

    async def _token_refresh_loop(self) -> None:
        """Token-Erneuerungs-Loop."""
        while True:
            try:
                if self._token_expires:
                    # Erneuere Token 5 Minuten vor Ablauf
                    refresh_time = self._token_expires - timedelta(minutes=5)
                    sleep_duration = (
                        refresh_time - datetime.now(timezone.utc)
                    ).total_seconds()

                    if sleep_duration > 0:
                        await asyncio.sleep(sleep_duration)

                    # Token erneuern
                    await self._get_oidc_token()
                else:
                    # Fallback: alle 30 Minuten prüfen
                    await asyncio.sleep(1800)

            except asyncio.CancelledError:
                break
            except Exception as e:
                # Bei Fehlern: 5 Minuten warten und erneut versuchen
                _logger.error(f"Fehler bei Token-Erneuerung: {e}", exc_info=True)
                await asyncio.sleep(300)


# Protokoll-Client-Implementierungen (Embedded für Autonomie)


class KEIRPCClient:
    """Embedded KEI-RPC Client für synchrone Agent-Operationen."""

    def __init__(self, base_url: str, security_manager: SecurityManager):
        self.base_url = base_url.rstrip("/")
        self.security = security_manager
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()

    async def plan(
        self, objective: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Führt Plan-Operation über KEI-RPC aus."""
        return await self._rpc_call(
            "plan", {"objective": objective, "context": context or {}}
        )

    async def act(
        self, action: str, parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Führt Act-Operation über KEI-RPC aus."""
        return await self._rpc_call(
            "act", {"action": action, "parameters": parameters or {}}
        )

    async def observe(
        self, observation_type: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Führt Observe-Operation über KEI-RPC aus."""
        return await self._rpc_call(
            "observe", {"observation_type": observation_type, "data": data or {}}
        )

    async def explain(
        self, query: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Führt Explain-Operation über KEI-RPC aus."""
        return await self._rpc_call(
            "explain", {"query": query, "context": context or {}}
        )

    async def _rpc_call(self, method: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Führt RPC-Call aus."""
        if not self._client:
            raise ProtocolError("RPC Client nicht initialisiert")

        headers = await self.security.get_auth_headers()
        headers.update(
            {
                "Content-Type": "application/json",
                "X-Correlation-ID": create_correlation_id(),
            }
        )

        try:
            response = await self._client.post(
                "/api/v1/rpc/invoke",
                json={"service": "agent", "method": method, "payload": payload},
                headers=headers,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise ProtocolError(f"RPC-Call fehlgeschlagen: {e}")


class KEIStreamClient:
    """Embedded KEI-Stream Client für Realtime-Events."""

    def __init__(self, base_url: str, security_manager: SecurityManager):
        self.base_url = base_url.replace("http", "ws")
        self.security = security_manager
        self._websocket: Optional[Any] = None
        self._connected = False

    async def connect(self) -> None:
        """Stellt WebSocket-Verbindung her."""
        try:
            import websockets

            headers = await self.security.get_auth_headers()
            uri = f"{self.base_url}/api/v1/stream"

            self._websocket = await websockets.connect(uri, extra_headers=headers)
            self._connected = True
        except Exception as e:
            raise ProtocolError(f"Stream-Verbindung fehlgeschlagen: {e}")

    async def disconnect(self) -> None:
        """Schließt WebSocket-Verbindung."""
        if self._websocket:
            await self._websocket.close()
            self._connected = False

    async def subscribe(
        self, stream_id: str, callback: Callable[[Dict[str, Any]], Awaitable[None]]
    ) -> None:
        """Abonniert Stream für Realtime-Events."""
        if not self._connected:
            await self.connect()

        # Sende Subscribe-Message
        await self._websocket.send(
            json.dumps(
                {
                    "type": "subscribe",
                    "stream_id": stream_id,
                    "correlation_id": create_correlation_id(),
                }
            )
        )

        # Höre auf eingehende Messages
        async for message in self._websocket:
            try:
                data = json.loads(message)
                await callback(data)
            except Exception as e:
                # Log error but continue listening
                _logger.error(f"Fehler bei WebSocket-Callback: {e}", exc_info=True)

    async def send_frame(
        self, stream_id: str, frame_type: str, payload: Dict[str, Any]
    ) -> None:
        """Sendet Frame über Stream."""
        if not self._connected:
            await self.connect()

        frame = {
            "type": frame_type,
            "stream_id": stream_id,
            "payload": payload,
            "correlation_id": create_correlation_id(),
            "timestamp": time.time(),
        }

        await self._websocket.send(json.dumps(frame))


class KEIBusClient:
    """Embedded KEI-Bus Client für Event-driven Kommunikation."""

    def __init__(self, base_url: str, security_manager: SecurityManager):
        self.base_url = base_url.rstrip("/")
        self.security = security_manager
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()

    async def publish(self, envelope: Dict[str, Any]) -> Dict[str, Any]:
        """Veröffentlicht Event über Bus."""
        if not self._client:
            raise ProtocolError("Bus Client nicht initialisiert")

        headers = await self.security.get_auth_headers()
        headers.update(
            {
                "Content-Type": "application/json",
                "X-Correlation-ID": create_correlation_id(),
            }
        )

        try:
            response = await self._client.post(
                "/api/v1/bus/publish", json=envelope, headers=headers
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise ProtocolError(f"Bus-Publish fehlgeschlagen: {e}")

    async def rpc_invoke(
        self,
        service: str,
        method: str,
        payload: Dict[str, Any],
        timeout_seconds: float = 5.0,
    ) -> Dict[str, Any]:
        """Führt RPC über Bus aus."""
        if not self._client:
            raise ProtocolError("Bus Client nicht initialisiert")

        headers = await self.security.get_auth_headers()
        headers.update(
            {
                "Content-Type": "application/json",
                "X-Correlation-ID": create_correlation_id(),
            }
        )

        try:
            response = await self._client.post(
                "/api/v1/bus/rpc/invoke",
                json={
                    "service": service,
                    "method": method,
                    "payload": payload,
                    "timeout_seconds": timeout_seconds,
                },
                headers=headers,
                timeout=timeout_seconds + 1.0,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise ProtocolError(f"Bus-RPC fehlgeschlagen: {e}")


class KEIMCPClient:
    """Embedded KEI-MCP Client für Tool/Resource/Prompt Discovery."""

    def __init__(self, base_url: str, security_manager: SecurityManager):
        self.base_url = base_url.rstrip("/")
        self.security = security_manager
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()

    async def discover_tools(
        self, category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Entdeckt verfügbare MCP-Tools."""
        if not self._client:
            raise ProtocolError("MCP Client nicht initialisiert")

        headers = await self.security.get_auth_headers()
        params = {"category": category} if category else {}

        try:
            response = await self._client.get(
                "/api/v1/mcp/tools", params=params, headers=headers
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise ProtocolError(f"MCP Tool-Discovery fehlgeschlagen: {e}")

    async def invoke_tool(
        self, tool_name: str, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Führt MCP-Tool aus."""
        if not self._client:
            raise ProtocolError("MCP Client nicht initialisiert")

        headers = await self.security.get_auth_headers()
        headers.update(
            {
                "Content-Type": "application/json",
                "X-Correlation-ID": create_correlation_id(),
            }
        )

        try:
            response = await self._client.post(
                f"/api/v1/mcp/tools/{tool_name}/invoke",
                json={"parameters": parameters},
                headers=headers,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise ProtocolError(f"MCP Tool-Ausführung fehlgeschlagen: {e}")

    async def discover_resources(
        self, resource_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Entdeckt verfügbare MCP-Resources."""
        if not self._client:
            raise ProtocolError("MCP Client nicht initialisiert")

        headers = await self.security.get_auth_headers()
        params = {"type": resource_type} if resource_type else {}

        try:
            response = await self._client.get(
                "/api/v1/mcp/resources", params=params, headers=headers
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise ProtocolError(f"MCP Resource-Discovery fehlgeschlagen: {e}")

    async def discover_prompts(
        self, category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Entdeckt verfügbare MCP-Prompts."""
        if not self._client:
            raise ProtocolError("MCP Client nicht initialisiert")

        headers = await self.security.get_auth_headers()
        params = {"category": category} if category else {}

        try:
            response = await self._client.get(
                "/api/v1/mcp/prompts", params=params, headers=headers
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise ProtocolError(f"MCP Prompt-Discovery fehlgeschlagen: {e}")


class UnifiedKeiAgentClient:
    """
    Unified KEI-Agent Client mit vollständiger Protokoll-Integration.

    Integriert alle KEI-Protokolle (RPC, Stream, Bus, MCP) in einer einheitlichen API
    mit intelligenter Protokoll-Auswahl und Enterprise-Features.
    """

    def __init__(
        self,
        config: AgentClientConfig,
        protocol_config: Optional[ProtocolConfig] = None,
        security_config: Optional[SecurityConfig] = None,
    ):
        """
        Initialisiert Unified KEI-Agent Client.

        Args:
            config: Basis-Agent-Konfiguration
            protocol_config: Protokoll-spezifische Konfiguration
            security_config: Sicherheitskonfiguration
        """
        self.config = config
        self.protocol_config = protocol_config or ProtocolConfig()
        self.security_config = security_config or SecurityConfig(
            auth_type=AuthType.BEARER, api_token=config.api_token
        )

        # Initialisiere Komponenten
        self.security = SecurityManager(self.security_config)
        self.tracing = (
            TracingManager(config.tracing) if config.tracing.enabled else None
        )
        self.retry = RetryManager(config.retry)
        self.capabilities = CapabilityManager(config)
        self.discovery = (
            ServiceDiscovery(config) if config.enable_service_discovery else None
        )

        # Erstelle Retry-Manager je Protokoll auf Basis protokollspezifischer Policies
        self._retry_managers: Dict[str, RetryManager] = {}
        try:
            # Standard-RetryManager (Fallback)
            self._retry_managers["default"] = RetryManager(config.retry)

            # Protokoll-spezifische Manager anlegen, falls konfiguriert
            for proto_key in ("rpc", "stream", "bus", "mcp"):
                policy_cfg = getattr(config, "protocol_retry_policies", {}).get(
                    proto_key
                )
                if policy_cfg:
                    self._retry_managers[proto_key] = RetryManager(policy_cfg)
                    _logger.info(
                        "RetryPolicy konfiguriert für Protokoll '%s': max_attempts=%s base_delay=%s",
                        proto_key,
                        policy_cfg.max_attempts,
                        policy_cfg.base_delay,
                    )
        except Exception as e:
            # Defensive: Fällt auf Standard zurück, falls etwas schief geht
            _logger.warning(
                f"Fehler bei RetryManager-Konfiguration: {e}", exc_info=True
            )
            self._retry_managers["default"] = RetryManager(config.retry)

        # Protokoll-Clients (werden lazy initialisiert)
        self._rpc_client: Optional[KEIRPCClient] = None
        self._stream_client: Optional[KEIStreamClient] = None
        self._bus_client: Optional[KEIBusClient] = None
        self._mcp_client: Optional[KEIMCPClient] = None

        # Legacy Client für Kompatibilität
        self._legacy_client: Optional[KeiAgentClient] = None

        # Status
        self._initialized = False
        self._closed = False

    async def __aenter__(self):
        """Async Context Manager Entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async Context Manager Exit."""
        await self.close()

    async def initialize(self) -> None:
        """Initialisiert alle Komponenten und Protokoll-Clients."""
        if self._initialized:
            return

        try:
            # Starte Security Manager
            await self.security.start_token_refresh()

            # Initialisiere Legacy Client für Kompatibilität
            self._legacy_client = KeiAgentClient(self.config)

            # Initialisiere Protokoll-Clients
            if self.protocol_config.rpc_enabled:
                self._rpc_client = KEIRPCClient(self.config.base_url, self.security)

            if self.protocol_config.stream_enabled:
                self._stream_client = KEIStreamClient(
                    self.config.base_url, self.security
                )

            if self.protocol_config.bus_enabled:
                self._bus_client = KEIBusClient(self.config.base_url, self.security)

            if self.protocol_config.mcp_enabled:
                self._mcp_client = KEIMCPClient(self.config.base_url, self.security)

            self._initialized = True

        except Exception as e:
            raise KeiSDKError(f"Initialisierung fehlgeschlagen: {e}")

    async def close(self) -> None:
        """Schließt alle Verbindungen und Ressourcen."""
        if self._closed:
            return

        try:
            # Schließe Protokoll-Clients
            if self._stream_client:
                await self._stream_client.disconnect()

            # Stoppe Security Manager
            await self.security.stop_token_refresh()

            # Schließe Legacy Client
            if self._legacy_client:
                await self._legacy_client.close()

            self._closed = True

        except Exception as e:
            # Log error but don't raise
            _logger.error(f"Fehler beim Schließen des Clients: {e}", exc_info=True)

    # Intelligente Protokoll-Auswahl und Orchestrierung

    async def execute_agent_operation(
        self,
        operation: str,
        payload: Dict[str, Any],
        protocol: ProtocolType = ProtocolType.AUTO,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Führt Agent-Operation mit intelligenter Protokoll-Auswahl aus.

        Args:
            operation: Name der Operation (z.B. 'plan', 'act', 'observe', 'explain')
            payload: Operation-spezifische Daten
            protocol: Zu verwendendes Protokoll (AUTO für automatische Auswahl)
            timeout: Timeout in Sekunden

        Returns:
            Ergebnis der Operation

        Raises:
            ProtocolError: Bei Protokoll-Fehlern
            KeiSDKError: Bei allgemeinen SDK-Fehlern
        """
        if not self._initialized:
            await self.initialize()

        # Wähle optimales Protokoll
        if protocol == ProtocolType.AUTO:
            protocol = self._select_optimal_protocol(operation)

        # Führe Operation mit Tracing aus
        trace_name = f"agent.{operation}"
        if self.tracing:
            with self.tracing.start_span(trace_name) as span:
                span.set_attribute("agent.id", self.config.agent_id)
                span.set_attribute("protocol", protocol.value)
                span.set_attribute("operation", operation)

                try:
                    return await self._execute_with_protocol(
                        protocol, operation, payload, timeout
                    )
                except Exception as e:
                    span.record_exception(e)
                    raise
        else:
            return await self._execute_with_protocol(
                protocol, operation, payload, timeout
            )

    def _select_optimal_protocol(self, operation: str) -> ProtocolType:
        """
        Wählt optimales Protokoll basierend auf Operation.

        Args:
            operation: Name der Operation

        Returns:
            Optimales Protokoll für die Operation
        """
        # Streaming-Operationen
        streaming_ops = {
            "stream_response",
            "voice_synthesis",
            "real_time_data",
            "partial_results",
            "live_updates",
        }

        # Asynchrone Event-Operationen
        async_ops = {
            "background_task",
            "notification",
            "event_processing",
            "agent_communication",
            "workflow_trigger",
        }

        # MCP-Tool-Operationen
        mcp_ops = {
            "tool_discovery",
            "tool_invoke",
            "resource_access",
            "prompt_discovery",
            "capability_query",
        }

        if operation in streaming_ops and self.protocol_config.stream_enabled:
            return ProtocolType.STREAM
        elif operation in async_ops and self.protocol_config.bus_enabled:
            return ProtocolType.BUS
        elif operation in mcp_ops and self.protocol_config.mcp_enabled:
            return ProtocolType.MCP
        elif self.protocol_config.rpc_enabled:
            return ProtocolType.RPC
        else:
            # Fallback auf verfügbares Protokoll
            if self.protocol_config.rpc_enabled:
                return ProtocolType.RPC
            elif self.protocol_config.bus_enabled:
                return ProtocolType.BUS
            else:
                raise ProtocolError("Kein verfügbares Protokoll für Operation")

    def _get_retry_manager(self, protocol: str) -> RetryManager:
        """Gibt den Retry-Manager für das angegebene Protokoll zurück.

        Args:
            protocol: Protokollname ("rpc", "stream", "bus", "mcp")

        Returns:
            RetryManager-Instanz; fällt auf Standard zurück, wenn nicht vorhanden
        """
        proto = (protocol or "").lower()
        return (
            self._retry_managers.get(proto)
            or self._retry_managers.get("default")
            or self.retry
        )

    async def _execute_with_protocol(
        self,
        protocol: ProtocolType,
        operation: str,
        payload: Dict[str, Any],
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Führt Operation mit spezifischem Protokoll aus.

        Args:
            protocol: Zu verwendendes Protokoll
            operation: Name der Operation
            payload: Operation-spezifische Daten
            timeout: Timeout in Sekunden

        Returns:
            Ergebnis der Operation
        """
        try:
            if protocol == ProtocolType.RPC:
                return await self._execute_rpc_operation(operation, payload, timeout)
            elif protocol == ProtocolType.STREAM:
                return await self._execute_stream_operation(operation, payload, timeout)
            elif protocol == ProtocolType.BUS:
                return await self._execute_bus_operation(operation, payload, timeout)
            elif protocol == ProtocolType.MCP:
                return await self._execute_mcp_operation(operation, payload, timeout)
            else:
                raise ProtocolError(f"Unbekanntes Protokoll: {protocol}")

        except Exception as e:
            # Fallback-Mechanismus wenn aktiviert
            _logger.warning(
                f"Protokoll-Operation fehlgeschlagen mit {protocol}: {e}", exc_info=True
            )
            if (
                self.protocol_config.protocol_fallback_enabled
                and protocol != ProtocolType.RPC
                and self.protocol_config.rpc_enabled
            ):
                return await self._execute_rpc_operation(operation, payload, timeout)
            raise

    async def _execute_rpc_operation(
        self, operation: str, payload: Dict[str, Any], timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """Führt Operation über KEI-RPC aus."""
        if not self._rpc_client:
            raise ProtocolError("KEI-RPC Client nicht verfügbar")

        # Umschließt RPC-Operation mit Retry- und Circuit-Breaker-Mechanismen
        async def operation_call() -> Dict[str, Any]:
            """Führt die eigentliche RPC-Operation aus (einzelner Versuch)."""
            async with self._rpc_client:
                if operation == "plan":
                    return await self._rpc_client.plan(
                        payload.get("objective", ""), payload.get("context")
                    )
                elif operation == "act":
                    return await self._rpc_client.act(
                        payload.get("action", ""), payload.get("parameters")
                    )
                elif operation == "observe":
                    return await self._rpc_client.observe(
                        payload.get("observation_type", ""), payload.get("data")
                    )
                elif operation == "explain":
                    return await self._rpc_client.explain(
                        payload.get("query", ""), payload.get("context")
                    )
                else:
                    # Generischer RPC-Call
                    return await self._rpc_client._rpc_call(operation, payload)

        cb_name = f"rpc.{operation}"
        retry_manager = (
            self._retry_managers.get("rpc")
            or self._retry_managers.get("default")
            or self.retry
        )
        _logger.debug(
            "Retry-Call vorbereitet (Policy via '%s'): operation='%s'", "rpc", operation
        )
        return await retry_manager.execute_with_retry(
            operation_call, circuit_breaker_name=cb_name
        )

    async def _execute_stream_operation(
        self, operation: str, payload: Dict[str, Any], timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """Führt Operation über KEI-Stream aus."""
        if not self._stream_client:
            raise ProtocolError("KEI-Stream Client nicht verfügbar")

        # Für Stream-Operationen wird meist ein Callback benötigt
        if "callback" not in payload:
            raise ProtocolError("Stream-Operationen benötigen einen Callback")

        stream_id = payload.get("stream_id", create_correlation_id())
        callback = payload["callback"]

        # Umschließt Stream-Operationen mit Retry- und Circuit-Breaker-Mechanismen
        async def operation_call() -> Dict[str, Any]:
            """Führt die eigentliche Stream-Operation aus (einzelner Versuch)."""
            if operation == "subscribe":
                await self._stream_client.subscribe(stream_id, callback)
                return {"status": "subscribed", "stream_id": stream_id}
            else:
                # Sende Frame
                frame_type = payload.get("frame_type", operation)
                frame_payload = payload.get("frame_payload", {})
                await self._stream_client.send_frame(
                    stream_id, frame_type, frame_payload
                )
                return {
                    "status": "sent",
                    "stream_id": stream_id,
                    "frame_type": frame_type,
                }

        cb_name = f"stream.{operation}"
        retry_manager = (
            self._retry_managers.get("stream")
            or self._retry_managers.get("default")
            or self.retry
        )
        return await retry_manager.execute_with_retry(
            operation_call, circuit_breaker_name=cb_name
        )

    async def _execute_bus_operation(
        self, operation: str, payload: Dict[str, Any], timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """Führt Operation über KEI-Bus aus."""
        if not self._bus_client:
            raise ProtocolError("KEI-Bus Client nicht verfügbar")

        # Umschließt Bus-Operationen mit Retry- und Circuit-Breaker-Mechanismen
        async def operation_call() -> Dict[str, Any]:
            """Führt die eigentliche Bus-Operation aus (einzelner Versuch)."""
            async with self._bus_client:
                if operation == "publish":
                    envelope = payload.get("envelope", payload)
                    return await self._bus_client.publish(envelope)
                elif operation == "rpc_invoke":
                    return await self._bus_client.rpc_invoke(
                        payload.get("service", "agent"),
                        payload.get("method", operation),
                        payload.get("payload", {}),
                        timeout or 5.0,
                    )
                else:
                    # Generischer Bus-RPC-Call
                    return await self._bus_client.rpc_invoke(
                        "agent", operation, payload, timeout or 5.0
                    )

        cb_name = f"bus.{operation}"
        retry_manager = (
            self._retry_managers.get("bus")
            or self._retry_managers.get("default")
            or self.retry
        )
        _logger.debug(
            "Retry-Call vorbereitet (Policy via '%s'): operation='%s'", "bus", operation
        )
        return await retry_manager.execute_with_retry(
            operation_call, circuit_breaker_name=cb_name
        )

    async def _execute_mcp_operation(
        self, operation: str, payload: Dict[str, Any], timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """Führt Operation über KEI-MCP aus."""
        if not self._mcp_client:
            raise ProtocolError("KEI-MCP Client nicht verfügbar")

        # Umschließt MCP-Operationen mit Retry- und Circuit-Breaker-Mechanismen
        async def operation_call() -> Dict[str, Any]:
            """Führt die eigentliche MCP-Operation aus (einzelner Versuch)."""
            async with self._mcp_client:
                if operation == "discover_tools":
                    return {
                        "tools": await self._mcp_client.discover_tools(
                            payload.get("category")
                        )
                    }
                elif operation == "invoke_tool":
                    return await self._mcp_client.invoke_tool(
                        payload.get("tool_name", ""), payload.get("parameters", {})
                    )
                elif operation == "discover_resources":
                    return {
                        "resources": await self._mcp_client.discover_resources(
                            payload.get("type")
                        )
                    }
                elif operation == "discover_prompts":
                    return {
                        "prompts": await self._mcp_client.discover_prompts(
                            payload.get("category")
                        )
                    }
                else:
                    raise ProtocolError(f"Unbekannte MCP-Operation: {operation}")

        cb_name = f"mcp.{operation}"
        retry_manager = (
            self._retry_managers.get("mcp")
            or self._retry_managers.get("default")
            or self.retry
        )
        _logger.debug(
            "Retry-Call vorbereitet (Policy via '%s'): operation='%s'", "mcp", operation
        )
        return await retry_manager.execute_with_retry(
            operation_call, circuit_breaker_name=cb_name
        )

    # High-Level API-Methoden für häufige Anwendungsfälle

    async def plan_task(
        self, objective: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Erstellt Plan für gegebenes Ziel."""
        return await self.execute_agent_operation(
            "plan", {"objective": objective, "context": context or {}}
        )

    async def execute_action(
        self, action: str, parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Führt Aktion aus."""
        return await self.execute_agent_operation(
            "act", {"action": action, "parameters": parameters or {}}
        )

    async def observe_environment(
        self, observation_type: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Führt Umgebungsbeobachtung durch."""
        return await self.execute_agent_operation(
            "observe", {"observation_type": observation_type, "data": data or {}}
        )

    async def explain_reasoning(
        self, query: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Erklärt Reasoning für gegebene Anfrage."""
        return await self.execute_agent_operation(
            "explain", {"query": query, "context": context or {}}
        )

    # Agent-to-Agent Kommunikation

    async def send_agent_message(
        self,
        target_agent: str,
        message_type: str,
        payload: Dict[str, Any],
        protocol: ProtocolType = ProtocolType.AUTO,
    ) -> Dict[str, Any]:
        """
        Sendet Nachricht an anderen Agent.

        Args:
            target_agent: ID des Ziel-Agents
            message_type: Typ der Nachricht
            payload: Nachrichteninhalt
            protocol: Zu verwendendes Protokoll

        Returns:
            Antwort des Ziel-Agents
        """
        envelope = {
            "type": "agent_message",
            "subject": f"agent.{target_agent}",
            "payload": {
                "from_agent": self.config.agent_id,
                "to_agent": target_agent,
                "message_type": message_type,
                "payload": payload,
                "correlation_id": create_correlation_id(),
                "timestamp": time.time(),
            },
        }

        if protocol == ProtocolType.AUTO:
            protocol = ProtocolType.BUS  # Bus ist optimal für A2A

        return await self.execute_agent_operation(
            "publish", {"envelope": envelope}, protocol
        )

    async def subscribe_to_agent_messages(
        self,
        callback: Callable[[Dict[str, Any]], Awaitable[None]],
        message_types: Optional[List[str]] = None,
    ) -> None:
        """
        Abonniert Agent-Nachrichten.

        Args:
            callback: Callback-Funktion für eingehende Nachrichten
            message_types: Zu abonnierende Nachrichtentypen (None = alle)
        """
        stream_id = f"agent.{self.config.agent_id}.messages"

        async def filtered_callback(message: Dict[str, Any]) -> None:
            """Filtert Nachrichten nach Typ."""
            if message_types is None:
                await callback(message)
            else:
                msg_type = message.get("payload", {}).get("message_type")
                if msg_type in message_types:
                    await callback(message)

        await self.execute_agent_operation(
            "subscribe",
            {"stream_id": stream_id, "callback": filtered_callback},
            ProtocolType.STREAM,
        )

    # MCP-Integration High-Level API

    async def discover_available_tools(
        self, category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Entdeckt verfügbare MCP-Tools."""
        result = await self.execute_agent_operation(
            "discover_tools", {"category": category}, ProtocolType.MCP
        )
        return result.get("tools", [])

    async def use_tool(self, tool_name: str, **parameters) -> Dict[str, Any]:
        """Verwendet MCP-Tool mit gegebenen Parametern."""
        return await self.execute_agent_operation(
            "invoke_tool",
            {"tool_name": tool_name, "parameters": parameters},
            ProtocolType.MCP,
        )

    async def discover_available_resources(
        self, resource_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Entdeckt verfügbare MCP-Resources."""
        result = await self.execute_agent_operation(
            "discover_resources", {"type": resource_type}, ProtocolType.MCP
        )
        return result.get("resources", [])

    async def discover_available_prompts(
        self, category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Entdeckt verfügbare MCP-Prompts."""
        result = await self.execute_agent_operation(
            "discover_prompts", {"category": category}, ProtocolType.MCP
        )
        return result.get("prompts", [])

    # Streaming und Realtime-Features

    async def start_streaming_session(
        self,
        session_id: Optional[str] = None,
        callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None,
    ) -> str:
        """
        Startet Streaming-Session für Realtime-Kommunikation.

        Args:
            session_id: Optional Session-ID (wird generiert wenn nicht angegeben)
            callback: Callback für eingehende Stream-Nachrichten

        Returns:
            Session-ID
        """
        session_id = session_id or create_correlation_id()

        if callback:
            await self.execute_agent_operation(
                "subscribe",
                {"stream_id": session_id, "callback": callback},
                ProtocolType.STREAM,
            )

        return session_id

    async def send_streaming_data(
        self, session_id: str, data_type: str, data: Dict[str, Any]
    ) -> None:
        """Sendet Daten über Streaming-Session."""
        await self.execute_agent_operation(
            "send_frame",
            {"stream_id": session_id, "frame_type": data_type, "frame_payload": data},
            ProtocolType.STREAM,
        )

    # Kompatibilitäts-API für Legacy-Code

    async def register_agent(
        self,
        name: str,
        version: str = "1.0.0",
        description: str = "",
        capabilities: Optional[List[str]] = None,
    ) -> Agent:
        """Registriert Agent (Legacy-Kompatibilität)."""
        if not self._legacy_client:
            raise KeiSDKError("Legacy Client nicht verfügbar")

        return await self._legacy_client.register_agent(
            name, version, description, capabilities or []
        )

    async def get_agent(self, agent_id: str, version: str = "latest") -> Agent:
        """Holt Agent-Informationen (Legacy-Kompatibilität)."""
        if not self._legacy_client:
            raise KeiSDKError("Legacy Client nicht verfügbar")

        return await self._legacy_client.get_agent(agent_id, version)

    async def list_agents(
        self, capabilities: Optional[List[str]] = None, status: Optional[str] = None
    ) -> List[Agent]:
        """Listet Agents auf (Legacy-Kompatibilität)."""
        if not self._legacy_client:
            raise KeiSDKError("Legacy Client nicht verfügbar")

        return await self._legacy_client.list_agents(capabilities, status)

    async def health_check(self) -> Dict[str, Any]:
        """Führt Health-Check durch."""
        if not self._legacy_client:
            raise KeiSDKError("Legacy Client nicht verfügbar")

        return await self._legacy_client.health_check()

    # Utility-Methoden

    def is_protocol_available(self, protocol: ProtocolType) -> bool:
        """Prüft ob Protokoll verfügbar ist."""
        if protocol == ProtocolType.RPC:
            return self.protocol_config.rpc_enabled and self._rpc_client is not None
        elif protocol == ProtocolType.STREAM:
            return (
                self.protocol_config.stream_enabled and self._stream_client is not None
            )
        elif protocol == ProtocolType.BUS:
            return self.protocol_config.bus_enabled and self._bus_client is not None
        elif protocol == ProtocolType.MCP:
            return self.protocol_config.mcp_enabled and self._mcp_client is not None
        return False

    def get_available_protocols(self) -> List[ProtocolType]:
        """Gibt Liste verfügbarer Protokolle zurück."""
        protocols = []
        for protocol in ProtocolType:
            if protocol != ProtocolType.AUTO and self.is_protocol_available(protocol):
                protocols.append(protocol)
        return protocols

    def get_client_info(self) -> Dict[str, Any]:
        """Gibt Client-Informationen zurück."""
        return {
            "agent_id": self.config.agent_id,
            "base_url": self.config.base_url,
            "initialized": self._initialized,
            "closed": self._closed,
            "available_protocols": [p.value for p in self.get_available_protocols()],
            "security_type": self.security_config.auth_type.value,
            "features": {
                "tracing": self.tracing is not None,
                "retry": True,
                "capabilities": True,
                "discovery": self.discovery is not None,
                "auto_protocol_selection": self.protocol_config.auto_protocol_selection,
                "protocol_fallback": self.protocol_config.protocol_fallback_enabled,
            },
        }
