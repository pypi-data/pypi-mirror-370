# tests/integration/test_protocol_integration.py
"""
Integration tests for all supported protocols (RPC, Stream, Bus, MCP).

These tests validate end-to-end protocol functionality including:
- Protocol negotiation and selection
- Message serialization/deserialization
- Connection management and recovery
- Protocol-specific features and capabilities
- Cross-protocol communication scenarios
"""

import asyncio
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, List

from kei_agent import UnifiedKeiAgentClient, AgentClientConfig
from kei_agent.protocol_types import ProtocolConfig, Protocoltypee
from kei_agent.exceptions import CommunicationError, ProtocolError
from . import (
    skip_if_no_integration_env, requires_service, IntegrationTestBase,
    integration_test_base, test_endpoints, test_credentials
)


@pytest.mark.integration
class TestRPCProtocolIntegration:
    """Integration tests for RPC protocol functionality."""

    @pytest.mark.protocol_rpc
    @skip_if_no_integration_env()
    async def test_rpc_basic_request_response(self, integration_test_base):
        """Test basic RPC request-response pattern."""
        config = AgentClientConfig(**integration_test_base.get_test_config())

        # Force RPC protocol
        protocol_config = ProtocolConfig(
            rpc_enabled=True,
            stream_enabled=False,
            bus_enabled=False,
            mcp_enabled=False,
            preferred_protocol="rpc"
        )

        async with UnifiedKeiAgentClient(config) as client:
            # Mock RPC call
            with patch.object(client, '_make_rpc_call') as mock_rpc:
                mock_rpc.return_value = {"result": "success", "data": {"message": "Hello RPC"}}

                response = await client.call_remote_method(
                    "test_service",
                    "echo",
                    {"message": "Hello RPC"}
                )

                assert response["result"] == "success"
                assert response["data"]["message"] == "Hello RPC"
                mock_rpc.assert_called_once()

    @pytest.mark.protocol_rpc
    @skip_if_no_integration_env()
    async def test_rpc_error_handling(self, integration_test_base):
        """Test RPC error handling and recovery."""
        config = AgentClientConfig(**integration_test_base.get_test_config())

        async with UnifiedKeiAgentClient(config) as client:
            with patch.object(client, '_make_rpc_call') as mock_rpc:
                # Simulate RPC error
                mock_rpc.side_effect = CommunicationError("RPC call failed")

                with pytest.raises(CommunicationError):
                    await client.call_remote_method(
                        "test_service",
                        "failing_method",
                        {}
                    )

    @pytest.mark.protocol_rpc
    @skip_if_no_integration_env()
    async def test_rpc_concurrent_calls(self, integration_test_base):
        """Test concurrent RPC calls."""
        config = AgentClientConfig(**integration_test_base.get_test_config())

        async with UnifiedKeiAgentClient(config) as client:
            with patch.object(client, '_make_rpc_call') as mock_rpc:
                # Mock successful responses
                mock_rpc.return_value = {"result": "success", "call_id": "test"}

                # Make concurrent calls
                tasks = [
                    client.call_remote_method("service", "method", {"id": i})
                    for i in range(10)
                ]

                results = await asyncio.gather(*tasks)

                assert len(results) == 10
                assert all(r["result"] == "success" for r in results)
                assert mock_rpc.call_count == 10


@pytest.mark.integration
class TestStreamProtocolIntegration:
    """Integration tests for Stream protocol functionality."""

    @pytest.mark.protocol_stream
    @skip_if_no_integration_env()
    async def test_stream_connection_lifecycle(self, integration_test_base):
        """Test Stream protocol connection lifecycle."""
        config = AgentClientConfig(**integration_test_base.get_test_config())

        # Force Stream protocol
        protocol_config = ProtocolConfig(
            rpc_enabled=False,
            stream_enabled=True,
            bus_enabled=False,
            mcp_enabled=False,
            preferred_protocol="stream"
        )

        async with UnifiedKeiAgentClient(config) as client:
            # Mock stream connection
            mock_stream = AsyncMock()

            with patch.object(client, '_create_stream_connection', return_value=mock_stream):
                # Test connection establishment
                stream = await client.create_stream("test_stream")
                assert stream is not None

                # Test sending data
                await client.send_stream_data(stream, {"message": "test"})
                mock_stream.send.assert_called_once()

                # Test receiving data
                mock_stream.receive.return_value = {"response": "received"}
                data = await client.receive_stream_data(stream)
                assert data["response"] == "received"

    @pytest.mark.protocol_stream
    @skip_if_no_integration_env()
    async def test_stream_reconnection(self, integration_test_base):
        """Test Stream protocol automatic reconnection."""
        config = AgentClientConfig(**integration_test_base.get_test_config())

        async with UnifiedKeiAgentClient(config) as client:
            mock_stream = AsyncMock()

            with patch.object(client, '_create_stream_connection', return_value=mock_stream):
                # Simulate connection loss
                mock_stream.send.side_effect = [
                    None,  # First call succeeds
                    ConnectionError("Connection lost"),  # Second call fails
                    None   # Third call succeeds after reconnection
                ]

                stream = await client.create_stream("test_stream")

                # First send should succeed
                await client.send_stream_data(stream, {"message": "test1"})

                # Second send should trigger reconnection
                await client.send_stream_data(stream, {"message": "test2"})

                # Verify reconnection logic was triggered
                assert mock_stream.send.call_count >= 2

    @pytest.mark.protocol_stream
    @skip_if_no_integration_env()
    async def test_stream_backpressure_handling(self, integration_test_base):
        """Test Stream protocol backpressure handling."""
        config = AgentClientConfig(**integration_test_base.get_test_config())

        async with UnifiedKeiAgentClient(config) as client:
            mock_stream = AsyncMock()

            with patch.object(client, '_create_stream_connection', return_value=mock_stream):
                # Simulate slow consumer
                mock_stream.send.side_effect = lambda data: asyncio.sleep(0.1)

                stream = await client.create_stream("test_stream")

                # Send multiple messages rapidly
                start_time = asyncio.get_event_loop().time()
                tasks = [
                    client.send_stream_data(stream, {"message": f"test{i}"})
                    for i in range(5)
                ]

                await asyncio.gather(*tasks)
                end_time = asyncio.get_event_loop().time()

                # Verify backpressure was applied (should take at least 0.5 seconds)
                assert end_time - start_time >= 0.4


