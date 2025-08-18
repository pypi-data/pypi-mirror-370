# sdk/python/kei_agent/tests/test_protocol_clients.py
"""
Unit Tests für Protocol Clients.

Testet KEI-RPC, KEI-Stream, KEI-Bus und KEI-MCP Clients
mit umfassenden Mock-Szenarien und Error Handling.
"""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from protocol_clients import (
    BaseProtocolClient,
    KEIRPCClient,
    KEIStreamClient,
    KEIBusClient,
    KEIMCPClient,
)
from security_manager import SecurityManager
from protocol_types import SecurityConfig, AuthType
from exceptions import ProtocolError, CommunicationError

# Markiere alle Tests in dieser Datei als Protokoll-Tests
pytestmark = pytest.mark.protocol


class TestBaseProtocolClient:
    """Tests für BaseProtocolClient abstrakte Klasse."""

    @pytest.fixture
    def security_manager(self):
        """Erstellt Mock Security Manager."""
        config = SecurityConfig(auth_type=AuthType.BEARER, api_token="test-token")
        return SecurityManager(config)

    def test_initialization(self, security_manager):
        """Testet Basis-Client-Initialisierung."""
        # Kann nicht direkt instanziiert werden (abstrakte Klasse)
        # Aber wir können die __init__ Methode testen

        class TestClient(BaseProtocolClient):
            async def __aenter__(self):
                pass

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

        client = TestClient("https://test.com", security_manager)

        assert client.base_url == "https://test.com"
        assert client.security == security_manager

    def test_base_url_normalization(self, security_manager):
        """Testet URL-Normalisierung (entfernt trailing slash)."""

        class TestClient(BaseProtocolClient):
            async def __aenter__(self):
                pass

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

        client = TestClient("https://test.com/", security_manager)
        assert client.base_url == "https://test.com"

    @pytest.mark.asyncio
    async def test_get_auth_headers_success(self, security_manager):
        """Testet erfolgreichen Auth-Header-Abruf."""

        class TestClient(BaseProtocolClient):
            async def __aenter__(self):
                pass

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

        client = TestClient("https://test.com", security_manager)

        headers = await client._get_auth_headers()
        assert headers == {"Authorization": "Bearer test-token"}

    @pytest.mark.asyncio
    async def test_get_auth_headers_error(self, security_manager):
        """Testet Auth-Header-Abruf mit Fehler."""

        class TestClient(BaseProtocolClient):
            async def __aenter__(self):
                pass

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

        client = TestClient("https://test.com", security_manager)

        # Mock Security Manager um Fehler zu werfen
        with patch.object(
            security_manager, "get_auth_headers", side_effect=Exception("Auth error")
        ):
            with pytest.raises(ProtocolError, match="Authentifizierung fehlgeschlagen"):
                await client._get_auth_headers()


