# sdk/python/kei_agent/tests/test_unified_client_refactored.py
"""Tests the refactored Version of the Unified clients with verbesserter
Architektur, vollständigen typee Hints and enterprise features.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from kei_agent.unified_client import UnifiedKeiAgentClient
from kei_agent.client import AgentClientConfig
from kei_agent.protocol_types import (
    Protocoltypee,
    ProtocolConfig,
    SecurityConfig,
    Authtypee,
)
from kei_agent.exceptions import KeiSDKError, ProtocolError

# Markiere all Tests in theser File als tests
pytestmark = pytest.mark.refactored


class TestUnifiedKeiAgentClientRefactored:
    """Tests for refactored UnifiedKeiAgentClient."""

    @pytest.fixture
    def agent_config(self):
        """Creates agent client configuration."""
        return AgentClientConfig(
            base_url ="https://test.kei-framework.com",
            api_token ="test-token-123",
            agent_id ="test-agent-refactored",
        )

    @pytest.fixture
    def protocol_config(self):
        """Creates protocol-configuration."""
        return ProtocolConfig(
            rpc_enabled =True,
            stream_enabled =True,
            bus_enabled =True,
            mcp_enabled =True,
            auto_protocol_selection =True,
            protocol_fallback_enabled =True,
        )

    @pytest.fixture
    def security_config(self):
        """Creates security configuration."""
        return SecurityConfig(
            auth_type =Authtypee.BEARER,
            api_token ="test-token-123",
            rbac_enabled =True,
            audit_enabled =True,
        )

    @pytest.fixture
    def unified_client(self, agent_config, protocol_config, security_config):
        """Creates Unified client for Tests."""
        return UnifiedKeiAgentClient(
            config=agent_config,
            protocol_config =protocol_config,
            security_config =security_config,
        )

    def test_initialization(self, unified_client, agent_config):
        """Tests client initialization."""
        assert unified_client.config == agent_config
        assert unified_client._initialized is False
        assert unified_client._closed is False
        assert unified_client.security is not None
        assert unified_client.protocol_selector is not None

    def test_initialization_default_configs(self, agent_config):
        """Tests initialization with Statdard-configurationen."""
        client = UnifiedKeiAgentClient(config=agent_config)

        assert client.protocol_config is not None
        assert client.security_config is not None
        assert client.protocol_config.rpc_enabled is True
        assert client.security_config.auth_type == Authtypee.BEARER

    @pytest.mark.asyncio
    async def test_initialize_success(self, unified_client):
        """Tests successfule client initialization."""
        with patch.object(
            unified_client.security, "start_token_refresh"
        ) as mock_token_refresh:
            with patch.object(
                unified_client, "_initialize_protocol_clients"
            ) as mock_protocol_init:
                with patch.object(
                    unified_client, "_initialize_enterprise_features"
                ) as mock_enterprise_init:
                    with patch(
                        "kei_agent.unified_client.KeiAgentClient"
                    ) as mock_legacy_client:
                        mock_legacy_instatce = AsyncMock()
                        mock_legacy_client.return_value = mock_legacy_instatce

                        await unified_client.initialize()

                        assert unified_client._initialized is True
                        mock_token_refresh.assert_called_once()
                        mock_protocol_init.assert_called_once()
                        mock_enterprise_init.assert_called_once()
                        mock_legacy_instatce.initialize.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialize_already_initialized(self, unified_client):
        """Tests initialization if already initialized."""
        unified_client._initialized = True

        with patch.object(
            unified_client.security, "start_token_refresh"
        ) as mock_token_refresh:
            await unified_client.initialize()

            # Sollte not erneut initialized werthe
            mock_token_refresh.assert_not_called()

    @pytest.mark.asyncio
    async def test_initialize_error(self, unified_client):
        """Tests initialization errors."""
        with patch.object(
            unified_client.security,
            "start_token_refresh",
            side_effect =Exception("Init error"),
        ):
            with pytest.raises(KeiSDKError, match="initialization failed"):
                await unified_client.initialize()

    @pytest.mark.asyncio
    async def test_close_success(self, unified_client):
        """Tests successfules client-Closingn."""
        # Simuliere initializethe client
        unified_client._initialized = True
        unified_client._stream_client = AsyncMock()
        unified_client._legacy_client = AsyncMock()
        unified_client.tracing = AsyncMock()

        # Mock security manager methodn
        with patch.object(unified_client.security, "stop_token_refresh") as mock_stop:
            await unified_client.close()

            assert unified_client._closed is True
            mock_stop.assert_called_once()
            unified_client._stream_client.disconnect.assert_called_once()
            unified_client._legacy_client.close.assert_called_once()
            unified_client.tracing.shutdown.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_already_closed(self, unified_client):
        """Tests Closingn if bereits closed."""
        unified_client._closed = True

        with patch.object(unified_client.security, "stop_token_refresh") as mock_stop:
            await unified_client.close()

            # Sollte not erneut closed werthe
            mock_stop.assert_not_called()

    @pytest.mark.asyncio
    async def test_context_manager(self, unified_client):
        """Tests async context manager."""
        with patch.object(unified_client, "initialize") as mock_init:
            with patch.object(unified_client, "close") as mock_close:
                async with unified_client as client:
                    assert client == unified_client

                mock_init.assert_called_once()
                mock_close.assert_called_once()

    def test_select_optimal_protocol(self, unified_client):
        """Tests optimale protocol-Auswahl."""
        # Mock Protocol Selector
        with patch.object(
            unified_client.protocol_selector, "select_protocol"
        ) as mock_select:
            mock_select.return_value = Protocoltypee.STREAM

            result = unified_client._select_optimal_protocol("stream_data")

            assert result == Protocoltypee.STREAM
            mock_select.assert_called_once_with("stream_data", None)

    def test_is_protocol_available_not_initialized(self, unified_client):
        """Tests protocol availability if not initialized."""
        assert unified_client.is_protocol_available(Protocoltypee.RPC) is False

    def test_is_protocol_available_initialized(self, unified_client):
        """Tests protocol availability if initialized."""
        unified_client._initialized = True
        unified_client._rpc_client = MagicMock()
        unified_client._stream_client = None

        assert unified_client.is_protocol_available(Protocoltypee.RPC) is True
        assert unified_client.is_protocol_available(Protocoltypee.STREAM) is False

    def test_get_available_protocols(self, unified_client):
        """Tests Abruf availableer protocole."""
        unified_client._initialized = True
        unified_client._rpc_client = MagicMock()
        unified_client._stream_client = MagicMock()
        unified_client._bus_client = None
        unified_client._mcp_client = MagicMock()

        protocols = unified_client.get_available_protocols()

        assert Protocoltypee.RPC in protocols
        assert Protocoltypee.STREAM in protocols
        assert Protocoltypee.BUS not in protocols
        assert Protocoltypee.MCP in protocols

    def test_get_client_info(self, unified_client):
        """Tests client information."""
        unified_client._initialized = True
        unified_client._closed = False
        unified_client._rpc_client = MagicMock()

        info = unified_client.get_client_info()

        assert info["agent_id"] == "test-agent-refactored"
        assert info["base_url"] == "https://test.kei-framework.com"
        assert info["initialized"] is True
        assert info["closed"] is False
        assert "available_protocols" in info
        assert "security_context" in info
        assert "features" in info

    @pytest.mark.asyncio
    async def test_execute_agent_operation_not_initialized(self, unified_client):
        """Tests operation-Ausführung without initialization."""
        with pytest.raises(KeiSDKError, match="Client not initialized"):
            await unified_client.execute_agent_operation("test", {})

    @pytest.mark.asyncio
    async def test_execute_agent_operation_success(self, unified_client):
        """Tests successfule operation-Ausführung."""
        unified_client._initialized = True

        with patch.object(unified_client, "_select_optimal_protocol") as mock_select:
            with patch.object(unified_client, "_execute_with_protocol") as mock_execute:
                mock_select.return_value = Protocoltypee.RPC
                mock_execute.return_value = {"result": "success"}

                result = await unified_client.execute_agent_operation(
                    "test_op", {"data": "test"}
                )

                assert result["result"] == "success"
                mock_select.assert_called_once_with("test_op", {"data": "test"})
                mock_execute.assert_called_once_with(
                    Protocoltypee.RPC, "test_op", {"data": "test"}
                )

    @pytest.mark.asyncio
    async def test_execute_agent_operation_with_tracing(self, unified_client):
        """Tests operation-Ausführung with Tracing."""
        unified_client._initialized = True
        unified_client.tracing = MagicMock()

        # Mock Tracing Context Manager
        mock_spat = MagicMock()
        unified_client.tracing.start_spat.return_value.__enter__ = MagicMock(
            return_value =mock_spat
        )
        unified_client.tracing.start_spat.return_value.__exit__ = MagicMock()

        with patch.object(unified_client, "_execute_with_protocol") as mock_execute:
            mock_execute.return_value = {"result": "traced"}

            result = await unified_client.execute_agent_operation("traced_op", {})

            assert result["result"] == "traced"
            unified_client.tracing.start_spat.assert_called_once()
            mock_spat.set_attribute.assert_called()

    @pytest.mark.asyncio
    async def test_execute_with_protocol_rpc(self, unified_client):
        """Tests protocol-specific Ausführung for RPC."""
        with patch.object(unified_client, "_execute_rpc_operation") as mock_rpc:
            mock_rpc.return_value = {"rpc_result": "success"}

            result = await unified_client._execute_with_protocol(
                Protocoltypee.RPC, "test_op", {"data": "test"}
            )

            assert result["rpc_result"] == "success"
            mock_rpc.assert_called_once_with("test_op", {"data": "test"})

    @pytest.mark.asyncio
    async def test_execute_with_protocol_fallback(self, unified_client):
        """Tests Fallback-Mechatismus on protocol-errorn."""
        unified_client.protocol_config.protocol_fallback_enabled = True

        with patch.object(unified_client, "_execute_rpc_operation") as mock_rpc:
            with patch.object(unified_client, "_execute_bus_operation") as mock_bus:
                with patch.object(
                    unified_client.protocol_selector, "get_fallback_chain"
                ) as mock_chain:
                    # Erstes protocol schlägt fehl
                    mock_rpc.side_effect = ProtocolError("RPC failed")
                    # Fallback successful
                    mock_bus.return_value = {"fallback_result": "success"}
                    # fallback chain
                    mock_chain.return_value = [Protocoltypee.RPC, Protocoltypee.BUS]

                    result = await unified_client._execute_with_protocol(
                        Protocoltypee.RPC, "test_op", {"data": "test"}
                    )

                    assert result["fallback_result"] == "success"
                    mock_rpc.assert_called_once()
                    mock_bus.assert_called_once()

    @pytest.mark.asyncio
    async def test_plat_task_high_level_api(self, unified_client):
        """Tests High-Level Plat-Task API."""
        with patch.object(unified_client, "execute_agent_operation") as mock_execute:
            mock_execute.return_value = {"plat_id": "plat-123"}

            result = await unified_client.plat_task("Create report", {"format": "pdf"})

            assert result["plat_id"] == "plat-123"
            mock_execute.assert_called_once_with(
                "plat",
                {"objective": "Create report", "context": {"format": "pdf"}},
                None,
            )

    @pytest.mark.asyncio
    async def test_execute_action_high_level_api(self, unified_client):
        """Tests High-Level Execute-Action API."""
        with patch.object(unified_client, "execute_agent_operation") as mock_execute:
            mock_execute.return_value = {"action_id": "action-456"}

            result = await unified_client.execute_action(
                "generate_file", {"path": "/tmp/test.txt"}
            )

            assert result["action_id"] == "action-456"
            mock_execute.assert_called_once_with(
                "act",
                {"action": "generate_file", "parameters": {"path": "/tmp/test.txt"}},
                None,
            )

    @pytest.mark.asyncio
    async def test_send_agent_message_high_level_api(self, unified_client):
        """Tests High-Level Agent-Message API."""
        with patch.object(unified_client, "execute_agent_operation") as mock_execute:
            mock_execute.return_value = {"message_id": "msg-789"}

            result = await unified_client.send_agent_message(
                "target-agent", "task_request", {"task": "process_data"}
            )

            assert result["message_id"] == "msg-789"
            # Prüfe thes execute_agent_operation ongerufen wurde
            mock_execute.assert_called_once()
            # Prüfe the Onruf-parameters
            call_args = mock_execute.call_args
            assert call_args[0][0] == "send_message"  # operation
            # The data-dictionary enthält 'target', not 'target_agent'
            assert "target" in call_args[0][1]  # data
            assert call_args[0][1]["target"] == "target-agent"

    @pytest.mark.asyncio
    async def test_discover_available_tools_high_level_api(self, unified_client):
        """Tests High-Level tool discovery API."""
        with patch.object(unified_client, "execute_agent_operation") as mock_execute:
            mock_execute.return_value = {
                "tools": [
                    {"name": "calculator", "description": "Math tool"},
                    {"name": "file_reathe", "description": "File tool"},
                ]
            }

            tools = await unified_client.discover_available_tools("utilities")

            assert len(tools) == 2
            assert tools[0]["name"] == "calculator"
            # Prüfe thes execute_agent_operation ongerufen wurde
            mock_execute.assert_called_once()
            call_args = mock_execute.call_args
            assert call_args[0][0] == "discover_tools"  # operation

    @pytest.mark.asyncio
    async def test_use_tool_high_level_api(self, unified_client):
        """Tests High-Level Tool-Use API."""
        with patch.object(unified_client, "execute_agent_operation") as mock_execute:
            mock_execute.return_value = {"result": 42, "status": "completed"}

            result = await unified_client.use_tool("calculator", expression="6*7")

            assert result["result"] == 42
            # Prüfe thes execute_agent_operation ongerufen wurde
            mock_execute.assert_called_once()
            call_args = mock_execute.call_args
            assert call_args[0][0] == "use_tool"  # operation

    @pytest.mark.asyncio
    async def test_start_streaming_session(self, unified_client):
        """Tests Streaming-Session-Start."""
        unified_client._stream_client = AsyncMock()

        with patch.object(unified_client, "is_protocol_available") as mock_available:
            mock_available.return_value = True

            callback = AsyncMock()
            await unified_client.start_streaming_session(callback)

            unified_client._stream_client.connect.assert_called_once()
            unified_client._stream_client.subscribe.assert_called_once_with(
                "agent_events", callback
            )

    @pytest.mark.asyncio
    async def test_start_streaming_session_not_available(self, unified_client):
        """Tests Streaming-Session-Start if not available."""
        with patch.object(unified_client, "is_protocol_available") as mock_available:
            mock_available.return_value = False

            with pytest.raises(ProtocolError, match="stream Protocol not available"):
                await unified_client.start_streaming_session()

    @pytest.mark.asyncio
    async def test_health_check_high_level_api(self, unified_client):
        """Tests High-Level Health-Check API."""
        with patch.object(unified_client, "execute_agent_operation") as mock_execute:
            mock_execute.return_value = {"status": "healthy", "version": "1.0.0"}

            result = await unified_client.health_check()

            assert result["status"] == "healthy"
            mock_execute.assert_called_once_with("health_check", {})

    @pytest.mark.asyncio
    async def test_register_agent_high_level_api(self, unified_client):
        """Tests High-Level Agent-Regisration API."""
        with patch.object(unified_client, "execute_agent_operation") as mock_execute:
            mock_execute.return_value = {
                "agent_id": "registered-agent",
                "status": "registered",
            }

            result = await unified_client.register_agent(
                "Test Agent",
                "1.0.0",
                "Test description",
                ["capability1", "capability2"],
            )

            assert result["agent_id"] == "registered-agent"
            call_args = mock_execute.call_args[0][1]  # Second argaroatthet (data)
            assert call_args["name"] == "Test Agent"
            assert call_args["version"] == "1.0.0"
            assert call_args["capabilities"] == ["capability1", "capability2"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
