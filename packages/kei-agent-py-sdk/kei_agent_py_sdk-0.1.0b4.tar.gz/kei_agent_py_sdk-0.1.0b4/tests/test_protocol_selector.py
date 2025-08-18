# sdk/python/kei_agent/tests/test_protocol_selector.py
"""
Unit Tests für Protocol Selector.

Testet intelligente Protokoll-Auswahl, Fallback-Mechanismen und
Operation-Analyse mit verschiedenen Konfigurationen.
"""

import pytest

from protocol_selector import ProtocolSelector
from protocol_types import ProtocolType, ProtocolConfig
from exceptions import ProtocolError

# Markiere alle Tests in dieser Datei als Protokoll-Tests
pytestmark = pytest.mark.protocol


class TestProtocolSelector:
    """Tests für ProtocolSelector Klasse."""

    @pytest.fixture
    def full_config(self):
        """Erstellt Konfiguration mit allen Protokollen aktiviert."""
        return ProtocolConfig(
            rpc_enabled=True,
            stream_enabled=True,
            bus_enabled=True,
            mcp_enabled=True,
            auto_protocol_selection=True,
            protocol_fallback_enabled=True,
        )

    @pytest.fixture
    def limited_config(self):
        """Erstellt Konfiguration mit nur RPC und Bus aktiviert."""
        return ProtocolConfig(
            rpc_enabled=True,
            stream_enabled=False,
            bus_enabled=True,
            mcp_enabled=False,
            auto_protocol_selection=True,
            protocol_fallback_enabled=True,
        )

    @pytest.fixture
    def no_fallback_config(self):
        """Erstellt Konfiguration ohne Fallback."""
        return ProtocolConfig(
            rpc_enabled=True,
            stream_enabled=True,
            bus_enabled=True,
            mcp_enabled=True,
            auto_protocol_selection=True,
            protocol_fallback_enabled=False,
        )

    def test_initialization(self, full_config):
        """Testet Initialisierung des Protocol Selectors."""
        selector = ProtocolSelector(full_config)

        assert selector.config == full_config
        assert len(selector._operation_patterns) > 0
        assert len(selector._protocol_priorities) == 4

    def test_select_protocol_preferred_available(self, full_config):
        """Testet Protokoll-Auswahl mit verfügbarem bevorzugtem Protokoll."""
        selector = ProtocolSelector(full_config)

        result = selector.select_protocol(
            "test_operation", preferred_protocol=ProtocolType.STREAM
        )

        assert result == ProtocolType.STREAM

    def test_select_protocol_preferred_unavailable(self, limited_config):
        """Testet Protokoll-Auswahl mit nicht verfügbarem bevorzugtem Protokoll."""
        selector = ProtocolSelector(limited_config)

        # Stream ist nicht verfügbar, sollte auf Auto-Auswahl fallen
        result = selector.select_protocol(
            "plan",  # RPC-Operation
            preferred_protocol=ProtocolType.STREAM,
        )

        assert result == ProtocolType.RPC

    def test_auto_select_streaming_operations(self, full_config):
        """Testet Auto-Auswahl für Streaming-Operationen."""
        selector = ProtocolSelector(full_config)

        streaming_operations = [
            "stream_data",
            "realtime_updates",
            "live_monitoring",
            "subscribe_events",
        ]

        for operation in streaming_operations:
            result = selector.select_protocol(operation)
            assert result == ProtocolType.STREAM

    def test_auto_select_async_operations(self, full_config):
        """Testet Auto-Auswahl für asynchrone Operationen."""
        selector = ProtocolSelector(full_config)

        async_operations = [
            "background_task",
            "async_process",
            "queue_message",
            "publish_event",
        ]

        for operation in async_operations:
            result = selector.select_protocol(operation)
            assert result == ProtocolType.BUS

    def test_auto_select_mcp_operations(self, full_config):
        """Testet Auto-Auswahl für MCP-Operationen."""
        selector = ProtocolSelector(full_config)

        mcp_operations = [
            "tool_discovery",
            "resource_access",
            "prompt_management",
            "discover_capabilities",
        ]

        for operation in mcp_operations:
            result = selector.select_protocol(operation)
            assert result == ProtocolType.MCP

    def test_auto_select_rpc_operations(self, full_config):
        """Testet Auto-Auswahl für RPC-Operationen."""
        selector = ProtocolSelector(full_config)

        rpc_operations = ["plan", "act", "observe", "explain", "sync_operation"]

        for operation in rpc_operations:
            result = selector.select_protocol(operation)
            assert result == ProtocolType.RPC

    def test_auto_select_unknown_operation(self, full_config):
        """Testet Auto-Auswahl für unbekannte Operation (sollte RPC sein)."""
        selector = ProtocolSelector(full_config)

        result = selector.select_protocol("unknown_operation")
        assert result == ProtocolType.RPC

    def test_context_based_selection(self, full_config):
        """Testet Kontext-basierte Protokoll-Auswahl."""
        selector = ProtocolSelector(full_config)

        # Streaming-Kontext
        result = selector.select_protocol(
            "process_data", context={"stream": True, "realtime": True}
        )
        assert result == ProtocolType.STREAM

        # Async-Kontext
        result = selector.select_protocol(
            "process_data", context={"async": True, "background": True}
        )
        assert result == ProtocolType.BUS

        # MCP-Kontext
        result = selector.select_protocol(
            "process_data", context={"tool": "calculator", "capability": "math"}
        )
        assert result == ProtocolType.MCP

    def test_get_fallback_chain(self, full_config):
        """Testet Fallback-Kette für Protokolle."""
        selector = ProtocolSelector(full_config)

        # RPC hat höchste Priorität, sollte an erster Stelle stehen
        chain = selector.get_fallback_chain(ProtocolType.STREAM)

        assert ProtocolType.STREAM in chain
        assert ProtocolType.RPC in chain
        assert chain.index(ProtocolType.STREAM) == 0  # Primary protocol first

        # RPC sollte hohe Priorität in Fallback haben
        fallback_protocols = chain[1:]  # Ohne primary protocol
        if fallback_protocols:
            assert ProtocolType.RPC in fallback_protocols[:2]  # In top 2

    def test_get_fallback_chain_disabled(self, no_fallback_config):
        """Testet Fallback-Kette wenn Fallback deaktiviert ist."""
        selector = ProtocolSelector(no_fallback_config)

        chain = selector.get_fallback_chain(ProtocolType.STREAM)

        # Nur primary protocol, kein Fallback
        assert chain == [ProtocolType.STREAM]

    def test_get_fallback_chain_unavailable_primary(self, limited_config):
        """Testet Fallback-Kette wenn primäres Protokoll nicht verfügbar ist."""
        selector = ProtocolSelector(limited_config)

        # Stream ist nicht verfügbar
        chain = selector.get_fallback_chain(ProtocolType.STREAM)

        # Stream sollte nicht in der Kette sein
        assert ProtocolType.STREAM not in chain
        # Verfügbare Protokolle sollten enthalten sein
        assert ProtocolType.RPC in chain
        assert ProtocolType.BUS in chain

    def test_no_protocols_available(self):
        """Testet Verhalten wenn keine Protokolle verfügbar sind."""
        config = ProtocolConfig(
            rpc_enabled=False,
            stream_enabled=False,
            bus_enabled=False,
            mcp_enabled=False,
        )
        selector = ProtocolSelector(config)

        with pytest.raises(ProtocolError, match="Kein geeignetes Protokoll"):
            selector.select_protocol("test_operation")

    def test_analyze_operation_requirements(self, full_config):
        """Testet Operation-Anforderungs-Analyse."""
        selector = ProtocolSelector(full_config)

        # Streaming-Operation
        analysis = selector.analyze_operation_requirements(
            "stream_data", context={"realtime": True}
        )

        assert analysis["operation"] == "stream_data"
        assert analysis["recommended_protocol"] == ProtocolType.STREAM
        assert analysis["requirements"]["streaming"] is True
        assert analysis["requirements"]["realtime"] is True
        assert len(analysis["fallback_chain"]) > 1

        # Tool-Operation
        analysis = selector.analyze_operation_requirements(
            "use_calculator", context={"tool": "calculator"}
        )

        assert analysis["recommended_protocol"] == ProtocolType.MCP
        assert analysis["requirements"]["tools"] is True

    def test_get_protocol_capabilities(self, full_config):
        """Testet Abruf von Protokoll-Capabilities."""
        selector = ProtocolSelector(full_config)

        capabilities = selector.get_protocol_capabilities()

        # Alle aktivierten Protokolle sollten enthalten sein
        assert ProtocolType.RPC in capabilities
        assert ProtocolType.STREAM in capabilities
        assert ProtocolType.BUS in capabilities
        assert ProtocolType.MCP in capabilities

        # RPC-Capabilities prüfen
        rpc_caps = capabilities[ProtocolType.RPC]
        assert rpc_caps["type"] == "synchronous"
        assert "plan" in rpc_caps["operations"]
        assert rpc_caps["reliability"] == "high"

        # Stream-Capabilities prüfen
        stream_caps = capabilities[ProtocolType.STREAM]
        assert stream_caps["type"] == "streaming"
        assert "realtime" in stream_caps["operations"]
        assert stream_caps["latency"] == "very_low"

    def test_get_protocol_capabilities_limited(self, limited_config):
        """Testet Protokoll-Capabilities mit begrenzter Konfiguration."""
        selector = ProtocolSelector(limited_config)

        capabilities = selector.get_protocol_capabilities()

        # Nur aktivierte Protokolle sollten enthalten sein
        assert ProtocolType.RPC in capabilities
        assert ProtocolType.BUS in capabilities
        assert ProtocolType.STREAM not in capabilities
        assert ProtocolType.MCP not in capabilities

    def test_auto_selection_disabled(self):
        """Testet Verhalten wenn Auto-Auswahl deaktiviert ist."""
        config = ProtocolConfig(
            rpc_enabled=True,
            stream_enabled=True,
            bus_enabled=True,
            mcp_enabled=True,
            auto_protocol_selection=False,  # Deaktiviert
            protocol_fallback_enabled=True,
        )
        selector = ProtocolSelector(config)

        # Ohne bevorzugtes Protokoll sollte Fallback verwendet werden
        result = selector.select_protocol("stream_data")  # Normalerweise STREAM

        # Sollte auf Fallback-Protokoll fallen (RPC hat höchste Priorität)
        assert result == ProtocolType.RPC

    def test_complex_operation_patterns(self, full_config):
        """Testet komplexe Operation-Pattern-Matching."""
        selector = ProtocolSelector(full_config)

        # Mehrere Pattern in einem Operation-Namen
        result = selector.select_protocol("async_stream_tool_discovery")

        # Erstes gefundenes Pattern sollte gewinnen
        # "async" kommt vor "stream" und "tool" in der Reihenfolge der Prüfung
        assert result in [ProtocolType.BUS, ProtocolType.STREAM, ProtocolType.MCP]

    def test_case_insensitive_matching(self, full_config):
        """Testet case-insensitive Pattern-Matching."""
        selector = ProtocolSelector(full_config)

        operations = [
            "STREAM_data",
            "Stream_Data",
            "ASYNC_process",
            "Async_Process",
            "TOOL_discovery",
            "Tool_Discovery",
        ]

        expected_protocols = [
            ProtocolType.STREAM,
            ProtocolType.STREAM,
            ProtocolType.BUS,
            ProtocolType.BUS,
            ProtocolType.MCP,
            ProtocolType.MCP,
        ]

        for operation, expected in zip(operations, expected_protocols):
            result = selector.select_protocol(operation)
            assert result == expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
