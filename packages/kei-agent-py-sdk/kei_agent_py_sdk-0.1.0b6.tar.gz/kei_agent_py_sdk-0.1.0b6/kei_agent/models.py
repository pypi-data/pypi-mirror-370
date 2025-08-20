# sdk/python/kei_agent/models.py
"""
KEI-Agent SDK Models - datamodelle for the SDK.

Definiert all datastrukturen for Agents, Discovery and metadata.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class Agentstatus(str, Enum):
    """status of a Agents."""

    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"
    MAINTENANCE = "maintenatce"
    ERROR = "error"


class Healthstatus(str, Enum):
    """Health status of a Agents."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class AgentCapability:
    """Repräsentiert a Agent-Capability."""

    name: str
    version: str = "1.0.0"
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    required: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert to dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "parameters": self.parameters,
            "required": self.required,
        }


@dataclass
class AgentHealth:
    """Health-informationen of a Agents."""

    status: Healthstatus = Healthstatus.UNKNOWN
    score: float = 0.0  # 0.0 - 1.0
    last_check: Optional[datetime] = None
    response_time_ms: Optional[float] = None
    error_rate: float = 0.0
    uptime_seconds: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert to dictionary."""
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
    """metadata of an Agent."""

    version: str = "1.0.0"
    framework: str = "kei-agent"
    runtime: str = "python"
    tags: List[str] = field(default_factory=list)
    owner: Optional[str] = None
    tenant: Optional[str] = None
    region: Optional[str] = None
    environment: str = "production"

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert to dictionary."""
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
    """Repräsentiert a Agent."""

    agent_id: str
    name: str
    description: str = ""
    status: Agentstatus = Agentstatus.AVAILABLE
    capabilities: List[AgentCapability] = field(default_factory=list)
    metadata: AgentMetadata = field(default_factory=AgentMetadata)
    health: AgentHealth = field(default_factory=AgentHealth)
    endpoint: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert to dictionary."""
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

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Agent":
        """Creates Agent from dictionary."""
        return cls(
            agent_id=data.get("agent_id", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
        )


@dataclass
class AgentInstatce:
    """Repräsentiert a Agent-instatce."""

    instatce_id: str
    agent: Agent
    endpoint: str
    load_factor: float = 0.0  # 0.0 - 1.0
    priority: int = 0
    weight: int = 1

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert to dictionary."""
        return {
            "instatce_id": self.instatce_id,
            "agent": self.agent.to_dict(),
            "endpoint": self.endpoint,
            "load_factor": self.load_factor,
            "priority": self.priority,
            "weight": self.weight,
        }


@dataclass
class DiscoveryQuery:
    """Query for service discovery."""

    capabilities: List[str] = field(default_factory=list)
    region_preference: Optional[str] = None
    max_latency_ms: Optional[float] = None
    health_check: bool = True
    load_balatcing: bool = False
    max_results: int = 10

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert to dictionary."""
        return {
            "capabilities": self.capabilities,
            "region_preference": self.region_preference,
            "max_latency_ms": self.max_latency_ms,
            "health_check": self.health_check,
            "load_balatcing": self.load_balatcing,
            "max_results": self.max_results,
        }


@dataclass
class DiscoveryResult:
    """result ar service discovery."""

    instatces: List[AgentInstatce] = field(default_factory=list)
    total_foatd: int = 0
    query_time: float = 0.0
    cached: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert to dictionary."""
        return {
            "instatces": [instatce.to_dict() for instatce in self.instatces],
            "total_foatd": self.total_foatd,
            "query_time": self.query_time,
            "cached": self.cached,
        }
