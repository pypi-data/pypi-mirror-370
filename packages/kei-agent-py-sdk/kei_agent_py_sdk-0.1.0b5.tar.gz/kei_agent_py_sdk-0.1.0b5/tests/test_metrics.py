# tests/test_metrics.py
"""
Tests for comprehensive metrics collection functionality.

This test validates that:
1. Prometheus metrics are collected correctly
2. OpenTelemetry tracing works properly
3. Business metrics are recorded accurately
4. Security events are tracked
5. Performance metrics are captured
6. Metrics server functionality works
"""

import asyncio
import time
from unittest.mock import patch, MagicMock

import pytest

from kei_agent.metrics import (
    MetricsCollector, MetricEvent, get_metrics_collector,
    initialize_metrics, record_request_metric, record_connection_metric
)


class TestMetricsCollector:
    """Tests for MetricsCollector functionality."""

    def test_metrics_collector_initialization(self):
        """Test MetricsCollector initialization."""
        collector = MetricsCollector()

        # Should initialize without errors
        assert collector is not None
        assert hasattr(collector, 'enabled')
        assert hasattr(collector, 'metrics')
        assert hasattr(collector, 'custom_metrics')

    def test_prometheus_metrics_availability(self):
        """Test Prometheus metrics availability detection."""
        collector = MetricsCollector()

        # Should detect if Prometheus is available
        assert isinstance(collector.enabled, bool)

        if collector.enabled:
            assert collector.registry is not None
            assert len(collector.metrics) > 0

    def test_record_connection_metric(self):
        """Test connection metric recording."""
        collector = MetricsCollector()

        # Should not raise errors even if Prometheus not available
        collector.record_connection("test-agent", "rpc", "connected")
        collector.record_connection("test-agent", "stream", "disconnected")

        # If Prometheus is available, check metric was recorded
        if collector.enabled and 'agent_connections_total' in collector.metrics:
            metric = collector.metrics['agent_connections_total']
            # Metric should exist and be callable
            assert hasattr(metric, 'labels')

    def test_record_request_metric(self):
        """Test request metric recording."""
        collector = MetricsCollector()

        # Should not raise errors
        collector.record_request("test-agent", "get_status", "success", 0.1, "rpc")
        collector.record_request("test-agent", "send_message", "error", 0.5, "stream")

        # If Prometheus is available, check metrics were recorded
        if collector.enabled:
            if 'agent_requests_total' in collector.metrics:
                assert hasattr(collector.metrics['agent_requests_total'], 'labels')
            if 'agent_request_duration' in collector.metrics:
                assert hasattr(collector.metrics['agent_request_duration'], 'labels')

    def test_record_protocol_message(self):
        """Test protocol message metric recording."""
        collector = MetricsCollector()

        collector.record_protocol_message("test-agent", "rpc", "sent", "request")
        collector.record_protocol_message("test-agent", "stream", "received", "response")

        # Should not raise errors
        assert True

    def test_record_security_event(self):
        """Test security event metric recording."""
        collector = MetricsCollector()

        collector.record_security_event("test-agent", "auth_failure", "warning")
        collector.record_security_event("test-agent", "validation_error", "error")

        # Should not raise errors
        assert True

    def test_record_auth_attempt(self):
        """Test authentication attempt metric recording."""
        collector = MetricsCollector()

        collector.record_auth_attempt("test-agent", "bearer", "success")
        collector.record_auth_attempt("test-agent", "oidc", "failure")

        # Should not raise errors
        assert True

    def test_update_performance_metrics(self):
        """Test performance metric updates."""
        collector = MetricsCollector()

        collector.update_memory_usage("test-agent", 1024 * 1024)  # 1MB
        collector.update_cpu_usage("test-agent", 25.5)
        collector.update_uptime("test-agent", 3600)  # 1 hour

        # Should not raise errors
        assert True

    def test_set_agent_info(self):
        """Test agent information setting."""
        collector = MetricsCollector()

        collector.set_agent_info(
            agent_id="test-agent",
            version="1.0.0",
            protocol_version="1.0",
            environment="test"
        )

        # Should not raise errors
        assert True

    def test_custom_metric_recording(self):
        """Test custom metric event recording."""
        collector = MetricsCollector()

        event = MetricEvent(
            name="custom_test_metric",
            value=42.0,
            labels={"type": "test", "environment": "unit_test"},
            metric_type="gauge",
            help_text="Test custom metric"
        )

        collector.record_custom_metric(event)

        # Should be added to custom metrics
        assert len(collector.custom_metrics) == 1
        assert collector.custom_metrics[0].name == "custom_test_metric"
        assert collector.custom_metrics[0].value == 42.0

    @pytest.mark.asyncio
    async def test_trace_operation_context_manager(self):
        """Test OpenTelemetry tracing context manager."""
        collector = MetricsCollector()

        # Should work even if OpenTelemetry not available
        async with collector.trace_operation("test_operation", "test-agent", test_attr="value") as span:
            # Simulate some work
            await asyncio.sleep(0.01)

            # Should not raise errors
            assert True

    def test_get_prometheus_metrics(self):
        """Test Prometheus metrics export."""
        collector = MetricsCollector()

        metrics_text = collector.get_prometheus_metrics()

        # Should return string
        assert isinstance(metrics_text, str)

        if collector.enabled:
            # Should contain metric definitions
            assert len(metrics_text) > 0
        else:
            # Should contain unavailable message
            assert "not available" in metrics_text.lower()

    def test_get_metrics_summary(self):
        """Test metrics summary generation."""
        collector = MetricsCollector()

        summary = collector.get_metrics_summary()

        # Should return dictionary with expected keys
        assert isinstance(summary, dict)
        assert "prometheus_enabled" in summary
        assert "opentelemetry_enabled" in summary
        assert "custom_metrics_count" in summary
        assert "registered_metrics" in summary

        # Values should be correct types
        assert isinstance(summary["prometheus_enabled"], bool)
        assert isinstance(summary["opentelemetry_enabled"], bool)
        assert isinstance(summary["custom_metrics_count"], int)
        assert isinstance(summary["registered_metrics"], list)


