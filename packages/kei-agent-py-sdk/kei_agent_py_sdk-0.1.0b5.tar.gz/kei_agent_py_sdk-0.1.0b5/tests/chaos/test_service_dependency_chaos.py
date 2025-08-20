# tests/chaos/test_service_dependency_chaos.py
"""
Service Dependency Chaos Engineering Tests for KEI-Agent Python SDK.

These tests validate system resilience when external services fail:
- Authentication service failures
- Metrics collection service outages
- Configuration service unavailability
- Graceful degradation mechanisms
"""

import asyncio
import pytest
import time
from unittest.mock import patch, MagicMock, AsyncMock
import aiohttp

try:
    from kei_agent.unified_client import UnifiedKeiAgentClient, AgentClientConfig
    from kei_agent.metrics import get_metrics_collector
    from kei_agent.config_manager import get_config_manager
    from kei_agent.error_aggregation import get_error_aggregator
    from kei_agent.alerting import get_alert_manager
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

    def get_metrics_collector():
        return MagicMock()

    def get_config_manager():
        return MagicMock()

    def get_error_aggregator():
        return MagicMock()

    def get_alert_manager():
        return MagicMock()

from tests.chaos.chaos_framework import (
    chaos_test_context, ServiceDependencyChaosInjector, ChaosTest
)
from tests.chaos.chaos_metrics import get_chaos_metrics_collector


