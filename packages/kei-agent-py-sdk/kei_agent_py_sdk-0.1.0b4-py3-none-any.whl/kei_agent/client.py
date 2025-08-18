# sdk/python/kei_agent_sdk/client.py
"""
Haupt-Client für KEI-Agent-Framework SDK.

Implementiert vollständige Client-Funktionalität mit Enterprise-Features
wie Retry-Mechanismen, Tracing und Service Discovery.
"""

from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable, Awaitable
from urllib.parse import urljoin

import aiohttp
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from models import Agent, AgentHealth
from exceptions import (
    KeiSDKError,
    AgentNotFoundError,
    CommunicationError,
    RetryExhaustedError,
)
from tracing import TracingManager
from retry import RetryManager, RetryPolicy, RetryStrategy
from utils import create_correlation_id


@dataclass
class ConnectionConfig:
    """Konfiguration für HTTP-Verbindungen."""

    timeout: float = 30.0
    max_connections: int = 100
    max_connections_per_host: int = 30
    keepalive_timeout: float = 30.0
    enable_compression: bool = True
    ssl_verify: bool = True

    # Connection Pool Settings
    pool_recycle: int = 3600  # Sekunden
    pool_pre_ping: bool = True

    # HTTP/2 Settings
    enable_http2: bool = False


@dataclass
class RetryConfig:
    """Konfiguration für Retry-Mechanismen."""

    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    # Retry-Strategie (z. B. EXPONENTIAL_BACKOFF, FIXED_DELAY, LINEAR_BACKOFF)
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF

    # Circuit Breaker Settings
    circuit_breaker_enabled: bool = True
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    half_open_max_calls: int = 3

    # Retry Conditions
    retry_on_status_codes: List[int] = field(
        default_factory=lambda: [429, 502, 503, 504]
    )
    retry_on_exceptions: List[type] = field(
        default_factory=lambda: [
            aiohttp.ClientTimeout,
            aiohttp.ClientConnectionError,
            aiohttp.ServerDisconnectedError,
        ]
    )


@dataclass
class TracingConfig:
    """Konfiguration für Distributed Tracing."""

    enabled: bool = True
    service_name: str = "kei-agent-sdk"
    service_version: str = "1.0.0"

    # OpenTelemetry Settings
    trace_sampling_rate: float = 1.0
    span_processor_batch_size: int = 512
    span_processor_export_timeout: float = 30.0

    # Jaeger Settings
    jaeger_endpoint: Optional[str] = None
    jaeger_agent_host: str = "localhost"
    jaeger_agent_port: int = 6831

    # Custom Attributes
    custom_attributes: Dict[str, str] = field(default_factory=dict)


@dataclass
class AgentClientConfig:
    """Hauptkonfiguration für KEI-Agent-Client."""

    base_url: str
    api_token: str
    agent_id: str

    # Optional Settings
    tenant_id: Optional[str] = None
    user_agent: str = "KEI-Agent-SDK/1.0.0"

    # Sub-Configurations
    connection: ConnectionConfig = field(default_factory=ConnectionConfig)
    retry: RetryConfig = field(default_factory=RetryConfig)
    # Protokoll-spezifische Retry-Policies (Schlüssel: "rpc", "stream", "bus", "mcp")
    protocol_retry_policies: Dict[str, RetryConfig] = field(default_factory=dict)
    tracing: TracingConfig = field(default_factory=TracingConfig)

    # Feature Flags
    enable_service_discovery: bool = True
    enable_health_monitoring: bool = True
    enable_capability_advertisement: bool = True
    enable_a2a_communication: bool = True

    # Callbacks
    on_connection_error: Optional[Callable[[Exception], Awaitable[None]]] = None
    on_retry_attempt: Optional[Callable[[int, Exception], Awaitable[None]]] = None
    on_circuit_breaker_open: Optional[Callable[[str], Awaitable[None]]] = None


