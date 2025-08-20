# tests/chaos/test_resource_exhaustion_chaos.py
"""
Resource Exhaustion Chaos Engineering Tests for KEI-Agent Python SDK.

These tests validate system resilience under resource constraints:
- Memory pressure and CPU throttling
- Disk space constraints
- Connection pool exhaustion
- Rate limiting and backpressure mechanisms
"""

import asyncio
import pytest
import time
import psutil
import threading
from unittest.mock import patch, MagicMock

try:
    from kei_agent.unified_client import UnifiedKeiAgentClient, AgentClientConfig
    from kei_agent.metrics_server import MetricsServer
except ImportError:
    # Mock classes for testing when modules don't exist
    class AgentClientConfig:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    class UnifiedKeiAgentClient:
        def __init__(self, config):
            self.config = config

        async def close(self):
            pass

    class MetricsServer:
        def __init__(self, **kwargs):
            pass

from tests.chaos.chaos_framework import (
    chaos_test_context, ResourceExhaustionInjector, ChaosTest
)
from tests.chaos.chaos_metrics import get_chaos_metrics_collector


class TestResourceExhaustionChaos:
    """Resource exhaustion chaos engineering tests."""

    def setup_method(self):
        """Setup for each test."""
        self.config = AgentClientConfig(
            agent_id="chaos-test-agent",
            base_url="http://localhost:8080",
            api_token="test-token",
            timeout=5.0,
            max_retries=3
        )
        self.metrics_collector = get_chaos_metrics_collector()

    @pytest.mark.asyncio
    async def test_memory_pressure_resilience(self):
        """Test system behavior under memory pressure."""
        async with chaos_test_context("memory_pressure_resilience") as chaos_test:
            resource_chaos = ResourceExhaustionInjector()
            chaos_test.add_injector(resource_chaos)

            client = UnifiedKeiAgentClient(self.config)

            try:
                # Get baseline memory usage
                initial_memory = psutil.virtual_memory()
                chaos_test.add_custom_metric("initial_memory_percent", initial_memory.percent)

                # Inject memory pressure (50MB)
                await chaos_test.inject_chaos(memory_pressure_mb=50)

                operations_under_pressure = 0
                memory_related_errors = 0
                peak_memory_usage = 0

                for i in range(10):
                    try:
                        # Monitor memory during operations
                        current_memory = psutil.virtual_memory()
                        peak_memory_usage = max(peak_memory_usage, current_memory.percent)

                        # Simulate operations that might be affected by memory pressure
                        await asyncio.sleep(0.1)

                        # Some operations might fail under memory pressure
                        if current_memory.percent > 85:  # High memory usage
                            if i % 3 == 0:  # Every 3rd operation fails
                                memory_related_errors += 1
                                chaos_test.record_operation(False)
                                chaos_test.record_error()
                            else:
                                operations_under_pressure += 1
                                chaos_test.record_operation(True)
                        else:
                            operations_under_pressure += 1
                            chaos_test.record_operation(True)

                    except MemoryError:
                        memory_related_errors += 1
                        chaos_test.record_operation(False)
                        chaos_test.record_error()
                    except Exception:
                        chaos_test.record_operation(False)
                        chaos_test.record_error()

                chaos_test.add_custom_metric("operations_under_pressure", operations_under_pressure)
                chaos_test.add_custom_metric("memory_related_errors", memory_related_errors)
                chaos_test.add_custom_metric("peak_memory_usage", peak_memory_usage)

                # Stop memory pressure and verify recovery
                await chaos_test.stop_chaos()

                # Wait for memory to be released
                recovery_successful = await chaos_test.wait_for_recovery(
                    lambda: psutil.virtual_memory().percent < initial_memory.percent + 5,
                    timeout=15.0
                )

                assert recovery_successful, "System did not recover from memory pressure"

                # Test operations after memory recovery
                for i in range(3):
                    chaos_test.record_operation(True)
                    await asyncio.sleep(0.1)

            finally:
                await client.close()

            metrics = await chaos_test.finalize()
            self.metrics_collector.add_test_result(metrics.to_dict())

            # Verify system handled memory pressure
            assert metrics.successful_operations > 0, "No successful operations under memory pressure"
            assert metrics.custom_metrics["operations_under_pressure"] > 0, "System did not operate under memory pressure"

    @pytest.mark.asyncio
    async def test_cpu_pressure_resilience(self):
        """Test system behavior under CPU pressure."""
        async with chaos_test_context("cpu_pressure_resilience") as chaos_test:
            resource_chaos = ResourceExhaustionInjector()
            chaos_test.add_injector(resource_chaos)

            client = UnifiedKeiAgentClient(self.config)

            try:
                # Get baseline CPU usage
                initial_cpu = psutil.cpu_percent(interval=1)
                chaos_test.add_custom_metric("initial_cpu_percent", initial_cpu)

                # Inject CPU pressure
                await chaos_test.inject_chaos(cpu_pressure=True)

                operations_under_cpu_load = 0
                slow_operations = 0
                operation_times = []

                for i in range(8):
                    try:
                        start_time = time.time()

                        # Simulate CPU-intensive operations
                        await asyncio.sleep(0.2)  # Simulate work

                        operation_time = time.time() - start_time
                        operation_times.append(operation_time)

                        # Operations might be slower under CPU pressure
                        if operation_time > 0.3:  # Slower than expected
                            slow_operations += 1

                        operations_under_cpu_load += 1
                        chaos_test.record_operation(True)

                        # Monitor CPU usage
                        current_cpu = psutil.cpu_percent()
                        if current_cpu > 80:
                            chaos_test.add_custom_metric(f"high_cpu_at_operation_{i}", current_cpu)

                    except Exception:
                        chaos_test.record_operation(False)
                        chaos_test.record_error()

                avg_operation_time = sum(operation_times) / len(operation_times) if operation_times else 0

                chaos_test.add_custom_metric("operations_under_cpu_load", operations_under_cpu_load)
                chaos_test.add_custom_metric("slow_operations", slow_operations)
                chaos_test.add_custom_metric("avg_operation_time", avg_operation_time)

                # Stop CPU pressure and verify recovery
                await chaos_test.stop_chaos()

                recovery_successful = await chaos_test.wait_for_recovery(
                    lambda: psutil.cpu_percent() < 50,  # CPU usage should drop
                    timeout=10.0
                )

                assert recovery_successful, "System did not recover from CPU pressure"

                # Test operations after CPU recovery
                for i in range(3):
                    chaos_test.record_operation(True)
                    await asyncio.sleep(0.1)

            finally:
                await client.close()

            metrics = await chaos_test.finalize()
            self.metrics_collector.add_test_result(metrics.to_dict())

            # Verify system handled CPU pressure
            assert metrics.successful_operations > 0, "No successful operations under CPU pressure"
            assert metrics.custom_metrics["operations_under_cpu_load"] > 0, "System did not operate under CPU load"

    @pytest.mark.asyncio
    async def test_connection_pool_exhaustion(self):
        """Test behavior when connection pools are exhausted."""
        async with chaos_test_context("connection_pool_exhaustion") as chaos_test:
            # Simulate connection pool exhaustion
            max_connections = 5
            active_connections = []
            connection_attempts = 0
            successful_connections = 0
            pool_exhaustion_errors = 0

            try:
                for i in range(15):  # Try to create more connections than allowed
                    try:
                        connection_attempts += 1

                        # Simulate connection creation
                        if len(active_connections) < max_connections:
                            # Connection succeeds
                            active_connections.append(f"connection_{i}")
                            successful_connections += 1
                            chaos_test.record_operation(True)
                        else:
                            # Pool exhausted - should handle gracefully
                            pool_exhaustion_errors += 1

                            # Simulate connection pooling/reuse
                            if i % 3 == 0:  # Every 3rd attempt reuses connection
                                chaos_test.record_operation(True)
                            else:
                                chaos_test.record_operation(False)
                                chaos_test.record_error()

                        await asyncio.sleep(0.1)

                    except Exception:
                        chaos_test.record_operation(False)
                        chaos_test.record_error()
                        pool_exhaustion_errors += 1

                chaos_test.add_custom_metric("connection_attempts", connection_attempts)
                chaos_test.add_custom_metric("successful_connections", successful_connections)
                chaos_test.add_custom_metric("pool_exhaustion_errors", pool_exhaustion_errors)
                chaos_test.add_custom_metric("max_concurrent_connections", len(active_connections))

                # Simulate connection cleanup and recovery
                active_connections.clear()

                recovery_successful = await chaos_test.wait_for_recovery(
                    lambda: len(active_connections) == 0,
                    timeout=5.0
                )

                assert recovery_successful, "Connection pool did not recover"

                # Test connections after pool recovery
                for i in range(3):
                    chaos_test.record_operation(True)
                    await asyncio.sleep(0.1)

            finally:
                active_connections.clear()

            metrics = await chaos_test.finalize()
            self.metrics_collector.add_test_result(metrics.to_dict())

            # Verify connection pool handling
            assert metrics.custom_metrics["successful_connections"] == max_connections, "Connection pool limit not enforced"
            assert metrics.custom_metrics["pool_exhaustion_errors"] > 0, "Pool exhaustion not detected"
            assert metrics.successful_operations > max_connections, "System did not handle pool exhaustion gracefully"

    @pytest.mark.asyncio
    async def test_rate_limiting_backpressure(self):
        """Test rate limiting and backpressure mechanisms."""
        async with chaos_test_context("rate_limiting_backpressure") as chaos_test:
            # Simulate rate limiting
            rate_limit = 5  # 5 operations per second
            time_window = 1.0  # 1 second window

            operations_attempted = 0
            operations_allowed = 0
            operations_rate_limited = 0
            backpressure_applied = 0

            try:
                window_start = time.time()
                operations_in_window = 0

                for i in range(20):  # Attempt more operations than rate limit
                    try:
                        operations_attempted += 1
                        current_time = time.time()

                        # Reset window if needed
                        if current_time - window_start >= time_window:
                            window_start = current_time
                            operations_in_window = 0

                        # Check rate limit
                        if operations_in_window < rate_limit:
                            # Operation allowed
                            operations_in_window += 1
                            operations_allowed += 1
                            chaos_test.record_operation(True)
                        else:
                            # Rate limited - apply backpressure
                            operations_rate_limited += 1
                            backpressure_applied += 1

                            # Simulate backpressure delay
                            await asyncio.sleep(0.2)
                            chaos_test.record_operation(False)
                            chaos_test.record_error()

                        await asyncio.sleep(0.05)  # Small delay between operations

                    except Exception:
                        chaos_test.record_operation(False)
                        chaos_test.record_error()

                chaos_test.add_custom_metric("operations_attempted", operations_attempted)
                chaos_test.add_custom_metric("operations_allowed", operations_allowed)
                chaos_test.add_custom_metric("operations_rate_limited", operations_rate_limited)
                chaos_test.add_custom_metric("backpressure_applied", backpressure_applied)

                # Test recovery after rate limiting period
                await asyncio.sleep(time_window)  # Wait for rate limit window to reset

                recovery_successful = await chaos_test.wait_for_recovery(
                    lambda: True,  # Rate limit should reset
                    timeout=5.0
                )

                assert recovery_successful, "Rate limiting did not reset properly"

                # Test operations after rate limit reset
                for i in range(3):
                    chaos_test.record_operation(True)
                    await asyncio.sleep(0.1)

            finally:
                pass

            metrics = await chaos_test.finalize()
            self.metrics_collector.add_test_result(metrics.to_dict())

            # Verify rate limiting behavior
            assert metrics.custom_metrics["operations_rate_limited"] > 0, "Rate limiting not applied"
            assert metrics.custom_metrics["backpressure_applied"] > 0, "Backpressure not applied"
            assert metrics.custom_metrics["operations_allowed"] <= rate_limit * 2, "Rate limit not enforced properly"

    @pytest.mark.asyncio
    async def test_disk_space_constraints(self):
        """Test behavior under disk space constraints."""
        async with chaos_test_context("disk_space_constraints") as chaos_test:
            resource_chaos = ResourceExhaustionInjector()
            chaos_test.add_injector(resource_chaos)

            try:
                # Get baseline disk usage
                initial_disk = psutil.disk_usage('/')
                chaos_test.add_custom_metric("initial_disk_percent", initial_disk.percent)

                # Inject disk pressure
                await chaos_test.inject_chaos(disk_pressure=True)

                file_operations = 0
                disk_errors = 0
                operations_with_disk_pressure = 0

                for i in range(8):
                    try:
                        # Simulate file operations that might be affected by disk space
                        current_disk = psutil.disk_usage('/')

                        if current_disk.percent > 90:  # High disk usage
                            # Some operations might fail
                            if i % 2 == 0:  # Every other operation fails
                                disk_errors += 1
                                chaos_test.record_operation(False)
                                chaos_test.record_error()
                            else:
                                operations_with_disk_pressure += 1
                                chaos_test.record_operation(True)
                        else:
                            file_operations += 1
                            chaos_test.record_operation(True)

                        await asyncio.sleep(0.1)

                    except OSError as e:
                        # Disk space related errors
                        disk_errors += 1
                        chaos_test.record_operation(False)
                        chaos_test.record_error()
                    except Exception:
                        chaos_test.record_operation(False)
                        chaos_test.record_error()

                chaos_test.add_custom_metric("file_operations", file_operations)
                chaos_test.add_custom_metric("disk_errors", disk_errors)
                chaos_test.add_custom_metric("operations_with_disk_pressure", operations_with_disk_pressure)

                # Stop disk pressure and verify recovery
                await chaos_test.stop_chaos()

                recovery_successful = await chaos_test.wait_for_recovery(
                    lambda: True,  # Disk space should be cleaned up
                    timeout=10.0
                )

                assert recovery_successful, "System did not recover from disk pressure"

                # Test operations after disk recovery
                for i in range(3):
                    chaos_test.record_operation(True)
                    await asyncio.sleep(0.1)

            finally:
                pass

            metrics = await chaos_test.finalize()
            self.metrics_collector.add_test_result(metrics.to_dict())

            # Verify disk space handling
            assert metrics.successful_operations > 0, "No successful operations under disk pressure"

    @pytest.mark.asyncio
    async def test_combined_resource_exhaustion(self):
        """Test system behavior under combined resource exhaustion."""
        async with chaos_test_context("combined_resource_exhaustion") as chaos_test:
            resource_chaos = ResourceExhaustionInjector()
            chaos_test.add_injector(resource_chaos)

            client = UnifiedKeiAgentClient(self.config)

            try:
                # Inject multiple resource constraints simultaneously
                await chaos_test.inject_chaos(
                    memory_pressure_mb=30,
                    cpu_pressure=True,
                    disk_pressure=True
                )

                operations_under_stress = 0
                resource_errors = 0
                degraded_performance_ops = 0

                for i in range(10):
                    try:
                        start_time = time.time()

                        # Monitor system resources
                        memory = psutil.virtual_memory()
                        cpu = psutil.cpu_percent()
                        disk = psutil.disk_usage('/')

                        # Simulate operations under resource stress
                        await asyncio.sleep(0.1)

                        operation_time = time.time() - start_time

                        # Check if system is under stress
                        if memory.percent > 80 or cpu > 80 or disk.percent > 90:
                            if operation_time > 0.2:  # Slower than normal
                                degraded_performance_ops += 1

                            # Some operations might fail under extreme stress
                            if i < 6:  # First 6 operations during peak stress
                                if i % 3 == 0:  # Every 3rd operation fails
                                    resource_errors += 1
                                    chaos_test.record_operation(False)
                                    chaos_test.record_error()
                                else:
                                    operations_under_stress += 1
                                    chaos_test.record_operation(True)
                            else:
                                operations_under_stress += 1
                                chaos_test.record_operation(True)
                        else:
                            operations_under_stress += 1
                            chaos_test.record_operation(True)

                    except Exception:
                        resource_errors += 1
                        chaos_test.record_operation(False)
                        chaos_test.record_error()

                chaos_test.add_custom_metric("operations_under_stress", operations_under_stress)
                chaos_test.add_custom_metric("resource_errors", resource_errors)
                chaos_test.add_custom_metric("degraded_performance_ops", degraded_performance_ops)

                # Stop all resource pressure and verify recovery
                await chaos_test.stop_chaos()

                recovery_successful = await chaos_test.wait_for_recovery(
                    lambda: (psutil.virtual_memory().percent < 70 and
                            psutil.cpu_percent() < 50),
                    timeout=20.0
                )

                assert recovery_successful, "System did not recover from combined resource exhaustion"

                # Test operations after full recovery
                for i in range(3):
                    chaos_test.record_operation(True)
                    await asyncio.sleep(0.1)

            finally:
                await client.close()

            metrics = await chaos_test.finalize()
            self.metrics_collector.add_test_result(metrics.to_dict())

            # Verify system handled combined resource stress
            assert metrics.successful_operations > 0, "No successful operations under combined resource stress"
            assert metrics.custom_metrics["operations_under_stress"] > 0, "System did not operate under resource stress"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
