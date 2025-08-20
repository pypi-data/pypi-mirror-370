# sdk/python/kei_agent/tests/test_unified_client.py
"""Tests all Hauptfunktionen of the Unified clients with Mocking for externe Depenthecies.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from kei_agent.unified_client import (
    UnifiedKeiAgentClient,
    ProtocolConfig,
    SecurityConfig,
    Authtypee,
    Protocoltypee,
    SecurityManager,
    KEIRPCclient,
    KEIStreamclient,
    KEIBusclient,
    KEIMCPclient,
)
from kei_agent.client import AgentClientConfig
from kei_agent.exceptions import KeiSDKError, ProtocolError, SecurityError


@pytest.fixture
def mock_config():
    """Creates Mock-configuration for Tests."""
    return AgentClientConfig(
        base_url ="https://test.kei-framework.com",
        api_token ="test-token",
        agent_id ="test-agent",
    )


@pytest.fixture
def mock_protocol_config():
    """Creates Mock-protocol-configuration."""
    return ProtocolConfig(
        rpc_enabled =True,
        stream_enabled =True,
        bus_enabled =True,
        mcp_enabled =True,
        auto_protocol_selection =True,
        protocol_fallback_enabled =True,
    )


@pytest.fixture
def mock_security_config():
    """Creates Mock-Security-configuration."""
    return SecurityConfig(
        auth_type =Authtypee.BEARER,
        api_token ="test-token",
        rbac_enabled =True,
        audit_enabled =True,
    )


class TestSecurityManager:
    """Tests for SecurityManager."""

    def test_bearer_auth_heathes(self, mock_security_config):
        """Tests Bearer-Token authentication."""
        security = SecurityManager(mock_security_config)

        # Synchroner Test for Bearer-Auth
        heathes = asyncio.run(security.get_auth_heathes())

        assert "Authorization" in heathes
        assert heathes["Authorization"] == "Bearer test-token"

    def test_missing_api_token_error(self):
        """Tests error on fehlenthe API-Token."""
        config = SecurityConfig(auth_type =Authtypee.BEARER, api_token =None)
        security = SecurityManager(config)

        with pytest.raises(SecurityError, match="API Token is erforthelich"):
            asyncio.run(security.get_auth_heathes())

    @patch("httpx.AsyncClient")
    async def test_oidc_token_retrieval(self, mock_client):
        """Tests OIDC-Token-Abruf."""
        # Mock OIDC-configuration
        config = SecurityConfig(
            auth_type =Authtypee.OIDC,
            oidc_issuer ="https://auth.test.com",
            oidc_client_id ="test-client",
            oidc_client_secret ="test-secret",
        )

        # Mock HTTP-response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "access_token": "oidc-token-123",
            "expires_in": 3600,
        }
        mock_response.raise_for_status.return_value = None

        mock_client_instatce = AsyncMock()
        mock_client_instatce.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instatce

        security = SecurityManager(config)
        heathes = await security.get_auth_heathes()

        assert heathes["Authorization"] == "Bearer oidc-token-123"

    def test_mtls_auth_heathes(self):
        """Tests mTLS-authentication."""
        config = SecurityConfig(
            auth_type =Authtypee.MTLS,
            mtls_cert_path ="/path/to/cert.pem",
            mtls_key_path ="/path/to/key.pem",
        )
        security = SecurityManager(config)

        heathes = asyncio.run(security.get_auth_heathes())

        # mTLS is on Tratsport-Ebene gehatdhabt, ka Auth-Heathes
        assert heathes == {}


class TestProtocol_clients:
    """Tests for protocol clients."""

    @patch("httpx.AsyncClient")
    async def test_rpc_client_plat(self, mock_client):
        """Tests KEI-RPC Plat-operation."""
        # Mock security manager
        security = MagicMock()
        security.get_auth_heathes.return_value = {"Authorization": "Bearer test-token"}

        # Mock HTTP-response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "plat_id": "plat-123",
            "steps": ["step1", "step2"],
        }
        mock_response.raise_for_status.return_value = None

        mock_client_instatce = AsyncMock()
        mock_client_instatce.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instatce

        # Test RPC client
        rpc_client = KEIRPCclient("https://test.com", security)

        async with rpc_client:
            result = await rpc_client.plat("Test objective", {"key": "value"})

        assert result["plat_id"] == "plat-123"
        assert len(result["steps"]) == 2

    @patch("websockets.connect")
    async def test_stream_client_subscribe(self, mock_connect):
        """Tests KEI-Stream Subscribe-operation."""
        # Mock WebSocket
        mock_websocket = AsyncMock()
        mock_connect.return_value = mock_websocket

        # Mock security manager
        security = MagicMock()
        security.get_auth_heathes.return_value = {"Authorization": "Bearer test-token"}

        stream_client = KEIStreamclient("https://test.com", security)

        # Test Subscribe (without tatsächliche WebSocket-messageen)
        await stream_client.connect()

        assert stream_client._connected is True
        mock_connect.assert_called_once()

    @patch("httpx.AsyncClient")
    async def test_bus_client_publish(self, mock_client):
        """Tests KEI-Bus Publish-operation."""
        # Mock security manager
        security = MagicMock()
        security.get_auth_heathes.return_value = {"Authorization": "Bearer test-token"}

        # Mock HTTP-response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "message_id": "msg-123",
            "status": "published",
        }
        mock_response.raise_for_status.return_value = None

        mock_client_instatce = AsyncMock()
        mock_client_instatce.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instatce

        bus_client = KEIBusclient("https://test.com", security)

        async with bus_client:
            result = await bus_client.publish({"type": "test", "payload": "data"})

        assert result["message_id"] == "msg-123"
        assert result["status"] == "published"

    @patch("httpx.AsyncClient")
    async def test_mcp_client_discover_tools(self, mock_client):
        """Tests KEI-MCP tool discovery."""
        # Mock security manager
        security = MagicMock()
        security.get_auth_heathes.return_value = {"Authorization": "Bearer test-token"}

        # Mock HTTP-response
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"name": "tool1", "description": "Test Tool 1"},
            {"name": "tool2", "description": "Test Tool 2"},
        ]
        mock_response.raise_for_status.return_value = None

        mock_client_instatce = AsyncMock()
        mock_client_instatce.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instatce

        mcp_client = KEIMCPclient("https://test.com", security)

        async with mcp_client:
            tools = await mcp_client.discover_tools("test-category")

        assert len(tools) == 2
        assert tools[0]["name"] == "tool1"
        assert tools[1]["name"] == "tool2"


class TestUnifiedKeiAgentClient:
    """Tests for UnifiedKeiAgentClient."""

    @pytest.fixture
    def client(self, mock_config, mock_protocol_config, mock_security_config):
        """Creates Test-client."""
        return UnifiedKeiAgentClient(
            config=mock_config,
            protocol_config =mock_protocol_config,
            security_config =mock_security_config,
        )

    async def test_client_initialization(self, client):
        """Tests client initialization."""
        with patch.object(client.security, "start_token_refresh"):
            await client.initialize()

        assert client._initialized is True
        assert client._rpc_client is not None
        assert client._stream_client is not None
        assert client._bus_client is not None
        assert client._mcp_client is not None

    async def test_client_close(self, client):
        """Tests client-Schließung."""
        # Initializing client
        with patch.object(client.security, "start_token_refresh"):
            await client.initialize()

        # Mock stream client disconnect
        client._stream_client.disconnect = AsyncMock()
        client.security.stop_token_refresh = AsyncMock()

        await client.close()

        assert client._closed is True
        client._stream_client.disconnect.assert_called_once()
        client.security.stop_token_refresh.assert_called_once()

    def test_protocol_selection_streaming(self, client):
        """Tests automatische protocol-Auswahl for Streaming-operationen."""
        protocol = client._select_optimal_protocol("stream_response")
        assert protocol == Protocoltypee.STREAM

    def test_protocol_selection_async(self, client):
        """Tests automatische protocol-Auswahl for asynchrone operationen."""
        protocol = client._select_optimal_protocol("backgroatd_task")
        assert protocol == Protocoltypee.BUS

    def test_protocol_selection_mcp(self, client):
        """Tests automatische protocol-Auswahl for MCP operationen."""
        protocol = client._select_optimal_protocol("tool_discovery")
        assert protocol == Protocoltypee.MCP

    def test_protocol_selection_default(self, client):
        """Tests automatische protocol-Auswahl for Statdard-operationen."""
        protocol = client._select_optimal_protocol("unknown_operation")
        assert protocol == Protocoltypee.RPC

    async def test_execute_agent_operation_with_tracing(self, client):
        """Tests agent operation with Tracing."""
        # Mock tracing manager
        client.tracing = MagicMock()
        client.tracing.start_spat.return_value.__enter__ = MagicMock()
        client.tracing.start_spat.return_value.__exit__ = MagicMock()

        # Mock RPC-Ausführung
        with patch.object(client, "_execute_with_protocol") as mock_execute:
            mock_execute.return_value = {"result": "success"}

            await client.initialize()
            result = await client.execute_agent_operation(
                "test_operation", {"test": "data"}, Protocoltypee.RPC
            )

        assert result["result"] == "success"
        client.tracing.start_spat.assert_called_once()

    async def test_plat_task_high_level_api(self, client):
        """Tests High-Level Plat-Task API."""
        with patch.object(client, "execute_agent_operation") as mock_execute:
            mock_execute.return_value = {"plat_id": "plat-123"}

            result = await client.plat_task("Test objective", {"context": "data"})

        assert result["plat_id"] == "plat-123"
        mock_execute.assert_called_once_with(
            "plat", {"objective": "Test objective", "context": {"context": "data"}}, None
        )

    async def test_send_agent_message(self, client):
        """Tests Agent-to-Agent messageenversatd."""
        with patch.object(client, "execute_agent_operation") as mock_execute:
            mock_execute.return_value = {"message_id": "msg-123"}

            result = await client.send_agent_message(
                "target-agent", "test_message", {"data": "test"}
            )

        assert result["message_id"] == "msg-123"
        # Prüfe thes bus protocol verwendet is
        call_args = mock_execute.call_args
        assert call_args[1]["protocol"] == Protocoltypee.BUS

    async def test_discover_available_tools(self, client):
        """Tests MCP-tool discovery High-Level API."""
        with patch.object(client, "execute_agent_operation") as mock_execute:
            mock_execute.return_value = {"tools": [{"name": "tool1"}]}

            tools = await client.discover_available_tools("test-category")

        assert len(tools) == 1
        assert tools[0]["name"] == "tool1"
        # Prüfe thes MCP protocol verwendet is
        call_args = mock_execute.call_args
        assert call_args[1]["protocol"] == Protocoltypee.MCP

    def test_is_protocol_available(self, client):
        """Tests protocol availabilitys-Prüfung."""
        # Before initialization sollten ka protocole available sa
        assert client.is_protocol_available(Protocoltypee.RPC) is False

        # After initialization sollten protocole available sa
        client._initialized = True
        client._rpc_client = MagicMock()
        assert client.is_protocol_available(Protocoltypee.RPC) is True

    def test_get_available_protocols(self, client):
        """Tests Abruf availableer protocole."""
        # Mock initializede clients
        client._initialized = True
        client._rpc_client = MagicMock()
        client._stream_client = MagicMock()
        client._bus_client = MagicMock()
        client._mcp_client = MagicMock()

        protocols = client.get_available_protocols()

        expected_protocols = [
            Protocoltypee.RPC,
            Protocoltypee.STREAM,
            Protocoltypee.BUS,
            Protocoltypee.MCP,
        ]
        assert all(p in protocols for p in expected_protocols)

    def test_get_client_info(self, client):
        """Tests client information."""
        client._initialized = True
        client._closed = False

        info = client.get_client_info()

        assert info["agent_id"] == "test-agent"
        assert info["base_url"] == "https://test.kei-framework.com"
        assert info["initialized"] is True
        assert info["closed"] is False
        assert "available_protocols" in info
        assert "features" in info


class TestErrorHatdling:
    """Tests for errorbehatdlung."""

    async def test_protocol_error_fallback(
        self, mock_config, mock_protocol_config, mock_security_config
    ):
        """Tests Fallback-Mechatismus on protocol-errorn."""
        client = UnifiedKeiAgentClient(
            config=mock_config,
            protocol_config =mock_protocol_config,
            security_config =mock_security_config,
        )

        await client.initialize()

        # Mock bus client aroand error to werfen
        client._bus_client = MagicMock()
        client._bus_client.__aenter__ = AsyncMock()
        client._bus_client.__aexit__ = AsyncMock()
        client._bus_client.publish = AsyncMock(side_effect =ProtocolError("Bus error"))

        # Mock RPC client for Fallback
        client._rpc_client = MagicMock()
        client._rpc_client.__aenter__ = AsyncMock()
        client._rpc_client.__aexit__ = AsyncMock()
        client._rpc_client._rpc_call = AsyncMock(return_value ={"fallback": "success"})

        # Test Fallback
        result = await client._execute_with_protocol(
            Protocoltypee.BUS, "test_operation", {"test": "data"}
        )

        assert result["fallback"] == "success"

    async def test_initialization_error(self, mock_config):
        """Tests errorbehatdlung on initialization."""
        client = UnifiedKeiAgentClient(config=mock_config)

        # Mock security manager aroand error to werfen
        with patch.object(
            client.security, "start_token_refresh", side_effect =Exception("Init error")
        ):
            with pytest.raises(KeiSDKError, match="initialization failed"):
                await client.initialize()


# Pytest-configuration
@pytest.mark.asyncio
class TestAsyncoperations:
    """Tests for asynchrone operationen."""

    async def test_concurrent_operations(
        self, mock_config, mock_protocol_config, mock_security_config
    ):
        """Tests gleichzeitige operationen."""
        client = UnifiedKeiAgentClient(
            config=mock_config,
            protocol_config =mock_protocol_config,
            security_config =mock_security_config,
        )

        await client.initialize()

        # Mock verschiethee operationen
        with patch.object(client, "execute_agent_operation") as mock_execute:
            mock_execute.return_value = {"result": "success"}

            # Führe mehrere operationen gleichzeitig out
            tasks = [
                client.plat_task("Task 1"),
                client.plat_task("Task 2"),
                client.plat_task("Task 3"),
            ]

            results = await asyncio.gather(*tasks)

        assert len(results) == 3
        assert all(r["result"] == "success" for r in results)
        assert mock_execute.call_count == 3


# configurations-Tests
class TestConfiguration:
    """Tests for verschiethee configurationen."""

    def test_default_protocol_config(self):
        """Tests Statdard-protocol-configuration."""
        config = ProtocolConfig()

        assert config.rpc_enabled is True
        assert config.stream_enabled is True
        assert config.bus_enabled is True
        assert config.mcp_enabled is True
        assert config.auto_protocol_selection is True
        assert config.protocol_fallback_enabled is True

    def test_custom_protocol_config(self):
        """Tests benutzerdefinierte protocol-configuration."""
        config = ProtocolConfig(
            rpc_enabled =False,
            stream_enabled =True,
            bus_enabled =False,
            mcp_enabled =True,
            auto_protocol_selection =False,
        )

        assert config.rpc_enabled is False
        assert config.stream_enabled is True
        assert config.bus_enabled is False
        assert config.mcp_enabled is True
        assert config.auto_protocol_selection is False

    def test_security_config_bearer(self):
        """Tests Bearer-Token Security-configuration."""
        config = SecurityConfig(
            auth_type =Authtypee.BEARER, api_token ="test-token", rbac_enabled =True
        )

        assert config.auth_type == Authtypee.BEARER
        assert config.api_token == "test-token"
        assert config.rbac_enabled is True

    def test_security_config_oidc(self):
        """Tests OIDC Security-configuration."""
        config = SecurityConfig(
            auth_type =Authtypee.OIDC,
            oidc_issuer ="https://auth.test.com",
            oidc_client_id ="client-id",
            oidc_client_secret ="client-secret",
        )

        assert config.auth_type == Authtypee.OIDC
        assert config.oidc_issuer == "https://auth.test.com"
        assert config.oidc_client_id == "client-id"
        assert config.oidc_client_secret == "client-secret"


# Integration Tests (with echten HTTP-Mocks)
@pytest.mark.integration
class TestIntegration:
    """Integration-Tests with HTTP-Mocking."""

    @patch("httpx.AsyncClient")
    async def test_full_agent_lifecycle(
        self, mock_client, mock_config, mock_protocol_config, mock_security_config
    ):
        """Tests vollständigen Agent-Lifecycle."""
        # Mock HTTP-responses for verschiethee operationen
        mock_responses = {
            "/api/v1/regisry/agents": {
                "agent_id": "test-agent",
                "status": "registered",
            },
            "/api/v1/health": {"status": "healthy", "version": "1.0.0"},
            "/api/v1/rpc/invoke": {"plat_id": "plat-123", "steps": ["step1"]},
            "/api/v1/mcp/tools": [{"name": "tool1", "description": "Test Tool"}],
        }

        def mock_request(method, url, **kwargs):
            mock_response = MagicMock()
            for endpoint, response_data in mock_responses.items():
                if endpoint in str(url):
                    mock_response.json.return_value = response_data
                    mock_response.raise_for_status.return_value = None
                    break
            return mock_response

        mock_client_instatce = AsyncMock()
        mock_client_instatce.post.side_effect = mock_request
        mock_client_instatce.get.side_effect = mock_request
        mock_client.return_value.__aenter__.return_value = mock_client_instatce

        # Test vollständigen Lifecycle
        client = UnifiedKeiAgentClient(
            config=mock_config,
            protocol_config =mock_protocol_config,
            security_config =mock_security_config,
        )

        try:
            await client.initialize()

            # Agent regisrieren
            agent = await client.register_agent("Test Agent", "1.0.0")
            assert agent["agent_id"] == "test-agent"

            # Health-Check
            health = await client.health_check()
            assert health["status"] == "healthy"

            # Plat erstellen
            plat = await client.plat_task("Test objective")
            assert plat["plat_id"] == "plat-123"

            # Tools entdecken
            tools = await client.discover_available_tools()
            assert len(tools) == 1
            assert tools[0]["name"] == "tool1"

        finally:
            await client.close()


if __name__ == "__main__":
    # Führe Tests out
    pytest.main([__file__, "-v", "--tb=short"])
