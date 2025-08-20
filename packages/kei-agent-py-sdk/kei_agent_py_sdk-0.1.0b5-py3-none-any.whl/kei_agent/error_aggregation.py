# kei_agent/error_aggregation.py
"""
Centralized error aggregation and alerting system for KEI-Agent Python SDK.

This module provides:
- Structured error collection and categorization
- Real-time error rate monitoring and alerting
- Error trend analysis and anomaly detection
- Integration with monitoring systems (Prometheus/Grafana)
- Automated incident response and notification routing
"""

import time
import traceback
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
import logging

from .metrics import get_metrics_collector, MetricEvent

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for classification."""

    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    VALIDATION = "validation"
    NETWORK = "network"
    PROTOCOL = "protocol"
    SECURITY = "security"
    PERFORMANCE = "performance"
    CONFIGURATION = "configuration"
    SYSTEM = "system"
    BUSINESS_LOGIC = "business_logic"
    UNKNOWN = "unknown"


@dataclass
class ErrorEvent:
    """Represents an error event with metadata."""

    error_id: str
    timestamp: float
    agent_id: str
    error_type: str
    error_message: str
    category: ErrorCategory
    severity: ErrorSeverity
    context: Dict[str, Any] = field(default_factory=dict)
    stack_trace: Optional[str] = None
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    protocol: Optional[str] = None
    endpoint: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert error event to dictionary."""
        return {
            "error_id": self.error_id,
            "timestamp": self.timestamp,
            "agent_id": self.agent_id,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "category": self.category.value,
            "severity": self.severity.value,
            "context": self.context,
            "stack_trace": self.stack_trace,
            "correlation_id": self.correlation_id,
            "user_id": self.user_id,
            "request_id": self.request_id,
            "protocol": self.protocol,
            "endpoint": self.endpoint,
        }


@dataclass
class AlertRule:
    """Defines alerting rules for error conditions."""

    name: str
    description: str
    condition: Callable[[List[ErrorEvent]], bool]
    severity: ErrorSeverity
    cooldown_minutes: int = 15
    enabled: bool = True
    last_triggered: Optional[float] = None

    def should_trigger(self, errors: List[ErrorEvent]) -> bool:
        """Check if alert should trigger based on current errors."""
        if not self.enabled:
            return False

        # Check cooldown period
        if self.last_triggered:
            cooldown_seconds = self.cooldown_minutes * 60
            if time.time() - self.last_triggered < cooldown_seconds:
                return False

        return self.condition(errors)

    def trigger(self) -> None:
        """Mark alert as triggered."""
        self.last_triggered = time.time()


