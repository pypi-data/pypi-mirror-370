# tests/integration/test_chaos_engineering.py
"""
Chaos engineering tests for KEI-Agent Python SDK.

These tests validate system resilience under failure conditions including:
- Network failures and partitions
- Service unavailability and timeouts
- Resource exhaustion scenarios
- Concurrent failure conditions
- Recovery and self-healing capabilities
- Circuit breaker and retry mechanisms
"""

import asyncio
import random
import time
from unittest.mock import AsyncMock, MagicMock, patch
from typing import List, Dict, Any

import pytest

from kei_agent import UnifiedKeiAgentClient, AgentClientConfig
from kei_agent.protocol_types import SecurityConfig, AuthType
from kei_agent.exceptions import (
    CommunicationError, SecurityError, ProtocolError,
    CircuitBreakerOpenError, retryExhaustedError
)
from . import (
    skip_if_no_integration_env, IntegrationTestBase,
    integration_test_base, INTEGRATION_TEST_CONFIG
)


@pytest.mark.chaos
@pytest.mark.skipif(
    not INTEGRATION_TEST_CONFIG.get("chaos_testing", False),
    reason="Chaos testing disabled"
)
class TestNetworkChaos:
    """Chaos engineering tests for network failure scenarios."""

    @pytest.mark.chaos
    @skip_if_no_integration_env()
    async def test_network_partition_recovery(self, integration_test_base):
        """Test recovery from network partition scenarios."""
        config = AgentClientConfig(**integration_test_base.get_test_config())

        async with UnifiedKeiAgentClient(config) as client:
            # Simulate network partition
            with patch.object(client, '_make_request') as mock_request:
                # First few requests fail due to network partition
                mock_request.side_effect = [
                    ConnectionError("Network unreachable"),
                    ConnectionError("Network unreachable"),
                    ConnectionError("Network unreachable"),
                    {"status": "recovered"}  # Network recovers
                ]

                # Client should eventually recover
                start_time = time.time()
                response = await client.get_agent_status()
                recovery_time = time.time() - start_time

                assert response["status"] == "recovered"
                assert mock_request.call_count == 4
                assert recovery_time < 30  # Should recover within 30 seconds

    @pytest.mark.chaos
    @skip_if_no_integration_env()
    async def test_intermittent_connectivity(self, integration_test_base):
        """Test handling of intermittent network connectivity."""
        config = AgentClientConfig(**integration_test_base.get_test_config())

        async with UnifiedKeiAgentClient(config) as client:
            success_count = 0
            failure_count = 0

            with patch.object(client, '_make_request') as mock_request:
                # Simulate intermittent connectivity (50% failure rate)
                def intermittent_response(*args, **kwargs):
                    if random.random() < 0.5:
                        raise ConnectionError("Intermittent failure")
                    return {"status": "success"}

                mock_request.side_effect = intermittent_response

                # Make multiple requests
                for _ in range(20):
                    try:
                        response = await client.get_agent_status()
                        if response["status"] == "success":
                            success_count += 1
                    except CommunicationError:
                        failure_count += 1

                # Should have some successes despite intermittent failures
                assert success_count > 0
                assert failure_count > 0
                assert success_count + failure_count <= 20

    @pytest.mark.chaos
    @skip_if_no_integration_env()
    async def test_dns_resolution_failure(self, integration_test_base):
        """Test handling of DNS resolution failures."""
        # Use invalid hostname to trigger DNS failure
        config = AgentClientConfig(
            base_url="https://nonexistent-host-12345.invalid",
            api_token=integration_test_base.credentials["api_token"],
            agent_id="chaos-test-agent",
            timeout=5,
            max_retries=2
        )

        async with UnifiedKeiAgentClient(config) as client:
            with pytest.raises(CommunicationError):
                await client.get_agent_status()

    @pytest.mark.chaos
    @skip_if_no_integration_env()
    async def test_slow_network_conditions(self, integration_test_base):
        """Test behavior under slow network conditions."""
        config = AgentClientConfig(**integration_test_base.get_test_config())

        async with UnifiedKeiAgentClient(config) as client:
            with patch.object(client, '_make_request') as mock_request:
                # Simulate slow network responses
                async def slow_response(*args, **kwargs):
                    await asyncio.sleep(2)  # 2 second delay
                    return {"status": "slow_response"}

                mock_request.side_effect = slow_response

                start_time = time.time()
                response = await client.get_agent_status()
                response_time = time.time() - start_time

                assert response["status"] == "slow_response"
                assert response_time >= 2  # Should take at least 2 seconds