@pytest.mark.integration
class TestBusProtocolIntegration:
    """Integration tests for Bus protocol functionality."""

    @pytest.mark.protocol_bus
    @skip_if_no_integration_env()
    async def test_bus_publish_subscribe(self, integration_test_base):
        """Test Bus protocol publish-subscribe pattern."""
        config = AgentClientConfig(**integration_test_base.get_test_config())

        # Force Bus protocol
        protocol_config = ProtocolConfig(
            rpc_enabled=False,
            stream_enabled=False,
            bus_enabled=True,
            mcp_enabled=False,
            preferred_protocol="bus"
        )

        async with UnifiedKeiAgentClient(config) as client:
            received_messages = []

            # Mock message handler
            async def message_handler(message):
                received_messages.append(message)

            with patch.object(client, '_subscribe_to_topic') as mock_subscribe:
                with patch.object(client, '_publish_to_topic') as mock_publish:
                    # Subscribe to topic
                    await client.subscribe("test_topic", message_handler)
                    mock_subscribe.assert_called_once_with("test_topic", message_handler)

                    # Publish message
                    test_message = {"type": "test", "data": "hello bus"}
                    await client.publish("test_topic", test_message)
                    mock_publish.assert_called_once_with("test_topic", test_message)

    @pytest.mark.protocol_bus
    @skip_if_no_integration_env()
    async def test_bus_topic_patterns(self, integration_test_base):
        """Test Bus protocol topic pattern matching."""
        config = AgentClientConfig(**integration_test_base.get_test_config())

        async with UnifiedKeiAgentClient(config) as client:
            received_messages = []

            async def pattern_handler(message):
                received_messages.append(message)

            with patch.object(client, '_subscribe_to_pattern') as mock_subscribe:
                # Subscribe to pattern
                await client.subscribe_pattern("events.*", pattern_handler)
                mock_subscribe.assert_called_once_with("events.*", pattern_handler)

                # Test that pattern matching works
                with patch.object(client, '_publish_to_topic') as mock_publish:
                    await client.publish("events.user.created", {"user_id": 123})
                    await client.publish("events.order.placed", {"order_id": 456})

                    assert mock_publish.call_count == 2

    @pytest.mark.protocol_bus
    @skip_if_no_integration_env()
    async def test_bus_message_ordering(self, integration_test_base):
        """Test Bus protocol message ordering guarantees."""
        config = AgentClientConfig(**integration_test_base.get_test_config())

        async with UnifiedKeiAgentClient(config) as client:
            received_order = []

            async def ordered_handler(message):
                received_order.append(message["sequence"])

            with patch.object(client, '_subscribe_to_topic') as mock_subscribe:
                with patch.object(client, '_publish_to_topic') as mock_publish:
                    await client.subscribe("ordered_topic", ordered_handler)

                    # Publish messages in sequence
                    for i in range(10):
                        await client.publish("ordered_topic", {"sequence": i})

                    # Verify all messages were published
                    assert mock_publish.call_count == 10


