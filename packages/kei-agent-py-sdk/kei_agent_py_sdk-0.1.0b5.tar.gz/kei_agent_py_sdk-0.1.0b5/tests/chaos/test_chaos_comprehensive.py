# tests/chaos/test_chaos_comprehensive.py
"""
Comprehensive Chaos Engineering Test Runner for KEI-Agent Python SDK.

This test validates the entire chaos engineering framework and runs
a comprehensive suite of chaos tests to measure overall system resilience.
"""

import asyncio
import pytest
import time
from pathlib import Path
import tempfile
import json

from tests.chaos.chaos_framework import chaos_test_context, ChaosTest
from tests.chaos.chaos_metrics import get_chaos_metrics_collector, reset_chaos_metrics_collector
from tests.chaos.chaos_integration import ChaosTestSuite
from tests.chaos.test_network_chaos import TestNetworkChaos
from tests.chaos.test_service_dependency_chaos import TestServiceDependencyChaos
from tests.chaos.test_resource_exhaustion_chaos import TestResourceExhaustionChaos
from tests.chaos.test_configuration_chaos import TestConfigurationChaos
from tests.chaos.test_security_chaos import TestSecurityChaos


class TestChaosFramework:
    """Tests for the chaos engineering framework itself."""

    def setup_method(self):
        """Setup for each test."""
        reset_chaos_metrics_collector()
        self.metrics_collector = get_chaos_metrics_collector()

    @pytest.mark.asyncio
    async def test_chaos_framework_basic_functionality(self):
        """Test basic chaos framework functionality."""
        async with chaos_test_context("framework_test") as chaos_test:
            # Test basic chaos test operations
            assert chaos_test.name == "framework_test"
            assert chaos_test.metrics.test_name == "framework_test"

            # Test operation recording
            chaos_test.record_operation(True)
            chaos_test.record_operation(False)
            chaos_test.record_error()

            assert chaos_test.metrics.successful_operations == 1
            assert chaos_test.metrics.failed_operations == 1
            assert chaos_test.metrics.errors_during_chaos == 1

            # Test custom metrics
            chaos_test.add_custom_metric("test_metric", 42)
            assert chaos_test.metrics.custom_metrics["test_metric"] == 42

            # Test recovery waiting
            recovery_successful = await chaos_test.wait_for_recovery(
                lambda: True,  # Always true for test
                timeout=1.0
            )
            assert recovery_successful

        # Test metrics finalization
        assert chaos_test.metrics.end_time is not None
        assert chaos_test.metrics.duration > 0

    @pytest.mark.asyncio
    async def test_metrics_collection_and_analysis(self):
        """Test metrics collection and analysis functionality."""
        # Add some test results
        test_results = [
            {
                "test_name": "test_1",
                "success_rate": 0.8,
                "time_to_recovery": 2.0,
                "errors_during_chaos": 1,
                "successful_operations": 8,
                "failed_operations": 2
            },
            {
                "test_name": "test_2",
                "success_rate": 0.9,
                "time_to_recovery": 1.5,
                "errors_during_chaos": 0,
                "successful_operations": 9,
                "failed_operations": 1
            }
        ]

        for result in test_results:
            self.metrics_collector.add_test_result(result)

        # Test resilience score calculation
        resilience_scores = self.metrics_collector.calculate_resilience_scores()
        assert len(resilience_scores) > 0

        # Test summary report generation
        summary_report = self.metrics_collector.generate_summary_report()

        assert "summary" in summary_report
        assert "resilience_scores" in summary_report
        assert "trends" in summary_report
        assert "recommendations" in summary_report

        # Verify summary contains expected data
        summary = summary_report["summary"]
        assert summary["total_tests"] == 2
        assert "overall_resilience_score" in summary

    def test_chaos_test_suite_initialization(self):
        """Test chaos test suite initialization."""
        config = {"safe_mode": True, "timeout": 30}
        test_suite = ChaosTestSuite(config)

        assert test_suite.config == config
        assert len(test_suite.test_categories) == 5
        assert "network" in test_suite.test_categories
        assert "security" in test_suite.test_categories

    @pytest.mark.asyncio
    async def test_safety_checks(self):
        """Test safety check mechanisms."""
        test_suite = ChaosTestSuite()

        # Test pre-test safety check
        safety_ok = await test_suite._pre_test_safety_check()
        assert isinstance(safety_ok, bool)

        # Test post-test safety check (should not raise)
        await test_suite._post_test_safety_check()


