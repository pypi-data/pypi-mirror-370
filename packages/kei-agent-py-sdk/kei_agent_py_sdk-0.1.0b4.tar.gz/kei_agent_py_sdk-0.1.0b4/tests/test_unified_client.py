# sdk/python/kei_agent/tests/test_unified_client.py
"""
Unit Tests für UnifiedKeiAgentClient.

Testet alle Hauptfunktionen des Unified Clients mit Mocking für externe Dependencies.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from unified_client import (
    UnifiedKeiAgentClient,
    ProtocolConfig,
    SecurityConfig,
    AuthType,
    ProtocolType,
    SecurityManager,
    KEIRPCClient,
    KEIStreamClient,
    KEIBusClient,
    KEIMCPClient,
)
from client import AgentClientConfig
from exceptions import KeiSDKError, ProtocolError, SecurityError


@pytest.fixture
def mock_config():
    """Erstellt Mock-Konfiguration für Tests."""
    return AgentClientConfig(
        base_url="https://test.kei-framework.com",
        api_token="test-token",
        agent_id="test-agent",
    )


@pytest.fixture
def mock_protocol_config():
    """Erstellt Mock-Protokoll-Konfiguration."""
    return ProtocolConfig(
        rpc_enabled=True,
        stream_enabled=True,
        bus_enabled=True,
        mcp_enabled=True,
        auto_protocol_selection=True,
        protocol_fallback_enabled=True,
    )


@pytest.fixture
def mock_security_config():
    """Erstellt Mock-Security-Konfiguration."""
    return SecurityConfig(
        auth_type=AuthType.BEARER,
        api_token="test-token",
        rbac_enabled=True,
        audit_enabled=True,
    )


class TestSecurityManager:
    """Tests für SecurityManager."""

    def test_bearer_auth_headers(self, mock_security_config):
        """Testet Bearer-Token Authentifizierung."""
        security = SecurityManager(mock_security_config)

        # Synchroner Test für Bearer-Auth
        headers = asyncio.run(security.get_auth_headers())

        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer test-token"

    def test_missing_api_token_error(self):
        """Testet Fehler bei fehlendem API-Token."""
        config = SecurityConfig(auth_type=AuthType.BEARER, api_token=None)
        security = SecurityManager(config)

        with pytest.raises(SecurityError, match="API Token ist erforderlich"):
            asyncio.run(security.get_auth_headers())

    @patch("httpx.AsyncClient")
    async def test_oidc_token_retrieval(self, mock_client):
        """Testet OIDC-Token-Abruf."""
        # Mock OIDC-Konfiguration
        config = SecurityConfig(
            auth_type=AuthType.OIDC,
            oidc_issuer="https://auth.test.com",
            oidc_client_id="test-client",
            oidc_client_secret="test-secret",
        )

        # Mock HTTP-Response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "access_token": "oidc-token-123",
            "expires_in": 3600,
        }
        mock_response.raise_for_status.return_value = None

        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        security = SecurityManager(config)
        headers = await security.get_auth_headers()

        assert headers["Authorization"] == "Bearer oidc-token-123"

    def test_mtls_auth_headers(self):
        """Testet mTLS-Authentifizierung."""
        config = SecurityConfig(
            auth_type=AuthType.MTLS,
            mtls_cert_path="/path/to/cert.pem",
            mtls_key_path="/path/to/key.pem",
        )
        security = SecurityManager(config)

        headers = asyncio.run(security.get_auth_headers())

        # mTLS wird auf Transport-Ebene gehandhabt, keine Auth-Headers
        assert headers == {}


class TestProtocolClients:
    """Tests für Protokoll-Clients."""

    @patch("httpx.AsyncClient")
    async def test_rpc_client_plan(self, mock_client):
        """Testet KEI-RPC Plan-Operation."""
        # Mock Security Manager
        security = MagicMock()
        security.get_auth_headers.return_value = {"Authorization": "Bearer test-token"}

        # Mock HTTP-Response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "plan_id": "plan-123",
            "steps": ["step1", "step2"],
        }
        mock_response.raise_for_status.return_value = None

        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        # Test RPC Client
        rpc_client = KEIRPCClient("https://test.com", security)

        async with rpc_client:
            result = await rpc_client.plan("Test objective", {"key": "value"})

        assert result["plan_id"] == "plan-123"
        assert len(result["steps"]) == 2

    @patch("websockets.connect")
    async def test_stream_client_subscribe(self, mock_connect):
        """Testet KEI-Stream Subscribe-Operation."""
        # Mock WebSocket
        mock_websocket = AsyncMock()
        mock_connect.return_value = mock_websocket

        # Mock Security Manager
        security = MagicMock()
        security.get_auth_headers.return_value = {"Authorization": "Bearer test-token"}

        stream_client = KEIStreamClient("https://test.com", security)

        # Test Subscribe (ohne tatsächliche WebSocket-Nachrichten)
        await stream_client.connect()

        assert stream_client._connected is True
        mock_connect.assert_called_once()

    @patch("httpx.AsyncClient")
    async def test_bus_client_publish(self, mock_client):
        """Testet KEI-Bus Publish-Operation."""
        # Mock Security Manager
        security = MagicMock()
        security.get_auth_headers.return_value = {"Authorization": "Bearer test-token"}

        # Mock HTTP-Response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "message_id": "msg-123",
            "status": "published",
        }
        mock_response.raise_for_status.return_value = None

        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        bus_client = KEIBusClient("https://test.com", security)

        async with bus_client:
            result = await bus_client.publish({"type": "test", "payload": "data"})

        assert result["message_id"] == "msg-123"
        assert result["status"] == "published"

    @patch("httpx.AsyncClient")
    async def test_mcp_client_discover_tools(self, mock_client):
        """Testet KEI-MCP Tool-Discovery."""
        # Mock Security Manager
        security = MagicMock()
        security.get_auth_headers.return_value = {"Authorization": "Bearer test-token"}

        # Mock HTTP-Response
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"name": "tool1", "description": "Test Tool 1"},
            {"name": "tool2", "description": "Test Tool 2"},
        ]
        mock_response.raise_for_status.return_value = None

        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        mcp_client = KEIMCPClient("https://test.com", security)

        async with mcp_client:
            tools = await mcp_client.discover_tools("test-category")

        assert len(tools) == 2
        assert tools[0]["name"] == "tool1"
        assert tools[1]["name"] == "tool2"


class TestUnifiedKeiAgentClient:
    """Tests für UnifiedKeiAgentClient."""

    @pytest.fixture
    def client(self, mock_config, mock_protocol_config, mock_security_config):
        """Erstellt Test-Client."""
        return UnifiedKeiAgentClient(
            config=mock_config,
            protocol_config=mock_protocol_config,
            security_config=mock_security_config,
        )

    async def test_client_initialization(self, client):
        """Testet Client-Initialisierung."""
        with patch.object(client.security, "start_token_refresh"):
            await client.initialize()

        assert client._initialized is True
        assert client._rpc_client is not None
        assert client._stream_client is not None
        assert client._bus_client is not None
        assert client._mcp_client is not None

    async def test_client_close(self, client):
        """Testet Client-Schließung."""
        # Initialisiere Client
        with patch.object(client.security, "start_token_refresh"):
            await client.initialize()

        # Mock Stream-Client disconnect
        client._stream_client.disconnect = AsyncMock()
        client.security.stop_token_refresh = AsyncMock()

        await client.close()

        assert client._closed is True
        client._stream_client.disconnect.assert_called_once()
        client.security.stop_token_refresh.assert_called_once()

    def test_protocol_selection_streaming(self, client):
        """Testet automatische Protokoll-Auswahl für Streaming-Operationen."""
        protocol = client._select_optimal_protocol("stream_response")
        assert protocol == ProtocolType.STREAM

    def test_protocol_selection_async(self, client):
        """Testet automatische Protokoll-Auswahl für asynchrone Operationen."""
        protocol = client._select_optimal_protocol("background_task")
        assert protocol == ProtocolType.BUS

    def test_protocol_selection_mcp(self, client):
        """Testet automatische Protokoll-Auswahl für MCP-Operationen."""
        protocol = client._select_optimal_protocol("tool_discovery")
        assert protocol == ProtocolType.MCP

    def test_protocol_selection_default(self, client):
        """Testet automatische Protokoll-Auswahl für Standard-Operationen."""
        protocol = client._select_optimal_protocol("unknown_operation")
        assert protocol == ProtocolType.RPC

    async def test_execute_agent_operation_with_tracing(self, client):
        """Testet Agent-Operation mit Tracing."""
        # Mock Tracing Manager
        client.tracing = MagicMock()
        client.tracing.start_span.return_value.__enter__ = MagicMock()
        client.tracing.start_span.return_value.__exit__ = MagicMock()

        # Mock RPC-Ausführung
        with patch.object(client, "_execute_with_protocol") as mock_execute:
            mock_execute.return_value = {"result": "success"}

            await client.initialize()
            result = await client.execute_agent_operation(
                "test_operation", {"test": "data"}, ProtocolType.RPC
            )

        assert result["result"] == "success"
        client.tracing.start_span.assert_called_once()

    async def test_plan_task_high_level_api(self, client):
        """Testet High-Level Plan-Task API."""
        with patch.object(client, "execute_agent_operation") as mock_execute:
            mock_execute.return_value = {"plan_id": "plan-123"}

            result = await client.plan_task("Test objective", {"context": "data"})

        assert result["plan_id"] == "plan-123"
        mock_execute.assert_called_once_with(
            "plan", {"objective": "Test objective", "context": {"context": "data"}}
        )

    async def test_send_agent_message(self, client):
        """Testet Agent-to-Agent Nachrichtenversand."""
        with patch.object(client, "execute_agent_operation") as mock_execute:
            mock_execute.return_value = {"message_id": "msg-123"}

            result = await client.send_agent_message(
                "target-agent", "test_message", {"data": "test"}
            )

        assert result["message_id"] == "msg-123"
        # Prüfe dass Bus-Protokoll verwendet wird
        call_args = mock_execute.call_args
        assert call_args[1]["protocol"] == ProtocolType.BUS

    async def test_discover_available_tools(self, client):
        """Testet MCP-Tool-Discovery High-Level API."""
        with patch.object(client, "execute_agent_operation") as mock_execute:
            mock_execute.return_value = {"tools": [{"name": "tool1"}]}

            tools = await client.discover_available_tools("test-category")

        assert len(tools) == 1
        assert tools[0]["name"] == "tool1"
        # Prüfe dass MCP-Protokoll verwendet wird
        call_args = mock_execute.call_args
        assert call_args[1]["protocol"] == ProtocolType.MCP

    def test_is_protocol_available(self, client):
        """Testet Protokoll-Verfügbarkeits-Prüfung."""
        # Vor Initialisierung sollten keine Protokolle verfügbar sein
        assert client.is_protocol_available(ProtocolType.RPC) is False

        # Nach Initialisierung sollten Protokolle verfügbar sein
        client._initialized = True
        client._rpc_client = MagicMock()
        assert client.is_protocol_available(ProtocolType.RPC) is True

    def test_get_available_protocols(self, client):
        """Testet Abruf verfügbarer Protokolle."""
        # Mock initialisierte Clients
        client._initialized = True
        client._rpc_client = MagicMock()
        client._stream_client = MagicMock()
        client._bus_client = MagicMock()
        client._mcp_client = MagicMock()

        protocols = client.get_available_protocols()

        expected_protocols = [
            ProtocolType.RPC,
            ProtocolType.STREAM,
            ProtocolType.BUS,
            ProtocolType.MCP,
        ]
        assert all(p in protocols for p in expected_protocols)

    def test_get_client_info(self, client):
        """Testet Client-Informationen."""
        client._initialized = True
        client._closed = False

        info = client.get_client_info()

        assert info["agent_id"] == "test-agent"
        assert info["base_url"] == "https://test.kei-framework.com"
        assert info["initialized"] is True
        assert info["closed"] is False
        assert "available_protocols" in info
        assert "features" in info


class TestErrorHandling:
    """Tests für Fehlerbehandlung."""

    async def test_protocol_error_fallback(
        self, mock_config, mock_protocol_config, mock_security_config
    ):
        """Testet Fallback-Mechanismus bei Protokoll-Fehlern."""
        client = UnifiedKeiAgentClient(
            config=mock_config,
            protocol_config=mock_protocol_config,
            security_config=mock_security_config,
        )

        await client.initialize()

        # Mock Bus-Client um Fehler zu werfen
        client._bus_client = MagicMock()
        client._bus_client.__aenter__ = AsyncMock()
        client._bus_client.__aexit__ = AsyncMock()
        client._bus_client.publish = AsyncMock(side_effect=ProtocolError("Bus error"))

        # Mock RPC-Client für Fallback
        client._rpc_client = MagicMock()
        client._rpc_client.__aenter__ = AsyncMock()
        client._rpc_client.__aexit__ = AsyncMock()
        client._rpc_client._rpc_call = AsyncMock(return_value={"fallback": "success"})

        # Test Fallback
        result = await client._execute_with_protocol(
            ProtocolType.BUS, "test_operation", {"test": "data"}
        )

        assert result["fallback"] == "success"

    async def test_initialization_error(self, mock_config):
        """Testet Fehlerbehandlung bei Initialisierung."""
        client = UnifiedKeiAgentClient(config=mock_config)

        # Mock Security Manager um Fehler zu werfen
        with patch.object(
            client.security, "start_token_refresh", side_effect=Exception("Init error")
        ):
            with pytest.raises(KeiSDKError, match="Initialisierung fehlgeschlagen"):
                await client.initialize()


# Pytest-Konfiguration
@pytest.mark.asyncio
class TestAsyncOperations:
    """Tests für asynchrone Operationen."""

    async def test_concurrent_operations(
        self, mock_config, mock_protocol_config, mock_security_config
    ):
        """Testet gleichzeitige Operationen."""
        client = UnifiedKeiAgentClient(
            config=mock_config,
            protocol_config=mock_protocol_config,
            security_config=mock_security_config,
        )

        await client.initialize()

        # Mock verschiedene Operationen
        with patch.object(client, "execute_agent_operation") as mock_execute:
            mock_execute.return_value = {"result": "success"}

            # Führe mehrere Operationen gleichzeitig aus
            tasks = [
                client.plan_task("Task 1"),
                client.plan_task("Task 2"),
                client.plan_task("Task 3"),
            ]

            results = await asyncio.gather(*tasks)

        assert len(results) == 3
        assert all(r["result"] == "success" for r in results)
        assert mock_execute.call_count == 3


# Konfigurations-Tests
class TestConfiguration:
    """Tests für verschiedene Konfigurationen."""

    def test_default_protocol_config(self):
        """Testet Standard-Protokoll-Konfiguration."""
        config = ProtocolConfig()

        assert config.rpc_enabled is True
        assert config.stream_enabled is True
        assert config.bus_enabled is True
        assert config.mcp_enabled is True
        assert config.auto_protocol_selection is True
        assert config.protocol_fallback_enabled is True

    def test_custom_protocol_config(self):
        """Testet benutzerdefinierte Protokoll-Konfiguration."""
        config = ProtocolConfig(
            rpc_enabled=False,
            stream_enabled=True,
            bus_enabled=False,
            mcp_enabled=True,
            auto_protocol_selection=False,
        )

        assert config.rpc_enabled is False
        assert config.stream_enabled is True
        assert config.bus_enabled is False
        assert config.mcp_enabled is True
        assert config.auto_protocol_selection is False

    def test_security_config_bearer(self):
        """Testet Bearer-Token Security-Konfiguration."""
        config = SecurityConfig(
            auth_type=AuthType.BEARER, api_token="test-token", rbac_enabled=True
        )

        assert config.auth_type == AuthType.BEARER
        assert config.api_token == "test-token"
        assert config.rbac_enabled is True

    def test_security_config_oidc(self):
        """Testet OIDC Security-Konfiguration."""
        config = SecurityConfig(
            auth_type=AuthType.OIDC,
            oidc_issuer="https://auth.test.com",
            oidc_client_id="client-id",
            oidc_client_secret="client-secret",
        )

        assert config.auth_type == AuthType.OIDC
        assert config.oidc_issuer == "https://auth.test.com"
        assert config.oidc_client_id == "client-id"
        assert config.oidc_client_secret == "client-secret"


# Integration Tests (mit echten HTTP-Mocks)
@pytest.mark.integration
class TestIntegration:
    """Integration-Tests mit HTTP-Mocking."""

    @patch("httpx.AsyncClient")
    async def test_full_agent_lifecycle(
        self, mock_client, mock_config, mock_protocol_config, mock_security_config
    ):
        """Testet vollständigen Agent-Lifecycle."""
        # Mock HTTP-Responses für verschiedene Operationen
        mock_responses = {
            "/api/v1/registry/agents": {
                "agent_id": "test-agent",
                "status": "registered",
            },
            "/api/v1/health": {"status": "healthy", "version": "1.0.0"},
            "/api/v1/rpc/invoke": {"plan_id": "plan-123", "steps": ["step1"]},
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

        mock_client_instance = AsyncMock()
        mock_client_instance.post.side_effect = mock_request
        mock_client_instance.get.side_effect = mock_request
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        # Test vollständigen Lifecycle
        client = UnifiedKeiAgentClient(
            config=mock_config,
            protocol_config=mock_protocol_config,
            security_config=mock_security_config,
        )

        try:
            await client.initialize()

            # Agent registrieren
            agent = await client.register_agent("Test Agent", "1.0.0")
            assert agent["agent_id"] == "test-agent"

            # Health-Check
            health = await client.health_check()
            assert health["status"] == "healthy"

            # Plan erstellen
            plan = await client.plan_task("Test objective")
            assert plan["plan_id"] == "plan-123"

            # Tools entdecken
            tools = await client.discover_available_tools()
            assert len(tools) == 1
            assert tools[0]["name"] == "tool1"

        finally:
            await client.close()


if __name__ == "__main__":
    # Führe Tests aus
    pytest.main([__file__, "-v", "--tb=short"])
