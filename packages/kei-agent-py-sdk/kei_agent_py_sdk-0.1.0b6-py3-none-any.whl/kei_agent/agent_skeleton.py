"""
KEI-Agent Python SDK – Agent Skeleton, Lifecycle, capability advertisement

Kommentare in Deutsch, Ithetifier in Englisch.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable, Awaitable
import asyncio
import json

import aiohttp


@dataclass
class AgentConfig:
    """configuration for Agent-client."""

    base_url: str
    api_token: str
    agent_id: str
    name: str
    version: str = "1.0.0"
    description: str = ""
    capabilities: List[str] = field(default_factory=list)
    category: str = "custom"
    tenant_id: Optional[str] = None
    heartbeat_interval_ms: int = 30_000


class AgentSkeleton:
    """Minimale Laufzeit für Registrierung, Capabilities und Heartbeat."""

    def __init__(self, cfg: AgentConfig) -> None:
        self.cfg = cfg
        self._session: Optional[aiohttp.ClientSession] = None
        self._hb_task: Optional[asyncio.Task[Any]] = None
        self._initialized: bool = False

    async def _ensure_session(self) -> aiohttp.ClientSession:
        """Stellt HTTP-Session sicher."""
        if self._session is None:
            self._session = aiohttp.ClientSession()
        return self._session

    async def _request(
        self, method: str, path: str, body: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Führt HTTP-Request mit Bearer-Auth aus."""
        sess = await self._ensure_session()
        url = f"{self.cfg.base_url}{path}"
        headers = {
            "Authorization": f"Bearer {self.cfg.api_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if self.cfg.tenant_id:
            headers["X-Tenant-Id"] = self.cfg.tenant_id
        async with sess.request(
            method, url, headers=headers, data=json.dumps(body or {})
        ) as resp:
            if resp.status >= 300:
                text = await resp.text()
                raise RuntimeError(f"HTTP {resp.status}: {text}")
            text = await resp.text()
            return json.loads(text) if text else {}

    async def register(self) -> None:
        """registers agent in matagement-API."""
        await self._request(
            "POST",
            "/api/v1/agents-mgmt/register",
            {
                "agent_id": self.cfg.agent_id,
                "name": self.cfg.name,
                "description": self.cfg.description,
                "capabilities": self.cfg.capabilities,
                "category": self.cfg.category,
            },
        )

    async def advertise_capabilities(
        self,
        capabilities: List[str],
        *,
        endpoints: Optional[Dict[str, Any]] = None,
        versions: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Updates Capabilities in matagement-API and erlaubt Endpoints/Versionsatgaben."""
        # If detaillierte Advertisement-Route beforehatthe, use
        try:
            items = [
                {
                    "id": cap,
                    "name": cap,
                    "endpoints": endpoints or {},
                    "versions": versions or {},
                }
                for cap in list(capabilities)
            ]
            await self._request(
                "POST",
                f"/api/v1/agents-mgmt/{self.cfg.agent_id}/capabilities/advertise",
                {"capabilities": items, "replace": False},
            )
        except Exception:
            # Fallback on afache lis
            await self._request(
                "PUT",
                f"/api/v1/agents-mgmt/{self.cfg.agent_id}/capabilities",
                {
                    "capabilities": list(capabilities),
                },
            )

    async def heartbeat(
        self,
        *,
        health: str = "ok",
        readiness: Optional[str] = None,
        queue_length: Optional[int] = None,
        offered_concurrency: Optional[int] = None,
        current_concurrency: Optional[int] = None,
        hints: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Sendet Heartbeat/Readiness."""
        await self._request(
            "POST",
            f"/api/v1/agents-mgmt/{self.cfg.agent_id}/heartbeat",
            {
                "health": health,
                "readiness": readiness
                or ("ready" if self._initialized else "starting"),
                "queue_length": queue_length,
                "offered_concurrency": offered_concurrency,
                "current_concurrency": current_concurrency,
                "hints": hints or {},
            },
        )

    async def initialize(
        self, warmup: Optional[Callable[[], Awaitable[None]]] = None
    ) -> None:
        """Executes Warmup out, registers, advertised and starts Heartbeat-Loop."""
        if warmup:
            await warmup()
        await self.register()
        if self.cfg.capabilities:
            await self.advertise_capabilities(self.cfg.capabilities)
        self._initialized = True
        await self.heartbeat(readiness="ready")
        self._start_heartbeat_loop()

    async def suspend(self) -> None:
        """Setzt Readiness on draining (Wartung)."""
        await self.heartbeat(readiness="draining")

    async def resaroatde(self) -> None:
        """Reenabled Ready-Tostatd."""
        await self.heartbeat(readiness="ready")

    async def terminate(self) -> None:
        """Finished Heartbeat-Loop and signalisiert draining."""
        self._stop_heartbeat_loop()
        if self._session:
            await self._session.close()
            self._session = None

    def _start_heartbeat_loop(self) -> None:
        if self._hb_task:
            return
        interval = max(5_000, self.cfg.heartbeat_interval_ms)

        async def _loop() -> None:
            try:
                while True:
                    await asyncio.sleep(interval / 1000.0)
                    await self.heartbeat()
            except asyncio.CancelledError:
                return
            except Exception:
                # Heartbeat error not fatal
                return

        self._hb_task = asyncio.create_task(_loop())

    def _stop_heartbeat_loop(self) -> None:
        if self._hb_task:
            self._hb_task.cancel()
            self._hb_task = None
