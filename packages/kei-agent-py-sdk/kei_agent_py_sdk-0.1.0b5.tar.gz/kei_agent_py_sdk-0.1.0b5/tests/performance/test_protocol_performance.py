# tests/performance/test_protocol_performance.py
"""
Protocol-specific performance benchmarks for KEI-Agent Python SDK.

These benchmarks measure performance characteristics of:
- RPC protocol operations
- Stream protocol throughput
- Bus protocol message handling
- MCP protocol tool execution
- Protocol switching overhead
- Connection pooling efficiency
"""

import asyncio
import time
from unittest.mock import AsyncMock, patch

import pytest

from kei_agent import UnifiedKeiAgentClient, AgentClientConfig
from kei_agent.protocol_types import ProtocolConfig, Protocoltypee
from . import (
    skip_if_performance_disabled, performance_test,
    PerformanceBenchmark, PerformanceBaseline,
    PERFORMANCE_CONFIG
)


class RPCPerformanceBenchmark(PerformanceBenchmark):
    """Benchmark for RPC protocol performance."""

    def __init__(self):
        super().__init__("rpc_protocol", "RPC protocol request/response performance")
        self.client = None

    async def setup(self):
        """Setup RPC client."""
        config = AgentClientConfig(
            base_url="https://api.example.com",
            api_token="rpc-benchmark-token",
            agent_id="rpc-benchmark-agent"
        )

        protocol_config = ProtocolConfig(
            rpc_enabled=True,
            stream_enabled=False,
            bus_enabled=False,
            mcp_enabled=False,
            preferred_protocol="rpc"
        )

        self.client = UnifiedKeiAgentClient(config)
        await self.client.__aenter__()

    async def teardown(self):
        """Cleanup RPC client."""
        if self.client:
            await self.client.__aexit__(None, None, None)

    async def run_single_iteration(self):
        """Run single RPC call."""
        with patch.object(self.client, '_make_rpc_call') as mock_rpc:
            mock_rpc.return_value = {
                "result": "success",
                "data": {"message": "RPC benchmark response"},
                "execution_time": 0.001
            }

            response = await self.client.call_remote_method(
                "benchmark_service",
                "echo",
                {"message": "benchmark"}
            )
            return response


class StreamPerformanceBenchmark(PerformanceBenchmark):
    """Benchmark for Stream protocol performance."""

    def __init__(self):
        super().__init__("stream_protocol", "Stream protocol throughput performance")
        self.client = None
        self.stream = None

    async def setup(self):
        """Setup Stream client."""
        config = AgentClientConfig(
            base_url="https://api.example.com",
            api_token="stream-benchmark-token",
            agent_id="stream-benchmark-agent"
        )

        self.client = UnifiedKeiAgentClient(config)
        await self.client.__aenter__()

        # Mock stream connection
        self.stream = AsyncMock()
        self.stream.send = AsyncMock()
        self.stream.receive = AsyncMock(return_value={"status": "received"})

    async def teardown(self):
        """Cleanup Stream client."""
        if self.client:
            await self.client.__aexit__(None, None, None)

    async def run_single_iteration(self):
        """Run single stream operation."""
        with patch.object(self.client, '_create_stream_connection', return_value=self.stream):
            # Send data through stream
            await self.client.send_stream_data(self.stream, {
                "type": "benchmark",
                "data": "x" * 1024,  # 1KB payload
                "timestamp": time.time()
            })

            # Receive response
            response = await self.client.receive_stream_data(self.stream)
            return response


class BusPerformanceBenchmark(PerformanceBenchmark):
    """Benchmark for Bus protocol performance."""

    def __init__(self):
        super().__init__("bus_protocol", "Bus protocol message handling performance")
        self.client = None
        self.message_count = 0

    async def setup(self):
        """Setup Bus client."""
        config = AgentClientConfig(
            base_url="https://api.example.com",
            api_token="bus-benchmark-token",
            agent_id="bus-benchmark-agent"
        )

        self.client = UnifiedKeiAgentClient(config)
        await self.client.__aenter__()
        self.message_count = 0

    async def teardown(self):
        """Cleanup Bus client."""
        if self.client:
            await self.client.__aexit__(None, None, None)

    async def run_single_iteration(self):
        """Run single bus operation."""
        with patch.object(self.client, '_publish_to_topic') as mock_publish:
            with patch.object(self.client, '_subscribe_to_topic') as mock_subscribe:
                mock_publish.return_value = True

                # Publish message
                message = {
                    "id": f"benchmark-{self.message_count}",
                    "type": "benchmark",
                    "payload": {"data": "x" * 512},  # 512B payload
                    "timestamp": time.time()
                }

                await self.client.publish("benchmark.topic", message)
                self.message_count += 1

                return message


