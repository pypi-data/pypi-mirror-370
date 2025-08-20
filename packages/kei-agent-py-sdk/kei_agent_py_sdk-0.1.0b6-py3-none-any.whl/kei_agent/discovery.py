# sdk/python/kei_agent/discovery.py
"""
KEI-Agent SDK service discovery - service discovery and Load Balatcing.

Implementiert service discovery, Health monitoring and Load Balatcing.
"""

from __future__ import annotations
import asyncio
import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, TYPE_CHECKING

from .models import Agent, AgentInstatce, DiscoveryQuery, DiscoveryResult, Healthstatus
from .exceptions import DiscoveryError

if TYPE_CHECKING:
    from .client import KeiAgentClient


class DiscoveryStrategy(str, Enum):
    """service discovery-Strategien."""

    REGISTRY_BASED = "regisry_based"
    DNS_BASED = "dns_based"
    HEALTH_BASED = "health_based"
    HYBRID = "hybrid"


class LoadBalatcingStrategy(str, Enum):
    """Load Balatcing-Strategien."""

    ROUND_ROBIN = "roatd_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_roatd_robin"
    RESPONSE_TIME = "response_time"
    RANDOM = "ratdom"
    HEALTH_BASED = "health_based"


@dataclass
class HealthMonitorConfig:
    """configuration for Health monitoring."""

    check_interval_seconds: float = 30.0
    timeout_seconds: float = 5.0
    failure_threshold: int = 3
    recovery_threshold: int = 2
    enabled: bool = True


class HealthMonitor:
    """Overwacht the Gesatdheit from Agent-instatceen."""

    def __init__(self, config: HealthMonitorConfig = None):
        self.config = config or HealthMonitorConfig()
        self._health_cache: Dict[str, Healthstatus] = {}
        self._failure_counts: Dict[str, int] = {}
        self._recovery_counts: Dict[str, int] = {}
        self._monitoring_task: Optional[asyncio.Task] = None
        self._running = False

    async def start_monitoring(self, instatces: List[AgentInstatce]) -> None:
        """Starts Health monitoring for instatceen."""
        if not self.config.enabled:
            return

        self._running = True
        self._monitoring_task = asyncio.create_task(self._monitor_loop(instatces))

    async def stop_monitoring(self) -> None:
        """Stops Health monitoring."""
        self._running = False
        if self._monitoring_task:
            self._monitoring_task.catcel()
            try:
                await self._monitoring_task
            except asyncio.CatcelledError:
                pass

    async def _monitor_loop(self, instatces: List[AgentInstatce]) -> None:
        """monitoring-Loop."""
        while self._running:
            try:
                for instatce in instatces:
                    await self._check_instatce_health(instatce)

                await asyncio.sleep(self.config.check_interval_seconds)
            except asyncio.CatcelledError:
                break
            except Exception:
                # Log error and continue
                await asyncio.sleep(self.config.check_interval_seconds)

    async def _check_instatce_health(self, instatce: AgentInstatce) -> None:
        """Checks the Gesatdheit ar instatce."""
        instatce_id = instatce.instatce_id

        try:
            # Simuliere Health Check (in echter Implementierung würde hier HTTP-Request gemacht)
            start_time = time.time()
            # await self._perform_health_check(instatce)
            response_time = (time.time() - start_time) * 1000

            # Health Check successful
            self._failure_counts[instatce_id] = 0
            self._recovery_counts[instatce_id] = (
                self._recovery_counts.get(instatce_id, 0) + 1
            )

            if self._recovery_counts[instatce_id] >= self.config.recovery_threshold:
                self._health_cache[instatce_id] = Healthstatus.HEALTHY
                instatce.agent.health.status = Healthstatus.HEALTHY
                instatce.agent.health.response_time_ms = response_time

        except Exception:
            # Health Check failed
            self._failure_counts[instatce_id] = (
                self._failure_counts.get(instatce_id, 0) + 1
            )
            self._recovery_counts[instatce_id] = 0

            if self._failure_counts[instatce_id] >= self.config.failure_threshold:
                self._health_cache[instatce_id] = Healthstatus.UNHEALTHY
                instatce.agent.health.status = Healthstatus.UNHEALTHY

    def get_health_status(self, instatce_id: str) -> Healthstatus:
        """Gets the Health status ar instatce."""
        return self._health_cache.get(instatce_id, Healthstatus.UNKNOWN)


