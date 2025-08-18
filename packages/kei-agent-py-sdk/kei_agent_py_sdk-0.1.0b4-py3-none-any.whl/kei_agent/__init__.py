# sdk/python/kei_agent/__init__.py
"""
KEI-Agent-Framework Python SDK - Enterprise-Grade Client SDK.

Vollständige SDK-Implementation mit Agent-to-Agent-Kommunikation,
Distributed Tracing, Retry-Mechanismen und Capability Advertisement.
Enthält sowohl Enterprise SDK als auch Basic Agent Skeleton.
Integriert alle KEI-Protokolle (RPC, Stream, Bus, MCP) in einer einheitlichen API.
"""

from __future__ import annotations

import logging

# Agent-to-Agent Communication
from .a2a import (
    A2AClient,
    A2AMessage,
    A2AResponse,
    CommunicationProtocol,
    LoadBalancingStrategy,
    FailoverConfig,
)

# Capability Advertisement
from .capabilities import (
    CapabilityManager,
    CapabilityProfile,
    MCPIntegration,
    CapabilityNegotiation,
    CapabilityVersioning,
)

# Core SDK Components
from .client import (
    KeiAgentClient,
    AgentClientConfig,
    ConnectionConfig,
    RetryConfig,
    TracingConfig,
)

# Service Discovery
from .discovery import (
    ServiceDiscovery,
    AgentDiscoveryClient,
    DiscoveryStrategy,
    HealthMonitor,
    LoadBalancer,
)

# Enterprise Features
from .enterprise_logging import (
    LogContext,
    StructuredFormatter,
    EnterpriseLogger,
    get_logger,
    configure_logging,
)

# Exceptions
from .exceptions import (
    KeiSDKError,
    AgentNotFoundError,
    CommunicationError,
    DiscoveryError,
    RetryExhaustedError,
    CircuitBreakerOpenError,
    CapabilityError,
    TracingError,
)
from .health_checks import (
    HealthStatus,
    HealthCheckResult,
    BaseHealthCheck,
    DatabaseHealthCheck,
    APIHealthCheck,
    MemoryHealthCheck,
    HealthCheckSummary,
    HealthCheckManager,
    get_health_manager,
)
from .input_validation import (
    ValidationSeverity,
    ValidationResult,
    BaseValidator,
    StringValidator,
    NumberValidator,
    JSONValidator,
    CompositeValidator,
    InputValidator,
    get_input_validator,
)

# Basic Agent Components (from kei_agent.py)
from .kei_agent import AgentConfig, AgentSkeleton

# Models and Types
from .models import (
    Agent,
    AgentMetadata,
    AgentCapability,
    AgentHealth,
    AgentInstance,
    DiscoveryQuery,
    DiscoveryResult,
)
from .protocol_clients import (
    BaseProtocolClient,
    KEIRPCClient,
    KEIStreamClient,
    KEIBusClient,
    KEIMCPClient,
)
from .protocol_selector import ProtocolSelector

# Refactored Unified Protocol Integration
from .protocol_types import ProtocolType, AuthType, ProtocolConfig, SecurityConfig

# Retry Mechanisms
from .retry import (
    RetryManager,
    RetryStrategy,
    CircuitBreaker,
    CircuitBreakerState,
    DeadLetterQueue,
    RetryPolicy,
)
from .security_manager import SecurityManager

# Distributed Tracing
from .tracing import (
    TracingManager,
    TraceContext,
    SpanBuilder,
    TracingExporter,
    PerformanceMetrics,
)

# Unified Protocol Integration (Legacy)
from .unified_client import (
    UnifiedKeiAgentClient as LegacyUnifiedKeiAgentClient,
)
from .unified_client_refactored import UnifiedKeiAgentClient

# Utilities
from .utils import (
    create_correlation_id,
    parse_agent_id,
    validate_capability,
    format_trace_id,
    calculate_backoff,
)

# Version Information - Dynamisch aus Package-Metadaten geladen
try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    # Python < 3.8 Fallback
    from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version("kei_agent_py_sdk")
except PackageNotFoundError:
    # Fallback für Development-Umgebung (nicht installiertes Package)
    __version__ = "0.0.0-dev"

__author__ = "KEI-Agent-Framework Team"
__email__ = "dev@kei-agent-framework.com"
__license__ = "MIT"

# Package Metadata
__title__ = "kei_agent_py_sdk"
__description__ = "Enterprise-Grade Python SDK für KEI-Agent-Framework"
__url__ = "https://github.com/oscharko-dev/kei-agent-py-sdk"

# Compatibility Information
__python_requires__ = ">=3.8"
__framework_version__ = ">=1.0.0"

