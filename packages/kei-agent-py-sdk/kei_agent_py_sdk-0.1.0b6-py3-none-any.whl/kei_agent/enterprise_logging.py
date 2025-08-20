# sdk/python/kei_agent/enterprise_logging.py
"""
Enterprise-Grade Structured Logging for KEI-Agent SDK.

Implementiert strukturiertes JSON-Logging with Correlation-IDs, Performance-Metrics
and enterprise features for Production-Deployments.
"""

from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Union
from contextvars import ContextVar
from dataclasses import dataclass, field, asdict
import uuid

# Context Variables for Request-Tracking
correlation_id_var: ContextVar[Optional[str]] = ContextVar(
    "correlation_id", default=None
)
trace_id_var: ContextVar[Optional[str]] = ContextVar("trace_id", default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar("user_id", default=None)


def _get_package_version() -> str:
    """Loads the Package-Version out the metadata.

    Returns:
        Package-Version or Fallback-Version
    """
    try:
        from importlib.metadata import version

        return version("kei_agent_py_sdk")
    except Exception:
        return "0.0.0-dev"


@dataclass
class LogContext:
    """Kontext-informationen for strukturiertes Logging.

    Attributes:
        correlation_id: Adeutige ID for Request-Tracking
        trace_id: Distributed Tracing ID
        user_id: Benutzer-ID for Audit-Zwecke
        agent_id: Agent-ID for Multi-Agent-Systeme
        operation: Aktuelle operation
        component: SDK-Komponente
        version: SDK-Version
        environment: Deployment-Aroatdgebung
        custom_fields: Zusätzliche benutzerdefinierte Felder
    """

    correlation_id: Optional[str] = None
    trace_id: Optional[str] = None
    user_id: Optional[str] = None
    agent_id: Optional[str] = None
    operation: Optional[str] = None
    component: Optional[str] = None
    version: Optional[str] = None
    environment: Optional[str] = None
    custom_fields: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert LogContext to dictionary for JSON-Serialisierung.

        Returns:
            Dictionary-Repräsentation des Kontexts
        """
        context = asdict(self)
        # Entferne None-Werte für sauberes JSON
        return {k: v for k, v in context.items() if v is not None}


class StructuredFormatter(logging.Formatter):
    """JSON-Formatter for strukturiertes Logging.

    Creates JSON-formatierte Log-Messages with Kontext-Informationen,
    Timestamps and strukturierten Daten for Enterprise-Monitoring.
    """

    def __init__(
        self,
        include_context: bool = True,
        include_performance: bool = True,
        extra_fields: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initializes Structured Formatter.

        Args:
            include_context: Kontext-Informationen einschließen
            include_performance: Performance-Metrics einschließen
            extra_fields: Zusätzliche statische Felder
        """
        super().__init__()
        self.include_context = include_context
        self.include_performance = include_performance
        self.extra_fields = extra_fields or {}

    def format(self, record: logging.LogRecord) -> str:
        """Formats LogRecord as JSON."""
        log_data = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if hasattr(record, "thread") and record.thread:
            log_data["thread_id"] = record.thread
            log_data["thread_name"] = getattr(record, "threadName", None)
        if hasattr(record, "process") and record.process:
            log_data["process_id"] = record.process
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info)
                if record.exc_info
                else None,
            }
        if self.include_context:
            context = {
                "correlation_id": correlation_id_var.get(),
                "trace_id": trace_id_var.get(),
                "user_id": user_id_var.get(),
            }
            context = {k: v for k, v in context.items() if v is not None}
            if context:
                log_data["context"] = context
        extra_data = {}
        for key, value in record.__dict__.items():
            if key not in {
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "getMessage",
                "exc_info",
                "exc_text",
                "stack_info",
                "message",
            }:
                extra_data[key] = value
        if extra_data:
            log_data["extra"] = extra_data
        if self.include_performance and hasattr(record, "duration"):
            log_data["performance"] = {
                "duration_ms": getattr(record, "duration", None),
                "memory_usage": getattr(record, "memory_usage", None),
                "cpu_usage": getattr(record, "cpu_usage", None),
            }
        if self.extra_fields:
            log_data.update(self.extra_fields)
        return json.dumps(log_data, ensure_ascii=False, default=str)