class KeiAgentClient:
    """Haupt-Client für KEI-Agent-Framework."""

    def __init__(self, config: AgentClientConfig):
        """Initialisiert Client mit Konfiguration.

        Args:
            config: Client-Konfiguration
        """
        self.config = config
        self._session: Optional[aiohttp.ClientSession] = None
        self._closed = False

        # Initialize Components
        self._tracing_manager = (
            TracingManager(config.tracing) if config.tracing.enabled else None
        )
        self._retry_manager = RetryManager(config.retry)

        # Internal State
        self._request_count = 0
        self._error_count = 0
        self._last_health_check = 0.0

        # Tracer
        self._tracer = trace.get_tracer(__name__) if self._tracing_manager else None

    async def __aenter__(self) -> KeiAgentClient:
        """Async Context Manager Entry."""
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async Context Manager Exit."""
        await self.close()

    async def _ensure_session(self) -> aiohttp.ClientSession:
        """Stellt sicher, dass HTTP-Session verfügbar ist."""
        if self._session is None or self._session.closed:
            # Erstelle Connector mit Konfiguration
            connector = aiohttp.TCPConnector(
                limit=self.config.connection.max_connections,
                limit_per_host=self.config.connection.max_connections_per_host,
                keepalive_timeout=self.config.connection.keepalive_timeout,
                enable_cleanup_closed=True,
                ssl=self.config.connection.ssl_verify,
            )

            # Erstelle Timeout-Konfiguration
            timeout = aiohttp.ClientTimeout(total=self.config.connection.timeout)

            # Erstelle Session
            self._session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    "User-Agent": self.config.user_agent,
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
            )

        return self._session

    async def close(self) -> None:
        """Schließt Client und alle Verbindungen."""
        if not self._closed:
            if self._session and not self._session.closed:
                await self._session.close()

            if self._tracing_manager:
                await self._tracing_manager.shutdown()

            self._closed = True

    def _create_headers(
        self, additional_headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """Erstellt HTTP-Headers für Request.

        Args:
            additional_headers: Zusätzliche Headers

        Returns:
            Vollständige Headers
        """
        headers = {
            "Authorization": f"Bearer {self.config.api_token}",
            "X-Agent-ID": self.config.agent_id,
            "X-Correlation-ID": create_correlation_id(),
        }

        if self.config.tenant_id:
            headers["X-Tenant-ID"] = self.config.tenant_id

        # Tracing Headers
        if self._tracing_manager:
            trace_headers = self._tracing_manager.get_trace_headers()
            headers.update(trace_headers)

        if additional_headers:
            headers.update(additional_headers)

        return headers

    async def _make_request(
        self,
        method: str,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        trace_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Macht HTTP-Request mit Retry-Mechanismus und Tracing.

        Args:
            method: HTTP-Methode
            path: API-Pfad
            data: Request-Body-Daten
            params: Query-Parameter
            headers: Zusätzliche Headers
            trace_name: Name für Tracing-Span

        Returns:
            Response-Daten

        Raises:
            KeiSDKError: Bei API-Fehlern
            RetryExhaustedError: Bei erschöpften Retry-Versuchen
        """
        url = urljoin(self.config.base_url, path)
        request_headers = self._create_headers(headers)

        # Erstelle Trace-Span
        span_name = trace_name or f"{method.upper()} {path}"

        if self._tracer:
            with self._tracer.start_as_current_span(span_name) as span:
                span.set_attribute("http.method", method.upper())
                span.set_attribute("http.url", url)
                span.set_attribute("agent.id", self.config.agent_id)

                return await self._execute_request_with_retry(
                    method, url, data, params, request_headers, span
                )
        else:
            return await self._execute_request_with_retry(
                method, url, data, params, request_headers
            )

    async def _execute_request_with_retry(
        self,
        method: str,
        url: str,
        data: Optional[Dict[str, Any]],
        params: Optional[Dict[str, Any]],
        headers: Dict[str, str],
        span: Optional[trace.Span] = None,
    ) -> Dict[str, Any]:
        """Führt Request mit Retry-Mechanismus aus.

        Args:
            method: HTTP-Methode
            url: Vollständige URL
            data: Request-Body-Daten
            params: Query-Parameter
            headers: HTTP-Headers
            span: OpenTelemetry-Span

        Returns:
            Response-Daten
        """
        retry_policy = RetryPolicy(
            max_attempts=self.config.retry.max_attempts,
            base_delay=self.config.retry.base_delay,
            max_delay=self.config.retry.max_delay,
            exponential_base=self.config.retry.exponential_base,
            jitter=self.config.retry.jitter,
        )

        last_exception = None

        for attempt in range(retry_policy.max_attempts):
            try:
                self._request_count += 1

                # Führe HTTP-Request aus
                session = await self._ensure_session()

                async with session.request(
                    method=method, url=url, json=data, params=params, headers=headers
                ) as response:
                    # Update Span mit Response-Info
                    if span:
                        span.set_attribute("http.status_code", response.status)
                        span.set_attribute(
                            "http.response_size", len(await response.read())
                        )

                    # Prüfe Response-Status
                    if response.status >= 400:
                        error_text = await response.text()

                        if span:
                            span.set_status(
                                Status(StatusCode.ERROR, f"HTTP {response.status}")
                            )
                            span.set_attribute("http.error_message", error_text)

                        # Prüfe ob Retry möglich
                        if (
                            response.status in self.config.retry.retry_on_status_codes
                            and attempt < retry_policy.max_attempts - 1
                        ):
                            self._error_count += 1

                            # Callback für Retry-Versuch
                            if self.config.on_retry_attempt:
                                await self.config.on_retry_attempt(
                                    attempt + 1,
                                    KeiSDKError(
                                        f"HTTP {response.status}: {error_text}"
                                    ),
                                )

                            # Warte vor nächstem Versuch
                            delay = retry_policy.calculate_delay(attempt)
                            await asyncio.sleep(delay)
                            continue

                        # Erstelle spezifische Exception
                        if response.status == 404:
                            raise AgentNotFoundError(
                                f"Agent nicht gefunden: {error_text}"
                            )
                        else:
                            raise KeiSDKError(f"HTTP {response.status}: {error_text}")

                    # Erfolgreiche Response
                    if span:
                        span.set_status(Status(StatusCode.OK))

                    # Parse JSON-Response
                    try:
                        response_data = await response.json()
                        return response_data
                    except json.JSONDecodeError:
                        # Fallback für leere Responses
                        return {}

            except Exception as e:
                last_exception = e
                self._error_count += 1

                if span:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)

                # Prüfe ob Exception retry-fähig ist
                if (
                    any(
                        isinstance(e, exc_type)
                        for exc_type in self.config.retry.retry_on_exceptions
                    )
                    and attempt < retry_policy.max_attempts - 1
                ):
                    # Callback für Retry-Versuch
                    if self.config.on_retry_attempt:
                        await self.config.on_retry_attempt(attempt + 1, e)

                    # Warte vor nächstem Versuch
                    delay = retry_policy.calculate_delay(attempt)
                    await asyncio.sleep(delay)
                    continue

                # Callback für Connection-Error
                if (
                    isinstance(
                        e,
                        (
                            aiohttp.ClientConnectionError,
                            aiohttp.ServerDisconnectedError,
                        ),
                    )
                    and self.config.on_connection_error
                ):
                    await self.config.on_connection_error(e)

                raise CommunicationError(f"Request fehlgeschlagen: {e}") from e

        # Alle Retry-Versuche erschöpft
        raise RetryExhaustedError(
            f"Request nach {retry_policy.max_attempts} Versuchen fehlgeschlagen",
            last_exception=last_exception,
        )

    # Agent Management APIs

    async def register_agent(
        self,
        name: str,
        version: str = "1.0.0",
        description: str = "",
        capabilities: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Agent:
        """Registriert Agent in der Registry.

        Args:
            name: Agent-Name
            version: Agent-Version
            description: Agent-Beschreibung
            capabilities: Agent-Capabilities
            metadata: Zusätzliche Metadaten

        Returns:
            Registrierter Agent
        """
        request_data = {
            "agent_id": self.config.agent_id,
            "name": name,
            "version": version,
            "description": description,
            "capabilities": capabilities or [],
            "metadata": metadata or {},
        }

        if self.config.tenant_id:
            request_data["tenant_id"] = self.config.tenant_id

        response = await self._make_request(
            "POST",
            "/api/v1/registry/agents",
            data=request_data,
            trace_name="agent.register",
        )

        return Agent.from_dict(response)

    async def get_agent(self, agent_id: str, version: str = "latest") -> Agent:
        """Holt Agent-Informationen.

        Args:
            agent_id: Agent-ID
            version: Agent-Version oder Constraint

        Returns:
            Agent-Informationen
        """
        params = {"version": version}
        if self.config.tenant_id:
            params["tenant_id"] = self.config.tenant_id

        response = await self._make_request(
            "GET",
            f"/api/v1/registry/agents/{agent_id}",
            params=params,
            trace_name="agent.get",
        )

        return Agent.from_dict(response)

    async def update_agent(self, agent_id: Optional[str] = None, **updates) -> Agent:
        """Aktualisiert Agent-Informationen.

        Args:
            agent_id: Agent-ID (default: eigene Agent-ID)
            **updates: Zu aktualisierende Felder

        Returns:
            Aktualisierter Agent
        """
        target_agent_id = agent_id or self.config.agent_id

        response = await self._make_request(
            "PUT",
            f"/api/v1/registry/agents/{target_agent_id}",
            data=updates,
            trace_name="agent.update",
        )

        return Agent.from_dict(response)

    async def delete_agent(
        self, agent_id: Optional[str] = None, force: bool = False
    ) -> None:
        """Entfernt Agent aus Registry.

        Args:
            agent_id: Agent-ID (default: eigene Agent-ID)
            force: Erzwingt Löschung
        """
        target_agent_id = agent_id or self.config.agent_id
        params = {"force": force} if force else {}

        await self._make_request(
            "DELETE",
            f"/api/v1/registry/agents/{target_agent_id}",
            params=params,
            trace_name="agent.delete",
        )

    async def list_agents(
        self,
        capabilities: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        limit: int = 50,
    ) -> List[Agent]:
        """Listet verfügbare Agents auf.

        Args:
            capabilities: Filter nach Capabilities
            tags: Filter nach Tags
            limit: Maximale Anzahl Ergebnisse

        Returns:
            Liste von Agents
        """
        params = {"limit": limit}

        if capabilities:
            params["capabilities"] = ",".join(capabilities)

        if tags:
            params["tags"] = ",".join(tags)

        if self.config.tenant_id:
            params["tenant_id"] = self.config.tenant_id

        response = await self._make_request(
            "GET", "/api/v1/registry/agents", params=params, trace_name="agent.list"
        )

        return [
            Agent.from_dict(agent_data) for agent_data in response.get("agents", [])
        ]

    # Health and Status APIs

    async def health_check(self) -> AgentHealth:
        """Führt Health-Check durch.

        Returns:
            Health-Status
        """
        current_time = time.time()

        try:
            response = await self._make_request(
                "GET", "/api/v1/health", trace_name="health.check"
            )

            self._last_health_check = current_time

            return AgentHealth(
                status="healthy", timestamp=current_time, details=response
            )

        except Exception as e:
            return AgentHealth(
                status="unhealthy", timestamp=current_time, details={"error": str(e)}
            )

    async def get_metrics(self) -> Dict[str, Any]:
        """Holt Client-Metriken.

        Returns:
            Client-Metriken
        """
        return {
            "request_count": self._request_count,
            "error_count": self._error_count,
            "error_rate": self._error_count / max(self._request_count, 1),
            "last_health_check": self._last_health_check,
            "session_active": self._session is not None and not self._session.closed,
            "tracing_enabled": self._tracing_manager is not None,
            "retry_config": {
                "max_attempts": self.config.retry.max_attempts,
                "circuit_breaker_enabled": self.config.retry.circuit_breaker_enabled,
            },
        }
