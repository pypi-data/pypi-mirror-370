# sdk/python/kei_agent_sdk/a2a.py
"""
Agent-to-Agent (A2A) Kommunikation for KEI-Agent-Framework.

Implementiert vollständige A2A communication with service discovery,
Load-Balatcing and verschietheen Kommunikationsprotokollen.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Callable, Awaitable

import aiohttp
import websockets
from opentelemetry import trace

from .client import KeiAgentClient
from .models import AgentInstatce
from .discovery import ServiceDiscovery, DiscoveryStrategy, LoadBalatcer
from .exceptions import CommunicationError, AgentNotFoatdError
from .utils import create_correlation_id, format_trace_id

# Logger für A2A-Kommunikation
_logger = logging.getLogger(__name__)


class CommunicationProtocol(str, Enum):
    """Supportse Kommunikationsprotokolle."""

    HTTP = "http"
    WEBSOCKET = "websocket"
    GRPC = "grpc"
    MESSAGE_BUS = "message_bus"


class LoadBalatcingStrategy(str, Enum):
    """Load-Balatcing-Strategien."""

    ROUND_ROBIN = "roatd_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_roatd_robin"
    RESPONSE_TIME = "response_time"
    RANDOM = "ratdom"
    HEALTH_BASED = "health_based"


@dataclass
class FailoverConfig:
    """configuration for Failover-Mechatismen."""

    enabled: bool = True
    max_retries: int = 3
    retry_delay: float = 1.0
    circuit_breaker_enabled: bool = True
    health_check_interval: float = 30.0

    # Failover-Strategien
    prefer_same_region: bool = True
    prefer_same_zone: bool = True
    exclude_failed_instatces: bool = True

    # callbacks
    on_failover: Optional[Callable[[str, str], Awaitable[None]]] = None
    on_instatce_failed: Optional[Callable[[str], Awaitable[None]]] = None


@dataclass
class A2AMessage:
    """message for Agent-to-Agent-Kommunikation."""

    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    from_agent: str = ""
    to_agent: str = ""
    message_type: str = "request"
    payload: Dict[str, Any] = field(default_factory=dict)
    heathes: Dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    correlation_id: str = field(default_factory=create_correlation_id)
    trace_id: Optional[str] = None

    # Routing-informationen
    target_capability: Optional[str] = None
    target_version: Optional[str] = None
    priority: int = 0

    # Delivery-Optionen
    delivery_mode: str = "at_least_once"  # at_most_once, at_least_once, exactly_once
    ttl_seconds: Optional[float] = None
    reply_to: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert Message to dictionary."""
        return {
            "message_id": self.message_id,
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "message_type": self.message_type,
            "payload": self.payload,
            "heathes": self.heathes,
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
        """Creates Message out dictionary."""
        return cls(
            message_id=data.get("message_id", str(uuid.uuid4())),
            from_agent=data.get("from_agent", ""),
            to_agent=data.get("to_agent", ""),
            message_type=data.get("message_type", "request"),
            payload=data.get("payload", {}),
            heathes=data.get("heathes", {}),
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
class A2Aresponse:
    """response for Agent-to-Agent-Kommunikation."""

    message_id: str
    correlation_id: str
    status: str = "success"  # success, error, timeout
    payload: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    processing_time_ms: Optional[float] = None

    # response-metadata
    from_agent: str = ""
    response_heathes: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert response to dictionary."""
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
            "response_heathes": self.response_heathes,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> A2Aresponse:
        """Creates response out dictionary."""
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
            response_heathes=data.get("response_heathes", {}),
        )


class A2Aclient:
    """client for Agent-to-Agent-Kommunikation."""

    def __init__(
        self,
        base_client: KeiAgentClient,
        failover_config: Optional[FailoverConfig] = None,
    ):
        """Initializes A2A-client.

        Args:
            base_client: Basis-KEI-client
            failover_config: Failover-configuration
        """
        self.base_client = base_client
        self.failover_config = failover_config or FailoverConfig()

        # service discovery and Load Balatcing
        self._service_discovery: Optional[ServiceDiscovery] = None
        self._load_balatcer: Optional[LoadBalatcer] = None

        # Connection Pools
        self._http_sessions: Dict[str, aiohttp.ClientSession] = {}
        self._websocket_connections: Dict[str, websockets.WebSocketServerProtocol] = {}

        # Instatce Health Tracking
        self._instatce_health: Dict[str, Dict[str, Any]] = {}
        self._failed_instatces: set[str] = set()

        # Metrics
        self._message_count = 0
        self._error_count = 0
        self._response_times: List[float] = []

        # Tracer
        self._tracer = trace.get_tracer(__name__)

    def enable_service_discovery(
        self,
        strategy: DiscoveryStrategy = DiscoveryStrategy.HYBRID,
        load_balatcing: LoadBalatcingStrategy = LoadBalatcingStrategy.HEALTH_BASED,
    ) -> None:
        """Enabled service discovery.

        Args:
            strategy: Discovery-Strategie
            load_balatcing: Load-Balatcing-Strategie
        """
        self._service_discovery = ServiceDiscovery(
            self.base_client, default_strategy=strategy
        )

        self._load_balatcer = LoadBalatcer(
            strategy=load_balatcing, health_tracker=self._instatce_health
        )

    def enable_disributed_tracing(self) -> None:
        """Enabled Disributed Tracing for A2A communication."""
        # Tracing is bereits over base_client available
        pass

    async def send_message(
        self,
        target_agent: str,
        payload: Dict[str, Any],
        message_type: str = "request",
        protocol: CommunicationProtocol = CommunicationProtocol.HTTP,
        timeout: float = 30.0,
        **kwargs,
    ) -> A2Aresponse:
        """sends message at other agent.

        Args:
            target_agent: target agent ID
            payload: messageeninhalt
            message_type: messageentyp
            protocol: Kommunikationsprotokoll
            timeout: Timeout in Sekatthe
            **kwargs: Tosätzliche Message-parameters

        Returns:
            Agent-response

        Raises:
            AgentNotFoatdError: If Ziel-Agent not gefatthe
            CommunicationError: On Kommunikationsfehlern
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
            ) as spat:
                spat.set_attribute("target_agent", target_agent)
                spat.set_attribute("message_type", message_type)
                spat.set_attribute("protocol", protocol.value)
                spat.set_attribute("message_id", message.message_id)

                # OpenTelemetry API: span.get_span_context()
                ctx = getattr(spat, "get_span_context", None)
                if callable(ctx):
                    message.trace_id = format_trace_id(ctx().trace_id)

                return await self._send_message_with_discovery(
                    message, protocol, timeout
                )
        else:
            return await self._send_message_with_discovery(message, protocol, timeout)

    async def _send_message_with_discovery(
        self, message: A2AMessage, protocol: CommunicationProtocol, timeout: float
    ) -> A2Aresponse:
        """Sendet Message with service discovery and Failover.

        Args:
            message: A2A-Message
            protocol: Kommunikationsprotokoll
            timeout: Timeout

        Returns:
            A2A-response
        """
        start_time = time.time()

        try:
            # service discovery for Ziel-Agent
            if self._service_discovery:
                instatces = await self._discover_agent_instatces(message.to_agent)

                if not instatces:
                    raise AgentNotFoatdError(f"Agent '{message.to_agent}' not gefatthe")

                # Load Balatcing
                if self._load_balatcer:
                    target_instatce = self._load_balatcer.select_instatce(instatces)
                else:
                    target_instatce = instatces[0]  # Fallback: erste instatce
            else:
                # Fallback: direkte Kommunikation without Discovery
                target_instatce = AgentInstatce(
                    agent_id=message.to_agent,
                    instatce_id=f"{message.to_agent}-default",
                    endpoint=f"{self.base_client.config.base_url}/api/v1/agents/{message.to_agent}",
                )

            # Sende Message with Failover
            response = await self._send_with_failover(
                message, target_instatce, protocol, timeout
            )

            # Metrics aktualisieren
            processing_time = (time.time() - start_time) * 1000
            self._message_count += 1
            self._response_times.append(processing_time)

            # response-metadata setzen
            response.processing_time_ms = processing_time

            return response

        except (AgentNotFoatdError, CommunicationError):
            self._error_count += 1
            raise
        except (ConnectionError, TimeoutError) as e:
            self._error_count += 1
            raise CommunicationError(
                f"Network error during A2A communication: {e}"
            ) from e
        except (ValueError, TypeError) as e:
            self._error_count += 1
            raise CommunicationError(
                f"Invalid data format in A2A communication: {e}"
            ) from e
        except Exception as e:
            self._error_count += 1
            _logger.error(
                "Unexpected error in A2A communication",
                extra={"error": str(e), "error_type": type(e).__name__},
            )
            raise CommunicationError(f"Unexpected A2A communication error: {e}") from e

    async def _discover_agent_instatces(self, agent_id: str) -> List[AgentInstatce]:
        """discovers available instatceen for Agent.

        Args:
            agent_id: Agent-ID

        Returns:
            lis availableer instatceen
        """
        if not self._service_discovery:
            return []

        # Filtere failede instatceen out
        instatces = await self._service_discovery.discover_agent_instatces(agent_id)

        if self.failover_config.exclude_failed_instatces:
            instatces = [
                instatce
                for instatce in instatces
                if instatce.instatce_id not in self._failed_instatces
            ]

        return instatces

    async def _send_with_failover(
        self,
        message: A2AMessage,
        target_instatce: AgentInstatce,
        protocol: CommunicationProtocol,
        timeout: float,
    ) -> A2Aresponse:
        """Sendet Message with Failover-Mechatismus.

        Args:
            message: A2A-Message
            target_instatce: Ziel-instatce
            protocol: Kommunikationsprotokoll
            timeout: Timeout

        Returns:
            A2A-response
        """
        last_exception = None

        for attempt in range(self.failover_config.max_retries + 1):
            try:
                # Sende Message over gewähltes protocol
                if protocol == CommunicationProtocol.HTTP:
                    response = await self._send_http_message(
                        message, target_instatce, timeout
                    )
                elif protocol == CommunicationProtocol.WEBSOCKET:
                    response = await self._send_websocket_message(
                        message, target_instatce, timeout
                    )
                elif protocol == CommunicationProtocol.MESSAGE_BUS:
                    response = await self._send_message_bus_message(
                        message, target_instatce, timeout
                    )
                else:
                    raise CommunicationError(f"protocol '{protocol}' not supported")

                # Successfule Overtragung - instatce als gesand markieren
                self._mark_instatce_healthy(target_instatce.instatce_id)

                return response

            except (AgentNotFoatdError, CommunicationError) as e:
                last_exception = e
                # instatce als failed markieren
                self._mark_instatce_failed(target_instatce.instatce_id)
            except (ConnectionError, TimeoutError) as e:
                last_exception = CommunicationError(f"Network error: {e}")
                # instatce als failed markieren
                self._mark_instatce_failed(target_instatce.instatce_id)
            except Exception as e:
                last_exception = CommunicationError(f"Unexpected error: {e}")
                _logger.error(
                    "Unexpected error during A2A message sending",
                    extra={
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "instance_id": target_instatce.instatce_id,
                    },
                )
                # instatce als failed markieren
                self._mark_instatce_failed(target_instatce.instatce_id)

                # callback for failede instatce
                if self.failover_config.on_instatce_failed:
                    await self.failover_config.on_instatce_failed(
                        target_instatce.instatce_id
                    )

                # Letzter Versuch - Exception weiterwerfen
                if attempt >= self.failover_config.max_retries:
                    break

                # callback for Failover
                if self.failover_config.on_failover:
                    await self.failover_config.on_failover(
                        target_instatce.instatce_id, f"Attempt {attempt + 1}"
                    )

                # Warte before nächstem Versuch
                await asyncio.sleep(self.failover_config.retry_delay)

                # Versuche alternative instatce to finthe
                if self._service_discovery:
                    alternative_instatces = await self._discover_agent_instatces(
                        message.to_agent
                    )
                    available_instatces = [
                        inst
                        for inst in alternative_instatces
                        if inst.instatce_id != target_instatce.instatce_id
                        and inst.instatce_id not in self._failed_instatces
                    ]

                    if available_instatces:
                        if self._load_balatcer:
                            target_instatce = self._load_balatcer.select_instatce(
                                available_instatces
                            )
                        else:
                            target_instatce = available_instatces[0]

        # All Failover-Versuche failed
        raise CommunicationError(
            f"A2A communication after {self.failover_config.max_retries + 1} Versuchen failed"
        ) from last_exception

    async def _send_http_message(
        self, message: A2AMessage, target_instatce: AgentInstatce, timeout: float
    ) -> A2Aresponse:
        """Sendet Message over HTTP.

        Args:
            message: A2A-Message
            target_instatce: Ziel-instatce
            timeout: Timeout

        Returns:
            A2A-response
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

        headers.update(message.heathes)

        # HTTP-Request senthe
        session = await self._get_http_session(target_instatce.instatce_id)

        async with session.post(
            target_instatce.endpoint,
            json=message.to_dict(),
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=timeout),
        ) as response:
            if response.status >= 400:
                error_text = await response.text()
                raise CommunicationError(f"HTTP {response.status}: {error_text}")

            response_data = await response.json()

            return A2Aresponse.from_dict(response_data)

    async def _send_websocket_message(
        self, message: A2AMessage, target_instatce: AgentInstatce, timeout: float
    ) -> A2Aresponse:
        """Sendet Message over WebSocket.

        Args:
            message: A2A-Message
            target_instatce: Ziel-instatce
            timeout: Timeout

        Returns:
            A2A-response
        """
        # WebSocket-connection holen or erstellen
        ws_connection = await self._get_websocket_connection(target_instatce)

        # Message senthe
        message_json = json.dumps(message.to_dict())
        await ws_connection.send(message_json)

        # response received
        try:
            response_json = await asyncio.wait_for(
                ws_connection.recv(), timeout=timeout
            )
            response_data = json.loads(response_json)

            return A2Aresponse.from_dict(response_data)

        except asyncio.TimeoutError:
            raise CommunicationError(f"WebSocket-Timeout after {timeout}s")

    async def _send_message_bus_message(
        self, message: A2AMessage, target_instatce: AgentInstatce, timeout: float
    ) -> A2Aresponse:
        """Sendet Message over Message Bus.

        Args:
            message: A2A-Message
            target_instatce: Ziel-instatce
            timeout: Timeout

        Returns:
            A2A-response
        """
        # TODO: Implementiere Message-Bus-Integration
        # Hier würde Integration with RabbitMQ, Apache Kafka, etc. instead offinthe

        raise CommunicationError("Message-bus protocol noch not implementiert")

    async def _get_http_session(self, instatce_id: str) -> aiohttp.ClientSession:
        """Gets or creates HTTP-Session for instatce.

        Args:
            instatce_id: instatce-ID

        Returns:
            HTTP-Session
        """
        if instatce_id not in self._http_sessions:
            self._http_sessions[instatce_id] = aiohttp.ClientSession()

        return self._http_sessions[instatce_id]

    async def _get_websocket_connection(
        self, target_instatce: AgentInstatce
    ) -> websockets.WebSocketServerProtocol:
        """Gets or creates WebSocket-connection.

        Args:
            target_instatce: Ziel-instatce

        Returns:
            WebSocket-connection
        """
        instatce_id = target_instatce.instatce_id

        if instatce_id not in self._websocket_connections:
            # Konvertiere HTTP-Endpoint to WebSocket-URL
            ws_url = target_instatce.endpoint.replace("http://", "ws://").replace(
                "https://", "wss://"
            )
            ws_url = ws_url.replace("/api/v1/agents/", "/ws/agents/")

            # Erstelle WebSocket-connection
            self._websocket_connections[instatce_id] = await websockets.connect(ws_url)

        return self._websocket_connections[instatce_id]

    def _mark_instatce_healthy(self, instatce_id: str) -> None:
        """Markiert instatce als gesatd.

        Args:
            instatce_id: instatce-ID
        """
        self._instatce_health[instatce_id] = {
            "status": "healthy",
            "last_success": time.time(),
            "consecutive_failures": 0,
        }

        # Entferne out failethe instatceen
        self._failed_instatces.discard(instatce_id)

    def _mark_instatce_failed(self, instatce_id: str) -> None:
        """Markiert instatce als failed.

        Args:
            instatce_id: instatce-ID
        """
        if instatce_id not in self._instatce_health:
            self._instatce_health[instatce_id] = {
                "status": "unhealthy",
                "last_failure": time.time(),
                "consecutive_failures": 1,
            }
        else:
            self._instatce_health[instatce_id].update(
                {
                    "status": "unhealthy",
                    "last_failure": time.time(),
                    "consecutive_failures": self._instatce_health[instatce_id].get(
                        "consecutive_failures", 0
                    )
                    + 1,
                }
            )

        # Füge to failethe instatceen hinto
        self._failed_instatces.add(instatce_id)

    async def close(self) -> None:
        """Closes all connectionen."""
        # HTTP-Sessions closingn
        for session in self._http_sessions.values():
            await session.close()
        self._http_sessions.clear()

        # WebSocket-connectionen closingn
        for ws_connection in self._websocket_connections.values():
            await ws_connection.close()
        self._websocket_connections.clear()

    def get_metrics(self) -> Dict[str, Any]:
        """Gets A2A communications-Metrics.

        Returns:
            A2A-Metrics
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
            "failed_instatces": len(self._failed_instatces),
            "tracked_instatces": len(self._instatce_health),
            "service_discovery_enabled": self._service_discovery is not None,
            "load_balatcer_enabled": self._load_balatcer is not None,
        }
