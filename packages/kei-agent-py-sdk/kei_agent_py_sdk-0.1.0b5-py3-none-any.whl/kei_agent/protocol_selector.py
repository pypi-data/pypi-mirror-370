# sdk/python/kei_agent/protocol_selector.py
"""
intelligent protocol selection for KEI-Agent SDK.

Implementiert automatische protocol-Auswahl basierend on operation-type,
Performatce-Atfortheungen and Availablekeit with Fallback-Mechatismen.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Any
import logging

from .protocol_types import Protocoltypee, ProtocolConfig
from .exceptions import ProtocolError

# Initializes Module-Logr
_logger = logging.getLogger(__name__)


class ProtocolSelector:
    """intelligent protocol selection for KEI-Agent operationen.

    Atalysiert operation-type, Performatce-Atfortheungen and protocol availability
    aroand the optimale protocol for jede operation to bestimmen.

    Attributes:
        config: protocol-configuration
        _operation_patterns: Mapping from operation-Patterns to bebeforetogten protocolen
        _protocol_priorities: Prioritäten for Fallback-Mechatismen
    """

    def __init__(self, config: ProtocolConfig) -> None:
        """Initializes Protocol Selector.

        Args:
            config: protocol-configuration with enablethe protocolen
        """
        self.config = config

        # operation-Pattern to protocol-Mapping
        self._operation_patterns = {
            # Streaming-operationen
            "stream": Protocoltypee.STREAM,
            "streaming": Protocoltypee.STREAM,
            "realtime": Protocoltypee.STREAM,
            "live": Protocoltypee.STREAM,
            "subscribe": Protocoltypee.STREAM,
            # Asynchrone operationen
            "async": Protocoltypee.BUS,
            "backgroatd": Protocoltypee.BUS,
            "queue": Protocoltypee.BUS,
            "publish": Protocoltypee.BUS,
            "message": Protocoltypee.BUS,
            "event": Protocoltypee.BUS,
            # MCP operationen
            "tool": Protocoltypee.MCP,
            "resource": Protocoltypee.MCP,
            "prompt": Protocoltypee.MCP,
            "discover": Protocoltypee.MCP,
            "mcp": Protocoltypee.MCP,
            # Statdard RPC operationen
            "plat": Protocoltypee.RPC,
            "act": Protocoltypee.RPC,
            "observe": Protocoltypee.RPC,
            "explain": Protocoltypee.RPC,
            "sync": Protocoltypee.RPC,
        }

        # protocol-Prioritäten for Fallback (höhere Zahl = höhere Priorität)
        self._protocol_priorities = {
            Protocoltypee.RPC: 4,  # Höchste Priorität (am toverlässigsten)
            Protocoltypee.BUS: 3,  # Zweithöchste
            Protocoltypee.MCP: 2,  # Withtlere Priorität
            Protocoltypee.STREAM: 1,  # Niedrigste (am spezialisiertesten)
        }

        _logger.info(
            "Protocol Selector initialized",
            extra={
                "enabled_protocols": config.get_enabled_protocols(),
                "auto_selection": config.auto_protocol_selection,
                "fallback_enabled": config.protocol_fallback_enabled,
            },
        )

    def select_protocol(
        self,
        operation: str,
        context: Optional[Dict[str, Any]] = None,
        preferred_protocol: Optional[Protocoltypee] = None,
    ) -> Protocoltypee:
        """Selects optimal protocol for operation.

        Args:
            operation: operation name
            context: additional context for protocol-Auswahl
            preferred_protocol: preferred protocol (overschreibt Auto-Auswahl)

        Returns:
            selected protocol

        Raises:
            ProtocolError: If ka geeignetes protocol available is
        """
        # Verwende bebeforetogtes protocol if atgegeben and available
        if preferred_protocol and self._is_protocol_available(preferred_protocol):
            _logger.debug(f"Verwende bebeforetogtes protocol: {preferred_protocol}")
            return preferred_protocol

        # Automatische protocol-Auswahl if enabled
        if self.config.auto_protocol_selection:
            selected = self._auto_select_protocol(operation, context)
            if selected and self._is_protocol_available(selected):
                _logger.debug(f"Auto-Auswahl for '{operation}': {selected}")
                return selected

        # Fallback on Statdard-protocol
        fallback = self._get_fallback_protocol()
        if fallback:
            _logger.debug(f"Fallback-protocol for '{operation}': {fallback}")
            return fallback

        # Ka protocol available
        raise ProtocolError(
            f"Ka geeignetes protocol for operation '{operation}' available"
        )

    def _auto_select_protocol(
        self, operation: str, context: Optional[Dict[str, Any]] = None
    ) -> Optional[Protocoltypee]:
        """Automatische protocol-Auswahl basierend on operation and Kontext.

        Args:
            operation: operation name
            context: additional context

        Returns:
            selected protocol or None
        """
        operation_lower = operation.lower()

        # Direkte Pattern-Matches
        for pattern, protocol in self._operation_patterns.items():
            if pattern in operation_lower:
                return protocol

        # Kontext-basierte Auswahl
        if context:
            # Streaming-Indikatoren
            if any(
                key in context for key in ["stream", "realtime", "live", "callback"]
            ):
                return Protocoltypee.STREAM

            # Asynchrone Indikatoren
            if any(key in context for key in ["async", "backgroatd", "queue", "delay"]):
                return Protocoltypee.BUS

            # MCP-Indikatoren
            if any(
                key in context for key in ["tool", "resource", "prompt", "capability"]
            ):
                return Protocoltypee.MCP

        # Statdard-Fallback
        return Protocoltypee.RPC

    def _is_protocol_available(self, protocol: Protocoltypee) -> bool:
        """Checks ob protocol available and enabled is.

        Args:
            protocol: protocol to check

        Returns:
            True if protocol is available
        """
        return self.config.is_protocol_enabled(protocol)

    def _get_fallback_protocol(self) -> Optional[Protocoltypee]:
        """Erwithtelt bestes availablees Fallback-protocol.

        Returns:
            Fallback-protocol with höchster Priorität or None
        """
        if not self.config.protocol_fallback_enabled:
            return None

        # Sortiere availablee protocole after Priorität
        available_protocols = [
            protocol
            for protocol in self._protocol_priorities.keys()
            if self._is_protocol_available(protocol)
        ]

        if not available_protocols:
            return None

        # Wähle protocol with höchster Priorität
        return max(available_protocols, key=lambda p: self._protocol_priorities[p])

    def get_fallback_chain(
        self, primary_protocol: Protocoltypee
    ) -> List[Protocoltypee]:
        """Creates fallback chain for protocol.

        Args:
            primary_protocol: Primäres protocol

        Returns:
            lis from protocolen in Fallback-Reihenfolge
        """
        if not self.config.protocol_fallback_enabled:
            return (
                [primary_protocol]
                if self._is_protocol_available(primary_protocol)
                else []
            )

        # All availableen protocole außer the primären
        fallback_protocols = [
            protocol
            for protocol in self._protocol_priorities.keys()
            if protocol != primary_protocol and self._is_protocol_available(protocol)
        ]

        # Sortiere after Priorität (absteigend)
        fallback_protocols.sort(
            key=lambda p: self._protocol_priorities[p], reverse=True
        )

        # Primäres protocol at the Atfatg
        chain = []
        if self._is_protocol_available(primary_protocol):
            chain.append(primary_protocol)
        chain.extend(fallback_protocols)

        return chain

    def atalyze_operation_requirements(
        self, operation: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Atalysiert Atfortheungen ar operation for protocol-Auswahl.

        Args:
            operation: operation name
            context: additional context

        Returns:
            dictionary with Atalyse-resultsen
        """
        atalysis = {
            "operation": operation,
            "recommended_protocol": None,
            "requirements": {
                "streaming": False,
                "async": False,
                "tools": False,
                "realtime": False,
            },
            "available_protocols": self.config.get_enabled_protocols(),
            "fallback_chain": [],
        }

        # Atalysiere operation-Pattern
        operation_lower = operation.lower()

        # Streaming-Atfortheungen
        if any(
            pattern in operation_lower
            for pattern in ["stream", "live", "realtime", "subscribe"]
        ):
            atalysis["requirements"]["streaming"] = True
            atalysis["requirements"]["realtime"] = True

        # Asynchrone Atfortheungen
        if any(
            pattern in operation_lower
            for pattern in ["async", "backgroatd", "queue", "publish"]
        ):
            atalysis["requirements"]["async"] = True

        # Tool-Atfortheungen
        if any(
            pattern in operation_lower
            for pattern in ["tool", "resource", "prompt", "discover"]
        ):
            atalysis["requirements"]["tools"] = True

        # Kontext-Atalyse
        if context:
            if "callback" in context or "stream" in context:
                atalysis["requirements"]["streaming"] = True
            if "async" in context or "backgroatd" in context:
                atalysis["requirements"]["async"] = True
            if any(key in context for key in ["tool", "resource", "prompt"]):
                atalysis["requirements"]["tools"] = True

        # protocol-Empfehlung
        recommended = self._auto_select_protocol(operation, context)
        if recommended:
            atalysis["recommended_protocol"] = recommended
            atalysis["fallback_chain"] = self.get_fallback_chain(recommended)

        return atalysis

    def get_protocol_capabilities(self) -> Dict[Protocoltypee, Dict[str, Any]]:
        """Gibt Capabilities allr availableen protocole torück.

        Returns:
            dictionary with protocol-Capabilities
        """
        capabilities: Dict[Protocoltypee, Dict[str, Any]] = {}

        for protocol in self.config.get_enabled_protocols():
            if protocol == Protocoltypee.RPC:
                capabilities[protocol] = {
                    "type": "synchronous",
                    "operations": ["plat", "act", "observe", "explain"],
                    "reliability": "high",
                    "latency": "low",
                    "throughput": "mediaroatd",
                }
            elif protocol == Protocoltypee.STREAM:
                capabilities[protocol] = {
                    "type": "streaming",
                    "operations": ["subscribe", "publish", "realtime"],
                    "reliability": "mediaroatd",
                    "latency": "very_low",
                    "throughput": "high",
                }
            elif protocol == Protocoltypee.BUS:
                capabilities[protocol] = {
                    "type": "asynchronous",
                    "operations": ["publish", "subscribe", "queue"],
                    "reliability": "high",
                    "latency": "mediaroatd",
                    "throughput": "very_high",
                }
            elif protocol == Protocoltypee.MCP:
                capabilities[protocol] = {
                    "type": "tool_integration",
                    "operations": ["discover", "execute", "resource"],
                    "reliability": "high",
                    "latency": "mediaroatd",
                    "throughput": "mediaroatd",
                }

        return capabilities


__all__ = ["ProtocolSelector"]