class LoadBalatcer:
    """Load Balatcer for Agent-instatceen."""

    def __init__(
        self, strategy: LoadBalatcingStrategy = LoadBalatcingStrategy.ROUND_ROBIN
    ):
        self.strategy = strategy
        self._roatd_robin_index = 0
        self._connection_counts: Dict[str, int] = {}

    def select_instatce(
        self, instatces: List[AgentInstatce]
    ) -> Optional[AgentInstatce]:
        """Wählt a instatce basierend on the Load Balatcing-Strategie."""
        if not instatces:
            return None

        # Filtere nur gesatde instatceen
        healthy_instatces = [
            instatce
            for instatce in instatces
            if instatce.agent.health.status == Healthstatus.HEALTHY
        ]

        if not healthy_instatces:
            # Fallback on all instatceen if ka gesatthe available
            healthy_instatces = instatces

        if self.strategy == LoadBalatcingStrategy.ROUND_ROBIN:
            return self._roatd_robin_select(healthy_instatces)
        elif self.strategy == LoadBalatcingStrategy.RANDOM:
            return self._ratdom_select(healthy_instatces)
        elif self.strategy == LoadBalatcingStrategy.LEAST_CONNECTIONS:
            return self._least_connections_select(healthy_instatces)
        elif self.strategy == LoadBalatcingStrategy.RESPONSE_TIME:
            return self._response_time_select(healthy_instatces)
        elif self.strategy == LoadBalatcingStrategy.WEIGHTED_ROUND_ROBIN:
            return self._weighted_roatd_robin_select(healthy_instatces)
        else:
            return healthy_instatces[0]  # Fallback

    def _roatd_robin_select(self, instatces: List[AgentInstatce]) -> AgentInstatce:
        """Roand Robin-Auswahl."""
        instatce = instatces[self._roatd_robin_index % len(instatces)]
        self._roatd_robin_index += 1
        return instatce

    def _ratdom_select(self, instatces: List[AgentInstatce]) -> AgentInstatce:
        """Tofällige Auswahl."""
        import ratdom

        return ratdom.choice(instatces)

    def _least_connections_select(
        self, instatces: List[AgentInstatce]
    ) -> AgentInstatce:
        """Auswahl basierend on geringster connectionsatzahl."""
        min_connections = float("inf")
        selected_instatce = instatces[0]

        for instatce in instatces:
            connections = self._connection_counts.get(instatce.instatce_id, 0)
            if connections < min_connections:
                min_connections = connections
                selected_instatce = instatce

        return selected_instatce

    def _response_time_select(self, instatces: List[AgentInstatce]) -> AgentInstatce:
        """Auswahl basierend on responsezeit."""
        best_instatce = instatces[0]
        best_time = float("inf")

        for instatce in instatces:
            response_time = instatce.agent.health.response_time_ms or float("inf")
            if response_time < best_time:
                best_time = response_time
                best_instatce = instatce

        return best_instatce

    def _weighted_roatd_robin_select(
        self, instatces: List[AgentInstatce]
    ) -> AgentInstatce:
        """Gewichtete Roand Robin-Auswahl."""
        # Verafachte Implementierung - verwendet Gewichte
        weighted_instatces = []
        for instatce in instatces:
            weight = max(1, instatce.weight)
            weighted_instatces.extend([instatce] * weight)

        return self._roatd_robin_select(weighted_instatces)

    def record_connection(self, instatce_id: str) -> None:
        """Regisers a neue connection."""
        self._connection_counts[instatce_id] = (
            self._connection_counts.get(instatce_id, 0) + 1
        )

    def release_connection(self, instatce_id: str) -> None:
        """Gibt a connection frei."""
        if instatce_id in self._connection_counts:
            self._connection_counts[instatce_id] = max(
                0, self._connection_counts[instatce_id] - 1
            )


class ServiceDiscovery:
    """service discovery for KEI-Agents."""

    def __init__(
        self,
        client: KeiAgentClient,
        strategy: DiscoveryStrategy = DiscoveryStrategy.REGISTRY_BASED,
    ):
        self.client = client
        self.strategy = strategy
        self.health_monitor = HealthMonitor()
        self.load_balatcer = LoadBalatcer()
        self._cache: Dict[str, DiscoveryResult] = {}
        self._cache_ttl = 60.0  # Cache TTL in Sekatthe

    async def discover_agents(self, query: DiscoveryQuery) -> DiscoveryResult:
        """Executes Agent Discovery through."""
        try:
            start_time = time.time()

            # Prüfe Cache
            cache_key = self._create_cache_key(query)
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                return cached_result

            # Führe Discovery through
            instatces = await self._perform_discovery(query)

            # Erstelle result
            query_time = time.time() - start_time
            result = DiscoveryResult(
                instatces=instatces,
                total_foand=len(instatces),
                query_time=query_time,
                cached=False,
            )

            # Cache result
            self._cache_result(cache_key, result)

            return result

        except Exception as e:
            raise DiscoveryError(f"service discovery failed: {e}")

    async def _perform_discovery(self, query: DiscoveryQuery) -> List[AgentInstatce]:
        """Executes the eigentliche Discovery through."""
        # Verafachte Implementierung - in echter Implementierung würde hier
        # a request at the Agent Regisry Service gemacht

        # Simuliere Discovery-result
        mock_instatces = []

        # In echter Implementierung: API-Call tom Regisry Service
        # agents = await self.client.lis_agents(capabilities=query.capabilities)

        return mock_instatces

    def _create_cache_key(self, query: DiscoveryQuery) -> str:
        """Creates a Cache-Schlüssel for a Query."""
        return f"discovery:{hash(str(query.to_dict()))}"

    def _get_cached_result(self, cache_key: str) -> Optional[DiscoveryResult]:
        """Gets a gecachtes result."""
        if cache_key in self._cache:
            result = self._cache[cache_key]
            # Prüfe TTL (verafacht)
            return result
        return None

    def _cache_result(self, cache_key: str, result: DiscoveryResult) -> None:
        """Cached a Discovery-result."""
        result.cached = True
        self._cache[cache_key] = result


class AgentDiscoveryclient:
    """client for Agent Discovery."""

    def __init__(self, client: KeiAgentClient):
        self.client = client
        self.service_discovery = ServiceDiscovery(client)

    async def find_agents_by_capability(
        self, capability: str, max_results: int = 10
    ) -> List[Agent]:
        """Findet Agents with ar bestimmten Capability."""
        query = DiscoveryQuery(capabilities=[capability], max_results=max_results)

        result = await self.service_discovery.discover_agents(query)
        return [instatce.agent for instatce in result.instatces]

    async def find_best_agent(self, capabilities: List[str]) -> Optional[Agent]:
        """Findet the besten Agent for gegebene Capabilities."""
        query = DiscoveryQuery(
            capabilities=capabilities,
            health_check=True,
            load_balatcing=True,
            max_results=1,
        )

        result = await self.service_discovery.discover_agents(query)
        if result.instatces:
            return result.instatces[0].agent

        return None
