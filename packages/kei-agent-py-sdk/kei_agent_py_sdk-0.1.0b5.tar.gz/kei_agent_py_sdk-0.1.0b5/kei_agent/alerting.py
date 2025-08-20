# kei_agent/alerting.py
"""
Alerting and notification system for KEI-Agent Python SDK.

This module provides:
- Multi-channel alert notifications (email, Slack, webhooks)
- Alert escalation and routing based on severity
- Integration with monitoring platforms (PagerDuty, Grafana)
- Alert suppression and deduplication
- Incident management and tracking
"""

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any
import logging

try:
    import aiohttp

    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

from .error_aggregation import ErrorEvent, ErrorSeverity

logger = logging.getLogger(__name__)


class NotificationChannel(Enum):
    """Notification channel types."""

    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    PAGERDUTY = "pagerduty"
    TEAMS = "teams"
    DISCORD = "discord"


@dataclass
class NotificationConfig:
    """Configuration for notification channels."""

    channel: NotificationChannel
    enabled: bool = True
    config: Dict[str, Any] = None
    severity_filter: List[ErrorSeverity] = None

    def __post_init__(self):
        if self.config is None:
            self.config = {}
        if self.severity_filter is None:
            self.severity_filter = list(ErrorSeverity)


class NotificationHandler(ABC):
    """Abstract base class for notification handlers."""

    def __init__(self, config: NotificationConfig):
        """Initialize notification handler.

        Args:
            config: Notification configuration
        """
        self.config = config
        self.enabled = config.enabled

    @abstractmethod
    async def send_notification(self, alert_name: str, error_event: ErrorEvent) -> bool:
        """Send notification for an alert.

        Args:
            alert_name: Name of the triggered alert
            error_event: Error event that triggered the alert

        Returns:
            True if notification was sent successfully
        """
        pass

    def should_notify(self, error_event: ErrorEvent) -> bool:
        """Check if notification should be sent for this error.

        Args:
            error_event: Error event to check

        Returns:
            True if notification should be sent
        """
        if not self.enabled:
            return False

        return error_event.severity in self.config.severity_filter


class WebhookNotificationHandler(NotificationHandler):
    """Webhook notification handler."""

    async def send_notification(self, alert_name: str, error_event: ErrorEvent) -> bool:
        """Send webhook notification."""
        if not AIOHTTP_AVAILABLE:
            logger.error("aiohttp not available for webhook notifications")
            return False

        webhook_url = self.config.config.get("url")
        if not webhook_url:
            logger.error("Webhook URL not configured")
            return False

        payload = {
            "alert_name": alert_name,
            "timestamp": error_event.timestamp,
            "severity": error_event.severity.value,
            "agent_id": error_event.agent_id,
            "error_type": error_event.error_type,
            "error_message": error_event.error_message,
            "category": error_event.category.value,
            "correlation_id": error_event.correlation_id,
            "context": error_event.context,
        }

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "KEI-Agent-SDK-Alerting/1.0",
        }

        # Add custom headers if configured
        custom_headers = self.config.config.get("headers", {})
        headers.update(custom_headers)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    webhook_url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    if response.status < 400:
                        logger.info(
                            f"Webhook notification sent successfully: {alert_name}"
                        )
                        return True
                    else:
                        logger.error(f"Webhook notification failed: {response.status}")
                        return False

        except Exception as e:
            logger.error(f"Error sending webhook notification: {e}")
            return False


