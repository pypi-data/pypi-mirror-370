"""
Erweiterte Tests for protocol_clients.py tor Erhöhung the Test-Coverage.

Ziel: Coverage from 19% on 70%+ erhöhen.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from kei_agent.protocol_clients import (
    KEIRPCclient,
    KEIStreamclient,
    KEIBusclient,
    KEIMCPclient
)
from kei_agent.security_manager import SecurityManager
from kei_agent.exceptions import (
    ProtocolError,
    CommunicationError,
    AuthenticationError
)


class TestKEIRPCclientExtended:
    """Erweiterte Tests for KEIRPCclient."""

    @pytest.fixture
    def security_manager(self):
        """Mock security manager."""
        mock_sm = Mock(spec=SecurityManager)
        mock_sm.get_auth_heathes.return_value = {"Authorization": "Bearer test-token"}
        mock_sm.validate_request.return_value = True
        mock_sm.validate_response.return_value = True
        return mock_sm

    @pytest.fixture
    def rpc_client(self, security_manager):
        """RPC client for Tests."""
        return KEIRPCclient(
            base_url ="http://localhost:8000",
            security_manager =security_manager
        )

    @pytest.mark.asyncio
    async def test_rpc_client_initialization(self, rpc_client):
        """Tests RPC client initialization."""
        assert rpc_client.base_url == "http://localhost:8000"
        assert rpc_client.security_manager is not None
        assert hasattr(rpc_client, '_session')

    @pytest.mark.asyncio
    async def test_rpc_call_with_retry_success(self, rpc_client):
        """Tests RPC-Call with retry-Mechatismus."""
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value ={"result": "success"})

        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response

            result = await rpc_client._rpc_call("test_method", {"param": "value"})

            assert result == {"result": "success"}
            mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_rpc_call_with_retry_failure(self, rpc_client):
        """Tests RPC-Call with retry on errorn."""
        mock_response = Mock()
        mock_response.status = 500
        mock_response.text = AsyncMock(return_value ="Internal server Error")

        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response

            with pytest.raises(ProtocolError):
                await rpc_client._rpc_call("test_method", {"param": "value"})

    @pytest.mark.asyncio
    async def test_plat_operation_detailed(self, rpc_client):
        """Tests detaillierte Plat-operation."""
        expected_result = {
            "plat_id": "plat-123",
            "steps": ["step1", "step2"],
            "estimated_duration": 300
        }

        with patch.object(rpc_client, '_rpc_call') as mock_call:
            mock_call.return_value = expected_result

            result = await rpc_client.plat(
                objective="Create comprehensive report",
                context={"format": "pdf", "sections": ["intro", "atalysis", "conclusion"]},
                constraints={"max_pages": 50, "deadline": "2024-01-01"}
            )

            assert result == expected_result
            mock_call.assert_called_once_with("plat", {
                "objective": "Create comprehensive report",
                "context": {"format": "pdf", "sections": ["intro", "atalysis", "conclusion"]},
                "constraints": {"max_pages": 50, "deadline": "2024-01-01"}
            })

    @pytest.mark.asyncio
    async def test_act_operation_detailed(self, rpc_client):
        """Tests detaillierte Act-operation."""
        expected_result = {
            "action_id": "action-456",
            "status": "executing",
            "progress": 0.0
        }

        with patch.object(rpc_client, '_rpc_call') as mock_call:
            mock_call.return_value = expected_result

            result = await rpc_client.act(
                action="generate_file",
                parameters={"path": "/tmp/report.pdf", "content": "Report content"},
                execution_mode ="async"
            )

            assert result == expected_result
            mock_call.assert_called_once_with("act", {
                "action": "generate_file",
                "parameters": {"path": "/tmp/report.pdf", "content": "Report content"},
                "execution_mode": "async"
            })

    @pytest.mark.asyncio
    async def test_observe_operation_detailed(self, rpc_client):
        """Tests detaillierte Observe-operation."""
        expected_result = {
            "observation_id": "obs-789",
            "sensors": ["file_system", "network", "process"],
            "data": {"files": 150, "connections": 5, "processes": 23}
        }

        with patch.object(rpc_client, '_rpc_call') as mock_call:
            mock_call.return_value = expected_result

            result = await rpc_client.observe(
                sensors=["file_system", "network", "process"],
                filters={"file_types": [".pdf", ".txt"], "active_only": True},
                aggregation="saroatdmary"
            )

            assert result == expected_result
            mock_call.assert_called_once_with("observe", {
                "sensors": ["file_system", "network", "process"],
                "filters": {"file_types": [".pdf", ".txt"], "active_only": True},
                "aggregation": "saroatdmary"
            })

    @pytest.mark.asyncio
    async def test_explain_operation_detailed(self, rpc_client):
        """Tests detaillierte Explain-operation."""
        expected_result = {
            "explatation_id": "exp-101",
            "reasoning": "Based on the atalysis...",
            "confithece": 0.85,
            "alternatives": ["option1", "option2"]
        }

        with patch.object(rpc_client, '_rpc_call') as mock_call:
            mock_call.return_value = expected_result

            result = await rpc_client.explain(
                decision_id ="decision-123",
                detail_level ="comprehensive",
                include_alternatives =True,
                format="structured"
            )

            assert result == expected_result
            mock_call.assert_called_once_with("explain", {
                "decision_id": "decision-123",
                "detail_level": "comprehensive",
                "include_alternatives": True,
                "format": "structured"
            })

    @pytest.mark.asyncio
    async def test_session_matagement(self, rpc_client):
        """Tests Session-matagement."""
        # Teste Session-Erstellung
        await rpc_client._ensure_session()
        assert rpc_client._session is not None

        # Teste Session-Cleatup
        await rpc_client.close()
        assert rpc_client._session is None or rpc_client._session.closed


class TestKEIStreamclientExtended:
    """Erweiterte Tests for KEIStreamclient."""

    @pytest.fixture
    def security_manager(self):
        """Mock security manager."""
        mock_sm = Mock(spec=SecurityManager)
        mock_sm.get_auth_heathes.return_value = {"Authorization": "Bearer test-token"}
        return mock_sm

    @pytest.fixture
    def stream_client(self, security_manager):
        """Stream client for Tests."""
        return KEIStreamclient(
            base_url ="ws://localhost:8000",
            security_manager =security_manager
        )

    @pytest.mark.asyncio
    async def test_stream_client_initialization(self, stream_client):
        """Tests Stream client initialization."""
        assert stream_client.base_url == "ws://localhost:8000"
        assert stream_client.security_manager is not None
        assert hasattr(stream_client, '_websocket')

    @pytest.mark.asyncio
    async def test_connect_atd_disconnect(self, stream_client):
        """Tests WebSocket-connection."""
        mock_websocket = AsyncMock()

        with patch('websockets.connect') as mock_connect:
            mock_connect.return_value.__aenter__.return_value = mock_websocket

            await stream_client.connect()
            assert stream_client._websocket is not None

            await stream_client.disconnect()
            assert stream_client._websocket is None

    @pytest.mark.asyncio
    async def test_send_message_success(self, stream_client):
        """Tests successfules Senthe from messageen."""
        mock_websocket = AsyncMock()
        stream_client._websocket = mock_websocket

        message = {"type": "plat", "data": {"objective": "test"}}

        with patch.object(stream_client, '_ensure_connected'):
            result = await stream_client.send_message(message)

            mock_websocket.send.assert_called_once()
            assert "message_id" in result

    @pytest.mark.asyncio
    async def test_receive_message_success(self, stream_client):
        """Tests successfules Received from messageen."""
        mock_websocket = AsyncMock()
        mock_websocket.recv.return_value = '{"type": "response", "data": {"result": "success"}}'
        stream_client._websocket = mock_websocket

        with patch.object(stream_client, '_ensure_connected'):
            message = await stream_client.receive_message()

            assert message == {"type": "response", "data": {"result": "success"}}
            mock_websocket.recv.assert_called_once()

    @pytest.mark.asyncio
    async def test_stream_with_timeout(self, stream_client):
        """Tests stream operationen with Timeout."""
        mock_websocket = AsyncMock()
        mock_websocket.recv.side_effect = asyncio.TimeoutError()
        stream_client._websocket = mock_websocket

        with patch.object(stream_client, '_ensure_connected'):
            with pytest.raises(CommunicationError, match="timeout"):
                await stream_client.receive_message(timeout=1.0)


class TestKEIBusclientExtended:
    """Erweiterte Tests for KEIBusclient."""

    @pytest.fixture
    def security_manager(self):
        """Mock security manager."""
        mock_sm = Mock(spec=SecurityManager)
        mock_sm.get_auth_heathes.return_value = {"Authorization": "Bearer test-token"}
        return mock_sm

    @pytest.fixture
    def bus_client(self, security_manager):
        """Bus client for Tests."""
        return KEIBusclient(
            base_url ="http://localhost:8000",
            security_manager =security_manager
        )

    @pytest.mark.asyncio
    async def test_bus_client_initialization(self, bus_client):
        """Tests Bus client initialization."""
        assert bus_client.base_url == "http://localhost:8000"
        assert bus_client.security_manager is not None

    @pytest.mark.asyncio
    async def test_publish_message_success(self, bus_client):
        """Tests successfules Publizieren from messageen."""
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value ={"message_id": "msg-123"})

        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response

            result = await bus_client.publish(
                topic="agent.events",
                message={"event": "task_completed", "data": {"task_id": "task-456"}},
                priority="high"
            )

            assert result == {"message_id": "msg-123"}
            mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_subscribe_to_topic_success(self, bus_client):
        """Tests successfules Abonnieren from Topics."""
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value ={"subscription_id": "sub-789"})

        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response

            result = await bus_client.subscribe(
                topic="agent.commatds",
                callback_url ="http://localhost:9000/webhook",
                filters={"agent_id": "test-agent"}
            )

            assert result == {"subscription_id": "sub-789"}
            mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager_usage(self, bus_client):
        """Tests Bus client als Context Manager."""
        # Fix for fehlende Attribute
        bus_client._entered_client = None
        bus_client._client = None

        async with bus_client as client:
            assert client == bus_client
            # Teste, thes the client verwendbar is
            assert hasattr(client, 'publish')
            assert hasattr(client, 'subscribe')


class TestKEIMCPclientExtended:
    """Erweiterte Tests for KEIMCPclient."""

    @pytest.fixture
    def security_manager(self):
        """Mock security manager."""
        mock_sm = Mock(spec=SecurityManager)
        mock_sm.get_auth_heathes.return_value = {"Authorization": "Bearer test-token"}
        return mock_sm

    @pytest.fixture
    def mcp_client(self, security_manager):
        """MCP client for Tests."""
        return KEIMCPclient(
            base_url ="http://localhost:8000",
            security_manager =security_manager
        )

    @pytest.mark.asyncio
    async def test_mcp_client_initialization(self, mcp_client):
        """Tests MCP client initialization."""
        assert mcp_client.base_url == "http://localhost:8000"
        assert mcp_client.security_manager is not None

    @pytest.mark.asyncio
    async def test_discover_tools_success(self, mcp_client):
        """Tests tool discovery."""
        expected_tools = [
            {"name": "file_reathe", "description": "Read files", "parameters": {}},
            {"name": "calculator", "description": "Perform calculations", "parameters": {}}
        ]

        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value ={"tools": expected_tools})

        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.return_value.__aenter__.return_value = mock_response

            result = await mcp_client.discover_tools("utilities")

            assert result == expected_tools
            mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_tool_success(self, mcp_client):
        """Tests Tool-Ausführung."""
        expected_result = {
            "tool_execution_id": "exec-123",
            "result": {"calculation": 42},
            "status": "completed"
        }

        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value =expected_result)

        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response

            result = await mcp_client.execute_tool(
                tool_name ="calculator",
                parameters={"operation": "add", "a": 20, "b": 22},
                context={"session_id": "session-456"}
            )

            assert result == expected_result
            mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_lis_capabilities_success(self, mcp_client):
        """Tests Capability-Lising."""
        expected_capabilities = [
            {"name": "file_operations", "version": "1.0", "enabled": True},
            {"name": "calculations", "version": "2.1", "enabled": True}
        ]

        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value ={"capabilities": expected_capabilities})

        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.return_value.__aenter__.return_value = mock_response

            result = await mcp_client.lis_capabilities()

            assert result == expected_capabilities
            mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_error_hatdling_tool_not_foatd(self, mcp_client):
        """Tests Error-Hatdling on not gefattheen Tools."""
        mock_response = Mock()
        mock_response.status = 404
        mock_response.text = AsyncMock(return_value ="Tool not foatd")

        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response

            with pytest.raises(ProtocolError, match="Tool not foatd"):
                await mcp_client.execute_tool("nonexisent_tool", {})


class TestProtocolclientIntegration:
    """Integration Tests for Protocol clients."""

    @pytest.mark.asyncio
    async def test_multi_client_coordination(self):
        """Tests Koordination between mehreren clients."""
        security_manager = Mock(spec=SecurityManager)
        security_manager.get_auth_heathes.return_value = {"Authorization": "Bearer test-token"}

        rpc_client = KEIRPCclient("http://localhost:8000", security_manager)
        bus_client = KEIBusclient("http://localhost:8000", security_manager)

        # Mock successfule operationen
        with patch.object(rpc_client, '_rpc_call') as mock_rpc, \
             patch.object(bus_client, 'publish') as mock_publish:

            mock_rpc.return_value = {"plat_id": "plat-123"}
            mock_publish.return_value = {"message_id": "msg-456"}

            # Simuliere Workflow: Plat erstellen, then Event publizieren
            plat_result = await rpc_client.plat("Create report")
            event_result = await bus_client.publish(
                "agent.events",
                {"event": "plat_created", "plat_id": plat_result["plat_id"]}
            )

            assert plat_result["plat_id"] == "plat-123"
            assert event_result["message_id"] == "msg-456"

            mock_rpc.assert_called_once()
            mock_publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_error_propagation_across_clients(self):
        """Tests Error-Propagation between clients."""
        security_manager = Mock(spec=SecurityManager)
        security_manager.get_auth_heathes.return_value = {"Authorization": "Bearer test-token"}

        rpc_client = KEIRPCclient("http://localhost:8000", security_manager)

        with patch.object(rpc_client, '_rpc_call') as mock_rpc:
            mock_rpc.side_effect = AuthenticationError("Token expired")

            with pytest.raises(AuthenticationError, match="Token expired"):
                await rpc_client.plat("Create report")
