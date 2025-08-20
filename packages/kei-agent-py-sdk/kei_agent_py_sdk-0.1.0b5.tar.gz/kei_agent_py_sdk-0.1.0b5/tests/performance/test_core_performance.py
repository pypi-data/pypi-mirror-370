# tests/performance/test_core_performance.py
"""
Core performance benchmarks for KEI-Agent Python SDK.

These benchmarks establish baseline performance metrics for:
- Client initialization and teardown
- Basic request/response operations
- Authentication flows
- Message serialization/deserialization
- Connection management
- Memory usage patterns
"""

import asyncio
import time
from unittest.mock import AsyncMock, patch

import pytest

from kei_agent import UnifiedKeiAgentClient, AgentClientConfig
from kei_agent.protocol_types import SecurityConfig, Authtypee
from . import (
    skip_if_performance_disabled, performance_test,
    PerformanceBenchmark, PerformanceBaseline, PerformanceMetrics,
    PERFORMANCE_CONFIG, PERFORMANCE_BUDGETS
)


class ClientInitializationBenchmark(PerformanceBenchmark):
    """Benchmark for client initialization performance."""

    def __init__(self):
        super().__init__("client_initialization", "Client initialization and teardown")
        self.config = None

    async def setup(self):
        """Setup benchmark configuration."""
        self.config = AgentClientConfig(
            base_url="https://api.example.com",
            api_token="benchmark-token-123",
            agent_id="benchmark-agent",
            timeout=30,
            max_retries=3
        )

    async def run_single_iteration(self):
        """Run single client initialization."""
        async with UnifiedKeiAgentClient(self.config) as client:
            # Simulate basic initialization work
            await asyncio.sleep(0.001)  # Minimal work
            return client


class SimpleRequestBenchmark(PerformanceBenchmark):
    """Benchmark for simple request/response operations."""

    def __init__(self):
        super().__init__("simple_request", "Simple request/response operation")
        self.client = None

    async def setup(self):
        """Setup client for requests."""
        config = AgentClientConfig(
            base_url="https://api.example.com",
            api_token="benchmark-token-123",
            agent_id="benchmark-agent"
        )
        self.client = UnifiedKeiAgentClient(config)
        await self.client.__aenter__()

    async def teardown(self):
        """Cleanup client."""
        if self.client:
            await self.client.__aexit__(None, None, None)

    async def run_single_iteration(self):
        """Run single request."""
        with patch.object(self.client, '_make_request') as mock_request:
            mock_request.return_value = {"status": "ok", "data": {"message": "benchmark"}}
            response = await self.client.get_agent_status()
            return response


class AuthenticationBenchmark(PerformanceBenchmark):
    """Benchmark for authentication operations."""

    def __init__(self):
        super().__init__("authentication", "Authentication flow performance")
        self.security_manager = None

    async def setup(self):
        """Setup security manager."""
        from kei_agent.security_manager import SecurityManager

        security_config = SecurityConfig(
            auth_type=Authtypee.BEARER,
            api_token="benchmark-token-123456789"
        )
        self.security_manager = SecurityManager(security_config)

    async def run_single_iteration(self):
        """Run single authentication."""
        headers = await self.security_manager.get_auth_heathes()
        return headers


class MessageSerializationBenchmark(PerformanceBenchmark):
    """Benchmark for message serialization/deserialization."""

    def __init__(self):
        super().__init__("message_serialization", "Message serialization performance")
        self.test_data = None

    async def setup(self):
        """Setup test data."""
        self.test_data = {
            "message_id": "benchmark-msg-123",
            "recipient": "benchmark-agent",
            "content": {
                "type": "benchmark",
                "data": "x" * 1000,  # 1KB of data
                "metadata": {
                    "timestamp": time.time(),
                    "priority": "normal",
                    "tags": ["benchmark", "performance", "test"]
                }
            },
            "attachments": [
                {"name": f"file_{i}.txt", "size": 1024, "type": "text/plain"}
                for i in range(10)
            ]
        }

    async def run_single_iteration(self):
        """Run single serialization/deserialization cycle."""
        import json

        # Serialize
        serialized = json.dumps(self.test_data)

        # Deserialize
        deserialized = json.loads(serialized)

        return len(serialized)


class ConcurrentRequestsBenchmark(PerformanceBenchmark):
    """Benchmark for concurrent request handling."""

    def __init__(self, concurrent_count: int = 10):
        super().__init__("concurrent_requests", f"Concurrent requests ({concurrent_count})")
        self.concurrent_count = concurrent_count
        self.client = None

    async def setup(self):
        """Setup client for concurrent requests."""
        config = AgentClientConfig(
            base_url="https://api.example.com",
            api_token="benchmark-token-123",
            agent_id="benchmark-agent"
        )
        self.client = UnifiedKeiAgentClient(config)
        await self.client.__aenter__()

    async def teardown(self):
        """Cleanup client."""
        if self.client:
            await self.client.__aexit__(None, None, None)

    async def run_single_iteration(self):
        """Run concurrent requests."""
        with patch.object(self.client, '_make_request') as mock_request:
            mock_request.return_value = {"status": "ok", "request_id": "benchmark"}

            # Create concurrent tasks
            tasks = [
                self.client.get_agent_status()
                for _ in range(self.concurrent_count)
            ]

            # Execute concurrently
            results = await asyncio.gather(*tasks)
            return len(results)


