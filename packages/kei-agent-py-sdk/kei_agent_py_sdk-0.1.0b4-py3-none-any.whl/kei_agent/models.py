# sdk/python/kei_agent/models.py
"""
KEI-Agent SDK Models - Datenmodelle für das SDK.

Definiert alle Datenstrukturen für Agents, Discovery und Metadaten.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class AgentStatus(str, Enum):
    """Status eines Agents."""

    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    ERROR = "error"


class HealthStatus(str, Enum):
    """Health Status eines Agents."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class AgentCapability:
    """Repräsentiert eine Agent-Capability."""

    name: str
    version: str = "1.0.0"
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    required: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "parameters": self.parameters,
            "required": self.required,
        }


@dataclass
class AgentHealth:
    """Health-Informationen eines Agents."""

    status: HealthStatus = HealthStatus.UNKNOWN
    score: float = 0.0  # 0.0 - 1.0
    last_check: Optional[datetime] = None
    response_time_ms: Optional[float] = None
    error_rate: float = 0.0
    uptime_seconds: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary."""
        return {
            "status": self.status.value,
            "score": self.score,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "response_time_ms": self.response_time_ms,
            "error_rate": self.error_rate,
            "uptime_seconds": self.uptime_seconds,
        }


@dataclass
class AgentMetadata:
    """Metadaten eines Agents."""

    version: str = "1.0.0"
    framework: str = "kei-agent"
    runtime: str = "python"
    tags: List[str] = field(default_factory=list)
    owner: Optional[str] = None
    tenant: Optional[str] = None
    region: Optional[str] = None
    environment: str = "production"

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary."""
        return {
            "version": self.version,
            "framework": self.framework,
            "runtime": self.runtime,
            "tags": self.tags,
            "owner": self.owner,
            "tenant": self.tenant,
            "region": self.region,
            "environment": self.environment,
        }


@dataclass
class Agent:
    """Repräsentiert einen Agent."""

    agent_id: str
    name: str
    description: str = ""
    status: AgentStatus = AgentStatus.AVAILABLE
    capabilities: List[AgentCapability] = field(default_factory=list)
    metadata: AgentMetadata = field(default_factory=AgentMetadata)
    health: AgentHealth = field(default_factory=AgentHealth)
    endpoint: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "capabilities": [cap.to_dict() for cap in self.capabilities],
            "metadata": self.metadata.to_dict(),
            "health": self.health.to_dict(),
            "endpoint": self.endpoint,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


@dataclass
class AgentInstance:
    """Repräsentiert eine Agent-Instanz."""

    instance_id: str
    agent: Agent
    endpoint: str
    load_factor: float = 0.0  # 0.0 - 1.0
    priority: int = 0
    weight: int = 1

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary."""
        return {
            "instance_id": self.instance_id,
            "agent": self.agent.to_dict(),
            "endpoint": self.endpoint,
            "load_factor": self.load_factor,
            "priority": self.priority,
            "weight": self.weight,
        }


@dataclass
class DiscoveryQuery:
    """Query für Service Discovery."""

    capabilities: List[str] = field(default_factory=list)
    region_preference: Optional[str] = None
    max_latency_ms: Optional[float] = None
    health_check: bool = True
    load_balancing: bool = False
    max_results: int = 10

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary."""
        return {
            "capabilities": self.capabilities,
            "region_preference": self.region_preference,
            "max_latency_ms": self.max_latency_ms,
            "health_check": self.health_check,
            "load_balancing": self.load_balancing,
            "max_results": self.max_results,
        }


@dataclass
class DiscoveryResult:
    """Ergebnis einer Service Discovery."""

    instances: List[AgentInstance] = field(default_factory=list)
    total_found: int = 0
    query_time: float = 0.0
    cached: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary."""
        return {
            "instances": [instance.to_dict() for instance in self.instances],
            "total_found": self.total_found,
            "query_time": self.query_time,
            "cached": self.cached,
        }
