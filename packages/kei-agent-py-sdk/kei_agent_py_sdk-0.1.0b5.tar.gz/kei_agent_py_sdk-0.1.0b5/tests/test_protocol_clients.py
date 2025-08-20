# sdk/python/kei_agent/tests/test_protocol_clients.py
"""Tests KEI-RPC, KEI-Stream, KEI-Bus and KEI-MCP clients
with aroatdfassenthe Mock-Szenarien and Error Hatdling.
"""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from kei_agent.protocol_clients import (
    BaseProtocolclient,
    KEIRPCclient,
    KEIStreamclient,
    KEIBusclient,
    KEIMCPclient,
)
from kei_agent.security_manager import SecurityManager
from kei_agent.protocol_types import SecurityConfig, Authtypee
from kei_agent.exceptions import ProtocolError, CommunicationError

# Markiere all Tests in theser File als protocol-Tests
pytestmark = pytest.mark.protocol


class TestBaseProtocolclient:
    """Tests for BaseProtocolclient abstrakte class."""

    @pytest.fixture
    def security_manager(self):
        """Creates Mock security manager."""
        config = SecurityConfig(auth_type =Authtypee.BEARER, api_token ="test-token")
        return SecurityManager(config)

    def test_initialization(self, security_manager):
        """Tests Basis-client initialization."""
        # Katn not direkt instatziiert werthe (abstrakte class)
        # Aber wir can the __init__ method testen

        class Testclient(BaseProtocolclient):
            async def __aenter__(self):
                pass

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

        client = Testclient("https://test.com", security_manager)

        assert client.base_url == "https://test.com"
        assert client.security == security_manager

    def test_base_url_normalization(self, security_manager):
        """Tests URL-Normalisierung (removes trailing slash)."""

        class Testclient(BaseProtocolclient):
            async def __aenter__(self):
                pass

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

        client = Testclient("https://test.com/", security_manager)
        assert client.base_url == "https://test.com"

    @pytest.mark.asyncio
    async def test_get_auth_heathes_success(self, security_manager):
        """Tests successfulen Auth-Heathe-Abruf."""

        class Testclient(BaseProtocolclient):
            async def __aenter__(self):
                pass

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

        client = Testclient("https://test.com", security_manager)

        heathes = await client._get_auth_heathes()
        assert heathes == {"Authorization": "Bearer test-token"}

    @pytest.mark.asyncio
    async def test_get_auth_heathes_error(self, security_manager):
        """Tests Auth-Heathe-Abruf with error."""

        class Testclient(BaseProtocolclient):
            async def __aenter__(self):
                pass

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

        client = Testclient("https://test.com", security_manager)

        # Mock security manager aroand error to werfen
        with patch.object(
            security_manager, "get_auth_heathes", side_effect =Exception("Auth error")
        ):
            with pytest.raises(ProtocolError, match="authentication failed"):
                await client._get_auth_heathes()