@pytest.mark.performance
class TestCorePerformance:
    """Core performance tests with baseline validation."""

    def setup_method(self):
        """Setup performance baseline manager."""
        self.baseline = PerformanceBaseline()

    @pytest.mark.performance
    @skip_if_performance_disabled()
    @performance_test("client_initialization", {"max_time": 1.0, "max_memory_mb": 50})
    async def test_client_initialization_performance(self):
        """Test client initialization performance."""
        benchmark = ClientInitializationBenchmark()
        metrics = await benchmark.run_benchmark()

        # Validate against performance budget
        assert benchmark.validate_performance_budget(metrics), \
            f"Client initialization exceeded performance budget: {metrics.duration:.3f}s, {metrics.memory_usage_mb:.1f}MB"

        # Check for regression
        regression = self.baseline.check_regression(metrics)
        if regression["has_regression"]:
            pytest.fail(f"Performance regression detected: {regression}")

        # Update baseline if this is a new test or improvement
        if not regression["has_regression"]:
            self.baseline.update_baseline(metrics)

        # Log performance metrics
        print(f"\n📊 Client Initialization Performance:")
        print(f"   Duration: {metrics.duration:.3f}s")
        print(f"   Memory: {metrics.memory_usage_mb:.1f}MB")
        print(f"   Iterations: {metrics.iterations}")

    @pytest.mark.performance
    @skip_if_performance_disabled()
    @performance_test("simple_request", {"max_time": 0.1, "max_memory_mb": 10})
    async def test_simple_request_performance(self):
        """Test simple request performance."""
        benchmark = SimpleRequestBenchmark()
        metrics = await benchmark.run_benchmark()

        # Validate against performance budget
        assert benchmark.validate_performance_budget(metrics), \
            f"Simple request exceeded performance budget: {metrics.duration:.3f}s, {metrics.memory_usage_mb:.1f}MB"

        # Check for regression
        regression = self.baseline.check_regression(metrics)
        if regression["has_regression"]:
            pytest.fail(f"Performance regression detected: {regression}")

        # Update baseline
        if not regression["has_regression"]:
            self.baseline.update_baseline(metrics)

        # Log performance metrics
        print(f"\n📊 Simple Request Performance:")
        print(f"   Duration: {metrics.duration:.3f}s")
        print(f"   Memory: {metrics.memory_usage_mb:.1f}MB")
        print(f"   Requests per second: {metrics.iterations / metrics.duration:.1f}")

    @pytest.mark.performance
    @skip_if_performance_disabled()
    @performance_test("authentication", {"max_time": 0.5, "max_memory_mb": 20})
    async def test_authentication_performance(self):
        """Test authentication performance."""
        benchmark = AuthenticationBenchmark()
        metrics = await benchmark.run_benchmark()

        # Validate against performance budget
        assert benchmark.validate_performance_budget(metrics), \
            f"Authentication exceeded performance budget: {metrics.duration:.3f}s, {metrics.memory_usage_mb:.1f}MB"

        # Check for regression
        regression = self.baseline.check_regression(metrics)
        if regression["has_regression"]:
            pytest.fail(f"Performance regression detected: {regression}")

        # Update baseline
        if not regression["has_regression"]:
            self.baseline.update_baseline(metrics)

        # Log performance metrics
        print(f"\n📊 Authentication Performance:")
        print(f"   Duration: {metrics.duration:.3f}s")
        print(f"   Memory: {metrics.memory_usage_mb:.1f}MB")
        print(f"   Auth operations per second: {metrics.iterations / metrics.duration:.1f}")

    @pytest.mark.performance
    @skip_if_performance_disabled()
    @performance_test("message_serialization", {"max_time": 0.2, "max_memory_mb": 15})
    async def test_message_serialization_performance(self):
        """Test message serialization performance."""
        benchmark = MessageSerializationBenchmark()
        metrics = await benchmark.run_benchmark()

        # Validate against performance budget
        assert benchmark.validate_performance_budget(metrics), \
            f"Message serialization exceeded performance budget: {metrics.duration:.3f}s, {metrics.memory_usage_mb:.1f}MB"

        # Check for regression
        regression = self.baseline.check_regression(metrics)
        if regression["has_regression"]:
            pytest.fail(f"Performance regression detected: {regression}")

        # Update baseline
        if not regression["has_regression"]:
            self.baseline.update_baseline(metrics)

        # Log performance metrics
        print(f"\n📊 Message Serialization Performance:")
        print(f"   Duration: {metrics.duration:.3f}s")
        print(f"   Memory: {metrics.memory_usage_mb:.1f}MB")
        print(f"   Serializations per second: {metrics.iterations / metrics.duration:.1f}")

    @pytest.mark.performance
    @skip_if_performance_disabled()
    @performance_test("concurrent_requests", {"max_time": 5.0, "max_memory_mb": 100})
    async def test_concurrent_requests_performance(self):
        """Test concurrent request handling performance."""
        concurrent_count = PERFORMANCE_CONFIG["concurrent_users"]
        benchmark = ConcurrentRequestsBenchmark(concurrent_count)
        metrics = await benchmark.run_benchmark(iterations=5)  # Fewer iterations for concurrent test

        # Validate against performance budget
        assert benchmark.validate_performance_budget(metrics), \
            f"Concurrent requests exceeded performance budget: {metrics.duration:.3f}s, {metrics.memory_usage_mb:.1f}MB"

        # Check for regression
        regression = self.baseline.check_regression(metrics)
        if regression["has_regression"]:
            pytest.fail(f"Performance regression detected: {regression}")

        # Update baseline
        if not regression["has_regression"]:
            self.baseline.update_baseline(metrics)

        # Calculate throughput
        total_requests = metrics.iterations * concurrent_count
        throughput = total_requests / metrics.duration

        # Log performance metrics
        print(f"\n📊 Concurrent Requests Performance:")
        print(f"   Duration: {metrics.duration:.3f}s")
        print(f"   Memory: {metrics.memory_usage_mb:.1f}MB")
        print(f"   Concurrent users: {concurrent_count}")
        print(f"   Total requests: {total_requests}")
        print(f"   Throughput: {throughput:.1f} requests/second")

    @pytest.mark.performance
    @skip_if_performance_disabled()
    async def test_memory_usage_patterns(self):
        """Test memory usage patterns during operations."""
        from . import PerformanceMonitor

        monitor = PerformanceMonitor()
        monitor.start_monitoring()

        # Simulate various operations
        config = AgentClientConfig(
            base_url="https://api.example.com",
            api_token="memory-test-token",
            agent_id="memory-test-agent"
        )

        # Client creation
        async with UnifiedKeiAgentClient(config) as client:
            monitor.record_measurement("client_created")

            # Mock multiple operations
            with patch.object(client, '_make_request') as mock_request:
                mock_request.return_value = {"status": "ok"}

                # Multiple requests
                for i in range(50):
                    await client.get_agent_status()
                    if i % 10 == 0:
                        monitor.record_measurement(f"requests_{i}")

        metrics = monitor.stop_monitoring()

        # Analyze memory usage pattern
        measurements = metrics.metadata["measurements"]
        max_memory_delta = max(m["memory_delta_mb"] for m in measurements)

        print(f"\n📊 Memory Usage Analysis:")
        print(f"   Peak memory delta: {max_memory_delta:.1f}MB")
        print(f"   Final memory delta: {metrics.memory_usage_mb:.1f}MB")
        print(f"   Memory measurements: {len(measurements)}")

        # Validate memory doesn't grow excessively
        assert max_memory_delta < 100, f"Memory usage too high: {max_memory_delta:.1f}MB"

    @pytest.mark.performance
    @skip_if_performance_disabled()
    async def test_performance_under_load(self):
        """Test performance degradation under sustained load."""
        config = AgentClientConfig(
            base_url="https://api.example.com",
            api_token="load-test-token",
            agent_id="load-test-agent"
        )

        duration = PERFORMANCE_CONFIG["test_duration"]
        start_time = time.time()
        request_count = 0
        response_times = []

        async with UnifiedKeiAgentClient(config) as client:
            with patch.object(client, '_make_request') as mock_request:
                mock_request.return_value = {"status": "ok"}

                # Run requests for specified duration
                while time.time() - start_time < duration:
                    request_start = time.time()
                    await client.get_agent_status()
                    request_end = time.time()

                    response_times.append(request_end - request_start)
                    request_count += 1

                    # Small delay to prevent overwhelming
                    await asyncio.sleep(0.01)

        # Analyze performance under load
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        throughput = request_count / duration

        print(f"\n📊 Load Test Results:")
        print(f"   Duration: {duration}s")
        print(f"   Total requests: {request_count}")
        print(f"   Throughput: {throughput:.1f} requests/second")
        print(f"   Average response time: {avg_response_time:.3f}s")
        print(f"   Max response time: {max_response_time:.3f}s")

        # Validate performance under load
        assert avg_response_time < 0.1, f"Average response time too high: {avg_response_time:.3f}s"
        assert max_response_time < 1.0, f"Max response time too high: {max_response_time:.3f}s"
        assert throughput > 10, f"Throughput too low: {throughput:.1f} requests/second"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "performance"])
