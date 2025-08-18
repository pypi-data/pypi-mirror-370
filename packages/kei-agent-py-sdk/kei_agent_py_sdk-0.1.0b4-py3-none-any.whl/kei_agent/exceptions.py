# sdk/python/kei_agent/exceptions.py
"""
KEI-Agent SDK Exceptions - Spezifische Ausnahmen für das SDK.

Definiert alle SDK-spezifischen Ausnahmen für bessere Fehlerbehandlung.
"""

from __future__ import annotations
from typing import Any, Optional


class KeiSDKError(Exception):
    """Basis-Ausnahme für alle KEI-SDK-Fehler."""

    def __init__(
        self, message: str, error_code: Optional[str] = None, **kwargs: Any
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = kwargs


class AgentNotFoundError(KeiSDKError):
    """Ausnahme wenn ein Agent nicht gefunden wird."""

    def __init__(self, agent_id: str, **kwargs: Any) -> None:
        message = f"Agent nicht gefunden: {agent_id}"
        super().__init__(
            message, error_code="AGENT_NOT_FOUND", agent_id=agent_id, **kwargs
        )
        self.agent_id = agent_id


class CommunicationError(KeiSDKError):
    """Ausnahme für Kommunikationsfehler zwischen Agents."""

    def __init__(
        self, message: str, status_code: Optional[int] = None, **kwargs: Any
    ) -> None:
        super().__init__(message, error_code="COMMUNICATION_ERROR", **kwargs)
        self.status_code = status_code


class DiscoveryError(KeiSDKError):
    """Ausnahme für Service Discovery-Fehler."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(message, error_code="DISCOVERY_ERROR", **kwargs)


class RetryExhaustedError(KeiSDKError):
    """Ausnahme wenn alle Retry-Versuche erschöpft sind."""

    def __init__(
        self, attempts: int, last_error: Optional[Exception] = None, **kwargs: Any
    ) -> None:
        message = f"Retry-Versuche erschöpft nach {attempts} Versuchen"
        super().__init__(
            message, error_code="RETRY_EXHAUSTED", attempts=attempts, **kwargs
        )
        self.attempts = attempts
        self.last_error = last_error


class CircuitBreakerOpenError(KeiSDKError):
    """Ausnahme wenn Circuit Breaker geöffnet ist."""

    def __init__(self, service_name: str, **kwargs: Any) -> None:
        message = f"Circuit Breaker ist geöffnet für Service: {service_name}"
        super().__init__(
            message,
            error_code="CIRCUIT_BREAKER_OPEN",
            service_name=service_name,
            **kwargs,
        )
        self.service_name = service_name


class CapabilityError(KeiSDKError):
    """Ausnahme für Capability-bezogene Fehler."""

    def __init__(
        self, message: str, capability: Optional[str] = None, **kwargs: Any
    ) -> None:
        super().__init__(
            message, error_code="CAPABILITY_ERROR", capability=capability, **kwargs
        )
        self.capability = capability


class TracingError(KeiSDKError):
    """Ausnahme für Tracing-bezogene Fehler."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(message, error_code="TRACING_ERROR", **kwargs)


class ConfigurationError(KeiSDKError):
    """Ausnahme für Konfigurationsfehler."""

    def __init__(
        self, message: str, config_key: Optional[str] = None, **kwargs: Any
    ) -> None:
        super().__init__(
            message, error_code="CONFIGURATION_ERROR", config_key=config_key, **kwargs
        )
        self.config_key = config_key


class AuthenticationError(KeiSDKError):
    """Ausnahme für Authentifizierungsfehler."""

    def __init__(
        self, message: str = "Authentifizierung fehlgeschlagen", **kwargs: Any
    ) -> None:
        super().__init__(message, error_code="AUTHENTICATION_ERROR", **kwargs)


class TimeoutError(KeiSDKError):
    """Ausnahme für Timeout-Fehler."""

    def __init__(
        self, timeout_seconds: float, operation: Optional[str] = None, **kwargs: Any
    ) -> None:
        message = f"Timeout nach {timeout_seconds}s"
        if operation:
            message += f" für Operation: {operation}"
        super().__init__(
            message,
            error_code="TIMEOUT_ERROR",
            timeout_seconds=timeout_seconds,
            **kwargs,
        )
        self.timeout_seconds = timeout_seconds
        self.operation = operation


class ProtocolError(KeiSDKError):
    """Ausnahme für Protokoll-spezifische Fehler."""

    def __init__(
        self, message: str, protocol: Optional[str] = None, **kwargs: Any
    ) -> None:
        super().__init__(
            message, error_code="PROTOCOL_ERROR", protocol=protocol, **kwargs
        )
        self.protocol = protocol


class SecurityError(KeiSDKError):
    """Ausnahme für Sicherheits-bezogene Fehler."""

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