class ErrorAggregator:
    """Aggregates and analyzes errors for alerting and monitoring."""

    def __init__(self, window_minutes: int = 60, max_events: int = 10000):
        """Initialize error aggregator.

        Args:
            window_minutes: Time window for error analysis in minutes
            max_events: Maximum number of events to keep in memory
        """
        self.window_minutes = window_minutes
        self.max_events = max_events
        self.errors: deque = deque(maxlen=max_events)
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.category_counts: Dict[ErrorCategory, int] = defaultdict(int)
        self.severity_counts: Dict[ErrorSeverity, int] = defaultdict(int)
        self.agent_error_counts: Dict[str, int] = defaultdict(int)

        # Alert rules
        self.alert_rules: List[AlertRule] = []
        self.alert_handlers: List[Callable[[str, ErrorEvent], None]] = []

        # Metrics collector
        self.metrics_collector = get_metrics_collector()

        # Initialize default alert rules
        self._initialize_default_alert_rules()

    def add_error(self, error: ErrorEvent) -> None:
        """Add an error event to the aggregator.

        Args:
            error: Error event to add
        """
        # Add to deque
        self.errors.append(error)

        # Update counters
        self.error_counts[error.error_type] += 1
        self.category_counts[error.category] += 1
        self.severity_counts[error.severity] += 1
        self.agent_error_counts[error.agent_id] += 1

        # Record metrics
        self._record_error_metrics(error)

        # Check alert rules
        self._check_alert_rules()

        logger.debug(f"Added error event: {error.error_id}")

    def _record_error_metrics(self, error: ErrorEvent) -> None:
        """Record error metrics for monitoring.

        Args:
            error: Error event to record
        """
        # Record error count metric
        self.metrics_collector.record_custom_metric(
            MetricEvent(
                name="error_events_total",
                value=1,
                labels={
                    "agent_id": error.agent_id,
                    "error_type": error.error_type,
                    "category": error.category.value,
                    "severity": error.severity.value,
                    "protocol": error.protocol or "unknown",
                },
                metric_type="counter",
            )
        )

        # Record error rate metric
        recent_errors = self._get_recent_errors(minutes=5)
        error_rate = len(recent_errors) / 5.0  # errors per minute

        self.metrics_collector.record_custom_metric(
            MetricEvent(
                name="error_rate_per_minute",
                value=error_rate,
                labels={"agent_id": error.agent_id},
                metric_type="gauge",
            )
        )

    def _get_recent_errors(self, minutes: int = None) -> List[ErrorEvent]:
        """Get errors from recent time window.

        Args:
            minutes: Time window in minutes (default: window_minutes)

        Returns:
            List of recent error events
        """
        if minutes is None:
            minutes = self.window_minutes

        cutoff_time = time.time() - (minutes * 60)
        return [error for error in self.errors if error.timestamp >= cutoff_time]

    def _initialize_default_alert_rules(self) -> None:
        """Initialize default alerting rules."""

        # High error rate alert
        def high_error_rate(errors: List[ErrorEvent]) -> bool:
            recent_errors = [
                e for e in errors if e.timestamp >= time.time() - 300
            ]  # 5 minutes
            return len(recent_errors) > 50  # More than 50 errors in 5 minutes

        self.alert_rules.append(
            AlertRule(
                name="high_error_rate",
                description="High error rate detected",
                condition=high_error_rate,
                severity=ErrorSeverity.HIGH,
                cooldown_minutes=10,
            )
        )

        # Critical error alert
        def critical_errors(errors: List[ErrorEvent]) -> bool:
            recent_errors = [
                e for e in errors if e.timestamp >= time.time() - 60
            ]  # 1 minute
            critical_errors = [
                e for e in recent_errors if e.severity == ErrorSeverity.CRITICAL
            ]
            return len(critical_errors) > 0

        self.alert_rules.append(
            AlertRule(
                name="critical_error",
                description="Critical error detected",
                condition=critical_errors,
                severity=ErrorSeverity.CRITICAL,
                cooldown_minutes=5,
            )
        )

        # Authentication failure spike
        def auth_failure_spike(errors: List[ErrorEvent]) -> bool:
            recent_errors = [
                e for e in errors if e.timestamp >= time.time() - 300
            ]  # 5 minutes
            auth_errors = [
                e for e in recent_errors if e.category == ErrorCategory.AUTHENTICATION
            ]
            return len(auth_errors) > 10  # More than 10 auth failures in 5 minutes

        self.alert_rules.append(
            AlertRule(
                name="auth_failure_spike",
                description="Authentication failure spike detected",
                condition=auth_failure_spike,
                severity=ErrorSeverity.MEDIUM,
                cooldown_minutes=15,
            )
        )

        # Security event alert
        def security_events(errors: List[ErrorEvent]) -> bool:
            recent_errors = [
                e for e in errors if e.timestamp >= time.time() - 60
            ]  # 1 minute
            security_errors = [
                e for e in recent_errors if e.category == ErrorCategory.SECURITY
            ]
            return len(security_errors) > 0

        self.alert_rules.append(
            AlertRule(
                name="security_event",
                description="Security event detected",
                condition=security_events,
                severity=ErrorSeverity.HIGH,
                cooldown_minutes=5,
            )
        )

    def _check_alert_rules(self) -> None:
        """Check all alert rules against recent errors."""
        recent_errors = self._get_recent_errors()

        for rule in self.alert_rules:
            if rule.should_trigger(recent_errors):
                self._trigger_alert(rule, recent_errors)

    def _trigger_alert(self, rule: AlertRule, errors: List[ErrorEvent]) -> None:
        """Trigger an alert.

        Args:
            rule: Alert rule that triggered
            errors: Recent errors that caused the trigger
        """
        rule.trigger()

        # Create alert event
        alert_event = ErrorEvent(
            error_id=f"alert_{rule.name}_{int(time.time())}",
            timestamp=time.time(),
            agent_id="system",
            error_type="alert",
            error_message=f"Alert triggered: {rule.description}",
            category=ErrorCategory.SYSTEM,
            severity=rule.severity,
            context={
                "rule_name": rule.name,
                "rule_description": rule.description,
                "triggered_by_count": len(errors),
                "recent_errors": [
                    e.error_id for e in errors[-10:]
                ],  # Last 10 error IDs
            },
        )

        # Notify alert handlers
        for handler in self.alert_handlers:
            try:
                handler(rule.name, alert_event)
            except Exception as e:
                logger.error(f"Error in alert handler: {e}")

        logger.warning(f"Alert triggered: {rule.name} - {rule.description}")

    def add_alert_rule(self, rule: AlertRule) -> None:
        """Add a custom alert rule.

        Args:
            rule: Alert rule to add
        """
        self.alert_rules.append(rule)
        logger.info(f"Added alert rule: {rule.name}")

    def add_alert_handler(self, handler: Callable[[str, ErrorEvent], None]) -> None:
        """Add an alert handler function.

        Args:
            handler: Function to handle alerts (rule_name, alert_event)
        """
        self.alert_handlers.append(handler)
        logger.info("Added alert handler")

    def get_error_statistics(self) -> Dict[str, Any]:
        """Get comprehensive error statistics.

        Returns:
            Dictionary with error statistics
        """
        recent_errors = self._get_recent_errors()

        # Calculate error rates
        error_rate_1min = (
            len([e for e in recent_errors if e.timestamp >= time.time() - 60]) / 1.0
        )
        error_rate_5min = (
            len([e for e in recent_errors if e.timestamp >= time.time() - 300]) / 5.0
        )
        error_rate_15min = (
            len([e for e in recent_errors if e.timestamp >= time.time() - 900]) / 15.0
        )

        # Top error types
        error_type_counts = defaultdict(int)
        for error in recent_errors:
            error_type_counts[error.error_type] += 1

        top_error_types = sorted(
            error_type_counts.items(), key=lambda x: x[1], reverse=True
        )[:10]

        # Category distribution
        category_distribution = {}
        for category in ErrorCategory:
            count = len([e for e in recent_errors if e.category == category])
            if count > 0:
                category_distribution[category.value] = count

        # Severity distribution
        severity_distribution = {}
        for severity in ErrorSeverity:
            count = len([e for e in recent_errors if e.severity == severity])
            if count > 0:
                severity_distribution[severity.value] = count

        # Agent error distribution
        agent_distribution = defaultdict(int)
        for error in recent_errors:
            agent_distribution[error.agent_id] += 1

        return {
            "total_errors": len(self.errors),
            "recent_errors": len(recent_errors),
            "error_rates": {
                "per_minute_1min": error_rate_1min,
                "per_minute_5min": error_rate_5min,
                "per_minute_15min": error_rate_15min,
            },
            "top_error_types": top_error_types,
            "category_distribution": category_distribution,
            "severity_distribution": severity_distribution,
            "agent_distribution": dict(agent_distribution),
            "active_alert_rules": len([r for r in self.alert_rules if r.enabled]),
            "window_minutes": self.window_minutes,
        }

    def get_error_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Analyze error trends over time.

        Args:
            hours: Number of hours to analyze

        Returns:
            Dictionary with trend analysis
        """
        cutoff_time = time.time() - (hours * 3600)
        trend_errors = [e for e in self.errors if e.timestamp >= cutoff_time]

        # Group errors by hour
        hourly_counts = defaultdict(int)
        for error in trend_errors:
            hour = int(error.timestamp // 3600)
            hourly_counts[hour] += 1

        # Calculate trend direction
        if len(hourly_counts) >= 2:
            recent_hours = sorted(hourly_counts.keys())[-2:]
            if len(recent_hours) == 2:
                trend_direction = (
                    "increasing"
                    if hourly_counts[recent_hours[1]] > hourly_counts[recent_hours[0]]
                    else "decreasing"
                )
            else:
                trend_direction = "stable"
        else:
            trend_direction = "insufficient_data"

        return {
            "hours_analyzed": hours,
            "total_errors": len(trend_errors),
            "hourly_distribution": dict(hourly_counts),
            "trend_direction": trend_direction,
            "peak_hour": max(hourly_counts.items(), key=lambda x: x[1])[0]
            if hourly_counts
            else None,
            "average_per_hour": len(trend_errors) / hours if hours > 0 else 0,
        }


# Global error aggregator instance
_error_aggregator: Optional[ErrorAggregator] = None


def get_error_aggregator() -> ErrorAggregator:
    """Get the global error aggregator instance."""
    global _error_aggregator
    if _error_aggregator is None:
        _error_aggregator = ErrorAggregator()
    return _error_aggregator


def initialize_error_aggregation(
    window_minutes: int = 60, max_events: int = 10000
) -> ErrorAggregator:
    """Initialize the global error aggregator.

    Args:
        window_minutes: Time window for error analysis
        max_events: Maximum number of events to keep

    Returns:
        Initialized error aggregator
    """
    global _error_aggregator
    _error_aggregator = ErrorAggregator(window_minutes, max_events)
    return _error_aggregator


def record_error(
    agent_id: str,
    error: Exception,
    category: ErrorCategory = ErrorCategory.UNKNOWN,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    context: Optional[Dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
) -> str:
    """Record an error event.

    Args:
        agent_id: ID of the agent where error occurred
        error: Exception that occurred
        category: Error category
        severity: Error severity
        context: Additional context information
        correlation_id: Correlation ID for request tracking

    Returns:
        Error event ID
    """
    import uuid

    error_id = str(uuid.uuid4())

    error_event = ErrorEvent(
        error_id=error_id,
        timestamp=time.time(),
        agent_id=agent_id,
        error_type=type(error).__name__,
        error_message=str(error),
        category=category,
        severity=severity,
        context=context or {},
        stack_trace=traceback.format_exc(),
        correlation_id=correlation_id,
    )

    get_error_aggregator().add_error(error_event)
    return error_id


# Convenience functions for common error categories
def record_authentication_error(agent_id: str, error: Exception, **kwargs) -> str:
    """Record an authentication error."""
    return record_error(
        agent_id, error, ErrorCategory.AUTHENTICATION, ErrorSeverity.HIGH, **kwargs
    )


def record_security_error(agent_id: str, error: Exception, **kwargs) -> str:
    """Record a security error."""
    return record_error(
        agent_id, error, ErrorCategory.SECURITY, ErrorSeverity.CRITICAL, **kwargs
    )


def record_network_error(agent_id: str, error: Exception, **kwargs) -> str:
    """Record a network error."""
    return record_error(
        agent_id, error, ErrorCategory.NETWORK, ErrorSeverity.MEDIUM, **kwargs
    )


def record_validation_error(agent_id: str, error: Exception, **kwargs) -> str:
    """Record a validation error."""
    return record_error(
        agent_id, error, ErrorCategory.VALIDATION, ErrorSeverity.LOW, **kwargs
    )