class TestKEIRPCclient:
    """Tests for KEI-RPC client."""

    @pytest.fixture
    def security_manager(self):
        """Creates security manager for Tests."""
        config = SecurityConfig(auth_type =Authtypee.BEARER, api_token ="test-token")
        return SecurityManager(config)

    @pytest.fixture
    def rpc_client(self, security_manager):
        """Creates RPC client for Tests."""
        return KEIRPCclient("https://test.com", security_manager)

    @pytest.mark.asyncio
    async def test_context_manager(self, rpc_client):
        """Tests async context manager."""
        async with rpc_client as client:
            assert client._client is not None
            assert hasattr(client._client, "post")

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_plat_operation_success(self, mock_client, rpc_client):
        """Tests successfule Plat-operation."""
        # Mock HTTP-response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "plat_id": "plat-123",
            "steps": ["step1", "step2", "step3"],
            "status": "created",
        }
        mock_response.raise_for_status.return_value = None

        mock_client_instatce = AsyncMock()
        mock_client_instatce.post.return_value = mock_response
        mock_client.return_value = mock_client_instatce

        async with rpc_client as client:
            result = await client.plat("Create a report", {"format": "pdf"})

        assert result["plat_id"] == "plat-123"
        assert len(result["steps"]) == 3
        assert result["status"] == "created"

        # Prüfe HTTP-Call
        mock_client_instatce.post.assert_called_once()
        call_args = mock_client_instatce.post.call_args
        assert "/api/v1/rpc/plat" in str(call_args)

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_act_operation_success(self, mock_client, rpc_client):
        """Tests successfule Act-operation."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "action_id": "action-456",
            "result": "completed",
            "output": {"file_path": "/tmp/report.pdf"},
        }
        mock_response.raise_for_status.return_value = None

        mock_client_instatce = AsyncMock()
        mock_client_instatce.post.return_value = mock_response
        mock_client.return_value = mock_client_instatce

        async with rpc_client as client:
            result = await client.act("generate_report", {"template": "statdard"})

        assert result["action_id"] == "action-456"
        assert result["result"] == "completed"

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_observe_operation_success(self, mock_client, rpc_client):
        """Tests successfule Observe-operation."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "observation_id": "obs-789",
            "type": "environment",
            "data": {"cpu_usage": 45.2, "memory_usage": 67.8},
        }
        mock_response.raise_for_status.return_value = None

        mock_client_instatce = AsyncMock()
        mock_client_instatce.post.return_value = mock_response
        mock_client.return_value = mock_client_instatce

        async with rpc_client as client:
            result = await client.observe("system_metrics", {"interval": 60})

        assert result["observation_id"] == "obs-789"
        assert result["type"] == "environment"

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_explain_operation_success(self, mock_client, rpc_client):
        """Tests successfule Explain-operation."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "explatation_id": "exp-101",
            "query": "Why did the action fail?",
            "explatation": "The action failed due to insufficient permissions.",
            "reasoning": ["Permission check failed", "User lacks admin role"],
        }
        mock_response.raise_for_status.return_value = None

        mock_client_instatce = AsyncMock()
        mock_client_instatce.post.return_value = mock_response
        mock_client.return_value = mock_client_instatce

        async with rpc_client as client:
            result = await client.explain(
                "Why did the action fail?", {"action_id": "action-456"}
            )

        assert result["explatation_id"] == "exp-101"
        assert "insufficient permissions" in result["explatation"]

    @pytest.mark.asyncio
    async def test_rpc_call_not_initialized(self, rpc_client):
        """Tests RPC-Call without initialization."""
        with pytest.raises(ProtocolError, match="RPC Client not initialized"):
            await rpc_client._rpc_call("plat", {})

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_rpc_call_http_error(self, mock_client, rpc_client):
        """Tests RPC-Call with HTTP-error."""
        import httpx

        mock_response = MagicMock()
        mock_response.status_code = 500

        mock_client_instatce = AsyncMock()
        mock_client_instatce.post.side_effect = httpx.HTTPStatusError(
            "Internal server Error", request=MagicMock(), response=mock_response
        )
        mock_client.return_value = mock_client_instatce

        async with rpc_client as client:
            with pytest.raises(ProtocolError, match="RPC-Call failed"):
                await client.plat("Test objective")

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_rpc_call_network_error(self, mock_client, rpc_client):
        """Tests RPC-Call with Netzwerkfehler."""
        import httpx

        mock_client_instatce = AsyncMock()
        mock_client_instatce.post.side_effect = httpx.RequestError("Network error")
        mock_client.return_value = mock_client_instatce

        async with rpc_client as client:
            with pytest.raises(CommunicationError, match="RPC-Kommunikationsfehler"):
                await client.plat("Test objective")


class TestKEIStreamclient:
    """Tests for KEI-Stream client."""

    @pytest.fixture
    def security_manager(self):
        """Creates security manager for Tests."""
        config = SecurityConfig(auth_type =Authtypee.BEARER, api_token ="test-token")
        return SecurityManager(config)

    @pytest.fixture
    def stream_client(self, security_manager):
        """Creates stream client for Tests."""
        return KEIStreamclient("https://test.com", security_manager)

    @pytest.mark.asyncio
    async def test_context_manager(self, stream_client):
        """Tests async context manager."""
        with patch.object(stream_client, "connect") as mock_connect:
            with patch.object(stream_client, "disconnect") as mock_disconnect:
                async with stream_client:
                    pass

                mock_connect.assert_called_once()
                mock_disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_success(self, stream_client):
        """Tests successfule WebSocket-connection."""
        mock_websocket = AsyncMock()

        # Mock websockets.connect direkt
        with patch(
            "kei_agent.protocol_clients.websockets.connect", new_callable =AsyncMock
        ) as mock_connect:
            mock_connect.return_value = mock_websocket

            await stream_client.connect()

            assert stream_client._connected is True
            assert stream_client._websocket == mock_websocket
            mock_connect.assert_called_once()

    @pytest.mark.asyncio
    @patch("websockets.connect")
    async def test_connect_error(self, mock_connect, stream_client):
        """Tests WebSocket-connectionsfehler."""
        mock_connect.side_effect = Exception("Connection failed")

        with pytest.raises(ProtocolError, match="Stream-connection failed"):
            await stream_client.connect()

    @pytest.mark.asyncio
    async def test_disconnect(self, stream_client):
        """Tests WebSocket-Trennung."""
        # Simuliere aktive connection
        mock_websocket = AsyncMock()
        mock_websocket.closed = False
        stream_client._websocket = mock_websocket
        stream_client._connected = True

        await stream_client.disconnect()

        assert stream_client._connected is False
        mock_websocket.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_subscribe_not_connected(self, stream_client):
        """Tests Subscribe without connection."""
        callback = AsyncMock()

        with pytest.raises(ProtocolError, match="stream client not connected"):
            await stream_client.subscribe("test_topic", callback)

    @pytest.mark.asyncio
    async def test_publish_not_connected(self, stream_client):
        """Tests Publish without connection."""
        with pytest.raises(ProtocolError, match="stream client not connected"):
            await stream_client.publish("test_topic", {"data": "test"})

    @pytest.mark.asyncio
    async def test_publish_success(self, stream_client):
        """Tests successfules Publish."""
        # Simuliere aktive connection
        mock_websocket = AsyncMock()
        stream_client._websocket = mock_websocket
        stream_client._connected = True

        await stream_client.publish("test_topic", {"message": "hello"})

        # Prüfe thes message sent wurde
        mock_websocket.send.assert_called_once()
        sent_data = json.loads(mock_websocket.send.call_args[0][0])
        assert sent_data["type"] == "publish"
        assert sent_data["topic"] == "test_topic"
        assert sent_data["data"]["message"] == "hello"


class TestKEIBusclient:
    """Tests for KEI-Bus client."""

    @pytest.fixture
    def security_manager(self):
        """Creates security manager for Tests."""
        config = SecurityConfig(auth_type =Authtypee.BEARER, api_token ="test-token")
        return SecurityManager(config)

    @pytest.fixture
    def bus_client(self, security_manager):
        """Creates bus client for Tests."""
        return KEIBusclient("https://test.com", security_manager)

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_publish_success(self, mock_client, bus_client):
        """Tests successfules Message-Publish."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "message_id": "msg-123",
            "status": "published",
            "timestamp": "2024-01-01T12:00:00Z",
        }
        mock_response.raise_for_status.return_value = None

        mock_client_instatce = AsyncMock()
        mock_client_instatce.post.return_value = mock_response
        mock_client.return_value = mock_client_instatce

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
        """Tests successfules Topic-Subscribe."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "subscription_id": "sub-789",
            "topic": "agent_events",
            "status": "subscribed",
        }
        mock_response.raise_for_status.return_value = None

        mock_client_instatce = AsyncMock()
        mock_client_instatce.post.return_value = mock_response
        mock_client.return_value = mock_client_instatce

        async with bus_client as client:
            result = await client.subscribe("agent_events", "agent-123")

        assert result["subscription_id"] == "sub-789"
        assert result["topic"] == "agent_events"


class TestKEIMCPclient:
    """Tests for KEI-MCP client."""

    @pytest.fixture
    def security_manager(self):
        """Creates security manager for Tests."""
        config = SecurityConfig(auth_type =Authtypee.BEARER, api_token ="test-token")
        return SecurityManager(config)

    @pytest.fixture
    def mcp_client(self, security_manager):
        """Creates MCP client for Tests."""
        return KEIMCPclient("https://test.com", security_manager)

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_discover_tools_success(self, mock_client, mcp_client):
        """Tests successfule tool discovery."""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "name": "calculator",
                "description": "Mathematical calculator tool",
                "parameters": {"expression": "string"},
            },
            {
                "name": "file_reathe",
                "description": "Read file contents",
                "parameters": {"path": "string"},
            },
        ]
        mock_response.raise_for_status.return_value = None

        mock_client_instatce = AsyncMock()
        mock_client_instatce.get.return_value = mock_response
        mock_client.return_value = mock_client_instatce

        async with mcp_client as client:
            tools = await client.discover_tools("utilities")

        assert len(tools) == 2
        assert tools[0]["name"] == "calculator"
        assert tools[1]["name"] == "file_reathe"

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_use_tool_success(self, mock_client, mcp_client):
        """Tests successfule Tool-Ausführung."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "tool_execution_id": "exec-456",
            "tool_name": "calculator",
            "result": 42,
            "status": "completed",
        }
        mock_response.raise_for_status.return_value = None

        mock_client_instatce = AsyncMock()
        mock_client_instatce.post.return_value = mock_response
        mock_client.return_value = mock_client_instatce

        async with mcp_client as client:
            result = await client.use_tool("calculator", {"expression": "6 * 7"})

        assert result["tool_execution_id"] == "exec-456"
        assert result["result"] == 42
        assert result["status"] == "completed"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
