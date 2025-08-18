# sdk/python/kei_agent_sdk/a2a.py
"""
Agent-to-Agent (A2A) Kommunikation für KEI-Agent-Framework.

Implementiert vollständige A2A-Kommunikation mit Service Discovery,
Load-Balancing und verschiedenen Kommunikationsprotokollen.
"""

from __future__ import annotations

import asyncio
import json
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Callable, Awaitable

import aiohttp
import websockets
from opentelemetry import trace

from client import KeiAgentClient
from models import AgentInstance
from discovery import ServiceDiscovery, DiscoveryStrategy, LoadBalancer
from exceptions import CommunicationError, AgentNotFoundError
from utils import create_correlation_id, format_trace_id


class CommunicationProtocol(str, Enum):
    """Unterstützte Kommunikationsprotokolle."""

    HTTP = "http"
    WEBSOCKET = "websocket"
    GRPC = "grpc"
    MESSAGE_BUS = "message_bus"


class LoadBalancingStrategy(str, Enum):
    """Load-Balancing-Strategien."""

    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    RESPONSE_TIME = "response_time"
    RANDOM = "random"
    HEALTH_BASED = "health_based"


@dataclass
class FailoverConfig:
    """Konfiguration für Failover-Mechanismen."""

    enabled: bool = True
    max_retries: int = 3
    retry_delay: float = 1.0
    circuit_breaker_enabled: bool = True
    health_check_interval: float = 30.0

    # Failover-Strategien
    prefer_same_region: bool = True
    prefer_same_zone: bool = True
    exclude_failed_instances: bool = True

    # Callbacks
    on_failover: Optional[Callable[[str, str], Awaitable[None]]] = None
    on_instance_failed: Optional[Callable[[str], Awaitable[None]]] = None