class RedactingFilter(logging.Filter):
    """Filtert sensible informationen out Log-Records.

    Ersetzt bekannte geheime Werte (Token, Secrets, Passwörter) durch '***'.
    """

    SENSITIVE_KEYS = ("token", "secret", "password", "api_key", "client_secret")

    def filter(self, record: logging.LogRecord) -> bool:
        # Redact in message
        msg = record.getMessage()
        for key in self.SENSITIVE_KEYS:
            # naive pattern-based redaction
            msg = msg.replace(key, "***")
        record.msg = msg

        # Redact in extra dict
        for attr, value in list(record.__dict__.items()):
            if isinstance(value, str):
                lowered = attr.lower()
                if any(k in lowered for k in self.SENSITIVE_KEYS):
                    record.__dict__[attr] = "***"
        return True


class EnterpriseLogger:
    """Enterprise-Grade Logger for KEI-Agent SDK.

    Bietet strukturiertes Logging with Kontext-management, Performance-Tracking
    and enterprise features for Production-Deployments.
    """

    def __init__(
        self,
        name: str,
        level: Union[str, int] = logging.INFO,
        enable_structured: bool = True,
        enable_console: bool = True,
        enable_file: bool = False,
        file_path: Optional[str] = None,
        extra_fields: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initializes Enterprise Logger.

        Args:
            name: Logger name
            level: Log level
            enable_structured: Enable structured JSON logging
            enable_console: Enable console output
            enable_file: Enable file output
            file_path: Path to log file
            extra_fields: Additional static fields
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Clear existing handlers to avoid duplicates
        self.logger.handlers.clear()

        # Structured Formatter
        if enable_structured:
            formatter: Union[StructuredFormatter, logging.Formatter] = (
                StructuredFormatter(extra_fields=extra_fields)
            )
        else:
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )

        # Redaction filter
        redactor = RedactingFilter()
        self.logger.addFilter(redactor)

        # Console Handler
        if enable_console:
            console_handler = logging.StreamHandler()
            console_handler.addFilter(redactor)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

        # File Handler
        if enable_file and file_path:
            file_handler = logging.FileHandler(file_path)
            file_handler.addFilter(redactor)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def set_context(self, context: LogContext) -> None:
        """Setzt Logging-Kontext for aktuellen Request.

        Args:
            context: Log-Kontext with Tracking-informationen
        """
        if context.correlation_id:
            correlation_id_var.set(context.correlation_id)
        if context.trace_id:
            trace_id_var.set(context.trace_id)
        if context.user_id:
            user_id_var.set(context.user_id)

    def clear_context(self) -> None:
        """Deletes aktuellen Logging-Kontext."""
        correlation_id_var.set(None)
        trace_id_var.set(None)
        user_id_var.set(None)

    def create_correlation_id(self) -> str:
        """Creates neue Correlation-ID and setzt sie im Kontext.

        Returns:
            Neue Correlation-ID
        """
        correlation_id = str(uuid.uuid4())
        correlation_id_var.set(correlation_id)
        return correlation_id

    def debug(self, message: str, **kwargs: Any) -> None:
        """Debug-Level Logging."""
        self.logger.debug(message, extra=kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """Info-Level Logging."""
        self.logger.info(message, extra=kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Warning-Level Logging."""
        self.logger.warning(message, extra=kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Error-Level Logging."""
        self.logger.error(message, extra=kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        """Critical-Level Logging."""
        self.logger.critical(message, extra=kwargs)

    def log_operation_start(self, operation: str, **kwargs: Any) -> str:
        """Loggt Start ar operation with Performatce-Tracking.

        Args:
            operation: operation name
            **kwargs: Tosätzliche Kontext-informationen

        Returns:
            operation-ID for Tracking
        """
        operation_id = str(uuid.uuid4())
        start_time = time.time()

        self.info(
            f"operation startingd: {operation}",
            operation=operation,
            operation_id=operation_id,
            operation_start_time=start_time,
            **kwargs,
        )

        return operation_id

    def log_operation_end(
        self,
        operation: str,
        operation_id: str,
        start_time: float,
        success: bool = True,
        **kwargs: Any,
    ) -> None:
        """Loggt Ende ar operation with Performatce-Metrics.

        Args:
            operation: operation name
            operation_id: operation-ID vom Start
            start_time: Start-Zeitpunkt
            success: Erfolg the operation
            **kwargs: Tosätzliche Kontext-informationen
        """
        end_time = time.time()
        duration = (end_time - start_time) * 1000  # Millisekatthe

        level_method = self.info if success else self.error
        status = "successful" if success else "failed"

        level_method(
            f"operation {status}: {operation}",
            operation=operation,
            operation_id=operation_id,
            operation_end_time=end_time,
            duration=duration,
            success=success,
            **kwargs,
        )

    def log_performatce(
        self,
        operation: str,
        duration_ms: float,
        memory_usage: Optional[float] = None,
        cpu_usage: Optional[float] = None,
        **kwargs: Any,
    ) -> None:
        """Loggt Performatce-Metrics.

        Args:
            operation: operation name
            duration_ms: Dauer in Millisekatthe
            memory_usage: Speicherverbrauch in MB
            cpu_usage: CPU-Nuttong in Prozent
            **kwargs: Tosätzliche Metrics
        """
        self.info(
            f"Performatce-Metrik: {operation}",
            operation=operation,
            duration=duration_ms,
            memory_usage=memory_usage,
            cpu_usage=cpu_usage,
            **kwargs,
        )

    def log_security_event(
        self, event_type: str, severity: str, description: str, **kwargs: Any
    ) -> None:
        """Loggt securitysereignis for Audit-Zwecke.

        Args:
            event_type: type of the securitysereignisses
            severity: Schweregrad (low, mediaroatd, high, critical)
            description: Beschreibung of the Ereignisses
            **kwargs: Tosätzliche securityskontext-informationen
        """
        level_map = {
            "low": self.info,
            "mediaroatd": self.warning,
            "high": self.error,
            "critical": self.critical,
        }

        log_method = level_map.get(severity.lower(), self.warning)

        log_method(
            f"securitysereignis: {description}",
            security_event_type=event_type,
            security_severity=severity,
            security_description=description,
            **kwargs,
        )


# Globaler Logger for SDK
_sdk_logger: Optional[EnterpriseLogger] = None


def get_logger(name: str = "kei_agent") -> EnterpriseLogger:
    """Gibt Enterprise Logger for KEI-Agent SDK zurück.

    Args:
        name: Logger-Name

    Returns:
        Configurierter Enterprise Logger
    """
    global _sdk_logger

    if _sdk_logger is None:
        _sdk_logger = EnterpriseLogger(
            name=name,
            level=logging.INFO,
            enable_structured=True,
            enable_console=True,
            extra_fields={
                "service": "kei-agent-sdk",
                "version": _get_package_version(),
            },
        )

    return _sdk_logger


def configure_logging(
    level: Union[str, int] = logging.INFO,
    enable_structured: bool = True,
    enable_file: bool = False,
    file_path: Optional[str] = None,
    extra_fields: Optional[Dict[str, Any]] = None,
) -> EnterpriseLogger:
    """Configures globalen SDK-Logr.

    Args:
        level: Log-Level
        enable_structured: Strukturiertes JSON-Logging aktivieren
        enable_file: File-Output aktivieren
        file_path: Path for Log-File
        extra_fields: Tosätzliche statische Felthe

    Returns:
        Configureser Enterprise Logr
    """
    global _sdk_logger

    _sdk_logger = EnterpriseLogger(
        name="kei_agent",
        level=level,
        enable_structured=enable_structured,
        enable_console=True,
        enable_file=enable_file,
        file_path=file_path,
        extra_fields=extra_fields,
    )

    return _sdk_logger


__all__ = [
    "LogContext",
    "StructuredFormatter",
    "RedactingFilter",
    "EnterpriseLogger",
    "get_logger",
    "configure_logging",
    "correlation_id_var",
    "trace_id_var",
    "user_id_var",
]
