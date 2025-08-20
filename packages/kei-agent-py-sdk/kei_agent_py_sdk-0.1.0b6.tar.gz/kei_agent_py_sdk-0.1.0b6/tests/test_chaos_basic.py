# tests/test_chaos_basic.py
"""
Basic chaos engineering framework test to verify functionality.
"""

import asyncio
import pytest
import time

from tests.chaos.chaos_framework import chaos_test_context, ChaosTest, ChaosMetrics
from tests.chaos.chaos_metrics import get_chaos_metrics_collector, reset_chaos_metrics_collector


class TestBasicChaosFramework:
    """Basic tests for chaos engineering framework."""

    def setup_method(self):
        """Setup for each test."""
        reset_chaos_metrics_collector()
        self.metrics_collector = get_chaos_metrics_collector()

    @pytest.mark.asyncio
    async def test_chaos_test_context_basic(self):
        """Test basic chaos test context functionality."""
        async with chaos_test_context("basic_test") as chaos_test:
            # Verify test initialization
            assert chaos_test.name == "basic_test"
            assert chaos_test.metrics.test_name == "basic_test"
            assert chaos_test.metrics.start_time > 0

            # Test operation recording
            chaos_test.record_operation(True)
            chaos_test.record_operation(False)
            chaos_test.record_error()

            # Verify metrics
            assert chaos_test.metrics.successful_operations == 1
            assert chaos_test.metrics.failed_operations == 1
            assert chaos_test.metrics.errors_during_chaos == 1

            # Test custom metrics
            chaos_test.add_custom_metric("test_value", 42)
            assert chaos_test.metrics.custom_metrics["test_value"] == 42

        # Verify finalization
        assert chaos_test.metrics.end_time is not None
        assert chaos_test.metrics.duration > 0

    @pytest.mark.asyncio
    async def test_chaos_metrics_collection(self):
        """Test chaos metrics collection."""
        # Create test metrics
        metrics = ChaosMetrics(test_name="metrics_test", start_time=time.time())

        # Add some data
        metrics.successful_operations = 8
        metrics.failed_operations = 2
        metrics.errors_during_chaos = 1
        metrics.end_time = time.time()

        # Test serialization
        metrics_dict = metrics.to_dict()
        assert isinstance(metrics_dict, dict)
        assert metrics_dict["test_name"] == "metrics_test"
        assert metrics_dict["successful_operations"] == 8
        assert metrics_dict["failed_operations"] == 2
        assert metrics_dict["success_rate"] == 0.8  # 8/(8+2)

    def test_metrics_collector_basic(self):
        """Test basic metrics collector functionality."""
        collector = get_chaos_metrics_collector()

        # Add test result
        test_result = {
            "test_name": "collector_test",
            "success_rate": 0.9,
            "time_to_recovery": 2.5,
            "errors_during_chaos": 1
        }

        collector.add_test_result(test_result)

        # Verify result was added
        assert len(collector.test_results) == 1
        assert collector.test_results[0]["test_name"] == "collector_test"

    @pytest.mark.asyncio
    async def test_recovery_waiting(self):
        """Test recovery waiting functionality."""
        async with chaos_test_context("recovery_test") as chaos_test:
            # Test successful recovery
            recovery_successful = await chaos_test.wait_for_recovery(
                lambda: True,  # Always returns True
                timeout=1.0
            )
            assert recovery_successful

            # Test failed recovery (timeout)
            recovery_failed = await chaos_test.wait_for_recovery(
                lambda: False,  # Always returns False
                timeout=0.1
            )
            assert not recovery_failed

    @pytest.mark.asyncio
    async def test_simple_chaos_scenario(self):
        """Test a simple chaos scenario."""
        async with chaos_test_context("simple_chaos") as chaos_test:
            # Simulate normal operations
            for i in range(5):
                chaos_test.record_operation(True)
                await asyncio.sleep(0.01)

            # Simulate chaos injection
            chaos_test.metrics.failure_injected_at = time.time()

            # Simulate operations under chaos
            for i in range(10):
                if i % 3 == 0:  # Every 3rd operation fails
                    chaos_test.record_operation(False)
                    chaos_test.record_error()
                else:
                    chaos_test.record_operation(True)
                await asyncio.sleep(0.01)

            # Simulate recovery
            chaos_test.metrics.recovery_time = time.time()

            for i in range(3):
                chaos_test.record_operation(True)
                await asyncio.sleep(0.01)

            # Add custom metrics
            chaos_test.add_custom_metric("chaos_intensity", 0.3)
            chaos_test.add_custom_metric("recovery_successful", True)

        # Verify results
        metrics = chaos_test.metrics
        assert metrics.successful_operations > 0
        assert metrics.failed_operations > 0
        assert metrics.time_to_recovery is not None
        assert metrics.custom_metrics["chaos_intensity"] == 0.3

        # Add to collector
        self.metrics_collector.add_test_result(metrics.to_dict())

        # Verify collector has the result
        assert len(self.metrics_collector.test_results) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