@pytest.mark.chaos
@pytest.mark.skipif(
    not INTEGRATION_TEST_CONFIG.get("chaos_testing", False),
    reason="Chaos testing disabled"
)
class TestServiceChaos:
    """Chaos engineering tests for service failure scenarios."""

    @pytest.mark.chaos
    @skip_if_no_integration_env()
    async def test_service_unavailable_recovery(self, integration_test_base):
        """Test recovery when service becomes unavailable."""
        config = AgentClientConfig(**integration_test_base.get_test_config())

        async with UnifiedKeiAgentClient(config) as client:
            with patch.object(client, '_make_request') as mock_request:
                # Service unavailable, then recovers
                mock_request.side_effect = [
                    CommunicationError("Service unavailable"),
                    CommunicationError("Service unavailable"),
                    {"status": "service_recovered"}
                ]

                # Should eventually succeed after retries
                response = await client.get_agent_status()
                assert response["status"] == "service_recovered"
                assert mock_request.call_count == 3

    @pytest.mark.chaos
    @skip_if_no_integration_env()
    async def test_authentication_service_failure(self, integration_test_base):
        """Test handling of authentication service failures."""
        security_config = SecurityConfig(
            auth_type=Authtypee.OIDC,
            oidc_issuer="https://mock-auth-service.com",
            oidc_client_id="test-client",
            oidc_client_secret="test-secret"
        )

        config = AgentClientConfig(
            **integration_test_base.get_test_config(),
            security=security_config
        )

        async with UnifiedKeiAgentClient(config) as client:
            with patch.object(client.security_manager, '_fetch_oidc_token') as mock_auth:
                # Auth service fails, then recovers
                mock_auth.side_effect = [
                    ConnectionError("Auth service down"),
                    ConnectionError("Auth service down"),
                    {"access_token": "recovered-token", "token_type": "Bearer"}
                ]

                # Should eventually authenticate after auth service recovers
                headers = await client.security_manager.get_auth_heathes()
                assert "Authorization" in headers
                assert "recovered-token" in headers["Authorization"]

    @pytest.mark.chaos
    @skip_if_no_integration_env()
    async def test_partial_service_degradation(self, integration_test_base):
        """Test handling of partial service degradation."""
        config = AgentClientConfig(**integration_test_base.get_test_config())

        async with UnifiedKeiAgentClient(config) as client:
            with patch.object(client, '_make_request') as mock_request:
                # Some endpoints work, others fail
                def degraded_service(*args, **kwargs):
                    url = args[1] if len(args) > 1 else kwargs.get('url', '')
                    if 'status' in url:
                        return {"status": "degraded_but_working"}
                    else:
                        raise CommunicationError("Endpoint unavailable")

                mock_request.side_effect = degraded_service

                # Status endpoint should work
                response = await client.get_agent_status()
                assert response["status"] == "degraded_but_working"

                # Other endpoints should fail
                with pytest.raises(CommunicationError):
                    await client.send_message("test", {})


@pytest.mark.chaos
@pytest.mark.skipif(
    not INTEGRATION_TEST_CONFIG.get("chaos_testing", False),
    reason="Chaos testing disabled"
)
class TestResourceChaos:
    """Chaos engineering tests for resource exhaustion scenarios."""

    @pytest.mark.chaos
    @skip_if_no_integration_env()
    async def test_memory_pressure_handling(self, integration_test_base):
        """Test behavior under memory pressure conditions."""
        config = AgentClientConfig(**integration_test_base.get_test_config())

        async with UnifiedKeiAgentClient(config) as client:
            # Simulate memory pressure by creating large responses
            with patch.object(client, '_make_request') as mock_request:
                # Return large response to simulate memory pressure
                large_data = {"data": "x" * 1000000}  # 1MB of data
                mock_request.return_value = large_data

                # Should handle large responses gracefully
                response = await client.get_agent_status()
                assert "data" in response
                assert len(response["data"]) == 1000000

    @pytest.mark.chaos
    @skip_if_no_integration_env()
    async def test_connection_pool_exhaustion(self, integration_test_base):
        """Test handling of connection pool exhaustion."""
        config = AgentClientConfig(**integration_test_base.get_test_config())

        async with UnifiedKeiAgentClient(config) as client:
            # Make many concurrent requests to exhaust connection pool
            with patch.object(client, '_make_request') as mock_request:
                mock_request.return_value = {"status": "ok"}

                # Create more concurrent requests than typical pool size
                tasks = [
                    client.get_agent_status()
                    for _ in range(100)
                ]

                # Should handle all requests without errors
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Most should succeed, some might fail due to pool limits
                successes = [r for r in results if isinstance(r, dict)]
                errors = [r for r in results if isinstance(r, Exception)]

                assert len(successes) > 50  # At least half should succeed
                assert len(successes) + len(errors) == 100

    @pytest.mark.chaos
    @skip_if_no_integration_env()
    async def test_cpu_intensive_operations(self, integration_test_base):
        """Test behavior during CPU-intensive operations."""
        config = AgentClientConfig(**integration_test_base.get_test_config())

        async with UnifiedKeiAgentClient(config) as client:
            with patch.object(client, '_make_request') as mock_request:
                # Simulate CPU-intensive response processing
                def cpu_intensive_response(*args, **kwargs):
                    # Simulate CPU work
                    result = 0
                    for i in range(100000):
                        result += i * i
                    return {"status": "cpu_intensive_complete", "result": result}

                mock_request.side_effect = cpu_intensive_response

                start_time = time.time()
                response = await client.get_agent_status()
                processing_time = time.time() - start_time

                assert response["status"] == "cpu_intensive_complete"
                assert processing_time > 0.01  # Should take some time


