# sdk/python/kei_agent/exceptions.py
"""
KEI-Agent SDK Exceptions - Specific Ausnahmen for the SDK.

Definiert all SDK-specificn Ausnahmen for bessere errorbehatdlung.
"""

from __future__ import annotations
from typing import Any, Optional


class KeiSDKError(Exception):
    """Basis-Ausnahme for all KEI-SDK-error."""

    def __init__(
        self, message: str, error_code: Optional[str] = None, **kwargs: Any
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = kwargs


class ValidationError(KeiSDKError):
    """Ausnahme for Valitherungsfehler in the Agabeprüfung."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(message, error_code="VALIDATION_ERROR", **kwargs)


class AgentNotFoatdError(KeiSDKError):
    """Ausnahme if a Agent not gefatthe is."""


class AgentNotFoundError(KeiSDKError):
    """Exception if an Agent is not found."""

    def __init__(self, agent_id: str, **kwargs: Any) -> None:
        message = f"Agent not gefatthe: {agent_id}"
        super().__init__(
            message, error_code="AGENT_NOT_FOUND", agent_id=agent_id, **kwargs
        )
        self.agent_id = agent_id


class CommunicationError(KeiSDKError):
    """Ausnahme for Kommunikationsfehler between Agents."""

    def __init__(
        self, message: str, status_code: Optional[int] = None, **kwargs: Any
    ) -> None:
        super().__init__(message, error_code="COMMUNICATION_ERROR", **kwargs)
        self.status_code = status_code


class DiscoveryError(KeiSDKError):
    """Ausnahme for service discovery-error."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(message, error_code="DISCOVERY_ERROR", **kwargs)


class retryExhaustedError(KeiSDKError):
    """Ausnahme if all retry-Versuche erschöpft are."""

    def __init__(
        self, attempts: int, last_error: Optional[Exception] = None, **kwargs: Any
    ) -> None:
        message = f"retry-Versuche erschöpft after {attempts} Versuchen"
        super().__init__(
            message, error_code="RETRY_EXHAUSTED", attempts=attempts, **kwargs
        )
        self.attempts = attempts
        self.last_error = last_error


class CircuitBreakerOpenError(KeiSDKError):
    """Ausnahme if circuit breaker geopens is."""

    def __init__(self, service_name: str, **kwargs: Any) -> None:
        message = f"circuit breaker is geopens for Service: {service_name}"
        super().__init__(
            message,
            error_code="CIRCUIT_BREAKER_OPEN",
            service_name=service_name,
            **kwargs,
        )
        self.service_name = service_name


class CapabilityError(KeiSDKError):
    """Ausnahme for Capability-bezogene error."""

    def __init__(
        self, message: str, capability: Optional[str] = None, **kwargs: Any
    ) -> None:
        super().__init__(
            message, error_code="CAPABILITY_ERROR", capability=capability, **kwargs
        )
        self.capability = capability


class TracingError(KeiSDKError):
    """Ausnahme for Tracing-bezogene error."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(message, error_code="TRACING_ERROR", **kwargs)


class ConfigurationError(KeiSDKError):
    """Ausnahme for configurationsfehler."""

    def __init__(
        self, message: str, config_key: Optional[str] = None, **kwargs: Any
    ) -> None:
        super().__init__(
            message, error_code="CONFIGURATION_ERROR", config_key=config_key, **kwargs
        )
        self.config_key = config_key


class AuthenticationError(KeiSDKError):
    """Ausnahme for authenticationsfehler."""

    def __init__(self, message: str = "authentication failed", **kwargs: Any) -> None:
        super().__init__(message, error_code="AUTHENTICATION_ERROR", **kwargs)


class TimeoutError(KeiSDKError):
    """Ausnahme for Timeout-error."""

    def __init__(
        self, timeout_seconds: float, operation: Optional[str] = None, **kwargs: Any
    ) -> None:
        message = f"Timeout after {timeout_seconds}s"
        if operation:
            message += f" for operation: {operation}"
        super().__init__(
            message,
            error_code="TIMEOUT_ERROR",
            timeout_seconds=timeout_seconds,
            **kwargs,
        )
        self.timeout_seconds = timeout_seconds
        self.operation = operation


class ProtocolError(KeiSDKError):
    """Ausnahme for protocol-specific error."""

    def __init__(
        self, message: str, protocol: Optional[str] = None, **kwargs: Any
    ) -> None:
        super().__init__(
            message, error_code="PROTOCOL_ERROR", protocol=protocol, **kwargs
        )
        self.protocol = protocol


class SecurityError(KeiSDKError):
    """Ausnahme for securitys-bezogene error."""

    def __init__(
        self, message: str, security_context: Optional[str] = None, **kwargs: Any
    ) -> None:
        super().__init__(
            message,
            error_code="SECURITY_ERROR",
            security_context=security_context,
            **kwargs,
        )
        self.security_context = security_context