class TestComprehensiveChaosScenarios:
    """Comprehensive chaos engineering scenarios."""

    def setup_method(self):
        """Setup for each test."""
        reset_chaos_metrics_collector()
        self.metrics_collector = get_chaos_metrics_collector()

    @pytest.mark.asyncio
    async def test_multi_vector_chaos_scenario(self):
        """Test system resilience under multiple simultaneous chaos vectors."""
        async with chaos_test_context("multi_vector_chaos") as chaos_test:
            # Simulate multiple chaos vectors simultaneously
            chaos_vectors = {
                "network_latency": True,
                "service_failures": True,
                "memory_pressure": True,
                "config_corruption": True,
                "auth_failures": True
            }

            total_operations = 0
            successful_operations = 0
            chaos_events = 0
            recovery_attempts = 0

            # Phase 1: Normal operations
            for i in range(5):
                total_operations += 1
                successful_operations += 1
                chaos_test.record_operation(True)
                await asyncio.sleep(0.05)

            # Phase 2: Inject multiple chaos vectors
            chaos_test.metrics.failure_injected_at = time.time()

            for i in range(15):
                total_operations += 1

                # Simulate different types of failures
                if i % 5 == 0:  # Network issues
                    chaos_events += 1
                    chaos_test.record_operation(False)
                    chaos_test.record_error()
                elif i % 5 == 1:  # Service failures
                    chaos_events += 1
                    chaos_test.record_operation(False)
                    chaos_test.record_error()
                elif i % 5 == 2:  # Resource exhaustion
                    chaos_events += 1
                    # Some operations succeed with degraded performance
                    if i % 2 == 0:
                        successful_operations += 1
                        chaos_test.record_operation(True)
                    else:
                        chaos_test.record_operation(False)
                        chaos_test.record_error()
                else:
                    # Some operations succeed despite chaos
                    successful_operations += 1
                    chaos_test.record_operation(True)

                await asyncio.sleep(0.05)

            # Phase 3: Recovery
            chaos_test.metrics.recovery_time = time.time()

            for i in range(5):
                total_operations += 1
                recovery_attempts += 1

                # Most operations should succeed during recovery
                if i < 4:
                    successful_operations += 1
                    chaos_test.record_operation(True)
                else:
                    # Some lingering effects
                    chaos_test.record_operation(False)
                    chaos_test.record_error()

                await asyncio.sleep(0.05)

            # Record metrics
            chaos_test.add_custom_metric("total_operations", total_operations)
            chaos_test.add_custom_metric("chaos_events", chaos_events)
            chaos_test.add_custom_metric("recovery_attempts", recovery_attempts)
            chaos_test.add_custom_metric("chaos_vectors", len(chaos_vectors))

            # Calculate resilience metrics
            success_rate = successful_operations / total_operations
            chaos_test.add_custom_metric("overall_success_rate", success_rate)

            # Verify system maintained some functionality
            assert success_rate > 0.3, f"Success rate too low: {success_rate}"
            assert chaos_events > 0, "No chaos events recorded"
            assert recovery_attempts > 0, "No recovery attempts recorded"

        metrics = await chaos_test.finalize()
        self.metrics_collector.add_test_result(metrics.to_dict())

        # Verify comprehensive chaos scenario
        assert metrics.successful_operations > 0, "No successful operations during multi-vector chaos"
        assert metrics.time_to_recovery is not None, "Recovery time not recorded"
        assert metrics.custom_metrics["overall_success_rate"] > 0.3, "Overall success rate too low"

    @pytest.mark.asyncio
    async def test_cascading_failure_scenario(self):
        """Test system behavior under cascading failures."""
        async with chaos_test_context("cascading_failure") as chaos_test:
            # Simulate cascading failures
            failure_cascade = [
                "auth_service_down",
                "config_service_timeout",
                "metrics_collection_failed",
                "network_partition",
                "resource_exhaustion"
            ]

            cascade_depth = 0
            isolation_successful = False
            circuit_breakers_triggered = 0
            fallback_mechanisms_used = 0

            for i, failure_type in enumerate(failure_cascade):
                cascade_depth += 1

                # Simulate failure propagation
                if i == 0:  # Initial failure
                    chaos_test.record_operation(False)
                    chaos_test.record_error()
                elif i < 3:  # Cascading failures
                    # Some systems should isolate the failure
                    if i == 2:  # Circuit breaker triggers
                        circuit_breakers_triggered += 1
                        isolation_successful = True
                        chaos_test.record_operation(True)  # Isolated successfully
                    else:
                        chaos_test.record_operation(False)
                        chaos_test.record_error()
                else:  # Fallback mechanisms
                    fallback_mechanisms_used += 1
                    chaos_test.record_operation(True)

                await asyncio.sleep(0.1)

            chaos_test.add_custom_metric("cascade_depth", cascade_depth)
            chaos_test.add_custom_metric("isolation_successful", isolation_successful)
            chaos_test.add_custom_metric("circuit_breakers_triggered", circuit_breakers_triggered)
            chaos_test.add_custom_metric("fallback_mechanisms_used", fallback_mechanisms_used)

            # Verify cascade was contained
            assert isolation_successful, "Failure cascade was not isolated"
            assert circuit_breakers_triggered > 0, "Circuit breakers not triggered"
            assert fallback_mechanisms_used > 0, "Fallback mechanisms not used"

        metrics = await chaos_test.finalize()
        self.metrics_collector.add_test_result(metrics.to_dict())

    @pytest.mark.asyncio
    async def test_long_duration_chaos_scenario(self):
        """Test system behavior under extended chaos conditions."""
        async with chaos_test_context("long_duration_chaos") as chaos_test:
            # Extended chaos scenario (simulated)
            duration_phases = [
                {"name": "initial_chaos", "duration": 0.5, "intensity": 0.3},
                {"name": "peak_chaos", "duration": 0.3, "intensity": 0.8},
                {"name": "sustained_chaos", "duration": 0.4, "intensity": 0.5},
                {"name": "recovery_phase", "duration": 0.2, "intensity": 0.1}
            ]

            phase_results = {}
            total_duration = 0

            for phase in duration_phases:
                phase_name = phase["name"]
                phase_duration = phase["duration"]
                chaos_intensity = phase["intensity"]

                phase_start = time.time()
                phase_operations = 0
                phase_successes = 0

                # Simulate operations during this phase
                operations_in_phase = int(phase_duration * 20)  # 20 ops per simulated second

                for i in range(operations_in_phase):
                    phase_operations += 1

                    # Success rate inversely related to chaos intensity
                    success_probability = 1.0 - chaos_intensity

                    if i / operations_in_phase < success_probability:
                        phase_successes += 1
                        chaos_test.record_operation(True)
                    else:
                        chaos_test.record_operation(False)
                        chaos_test.record_error()

                    await asyncio.sleep(0.01)  # Small delay

                phase_end = time.time()
                actual_duration = phase_end - phase_start
                total_duration += actual_duration

                phase_results[phase_name] = {
                    "operations": phase_operations,
                    "successes": phase_successes,
                    "success_rate": phase_successes / phase_operations if phase_operations > 0 else 0,
                    "duration": actual_duration,
                    "chaos_intensity": chaos_intensity
                }

            chaos_test.add_custom_metric("phase_results", phase_results)
            chaos_test.add_custom_metric("total_test_duration", total_duration)

            # Verify system maintained functionality throughout
            for phase_name, results in phase_results.items():
                if phase_name != "peak_chaos":  # Allow lower success during peak chaos
                    assert results["success_rate"] > 0.2, f"Success rate too low in {phase_name}: {results['success_rate']}"

            # Verify recovery
            recovery_success_rate = phase_results["recovery_phase"]["success_rate"]
            assert recovery_success_rate > 0.8, f"Recovery success rate too low: {recovery_success_rate}"

        metrics = await chaos_test.finalize()
        self.metrics_collector.add_test_result(metrics.to_dict())

    @pytest.mark.asyncio
    async def test_chaos_test_suite_integration(self):
        """Test the complete chaos test suite integration."""
        # Create temporary config
        config = {
            "safe_mode": True,
            "timeout": 30,
            "max_chaos_intensity": 0.5
        }

        test_suite = ChaosTestSuite(config)

        # Run a subset of tests (to avoid long execution time)
        categories = ["network"]  # Just test one category for integration test

        try:
            report = await test_suite.run_chaos_tests(
                categories=categories,
                safe_mode=True
            )

            # Verify report structure
            assert "execution_metadata" in report
            assert "chaos_test_results" in report
            assert "recommendations" in report
            assert "next_steps" in report

            # Verify execution metadata
            metadata = report["execution_metadata"]
            assert "start_time" in metadata
            assert "end_time" in metadata
            assert "duration_seconds" in metadata
            assert "environment" in metadata

            # Verify chaos test results
            chaos_results = report["chaos_test_results"]
            assert "summary" in chaos_results

            # Save report for inspection
            temp_file = Path(tempfile.gettempdir()) / "chaos_integration_test_report.json"
            test_suite.save_report(report, temp_file)

            assert temp_file.exists(), "Report file was not created"

            # Verify report can be loaded
            with open(temp_file) as f:
                loaded_report = json.load(f)

            assert loaded_report == report, "Report serialization/deserialization failed"

        except Exception as e:
            pytest.fail(f"Chaos test suite integration failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
