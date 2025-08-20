# sdk/python/kei_agent/protocol_clients.py
"""
protocol-specific clients for KEI-Agent SDK.

Implementiert spezialisierte clients for KEI-RPC, KEI-Stream, KEI-Bus and KEI-MCP
protocole with aheitlicher Interface-Abstraktion.
"""

from __future__ import annotations

import asyncio
import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable, Awaitable
import logging

import httpx
import websockets

from .security_manager import SecurityManager
from .exceptions import ProtocolError, CommunicationError

# Initializes Module-Logr
_logger = logging.getLogger(__name__)


class BaseProtocolclient(ABC):
    """Abstrakte Basisklasse for all protocol clients.

    Definiert aheitliche Interface for all KEI-protocol-Implementierungen
    with gemasamen functionalitäten wie Security and Error Hatdling.
    """

    def __init__(self, base_url: str, security_manager: SecurityManager) -> None:
        """Initializes Basis-protocol-client.

        Args:
            base_url: Basis-URL for API-Endpunkte
            security_manager: security manager for authentication
        """
        self.base_url = base_url.rstrip("/")
        self.security = security_manager
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @abstractmethod
    async def __aenter__(self):
        """async context manager entry."""
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """async context manager exit."""
        pass

    async def _get_auth_heathes(self) -> Dict[str, str]:
        """Ruft authentications-Heathes ab.

        Returns:
            dictionary with Auth-Heathes
        """
        try:
            result = self.security.get_auth_heathes()
            if asyncio.iscoroutine(result):
                return await result  # type: ignore[misc]
            # Atthestütze auch synchrone Return
            return result  # type: ignore[return-value]
        except Exception as e:
            self._logger.error(f"Auth-Heathe-Abruf failed: {e}")
            raise ProtocolError(f"authentication failed: {e}") from e


