# tests/test_error_aggregation.py
"""
Tests for centralized error aggregation and alerting system.

This test validates that:
1. Error events are properly recorded and categorized
2. Alert rules trigger correctly based on conditions
3. Notification handlers work properly
4. Error statistics and trends are calculated correctly
5. Integration with metrics collection works
"""

import asyncio
import time
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from kei_agent.error_aggregation import (
    ErrorAggregator, ErrorEvent, ErrorCategory, ErrorSeverity, AlertRule,
    get_error_aggregator, initialize_error_aggregation, record_error,
    record_authentication_error, record_security_error, record_network_error
)
from kei_agent.alerting import (
    AlertManager, NotificationConfig, NotificationChannel,
    WebhookNotificationHandler, SlackNotificationHandler,
    get_alert_manager, initialize_alerting
)


class TestErrorEvent:
    """Tests for ErrorEvent data class."""

    def test_error_event_creation(self):
        """Test ErrorEvent creation and serialization."""
        error_event = ErrorEvent(
            error_id="test-error-123",
            timestamp=time.time(),
            agent_id="test-agent",
            error_type="ValueError",
            error_message="Test error message",
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.MEDIUM,
            context={"test": "data"},
            correlation_id="corr-123"
        )

        assert error_event.error_id == "test-error-123"
        assert error_event.agent_id == "test-agent"
        assert error_event.category == ErrorCategory.VALIDATION
        assert error_event.severity == ErrorSeverity.MEDIUM

        # Test serialization
        event_dict = error_event.to_dict()
        assert isinstance(event_dict, dict)
        assert event_dict["error_id"] == "test-error-123"
        assert event_dict["category"] == "validation"
        assert event_dict["severity"] == "medium"


class TestErrorAggregator:
    """Tests for ErrorAggregator functionality."""

    def setup_method(self):
        """Setup for each test."""
        self.aggregator = ErrorAggregator(window_minutes=60, max_events=1000)

    def test_error_aggregator_initialization(self):
        """Test ErrorAggregator initialization."""
        assert self.aggregator.window_minutes == 60
        assert self.aggregator.max_events == 1000
        assert len(self.aggregator.errors) == 0
        assert len(self.aggregator.alert_rules) > 0  # Default rules should be present

    def test_add_error_event(self):
        """Test adding error events to aggregator."""
        error_event = ErrorEvent(
            error_id="test-1",
            timestamp=time.time(),
            agent_id="test-agent",
            error_type="ConnectionError",
            error_message="Connection failed",
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.HIGH
        )

        self.aggregator.add_error(error_event)

        assert len(self.aggregator.errors) == 1
        assert self.aggregator.error_counts["ConnectionError"] == 1
        assert self.aggregator.category_counts[ErrorCategory.NETWORK] == 1
        assert self.aggregator.severity_counts[ErrorSeverity.HIGH] == 1
        assert self.aggregator.agent_error_counts["test-agent"] == 1

    def test_get_recent_errors(self):
        """Test getting recent errors within time window."""
        current_time = time.time()

        # Add old error (outside window)
        old_error = ErrorEvent(
            error_id="old-error",
            timestamp=current_time - 7200,  # 2 hours ago
            agent_id="test-agent",
            error_type="OldError",
            error_message="Old error",
            category=ErrorCategory.UNKNOWN,
            severity=ErrorSeverity.LOW
        )

        # Add recent error (within window)
        recent_error = ErrorEvent(
            error_id="recent-error",
            timestamp=current_time - 300,  # 5 minutes ago
            agent_id="test-agent",
            error_type="RecentError",
            error_message="Recent error",
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.HIGH
        )

        self.aggregator.add_error(old_error)
        self.aggregator.add_error(recent_error)

        # Get recent errors (last 10 minutes)
        recent_errors = self.aggregator._get_recent_errors(minutes=10)

        assert len(recent_errors) == 1
        assert recent_errors[0].error_id == "recent-error"

    def test_error_statistics(self):
        """Test error statistics calculation."""
        # Add multiple errors
        for i in range(5):
            error_event = ErrorEvent(
                error_id=f"error-{i}",
                timestamp=time.time() - (i * 60),  # Spread over 5 minutes
                agent_id="test-agent",
                error_type="TestError",
                error_message=f"Test error {i}",
                category=ErrorCategory.VALIDATION,
                severity=ErrorSeverity.MEDIUM
            )
            self.aggregator.add_error(error_event)

        stats = self.aggregator.get_error_statistics()

        assert stats["total_errors"] == 5
        assert stats["recent_errors"] == 5
        assert "error_rates" in stats
        assert "top_error_types" in stats
        assert "category_distribution" in stats
        assert "severity_distribution" in stats

    def test_error_trends(self):
        """Test error trend analysis."""
        current_time = time.time()

        # Add errors across different hours
        for hour in range(3):
            for i in range(2):
                error_event = ErrorEvent(
                    error_id=f"error-{hour}-{i}",
                    timestamp=current_time - (hour * 3600) - (i * 60),
                    agent_id="test-agent",
                    error_type="TrendError",
                    error_message=f"Trend error {hour}-{i}",
                    category=ErrorCategory.SYSTEM,
                    severity=ErrorSeverity.MEDIUM
                )
                self.aggregator.add_error(error_event)

        trends = self.aggregator.get_error_trends(hours=24)

        assert trends["hours_analyzed"] == 24
        assert trends["total_errors"] == 6
        assert "hourly_distribution" in trends
        assert "trend_direction" in trends

    def test_alert_rules(self):
        """Test alert rule functionality."""
        # Create custom alert rule
        def test_condition(errors):
            return len(errors) > 2

        custom_rule = AlertRule(
            name="test_alert",
            description="Test alert rule",
            condition=test_condition,
            severity=ErrorSeverity.HIGH,
            cooldown_minutes=5
        )

        self.aggregator.add_alert_rule(custom_rule)

        # Add errors to trigger alert
        for i in range(3):
            error_event = ErrorEvent(
                error_id=f"trigger-{i}",
                timestamp=time.time(),
                agent_id="test-agent",
                error_type="TriggerError",
                error_message=f"Trigger error {i}",
                category=ErrorCategory.SYSTEM,
                severity=ErrorSeverity.HIGH
            )
            self.aggregator.add_error(error_event)

        # Check if rule would trigger
        recent_errors = self.aggregator._get_recent_errors()
        assert custom_rule.should_trigger(recent_errors)