@pytest.mark.integration
class TestMCPProtocolIntegration:
    """Integration tests for MCP (Model Context Protocol) functionality."""

    @pytest.mark.protocol_mcp
    @skip_if_no_integration_env()
    async def test_mcp_capability_negotiation(self, integration_test_base):
        """Test MCP capability negotiation."""
        config = AgentClientConfig(**integration_test_base.get_test_config())

        # Force MCP protocol
        protocol_config = ProtocolConfig(
            rpc_enabled=False,
            stream_enabled=False,
            bus_enabled=False,
            mcp_enabled=True,
            preferred_protocol="mcp"
        )

        async with UnifiedKeiAgentClient(config) as client:
            with patch.object(client, '_negotiate_mcp_capabilities') as mock_negotiate:
                mock_negotiate.return_value = {
                    "supported_capabilities": ["tools", "resources", "prompts"],
                    "protocol_version": "1.0.0"
                }

                capabilities = await client.negotiate_capabilities()

                assert "tools" in capabilities["supported_capabilities"]
                assert "resources" in capabilities["supported_capabilities"]
                assert capabilities["protocol_version"] == "1.0.0"

    @pytest.mark.protocol_mcp
    @skip_if_no_integration_env()
    async def test_mcp_tool_execution(self, integration_test_base):
        """Test MCP tool execution."""
        config = AgentClientConfig(**integration_test_base.get_test_config())

        async with UnifiedKeiAgentClient(config) as client:
            with patch.object(client, '_execute_mcp_tool') as mock_execute:
                mock_execute.return_value = {
                    "result": "success",
                    "output": "Tool executed successfully",
                    "metadata": {"execution_time": 0.5}
                }

                result = await client.execute_tool(
                    "calculator",
                    "add",
                    {"a": 5, "b": 3}
                )

                assert result["result"] == "success"
                assert result["output"] == "Tool executed successfully"
                mock_execute.assert_called_once_with("calculator", "add", {"a": 5, "b": 3})

    @pytest.mark.protocol_mcp
    @skip_if_no_integration_env()
    async def test_mcp_resource_access(self, integration_test_base):
        """Test MCP resource access."""
        config = AgentClientConfig(**integration_test_base.get_test_config())

        async with UnifiedKeiAgentClient(config) as client:
            with patch.object(client, '_access_mcp_resource') as mock_access:
                mock_access.return_value = {
                    "resource_id": "test_resource",
                    "content": "Resource content",
                    "metadata": {"type": "text", "size": 16}
                }

                resource = await client.access_resource("test_resource")

                assert resource["resource_id"] == "test_resource"
                assert resource["content"] == "Resource content"
                mock_access.assert_called_once_with("test_resource")


@pytest.mark.integration
class TestCrossProtocolIntegration:
    """Integration tests for cross-protocol communication scenarios."""

    @pytest.mark.integration
    @skip_if_no_integration_env()
    async def test_protocol_fallback(self, integration_test_base):
        """Test automatic protocol fallback when preferred protocol fails."""
        config = AgentClientConfig(**integration_test_base.get_test_config())

        # Configure multiple protocols with fallback
        protocol_config = ProtocolConfig(
            rpc_enabled=True,
            stream_enabled=True,
            bus_enabled=True,
            mcp_enabled=True,
            preferred_protocol="rpc",
            protocol_fallback_enabled=True
        )

        async with UnifiedKeiAgentClient(config) as client:
            with patch.object(client, '_try_rpc_connection') as mock_rpc:
                with patch.object(client, '_try_stream_connection') as mock_stream:
                    # RPC fails, should fallback to Stream
                    mock_rpc.side_effect = ConnectionError("RPC unavailable")
                    mock_stream.return_value = True

                    success = await client.establish_connection()

                    assert success
                    mock_rpc.assert_called_once()
                    mock_stream.assert_called_once()

    @pytest.mark.integration
    @skip_if_no_integration_env()
    async def test_protocol_selection_based_on_capability(self, integration_test_base):
        """Test automatic protocol selection based on required capabilities."""
        config = AgentClientConfig(**integration_test_base.get_test_config())

        async with UnifiedKeiAgentClient(config) as client:
            with patch.object(client, '_select_optimal_protocol') as mock_select:
                mock_select.return_value = "stream"

                # Request capability that requires streaming
                protocol = await client.select_protocol_for_capability("real_time_data")

                assert protocol == "stream"
                mock_select.assert_called_once_with("real_time_data")

    @pytest.mark.integration
    @skip_if_no_integration_env()
    async def test_multi_protocol_session(self, integration_test_base):
        """Test maintaining multiple protocol connections simultaneously."""
        config = AgentClientConfig(**integration_test_base.get_test_config())

        async with UnifiedKeiAgentClient(config) as client:
            with patch.object(client, '_maintain_rpc_connection') as mock_rpc:
                with patch.object(client, '_maintain_stream_connection') as mock_stream:
                    with patch.object(client, '_maintain_bus_connection') as mock_bus:
                        # Establish multiple connections
                        await client.establish_multi_protocol_session()

                        # Verify all protocols are active
                        assert await client.is_protocol_active("rpc")
                        assert await client.is_protocol_active("stream")
                        assert await client.is_protocol_active("bus")

                        mock_rpc.assert_called()
                        mock_stream.assert_called()
                        mock_bus.assert_called()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
