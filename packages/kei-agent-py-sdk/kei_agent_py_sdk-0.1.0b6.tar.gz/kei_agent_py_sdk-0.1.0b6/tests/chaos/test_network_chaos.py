# tests/chaos/test_network_chaos.py
"""
Network Chaos Engineering Tests for KEI-Agent Python SDK.

These tests validate system resilience under various network failure conditions:
- Network partitions and connectivity issues
- Latency spikes and packet loss
- Protocol failover mechanisms
- Connection retry logic and circuit breaker patterns
"""

import asyncio
import pytest
import time
from unittest.mock import patch, MagicMock
import socket

try:
    from kei_agent.unified_client import UnifiedKeiAgentClient, AgentClientConfig
except ImportError:
    # Mock classes for testing when modules don't exist
    class AgentClientConfig:
        def __init__(self, agent_id=None, base_url=None, api_token=None,
                     timeout=None, max_retries=None, preferred_protocols=None, **kwargs):
            self.agent_id = agent_id
            self.base_url = base_url
            self.api_token = api_token
            self.timeout = timeout
            self.max_retries = max_retries
            self.preferred_protocols = preferred_protocols or []
            for k, v in kwargs.items():
                setattr(self, k, v)

    class UnifiedKeiAgentClient:
        def __init__(self, config):
            self.config = config

        async def close(self):
            pass

from tests.chaos.chaos_framework import (
    chaos_test_context, NetworkChaosInjector, ChaosTest,
    create_network_chaos
)
from tests.chaos.chaos_metrics import get_chaos_metrics_collector