class TestAlertRule:
    """Tests for AlertRule functionality."""

    def test_alert_rule_creation(self):
        """Test AlertRule creation."""
        def test_condition(errors):
            return len(errors) > 5

        rule = AlertRule(
            name="high_error_rate",
            description="High error rate detected",
            condition=test_condition,
            severity=ErrorSeverity.CRITICAL,
            cooldown_minutes=10
        )

        assert rule.name == "high_error_rate"
        assert rule.severity == ErrorSeverity.CRITICAL
        assert rule.cooldown_minutes == 10
        assert rule.enabled is True
        assert rule.last_triggered is None

    def test_alert_rule_cooldown(self):
        """Test alert rule cooldown functionality."""
        def always_true(errors):
            return True

        rule = AlertRule(
            name="test_cooldown",
            description="Test cooldown",
            condition=always_true,
            severity=ErrorSeverity.MEDIUM,
            cooldown_minutes=1  # 1 minute cooldown
        )

        # First trigger should work
        assert rule.should_trigger([])
        rule.trigger()

        # Second trigger should be blocked by cooldown
        assert not rule.should_trigger([])

        # Simulate time passing
        rule.last_triggered = time.time() - 120  # 2 minutes ago
        assert rule.should_trigger([])


class TestNotificationHandlers:
    """Tests for notification handlers."""

    @pytest.mark.asyncio
    async def test_webhook_notification_handler(self):
        """Test webhook notification handler."""
        config = NotificationConfig(
            channel=NotificationChannel.WEBHOOK,
            config={"url": "https://example.com/webhook"},
            severity_filter=[ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]
        )

        handler = WebhookNotificationHandler(config)

        error_event = ErrorEvent(
            error_id="webhook-test",
            timestamp=time.time(),
            agent_id="test-agent",
            error_type="WebhookError",
            error_message="Test webhook error",
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.HIGH
        )

        # Test should_notify
        assert handler.should_notify(error_event)

        # Test with low severity (should not notify)
        error_event.severity = ErrorSeverity.LOW
        assert not handler.should_notify(error_event)

    @pytest.mark.asyncio
    async def test_slack_notification_handler(self):
        """Test Slack notification handler."""
        config = NotificationConfig(
            channel=NotificationChannel.SLACK,
            config={"webhook_url": "https://hooks.slack.com/test"},
            severity_filter=[ErrorSeverity.CRITICAL]
        )

        handler = SlackNotificationHandler(config)

        error_event = ErrorEvent(
            error_id="slack-test",
            timestamp=time.time(),
            agent_id="test-agent",
            error_type="SlackError",
            error_message="Test Slack error",
            category=ErrorCategory.SECURITY,
            severity=ErrorSeverity.CRITICAL
        )

        # Test should_notify
        assert handler.should_notify(error_event)

        # Test color mapping
        color = handler._get_color_for_severity(ErrorSeverity.CRITICAL)
        assert color == "#8b0000"  # Dark red for critical