class MCPPerformanceBenchmark(PerformanceBenchmark):
    """Benchmark for MCP protocol performance."""

    def __init__(self):
        super().__init__("mcp_protocol", "MCP protocol tool execution performance")
        self.client = None

    async def setup(self):
        """Setup MCP client."""
        config = AgentClientConfig(
            base_url="https://api.example.com",
            api_token="mcp-benchmark-token",
            agent_id="mcp-benchmark-agent"
        )

        self.client = UnifiedKeiAgentClient(config)
        await self.client.__aenter__()

    async def teardown(self):
        """Cleanup MCP client."""
        if self.client:
            await self.client.__aexit__(None, None, None)

    async def run_single_iteration(self):
        """Run single MCP tool execution."""
        with patch.object(self.client, '_execute_mcp_tool') as mock_execute:
            mock_execute.return_value = {
                "result": "success",
                "output": "Benchmark tool executed successfully",
                "execution_time": 0.005,
                "metadata": {"tool": "benchmark", "version": "1.0"}
            }

            response = await self.client.execute_tool(
                "benchmark_tool",
                "calculate",
                {"operation": "add", "a": 5, "b": 3}
            )
            return response


class ProtocolSwitchingBenchmark(PerformanceBenchmark):
    """Benchmark for protocol switching overhead."""

    def __init__(self):
        super().__init__("protocol_switching", "Protocol switching overhead")
        self.client = None
        self.protocols = ["rpc", "stream", "bus", "mcp"]
        self.current_protocol_index = 0

    async def setup(self):
        """Setup multi-protocol client."""
        config = AgentClientConfig(
            base_url="https://api.example.com",
            api_token="switching-benchmark-token",
            agent_id="switching-benchmark-agent"
        )

        self.client = UnifiedKeiAgentClient(config)
        await self.client.__aenter__()

    async def teardown(self):
        """Cleanup client."""
        if self.client:
            await self.client.__aexit__(None, None, None)

    async def run_single_iteration(self):
        """Run single protocol switch."""
        # Switch to next protocol
        current_protocol = self.protocols[self.current_protocol_index]
        next_protocol = self.protocols[(self.current_protocol_index + 1) % len(self.protocols)]

        with patch.object(self.client, '_switch_protocol') as mock_switch:
            mock_switch.return_value = True

            # Simulate protocol switch
            switch_start = time.time()
            await self.client.switch_protocol(next_protocol)
            switch_end = time.time()

            self.current_protocol_index = (self.current_protocol_index + 1) % len(self.protocols)

            return {
                "from_protocol": current_protocol,
                "to_protocol": next_protocol,
                "switch_time": switch_end - switch_start
            }