@pytest.mark.chaos
@pytest.mark.skipif(
    not INTEGRATION_TEST_CONFIG.get("chaos_testing", False),
    reason="Chaos testing disabled"
)
class TestConcurrentChaos:
    """Chaos engineering tests for concurrent failure scenarios."""

    @pytest.mark.chaos
    @skip_if_no_integration_env()
    async def test_concurrent_network_and_auth_failures(self, integration_test_base):
        """Test handling of simultaneous network and authentication failures."""
        security_config = SecurityConfig(
            auth_type=Authtypee.BEARER,
            api_token=integration_test_base.credentials["api_token"],
            token_refresh_enabled=True
        )

        config = AgentClientConfig(
            **integration_test_base.get_test_config(),
            security=security_config
        )

        async with UnifiedKeiAgentClient(config) as client:
            with patch.object(client, '_make_request') as mock_request:
                with patch.object(client.security_manager, '_refresh_bearer_token') as mock_refresh:
                    # Both network and auth fail initially, then recover
                    mock_request.side_effect = [
                        ConnectionError("Network down"),
                        SecurityError("Auth failed"),
                        {"status": "recovered"}
                    ]
                    mock_refresh.return_value = "new-token"

                    # Should eventually recover from both failures
                    response = await client.get_agent_status()
                    assert response["status"] == "recovered"

    @pytest.mark.chaos
    @skip_if_no_integration_env()
    async def test_cascading_failure_recovery(self, integration_test_base):
        """Test recovery from cascading failure scenarios."""
        config = AgentClientConfig(**integration_test_base.get_test_config())

        async with UnifiedKeiAgentClient(config) as client:
            failure_sequence = [
                ConnectionError("Primary service down"),
                ConnectionError("Backup service down"),
                ConnectionError("Cache service down"),
                {"status": "all_services_recovered"}
            ]

            with patch.object(client, '_make_request') as mock_request:
                mock_request.side_effect = failure_sequence

                # Should recover after all services come back online
                response = await client.get_agent_status()
                assert response["status"] == "all_services_recovered"
                assert mock_request.call_count == 4

    @pytest.mark.chaos
    @skip_if_no_integration_env()
    async def test_circuit_breaker_under_chaos(self, integration_test_base):
        """Test circuit breaker behavior under chaotic conditions."""
        config = AgentClientConfig(**integration_test_base.get_test_config())

        async with UnifiedKeiAgentClient(config) as client:
            with patch.object(client, '_make_request') as mock_request:
                # Simulate high failure rate to trigger circuit breaker
                mock_request.side_effect = [
                    CommunicationError("Service error") for _ in range(10)
                ] + [{"status": "recovered"}]

                # First few requests should fail
                for _ in range(5):
                    with pytest.raises(CommunicationError):
                        await client.get_agent_status()

                # Circuit breaker should open after repeated failures
                with pytest.raises((CommunicationError, CircuitBreakerOpenError)):
                    await client.get_agent_status()


@pytest.mark.chaos
@pytest.mark.skipif(
    not INTEGRATION_TEST_CONFIG.get("chaos_testing", False),
    reason="Chaos testing disabled"
)
class TestRecoveryMechanisms:
    """Tests for system recovery and self-healing capabilities."""

    @pytest.mark.chaos
    @skip_if_no_integration_env()
    async def test_automatic_retry_mechanisms(self, integration_test_base):
        """Test automatic retry mechanisms under failure conditions."""
        config = AgentClientConfig(
            **integration_test_base.get_test_config(),
            max_retries=5,
            retry_delay=0.1
        )

        async with UnifiedKeiAgentClient(config) as client:
            with patch.object(client, '_make_request') as mock_request:
                # Fail 4 times, then succeed
                mock_request.side_effect = [
                    CommunicationError("Retry 1"),
                    CommunicationError("Retry 2"),
                    CommunicationError("Retry 3"),
                    CommunicationError("Retry 4"),
                    {"status": "success_after_retries"}
                ]

                start_time = time.time()
                response = await client.get_agent_status()
                total_time = time.time() - start_time

                assert response["status"] == "success_after_retries"
                assert mock_request.call_count == 5
                assert total_time >= 0.4  # Should include retry delays

    @pytest.mark.chaos
    @skip_if_no_integration_env()
    async def test_health_check_recovery(self, integration_test_base):
        """Test health check-based recovery mechanisms."""
        config = AgentClientConfig(**integration_test_base.get_test_config())

        async with UnifiedKeiAgentClient(config) as client:
            with patch.object(client, '_health_check') as mock_health:
                with patch.object(client, '_make_request') as mock_request:
                    # Health check fails, then passes
                    mock_health.side_effect = [False, False, True]
                    mock_request.return_value = {"status": "healthy"}

                    # Should wait for health check to pass
                    response = await client.get_agent_status()
                    assert response["status"] == "healthy"
                    assert mock_health.call_count >= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "chaos"])