# Export All Public APIs
__all__ = [
    # Core Client
    "KeiAgentClient",
    "AgentClientConfig",
    "ConnectionConfig",
    "RetryConfig",
    "TracingConfig",
    # Unified Protocol Integration
    "UnifiedKeiAgentClient",
    "ProtocolType",
    "AuthType",
    "ProtocolConfig",
    "SecurityConfig",
    "SecurityManager",
    "BaseProtocolClient",
    "KEIRPCClient",
    "KEIStreamClient",
    "KEIBusClient",
    "KEIMCPClient",
    "ProtocolSelector",
    # Legacy Support
    "LegacyUnifiedKeiAgentClient",
    # Enterprise Features
    "LogContext",
    "StructuredFormatter",
    "EnterpriseLogger",
    "get_logger",
    "configure_logging",
    "HealthStatus",
    "HealthCheckResult",
    "BaseHealthCheck",
    "DatabaseHealthCheck",
    "APIHealthCheck",
    "MemoryHealthCheck",
    "HealthCheckSummary",
    "HealthCheckManager",
    "get_health_manager",
    "ValidationSeverity",
    "ValidationResult",
    "BaseValidator",
    "StringValidator",
    "NumberValidator",
    "JSONValidator",
    "CompositeValidator",
    "InputValidator",
    "get_input_validator",
    # Agent-to-Agent Communication
    "A2AClient",
    "A2AMessage",
    "A2AResponse",
    "CommunicationProtocol",
    "LoadBalancingStrategy",
    "FailoverConfig",
    # Distributed Tracing
    "TracingManager",
    "TraceContext",
    "SpanBuilder",
    "TracingExporter",
    "PerformanceMetrics",
    # Retry Mechanisms
    "RetryManager",
    "RetryStrategy",
    "CircuitBreaker",
    "CircuitBreakerState",
    "DeadLetterQueue",
    "RetryPolicy",
    # Capability Advertisement
    "CapabilityManager",
    "CapabilityProfile",
    "MCPIntegration",
    "CapabilityNegotiation",
    "CapabilityVersioning",
    # Service Discovery
    "ServiceDiscovery",
    "AgentDiscoveryClient",
    "DiscoveryStrategy",
    "HealthMonitor",
    "LoadBalancer",
    # Models
    "Agent",
    "AgentMetadata",
    "AgentCapability",
    "AgentHealth",
    "AgentInstance",
    "DiscoveryQuery",
    "DiscoveryResult",
    # Exceptions
    "KeiSDKError",
    "AgentNotFoundError",
    "CommunicationError",
    "DiscoveryError",
    "RetryExhaustedError",
    "CircuitBreakerOpenError",
    "CapabilityError",
    "TracingError",
    # Utilities
    "create_correlation_id",
    "parse_agent_id",
    "validate_capability",
    "format_trace_id",
    "calculate_backoff",
    # Basic Agent Components
    "AgentConfig",
    "AgentSkeleton",
    # Version Info
    "__version__",
    "__author__",
    "__license__",
    "__title__",
    "__description__",
    "__url__",
    "__email__",
]

# Version Information - Bereits oben definiert, hier nur Referenz
# __version__ wird oben dynamisch geladen
__author__ = "KEI-Agent-Framework Team"
__license__ = "MIT"
__title__ = "kei_agent_py_sdk"
__description__ = "KEI-Agent Python SDK - Enterprise-Grade Multi-Agent Framework"
__url__ = "https://github.com/oscharko-dev/kei-agent-py-sdk"
__email__ = "dev@kei-agent-framework.com"


# SDK Initialization
def get_sdk_info() -> dict[str, str]:
    """Holt SDK-Informationen.

    Returns:
        Dictionary mit SDK-Metadaten
    """
    return {
        "name": __title__,
        "version": __version__,
        "description": __description__,
        "author": __author__,
        "license": __license__,
        "url": __url__,
        "python_requires": __python_requires__,
        "framework_version": __framework_version__,
    }


def create_default_client(
    base_url: str, api_token: str, agent_id: str, **kwargs
) -> KeiAgentClient:
    """Erstellt Standard-Client mit optimalen Einstellungen.

    Args:
        base_url: KEI-Framework Base-URL
        api_token: API-Token für Authentifizierung
        agent_id: Eindeutige Agent-ID
        **kwargs: Zusätzliche Konfigurationsparameter

    Returns:
        Konfigurierter KeiAgentClient
    """
    config = AgentClientConfig(
        base_url=base_url, api_token=api_token, agent_id=agent_id, **kwargs
    )

    return KeiAgentClient(config)


def create_a2a_client(
    base_url: str,
    api_token: str,
    agent_id: str,
    discovery_enabled: bool = True,
    tracing_enabled: bool = True,
    **kwargs,
) -> A2AClient:
    """Erstellt Agent-to-Agent-Client mit Enterprise-Features.

    Args:
        base_url: KEI-Framework Base-URL
        api_token: API-Token für Authentifizierung
        agent_id: Eindeutige Agent-ID
        discovery_enabled: Service Discovery aktivieren
        tracing_enabled: Distributed Tracing aktivieren
        **kwargs: Zusätzliche Konfigurationsparameter

    Returns:
        Konfigurierter A2AClient
    """
    # Erstelle Basis-Client
    client = create_default_client(base_url, api_token, agent_id, **kwargs)

    # Erstelle A2A-Client mit erweiterten Features
    a2a_client = A2AClient(client)

    if discovery_enabled:
        a2a_client.enable_service_discovery()

    if tracing_enabled:
        a2a_client.enable_distributed_tracing()

    return a2a_client


# Logging Configuration
# Erstelle SDK-Logger
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)

# Verhindere doppelte Log-Messages
_logger.propagate = False

# Füge Standard-Handler hinzu falls noch keiner existiert
if not _logger.handlers:
    _handler = logging.StreamHandler()
    _formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    _handler.setFormatter(_formatter)
    _logger.addHandler(_handler)

# SDK-Initialisierung loggen
_logger.info(f"KEI Agent SDK v{__version__} initialisiert")

# Cleanup
del logging, _logger, _handler, _formatter
