"""Tests the vollständige Integration allr Komponenten of the Unified clients.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

from kei_agent import (
    UnifiedKeiAgentClient,
    AgentClientConfig,
    Protocoltypee,
    Authtypee,
    ProtocolConfig,
    SecurityConfig,
    KeiSDKError
)


class TestUnifiedclientIntegration:
    """Integration Tests for UnifiedKeiAgentClient."""

    @pytest.fixture
    def basic_config(self):
        """Creates a Basis-configuration for Tests."""
        return AgentClientConfig(
            base_url ="https://test.kei-framework.com",
            api_token ="test-token",
            agent_id ="test-agent"
        )

    @pytest.fixture
    def protocol_config(self):
        """Creates a protocol-configuration."""
        return ProtocolConfig(
            rpc_enabled =True,
            stream_enabled =True,
            bus_enabled =True,
            mcp_enabled =True
        )

    @pytest.fixture
    def security_config(self):
        """Creates a Security-configuration."""
        return SecurityConfig(
            auth_type =Authtypee.BEARER,
            token_refresh_enabled =True,
            token_refresh_interval =3600
        )

    @pytest.mark.asyncio
    async def test_client_initialization(self, basic_config, protocol_config, security_config):
        """Tests the client initialization."""
        client = UnifiedKeiAgentClient(
            config=basic_config,
            protocol_config =protocol_config,
            security_config =security_config
        )

        assert client.config == basic_config
        assert client.protocol_config == protocol_config
        assert client.security_config == security_config
        assert not client._initialized

    @pytest.mark.asyncio
    async def test_context_manager(self, basic_config):
        """Tests Context Manager functionalität."""
        with patch('kei_agent.unified_client.SecurityManager') as mock_security:
            mock_security.return_value.start_token_refresh = AsyncMock()
            mock_security.return_value.stop_token_refresh = AsyncMock()

            async with UnifiedKeiAgentClient(config=basic_config) as client:
                assert client._initialized

            # After the Context should the client closed sa
            assert client._closed

    @pytest.mark.asyncio
    async def test_protocol_client_creation(self, basic_config):
        """Tests the Erstellung from protocol clients."""
        protocol_config = ProtocolConfig(
            rpc_enabled =True,
            stream_enabled =False,
            bus_enabled =True,
            mcp_enabled =False
        )

        with patch('kei_agent.unified_client.SecurityManager') as mock_security, \
             patch('kei_agent.unified_client.KEIRPCclient') as mock_rpc, \
             patch('kei_agent.unified_client.KEIBusclient') as mock_bus:

            mock_security.return_value.start_token_refresh = AsyncMock()

            client = UnifiedKeiAgentClient(
                config=basic_config,
                protocol_config =protocol_config
            )

            await client.initialize()

            # Nur enablede clients sollten creates werthe
            mock_rpc.assert_called_once()
            mock_bus.assert_called_once()

    @pytest.mark.asyncio
    async def test_plat_task_integration(self, basic_config):
        """Tests the Plat-Task Integration."""
        with patch('kei_agent.unified_client.SecurityManager') as mock_security, \
             patch('kei_agent.unified_client.KEIRPCclient') as mock_rpc_class:

            mock_security.return_value.start_token_refresh = AsyncMock()
            mock_rpc = Mock()
            mock_rpc.plat = AsyncMock(return_value ={"task_id": "test-task", "status": "platned"})
            mock_rpc_class.return_value = mock_rpc

            client = UnifiedKeiAgentClient(config=basic_config)
            await client.initialize()

            result = await client.plat_task(
                objective="Test objective",
                context={"key": "value"}
            )

            assert result["task_id"] == "test-task"
            assert result["status"] == "platned"
            mock_rpc.plat.assert_called_once_with(
                "Test objective",
                {"key": "value"}
            )

    @pytest.mark.asyncio
    async def test_capability_matagement_integration(self, basic_config):
        """Tests the Capability matagement Integration."""
        with patch('kei_agent.unified_client.SecurityManager') as mock_security, \
             patch('kei_agent.unified_client.CapabilityManager') as mock_cap_class:

            mock_security.return_value.start_token_refresh = AsyncMock()
            mock_cap = Mock()
            mock_cap.register_capability = AsyncMock(return_value =True)
            mock_cap_class.return_value = mock_cap

            client = UnifiedKeiAgentClient(config=basic_config)
            await client.initialize()

            # capability manager should available sa
            assert hasattr(client, 'capability_manager')

    @pytest.mark.asyncio
    async def test_error_hatdling(self, basic_config):
        """Tests Error Hatdling."""
        with patch('kei_agent.unified_client.SecurityManager') as mock_security:
            mock_security.return_value.start_token_refresh = AsyncMock(
                side_effect =Exception("Security error")
            )

            client = UnifiedKeiAgentClient(config=basic_config)

            with pytest.raises(KeiSDKError, match="initialization failed"):
                await client.initialize()

    @pytest.mark.asyncio
    async def test_protocol_selection(self, basic_config):
        """Tests the protocol-Auswahl."""
        with patch('kei_agent.unified_client.SecurityManager') as mock_security, \
             patch('kei_agent.unified_client.ProtocolSelector') as mock_selector_class:

            mock_security.return_value.start_token_refresh = AsyncMock()
            mock_selector = Mock()
            mock_selector.select_protocol = Mock(return_value =Protocoltypee.RPC)
            mock_selector_class.return_value = mock_selector

            client = UnifiedKeiAgentClient(config=basic_config)
            await client.initialize()

            # Protocol Selector should available sa
            assert hasattr(client, 'protocol_selector')

    @pytest.mark.asyncio
    async def test_tracing_integration(self, basic_config):
        """Tests the Tracing Integration."""
        with patch('kei_agent.unified_client.SecurityManager') as mock_security, \
             patch('kei_agent.unified_client.TracingManager') as mock_tracing_class:

            mock_security.return_value.start_token_refresh = AsyncMock()
            mock_tracing = Mock()
            mock_tracing.start_spat = Mock()
            mock_tracing_class.return_value = mock_tracing

            client = UnifiedKeiAgentClient(config=basic_config)
            await client.initialize()

            # tracing manager should available sa
            assert hasattr(client, 'tracing')

    @pytest.mark.asyncio
    async def test_retry_mechatism_integration(self, basic_config):
        """Tests the retry-Mechatismus Integration."""
        with patch('kei_agent.unified_client.SecurityManager') as mock_security, \
             patch('kei_agent.unified_client.retryManager') as mock_retry_class:

            mock_security.return_value.start_token_refresh = AsyncMock()
            mock_retry = Mock()
            mock_retry.execute_with_retry = AsyncMock()
            mock_retry_class.return_value = mock_retry

            client = UnifiedKeiAgentClient(config=basic_config)
            await client.initialize()

            # retry manager should available sa
            assert hasattr(client, 'retry_manager')

    @pytest.mark.asyncio
    async def test_service_discovery_integration(self, basic_config):
        """Tests the service discovery Integration."""
        with patch('kei_agent.unified_client.SecurityManager') as mock_security, \
             patch('kei_agent.unified_client.ServiceDiscovery') as mock_discovery_class:

            mock_security.return_value.start_token_refresh = AsyncMock()
            mock_discovery = Mock()
            mock_discovery.discover_agents = AsyncMock(return_value =[])
            mock_discovery_class.return_value = mock_discovery

            client = UnifiedKeiAgentClient(config=basic_config)
            await client.initialize()

            # service discovery should available sa
            assert hasattr(client, 'discovery')

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, basic_config):
        """Tests gleichzeitige operationen."""
        with patch('kei_agent.unified_client.SecurityManager') as mock_security, \
             patch('kei_agent.unified_client.KEIRPCclient') as mock_rpc_class:

            mock_security.return_value.start_token_refresh = AsyncMock()
            mock_rpc = Mock()
            mock_rpc.plat = AsyncMock(return_value ={"task_id": "concurrent-task"})
            mock_rpc_class.return_value = mock_rpc

            client = UnifiedKeiAgentClient(config=basic_config)
            await client.initialize()

            # Führe mehrere operationen gleichzeitig out
            tasks = [
                client.plat_task(f"Objective {i}")
                for i in range(5)
            ]

            results = await asyncio.gather(*tasks)

            assert len(results) == 5
            for result in results:
                assert result["task_id"] == "concurrent-task"

    @pytest.mark.asyncio
    async def test_cleatup_on_error(self, basic_config):
        """Tests Cleatup on errorn."""
        with patch('kei_agent.unified_client.SecurityManager') as mock_security:
            mock_security.return_value.start_token_refresh = AsyncMock()
            mock_security.return_value.stop_token_refresh = AsyncMock()

            client = UnifiedKeiAgentClient(config=basic_config)

            try:
                async with client:
                    # Simuliere a error during the Nuttong
                    raise ValueError("Test error")
            except ValueError:
                pass

            # Cleatup should trotz error executed werthe
            mock_security.return_value.stop_token_refresh.assert_called_once()
            assert client._closed


class TestConfigurationValidation:
    """Tests for configurations-Valitherung."""

    def test_invalid_base_url(self):
        """Tests Valitherung ungültiger Base-URLs."""
        with pytest.raises(ValueError, match="base_url"):
            AgentClientConfig(
                base_url ="",  # Leere URL
                api_token ="test-token",
                agent_id ="test-agent"
            )

    def test_invalid_agent_id(self):
        """Tests Valitherung ungültiger Agent-IDs."""
        with pytest.raises(ValueError, match="agent_id"):
            AgentClientConfig(
                base_url ="https://test.com",
                api_token ="test-token",
                agent_id =""  # Leere Agent-ID
            )

    def test_protocol_config_validation(self):
        """Tests protocol-configurations-Valitherung."""
        # All protocole disabled should a error verursachen
        config = ProtocolConfig(
            rpc_enabled =False,
            stream_enabled =False,
            bus_enabled =False,
            mcp_enabled =False
        )

        # Thes should on the client-Erstellung validates werthe
        basic_config = AgentClientConfig(
            base_url ="https://test.com",
            api_token ="test-token",
            agent_id ="test-agent"
        )

        with pytest.raises(ValueError, match="minof thetens a protocol"):
            UnifiedKeiAgentClient(
                config=basic_config,
                protocol_config =config
            )