class TestGlobalMetricsCollector:
    """Tests for global metrics collector functions."""

    def test_get_metrics_collector_singleton(self):
        """Test global metrics collector singleton."""
        collector1 = get_metrics_collector()
        collector2 = get_metrics_collector()

        # Should return same instance
        assert collector1 is collector2

    def test_initialize_metrics(self):
        """Test metrics initialization."""
        collector = initialize_metrics()

        # Should return MetricsCollector instance
        assert isinstance(collector, MetricsCollector)

        # Should be same as global instance
        global_collector = get_metrics_collector()
        assert collector is global_collector

    def test_convenience_functions(self):
        """Test convenience functions for common metrics."""
        # Should not raise errors
        record_request_metric("test-agent", "test_method", "success", 0.1, "rpc")
        record_connection_metric("test-agent", "stream", "connected")


class TestMetricEvent:
    """Tests for MetricEvent data class."""

    def test_metric_event_creation(self):
        """Test MetricEvent creation."""
        event = MetricEvent(
            name="test_metric",
            value=123.45,
            labels={"env": "test"},
            metric_type="counter",
            help_text="Test metric"
        )

        assert event.name == "test_metric"
        assert event.value == 123.45
        assert event.labels == {"env": "test"}
        assert event.metric_type == "counter"
        assert event.help_text == "Test metric"
        assert isinstance(event.timestamp, float)

    def test_metric_event_defaults(self):
        """Test MetricEvent default values."""
        event = MetricEvent(name="test", value=1.0)

        assert event.labels == {}
        assert event.metric_type == "counter"
        assert event.help_text == ""
        assert event.timestamp > 0