class SlackNotificationHandler(NotificationHandler):
    """Slack notification handler."""

    async def send_notification(self, alert_name: str, error_event: ErrorEvent) -> bool:
        """Send Slack notification."""
        if not AIOHTTP_AVAILABLE:
            logger.error("aiohttp not available for Slack notifications")
            return False

        webhook_url = self.config.config.get("webhook_url")
        if not webhook_url:
            logger.error("Slack webhook URL not configured")
            return False

        # Format severity with emoji
        severity_emoji = {
            ErrorSeverity.LOW: "🟡",
            ErrorSeverity.MEDIUM: "🟠",
            ErrorSeverity.HIGH: "🔴",
            ErrorSeverity.CRITICAL: "🚨",
        }

        # Create Slack message
        message = {
            "text": f"{severity_emoji.get(error_event.severity, '⚠️')} Alert: {alert_name}",
            "attachments": [
                {
                    "color": self._get_color_for_severity(error_event.severity),
                    "fields": [
                        {
                            "title": "Agent ID",
                            "value": error_event.agent_id,
                            "short": True,
                        },
                        {
                            "title": "Error Type",
                            "value": error_event.error_type,
                            "short": True,
                        },
                        {
                            "title": "Severity",
                            "value": error_event.severity.value.upper(),
                            "short": True,
                        },
                        {
                            "title": "Category",
                            "value": error_event.category.value,
                            "short": True,
                        },
                        {
                            "title": "Message",
                            "value": error_event.error_message,
                            "short": False,
                        },
                    ],
                    "footer": "KEI-Agent SDK",
                    "ts": int(error_event.timestamp),
                }
            ],
        }

        # Add correlation ID if available
        if error_event.correlation_id:
            message["attachments"][0]["fields"].append(
                {
                    "title": "Correlation ID",
                    "value": error_event.correlation_id,
                    "short": True,
                }
            )

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    webhook_url, json=message, timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status < 400:
                        logger.info(
                            f"Slack notification sent successfully: {alert_name}"
                        )
                        return True
                    else:
                        logger.error(f"Slack notification failed: {response.status}")
                        return False

        except Exception as e:
            logger.error(f"Error sending Slack notification: {e}")
            return False

    def _get_color_for_severity(self, severity: ErrorSeverity) -> str:
        """Get color code for severity level."""
        color_map = {
            ErrorSeverity.LOW: "#36a64f",  # Green
            ErrorSeverity.MEDIUM: "#ff9500",  # Orange
            ErrorSeverity.HIGH: "#ff0000",  # Red
            ErrorSeverity.CRITICAL: "#8b0000",  # Dark Red
        }
        return color_map.get(severity, "#808080")  # Gray default


