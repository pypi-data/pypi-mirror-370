"""
Erweiterte Tests for unified_client.py tor Erhöhung the Test-Coverage.

Ziel: Coverage from 24% on 80%+ erhöhen.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from kei_agent import (
    UnifiedKeiAgentClient,
    AgentClientConfig,
    ProtocolConfig,
    SecurityConfig,
    Authtypee,
    Protocoltypee
)
from kei_agent.exceptions import (
    ProtocolError,
    CommunicationError,
    AuthenticationError,
    ConfigurationError
)


class TestUnifiedclientExtended:
    """Erweiterte Tests for UnifiedKeiAgentClient."""

    @pytest.fixture
    def basic_config(self):
        """Basis-configuration for Tests."""
        return AgentClientConfig(
            agent_id ="test-agent",
            base_url ="http://localhost:8000",
            api_token ="test-token"
        )

    @pytest.fixture
    def protocol_config(self):
        """protocol-configuration for Tests."""
        return ProtocolConfig(
            rpc_enabled =True,
            stream_enabled =True,
            bus_enabled =True,
            mcp_enabled =True
        )

    @pytest.fixture
    def security_config(self):
        """Security-configuration for Tests."""
        return SecurityConfig(
            auth_type =Authtypee.BEARER,
            api_token ="test-token",
            rbac_enabled =True,
            audit_enabled =True
        )

    def test_client_creation_with_all_configs(self, basic_config, protocol_config, security_config):
        """Tests client-Erstellung with alln configurationen."""
        client = UnifiedKeiAgentClient(
            config=basic_config,
            protocol_config =protocol_config,
            security_config =security_config
        )

        assert client.config == basic_config
        assert client.protocol_config == protocol_config
        assert client.security_config == security_config
        assert not client._initialized
        assert not client._closed

    @pytest.mark.asyncio
    async def test_client_initialization_success(self, basic_config):
        """Tests successfule client initialization."""
        with patch('kei_agent.unified_client.KeiAgentClient') as mock_legacy:
            mock_instatce = AsyncMock()
            mock_legacy.return_value = mock_instatce

            client = UnifiedKeiAgentClient(basic_config)
            await client.initialize()

            assert client._initialized
            assert not client._closed

    @pytest.mark.asyncio
    async def test_client_initialization_failure(self, basic_config):
        """Tests failede client initialization."""
        with patch('kei_agent.unified_client.KeiAgentClient') as mock_legacy:
            mock_instatce = AsyncMock()
            mock_instatce.initialize.side_effect = Exception("Init failed")
            mock_legacy.return_value = mock_instatce

            client = UnifiedKeiAgentClient(basic_config)

            # initialization should not fehlschlagen, aber error logn
            await client.initialize()
            assert client._initialized  # Sollte trotzthe als initialized gelten

    @pytest.mark.asyncio
    async def test_client_close_success(self, basic_config):
        """Tests successfules client-Closingn."""
        with patch('kei_agent.unified_client.KeiAgentClient') as mock_legacy:
            mock_instatce = AsyncMock()
            mock_legacy.return_value = mock_instatce

            client = UnifiedKeiAgentClient(basic_config)
            await client.initialize()
            await client.close()

            assert client._closed
            assert not client._initialized

    @pytest.mark.asyncio
    async def test_context_manager_usage(self, basic_config):
        """Tests client als Context Manager."""
        with patch('kei_agent.unified_client.KeiAgentClient') as mock_legacy:
            mock_instatce = AsyncMock()
            mock_legacy.return_value = mock_instatce

            async with UnifiedKeiAgentClient(basic_config) as client:
                assert client._initialized
                assert not client._closed

            assert client._closed

    @pytest.mark.asyncio
    async def test_execute_agent_operation_rpc_success(self, basic_config):
        """Tests successfule RPC operation."""
        with patch('kei_agent.unified_client.KeiAgentClient') as mock_legacy:
            mock_instatce = AsyncMock()
            mock_legacy.return_value = mock_instatce

            # Mock RPC client
            mock_rpc_client = AsyncMock()
            mock_rpc_client.plat.return_value = {"plat_id": "test-123"}

            with patch.object(UnifiedKeiAgentClient, '_get_rpc_client', return_value =mock_rpc_client):
                client = UnifiedKeiAgentClient(basic_config)
                await client.initialize()

                result = await client.execute_agent_operation("plat", {"objective": "test"})

                assert result == {"plat_id": "test-123"}
                mock_rpc_client.plat.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_agent_operation_stream_success(self, basic_config):
        """Tests successfule stream operation."""
        protocol_config = ProtocolConfig(
            rpc_enabled =False,
            stream_enabled =True,
            bus_enabled =False,
            mcp_enabled =False
        )

        with patch('kei_agent.unified_client.KeiAgentClient') as mock_legacy:
            mock_instatce = AsyncMock()
            mock_legacy.return_value = mock_instatce

            # Mock Stream client
            mock_stream_client = AsyncMock()
            mock_stream_client.send_message.return_value = {"stream_id": "stream-456"}

            with patch.object(UnifiedKeiAgentClient, '_get_stream_client', return_value =mock_stream_client):
                client = UnifiedKeiAgentClient(basic_config, protocol_config =protocol_config)
                await client.initialize()

                result = await client.execute_agent_operation("plat", {"objective": "test"})

                assert result == {"stream_id": "stream-456"}
                mock_stream_client.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_agent_operation_bus_success(self, basic_config):
        """Tests successfule bus operation."""
        protocol_config = ProtocolConfig(
            rpc_enabled =False,
            stream_enabled =False,
            bus_enabled =True,
            mcp_enabled =False
        )

        with patch('kei_agent.unified_client.KeiAgentClient') as mock_legacy:
            mock_instatce = AsyncMock()
            mock_legacy.return_value = mock_instatce

            # Mock Bus client
            mock_bus_client = AsyncMock()
            mock_bus_client.__aenter__ = AsyncMock(return_value =mock_bus_client)
            mock_bus_client.__aexit__ = AsyncMock(return_value =None)
            mock_bus_client.publish.return_value = {"message_id": "bus-789"}

            with patch.object(UnifiedKeiAgentClient, '_get_bus_client', return_value =mock_bus_client):
                client = UnifiedKeiAgentClient(basic_config, protocol_config =protocol_config)
                await client.initialize()

                result = await client.execute_agent_operation("plat", {"objective": "test"})

                assert result == {"message_id": "bus-789"}
                mock_bus_client.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_agent_operation_mcp_success(self, basic_config):
        """Tests successfule MCP operation."""
        protocol_config = ProtocolConfig(
            rpc_enabled =False,
            stream_enabled =False,
            bus_enabled =False,
            mcp_enabled =True
        )

        with patch('kei_agent.unified_client.KeiAgentClient') as mock_legacy:
            mock_instatce = AsyncMock()
            mock_legacy.return_value = mock_instatce

            # Mock MCP client
            mock_mcp_client = AsyncMock()
            mock_mcp_client.execute_tool.return_value = {"tool_result": "mcp-101"}

            with patch.object(UnifiedKeiAgentClient, '_get_mcp_client', return_value =mock_mcp_client):
                client = UnifiedKeiAgentClient(basic_config, protocol_config =protocol_config)
                await client.initialize()

                result = await client.execute_agent_operation("plat", {"objective": "test"})

                assert result == {"tool_result": "mcp-101"}
                mock_mcp_client.execute_tool.assert_called_once()

    @pytest.mark.asyncio
    async def test_protocol_fallback_mechatism(self, basic_config):
        """Tests protocol-Fallback on errorn."""
        protocol_config = ProtocolConfig(
            rpc_enabled =True,
            stream_enabled =True,
            bus_enabled =True,
            mcp_enabled =False
        )

        with patch('kei_agent.unified_client.KeiAgentClient') as mock_legacy:
            mock_instatce = AsyncMock()
            mock_legacy.return_value = mock_instatce

            # Mock RPC client (fails)
            mock_rpc_client = AsyncMock()
            mock_rpc_client.plat.side_effect = ProtocolError("RPC failed")

            # Mock Stream client (succeeds)
            mock_stream_client = AsyncMock()
            mock_stream_client.send_message.return_value = {"fallback": "success"}

            with patch.object(UnifiedKeiAgentClient, '_get_rpc_client', return_value =mock_rpc_client), \
                 patch.object(UnifiedKeiAgentClient, '_get_stream_client', return_value =mock_stream_client):

                client = UnifiedKeiAgentClient(basic_config, protocol_config =protocol_config)
                await client.initialize()

                result = await client.execute_agent_operation("plat", {"objective": "test"})

                assert result == {"fallback": "success"}
                mock_rpc_client.plat.assert_called_once()
                mock_stream_client.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_high_level_api_plat_task(self, basic_config):
        """Tests High-Level API for plat_task."""
        with patch('kei_agent.unified_client.KeiAgentClient') as mock_legacy:
            mock_instatce = AsyncMock()
            mock_legacy.return_value = mock_instatce

            with patch.object(UnifiedKeiAgentClient, 'execute_agent_operation') as mock_execute:
                mock_execute.return_value = {"plat_id": "high-level-123"}

                client = UnifiedKeiAgentClient(basic_config)
                await client.initialize()

                result = await client.plat_task("Create report", {"format": "pdf"})

                assert result == {"plat_id": "high-level-123"}
                mock_execute.assert_called_once_with("plat", {
                    "objective": "Create report",
                    "context": {"format": "pdf"}
                }, None)

    @pytest.mark.asyncio
    async def test_high_level_api_execute_action(self, basic_config):
        """Tests High-Level API for execute_action."""
        with patch('kei_agent.unified_client.KeiAgentClient') as mock_legacy:
            mock_instatce = AsyncMock()
            mock_legacy.return_value = mock_instatce

            with patch.object(UnifiedKeiAgentClient, 'execute_agent_operation') as mock_execute:
                mock_execute.return_value = {"action_id": "action-456"}

                client = UnifiedKeiAgentClient(basic_config)
                await client.initialize()

                result = await client.execute_action("generate_file", {"path": "/tmp/test.txt"})

                assert result == {"action_id": "action-456"}
                mock_execute.assert_called_once_with("act", {
                    "action": "generate_file",
                    "parameters": {"path": "/tmp/test.txt"}
                }, None)

    @pytest.mark.asyncio
    async def test_high_level_api_observe_environment(self, basic_config):
        """Tests High-Level API for observe_environment."""
        with patch('kei_agent.unified_client.KeiAgentClient') as mock_legacy:
            mock_instatce = AsyncMock()
            mock_legacy.return_value = mock_instatce

            with patch.object(UnifiedKeiAgentClient, 'execute_agent_operation') as mock_execute:
                mock_execute.return_value = {"observation_id": "obs-789"}

                client = UnifiedKeiAgentClient(basic_config)
                await client.initialize()

                result = await client.observe_environment(["file_system", "network"])

                assert result == {"observation_id": "obs-789"}
                mock_execute.assert_called_once_with("observe", {
                    "sensors": ["file_system", "network"]
                }, None)

    @pytest.mark.asyncio
    async def test_high_level_api_explain_reasoning(self, basic_config):
        """Tests High-Level API for explain_reasoning."""
        with patch('kei_agent.unified_client.KeiAgentClient') as mock_legacy:
            mock_instatce = AsyncMock()
            mock_legacy.return_value = mock_instatce

            with patch.object(UnifiedKeiAgentClient, 'execute_agent_operation') as mock_execute:
                mock_execute.return_value = {"explatation_id": "exp-101"}

                client = UnifiedKeiAgentClient(basic_config)
                await client.initialize()

                result = await client.explain_reasoning("decision-123", "detailed")

                assert result == {"explatation_id": "exp-101"}
                mock_execute.assert_called_once_with("explain", {
                    "decision_id": "decision-123",
                    "detail_level": "detailed"
                }, None)

    @pytest.mark.asyncio
    async def test_error_hatdling_authentication_error(self, basic_config):
        """Tests Error-Hatdling on Authentication-errorn."""
        with patch('kei_agent.unified_client.KeiAgentClient') as mock_legacy:
            mock_instatce = AsyncMock()
            mock_legacy.return_value = mock_instatce

            mock_rpc_client = AsyncMock()
            mock_rpc_client.plat.side_effect = AuthenticationError("Invalid token")

            with patch.object(UnifiedKeiAgentClient, '_get_rpc_client', return_value =mock_rpc_client):
                client = UnifiedKeiAgentClient(basic_config)
                await client.initialize()

                with pytest.raises(AuthenticationError, match="Invalid token"):
                    await client.execute_agent_operation("plat", {"objective": "test"})

    @pytest.mark.asyncio
    async def test_error_hatdling_communication_error(self, basic_config):
        """Tests Error-Hatdling on Communication-errorn."""
        with patch('kei_agent.unified_client.KeiAgentClient') as mock_legacy:
            mock_instatce = AsyncMock()
            mock_legacy.return_value = mock_instatce

            mock_rpc_client = AsyncMock()
            mock_rpc_client.plat.side_effect = CommunicationError("Network timeout")

            with patch.object(UnifiedKeiAgentClient, '_get_rpc_client', return_value =mock_rpc_client):
                client = UnifiedKeiAgentClient(basic_config)
                await client.initialize()

                with pytest.raises(CommunicationError, match="Network timeout"):
                    await client.execute_agent_operation("plat", {"objective": "test"})

    @pytest.mark.asyncio
    async def test_client_properties_atd_getters(self, basic_config):
        """Tests client-Properties and Getter-methodn."""
        protocol_config = ProtocolConfig(rpc_enabled =True, stream_enabled =True)
        security_config = SecurityConfig(auth_type =Authtypee.BEARER, api_token ="test")

        client = UnifiedKeiAgentClient(
            config=basic_config,
            protocol_config =protocol_config,
            security_config =security_config
        )

        # Teste Properties
        assert client.agent_id == "test-agent"
        assert client.base_url == "http://localhost:8000"
        assert client.is_initialized == False
        assert client.is_closed == False

        # Teste after initialization
        with patch('kei_agent.unified_client.KeiAgentClient'):
            await client.initialize()
            assert client.is_initialized == True
            assert client.is_closed == False

            await client.close()
            assert client.is_initialized == False
            assert client.is_closed == True