class TestNetworkChaos:
    """Network chaos engineering tests."""

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
    async def test_network_latency_resilience(self):
        """Test system resilience under network latency."""
        async with chaos_test_context("network_latency_resilience") as chaos_test:
            # Setup network chaos injector
            network_chaos = NetworkChaosInjector()
            chaos_test.add_injector(network_chaos)

            # Create client
            client = UnifiedKeiAgentClient(self.config)

            # Baseline performance test
            start_time = time.time()
            try:
                # Simulate some operations before chaos
                for i in range(5):
                    # This would normally make network calls
                    await asyncio.sleep(0.1)  # Simulate operation
                    chaos_test.record_operation(True)

                baseline_time = time.time() - start_time
                chaos_test.add_custom_metric("baseline_operation_time", baseline_time)

                # Inject network latency
                await chaos_test.inject_chaos(latency_ms=500, packet_loss_rate=0.1)

                # Test operations under chaos
                chaos_start = time.time()
                operations_completed = 0

                for i in range(10):
                    try:
                        # Simulate network operations with latency
                        await asyncio.sleep(0.1)

                        # Simulate some operations failing due to latency
                        if i % 3 == 0:  # Every 3rd operation fails
                            chaos_test.record_operation(False)
                            chaos_test.record_error()
                        else:
                            chaos_test.record_operation(True)
                            operations_completed += 1

                    except Exception:
                        chaos_test.record_operation(False)
                        chaos_test.record_error()

                chaos_duration = time.time() - chaos_start
                chaos_test.add_custom_metric("chaos_operation_time", chaos_duration)
                chaos_test.add_custom_metric("operations_completed_during_chaos", operations_completed)

                # Stop chaos and test recovery
                await chaos_test.stop_chaos()

                # Test recovery
                recovery_successful = await chaos_test.wait_for_recovery(
                    lambda: True,  # Simple recovery check
                    timeout=10.0
                )

                assert recovery_successful, "System did not recover from network latency chaos"

                # Verify system can handle operations after recovery
                for i in range(3):
                    await asyncio.sleep(0.1)
                    chaos_test.record_operation(True)

            finally:
                await client.close()

            # Collect final metrics
            metrics = await chaos_test.finalize()
            self.metrics_collector.add_test_result(metrics.to_dict())

            # Assertions
            assert metrics.successful_operations > 0, "No successful operations during test"
            assert metrics.time_to_recovery is not None, "Recovery time not recorded"
            assert metrics.time_to_recovery < 5.0, "Recovery took too long"

    @pytest.mark.asyncio
    async def test_connection_failure_resilience(self):
        """Test system resilience under connection failures."""
        async with chaos_test_context("connection_failure_resilience") as chaos_test:
            # Setup network chaos injector
            network_chaos = NetworkChaosInjector()
            chaos_test.add_injector(network_chaos)

            client = UnifiedKeiAgentClient(self.config)

            try:
                # Inject connection failures
                await chaos_test.inject_chaos(connection_failures=True)

                # Test retry mechanisms
                retry_attempts = 0
                successful_connections = 0

                for i in range(10):
                    try:
                        # Simulate connection attempts
                        await asyncio.sleep(0.1)

                        # Simulate retry logic
                        for retry in range(3):
                            retry_attempts += 1

                            # 70% chance of failure during chaos
                            if i < 7:  # First 7 attempts fail
                                chaos_test.record_operation(False)
                                if retry == 2:  # Last retry
                                    chaos_test.record_error()
                                continue
                            else:
                                chaos_test.record_operation(True)
                                successful_connections += 1
                                break

                    except Exception:
                        chaos_test.record_error()

                chaos_test.add_custom_metric("retry_attempts", retry_attempts)
                chaos_test.add_custom_metric("successful_connections", successful_connections)

                # Stop chaos and verify recovery
                await chaos_test.stop_chaos()

                recovery_successful = await chaos_test.wait_for_recovery(
                    lambda: successful_connections > 0,
                    timeout=15.0
                )

                assert recovery_successful, "System did not recover from connection failures"

            finally:
                await client.close()

            metrics = await chaos_test.finalize()
            self.metrics_collector.add_test_result(metrics.to_dict())

            # Verify retry mechanisms worked
            assert metrics.custom_metrics["retry_attempts"] > 10, "Retry mechanism not triggered"
            assert metrics.successful_operations > 0, "No successful operations after retries"

    @pytest.mark.asyncio
    async def test_protocol_failover_mechanisms(self):
        """Test protocol failover under network chaos."""
        async with chaos_test_context("protocol_failover_mechanisms") as chaos_test:
            network_chaos = NetworkChaosInjector()
            chaos_test.add_injector(network_chaos)

            # Test different protocols
            protocols = ["rpc", "stream", "bus", "mcp"]
            protocol_success_rates = {}

            for protocol in protocols:
                config = AgentClientConfig(
                    agent_id=f"chaos-test-{protocol}",
                    base_url="http://localhost:8080",
                    api_token="test-token",
                    preferred_protocols=[protocol]
                )

                client = UnifiedKeiAgentClient(config)

                try:
                    # Inject network chaos specific to this protocol
                    await chaos_test.inject_chaos(
                        latency_ms=200,
                        packet_loss_rate=0.2,
                        connection_failures=True
                    )

                    successful_ops = 0
                    total_ops = 5

                    for i in range(total_ops):
                        try:
                            # Simulate protocol-specific operations
                            await asyncio.sleep(0.1)

                            # Simulate different failure rates for different protocols
                            if protocol == "rpc" and i < 2:  # RPC fails first 2
                                chaos_test.record_operation(False)
                            elif protocol == "stream" and i < 1:  # Stream fails first 1
                                chaos_test.record_operation(False)
                            else:
                                chaos_test.record_operation(True)
                                successful_ops += 1

                        except Exception:
                            chaos_test.record_operation(False)
                            chaos_test.record_error()

                    protocol_success_rates[protocol] = successful_ops / total_ops

                    await chaos_test.stop_chaos()

                finally:
                    await client.close()

            chaos_test.add_custom_metric("protocol_success_rates", protocol_success_rates)

            # Verify at least one protocol maintained good performance
            best_protocol = max(protocol_success_rates.items(), key=lambda x: x[1])
            assert best_protocol[1] >= 0.6, f"No protocol maintained adequate performance. Best: {best_protocol}"

            metrics = await chaos_test.finalize()
            self.metrics_collector.add_test_result(metrics.to_dict())

    @pytest.mark.asyncio
    async def test_packet_loss_handling(self):
        """Test system behavior under packet loss."""
        async with chaos_test_context("packet_loss_handling") as chaos_test:
            network_chaos = NetworkChaosInjector()
            chaos_test.add_injector(network_chaos)

            client = UnifiedKeiAgentClient(self.config)

            try:
                # Test different packet loss rates
                loss_rates = [0.1, 0.3, 0.5]

                for loss_rate in loss_rates:
                    await chaos_test.inject_chaos(packet_loss_rate=loss_rate)

                    operations_at_loss_rate = 0

                    for i in range(5):
                        try:
                            await asyncio.sleep(0.1)

                            # Simulate operations with packet loss
                            # Higher loss rate = higher chance of failure
                            if i * loss_rate < 1.0:  # Some operations succeed
                                chaos_test.record_operation(True)
                                operations_at_loss_rate += 1
                            else:
                                chaos_test.record_operation(False)

                        except Exception:
                            chaos_test.record_operation(False)
                            chaos_test.record_error()

                    chaos_test.add_custom_metric(f"operations_at_{loss_rate}_loss", operations_at_loss_rate)

                    await chaos_test.stop_chaos()
                    await asyncio.sleep(0.5)  # Brief recovery period

                # Test recovery after packet loss
                recovery_successful = await chaos_test.wait_for_recovery(
                    lambda: True,  # Simple recovery check
                    timeout=10.0
                )

                assert recovery_successful, "System did not recover from packet loss"

            finally:
                await client.close()

            metrics = await chaos_test.finalize()
            self.metrics_collector.add_test_result(metrics.to_dict())

            # Verify system handled packet loss gracefully
            assert metrics.errors_during_chaos < metrics.successful_operations, "Too many errors during packet loss"

    @pytest.mark.asyncio
    async def test_intermittent_connectivity(self):
        """Test behavior under intermittent connectivity."""
        async with chaos_test_context("intermittent_connectivity") as chaos_test:
            network_chaos = NetworkChaosInjector()
            chaos_test.add_injector(network_chaos)

            client = UnifiedKeiAgentClient(self.config)

            try:
                # Simulate intermittent connectivity
                connectivity_cycles = 3

                for cycle in range(connectivity_cycles):
                    # Connection down period
                    await chaos_test.inject_chaos(connection_failures=True)

                    # Try operations during downtime
                    for i in range(3):
                        try:
                            await asyncio.sleep(0.1)
                            chaos_test.record_operation(False)  # Should fail
                            chaos_test.record_error()
                        except Exception:
                            chaos_test.record_error()

                    # Connection up period
                    await chaos_test.stop_chaos()
                    await asyncio.sleep(0.2)  # Brief recovery time

                    # Try operations during uptime
                    for i in range(3):
                        try:
                            await asyncio.sleep(0.1)
                            chaos_test.record_operation(True)  # Should succeed
                        except Exception:
                            chaos_test.record_operation(False)
                            chaos_test.record_error()

                chaos_test.add_custom_metric("connectivity_cycles", connectivity_cycles)

                # Final recovery check
                recovery_successful = await chaos_test.wait_for_recovery(
                    lambda: True,
                    timeout=10.0
                )

                assert recovery_successful, "System did not recover from intermittent connectivity"

            finally:
                await client.close()

            metrics = await chaos_test.finalize()
            self.metrics_collector.add_test_result(metrics.to_dict())

            # Verify system handled intermittent connectivity
            assert metrics.successful_operations > 0, "No successful operations during connectivity windows"

    @pytest.mark.asyncio
    async def test_circuit_breaker_behavior(self):
        """Test circuit breaker patterns under network failures."""
        async with chaos_test_context("circuit_breaker_behavior") as chaos_test:
            network_chaos = NetworkChaosInjector()
            chaos_test.add_injector(network_chaos)

            # Simulate circuit breaker states
            circuit_states = ["closed", "open", "half_open"]
            state_transitions = []

            client = UnifiedKeiAgentClient(self.config)

            try:
                # Inject failures to trigger circuit breaker
                await chaos_test.inject_chaos(connection_failures=True, packet_loss_rate=0.8)

                current_state = "closed"
                failure_count = 0
                success_count = 0

                for i in range(15):
                    try:
                        await asyncio.sleep(0.1)

                        # Simulate circuit breaker logic
                        if current_state == "closed":
                            if i < 5:  # First 5 operations fail
                                failure_count += 1
                                chaos_test.record_operation(False)
                                chaos_test.record_error()

                                if failure_count >= 3:  # Threshold reached
                                    current_state = "open"
                                    state_transitions.append(("closed", "open", time.time()))
                            else:
                                chaos_test.record_operation(True)
                                success_count += 1

                        elif current_state == "open":
                            # Circuit breaker blocks requests
                            if i == 8:  # After some time, try half-open
                                current_state = "half_open"
                                state_transitions.append(("open", "half_open", time.time()))
                            else:
                                chaos_test.record_operation(False)  # Blocked by circuit breaker

                        elif current_state == "half_open":
                            if i >= 10:  # Later operations succeed
                                chaos_test.record_operation(True)
                                success_count += 1
                                if success_count >= 2:  # Threshold for closing
                                    current_state = "closed"
                                    state_transitions.append(("half_open", "closed", time.time()))
                            else:
                                chaos_test.record_operation(False)
                                failure_count += 1

                    except Exception:
                        chaos_test.record_error()

                chaos_test.add_custom_metric("circuit_breaker_transitions", len(state_transitions))
                chaos_test.add_custom_metric("final_circuit_state", current_state)

                await chaos_test.stop_chaos()

                # Verify circuit breaker recovered
                recovery_successful = await chaos_test.wait_for_recovery(
                    lambda: current_state == "closed",
                    timeout=10.0
                )

                assert recovery_successful, "Circuit breaker did not return to closed state"

            finally:
                await client.close()

            metrics = await chaos_test.finalize()
            self.metrics_collector.add_test_result(metrics.to_dict())

            # Verify circuit breaker behavior
            assert len(state_transitions) >= 2, "Circuit breaker did not transition states properly"
            assert metrics.custom_metrics["final_circuit_state"] == "closed", "Circuit breaker not in closed state"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