class TestKEIRPCClient:
    """Tests für KEI-RPC Client."""

    @pytest.fixture
    def security_manager(self):
        """Erstellt Security Manager für Tests."""
        config = SecurityConfig(auth_type=AuthType.BEARER, api_token="test-token")
        return SecurityManager(config)

    @pytest.fixture
    def rpc_client(self, security_manager):
        """Erstellt RPC-Client für Tests."""
        return KEIRPCClient("https://test.com", security_manager)

    @pytest.mark.asyncio
    async def test_context_manager(self, rpc_client):
        """Testet Async Context Manager."""
        async with rpc_client as client:
            assert client._client is not None
            assert hasattr(client._client, "post")

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_plan_operation_success(self, mock_client, rpc_client):
        """Testet erfolgreiche Plan-Operation."""
        # Mock HTTP-Response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "plan_id": "plan-123",
            "steps": ["step1", "step2", "step3"],
            "status": "created",
        }
        mock_response.raise_for_status.return_value = None

        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value = mock_client_instance

        async with rpc_client as client:
            result = await client.plan("Create a report", {"format": "pdf"})

        assert result["plan_id"] == "plan-123"
        assert len(result["steps"]) == 3
        assert result["status"] == "created"

        # Prüfe HTTP-Call
        mock_client_instance.post.assert_called_once()
        call_args = mock_client_instance.post.call_args
        assert "/api/v1/rpc/plan" in str(call_args)

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_act_operation_success(self, mock_client, rpc_client):
        """Testet erfolgreiche Act-Operation."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "action_id": "action-456",
            "result": "completed",
            "output": {"file_path": "/tmp/report.pdf"},
        }
        mock_response.raise_for_status.return_value = None

        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value = mock_client_instance

        async with rpc_client as client:
            result = await client.act("generate_report", {"template": "standard"})

        assert result["action_id"] == "action-456"
        assert result["result"] == "completed"

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_observe_operation_success(self, mock_client, rpc_client):
        """Testet erfolgreiche Observe-Operation."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "observation_id": "obs-789",
            "type": "environment",
            "data": {"cpu_usage": 45.2, "memory_usage": 67.8},
        }
        mock_response.raise_for_status.return_value = None

        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value = mock_client_instance

        async with rpc_client as client:
            result = await client.observe("system_metrics", {"interval": 60})

        assert result["observation_id"] == "obs-789"
        assert result["type"] == "environment"

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_explain_operation_success(self, mock_client, rpc_client):
        """Testet erfolgreiche Explain-Operation."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "explanation_id": "exp-101",
            "query": "Why did the action fail?",
            "explanation": "The action failed due to insufficient permissions.",
            "reasoning": ["Permission check failed", "User lacks admin role"],
        }
        mock_response.raise_for_status.return_value = None

        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value = mock_client_instance

        async with rpc_client as client:
            result = await client.explain(
                "Why did the action fail?", {"action_id": "action-456"}
            )

        assert result["explanation_id"] == "exp-101"
        assert "insufficient permissions" in result["explanation"]

    @pytest.mark.asyncio
    async def test_rpc_call_not_initialized(self, rpc_client):
        """Testet RPC-Call ohne Initialisierung."""
        with pytest.raises(ProtocolError, match="RPC-Client nicht initialisiert"):
            await rpc_client._rpc_call("plan", {})

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_rpc_call_http_error(self, mock_client, rpc_client):
        """Testet RPC-Call mit HTTP-Fehler."""
        import httpx

        mock_response = MagicMock()
        mock_response.status_code = 500

        mock_client_instance = AsyncMock()
        mock_client_instance.post.side_effect = httpx.HTTPStatusError(
            "Internal Server Error", request=MagicMock(), response=mock_response
        )
        mock_client.return_value = mock_client_instance

        async with rpc_client as client:
            with pytest.raises(ProtocolError, match="RPC-Call fehlgeschlagen"):
                await client.plan("Test objective")

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_rpc_call_network_error(self, mock_client, rpc_client):
        """Testet RPC-Call mit Netzwerkfehler."""
        import httpx

        mock_client_instance = AsyncMock()
        mock_client_instance.post.side_effect = httpx.RequestError("Network error")
        mock_client.return_value = mock_client_instance

        async with rpc_client as client:
            with pytest.raises(CommunicationError, match="RPC-Kommunikationsfehler"):
                await client.plan("Test objective")


class TestKEIStreamClient:
    """Tests für KEI-Stream Client."""

    @pytest.fixture
    def security_manager(self):
        """Erstellt Security Manager für Tests."""
        config = SecurityConfig(auth_type=AuthType.BEARER, api_token="test-token")
        return SecurityManager(config)

    @pytest.fixture
    def stream_client(self, security_manager):
        """Erstellt Stream-Client für Tests."""
        return KEIStreamClient("https://test.com", security_manager)

    @pytest.mark.asyncio
    async def test_context_manager(self, stream_client):
        """Testet Async Context Manager."""
        with patch.object(stream_client, "connect") as mock_connect:
            with patch.object(stream_client, "disconnect") as mock_disconnect:
                async with stream_client:
                    pass

                mock_connect.assert_called_once()
                mock_disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_success(self, stream_client):
        """Testet erfolgreiche WebSocket-Verbindung."""
        mock_websocket = AsyncMock()

        # Mock websockets.connect direkt
        with patch(
            "protocol_clients.websockets.connect", new_callable=AsyncMock
        ) as mock_connect:
            mock_connect.return_value = mock_websocket

            await stream_client.connect()

            assert stream_client._connected is True
            assert stream_client._websocket == mock_websocket
            mock_connect.assert_called_once()

    @pytest.mark.asyncio
    @patch("websockets.connect")
    async def test_connect_error(self, mock_connect, stream_client):
        """Testet WebSocket-Verbindungsfehler."""
        mock_connect.side_effect = Exception("Connection failed")

        with pytest.raises(ProtocolError, match="Stream-Verbindung fehlgeschlagen"):
            await stream_client.connect()

    @pytest.mark.asyncio
    async def test_disconnect(self, stream_client):
        """Testet WebSocket-Trennung."""
        # Simuliere aktive Verbindung
        mock_websocket = AsyncMock()
        mock_websocket.closed = False
        stream_client._websocket = mock_websocket
        stream_client._connected = True

        await stream_client.disconnect()

        assert stream_client._connected is False
        mock_websocket.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_subscribe_not_connected(self, stream_client):
        """Testet Subscribe ohne Verbindung."""
        callback = AsyncMock()

        with pytest.raises(ProtocolError, match="Stream-Client nicht verbunden"):
            await stream_client.subscribe("test_topic", callback)

    @pytest.mark.asyncio
    async def test_publish_not_connected(self, stream_client):
        """Testet Publish ohne Verbindung."""
        with pytest.raises(ProtocolError, match="Stream-Client nicht verbunden"):
            await stream_client.publish("test_topic", {"data": "test"})

    @pytest.mark.asyncio
    async def test_publish_success(self, stream_client):
        """Testet erfolgreiches Publish."""
        # Simuliere aktive Verbindung
        mock_websocket = AsyncMock()
        stream_client._websocket = mock_websocket
        stream_client._connected = True

        await stream_client.publish("test_topic", {"message": "hello"})

        # Prüfe dass Nachricht gesendet wurde
        mock_websocket.send.assert_called_once()
        sent_data = json.loads(mock_websocket.send.call_args[0][0])
        assert sent_data["type"] == "publish"
        assert sent_data["topic"] == "test_topic"
        assert sent_data["data"]["message"] == "hello"


class TestKEIBusClient:
    """Tests für KEI-Bus Client."""

    @pytest.fixture
    def security_manager(self):
        """Erstellt Security Manager für Tests."""
        config = SecurityConfig(auth_type=AuthType.BEARER, api_token="test-token")
        return SecurityManager(config)

    @pytest.fixture
    def bus_client(self, security_manager):
        """Erstellt Bus-Client für Tests."""
        return KEIBusClient("https://test.com", security_manager)

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_publish_success(self, mock_client, bus_client):
        """Testet erfolgreiches Message-Publish."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "message_id": "msg-123",
            "status": "published",
            "timestamp": "2024-01-01T12:00:00Z",
        }
        mock_response.raise_for_status.return_value = None

        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value = mock_client_instance

        message = {
            "type": "agent_message",
            "target": "agent-456",
            "payload": {"action": "process_data"},
        }

        async with bus_client as client:
            result = await client.publish(message)

        assert result["message_id"] == "msg-123"
        assert result["status"] == "published"

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_subscribe_success(self, mock_client, bus_client):
        """Testet erfolgreiches Topic-Subscribe."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "subscription_id": "sub-789",
            "topic": "agent_events",
            "status": "subscribed",
        }
        mock_response.raise_for_status.return_value = None

        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value = mock_client_instance

        async with bus_client as client:
            result = await client.subscribe("agent_events", "agent-123")

        assert result["subscription_id"] == "sub-789"
        assert result["topic"] == "agent_events"


class TestKEIMCPClient:
    """Tests für KEI-MCP Client."""

    @pytest.fixture
    def security_manager(self):
        """Erstellt Security Manager für Tests."""
        config = SecurityConfig(auth_type=AuthType.BEARER, api_token="test-token")
        return SecurityManager(config)

    @pytest.fixture
    def mcp_client(self, security_manager):
        """Erstellt MCP-Client für Tests."""
        return KEIMCPClient("https://test.com", security_manager)

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_discover_tools_success(self, mock_client, mcp_client):
        """Testet erfolgreiche Tool-Discovery."""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "name": "calculator",
                "description": "Mathematical calculator tool",
                "parameters": {"expression": "string"},
            },
            {
                "name": "file_reader",
                "description": "Read file contents",
                "parameters": {"path": "string"},
            },
        ]
        mock_response.raise_for_status.return_value = None

        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value = mock_client_instance

        async with mcp_client as client:
            tools = await client.discover_tools("utilities")

        assert len(tools) == 2
        assert tools[0]["name"] == "calculator"
        assert tools[1]["name"] == "file_reader"

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_use_tool_success(self, mock_client, mcp_client):
        """Testet erfolgreiche Tool-Ausführung."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "tool_execution_id": "exec-456",
            "tool_name": "calculator",
            "result": 42,
            "status": "completed",
        }
        mock_response.raise_for_status.return_value = None

        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value = mock_client_instance

        async with mcp_client as client:
            result = await client.use_tool("calculator", {"expression": "6 * 7"})

        assert result["tool_execution_id"] == "exec-456"
        assert result["result"] == 42
        assert result["status"] == "completed"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