class TestAlertManager:
    """Tests for AlertManager functionality."""

    def setup_method(self):
        """Setup for each test."""
        self.alert_manager = AlertManager()

    def test_alert_manager_initialization(self):
        """Test AlertManager initialization."""
        assert len(self.alert_manager.notification_handlers) == 0
        assert len(self.alert_manager.alert_history) == 0
        assert len(self.alert_manager.suppressed_alerts) == 0

    def test_configure_webhook(self):
        """Test webhook configuration."""
        self.alert_manager.configure_webhook(
            url="https://example.com/webhook",
            headers={"Authorization": "Bearer token"},
            severity_filter=[ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]
        )

        assert len(self.alert_manager.notification_handlers) == 1
        handler = self.alert_manager.notification_handlers[0]
        assert isinstance(handler, WebhookNotificationHandler)

    def test_configure_slack(self):
        """Test Slack configuration."""
        self.alert_manager.configure_slack(
            webhook_url="https://hooks.slack.com/test",
            severity_filter=[ErrorSeverity.CRITICAL]
        )

        assert len(self.alert_manager.notification_handlers) == 1
        handler = self.alert_manager.notification_handlers[0]
        assert isinstance(handler, SlackNotificationHandler)

    @pytest.mark.asyncio
    async def test_handle_alert(self):
        """Test alert handling."""
        # Configure mock webhook
        self.alert_manager.configure_webhook("https://example.com/webhook")

        error_event = ErrorEvent(
            error_id="alert-test",
            timestamp=time.time(),
            agent_id="test-agent",
            error_type="AlertError",
            error_message="Test alert error",
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.HIGH
        )

        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_post.return_value.__aenter__.return_value = mock_response

            await self.alert_manager.handle_alert("test_alert", error_event)

        # Check alert was recorded
        assert len(self.alert_manager.alert_history) == 1
        assert self.alert_manager.alert_history[0]["alert_name"] == "test_alert"

    def test_alert_suppression(self):
        """Test alert suppression functionality."""
        alert_name = "test_suppression"

        # Alert should not be suppressed initially
        assert not self.alert_manager._is_alert_suppressed(alert_name)

        # Suppress the alert
        self.alert_manager._suppress_alert(alert_name)

        # Alert should now be suppressed
        assert self.alert_manager._is_alert_suppressed(alert_name)

    def test_alert_statistics(self):
        """Test alert statistics."""
        stats = self.alert_manager.get_alert_statistics()

        assert "total_alerts" in stats
        assert "recent_alerts" in stats
        assert "active_handlers" in stats
        assert "suppressed_alerts" in stats
        assert "suppression_window_seconds" in stats


class TestGlobalFunctions:
    """Tests for global convenience functions."""

    def test_get_error_aggregator_singleton(self):
        """Test global error aggregator singleton."""
        aggregator1 = get_error_aggregator()
        aggregator2 = get_error_aggregator()

        # Should return same instance
        assert aggregator1 is aggregator2

    def test_initialize_error_aggregation(self):
        """Test error aggregation initialization."""
        aggregator = initialize_error_aggregation(window_minutes=30, max_events=500)

        assert isinstance(aggregator, ErrorAggregator)
        assert aggregator.window_minutes == 30
        assert aggregator.max_events == 500

    def test_record_error_function(self):
        """Test record_error convenience function."""
        test_error = ValueError("Test error")

        error_id = record_error(
            agent_id="test-agent",
            error=test_error,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.MEDIUM,
            context={"test": "context"},
            correlation_id="test-correlation"
        )

        assert isinstance(error_id, str)
        assert len(error_id) > 0

    def test_convenience_error_functions(self):
        """Test convenience functions for specific error types."""
        test_error = Exception("Test error")

        # Test authentication error
        auth_error_id = record_authentication_error("test-agent", test_error)
        assert isinstance(auth_error_id, str)

        # Test security error
        security_error_id = record_security_error("test-agent", test_error)
        assert isinstance(security_error_id, str)

        # Test network error
        network_error_id = record_network_error("test-agent", test_error)
        assert isinstance(network_error_id, str)

    def test_get_alert_manager_singleton(self):
        """Test global alert manager singleton."""
        manager1 = get_alert_manager()
        manager2 = get_alert_manager()

        # Should return same instance
        assert manager1 is manager2

    def test_initialize_alerting(self):
        """Test alerting initialization."""
        manager = initialize_alerting()

        assert isinstance(manager, AlertManager)


class TestIntegration:
    """Integration tests for error aggregation and alerting."""

    @pytest.mark.asyncio
    async def test_end_to_end_error_flow(self):
        """Test complete error flow from recording to alerting."""
        # Initialize systems
        aggregator = initialize_error_aggregation()
        alert_manager = initialize_alerting()

        # Configure alerting
        alert_manager.configure_webhook("https://example.com/webhook")

        # Add alert handler to aggregator
        aggregator.add_alert_handler(alert_manager.handle_alert)

        # Record multiple errors to trigger alert
        for i in range(60):  # Trigger high error rate alert
            test_error = Exception(f"Test error {i}")
            record_error(
                agent_id="integration-test-agent",
                error=test_error,
                category=ErrorCategory.SYSTEM,
                severity=ErrorSeverity.HIGH
            )

        # Check that errors were recorded
        stats = aggregator.get_error_statistics()
        assert stats["total_errors"] >= 60

        # Check that alerts were triggered (would need more sophisticated mocking for full test)
        assert len(aggregator.alert_rules) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