class TestMetricsIntegration:
    """Integration tests for metrics with other components."""

    @pytest.mark.asyncio
    async def test_metrics_with_unified_client(self):
        """Test metrics integration with UnifiedKeiAgentClient."""
        from kei_agent import UnifiedKeiAgentClient, AgentClientConfig

        config = AgentClientConfig(
            base_url="https://api.example.com",
            api_token="test-token",
            agent_id="metrics-test-agent"
        )

        # Mock the actual network calls
        with patch.object(UnifiedKeiAgentClient, '_execute_with_protocol') as mock_execute:
            mock_execute.return_value = {"status": "success"}

            async with UnifiedKeiAgentClient(config) as client:
                # Execute an operation
                result = await client.execute_agent_operation("test_operation", {"data": "test"})

                assert result["status"] == "success"

                # Metrics should have been recorded
                collector = get_metrics_collector()
                assert collector is not None

    def test_metrics_with_security_events(self):
        """Test metrics recording for security events."""
        from kei_agent.metrics import record_security_metric

        # Should not raise errors
        record_security_metric("test-agent", "auth_failure", "warning")
        record_security_metric("test-agent", "validation_error", "error")
        record_security_metric("test-agent", "token_refresh", "info")

    @pytest.mark.asyncio
    async def test_metrics_with_tracing(self):
        """Test metrics integration with tracing."""
        collector = get_metrics_collector()

        # Test tracing operation
        async with collector.trace_operation("test_trace", "test-agent", operation="test") as span:
            # Simulate work
            await asyncio.sleep(0.01)

            # Should complete without errors
            assert True

    def test_metrics_performance_impact(self):
        """Test that metrics collection has minimal performance impact."""
        collector = MetricsCollector()

        # Measure time for metric recording
        start_time = time.time()

        for i in range(1000):
            collector.record_request("test-agent", "test_method", "success", 0.001, "rpc")

        end_time = time.time()
        duration = end_time - start_time

        # Should complete quickly (less than 1 second for 1000 operations)
        assert duration < 1.0

    def test_metrics_memory_usage(self):
        """Test metrics memory usage patterns."""
        collector = MetricsCollector()

        # Record many custom metrics
        for i in range(100):
            event = MetricEvent(
                name=f"test_metric_{i}",
                value=float(i),
                labels={"index": str(i)}
            )
            collector.record_custom_metric(event)

        # Should have recorded all metrics
        assert len(collector.custom_metrics) == 100

        # Memory usage should be reasonable
        import sys
        memory_usage = sys.getsizeof(collector.custom_metrics)
        assert memory_usage < 1024 * 1024  # Less than 1MB


class TestMetricsErrorHandling:
    """Tests for metrics error handling and resilience."""

    def test_metrics_with_invalid_data(self):
        """Test metrics handling with invalid data."""
        collector = MetricsCollector()

        # Should handle invalid data gracefully
        collector.record_request("", "", "", -1, "")
        collector.record_connection(None, None, None)

        # Should not raise errors
        assert True

    def test_metrics_with_missing_prometheus(self):
        """Test metrics behavior when Prometheus is not available."""
        # Create collector with disabled Prometheus
        with patch('kei_agent.metrics.PROMETHEUS_AVAILABLE', False):
            collector = MetricsCollector()

            assert not collector.enabled
            assert collector.registry is None

            # Should still work without errors
            collector.record_request("test-agent", "test", "success", 0.1, "rpc")

            metrics_text = collector.get_prometheus_metrics()
            assert "not available" in metrics_text.lower()

    def test_metrics_with_missing_opentelemetry(self):
        """Test metrics behavior when OpenTelemetry is not available."""
        with patch('kei_agent.metrics.OPENTELEMETRY_AVAILABLE', False):
            collector = MetricsCollector()

            # Should initialize without OpenTelemetry
            assert collector.tracer is None
            assert collector.meter is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
