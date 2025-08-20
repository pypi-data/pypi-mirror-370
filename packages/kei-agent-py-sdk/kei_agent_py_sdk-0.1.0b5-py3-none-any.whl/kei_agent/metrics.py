# kei_agent/metrics.py
"""
Comprehensive metrics collection for KEI-Agent Python SDK.

This module provides:
- Prometheus-compatible metrics collection
- OpenTelemetry distributed tracing integration
- Business metrics for agent lifecycle and operations
- Custom metrics for security events and performance
- Metrics export to monitoring systems
"""

from __future__ import annotations

import time
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
import logging

# Prometheus metrics
try:
    from prometheus_client import (
        Counter,
        Histogram,
        Gauge,
        Info,
        CollectorRegistry,
        generate_latest,
    )

    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

# OpenTelemetry tracing
try:
    from opentelemetry import trace

    try:
        from opentelemetry.trace import Status, StatusCode
    except ImportError:
        # Fallback for older OpenTelemetry versions
        from opentelemetry.trace.status import Status, StatusCode
    from opentelemetry.metrics import get_meter
    from opentelemetry.sdk.trace import TracerProvider

    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class MetricEvent:
    """Represents a metric event."""

    name: str
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    metric_type: str = "counter"  # counter, gauge, histogram, summary
    help_text: str = ""


