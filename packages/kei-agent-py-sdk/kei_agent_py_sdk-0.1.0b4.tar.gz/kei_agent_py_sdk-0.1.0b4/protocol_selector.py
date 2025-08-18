# sdk/python/kei_agent/protocol_selector.py
"""
Intelligente Protokoll-Auswahl für KEI-Agent SDK.

Implementiert automatische Protokoll-Auswahl basierend auf Operation-Typ,
Performance-Anforderungen und Verfügbarkeit mit Fallback-Mechanismen.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Any
import logging

from protocol_types import ProtocolType, ProtocolConfig
from exceptions import ProtocolError

# Initialisiert Modul-Logger
_logger = logging.getLogger(__name__)


class ProtocolSelector:
    """Intelligente Protokoll-Auswahl für KEI-Agent Operationen.

    Analysiert Operation-Typ, Performance-Anforderungen und Protokoll-Verfügbarkeit
    um das optimale Protokoll für jede Operation zu bestimmen.

    Attributes:
        config: Protokoll-Konfiguration
        _operation_patterns: Mapping von Operation-Patterns zu bevorzugten Protokollen
        _protocol_priorities: Prioritäten für Fallback-Mechanismen
    """

    def __init__(self, config: ProtocolConfig) -> None:
        """Initialisiert Protocol Selector.

        Args:
            config: Protokoll-Konfiguration mit aktivierten Protokollen
        """
        self.config = config

        # Operation-Pattern zu Protokoll-Mapping
        self._operation_patterns = {
            # Streaming-Operationen
            "stream": ProtocolType.STREAM,
            "streaming": ProtocolType.STREAM,
            "realtime": ProtocolType.STREAM,
            "live": ProtocolType.STREAM,
            "subscribe": ProtocolType.STREAM,
            # Asynchrone Operationen
            "async": ProtocolType.BUS,
            "background": ProtocolType.BUS,
            "queue": ProtocolType.BUS,
            "publish": ProtocolType.BUS,
            "message": ProtocolType.BUS,
            "event": ProtocolType.BUS,
            # MCP-Operationen
            "tool": ProtocolType.MCP,
            "resource": ProtocolType.MCP,
            "prompt": ProtocolType.MCP,
            "discover": ProtocolType.MCP,
            "mcp": ProtocolType.MCP,
            # Standard RPC-Operationen
            "plan": ProtocolType.RPC,
            "act": ProtocolType.RPC,
            "observe": ProtocolType.RPC,
            "explain": ProtocolType.RPC,
            "sync": ProtocolType.RPC,
        }

        # Protokoll-Prioritäten für Fallback (höhere Zahl = höhere Priorität)
        self._protocol_priorities = {
            ProtocolType.RPC: 4,  # Höchste Priorität (am zuverlässigsten)
            ProtocolType.BUS: 3,  # Zweithöchste
            ProtocolType.MCP: 2,  # Mittlere Priorität
            ProtocolType.STREAM: 1,  # Niedrigste (am spezialisiertesten)
        }

        _logger.info(
            "Protocol Selector initialisiert",
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
        preferred_protocol: Optional[ProtocolType] = None,
    ) -> ProtocolType:
        """Wählt optimales Protokoll für Operation aus.

        Args:
            operation: Name der Operation
            context: Zusätzlicher Kontext für Protokoll-Auswahl
            preferred_protocol: Bevorzugtes Protokoll (überschreibt Auto-Auswahl)

        Returns:
            Ausgewähltes Protokoll

        Raises:
            ProtocolError: Wenn kein geeignetes Protokoll verfügbar ist
        """
        # Verwende bevorzugtes Protokoll wenn angegeben und verfügbar
        if preferred_protocol and self._is_protocol_available(preferred_protocol):
            _logger.debug(f"Verwende bevorzugtes Protokoll: {preferred_protocol}")
            return preferred_protocol

        # Automatische Protokoll-Auswahl wenn aktiviert
        if self.config.auto_protocol_selection:
            selected = self._auto_select_protocol(operation, context)
            if selected and self._is_protocol_available(selected):
                _logger.debug(f"Auto-Auswahl für '{operation}': {selected}")
                return selected

        # Fallback auf Standard-Protokoll
        fallback = self._get_fallback_protocol()
        if fallback:
            _logger.debug(f"Fallback-Protokoll für '{operation}': {fallback}")
            return fallback

        # Kein Protokoll verfügbar
        raise ProtocolError(
            f"Kein geeignetes Protokoll für Operation '{operation}' verfügbar"
        )

    def _auto_select_protocol(
        self, operation: str, context: Optional[Dict[str, Any]] = None
    ) -> Optional[ProtocolType]:
        """Automatische Protokoll-Auswahl basierend auf Operation und Kontext.

        Args:
            operation: Operation-Name
            context: Zusätzlicher Kontext

        Returns:
            Ausgewähltes Protokoll oder None
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
                return ProtocolType.STREAM

            # Asynchrone Indikatoren
            if any(key in context for key in ["async", "background", "queue", "delay"]):
                return ProtocolType.BUS

            # MCP-Indikatoren
            if any(
                key in context for key in ["tool", "resource", "prompt", "capability"]
            ):
                return ProtocolType.MCP

        # Standard-Fallback
        return ProtocolType.RPC

    def _is_protocol_available(self, protocol: ProtocolType) -> bool:
        """Prüft ob Protokoll verfügbar und aktiviert ist.

        Args:
            protocol: Zu prüfendes Protokoll

        Returns:
            True wenn Protokoll verfügbar ist
        """
        return self.config.is_protocol_enabled(protocol)

    def _get_fallback_protocol(self) -> Optional[ProtocolType]:
        """Ermittelt bestes verfügbares Fallback-Protokoll.

        Returns:
            Fallback-Protokoll mit höchster Priorität oder None
        """
        if not self.config.protocol_fallback_enabled:
            return None

        # Sortiere verfügbare Protokolle nach Priorität
        available_protocols = [
            protocol
            for protocol in self._protocol_priorities.keys()
            if self._is_protocol_available(protocol)
        ]

        if not available_protocols:
            return None

        # Wähle Protokoll mit höchster Priorität
        return max(available_protocols, key=lambda p: self._protocol_priorities[p])

    def get_fallback_chain(self, primary_protocol: ProtocolType) -> List[ProtocolType]:
        """Erstellt Fallback-Kette für Protokoll.

        Args:
            primary_protocol: Primäres Protokoll

        Returns:
            Liste von Protokollen in Fallback-Reihenfolge
        """
        if not self.config.protocol_fallback_enabled:
            return (
                [primary_protocol]
                if self._is_protocol_available(primary_protocol)
                else []
            )

        # Alle verfügbaren Protokolle außer dem primären
        fallback_protocols = [
            protocol
            for protocol in self._protocol_priorities.keys()
            if protocol != primary_protocol and self._is_protocol_available(protocol)
        ]

        # Sortiere nach Priorität (absteigend)
        fallback_protocols.sort(
            key=lambda p: self._protocol_priorities[p], reverse=True
        )

        # Primäres Protokoll an den Anfang
        chain = []
        if self._is_protocol_available(primary_protocol):
            chain.append(primary_protocol)
        chain.extend(fallback_protocols)

        return chain

    def analyze_operation_requirements(
        self, operation: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analysiert Anforderungen einer Operation für Protokoll-Auswahl.

        Args:
            operation: Operation-Name
            context: Zusätzlicher Kontext

        Returns:
            Dictionary mit Analyse-Ergebnissen
        """
        analysis = {
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

        # Analysiere Operation-Pattern
        operation_lower = operation.lower()

        # Streaming-Anforderungen
        if any(
            pattern in operation_lower
            for pattern in ["stream", "live", "realtime", "subscribe"]
        ):
            analysis["requirements"]["streaming"] = True
            analysis["requirements"]["realtime"] = True

        # Asynchrone Anforderungen
        if any(
            pattern in operation_lower
            for pattern in ["async", "background", "queue", "publish"]
        ):
            analysis["requirements"]["async"] = True

        # Tool-Anforderungen
        if any(
            pattern in operation_lower
            for pattern in ["tool", "resource", "prompt", "discover"]
        ):
            analysis["requirements"]["tools"] = True

        # Kontext-Analyse
        if context:
            if "callback" in context or "stream" in context:
                analysis["requirements"]["streaming"] = True
            if "async" in context or "background" in context:
                analysis["requirements"]["async"] = True
            if any(key in context for key in ["tool", "resource", "prompt"]):
                analysis["requirements"]["tools"] = True

        # Protokoll-Empfehlung
        recommended = self._auto_select_protocol(operation, context)
        if recommended:
            analysis["recommended_protocol"] = recommended
            analysis["fallback_chain"] = self.get_fallback_chain(recommended)

        return analysis

    def get_protocol_capabilities(self) -> Dict[ProtocolType, Dict[str, Any]]:
        """Gibt Capabilities aller verfügbaren Protokolle zurück.

        Returns:
            Dictionary mit Protokoll-Capabilities
        """
        capabilities = {}

        for protocol in self.config.get_enabled_protocols():
            if protocol == ProtocolType.RPC:
                capabilities[protocol] = {
                    "type": "synchronous",
                    "operations": ["plan", "act", "observe", "explain"],
                    "reliability": "high",
                    "latency": "low",
                    "throughput": "medium",
                }
            elif protocol == ProtocolType.STREAM:
                capabilities[protocol] = {
                    "type": "streaming",
                    "operations": ["subscribe", "publish", "realtime"],
                    "reliability": "medium",
                    "latency": "very_low",
                    "throughput": "high",
                }
            elif protocol == ProtocolType.BUS:
                capabilities[protocol] = {
                    "type": "asynchronous",
                    "operations": ["publish", "subscribe", "queue"],
                    "reliability": "high",
                    "latency": "medium",
                    "throughput": "very_high",
                }
            elif protocol == ProtocolType.MCP:
                capabilities[protocol] = {
                    "type": "tool_integration",
                    "operations": ["discover", "execute", "resource"],
                    "reliability": "high",
                    "latency": "medium",
                    "throughput": "medium",
                }

        return capabilities


__all__ = ["ProtocolSelector"]