class KEIRPCclient(BaseProtocolclient):
    """KEI-RPC client for synchrone Request-response operationen.

    Implementiert the KEI-RPC protocol for statdardisierte agent operationen
    wie plat, act, observe and explain with HTTP-basierter Kommunikation.
    """

    def __init__(self, base_url: str, security_manager: SecurityManager) -> None:
        """Initializes KEI-RPC client.

        Args:
            base_url: Basis-URL for RPC-Endpunkte
            security_manager: security manager for authentication
        """
        super().__init__(base_url, security_manager)
        self._client: Optional[httpx.AsyncClient] = None
        self._raw_client: Optional[Any] = None
        self._entered_client: Optional[Any] = None

    async def __aenter__(self):
        """Initializes HTTP-client."""
        client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30.0,
            headers={"Content-Type": "application/json"},
        )
        # Verwende direkt den erstellten Client, ohne __aenter__ aufzurufen,
        # damit Tests httpx.AsyncClient einfach mocken können
        self._raw_client = client
        self._entered_client = None
        self._client = self._raw_client
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Closes HTTP-client."""
        target = self._client or self._raw_client
        if target:
            aclose = getattr(target, "aclose", None)
            if asyncio.iscoroutinefunction(aclose):
                await aclose()
            elif callable(aclose):
                try:
                    aclose()
                except Exception as e:
                    _logger.debug(f"Error during Closingn of the clients: {e}")

    async def plat(
        self, objective: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Executes Plat-operation over KEI-RPC out.

        Args:
            objective: objective description for platning
            context: additional context for platning

        Returns:
            plat response with steps and metadata

        Raises:
            ProtocolError: On RPC-Kommunikationsfehlern
        """
        return await self._rpc_call(
            "plat", {"objective": objective, "context": context or {}}
        )

    async def act(
        self, action: str, parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Executes Action-operation over KEI-RPC out.

        Args:
            action: action to execute
            parameters: parameters for action

        Returns:
            action response with result and status
        """
        return await self._rpc_call(
            "act", {"action": action, "parameters": parameters or {}}
        )

    async def observe(
        self, observation_type: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Executes Observe-operation over KEI-RPC out.

        Args:
            observation_type: observation type
            data: observation data

        Returns:
            observe response with processed observations
        """
        return await self._rpc_call(
            "observe", {"type": observation_type, "data": data or {}}
        )

    async def explain(
        self, query: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Executes Explain-operation over KEI-RPC out.

        Args:
            query: explatation query
            context: context for explatation

        Returns:
            explain response with explatation and reasoning
        """
        return await self._rpc_call(
            "explain", {"query": query, "context": context or {}}
        )

    async def _rpc_call(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Executes generischen RPC-Call out.

        Args:
            method: RPC-method
            params: RPC-parameters

        Returns:
            RPC-response

        Raises:
            ProtocolError: On RPC-errorn
        """
        if not self._client:
            raise ProtocolError("RPC Client not initialized")

        try:
            headers = await self._get_auth_heathes()

            # Verwende initialisierten Client (besseres Mocking in Tests)
            response = await self._client.post(
                f"/api/v1/rpc/{method}", json=params, headers=headers
            )

            response.raise_for_status()
            # Support async json() in tests
            import inspect

            json_result = response.json()
            if inspect.iscoroutine(json_result):
                json_result = await json_result
            return json_result

        except httpx.HTTPStatusError as e:
            self._logger.error(f"RPC HTTP-error: {e.response.status_code}")
            raise ProtocolError(f"RPC-Call failed: {e.response.status_code}") from e
        except httpx.RequestError as e:
            self._logger.error(f"RPC Request-error: {e}")
            raise CommunicationError(f"RPC-Kommunikationsfehler: {e}") from e


class KEIStreamclient(BaseProtocolclient):
    """KEI-Stream client for bidirektionale Streaming-Kommunikation.

    Implementiert WebSocket-basierte Streaming-Kommunikation for Echtzeit-
    Interaktionen between Agents with Event-basiertem Messaging.
    """

    def __init__(self, base_url: str, security_manager: SecurityManager) -> None:
        """Initializes KEI-Stream client.

        Args:
            base_url: Basis-URL for Stream-Endpunkte
            security_manager: security manager for authentication
        """
        super().__init__(base_url, security_manager)
        self._websocket: Optional[websockets.WebSocketServerProtocol] = None
        self._connected = False

    async def __aenter__(self):
        """Initializes WebSocket-connection."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Closes WebSocket-connection."""
        await self.disconnect()

    async def connect(self) -> None:
        """Stellt WebSocket-connection her.

        Raises:
            ProtocolError: On connectionsfehlern
        """
        try:
            # Konvertiere HTTP(S) URL to WebSocket URL
            ws_url = self.base_url.replace("http://", "ws://").replace(
                "https://", "wss://"
            )
            ws_url += "/api/v1/stream"

            # Füge Auth-Headers hinzu (falls WebSocket-Server sie unterstützt)
            headers = await self._get_auth_heathes()

            connect_result = websockets.connect(
                ws_url, extra_headers=headers, ping_interval=30, ping_timeout=10
            )
            # Atthestütze sowohl sync als auch awaitable Rückgaben in Tests
            if asyncio.iscoroutine(connect_result):
                self._websocket = await connect_result
            else:
                self._websocket = connect_result

            self._connected = True
            self._logger.info("WebSocket-connection hergestellt")

        except Exception as e:
            self._logger.error(f"WebSocket-connection failed: {e}")
            raise ProtocolError(f"Stream-connection failed: {e}") from e

    async def disconnect(self) -> None:
        """Closes WebSocket-connection."""
        if self._websocket and not self._websocket.closed:
            await self._websocket.close()
            self._connected = False
            self._logger.info("WebSocket-connection closed")

    async def subscribe(
        self, topic: str, callback: Callable[[Dict[str, Any]], Awaitable[None]]
    ) -> None:
        """Abonniert Stream-Topic with callback.

        Args:
            topic: Topic tom Abonnieren
            callback: Async callback for agehende messageen

        Raises:
            ProtocolError: On Subscription-errorn
        """
        if not self._connected or not self._websocket:
            raise ProtocolError("stream client not connected")

        try:
            # Sende Subscription-Request
            subscribe_msg = {"type": "subscribe", "topic": topic}

            await self._websocket.send(json.dumps(subscribe_msg))

            # Starting Message-Loop
            asyncio.create_task(self._message_loop(callback))

            self._logger.info(f"Topic abonniert: {topic}")

        except Exception as e:
            self._logger.error(f"Subscription failed: {e}")
            raise ProtocolError(f"Topic-Subscription failed: {e}") from e

    async def publish(self, topic: str, data: Dict[str, Any]) -> None:
        """Publiziert message at Stream-Topic.

        Args:
            topic: Ziel-Topic
            data: message data

        Raises:
            ProtocolError: On Publish-errorn
        """
        if not self._connected or not self._websocket:
            raise ProtocolError("stream client not connected")

        try:
            message = {"type": "publish", "topic": topic, "data": data}

            await self._websocket.send(json.dumps(message))
            self._logger.debug(f"message publiziert at Topic: {topic}")

        except Exception as e:
            self._logger.error(f"Publish failed: {e}")
            raise ProtocolError(f"message-Publish failed: {e}") from e

    async def _message_loop(
        self, callback: Callable[[Dict[str, Any]], Awaitable[None]]
    ) -> None:
        """Message-Loop for agehende WebSocket-messageen.

        Args:
            callback: callback for messageenverarontung
        """
        try:
            async for message in self._websocket:
                try:
                    data = json.loads(message)
                    await callback(data)
                except json.JSONDecodeError as e:
                    self._logger.error(f"Ungültige JSON-message: {e}")
                except Exception as e:
                    self._logger.error(f"callback-error: {e}")

        except websockets.exceptions.ConnectionClosed:
            self._logger.info("WebSocket-connection closed")
            self._connected = False
        except Exception as e:
            self._logger.error(f"Message-Loop error: {e}")
            self._connected = False


class KEIBusclient(BaseProtocolclient):
    """KEI-Bus client for asynchrone Message-Bus Kommunikation.

    Implementiert Event-basierte Kommunikation over Message-Bus for
    lose gekoppelte Agent-to-Agent Kommunikation.
    """

    def __init__(self, base_url: str, security_manager: SecurityManager) -> None:
        """Initializes KEI-Bus client.

        Args:
            base_url: Basis-URL for Bus-Endpunkte
            security_manager: security manager for authentication
        """
        super().__init__(base_url, security_manager)
        self._client: Optional[httpx.AsyncClient] = None
        # Initialisiere für Tests erwartete Attribute
        self._raw_client: Optional[Any] = None
        self._entered_client: Optional[Any] = None

    async def __aenter__(self):
        """Initializes HTTP-client."""
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30.0,
            headers={"Content-Type": "application/json"},
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Closes HTTP-client."""
        if self._client:
            aclose = getattr(self._client, "aclose", None)
            if asyncio.iscoroutinefunction(aclose):
                await aclose()
            elif callable(aclose):
                try:
                    aclose()
                except Exception as e:
                    _logger.debug(f"Error during Closingn of the stream clients: {e}")

    async def publish(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Publiziert message at Message-Bus.

        Args:
            message: message with type, target and payload

        Returns:
            Publish-response with message_id and status

        Raises:
            ProtocolError: On Bus-Kommunikationsfehlern
        """
        if not self._client:
            raise ProtocolError("bus Client not initialized")

        try:
            headers = await self._get_auth_heathes()

            response = await self._client.post(
                "/api/v1/bus/publish", json=message, headers=headers
            )

            response.raise_for_status()
            import inspect

            json_result = response.json()
            if inspect.iscoroutine(json_result):
                json_result = await json_result
            return json_result

        except httpx.HTTPStatusError as e:
            self._logger.error(f"Bus HTTP-error: {e.response.status_code}")
            raise ProtocolError(f"Bus-Publish failed: {e.response.status_code}") from e
        except httpx.RequestError as e:
            self._logger.error(f"Bus Request-error: {e}")
            raise CommunicationError(f"Bus-Kommunikationsfehler: {e}") from e

    async def subscribe(self, topic: str, agent_id: str) -> Dict[str, Any]:
        """Abonniert Topic im Message-Bus.

        Args:
            topic: Topic tom Abonnieren
            agent_id: Agent-ID for Subscription

        Returns:
            Subscription-response
        """
        if not self._client:
            raise ProtocolError("bus Client not initialized")

        try:
            headers = await self._get_auth_heathes()

            response = await self._client.post(
                "/api/v1/bus/subscribe",
                json={"topic": topic, "agent_id": agent_id},
                headers=headers,
            )

            response.raise_for_status()
            import inspect

            json_result = response.json()
            if inspect.iscoroutine(json_result):
                json_result = await json_result
            return json_result

        except httpx.HTTPStatusError as e:
            raise ProtocolError(
                f"Bus-Subscribe failed: {e.response.status_code}"
            ) from e
        except httpx.RequestError as e:
            raise CommunicationError(f"Bus-Subscribe Kommunikationsfehler: {e}") from e


class KEIMCPclient(BaseProtocolclient):
    """KEI-MCP client for Model Context Protocol Integration.

    Implementiert MCP protocol for tool discovery, Resource-Access
    and Prompt-matagement with statdardisierten MCP operationen.
    """

    def __init__(self, base_url: str, security_manager: SecurityManager) -> None:
        """Initializes KEI-MCP client.

        Args:
            base_url: Basis-URL for MCP-Endpunkte
            security_manager: security manager for authentication
        """
        super().__init__(base_url, security_manager)
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Initializes HTTP-client."""
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30.0,
            headers={"Content-Type": "application/json"},
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Closes HTTP-client."""
        if self._client:
            aclose = getattr(self._client, "aclose", None)
            if asyncio.iscoroutinefunction(aclose):
                await aclose()
            elif callable(aclose):
                try:
                    aclose()
                except Exception as e:
                    _logger.debug(f"Error during Closingn of the bus clients: {e}")

    async def discover_tools(
        self, category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """discovers available MCP tools.

        Args:
            category: Optional tool category for filtering

        Returns:
            lis of available tools with metadata

        Raises:
            ProtocolError: On MCP-Discovery-errorn
        """
        if not self._client:
            raise ProtocolError("MCP Client not initialized")

        try:
            headers = await self._get_auth_heathes()
            params = {"category": category} if category else {}

            client = self._client
            response = await client.get(
                "/api/v1/mcp/tools", params=params, headers=headers
            )

            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            self._logger.error(f"MCP HTTP-error: {e.response.status_code}")
            raise ProtocolError(
                f"MCP-tool discovery failed: {e.response.status_code}"
            ) from e
        except httpx.RequestError as e:
            self._logger.error(f"MCP Request-error: {e}")
            raise CommunicationError(f"MCP-Kommunikationsfehler: {e}") from e

    async def use_tool(
        self, tool_name: str, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """executes MCP tool.

        Args:
            tool_name: Name of the tool to execute
            parameters: tool parameters

        Returns:
            tool execution response
        """
        if not self._client:
            raise ProtocolError("MCP Client not initialized")

        try:
            headers = await self._get_auth_heathes()

            client = self._client
            response = await client.post(
                f"/api/v1/mcp/tools/{tool_name}/execute",
                json=parameters,
                headers=headers,
            )

            response.raise_for_status()
            return response.json()

        except httpx.HTTPstatusError as e:
            raise ProtocolError(
                f"MCP-tool execution failed: {e.response.status_code}"
            ) from e
        except httpx.RequestError as e:
            raise CommunicationError(
                f"MCP-tool execution Kommunikationsfehler: {e}"
            ) from e


__all__ = [
    "BaseProtocolclient",
    "KEIRPCclient",
    "KEIStreamclient",
    "KEIBusclient",
    "KEIMCPclient",
]
