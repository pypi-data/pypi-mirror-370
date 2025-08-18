# sdk/python/kei_agent/protocol_clients.py
"""
Protokoll-spezifische Clients für KEI-Agent SDK.

Implementiert spezialisierte Clients für KEI-RPC, KEI-Stream, KEI-Bus und KEI-MCP
Protokolle mit einheitlicher Interface-Abstraktion.
"""

from __future__ import annotations

import asyncio
import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable, Awaitable
import logging

import httpx
import websockets

from security_manager import SecurityManager
from exceptions import ProtocolError, CommunicationError

# Initialisiert Modul-Logger
_logger = logging.getLogger(__name__)


class BaseProtocolClient(ABC):
    """Abstrakte Basisklasse für alle Protokoll-Clients.

    Definiert einheitliche Interface für alle KEI-Protokoll-Implementierungen
    mit gemeinsamen Funktionalitäten wie Security und Error Handling.
    """

    def __init__(self, base_url: str, security_manager: SecurityManager) -> None:
        """Initialisiert Basis-Protokoll-Client.

        Args:
            base_url: Basis-URL für API-Endpunkte
            security_manager: Security Manager für Authentifizierung
        """
        self.base_url = base_url.rstrip("/")
        self.security = security_manager
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @abstractmethod
    async def __aenter__(self):
        """Async Context Manager Eingang."""
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async Context Manager Ausgang."""
        pass

    async def _get_auth_headers(self) -> Dict[str, str]:
        """Ruft Authentifizierungs-Headers ab.

        Returns:
            Dictionary mit Auth-Headers
        """
        try:
            return await self.security.get_auth_headers()
        except Exception as e:
            self._logger.error(f"Auth-Header-Abruf fehlgeschlagen: {e}")
            raise ProtocolError(f"Authentifizierung fehlgeschlagen: {e}") from e


class KEIRPCClient(BaseProtocolClient):
    """KEI-RPC Client für synchrone Request-Response Operationen.

    Implementiert das KEI-RPC Protokoll für standardisierte Agent-Operationen
    wie plan, act, observe und explain mit HTTP-basierter Kommunikation.
    """

    def __init__(self, base_url: str, security_manager: SecurityManager) -> None:
        """Initialisiert KEI-RPC Client.

        Args:
            base_url: Basis-URL für RPC-Endpunkte
            security_manager: Security Manager für Authentifizierung
        """
        super().__init__(base_url, security_manager)
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Initialisiert HTTP-Client."""
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30.0,
            headers={"Content-Type": "application/json"},
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Schließt HTTP-Client."""
        if self._client:
            await self._client.aclose()

    async def plan(
        self, objective: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Führt Plan-Operation über KEI-RPC aus.

        Args:
            objective: Ziel-Beschreibung für Planung
            context: Zusätzlicher Kontext für Planung

        Returns:
            Plan-Response mit Schritten und Metadaten

        Raises:
            ProtocolError: Bei RPC-Kommunikationsfehlern
        """
        return await self._rpc_call(
            "plan", {"objective": objective, "context": context or {}}
        )

    async def act(
        self, action: str, parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Führt Action-Operation über KEI-RPC aus.

        Args:
            action: Auszuführende Aktion
            parameters: Parameter für Aktion

        Returns:
            Action-Response mit Ergebnis und Status
        """
        return await self._rpc_call(
            "act", {"action": action, "parameters": parameters or {}}
        )

    async def observe(
        self, observation_type: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Führt Observe-Operation über KEI-RPC aus.

        Args:
            observation_type: Typ der Beobachtung
            data: Beobachtungsdaten

        Returns:
            Observe-Response mit verarbeiteten Beobachtungen
        """
        return await self._rpc_call(
            "observe", {"type": observation_type, "data": data or {}}
        )

    async def explain(
        self, query: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Führt Explain-Operation über KEI-RPC aus.

        Args:
            query: Erklärungsanfrage
            context: Kontext für Erklärung

        Returns:
            Explain-Response mit Erklärung und Reasoning
        """
        return await self._rpc_call(
            "explain", {"query": query, "context": context or {}}
        )

    async def _rpc_call(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Führt generischen RPC-Call aus.

        Args:
            method: RPC-Methode
            params: RPC-Parameter

        Returns:
            RPC-Response

        Raises:
            ProtocolError: Bei RPC-Fehlern
        """
        if not self._client:
            raise ProtocolError("RPC-Client nicht initialisiert")

        try:
            headers = await self._get_auth_headers()

            response = await self._client.post(
                f"/api/v1/rpc/{method}", json=params, headers=headers
            )

            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            self._logger.error(f"RPC HTTP-Fehler: {e.response.status_code}")
            raise ProtocolError(
                f"RPC-Call fehlgeschlagen: {e.response.status_code}"
            ) from e
        except httpx.RequestError as e:
            self._logger.error(f"RPC Request-Fehler: {e}")
            raise CommunicationError(f"RPC-Kommunikationsfehler: {e}") from e


class KEIStreamClient(BaseProtocolClient):
    """KEI-Stream Client für bidirektionale Streaming-Kommunikation.

    Implementiert WebSocket-basierte Streaming-Kommunikation für Echtzeit-
    Interaktionen zwischen Agents mit Event-basiertem Messaging.
    """

    def __init__(self, base_url: str, security_manager: SecurityManager) -> None:
        """Initialisiert KEI-Stream Client.

        Args:
            base_url: Basis-URL für Stream-Endpunkte
            security_manager: Security Manager für Authentifizierung
        """
        super().__init__(base_url, security_manager)
        self._websocket: Optional[websockets.WebSocketServerProtocol] = None
        self._connected = False

    async def __aenter__(self):
        """Initialisiert WebSocket-Verbindung."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Schließt WebSocket-Verbindung."""
        await self.disconnect()

    async def connect(self) -> None:
        """Stellt WebSocket-Verbindung her.

        Raises:
            ProtocolError: Bei Verbindungsfehlern
        """
        try:
            # Konvertiere HTTP(S) URL zu WebSocket URL
            ws_url = self.base_url.replace("http://", "ws://").replace(
                "https://", "wss://"
            )
            ws_url += "/api/v1/stream"

            # Füge Auth-Headers hinzu (falls WebSocket-Server sie unterstützt)
            headers = await self._get_auth_headers()

            self._websocket = await websockets.connect(
                ws_url, extra_headers=headers, ping_interval=30, ping_timeout=10
            )

            self._connected = True
            self._logger.info("WebSocket-Verbindung hergestellt")

        except Exception as e:
            self._logger.error(f"WebSocket-Verbindung fehlgeschlagen: {e}")
            raise ProtocolError(f"Stream-Verbindung fehlgeschlagen: {e}") from e

    async def disconnect(self) -> None:
        """Schließt WebSocket-Verbindung."""
        if self._websocket and not self._websocket.closed:
            await self._websocket.close()
            self._connected = False
            self._logger.info("WebSocket-Verbindung geschlossen")

    async def subscribe(
        self, topic: str, callback: Callable[[Dict[str, Any]], Awaitable[None]]
    ) -> None:
        """Abonniert Stream-Topic mit Callback.

        Args:
            topic: Topic zum Abonnieren
            callback: Async Callback für eingehende Nachrichten

        Raises:
            ProtocolError: Bei Subscription-Fehlern
        """
        if not self._connected or not self._websocket:
            raise ProtocolError("Stream-Client nicht verbunden")

        try:
            # Sende Subscription-Request
            subscribe_msg = {"type": "subscribe", "topic": topic}

            await self._websocket.send(json.dumps(subscribe_msg))

            # Starte Message-Loop
            asyncio.create_task(self._message_loop(callback))

            self._logger.info(f"Topic abonniert: {topic}")

        except Exception as e:
            self._logger.error(f"Subscription fehlgeschlagen: {e}")
            raise ProtocolError(f"Topic-Subscription fehlgeschlagen: {e}") from e

    async def publish(self, topic: str, data: Dict[str, Any]) -> None:
        """Publiziert Nachricht an Stream-Topic.

        Args:
            topic: Ziel-Topic
            data: Nachrichtendaten

        Raises:
            ProtocolError: Bei Publish-Fehlern
        """
        if not self._connected or not self._websocket:
            raise ProtocolError("Stream-Client nicht verbunden")

        try:
            message = {"type": "publish", "topic": topic, "data": data}

            await self._websocket.send(json.dumps(message))
            self._logger.debug(f"Nachricht publiziert an Topic: {topic}")

        except Exception as e:
            self._logger.error(f"Publish fehlgeschlagen: {e}")
            raise ProtocolError(f"Nachricht-Publish fehlgeschlagen: {e}") from e

    async def _message_loop(
        self, callback: Callable[[Dict[str, Any]], Awaitable[None]]
    ) -> None:
        """Message-Loop für eingehende WebSocket-Nachrichten.

        Args:
            callback: Callback für Nachrichtenverarbeitung
        """
        try:
            async for message in self._websocket:
                try:
                    data = json.loads(message)
                    await callback(data)
                except json.JSONDecodeError as e:
                    self._logger.error(f"Ungültige JSON-Nachricht: {e}")
                except Exception as e:
                    self._logger.error(f"Callback-Fehler: {e}")

        except websockets.exceptions.ConnectionClosed:
            self._logger.info("WebSocket-Verbindung geschlossen")
            self._connected = False
        except Exception as e:
            self._logger.error(f"Message-Loop Fehler: {e}")
            self._connected = False


class KEIBusClient(BaseProtocolClient):
    """KEI-Bus Client für asynchrone Message-Bus Kommunikation.

    Implementiert Event-basierte Kommunikation über Message-Bus für
    lose gekoppelte Agent-to-Agent Kommunikation.
    """

    def __init__(self, base_url: str, security_manager: SecurityManager) -> None:
        """Initialisiert KEI-Bus Client.

        Args:
            base_url: Basis-URL für Bus-Endpunkte
            security_manager: Security Manager für Authentifizierung
        """
        super().__init__(base_url, security_manager)
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Initialisiert HTTP-Client."""
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30.0,
            headers={"Content-Type": "application/json"},
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Schließt HTTP-Client."""
        if self._client:
            await self._client.aclose()

    async def publish(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Publiziert Nachricht an Message-Bus.

        Args:
            message: Nachricht mit type, target und payload

        Returns:
            Publish-Response mit message_id und Status

        Raises:
            ProtocolError: Bei Bus-Kommunikationsfehlern
        """
        if not self._client:
            raise ProtocolError("Bus-Client nicht initialisiert")

        try:
            headers = await self._get_auth_headers()

            response = await self._client.post(
                "/api/v1/bus/publish", json=message, headers=headers
            )

            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            self._logger.error(f"Bus HTTP-Fehler: {e.response.status_code}")
            raise ProtocolError(
                f"Bus-Publish fehlgeschlagen: {e.response.status_code}"
            ) from e
        except httpx.RequestError as e:
            self._logger.error(f"Bus Request-Fehler: {e}")
            raise CommunicationError(f"Bus-Kommunikationsfehler: {e}") from e

    async def subscribe(self, topic: str, agent_id: str) -> Dict[str, Any]:
        """Abonniert Topic im Message-Bus.

        Args:
            topic: Topic zum Abonnieren
            agent_id: Agent-ID für Subscription

        Returns:
            Subscription-Response
        """
        if not self._client:
            raise ProtocolError("Bus-Client nicht initialisiert")

        try:
            headers = await self._get_auth_headers()

            response = await self._client.post(
                "/api/v1/bus/subscribe",
                json={"topic": topic, "agent_id": agent_id},
                headers=headers,
            )

            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            raise ProtocolError(
                f"Bus-Subscribe fehlgeschlagen: {e.response.status_code}"
            ) from e
        except httpx.RequestError as e:
            raise CommunicationError(f"Bus-Subscribe Kommunikationsfehler: {e}") from e


class KEIMCPClient(BaseProtocolClient):
    """KEI-MCP Client für Model Context Protocol Integration.

    Implementiert MCP-Protokoll für Tool-Discovery, Resource-Access
    und Prompt-Management mit standardisierten MCP-Operationen.
    """

    def __init__(self, base_url: str, security_manager: SecurityManager) -> None:
        """Initialisiert KEI-MCP Client.

        Args:
            base_url: Basis-URL für MCP-Endpunkte
            security_manager: Security Manager für Authentifizierung
        """
        super().__init__(base_url, security_manager)
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Initialisiert HTTP-Client."""
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30.0,
            headers={"Content-Type": "application/json"},
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Schließt HTTP-Client."""
        if self._client:
            await self._client.aclose()

    async def discover_tools(
        self, category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Entdeckt verfügbare MCP-Tools.

        Args:
            category: Optionale Tool-Kategorie für Filterung

        Returns:
            Liste verfügbarer Tools mit Metadaten

        Raises:
            ProtocolError: Bei MCP-Discovery-Fehlern
        """
        if not self._client:
            raise ProtocolError("MCP-Client nicht initialisiert")

        try:
            headers = await self._get_auth_headers()
            params = {"category": category} if category else {}

            response = await self._client.get(
                "/api/v1/mcp/tools", params=params, headers=headers
            )

            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            self._logger.error(f"MCP HTTP-Fehler: {e.response.status_code}")
            raise ProtocolError(
                f"MCP-Tool-Discovery fehlgeschlagen: {e.response.status_code}"
            ) from e
        except httpx.RequestError as e:
            self._logger.error(f"MCP Request-Fehler: {e}")
            raise CommunicationError(f"MCP-Kommunikationsfehler: {e}") from e

    async def use_tool(
        self, tool_name: str, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Führt MCP-Tool aus.

        Args:
            tool_name: Name des auszuführenden Tools
            parameters: Tool-Parameter

        Returns:
            Tool-Execution-Response
        """
        if not self._client:
            raise ProtocolError("MCP-Client nicht initialisiert")

        try:
            headers = await self._get_auth_headers()

            response = await self._client.post(
                f"/api/v1/mcp/tools/{tool_name}/execute",
                json=parameters,
                headers=headers,
            )

            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            raise ProtocolError(
                f"MCP-Tool-Execution fehlgeschlagen: {e.response.status_code}"
            ) from e
        except httpx.RequestError as e:
            raise CommunicationError(
                f"MCP-Tool-Execution Kommunikationsfehler: {e}"
            ) from e


__all__ = [
    "BaseProtocolClient",
    "KEIRPCClient",
    "KEIStreamClient",
    "KEIBusClient",
    "KEIMCPClient",
]