@pytest.mark.performance
class TestProtocolPerformance:
    """Protocol-specific performance tests."""

    def setup_method(self):
        """Setup performance baseline manager."""
        self.baseline = PerformanceBaseline()

    @pytest.mark.performance
    @skip_if_performance_disabled()
    @performance_test("rpc_protocol", {"max_time": 0.5, "max_memory_mb": 30})
    async def test_rpc_protocol_performance(self):
        """Test RPC protocol performance."""
        benchmark = RPCPerformanceBenchmark()
        metrics = await benchmark.run_benchmark()

        # Validate against performance budget
        assert benchmark.validate_performance_budget(metrics), \
            f"RPC protocol exceeded performance budget: {metrics.duration:.3f}s, {metrics.memory_usage_mb:.1f}MB"

        # Check for regression
        regression = self.baseline.check_regression(metrics)
        if regression["has_regression"]:
            pytest.fail(f"RPC performance regression detected: {regression}")

        # Update baseline
        if not regression["has_regression"]:
            self.baseline.update_baseline(metrics)

        # Calculate RPC-specific metrics
        rpc_calls_per_second = metrics.iterations / metrics.duration

        print(f"\n📊 RPC Protocol Performance:")
        print(f"   Duration: {metrics.duration:.3f}s")
        print(f"   Memory: {metrics.memory_usage_mb:.1f}MB")
        print(f"   RPC calls per second: {rpc_calls_per_second:.1f}")

        # Validate RPC performance expectations
        assert rpc_calls_per_second > 100, f"RPC throughput too low: {rpc_calls_per_second:.1f} calls/s"

    @pytest.mark.performance
    @skip_if_performance_disabled()
    @performance_test("stream_protocol", {"max_time": 1.0, "max_memory_mb": 40})
    async def test_stream_protocol_performance(self):
        """Test Stream protocol performance."""
        benchmark = StreamPerformanceBenchmark()
        metrics = await benchmark.run_benchmark()

        # Validate against performance budget
        assert benchmark.validate_performance_budget(metrics), \
            f"Stream protocol exceeded performance budget: {metrics.duration:.3f}s, {metrics.memory_usage_mb:.1f}MB"

        # Check for regression
        regression = self.baseline.check_regression(metrics)
        if regression["has_regression"]:
            pytest.fail(f"Stream performance regression detected: {regression}")

        # Update baseline
        if not regression["has_regression"]:
            self.baseline.update_baseline(metrics)

        # Calculate stream-specific metrics
        data_throughput_mb = (metrics.iterations * 1024) / (1024 * 1024) / metrics.duration  # MB/s

        print(f"\n📊 Stream Protocol Performance:")
        print(f"   Duration: {metrics.duration:.3f}s")
        print(f"   Memory: {metrics.memory_usage_mb:.1f}MB")
        print(f"   Data throughput: {data_throughput_mb:.2f} MB/s")

        # Validate stream performance expectations
        assert data_throughput_mb > 1.0, f"Stream throughput too low: {data_throughput_mb:.2f} MB/s"

    @pytest.mark.performance
    @skip_if_performance_disabled()
    @performance_test("bus_protocol", {"max_time": 0.8, "max_memory_mb": 35})
    async def test_bus_protocol_performance(self):
        """Test Bus protocol performance."""
        benchmark = BusPerformanceBenchmark()
        metrics = await benchmark.run_benchmark()

        # Validate against performance budget
        assert benchmark.validate_performance_budget(metrics), \
            f"Bus protocol exceeded performance budget: {metrics.duration:.3f}s, {metrics.memory_usage_mb:.1f}MB"

        # Check for regression
        regression = self.baseline.check_regression(metrics)
        if regression["has_regression"]:
            pytest.fail(f"Bus performance regression detected: {regression}")

        # Update baseline
        if not regression["has_regression"]:
            self.baseline.update_baseline(metrics)

        # Calculate bus-specific metrics
        messages_per_second = metrics.iterations / metrics.duration

        print(f"\n📊 Bus Protocol Performance:")
        print(f"   Duration: {metrics.duration:.3f}s")
        print(f"   Memory: {metrics.memory_usage_mb:.1f}MB")
        print(f"   Messages per second: {messages_per_second:.1f}")

        # Validate bus performance expectations
        assert messages_per_second > 50, f"Bus throughput too low: {messages_per_second:.1f} messages/s"

    @pytest.mark.performance
    @skip_if_performance_disabled()
    @performance_test("mcp_protocol", {"max_time": 1.5, "max_memory_mb": 45})
    async def test_mcp_protocol_performance(self):
        """Test MCP protocol performance."""
        benchmark = MCPPerformanceBenchmark()
        metrics = await benchmark.run_benchmark()

        # Validate against performance budget
        assert benchmark.validate_performance_budget(metrics), \
            f"MCP protocol exceeded performance budget: {metrics.duration:.3f}s, {metrics.memory_usage_mb:.1f}MB"

        # Check for regression
        regression = self.baseline.check_regression(metrics)
        if regression["has_regression"]:
            pytest.fail(f"MCP performance regression detected: {regression}")

        # Update baseline
        if not regression["has_regression"]:
            self.baseline.update_baseline(metrics)

        # Calculate MCP-specific metrics
        tool_executions_per_second = metrics.iterations / metrics.duration

        print(f"\n📊 MCP Protocol Performance:")
        print(f"   Duration: {metrics.duration:.3f}s")
        print(f"   Memory: {metrics.memory_usage_mb:.1f}MB")
        print(f"   Tool executions per second: {tool_executions_per_second:.1f}")

        # Validate MCP performance expectations
        assert tool_executions_per_second > 20, f"MCP throughput too low: {tool_executions_per_second:.1f} executions/s"

    @pytest.mark.performance
    @skip_if_performance_disabled()
    @performance_test("protocol_switching", {"max_time": 2.0, "max_memory_mb": 50})
    async def test_protocol_switching_performance(self):
        """Test protocol switching overhead."""
        benchmark = ProtocolSwitchingBenchmark()
        metrics = await benchmark.run_benchmark(iterations=20)  # More switches for better measurement

        # Validate against performance budget
        assert benchmark.validate_performance_budget(metrics), \
            f"Protocol switching exceeded performance budget: {metrics.duration:.3f}s, {metrics.memory_usage_mb:.1f}MB"

        # Check for regression
        regression = self.baseline.check_regression(metrics)
        if regression["has_regression"]:
            pytest.fail(f"Protocol switching performance regression detected: {regression}")

        # Update baseline
        if not regression["has_regression"]:
            self.baseline.update_baseline(metrics)

        # Calculate switching-specific metrics
        avg_switch_time = metrics.duration / metrics.iterations
        switches_per_second = metrics.iterations / metrics.duration

        print(f"\n📊 Protocol Switching Performance:")
        print(f"   Duration: {metrics.duration:.3f}s")
        print(f"   Memory: {metrics.memory_usage_mb:.1f}MB")
        print(f"   Average switch time: {avg_switch_time:.3f}s")
        print(f"   Switches per second: {switches_per_second:.1f}")

        # Validate switching performance expectations
        assert avg_switch_time < 0.1, f"Protocol switch too slow: {avg_switch_time:.3f}s"

    @pytest.mark.performance
    @skip_if_performance_disabled()
    async def test_protocol_comparison(self):
        """Compare performance across all protocols."""
        protocols = [
            ("RPC", RPCPerformanceBenchmark()),
            ("Stream", StreamPerformanceBenchmark()),
            ("Bus", BusPerformanceBenchmark()),
            ("MCP", MCPPerformanceBenchmark())
        ]

        results = {}

        # Run benchmarks for each protocol
        for protocol_name, benchmark in protocols:
            metrics = await benchmark.run_benchmark(iterations=5)  # Fewer iterations for comparison
            results[protocol_name] = {
                "duration": metrics.duration,
                "memory": metrics.memory_usage_mb,
                "throughput": metrics.iterations / metrics.duration
            }

        # Print comparison
        print(f"\n📊 Protocol Performance Comparison:")
        print(f"{'Protocol':<10} {'Duration':<10} {'Memory':<10} {'Throughput':<12}")
        print("-" * 50)

        for protocol, data in results.items():
            print(f"{protocol:<10} {data['duration']:<10.3f} {data['memory']:<10.1f} {data['throughput']:<12.1f}")

        # Find best performing protocol for each metric
        fastest = min(results.items(), key=lambda x: x[1]['duration'])
        most_efficient = min(results.items(), key=lambda x: x[1]['memory'])
        highest_throughput = max(results.items(), key=lambda x: x[1]['throughput'])

        print(f"\n🏆 Performance Leaders:")
        print(f"   Fastest: {fastest[0]} ({fastest[1]['duration']:.3f}s)")
        print(f"   Most memory efficient: {most_efficient[0]} ({most_efficient[1]['memory']:.1f}MB)")
        print(f"   Highest throughput: {highest_throughput[0]} ({highest_throughput[1]['throughput']:.1f} ops/s)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "performance"])