@dataclass
class A2AMessage:
    """Nachricht für Agent-to-Agent-Kommunikation."""

    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    from_agent: str = ""
    to_agent: str = ""
    message_type: str = "request"
    payload: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    correlation_id: str = field(default_factory=create_correlation_id)
    trace_id: Optional[str] = None

    # Routing-Informationen
    target_capability: Optional[str] = None
    target_version: Optional[str] = None
    priority: int = 0

    # Delivery-Optionen
    delivery_mode: str = "at_least_once"  # at_most_once, at_least_once, exactly_once
    ttl_seconds: Optional[float] = None
    reply_to: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert Message zu Dictionary."""
        return {
            "message_id": self.message_id,
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "message_type": self.message_type,
            "payload": self.payload,
            "headers": self.headers,
            "timestamp": self.timestamp,
            "correlation_id": self.correlation_id,
            "trace_id": self.trace_id,
            "target_capability": self.target_capability,
            "target_version": self.target_version,
            "priority": self.priority,
            "delivery_mode": self.delivery_mode,
            "ttl_seconds": self.ttl_seconds,
            "reply_to": self.reply_to,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> A2AMessage:
        """Erstellt Message aus Dictionary."""
        return cls(
            message_id=data.get("message_id", str(uuid.uuid4())),
            from_agent=data.get("from_agent", ""),
            to_agent=data.get("to_agent", ""),
            message_type=data.get("message_type", "request"),
            payload=data.get("payload", {}),
            headers=data.get("headers", {}),
            timestamp=data.get("timestamp", time.time()),
            correlation_id=data.get("correlation_id", create_correlation_id()),
            trace_id=data.get("trace_id"),
            target_capability=data.get("target_capability"),
            target_version=data.get("target_version"),
            priority=data.get("priority", 0),
            delivery_mode=data.get("delivery_mode", "at_least_once"),
            ttl_seconds=data.get("ttl_seconds"),
            reply_to=data.get("reply_to"),
        )


@dataclass
class A2AResponse:
    """Response für Agent-to-Agent-Kommunikation."""

    message_id: str
    correlation_id: str
    status: str = "success"  # success, error, timeout
    payload: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    processing_time_ms: Optional[float] = None

    # Response-Metadaten
    from_agent: str = ""
    response_headers: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert Response zu Dictionary."""
        return {
            "message_id": self.message_id,
            "correlation_id": self.correlation_id,
            "status": self.status,
            "payload": self.payload,
            "error_message": self.error_message,
            "error_code": self.error_code,
            "timestamp": self.timestamp,
            "processing_time_ms": self.processing_time_ms,
            "from_agent": self.from_agent,
            "response_headers": self.response_headers,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> A2AResponse:
        """Erstellt Response aus Dictionary."""
        return cls(
            message_id=data.get("message_id", ""),
            correlation_id=data.get("correlation_id", ""),
            status=data.get("status", "success"),
            payload=data.get("payload", {}),
            error_message=data.get("error_message"),
            error_code=data.get("error_code"),
            timestamp=data.get("timestamp", time.time()),
            processing_time_ms=data.get("processing_time_ms"),
            from_agent=data.get("from_agent", ""),
            response_headers=data.get("response_headers", {}),
        )


class A2AClient:
    """Client für Agent-to-Agent-Kommunikation."""

    def __init__(
        self,
        base_client: KeiAgentClient,
        failover_config: Optional[FailoverConfig] = None,
    ):
        """Initialisiert A2A-Client.

        Args:
            base_client: Basis-KEI-Client
            failover_config: Failover-Konfiguration
        """
        self.base_client = base_client
        self.failover_config = failover_config or FailoverConfig()

        # Service Discovery und Load Balancing
        self._service_discovery: Optional[ServiceDiscovery] = None
        self._load_balancer: Optional[LoadBalancer] = None

        # Connection Pools
        self._http_sessions: Dict[str, aiohttp.ClientSession] = {}
        self._websocket_connections: Dict[str, websockets.WebSocketServerProtocol] = {}

        # Instance Health Tracking
        self._instance_health: Dict[str, Dict[str, Any]] = {}
        self._failed_instances: set[str] = set()

        # Metrics
        self._message_count = 0
        self._error_count = 0
        self._response_times: List[float] = []

        # Tracer
        self._tracer = trace.get_tracer(__name__)

    def enable_service_discovery(
        self,
        strategy: DiscoveryStrategy = DiscoveryStrategy.HYBRID,
        load_balancing: LoadBalancingStrategy = LoadBalancingStrategy.HEALTH_BASED,
    ) -> None:
        """Aktiviert Service Discovery.

        Args:
            strategy: Discovery-Strategie
            load_balancing: Load-Balancing-Strategie
        """
        self._service_discovery = ServiceDiscovery(
            self.base_client, default_strategy=strategy
        )

        self._load_balancer = LoadBalancer(
            strategy=load_balancing, health_tracker=self._instance_health
        )

    def enable_distributed_tracing(self) -> None:
        """Aktiviert Distributed Tracing für A2A-Kommunikation."""
        # Tracing ist bereits über base_client verfügbar
        pass

    async def send_message(
        self,
        target_agent: str,
        payload: Dict[str, Any],
        message_type: str = "request",
        protocol: CommunicationProtocol = CommunicationProtocol.HTTP,
        timeout: float = 30.0,
        **kwargs,
    ) -> A2AResponse:
        """Sendet Nachricht an anderen Agent.

        Args:
            target_agent: Ziel-Agent-ID
            payload: Nachrichteninhalt
            message_type: Nachrichtentyp
            protocol: Kommunikationsprotokoll
            timeout: Timeout in Sekunden
            **kwargs: Zusätzliche Message-Parameter

        Returns:
            Agent-Response

        Raises:
            AgentNotFoundError: Wenn Ziel-Agent nicht gefunden
            CommunicationError: Bei Kommunikationsfehlern
        """
        # Erstelle A2A-Message
        message = A2AMessage(
            from_agent=self.base_client.config.agent_id,
            to_agent=target_agent,
            message_type=message_type,
            payload=payload,
            **kwargs,
        )

        # Trace-Kontext setzen
        if self._tracer:
            with self._tracer.start_as_current_span(
                f"a2a.send_message.{target_agent}"
            ) as span:
                span.set_attribute("target_agent", target_agent)
                span.set_attribute("message_type", message_type)
                span.set_attribute("protocol", protocol.value)
                span.set_attribute("message_id", message.message_id)

                message.trace_id = format_trace_id(span.get_span_context().trace_id)

                return await self._send_message_with_discovery(
                    message, protocol, timeout
                )
        else:
            return await self._send_message_with_discovery(message, protocol, timeout)

    async def _send_message_with_discovery(
        self, message: A2AMessage, protocol: CommunicationProtocol, timeout: float
    ) -> A2AResponse:
        """Sendet Message mit Service Discovery und Failover.

        Args:
            message: A2A-Message
            protocol: Kommunikationsprotokoll
            timeout: Timeout

        Returns:
            A2A-Response
        """
        start_time = time.time()

        try:
            # Service Discovery für Ziel-Agent
            if self._service_discovery:
                instances = await self._discover_agent_instances(message.to_agent)

                if not instances:
                    raise AgentNotFoundError(
                        f"Agent '{message.to_agent}' nicht gefunden"
                    )

                # Load Balancing
                if self._load_balancer:
                    target_instance = self._load_balancer.select_instance(instances)
                else:
                    target_instance = instances[0]  # Fallback: erste Instanz
            else:
                # Fallback: direkte Kommunikation ohne Discovery
                target_instance = AgentInstance(
                    agent_id=message.to_agent,
                    instance_id=f"{message.to_agent}-default",
                    endpoint=f"{self.base_client.config.base_url}/api/v1/agents/{message.to_agent}",
                )

            # Sende Message mit Failover
            response = await self._send_with_failover(
                message, target_instance, protocol, timeout
            )

            # Metrics aktualisieren
            processing_time = (time.time() - start_time) * 1000
            self._message_count += 1
            self._response_times.append(processing_time)

            # Response-Metadaten setzen
            response.processing_time_ms = processing_time

            return response

        except Exception as e:
            self._error_count += 1

            if isinstance(e, (AgentNotFoundError, CommunicationError)):
                raise
            else:
                raise CommunicationError(
                    f"A2A-Kommunikation fehlgeschlagen: {e}"
                ) from e

    async def _discover_agent_instances(self, agent_id: str) -> List[AgentInstance]:
        """Entdeckt verfügbare Instanzen für Agent.

        Args:
            agent_id: Agent-ID

        Returns:
            Liste verfügbarer Instanzen
        """
        if not self._service_discovery:
            return []

        # Filtere fehlgeschlagene Instanzen aus
        instances = await self._service_discovery.discover_agent_instances(agent_id)

        if self.failover_config.exclude_failed_instances:
            instances = [
                instance
                for instance in instances
                if instance.instance_id not in self._failed_instances
            ]

        return instances

    async def _send_with_failover(
        self,
        message: A2AMessage,
        target_instance: AgentInstance,
        protocol: CommunicationProtocol,
        timeout: float,
    ) -> A2AResponse:
        """Sendet Message mit Failover-Mechanismus.

        Args:
            message: A2A-Message
            target_instance: Ziel-Instanz
            protocol: Kommunikationsprotokoll
            timeout: Timeout

        Returns:
            A2A-Response
        """
        last_exception = None

        for attempt in range(self.failover_config.max_retries + 1):
            try:
                # Sende Message über gewähltes Protokoll
                if protocol == CommunicationProtocol.HTTP:
                    response = await self._send_http_message(
                        message, target_instance, timeout
                    )
                elif protocol == CommunicationProtocol.WEBSOCKET:
                    response = await self._send_websocket_message(
                        message, target_instance, timeout
                    )
                elif protocol == CommunicationProtocol.MESSAGE_BUS:
                    response = await self._send_message_bus_message(
                        message, target_instance, timeout
                    )
                else:
                    raise CommunicationError(
                        f"Protokoll '{protocol}' nicht unterstützt"
                    )

                # Erfolgreiche Übertragung - Instanz als gesund markieren
                self._mark_instance_healthy(target_instance.instance_id)

                return response

            except Exception as e:
                last_exception = e

                # Instanz als fehlgeschlagen markieren
                self._mark_instance_failed(target_instance.instance_id)

                # Callback für fehlgeschlagene Instanz
                if self.failover_config.on_instance_failed:
                    await self.failover_config.on_instance_failed(
                        target_instance.instance_id
                    )

                # Letzter Versuch - Exception weiterwerfen
                if attempt >= self.failover_config.max_retries:
                    break

                # Callback für Failover
                if self.failover_config.on_failover:
                    await self.failover_config.on_failover(
                        target_instance.instance_id, f"Attempt {attempt + 1}"
                    )

                # Warte vor nächstem Versuch
                await asyncio.sleep(self.failover_config.retry_delay)

                # Versuche alternative Instanz zu finden
                if self._service_discovery:
                    alternative_instances = await self._discover_agent_instances(
                        message.to_agent
                    )
                    available_instances = [
                        inst
                        for inst in alternative_instances
                        if inst.instance_id != target_instance.instance_id
                        and inst.instance_id not in self._failed_instances
                    ]

                    if available_instances:
                        if self._load_balancer:
                            target_instance = self._load_balancer.select_instance(
                                available_instances
                            )
                        else:
                            target_instance = available_instances[0]

        # Alle Failover-Versuche fehlgeschlagen
        raise CommunicationError(
            f"A2A-Kommunikation nach {self.failover_config.max_retries + 1} Versuchen fehlgeschlagen"
        ) from last_exception

    async def _send_http_message(
        self, message: A2AMessage, target_instance: AgentInstance, timeout: float
    ) -> A2AResponse:
        """Sendet Message über HTTP.

        Args:
            message: A2A-Message
            target_instance: Ziel-Instanz
            timeout: Timeout

        Returns:
            A2A-Response
        """
        # Erstelle HTTP-Headers
        headers = {
            "Content-Type": "application/json",
            "X-Message-ID": message.message_id,
            "X-Correlation-ID": message.correlation_id,
            "X-From-Agent": message.from_agent,
            "X-Message-Type": message.message_type,
        }

        if message.trace_id:
            headers["X-Trace-ID"] = message.trace_id

        headers.update(message.headers)

        # HTTP-Request senden
        session = await self._get_http_session(target_instance.instance_id)

        async with session.post(
            target_instance.endpoint,
            json=message.to_dict(),
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=timeout),
        ) as response:
            if response.status >= 400:
                error_text = await response.text()
                raise CommunicationError(f"HTTP {response.status}: {error_text}")

            response_data = await response.json()

            return A2AResponse.from_dict(response_data)

    async def _send_websocket_message(
        self, message: A2AMessage, target_instance: AgentInstance, timeout: float
    ) -> A2AResponse:
        """Sendet Message über WebSocket.

        Args:
            message: A2A-Message
            target_instance: Ziel-Instanz
            timeout: Timeout

        Returns:
            A2A-Response
        """
        # WebSocket-Verbindung holen oder erstellen
        ws_connection = await self._get_websocket_connection(target_instance)

        # Message senden
        message_json = json.dumps(message.to_dict())
        await ws_connection.send(message_json)

        # Response empfangen
        try:
            response_json = await asyncio.wait_for(
                ws_connection.recv(), timeout=timeout
            )
            response_data = json.loads(response_json)

            return A2AResponse.from_dict(response_data)

        except asyncio.TimeoutError:
            raise CommunicationError(f"WebSocket-Timeout nach {timeout}s")

    async def _send_message_bus_message(
        self, message: A2AMessage, target_instance: AgentInstance, timeout: float
    ) -> A2AResponse:
        """Sendet Message über Message Bus.

        Args:
            message: A2A-Message
            target_instance: Ziel-Instanz
            timeout: Timeout

        Returns:
            A2A-Response
        """
        # TODO: Implementiere Message-Bus-Integration
        # Hier würde Integration mit RabbitMQ, Apache Kafka, etc. stattfinden

        raise CommunicationError("Message-Bus-Protokoll noch nicht implementiert")

    async def _get_http_session(self, instance_id: str) -> aiohttp.ClientSession:
        """Holt oder erstellt HTTP-Session für Instanz.

        Args:
            instance_id: Instanz-ID

        Returns:
            HTTP-Session
        """
        if instance_id not in self._http_sessions:
            self._http_sessions[instance_id] = aiohttp.ClientSession()

        return self._http_sessions[instance_id]

    async def _get_websocket_connection(
        self, target_instance: AgentInstance
    ) -> websockets.WebSocketServerProtocol:
        """Holt oder erstellt WebSocket-Verbindung.

        Args:
            target_instance: Ziel-Instanz

        Returns:
            WebSocket-Verbindung
        """
        instance_id = target_instance.instance_id

        if instance_id not in self._websocket_connections:
            # Konvertiere HTTP-Endpoint zu WebSocket-URL
            ws_url = target_instance.endpoint.replace("http://", "ws://").replace(
                "https://", "wss://"
            )
            ws_url = ws_url.replace("/api/v1/agents/", "/ws/agents/")

            # Erstelle WebSocket-Verbindung
            self._websocket_connections[instance_id] = await websockets.connect(ws_url)

        return self._websocket_connections[instance_id]

    def _mark_instance_healthy(self, instance_id: str) -> None:
        """Markiert Instanz als gesund.

        Args:
            instance_id: Instanz-ID
        """
        self._instance_health[instance_id] = {
            "status": "healthy",
            "last_success": time.time(),
            "consecutive_failures": 0,
        }

        # Entferne aus fehlgeschlagenen Instanzen
        self._failed_instances.discard(instance_id)

    def _mark_instance_failed(self, instance_id: str) -> None:
        """Markiert Instanz als fehlgeschlagen.

        Args:
            instance_id: Instanz-ID
        """
        if instance_id not in self._instance_health:
            self._instance_health[instance_id] = {
                "status": "unhealthy",
                "last_failure": time.time(),
                "consecutive_failures": 1,
            }
        else:
            self._instance_health[instance_id].update(
                {
                    "status": "unhealthy",
                    "last_failure": time.time(),
                    "consecutive_failures": self._instance_health[instance_id].get(
                        "consecutive_failures", 0
                    )
                    + 1,
                }
            )

        # Füge zu fehlgeschlagenen Instanzen hinzu
        self._failed_instances.add(instance_id)

    async def close(self) -> None:
        """Schließt alle Verbindungen."""
        # HTTP-Sessions schließen
        for session in self._http_sessions.values():
            await session.close()
        self._http_sessions.clear()

        # WebSocket-Verbindungen schließen
        for ws_connection in self._websocket_connections.values():
            await ws_connection.close()
        self._websocket_connections.clear()

    def get_metrics(self) -> Dict[str, Any]:
        """Holt A2A-Kommunikations-Metriken.

        Returns:
            A2A-Metriken
        """
        avg_response_time = (
            sum(self._response_times) / len(self._response_times)
            if self._response_times
            else 0.0
        )

        return {
            "message_count": self._message_count,
            "error_count": self._error_count,
            "error_rate": self._error_count / max(self._message_count, 1),
            "average_response_time_ms": avg_response_time,
            "active_http_sessions": len(self._http_sessions),
            "active_websocket_connections": len(self._websocket_connections),
            "failed_instances": len(self._failed_instances),
            "tracked_instances": len(self._instance_health),
            "service_discovery_enabled": self._service_discovery is not None,
            "load_balancer_enabled": self._load_balancer is not None,
        }
