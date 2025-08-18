# sdk/python/kei_agent/discovery.py
"""
KEI-Agent SDK Service Discovery - Service Discovery und Load Balancing.

Implementiert Service Discovery, Health Monitoring und Load Balancing.
"""

from __future__ import annotations
import asyncio
import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, TYPE_CHECKING

from models import Agent, AgentInstance, DiscoveryQuery, DiscoveryResult, HealthStatus
from exceptions import DiscoveryError

if TYPE_CHECKING:
    from client import KeiAgentClient


class DiscoveryStrategy(str, Enum):
    """Service Discovery-Strategien."""

    REGISTRY_BASED = "registry_based"
    DNS_BASED = "dns_based"
    HEALTH_BASED = "health_based"
    HYBRID = "hybrid"


class LoadBalancingStrategy(str, Enum):
    """Load Balancing-Strategien."""

    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    RESPONSE_TIME = "response_time"
    RANDOM = "random"
    HEALTH_BASED = "health_based"


@dataclass
class HealthMonitorConfig:
    """Konfiguration für Health Monitoring."""

    check_interval_seconds: float = 30.0
    timeout_seconds: float = 5.0
    failure_threshold: int = 3
    recovery_threshold: int = 2
    enabled: bool = True


class HealthMonitor:
    """Überwacht die Gesundheit von Agent-Instanzen."""

    def __init__(self, config: HealthMonitorConfig = None):
        self.config = config or HealthMonitorConfig()
        self._health_cache: Dict[str, HealthStatus] = {}
        self._failure_counts: Dict[str, int] = {}
        self._recovery_counts: Dict[str, int] = {}
        self._monitoring_task: Optional[asyncio.Task] = None
        self._running = False

    async def start_monitoring(self, instances: List[AgentInstance]) -> None:
        """Startet Health Monitoring für Instanzen."""
        if not self.config.enabled:
            return

        self._running = True
        self._monitoring_task = asyncio.create_task(self._monitor_loop(instances))

    async def stop_monitoring(self) -> None:
        """Stoppt Health Monitoring."""
        self._running = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass

    async def _monitor_loop(self, instances: List[AgentInstance]) -> None:
        """Monitoring-Loop."""
        while self._running:
            try:
                for instance in instances:
                    await self._check_instance_health(instance)

                await asyncio.sleep(self.config.check_interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception:
                # Log error and continue
                await asyncio.sleep(self.config.check_interval_seconds)

    async def _check_instance_health(self, instance: AgentInstance) -> None:
        """Prüft die Gesundheit einer Instanz."""
        instance_id = instance.instance_id

        try:
            # Simuliere Health Check (in echter Implementierung würde hier HTTP-Request gemacht)
            start_time = time.time()
            # await self._perform_health_check(instance)
            response_time = (time.time() - start_time) * 1000

            # Health Check erfolgreich
            self._failure_counts[instance_id] = 0
            self._recovery_counts[instance_id] = (
                self._recovery_counts.get(instance_id, 0) + 1
            )

            if self._recovery_counts[instance_id] >= self.config.recovery_threshold:
                self._health_cache[instance_id] = HealthStatus.HEALTHY
                instance.agent.health.status = HealthStatus.HEALTHY
                instance.agent.health.response_time_ms = response_time

        except Exception:
            # Health Check fehlgeschlagen
            self._failure_counts[instance_id] = (
                self._failure_counts.get(instance_id, 0) + 1
            )
            self._recovery_counts[instance_id] = 0

            if self._failure_counts[instance_id] >= self.config.failure_threshold:
                self._health_cache[instance_id] = HealthStatus.UNHEALTHY
                instance.agent.health.status = HealthStatus.UNHEALTHY

    def get_health_status(self, instance_id: str) -> HealthStatus:
        """Holt den Health Status einer Instanz."""
        return self._health_cache.get(instance_id, HealthStatus.UNKNOWN)


class LoadBalancer:
    """Load Balancer für Agent-Instanzen."""

    def __init__(
        self, strategy: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN
    ):
        self.strategy = strategy
        self._round_robin_index = 0
        self._connection_counts: Dict[str, int] = {}

    def select_instance(
        self, instances: List[AgentInstance]
    ) -> Optional[AgentInstance]:
        """Wählt eine Instanz basierend auf der Load Balancing-Strategie."""
        if not instances:
            return None

        # Filtere nur gesunde Instanzen
        healthy_instances = [
            instance
            for instance in instances
            if instance.agent.health.status == HealthStatus.HEALTHY
        ]

        if not healthy_instances:
            # Fallback auf alle Instanzen wenn keine gesunden verfügbar
            healthy_instances = instances

        if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return self._round_robin_select(healthy_instances)
        elif self.strategy == LoadBalancingStrategy.RANDOM:
            return self._random_select(healthy_instances)
        elif self.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            return self._least_connections_select(healthy_instances)
        elif self.strategy == LoadBalancingStrategy.RESPONSE_TIME:
            return self._response_time_select(healthy_instances)
        elif self.strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin_select(healthy_instances)
        else:
            return healthy_instances[0]  # Fallback

    def _round_robin_select(self, instances: List[AgentInstance]) -> AgentInstance:
        """Round Robin-Auswahl."""
        instance = instances[self._round_robin_index % len(instances)]
        self._round_robin_index += 1
        return instance

    def _random_select(self, instances: List[AgentInstance]) -> AgentInstance:
        """Zufällige Auswahl."""
        import random

        return random.choice(instances)

    def _least_connections_select(
        self, instances: List[AgentInstance]
    ) -> AgentInstance:
        """Auswahl basierend auf geringster Verbindungsanzahl."""
        min_connections = float("inf")
        selected_instance = instances[0]

        for instance in instances:
            connections = self._connection_counts.get(instance.instance_id, 0)
            if connections < min_connections:
                min_connections = connections
                selected_instance = instance

        return selected_instance

    def _response_time_select(self, instances: List[AgentInstance]) -> AgentInstance:
        """Auswahl basierend auf Antwortzeit."""
        best_instance = instances[0]
        best_time = float("inf")

        for instance in instances:
            response_time = instance.agent.health.response_time_ms or float("inf")
            if response_time < best_time:
                best_time = response_time
                best_instance = instance

        return best_instance

    def _weighted_round_robin_select(
        self, instances: List[AgentInstance]
    ) -> AgentInstance:
        """Gewichtete Round Robin-Auswahl."""
        # Vereinfachte Implementierung - verwendet Gewichte
        weighted_instances = []
        for instance in instances:
            weight = max(1, instance.weight)
            weighted_instances.extend([instance] * weight)

        return self._round_robin_select(weighted_instances)

    def record_connection(self, instance_id: str) -> None:
        """Registriert eine neue Verbindung."""
        self._connection_counts[instance_id] = (
            self._connection_counts.get(instance_id, 0) + 1
        )

    def release_connection(self, instance_id: str) -> None:
        """Gibt eine Verbindung frei."""
        if instance_id in self._connection_counts:
            self._connection_counts[instance_id] = max(
                0, self._connection_counts[instance_id] - 1
            )


class ServiceDiscovery:
    """Service Discovery für KEI-Agents."""

    def __init__(
        self,
        client: KeiAgentClient,
        strategy: DiscoveryStrategy = DiscoveryStrategy.REGISTRY_BASED,
    ):
        self.client = client
        self.strategy = strategy
        self.health_monitor = HealthMonitor()
        self.load_balancer = LoadBalancer()
        self._cache: Dict[str, DiscoveryResult] = {}
        self._cache_ttl = 60.0  # Cache TTL in Sekunden

    async def discover_agents(self, query: DiscoveryQuery) -> DiscoveryResult:
        """Führt Agent Discovery durch."""
        try:
            start_time = time.time()

            # Prüfe Cache
            cache_key = self._create_cache_key(query)
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                return cached_result

            # Führe Discovery durch
            instances = await self._perform_discovery(query)

            # Erstelle Ergebnis
            query_time = time.time() - start_time
            result = DiscoveryResult(
                instances=instances,
                total_found=len(instances),
                query_time=query_time,
                cached=False,
            )

            # Cache Ergebnis
            self._cache_result(cache_key, result)

            return result

        except Exception as e:
            raise DiscoveryError(f"Service Discovery fehlgeschlagen: {e}")

    async def _perform_discovery(self, query: DiscoveryQuery) -> List[AgentInstance]:
        """Führt die eigentliche Discovery durch."""
        # Vereinfachte Implementierung - in echter Implementierung würde hier
        # eine Anfrage an den Agent Registry Service gemacht

        # Simuliere Discovery-Ergebnis
        mock_instances = []

        # In echter Implementierung: API-Call zum Registry Service
        # agents = await self.client.list_agents(capabilities=query.capabilities)

        return mock_instances

    def _create_cache_key(self, query: DiscoveryQuery) -> str:
        """Erstellt einen Cache-Schlüssel für eine Query."""
        return f"discovery:{hash(str(query.to_dict()))}"

    def _get_cached_result(self, cache_key: str) -> Optional[DiscoveryResult]:
        """Holt ein gecachtes Ergebnis."""
        if cache_key in self._cache:
            result = self._cache[cache_key]
            # Prüfe TTL (vereinfacht)
            return result
        return None

    def _cache_result(self, cache_key: str, result: DiscoveryResult) -> None:
        """Cached ein Discovery-Ergebnis."""
        result.cached = True
        self._cache[cache_key] = result


class AgentDiscoveryClient:
    """Client für Agent Discovery."""

    def __init__(self, client: KeiAgentClient):
        self.client = client
        self.service_discovery = ServiceDiscovery(client)

    async def find_agents_by_capability(
        self, capability: str, max_results: int = 10
    ) -> List[Agent]:
        """Findet Agents mit einer bestimmten Capability."""
        query = DiscoveryQuery(capabilities=[capability], max_results=max_results)

        result = await self.service_discovery.discover_agents(query)
        return [instance.agent for instance in result.instances]

    async def find_best_agent(self, capabilities: List[str]) -> Optional[Agent]:
        """Findet den besten Agent für gegebene Capabilities."""
        query = DiscoveryQuery(
            capabilities=capabilities,
            health_check=True,
            load_balancing=True,
            max_results=1,
        )

        result = await self.service_discovery.discover_agents(query)
        if result.instances:
            return result.instances[0].agent

        return None
