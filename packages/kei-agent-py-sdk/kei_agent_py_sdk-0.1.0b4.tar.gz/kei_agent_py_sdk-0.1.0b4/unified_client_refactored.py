# sdk/python/kei_agent/unified_client_refactored.py
"""
Refactored Unified KEI-Agent Client mit Enterprise-Grade Architektur.

Integriert alle KEI-Protokolle in einer einheitlichen API mit verbesserter
Code-Qualität, vollständigen Type Hints und Enterprise-Features.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Callable, Awaitable
import logging

from client import AgentClientConfig, KeiAgentClient
from protocol_types import ProtocolType, ProtocolConfig, SecurityConfig
from security_manager import SecurityManager
from protocol_clients import KEIRPCClient, KEIStreamClient, KEIBusClient, KEIMCPClient
from protocol_selector import ProtocolSelector
from exceptions import KeiSDKError, ProtocolError
from tracing import TracingManager
from retry import RetryManager
from capabilities import CapabilityManager
from discovery import ServiceDiscovery
from utils import create_correlation_id

# Initialisiert Modul-Logger
_logger = logging.getLogger(__name__)


class UnifiedKeiAgentClient:
    """Unified KEI-Agent Client mit vollständiger Protokoll-Integration.

    Bietet einheitliche API für alle KEI-Protokolle (RPC, Stream, Bus, MCP)
    mit automatischer Protokoll-Auswahl, Enterprise-Security und Monitoring.

    Attributes:
        config: Agent-Client-Konfiguration
        protocol_config: Protokoll-spezifische Konfiguration
        security_config: Sicherheitskonfiguration
        security: Security Manager für Authentifizierung
        protocol_selector: Intelligente Protokoll-Auswahl
        tracing: Distributed Tracing Manager
        retry_manager: Retry-Mechanismen und Circuit Breaker
        capability_manager: Capability Advertisement und Management
        service_discovery: Service Discovery für Agent-Registrierung
    """

    def __init__(
        self,
        config: AgentClientConfig,
        protocol_config: Optional[ProtocolConfig] = None,
        security_config: Optional[SecurityConfig] = None,
    ) -> None:
        """Initialisiert Unified KEI-Agent Client.

        Args:
            config: Basis-Konfiguration für Agent-Client
            protocol_config: Protokoll-spezifische Konfiguration
            security_config: Sicherheitskonfiguration

        Raises:
            KeiSDKError: Bei ungültiger Konfiguration
        """
        self.config = config
        self.protocol_config = protocol_config or ProtocolConfig()
        self.security_config = security_config or SecurityConfig(
            auth_type=self.protocol_config.auth_type
            if hasattr(self.protocol_config, "auth_type")
            else "bearer",
            api_token=config.api_token,
        )

        # Initialisiere Core-Komponenten
        self.security = SecurityManager(self.security_config)
        self.protocol_selector = ProtocolSelector(self.protocol_config)

        # Enterprise-Features
        self.tracing: Optional[TracingManager] = None
        self.retry_manager: Optional[RetryManager] = None
        self.capability_manager: Optional[CapabilityManager] = None
        self.service_discovery: Optional[ServiceDiscovery] = None

        # Protokoll-Clients
        self._rpc_client: Optional[KEIRPCClient] = None
        self._stream_client: Optional[KEIStreamClient] = None
        self._bus_client: Optional[KEIBusClient] = None
        self._mcp_client: Optional[KEIMCPClient] = None

        # Legacy Client für Kompatibilität
        self._legacy_client: Optional[KeiAgentClient] = None

        # Status-Tracking
        self._initialized = False
        self._closed = False

        _logger.info(
            "Unified KEI-Agent Client erstellt",
            extra={
                "agent_id": config.agent_id,
                "base_url": config.base_url,
                "enabled_protocols": self.protocol_config.get_enabled_protocols(),
            },
        )

    async def initialize(self) -> None:
        """Initialisiert Client und alle Komponenten.

        Startet Security Manager, initialisiert Protokoll-Clients und
        Enterprise-Features wie Tracing und Retry-Mechanismen.

        Raises:
            KeiSDKError: Bei Initialisierungsfehlern
        """
        if self._initialized:
            _logger.warning("Client bereits initialisiert")
            return

        try:
            _logger.info("Initialisiere Unified KEI-Agent Client")

            # Starte Security Manager
            await self.security.start_token_refresh()

            # Initialisiere Legacy Client für Kompatibilität
            self._legacy_client = KeiAgentClient(self.config)
            await self._legacy_client.initialize()

            # Initialisiere Protokoll-Clients
            await self._initialize_protocol_clients()

            # Initialisiere Enterprise-Features
            await self._initialize_enterprise_features()

            self._initialized = True
            _logger.info("Unified KEI-Agent Client erfolgreich initialisiert")

        except Exception as e:
            _logger.error(f"Client-Initialisierung fehlgeschlagen: {e}")
            raise KeiSDKError(f"Initialisierung fehlgeschlagen: {e}") from e

    async def _initialize_protocol_clients(self) -> None:
        """Initialisiert alle aktivierten Protokoll-Clients."""
        if self.protocol_config.rpc_enabled:
            self._rpc_client = KEIRPCClient(self.config.base_url, self.security)

        if self.protocol_config.stream_enabled:
            self._stream_client = KEIStreamClient(self.config.base_url, self.security)

        if self.protocol_config.bus_enabled:
            self._bus_client = KEIBusClient(self.config.base_url, self.security)

        if self.protocol_config.mcp_enabled:
            self._mcp_client = KEIMCPClient(self.config.base_url, self.security)

        _logger.debug("Protokoll-Clients initialisiert")

    async def _initialize_enterprise_features(self) -> None:
        """Initialisiert Enterprise-Features."""
        # Tracing Manager
        if hasattr(self.config, "tracing") and self.config.tracing:
            self.tracing = TracingManager(self.config.tracing)
            await self.tracing.initialize()

        # Retry Manager
        if hasattr(self.config, "retry") and self.config.retry:
            self.retry_manager = RetryManager(self.config.retry)

        # Capability Manager
        self.capability_manager = CapabilityManager(self.config.agent_id)

        # Service Discovery
        self.service_discovery = ServiceDiscovery(self.config.base_url, self.security)

        _logger.debug("Enterprise-Features initialisiert")

    async def close(self) -> None:
        """Schließt Client und alle Verbindungen.

        Stoppt alle Background-Tasks, schließt Protokoll-Clients und
        räumt Ressourcen auf.
        """
        if self._closed:
            return

        try:
            _logger.info("Schließe Unified KEI-Agent Client")

            # Stoppe Security Manager
            await self.security.stop_token_refresh()

            # Schließe Stream-Client
            if self._stream_client:
                await self._stream_client.disconnect()

            # Schließe Legacy Client
            if self._legacy_client:
                await self._legacy_client.close()

            # Schließe Tracing Manager
            if self.tracing:
                await self.tracing.shutdown()

            self._closed = True
            _logger.info("Unified KEI-Agent Client geschlossen")

        except Exception as e:
            _logger.error(f"Fehler beim Schließen des Clients: {e}")

    async def __aenter__(self):
        """Async Context Manager Eingang."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async Context Manager Ausgang."""
        await self.close()

    def _select_optimal_protocol(
        self, operation: str, context: Optional[Dict[str, Any]] = None
    ) -> ProtocolType:
        """Wählt optimales Protokoll für Operation aus.

        Args:
            operation: Name der Operation
            context: Zusätzlicher Kontext

        Returns:
            Ausgewähltes Protokoll
        """
        return self.protocol_selector.select_protocol(operation, context)

    def is_protocol_available(self, protocol: ProtocolType) -> bool:
        """Prüft ob Protokoll verfügbar ist.

        Args:
            protocol: Zu prüfendes Protokoll

        Returns:
            True wenn Protokoll verfügbar ist
        """
        if not self._initialized:
            return False

        protocol_clients = {
            ProtocolType.RPC: self._rpc_client,
            ProtocolType.STREAM: self._stream_client,
            ProtocolType.BUS: self._bus_client,
            ProtocolType.MCP: self._mcp_client,
        }

        return protocol_clients.get(protocol) is not None

    def get_available_protocols(self) -> List[ProtocolType]:
        """Gibt Liste verfügbarer Protokolle zurück.

        Returns:
            Liste verfügbarer Protokolle
        """
        available = []
        for protocol in [
            ProtocolType.RPC,
            ProtocolType.STREAM,
            ProtocolType.BUS,
            ProtocolType.MCP,
        ]:
            if self.is_protocol_available(protocol):
                available.append(protocol)
        return available

    def get_client_info(self) -> Dict[str, Any]:
        """Gibt Client-Informationen zurück.

        Returns:
            Dictionary mit Client-Status und Konfiguration
        """
        return {
            "agent_id": self.config.agent_id,
            "base_url": self.config.base_url,
            "initialized": self._initialized,
            "closed": self._closed,
            "available_protocols": self.get_available_protocols(),
            "security_context": self.security.get_security_context(),
            "features": {
                "tracing": self.tracing is not None,
                "retry_manager": self.retry_manager is not None,
                "capability_manager": self.capability_manager is not None,
                "service_discovery": self.service_discovery is not None,
            },
        }

    # ============================================================================
    # CORE EXECUTION METHODS
    # ============================================================================

    async def execute_agent_operation(
        self,
        operation: str,
        data: Dict[str, Any],
        protocol: Optional[ProtocolType] = None,
    ) -> Dict[str, Any]:
        """Führt Agent-Operation mit automatischer Protokoll-Auswahl aus.

        Args:
            operation: Name der Operation
            data: Operation-Daten
            protocol: Bevorzugtes Protokoll (optional)

        Returns:
            Operation-Response

        Raises:
            KeiSDKError: Bei Ausführungsfehlern
        """
        if not self._initialized:
            raise KeiSDKError("Client nicht initialisiert")

        # Wähle Protokoll aus
        selected_protocol = protocol or self._select_optimal_protocol(operation, data)

        # Erstelle Trace-Kontext
        correlation_id = create_correlation_id()

        try:
            # Führe Operation mit Tracing aus
            if self.tracing:
                with self.tracing.start_span(f"agent_operation_{operation}") as span:
                    span.set_attribute("operation", operation)
                    span.set_attribute("protocol", selected_protocol)
                    span.set_attribute("correlation_id", correlation_id)

                    return await self._execute_with_protocol(
                        selected_protocol, operation, data
                    )
            else:
                return await self._execute_with_protocol(
                    selected_protocol, operation, data
                )

        except Exception as e:
            _logger.error(
                f"Operation '{operation}' fehlgeschlagen",
                extra={
                    "operation": operation,
                    "protocol": selected_protocol,
                    "correlation_id": correlation_id,
                    "error": str(e),
                },
            )
            raise

    async def _execute_with_protocol(
        self, protocol: ProtocolType, operation: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Führt Operation mit spezifischem Protokoll aus.

        Args:
            protocol: Zu verwendendes Protokoll
            operation: Operation-Name
            data: Operation-Daten

        Returns:
            Operation-Response

        Raises:
            ProtocolError: Bei Protokoll-spezifischen Fehlern
        """
        try:
            if protocol == ProtocolType.RPC:
                return await self._execute_rpc_operation(operation, data)
            elif protocol == ProtocolType.STREAM:
                return await self._execute_stream_operation(operation, data)
            elif protocol == ProtocolType.BUS:
                return await self._execute_bus_operation(operation, data)
            elif protocol == ProtocolType.MCP:
                return await self._execute_mcp_operation(operation, data)
            else:
                raise ProtocolError(f"Unbekanntes Protokoll: {protocol}")

        except ProtocolError as e:
            # Versuche Fallback wenn aktiviert
            if self.protocol_config.protocol_fallback_enabled:
                fallback_chain = self.protocol_selector.get_fallback_chain(protocol)
                for fallback_protocol in fallback_chain[1:]:  # Skip primary protocol
                    try:
                        _logger.warning(
                            f"Fallback von {protocol} zu {fallback_protocol} für Operation '{operation}'"
                        )
                        return await self._execute_with_protocol(
                            fallback_protocol, operation, data
                        )
                    except Exception as e:
                        _logger.warning(
                            f"Fallback fehlgeschlagen mit {fallback_protocol}: {e}",
                            exc_info=True,
                        )
                        continue

            # Kein Fallback erfolgreich
            raise e

    async def _execute_rpc_operation(
        self, operation: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Führt RPC-Operation aus."""
        if not self._rpc_client:
            raise ProtocolError("RPC-Client nicht verfügbar")

        async with self._rpc_client as client:
            if operation == "plan":
                return await client.plan(data["objective"], data.get("context"))
            elif operation == "act":
                return await client.act(data["action"], data.get("parameters"))
            elif operation == "observe":
                return await client.observe(data["type"], data.get("data"))
            elif operation == "explain":
                return await client.explain(data["query"], data.get("context"))
            else:
                # Fallback auf Legacy Client
                return await self._legacy_client._make_request(
                    "POST", f"/api/v1/{operation}", data
                )

    async def _execute_stream_operation(
        self, operation: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Führt Stream-Operation aus."""
        if not self._stream_client:
            raise ProtocolError("Stream-Client nicht verfügbar")

        # Stream-Operationen sind meist asynchron
        if operation == "subscribe":
            await self._stream_client.subscribe(data["topic"], data["callback"])
            return {"status": "subscribed", "topic": data["topic"]}
        elif operation == "publish":
            await self._stream_client.publish(data["topic"], data["data"])
            return {"status": "published", "topic": data["topic"]}
        else:
            raise ProtocolError(f"Unbekannte Stream-Operation: {operation}")

    async def _execute_bus_operation(
        self, operation: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Führt Bus-Operation aus."""
        if not self._bus_client:
            raise ProtocolError("Bus-Client nicht verfügbar")

        async with self._bus_client as client:
            if operation == "send_message":
                message = {
                    "type": data["type"],
                    "target": data["target"],
                    "payload": data["payload"],
                }
                return await client.publish(message)
            elif operation == "subscribe":
                return await client.subscribe(data["topic"], data["agent_id"])
            else:
                # Generische Bus-Publish
                return await client.publish({"operation": operation, **data})

    async def _execute_mcp_operation(
        self, operation: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Führt MCP-Operation aus."""
        if not self._mcp_client:
            raise ProtocolError("MCP-Client nicht verfügbar")

        async with self._mcp_client as client:
            if operation == "discover_tools":
                tools = await client.discover_tools(data.get("category"))
                return {"tools": tools}
            elif operation == "use_tool":
                return await client.use_tool(data["tool_name"], data["parameters"])
            else:
                raise ProtocolError(f"Unbekannte MCP-Operation: {operation}")

    # ============================================================================
    # HIGH-LEVEL API METHODS
    # ============================================================================

    async def plan_task(
        self,
        objective: str,
        context: Optional[Dict[str, Any]] = None,
        protocol: Optional[ProtocolType] = None,
    ) -> Dict[str, Any]:
        """Erstellt Plan für gegebenes Ziel.

        Args:
            objective: Ziel-Beschreibung für Planung
            context: Zusätzlicher Kontext für Planung
            protocol: Bevorzugtes Protokoll (optional)

        Returns:
            Plan-Response mit Schritten und Metadaten

        Raises:
            KeiSDKError: Bei Plan-Erstellungsfehlern
        """
        return await self.execute_agent_operation(
            "plan", {"objective": objective, "context": context or {}}, protocol
        )

    async def execute_action(
        self,
        action: str,
        parameters: Optional[Dict[str, Any]] = None,
        protocol: Optional[ProtocolType] = None,
    ) -> Dict[str, Any]:
        """Führt Aktion aus.

        Args:
            action: Auszuführende Aktion
            parameters: Parameter für Aktion
            protocol: Bevorzugtes Protokoll (optional)

        Returns:
            Action-Response mit Ergebnis
        """
        return await self.execute_agent_operation(
            "act", {"action": action, "parameters": parameters or {}}, protocol
        )

    async def observe_environment(
        self,
        observation_type: str,
        data: Optional[Dict[str, Any]] = None,
        protocol: Optional[ProtocolType] = None,
    ) -> Dict[str, Any]:
        """Führt Umgebungsbeobachtung durch.

        Args:
            observation_type: Typ der Beobachtung
            data: Beobachtungsdaten
            protocol: Bevorzugtes Protokoll (optional)

        Returns:
            Observe-Response mit verarbeiteten Beobachtungen
        """
        return await self.execute_agent_operation(
            "observe", {"type": observation_type, "data": data or {}}, protocol
        )

    async def explain_reasoning(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        protocol: Optional[ProtocolType] = None,
    ) -> Dict[str, Any]:
        """Erklärt Reasoning für gegebene Anfrage.

        Args:
            query: Erklärungsanfrage
            context: Kontext für Erklärung
            protocol: Bevorzugtes Protokoll (optional)

        Returns:
            Explain-Response mit Erklärung und Reasoning
        """
        return await self.execute_agent_operation(
            "explain", {"query": query, "context": context or {}}, protocol
        )

    async def send_agent_message(
        self, target_agent: str, message_type: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Sendet Nachricht an anderen Agent (A2A-Kommunikation).

        Args:
            target_agent: Ziel-Agent-ID
            message_type: Typ der Nachricht
            payload: Nachrichtendaten

        Returns:
            Message-Response mit Status
        """
        return await self.execute_agent_operation(
            "send_message",
            {"target": target_agent, "type": message_type, "payload": payload},
            ProtocolType.BUS,  # Bus-Protokoll für A2A-Kommunikation
        )

    async def discover_available_tools(
        self, category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Entdeckt verfügbare MCP-Tools.

        Args:
            category: Optionale Tool-Kategorie für Filterung

        Returns:
            Liste verfügbarer Tools mit Metadaten
        """
        result = await self.execute_agent_operation(
            "discover_tools",
            {"category": category},
            ProtocolType.MCP,  # MCP-Protokoll für Tool-Discovery
        )

        # Extrahiere Tools aus Response
        return result.get("tools", [])

    async def use_tool(self, tool_name: str, **parameters: Any) -> Dict[str, Any]:
        """Führt MCP-Tool aus.

        Args:
            tool_name: Name des auszuführenden Tools
            **parameters: Tool-Parameter als Keyword-Arguments

        Returns:
            Tool-Execution-Response
        """
        return await self.execute_agent_operation(
            "use_tool",
            {"tool_name": tool_name, "parameters": parameters},
            ProtocolType.MCP,  # MCP-Protokoll für Tool-Execution
        )

    async def start_streaming_session(
        self, callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None
    ) -> None:
        """Startet Streaming-Session für Echtzeit-Kommunikation.

        Args:
            callback: Callback für eingehende Stream-Nachrichten

        Raises:
            ProtocolError: Wenn Stream-Protokoll nicht verfügbar ist
        """
        if not self.is_protocol_available(ProtocolType.STREAM):
            raise ProtocolError("Stream-Protokoll nicht verfügbar")

        if self._stream_client:
            await self._stream_client.connect()
            if callback:
                await self._stream_client.subscribe("agent_events", callback)

    async def health_check(self) -> Dict[str, Any]:
        """Führt Health-Check durch.

        Returns:
            Health-Status mit Protokoll-Verfügbarkeit
        """
        return await self.execute_agent_operation("health_check", {})

    async def register_agent(
        self,
        name: str,
        version: str,
        description: str = "",
        capabilities: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Registriert Agent im KEI-Framework.

        Args:
            name: Agent-Name
            version: Agent-Version
            description: Agent-Beschreibung
            capabilities: Agent-Capabilities

        Returns:
            Registrierungs-Response
        """
        return await self.execute_agent_operation(
            "register",
            {
                "name": name,
                "version": version,
                "description": description,
                "capabilities": capabilities or [],
            },
        )


__all__ = ["UnifiedKeiAgentClient"]