class PagerDutyNotificationHandler(NotificationHandler):
    """PagerDuty notification handler."""

    async def send_notification(self, alert_name: str, error_event: ErrorEvent) -> bool:
        """Send PagerDuty notification."""
        if not AIOHTTP_AVAILABLE:
            logger.error("aiohttp not available for PagerDuty notifications")
            return False

        integration_key = self.config.config.get("integration_key")
        if not integration_key:
            logger.error("PagerDuty integration key not configured")
            return False

        # Create PagerDuty event
        event = {
            "routing_key": integration_key,
            "event_action": "trigger",
            "dedup_key": f"{error_event.agent_id}_{alert_name}",
            "payload": {
                "summary": f"{alert_name}: {error_event.error_message}",
                "source": error_event.agent_id,
                "severity": self._map_severity_to_pagerduty(error_event.severity),
                "component": "kei-agent-sdk",
                "group": error_event.category.value,
                "class": error_event.error_type,
                "custom_details": {
                    "error_id": error_event.error_id,
                    "correlation_id": error_event.correlation_id,
                    "protocol": error_event.protocol,
                    "context": error_event.context,
                },
            },
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://events.pagerduty.com/v2/enqueue",
                    json=event,
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    if response.status < 400:
                        logger.info(
                            f"PagerDuty notification sent successfully: {alert_name}"
                        )
                        return True
                    else:
                        logger.error(
                            f"PagerDuty notification failed: {response.status}"
                        )
                        return False

        except Exception as e:
            logger.error(f"Error sending PagerDuty notification: {e}")
            return False

    def _map_severity_to_pagerduty(self, severity: ErrorSeverity) -> str:
        """Map error severity to PagerDuty severity."""
        mapping = {
            ErrorSeverity.LOW: "info",
            ErrorSeverity.MEDIUM: "warning",
            ErrorSeverity.HIGH: "error",
            ErrorSeverity.CRITICAL: "critical",
        }
        return mapping.get(severity, "warning")


class AlertManager:
    """Manages alert notifications and routing."""

    def __init__(self):
        """Initialize alert manager."""
        self.notification_handlers: List[NotificationHandler] = []
        self.alert_history: List[Dict[str, Any]] = []
        self.suppressed_alerts: Dict[str, float] = {}
        self.suppression_window = 300  # 5 minutes default

    def add_notification_handler(self, handler: NotificationHandler) -> None:
        """Add a notification handler.

        Args:
            handler: Notification handler to add
        """
        self.notification_handlers.append(handler)
        logger.info(f"Added notification handler: {handler.__class__.__name__}")

    def configure_webhook(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        severity_filter: Optional[List[ErrorSeverity]] = None,
    ) -> None:
        """Configure webhook notifications.

        Args:
            url: Webhook URL
            headers: Optional custom headers
            severity_filter: List of severities to notify for
        """
        config = NotificationConfig(
            channel=NotificationChannel.WEBHOOK,
            config={"url": url, "headers": headers or {}},
            severity_filter=severity_filter or list(ErrorSeverity),
        )
        handler = WebhookNotificationHandler(config)
        self.add_notification_handler(handler)

    def configure_slack(
        self, webhook_url: str, severity_filter: Optional[List[ErrorSeverity]] = None
    ) -> None:
        """Configure Slack notifications.

        Args:
            webhook_url: Slack webhook URL
            severity_filter: List of severities to notify for
        """
        config = NotificationConfig(
            channel=NotificationChannel.SLACK,
            config={"webhook_url": webhook_url},
            severity_filter=severity_filter
            or [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL],
        )
        handler = SlackNotificationHandler(config)
        self.add_notification_handler(handler)

    def configure_pagerduty(
        self,
        integration_key: str,
        severity_filter: Optional[List[ErrorSeverity]] = None,
    ) -> None:
        """Configure PagerDuty notifications.

        Args:
            integration_key: PagerDuty integration key
            severity_filter: List of severities to notify for
        """
        config = NotificationConfig(
            channel=NotificationChannel.PAGERDUTY,
            config={"integration_key": integration_key},
            severity_filter=severity_filter or [ErrorSeverity.CRITICAL],
        )
        handler = PagerDutyNotificationHandler(config)
        self.add_notification_handler(handler)

    async def handle_alert(self, alert_name: str, error_event: ErrorEvent) -> None:
        """Handle an alert by sending notifications.

        Args:
            alert_name: Name of the alert
            error_event: Error event that triggered the alert
        """
        # Check if alert is suppressed
        if self._is_alert_suppressed(alert_name):
            logger.debug(f"Alert suppressed: {alert_name}")
            return

        # Record alert in history
        self.alert_history.append(
            {
                "alert_name": alert_name,
                "error_event": error_event.to_dict(),
                "timestamp": time.time(),
                "handlers_notified": [],
            }
        )

        # Send notifications
        for handler in self.notification_handlers:
            if handler.should_notify(error_event):
                try:
                    success = await handler.send_notification(alert_name, error_event)
                    if success:
                        self.alert_history[-1]["handlers_notified"].append(
                            handler.__class__.__name__
                        )
                except Exception as e:
                    logger.error(
                        f"Error in notification handler {handler.__class__.__name__}: {e}"
                    )

        # Suppress similar alerts
        self._suppress_alert(alert_name)

    def _is_alert_suppressed(self, alert_name: str) -> bool:
        """Check if an alert is currently suppressed.

        Args:
            alert_name: Name of the alert

        Returns:
            True if alert is suppressed
        """
        if alert_name in self.suppressed_alerts:
            suppressed_until = self.suppressed_alerts[alert_name]
            if time.time() < suppressed_until:
                return True
            else:
                # Remove expired suppression
                del self.suppressed_alerts[alert_name]

        return False

    def _suppress_alert(self, alert_name: str) -> None:
        """Suppress an alert for the configured window.

        Args:
            alert_name: Name of the alert to suppress
        """
        self.suppressed_alerts[alert_name] = time.time() + self.suppression_window

    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alert statistics.

        Returns:
            Dictionary with alert statistics
        """
        recent_alerts = [
            alert
            for alert in self.alert_history
            if alert["timestamp"] >= time.time() - 3600  # Last hour
        ]

        return {
            "total_alerts": len(self.alert_history),
            "recent_alerts": len(recent_alerts),
            "active_handlers": len(self.notification_handlers),
            "suppressed_alerts": len(self.suppressed_alerts),
            "suppression_window_seconds": self.suppression_window,
        }


# Global alert manager instance
_alert_manager: Optional[AlertManager] = None


def get_alert_manager() -> AlertManager:
    """Get the global alert manager instance."""
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = AlertManager()
    return _alert_manager


def initialize_alerting() -> AlertManager:
    """Initialize the global alert manager.

    Returns:
        Initialized alert manager
    """
    global _alert_manager
    _alert_manager = AlertManager()
    return _alert_manager