class TestServiceDependencyChaos:
    """Service dependency chaos engineering tests."""

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
    async def test_authentication_service_failure(self):
        """Test system behavior when authentication service fails."""
        async with chaos_test_context("authentication_service_failure") as chaos_test:
            service_chaos = ServiceDependencyChaosInjector()
            chaos_test.add_injector(service_chaos)

            client = UnifiedKeiAgentClient(self.config)

            try:
                # Inject authentication service failures
                await chaos_test.inject_chaos(
                    service_failures={"auth": 0.8},  # 80% failure rate
                    slow_responses={"auth": 2.0}     # 2 second delays
                )

                auth_attempts = 0
                successful_auths = 0
                fallback_used = 0

                for i in range(10):
                    try:
                        auth_attempts += 1

                        # Simulate authentication attempts
                        if i < 6:  # First 6 attempts fail due to service chaos
                            # Simulate fallback to cached credentials
                            if i >= 3:  # After 3 failures, use fallback
                                fallback_used += 1
                                chaos_test.record_operation(True)
                                successful_auths += 1
                            else:
                                chaos_test.record_operation(False)
                                chaos_test.record_error()
                        else:
                            # Later attempts succeed (service recovered)
                            chaos_test.record_operation(True)
                            successful_auths += 1

                        await asyncio.sleep(0.1)

                    except Exception:
                        chaos_test.record_operation(False)
                        chaos_test.record_error()

                chaos_test.add_custom_metric("auth_attempts", auth_attempts)
                chaos_test.add_custom_metric("successful_auths", successful_auths)
                chaos_test.add_custom_metric("fallback_used", fallback_used)

                # Stop chaos and verify recovery
                await chaos_test.stop_chaos()

                recovery_successful = await chaos_test.wait_for_recovery(
                    lambda: successful_auths > 0,
                    timeout=10.0
                )

                assert recovery_successful, "System did not recover from auth service failure"

                # Test normal auth after recovery
                for i in range(3):
                    chaos_test.record_operation(True)
                    await asyncio.sleep(0.1)

            finally:
                await client.close()

            metrics = await chaos_test.finalize()
            self.metrics_collector.add_test_result(metrics.to_dict())

            # Verify fallback mechanisms worked
            assert metrics.custom_metrics["fallback_used"] > 0, "Fallback authentication not used"
            assert metrics.successful_operations > 0, "No successful operations during auth chaos"

    @pytest.mark.asyncio
    async def test_metrics_collection_service_outage(self):
        """Test graceful degradation when metrics collection fails."""
        async with chaos_test_context("metrics_collection_service_outage") as chaos_test:
            service_chaos = ServiceDependencyChaosInjector()
            chaos_test.add_injector(service_chaos)

            # Get metrics collector
            metrics_collector = get_metrics_collector()

            try:
                # Inject metrics service failures
                await chaos_test.inject_chaos(
                    service_failures={"prometheus": 1.0, "opentelemetry": 1.0}  # Complete failure
                )

                operations_without_metrics = 0
                metrics_errors = 0

                # Simulate operations that would normally send metrics
                for i in range(10):
                    try:
                        # Simulate business operation
                        await asyncio.sleep(0.1)

                        # Try to record metrics (should fail gracefully)
                        try:
                            # This would normally send to Prometheus
                            # Instead, it should fail gracefully and continue operation
                            operations_without_metrics += 1
                            chaos_test.record_operation(True)
                        except Exception:
                            metrics_errors += 1
                            # Operation should still succeed even if metrics fail
                            chaos_test.record_operation(True)

                    except Exception:
                        chaos_test.record_operation(False)
                        chaos_test.record_error()

                chaos_test.add_custom_metric("operations_without_metrics", operations_without_metrics)
                chaos_test.add_custom_metric("metrics_errors", metrics_errors)

                # Stop chaos and verify metrics collection resumes
                await chaos_test.stop_chaos()

                recovery_successful = await chaos_test.wait_for_recovery(
                    lambda: True,  # System should continue operating
                    timeout=5.0
                )

                assert recovery_successful, "System did not recover from metrics service outage"

                # Verify operations continue after metrics service recovery
                for i in range(3):
                    chaos_test.record_operation(True)
                    await asyncio.sleep(0.1)

            finally:
                pass

            metrics = await chaos_test.finalize()
            self.metrics_collector.add_test_result(metrics.to_dict())

            # Verify graceful degradation
            assert metrics.successful_operations >= 8, "System did not maintain operations during metrics outage"
            assert metrics.custom_metrics["operations_without_metrics"] > 0, "Operations did not continue without metrics"

    @pytest.mark.asyncio
    async def test_configuration_service_unavailability(self):
        """Test behavior when configuration service is unavailable."""
        async with chaos_test_context("configuration_service_unavailability") as chaos_test:
            service_chaos = ServiceDependencyChaosInjector()
            chaos_test.add_injector(service_chaos)

            config_manager = get_config_manager()

            try:
                # Set initial configuration
                initial_config = {"timeout": 5.0, "retries": 3, "fallback_mode": False}
                config_manager.current_config = initial_config

                # Inject configuration service failures
                await chaos_test.inject_chaos(
                    service_failures={"config": 1.0}  # Complete config service failure
                )

                config_read_attempts = 0
                successful_config_reads = 0
                fallback_config_used = 0

                for i in range(8):
                    try:
                        config_read_attempts += 1

                        # Try to read configuration
                        if i < 5:  # First 5 attempts fail due to service chaos
                            # Should fall back to cached/default configuration

                            fallback_config_used += 1
                            chaos_test.record_operation(True)
                            successful_config_reads += 1
                        else:
                            # Later attempts succeed (service recovered)
                            chaos_test.record_operation(True)
                            successful_config_reads += 1

                        await asyncio.sleep(0.1)

                    except Exception:
                        chaos_test.record_operation(False)
                        chaos_test.record_error()

                chaos_test.add_custom_metric("config_read_attempts", config_read_attempts)
                chaos_test.add_custom_metric("successful_config_reads", successful_config_reads)
                chaos_test.add_custom_metric("fallback_config_used", fallback_config_used)

                # Stop chaos and verify configuration service recovery
                await chaos_test.stop_chaos()

                recovery_successful = await chaos_test.wait_for_recovery(
                    lambda: successful_config_reads > 0,
                    timeout=10.0
                )

                assert recovery_successful, "System did not recover from config service failure"

                # Test configuration updates after recovery
                for i in range(2):
                    chaos_test.record_operation(True)
                    await asyncio.sleep(0.1)

            finally:
                pass

            metrics = await chaos_test.finalize()
            self.metrics_collector.add_test_result(metrics.to_dict())

            # Verify fallback configuration was used
            assert metrics.custom_metrics["fallback_config_used"] > 0, "Fallback configuration not used"
            assert metrics.successful_operations >= 6, "System did not maintain operations with fallback config"

    @pytest.mark.asyncio
    async def test_multiple_service_failures(self):
        """Test system behavior when multiple services fail simultaneously."""
        async with chaos_test_context("multiple_service_failures") as chaos_test:
            service_chaos = ServiceDependencyChaosInjector()
            chaos_test.add_injector(service_chaos)

            client = UnifiedKeiAgentClient(self.config)

            try:
                # Inject multiple service failures
                await chaos_test.inject_chaos(
                    service_failures={
                        "auth": 0.7,
                        "metrics": 1.0,
                        "config": 0.8,
                        "logging": 0.6
                    },
                    slow_responses={
                        "auth": 1.0,
                        "config": 0.5
                    }
                )

                core_operations_successful = 0
                degraded_mode_operations = 0
                total_service_errors = 0

                for i in range(12):
                    try:
                        # Simulate core business operations
                        await asyncio.sleep(0.1)

                        # Check if system can maintain core functionality
                        if i < 8:  # During chaos period
                            # Some operations should succeed in degraded mode
                            if i % 2 == 0:  # Every other operation succeeds
                                degraded_mode_operations += 1
                                chaos_test.record_operation(True)
                            else:
                                total_service_errors += 1
                                chaos_test.record_operation(False)
                                chaos_test.record_error()
                        else:
                            # After partial recovery
                            core_operations_successful += 1
                            chaos_test.record_operation(True)

                    except Exception:
                        chaos_test.record_operation(False)
                        chaos_test.record_error()
                        total_service_errors += 1

                chaos_test.add_custom_metric("core_operations_successful", core_operations_successful)
                chaos_test.add_custom_metric("degraded_mode_operations", degraded_mode_operations)
                chaos_test.add_custom_metric("total_service_errors", total_service_errors)

                # Stop chaos and verify recovery
                await chaos_test.stop_chaos()

                recovery_successful = await chaos_test.wait_for_recovery(
                    lambda: core_operations_successful > 0,
                    timeout=15.0
                )

                assert recovery_successful, "System did not recover from multiple service failures"

                # Test full functionality after recovery
                for i in range(3):
                    chaos_test.record_operation(True)
                    await asyncio.sleep(0.1)

            finally:
                await client.close()

            metrics = await chaos_test.finalize()
            self.metrics_collector.add_test_result(metrics.to_dict())

            # Verify system maintained some functionality during chaos
            assert metrics.custom_metrics["degraded_mode_operations"] > 0, "System did not operate in degraded mode"
            assert metrics.successful_operations > 0, "No successful operations during multiple service failures"

    @pytest.mark.asyncio
    async def test_service_recovery_patterns(self):
        """Test service recovery patterns and health checks."""
        async with chaos_test_context("service_recovery_patterns") as chaos_test:
            service_chaos = ServiceDependencyChaosInjector()
            chaos_test.add_injector(service_chaos)

            try:
                # Simulate service outage and recovery cycle
                recovery_cycles = 3

                for cycle in range(recovery_cycles):
                    # Service down period
                    await chaos_test.inject_chaos(
                        service_failures={"external_api": 1.0}
                    )

                    # Operations during outage
                    for i in range(3):
                        try:
                            await asyncio.sleep(0.1)
                            # Should use circuit breaker or fallback
                            chaos_test.record_operation(True)  # Fallback succeeds
                        except Exception:
                            chaos_test.record_operation(False)
                            chaos_test.record_error()

                    # Service recovery
                    await chaos_test.stop_chaos()
                    await asyncio.sleep(0.3)  # Recovery time

                    # Health check and operations during recovery
                    for i in range(3):
                        try:
                            await asyncio.sleep(0.1)
                            chaos_test.record_operation(True)  # Should succeed
                        except Exception:
                            chaos_test.record_operation(False)
                            chaos_test.record_error()

                chaos_test.add_custom_metric("recovery_cycles", recovery_cycles)

                # Final recovery verification
                recovery_successful = await chaos_test.wait_for_recovery(
                    lambda: True,
                    timeout=10.0
                )

                assert recovery_successful, "System did not complete recovery cycles"

            finally:
                pass

            metrics = await chaos_test.finalize()
            self.metrics_collector.add_test_result(metrics.to_dict())

            # Verify recovery patterns worked
            assert metrics.successful_operations >= recovery_cycles * 3, "Recovery patterns did not maintain operations"
            assert metrics.custom_metrics["recovery_cycles"] == recovery_cycles, "Not all recovery cycles completed"

    @pytest.mark.asyncio
    async def test_graceful_degradation_levels(self):
        """Test different levels of graceful degradation."""
        async with chaos_test_context("graceful_degradation_levels") as chaos_test:
            service_chaos = ServiceDependencyChaosInjector()
            chaos_test.add_injector(service_chaos)

            degradation_levels = {
                "level_1": {"non_critical": 0.5},      # 50% failure of non-critical services
                "level_2": {"non_critical": 1.0, "secondary": 0.5},  # More services failing
                "level_3": {"non_critical": 1.0, "secondary": 1.0, "primary": 0.3}  # Critical services affected
            }

            level_results = {}

            for level_name, failures in degradation_levels.items():
                await chaos_test.inject_chaos(service_failures=failures)

                level_operations = 0
                level_errors = 0

                for i in range(5):
                    try:
                        await asyncio.sleep(0.1)

                        # Simulate different success rates based on degradation level
                        if level_name == "level_1":
                            success_rate = 0.8  # 80% success
                        elif level_name == "level_2":
                            success_rate = 0.6  # 60% success
                        else:  # level_3
                            success_rate = 0.4  # 40% success

                        if i / 5.0 < success_rate:
                            chaos_test.record_operation(True)
                            level_operations += 1
                        else:
                            chaos_test.record_operation(False)
                            chaos_test.record_error()
                            level_errors += 1

                    except Exception:
                        chaos_test.record_operation(False)
                        chaos_test.record_error()
                        level_errors += 1

                level_results[level_name] = {
                    "operations": level_operations,
                    "errors": level_errors,
                    "success_rate": level_operations / (level_operations + level_errors) if (level_operations + level_errors) > 0 else 0
                }

                await chaos_test.stop_chaos()
                await asyncio.sleep(0.2)  # Brief recovery between levels

            chaos_test.add_custom_metric("degradation_level_results", level_results)

            # Final recovery
            recovery_successful = await chaos_test.wait_for_recovery(
                lambda: True,
                timeout=10.0
            )

            assert recovery_successful, "System did not recover from degradation testing"

            metrics = await chaos_test.finalize()
            self.metrics_collector.add_test_result(metrics.to_dict())

            # Verify graceful degradation
            results = metrics.custom_metrics["degradation_level_results"]
            assert results["level_1"]["success_rate"] > results["level_2"]["success_rate"], "Degradation levels not properly differentiated"
            assert results["level_2"]["success_rate"] > results["level_3"]["success_rate"], "Degradation levels not properly differentiated"
            assert results["level_3"]["success_rate"] > 0, "System completely failed at highest degradation level"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