class MetricsCollector:
    """Collects and manages metrics for the KEI-Agent SDK."""

    def __init__(self, registry: Optional[CollectorRegistry] = None) -> None:
        """Initialize metrics collector.

        Args:
            registry: Prometheus registry to use (creates new if None)
        """
        self.enabled = PROMETHEUS_AVAILABLE
        self.registry: Optional[CollectorRegistry] = (
            registry or CollectorRegistry() if PROMETHEUS_AVAILABLE else None
        )
        self.metrics: Dict[str, Any] = {}
        self.custom_metrics: List[MetricEvent] = []

        if self.enabled:
            self._initialize_prometheus_metrics()

        # OpenTelemetry setup
        self.tracer: Optional[Any] = None
        self.meter: Optional[Any] = None
        if OPENTELEMETRY_AVAILABLE:
            self._initialize_opentelemetry()

    def _initialize_prometheus_metrics(self) -> None:
        """Initialize Prometheus metrics."""
        if not self.enabled:
            return

        # Agent lifecycle metrics
        self.metrics["agent_connections_total"] = Counter(
            "kei_agent_connections_total",
            "Total number of agent connections",
            ["agent_id", "protocol", "status"],
            registry=self.registry,
        )

        self.metrics["agent_requests_total"] = Counter(
            "kei_agent_requests_total",
            "Total number of requests made",
            ["agent_id", "method", "status"],
            registry=self.registry,
        )

        self.metrics["agent_request_duration"] = Histogram(
            "kei_agent_request_duration_seconds",
            "Request duration in seconds",
            ["agent_id", "method", "protocol"],
            registry=self.registry,
            buckets=[
                0.001,
                0.005,
                0.01,
                0.025,
                0.05,
                0.1,
                0.25,
                0.5,
                1.0,
                2.5,
                5.0,
                10.0,
            ],
        )

        self.metrics["agent_active_connections"] = Gauge(
            "kei_agent_active_connections",
            "Number of active connections",
            ["agent_id", "protocol"],
            registry=self.registry,
        )

        # Protocol-specific metrics
        self.metrics["protocol_messages_total"] = Counter(
            "kei_agent_protocol_messages_total",
            "Total protocol messages sent/received",
            ["agent_id", "protocol", "direction", "message_type"],
            registry=self.registry,
        )

        self.metrics["protocol_errors_total"] = Counter(
            "kei_agent_protocol_errors_total",
            "Total protocol errors",
            ["agent_id", "protocol", "error_type"],
            registry=self.registry,
        )

        # Authentication metrics
        self.metrics["auth_attempts_total"] = Counter(
            "kei_agent_auth_attempts_total",
            "Total authentication attempts",
            ["agent_id", "auth_type", "status"],
            registry=self.registry,
        )

        self.metrics["auth_token_refresh_total"] = Counter(
            "kei_agent_auth_token_refresh_total",
            "Total token refresh attempts",
            ["agent_id", "auth_type", "status"],
            registry=self.registry,
        )

        # Security metrics
        self.metrics["security_events_total"] = Counter(
            "kei_agent_security_events_total",
            "Total security events",
            ["agent_id", "event_type", "severity"],
            registry=self.registry,
        )

        self.metrics["validation_errors_total"] = Counter(
            "kei_agent_validation_errors_total",
            "Total validation errors",
            ["agent_id", "validation_type", "field"],
            registry=self.registry,
        )

        # Performance metrics
        self.metrics["memory_usage_bytes"] = Gauge(
            "kei_agent_memory_usage_bytes",
            "Memory usage in bytes",
            ["agent_id"],
            registry=self.registry,
        )

        self.metrics["cpu_usage_percent"] = Gauge(
            "kei_agent_cpu_usage_percent",
            "CPU usage percentage",
            ["agent_id"],
            registry=self.registry,
        )

        # Business metrics
        self.metrics["agent_uptime_seconds"] = Gauge(
            "kei_agent_uptime_seconds",
            "Agent uptime in seconds",
            ["agent_id"],
            registry=self.registry,
        )

        self.metrics["agent_info"] = Info(
            "kei_agent_info", "Agent information", registry=self.registry
        )

    def _initialize_opentelemetry(self) -> None:
        """Initialize OpenTelemetry tracing and metrics."""
        try:
            # Set up tracer
            trace.set_tracer_provider(TracerProvider())
            self.tracer = trace.get_tracer("kei-agent-sdk")

            # Set up meter
            self.meter = get_meter("kei-agent-sdk")

            logger.info("OpenTelemetry initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize OpenTelemetry: {e}")

    def record_connection(self, agent_id: str, protocol: str, status: str) -> None:
        """Record a connection event."""
        if self.enabled and "agent_connections_total" in self.metrics:
            self.metrics["agent_connections_total"].labels(
                agent_id=agent_id, protocol=protocol, status=status
            ).inc()

    def record_request(
        self,
        agent_id: str,
        method: str,
        status: str,
        duration: float,
        protocol: str = "unknown",
    ) -> None:
        """Record a request event."""
        if not self.enabled:
            return

        # Record request count
        if "agent_requests_total" in self.metrics:
            self.metrics["agent_requests_total"].labels(
                agent_id=agent_id, method=method, status=status
            ).inc()

        # Record request duration
        if "agent_request_duration" in self.metrics:
            self.metrics["agent_request_duration"].labels(
                agent_id=agent_id, method=method, protocol=protocol
            ).observe(duration)

    def update_active_connections(
        self, agent_id: str, protocol: str, count: int
    ) -> None:
        """Update active connections gauge."""
        if self.enabled and "agent_active_connections" in self.metrics:
            self.metrics["agent_active_connections"].labels(
                agent_id=agent_id, protocol=protocol
            ).set(count)

    def record_protocol_message(
        self, agent_id: str, protocol: str, direction: str, message_type: str
    ) -> None:
        """Record a protocol message."""
        if self.enabled and "protocol_messages_total" in self.metrics:
            self.metrics["protocol_messages_total"].labels(
                agent_id=agent_id,
                protocol=protocol,
                direction=direction,
                message_type=message_type,
            ).inc()

    def record_protocol_error(
        self, agent_id: str, protocol: str, error_type: str
    ) -> None:
        """Record a protocol error."""
        if self.enabled and "protocol_errors_total" in self.metrics:
            self.metrics["protocol_errors_total"].labels(
                agent_id=agent_id, protocol=protocol, error_type=error_type
            ).inc()

    def record_auth_attempt(self, agent_id: str, auth_type: str, status: str) -> None:
        """Record an authentication attempt."""
        if self.enabled and "auth_attempts_total" in self.metrics:
            self.metrics["auth_attempts_total"].labels(
                agent_id=agent_id, auth_type=auth_type, status=status
            ).inc()

    def record_token_refresh(self, agent_id: str, auth_type: str, status: str) -> None:
        """Record a token refresh attempt."""
        if self.enabled and "auth_token_refresh_total" in self.metrics:
            self.metrics["auth_token_refresh_total"].labels(
                agent_id=agent_id, auth_type=auth_type, status=status
            ).inc()

    def record_security_event(
        self, agent_id: str, event_type: str, severity: str
    ) -> None:
        """Record a security event."""
        if self.enabled and "security_events_total" in self.metrics:
            self.metrics["security_events_total"].labels(
                agent_id=agent_id, event_type=event_type, severity=severity
            ).inc()

    def record_validation_error(
        self, agent_id: str, validation_type: str, field: str
    ) -> None:
        """Record a validation error."""
        if self.enabled and "validation_errors_total" in self.metrics:
            self.metrics["validation_errors_total"].labels(
                agent_id=agent_id, validation_type=validation_type, field=field
            ).inc()

    def update_memory_usage(self, agent_id: str, bytes_used: int) -> None:
        """Update memory usage gauge."""
        if self.enabled and "memory_usage_bytes" in self.metrics:
            self.metrics["memory_usage_bytes"].labels(agent_id=agent_id).set(bytes_used)

    def update_cpu_usage(self, agent_id: str, cpu_percent: float) -> None:
        """Update CPU usage gauge."""
        if self.enabled and "cpu_usage_percent" in self.metrics:
            self.metrics["cpu_usage_percent"].labels(agent_id=agent_id).set(cpu_percent)

    def update_uptime(self, agent_id: str, uptime_seconds: float) -> None:
        """Update agent uptime."""
        if self.enabled and "agent_uptime_seconds" in self.metrics:
            self.metrics["agent_uptime_seconds"].labels(agent_id=agent_id).set(
                uptime_seconds
            )

    def set_agent_info(
        self, agent_id: str, version: str, protocol_version: str, **kwargs: Any
    ) -> None:
        """Set agent information."""
        if self.enabled and "agent_info" in self.metrics:
            info_dict = {
                "agent_id": agent_id,
                "version": version,
                "protocol_version": protocol_version,
                **kwargs,
            }
            self.metrics["agent_info"].info(info_dict)

    def record_custom_metric(self, event: MetricEvent) -> None:
        """Record a custom metric event."""
        self.custom_metrics.append(event)

        # If we have a custom metric with the same name, update it
        if self.enabled and event.name in self.metrics:
            metric = self.metrics[event.name]

            if event.metric_type == "counter":
                metric.labels(**event.labels).inc(event.value)
            elif event.metric_type == "gauge":
                metric.labels(**event.labels).set(event.value)
            elif event.metric_type == "histogram":
                metric.labels(**event.labels).observe(event.value)

    @asynccontextmanager
    async def trace_operation(
        self, operation_name: str, agent_id: str, **attributes: Any
    ) -> Any:
        """Context manager for tracing operations with OpenTelemetry."""
        if not self.tracer:
            yield None
            return

        # Absicherung: tracer kann in Tests ein einfacher Mock ohne Methode sein
        start_span = getattr(self.tracer, "start_as_current_span", None)
        if start_span is None:
            # Kein echtes Tracing verfügbar
            start_time = time.time()
            try:
                yield None
            finally:
                _ = time.time() - start_time
            return

        with start_span(operation_name) as span:
            # Set attributes
            span.set_attribute("agent_id", agent_id)
            for key, value in attributes.items():
                span.set_attribute(key, str(value))

            start_time = time.time()

            try:
                yield span
                span.set_status(Status(StatusCode.OK))
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise
            finally:
                duration = time.time() - start_time
                span.set_attribute("duration_seconds", duration)

    def get_prometheus_metrics(self) -> str:
        """Get Prometheus metrics in text format."""
        if not self.enabled or self.registry is None:
            return "# Prometheus not available\n"

        data: bytes = generate_latest(self.registry)
        return data.decode("utf-8")

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of current metrics."""
        summary = {
            "prometheus_enabled": self.enabled,
            "opentelemetry_enabled": OPENTELEMETRY_AVAILABLE,
            "custom_metrics_count": len(self.custom_metrics),
            "registered_metrics": list(self.metrics.keys()) if self.enabled else [],
        }

        return summary


# Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


def initialize_metrics(
    registry: Optional[CollectorRegistry] = None,
) -> MetricsCollector:
    """Initialize the global metrics collector.

    Args:
        registry: Optional Prometheus registry

    Returns:
        Initialized metrics collector
    """
    global _metrics_collector
    _metrics_collector = MetricsCollector(registry)
    return _metrics_collector


# Convenience functions for common metrics
def record_request_metric(
    agent_id: str, method: str, status: str, duration: float, protocol: str = "unknown"
) -> None:
    """Record a request metric."""
    get_metrics_collector().record_request(agent_id, method, status, duration, protocol)


def record_connection_metric(agent_id: str, protocol: str, status: str) -> None:
    """Record a connection metric."""
    get_metrics_collector().record_connection(agent_id, protocol, status)


def record_security_metric(
    agent_id: str, event_type: str, severity: str = "info"
) -> None:
    """Record a security metric."""
    get_metrics_collector().record_security_event(agent_id, event_type, severity)


async def trace_async_operation(
    operation_name: str, agent_id: str, **attributes: Any
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator for tracing async operations."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            async with get_metrics_collector().trace_operation(
                operation_name, agent_id, **attributes
            ):
                return await func(*args, **kwargs)

        return wrapper

    return decorator
