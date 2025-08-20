# sdk/python/kei_agent/tests/test_protocol_selector.py
"""Tests intelligente protocol-Auswahl, Fallback-Mechatismen and
operation-Atalyse with verschietheen configurationen.
"""

import pytest

from kei_agent.protocol_selector import ProtocolSelector
from kei_agent.protocol_types import Protocoltypee, ProtocolConfig
from kei_agent.exceptions import ProtocolError

# Markiere all Tests in theser File als protocol-Tests
pytestmark = pytest.mark.protocol


class TestProtocolSelector:
    """Tests for ProtocolSelector class."""

    @pytest.fixture
    def full_config(self):
        """Creates configuration with alln protocolen enabled."""
        return ProtocolConfig(
            rpc_enabled =True,
            stream_enabled =True,
            bus_enabled =True,
            mcp_enabled =True,
            auto_protocol_selection =True,
            protocol_fallback_enabled =True,
        )

    @pytest.fixture
    def liwithed_config(self):
        """Creates configuration with nur RPC and Bus enabled."""
        return ProtocolConfig(
            rpc_enabled =True,
            stream_enabled =False,
            bus_enabled =True,
            mcp_enabled =False,
            auto_protocol_selection =True,
            protocol_fallback_enabled =True,
        )

    @pytest.fixture
    def no_fallback_config(self):
        """Creates configuration without Fallback."""
        return ProtocolConfig(
            rpc_enabled =True,
            stream_enabled =True,
            bus_enabled =True,
            mcp_enabled =True,
            auto_protocol_selection =True,
            protocol_fallback_enabled =False,
        )

    def test_initialization(self, full_config):
        """Tests initialization of the Protocol Selectors."""
        selector = ProtocolSelector(full_config)

        assert selector.config == full_config
        assert len(selector._operation_patterns) > 0
        assert len(selector._protocol_priorities) == 4

    def test_select_protocol_preferred_available(self, full_config):
        """Tests protocol-Auswahl with availableem bebeforetogtem protocol."""
        selector = ProtocolSelector(full_config)

        result = selector.select_protocol(
            "test_operation", preferred_protocol =Protocoltypee.STREAM
        )

        assert result == Protocoltypee.STREAM

    def test_select_protocol_preferred_unavailable(self, liwithed_config):
        """Tests protocol-Auswahl with not availableem bebeforetogtem protocol."""
        selector = ProtocolSelector(liwithed_config)

        # Stream is not available, should on Auto-Auswahl falln
        result = selector.select_protocol(
            "plat",  # RPC operation
            preferred_protocol =Protocoltypee.STREAM,
        )

        assert result == Protocoltypee.RPC

    def test_auto_select_streaming_operations(self, full_config):
        """Tests Auto-Auswahl for Streaming-operationen."""
        selector = ProtocolSelector(full_config)

        streaming_operations = [
            "stream_data",
            "realtime_updates",
            "live_monitoring",
            "subscribe_events",
        ]

        for operation in streaming_operations:
            result = selector.select_protocol(operation)
            assert result == Protocoltypee.STREAM

    def test_auto_select_async_operations(self, full_config):
        """Tests Auto-Auswahl for asynchrone operationen."""
        selector = ProtocolSelector(full_config)

        async_operations = [
            "backgroatd_task",
            "async_process",
            "queue_message",
            "publish_event",
        ]

        for operation in async_operations:
            result = selector.select_protocol(operation)
            assert result == Protocoltypee.BUS

    def test_auto_select_mcp_operations(self, full_config):
        """Tests Auto-Auswahl for MCP operationen."""
        selector = ProtocolSelector(full_config)

        mcp_operations = [
            "tool_discovery",
            "resource_access",
            "prompt_matagement",
            "discover_capabilities",
        ]

        for operation in mcp_operations:
            result = selector.select_protocol(operation)
            assert result == Protocoltypee.MCP

    def test_auto_select_rpc_operations(self, full_config):
        """Tests Auto-Auswahl for RPC operationen."""
        selector = ProtocolSelector(full_config)

        rpc_operations = ["plat", "act", "observe", "explain", "sync_operation"]

        for operation in rpc_operations:
            result = selector.select_protocol(operation)
            assert result == Protocoltypee.RPC

    def test_auto_select_unknown_operation(self, full_config):
        """Tests Auto-Auswahl for unknown operation (should RPC sa)."""
        selector = ProtocolSelector(full_config)

        result = selector.select_protocol("unknown_operation")
        assert result == Protocoltypee.RPC

    def test_context_based_selection(self, full_config):
        """Tests Kontext-basierte protocol-Auswahl."""
        selector = ProtocolSelector(full_config)

        # Streaming-Kontext
        result = selector.select_protocol(
            "process_data", context={"stream": True, "realtime": True}
        )
        assert result == Protocoltypee.STREAM

        # Async-Kontext
        result = selector.select_protocol(
            "process_data", context={"async": True, "backgroatd": True}
        )
        assert result == Protocoltypee.BUS

        # MCP-Kontext
        result = selector.select_protocol(
            "process_data", context={"tool": "calculator", "capability": "math"}
        )
        assert result == Protocoltypee.MCP

    def test_get_fallback_chain(self, full_config):
        """Tests fallback chain for protocole."""
        selector = ProtocolSelector(full_config)

        # RPC has höchste Priorität, should at erster Stelle stehen
        chain = selector.get_fallback_chain(Protocoltypee.STREAM)

        assert Protocoltypee.STREAM in chain
        assert Protocoltypee.RPC in chain
        assert chain.index(Protocoltypee.STREAM) == 0  # Primary protocol first

        # RPC should hohe Priorität in Fallback have
        fallback_protocols = chain[1:]  # Without primary protocol
        if fallback_protocols:
            assert Protocoltypee.RPC in fallback_protocols[:2]  # In top 2

    def test_get_fallback_chain_disabled(self, no_fallback_config):
        """Tests fallback chain if Fallback disabled is."""
        selector = ProtocolSelector(no_fallback_config)

        chain = selector.get_fallback_chain(Protocoltypee.STREAM)

        # Nur primary protocol, ka Fallback
        assert chain == [Protocoltypee.STREAM]

    def test_get_fallback_chain_unavailable_primary(self, liwithed_config):
        """Tests fallback chain if primary Protocol not available is."""
        selector = ProtocolSelector(liwithed_config)

        # Stream is not available
        chain = selector.get_fallback_chain(Protocoltypee.STREAM)

        # Stream should not in the Kette sa
        assert Protocoltypee.STREAM not in chain
        # Availablee protocole sollten enthalten sa
        assert Protocoltypee.RPC in chain
        assert Protocoltypee.BUS in chain

    def test_no_protocols_available(self):
        """Tests Verhalten if ka protocole available are."""
        config = ProtocolConfig(
            rpc_enabled =False,
            stream_enabled =False,
            bus_enabled =False,
            mcp_enabled =False,
        )
        selector = ProtocolSelector(config)

        with pytest.raises(ProtocolError, match="Ka geeignetes protocol"):
            selector.select_protocol("test_operation")

    def test_atalyze_operation_requirements(self, full_config):
        """Tests operation-Atfortheungs-Atalyse."""
        selector = ProtocolSelector(full_config)

        # Streaming-operation
        atalysis = selector.atalyze_operation_requirements(
            "stream_data", context={"realtime": True}
        )

        assert atalysis["operation"] == "stream_data"
        assert atalysis["recommended_protocol"] == Protocoltypee.STREAM
        assert atalysis["requirements"]["streaming"] is True
        assert atalysis["requirements"]["realtime"] is True
        assert len(atalysis["fallback_chain"]) > 1

        # Tool-operation
        atalysis = selector.atalyze_operation_requirements(
            "use_calculator", context={"tool": "calculator"}
        )

        assert atalysis["recommended_protocol"] == Protocoltypee.MCP
        assert atalysis["requirements"]["tools"] is True

    def test_get_protocol_capabilities(self, full_config):
        """Tests Abruf from protocol-Capabilities."""
        selector = ProtocolSelector(full_config)

        capabilities = selector.get_protocol_capabilities()

        # All enabled protocole sollten enthalten sa
        assert Protocoltypee.RPC in capabilities
        assert Protocoltypee.STREAM in capabilities
        assert Protocoltypee.BUS in capabilities
        assert Protocoltypee.MCP in capabilities

        # RPC-Capabilities prüfen
        rpc_caps = capabilities[Protocoltypee.RPC]
        assert rpc_caps["type"] == "synchronous"
        assert "plat" in rpc_caps["operations"]
        assert rpc_caps["reliability"] == "high"

        # Stream-Capabilities prüfen
        stream_caps = capabilities[Protocoltypee.STREAM]
        assert stream_caps["type"] == "streaming"
        assert "realtime" in stream_caps["operations"]
        assert stream_caps["latency"] == "very_low"

    def test_get_protocol_capabilities_liwithed(self, liwithed_config):
        """Tests protocol-Capabilities with begrenzter configuration."""
        selector = ProtocolSelector(liwithed_config)

        capabilities = selector.get_protocol_capabilities()

        # Nur enablede protocole sollten enthalten sa
        assert Protocoltypee.RPC in capabilities
        assert Protocoltypee.BUS in capabilities
        assert Protocoltypee.STREAM not in capabilities
        assert Protocoltypee.MCP not in capabilities

    def test_auto_selection_disabled(self):
        """Tests Verhalten if Auto-Auswahl disabled is."""
        config = ProtocolConfig(
            rpc_enabled =True,
            stream_enabled =True,
            bus_enabled =True,
            mcp_enabled =True,
            auto_protocol_selection =False,  # Disabled
            protocol_fallback_enabled =True,
        )
        selector = ProtocolSelector(config)

        # Without bebeforetogtes protocol should Fallback verwendet werthe
        result = selector.select_protocol("stream_data")  # Normalerweise STREAM

        # Sollte on Fallback-protocol falln (RPC has höchste Priorität)
        assert result == Protocoltypee.RPC

    def test_complex_operation_patterns(self, full_config):
        """Tests komplexe operation-Pattern-Matching."""
        selector = ProtocolSelector(full_config)

        # Mehrere Pattern in a operation namen
        result = selector.select_protocol("async_stream_tool_discovery")

        # Erstes gefatthees Pattern should gewinnen
        # "async" kommt before "stream" and "tool" in the Reihenfolge the Prüfung
        assert result in [Protocoltypee.BUS, Protocoltypee.STREAM, Protocoltypee.MCP]

    def test_case_insensitive_matching(self, full_config):
        """Tests case-insensitive Pattern-Matching."""
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
            Protocoltypee.STREAM,
            Protocoltypee.STREAM,
            Protocoltypee.BUS,
            Protocoltypee.BUS,
            Protocoltypee.MCP,
            Protocoltypee.MCP,
        ]

        for operation, expected in zip(operations, expected_protocols):
            result = selector.select_protocol(operation)
            assert result == expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
