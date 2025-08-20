# tests/chaos/chaos_framework.py
"""
Chaos Engineering Framework for KEI-Agent Python SDK.

This framework provides the foundation for chaos engineering tests that validate
system resilience and fault tolerance under various failure conditions.
"""

import asyncio
import contextlib
import logging
import random
import time
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Callable, AsyncGenerator, Generator
from unittest.mock import patch, MagicMock
import psutil
import socket
import subprocess
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ChaosMetrics:
    """Metrics collected during chaos tests."""

    test_name: str
    start_time: float
    end_time: Optional[float] = None
    failure_injected_at: Optional[float] = None
    recovery_time: Optional[float] = None
    errors_during_chaos: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    system_metrics: Dict[str, Any] = field(default_factory=dict)
    custom_metrics: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> float:
        """Total test duration."""
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time

    @property
    def time_to_recovery(self) -> Optional[float]:
        """Time from failure injection to recovery."""
        if self.failure_injected_at and self.recovery_time:
            return self.recovery_time - self.failure_injected_at
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "test_name": self.test_name,
            "duration": self.duration,
            "time_to_recovery": self.time_to_recovery,
            "errors_during_chaos": self.errors_during_chaos,
            "successful_operations": self.successful_operations,
            "failed_operations": self.failed_operations,
            "success_rate": self.successful_operations / (self.successful_operations + self.failed_operations) if (self.successful_operations + self.failed_operations) > 0 else 0,
            "system_metrics": self.system_metrics,
            "custom_metrics": self.custom_metrics
        }


class ChaosInjector(ABC):
    """Abstract base class for chaos injectors."""

    def __init__(self, name: str):
        """Initialize chaos injector.

        Args:
            name: Name of the chaos injector
        """
        self.name = name
        self.active = False
        self._cleanup_callbacks: List[Callable] = []

    @abstractmethod
    async def inject_chaos(self, **kwargs) -> None:
        """Inject chaos into the system.

        Args:
            **kwargs: Chaos-specific parameters
        """
        pass

    @abstractmethod
    async def stop_chaos(self) -> None:
        """Stop chaos injection and restore normal operation."""
        pass

    def add_cleanup_callback(self, callback: Callable) -> None:
        """Add a cleanup callback to be called when stopping chaos.

        Args:
            callback: Function to call during cleanup
        """
        self._cleanup_callbacks.append(callback)

    async def cleanup(self) -> None:
        """Perform cleanup operations."""
        for callback in self._cleanup_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback()
                else:
                    callback()
            except Exception as e:
                logger.error(f"Error in cleanup callback: {e}")

        self._cleanup_callbacks.clear()


class NetworkChaosInjector(ChaosInjector):
    """Injects network-related chaos."""

    def __init__(self):
        super().__init__("network_chaos")
        self._original_socket_connect = None
        self._original_socket_send = None
        self._latency_ms = 0
        self._packet_loss_rate = 0.0
        self._connection_failures = False

    async def inject_chaos(self,
                          latency_ms: int = 0,
                          packet_loss_rate: float = 0.0,
                          connection_failures: bool = False,
                          **kwargs) -> None:
        """Inject network chaos.

        Args:
            latency_ms: Network latency to inject in milliseconds
            packet_loss_rate: Packet loss rate (0.0 to 1.0)
            connection_failures: Whether to simulate connection failures
        """
        self._latency_ms = latency_ms
        self._packet_loss_rate = packet_loss_rate
        self._connection_failures = connection_failures

        # Patch socket operations
        self._patch_socket_operations()
        self.active = True
        logger.info(f"Network chaos injected: latency={latency_ms}ms, loss={packet_loss_rate}, failures={connection_failures}")

    async def stop_chaos(self) -> None:
        """Stop network chaos injection."""
        self._restore_socket_operations()
        self.active = False
        logger.info("Network chaos stopped")

    def _patch_socket_operations(self) -> None:
        """Patch socket operations to inject chaos."""
        original_connect = socket.socket.connect
        original_send = socket.socket.send

        def chaotic_connect(self, address):
            if self._connection_failures and random.random() < 0.3:
                raise ConnectionRefusedError("Chaos: Connection refused")

            if self._latency_ms > 0:
                time.sleep(self._latency_ms / 1000.0)

            return original_connect(self, address)

        def chaotic_send(self, data):
            if self._packet_loss_rate > 0 and random.random() < self._packet_loss_rate:
                # Simulate packet loss by not sending
                return len(data)

            if self._latency_ms > 0:
                time.sleep(self._latency_ms / 1000.0)

            return original_send(self, data)

        self._original_socket_connect = original_connect
        self._original_socket_send = original_send

        socket.socket.connect = chaotic_connect
        socket.socket.send = chaotic_send

    def _restore_socket_operations(self) -> None:
        """Restore original socket operations."""
        if self._original_socket_connect:
            socket.socket.connect = self._original_socket_connect
        if self._original_socket_send:
            socket.socket.send = self._original_socket_send


class ServiceDependencyChaosInjector(ChaosInjector):
    """Injects service dependency chaos."""

    def __init__(self):
        super().__init__("service_dependency_chaos")
        self._patches = []

    async def inject_chaos(self,
                          service_failures: Dict[str, float] = None,
                          slow_responses: Dict[str, float] = None,
                          **kwargs) -> None:
        """Inject service dependency chaos.

        Args:
            service_failures: Map of service names to failure rates
            slow_responses: Map of service names to response delays
        """
        service_failures = service_failures or {}
        slow_responses = slow_responses or {}

        # Patch HTTP requests to simulate service failures
        self._patch_http_requests(service_failures, slow_responses)
        self.active = True
        logger.info(f"Service dependency chaos injected: failures={service_failures}, delays={slow_responses}")

    async def stop_chaos(self) -> None:
        """Stop service dependency chaos."""
        for patcher in self._patches:
            patcher.stop()
        self._patches.clear()
        self.active = False
        logger.info("Service dependency chaos stopped")

    def _patch_http_requests(self, failures: Dict[str, float], delays: Dict[str, float]) -> None:
        """Patch HTTP requests to inject chaos."""
        try:
            import aiohttp

            original_request = aiohttp.ClientSession._request

            async def chaotic_request(self, method, url, **kwargs):
                # Check if this URL should fail
                for service, failure_rate in failures.items():
                    if service in str(url) and random.random() < failure_rate:
                        raise aiohttp.ClientError(f"Chaos: {service} service failure")

                # Check if this URL should be slow
                for service, delay in delays.items():
                    if service in str(url):
                        await asyncio.sleep(delay)

                return await original_request(self, method, url, **kwargs)

            patcher = patch.object(aiohttp.ClientSession, '_request', chaotic_request)
            patcher.start()
            self._patches.append(patcher)

        except ImportError:
            logger.warning("aiohttp not available for service dependency chaos")


class ResourceExhaustionInjector(ChaosInjector):
    """Injects resource exhaustion chaos."""

    def __init__(self):
        super().__init__("resource_exhaustion")
        self._memory_hog = None
        self._cpu_hog_thread = None
        self._stop_cpu_hog = False

    async def inject_chaos(self,
                          memory_pressure_mb: int = 0,
                          cpu_pressure: bool = False,
                          disk_pressure: bool = False,
                          **kwargs) -> None:
        """Inject resource exhaustion chaos.

        Args:
            memory_pressure_mb: Amount of memory to consume in MB
            cpu_pressure: Whether to create CPU pressure
            disk_pressure: Whether to create disk pressure
        """
        if memory_pressure_mb > 0:
            self._create_memory_pressure(memory_pressure_mb)

        if cpu_pressure:
            self._create_cpu_pressure()

        if disk_pressure:
            self._create_disk_pressure()

        self.active = True
        logger.info(f"Resource exhaustion injected: memory={memory_pressure_mb}MB, cpu={cpu_pressure}, disk={disk_pressure}")

    async def stop_chaos(self) -> None:
        """Stop resource exhaustion."""
        if self._memory_hog:
            del self._memory_hog
            self._memory_hog = None

        if self._cpu_hog_thread:
            self._stop_cpu_hog = True
            self._cpu_hog_thread.join(timeout=1.0)
            self._cpu_hog_thread = None

        self.active = False
        logger.info("Resource exhaustion stopped")

    def _create_memory_pressure(self, mb: int) -> None:
        """Create memory pressure by allocating memory."""
        self._memory_hog = bytearray(mb * 1024 * 1024)

    def _create_cpu_pressure(self) -> None:
        """Create CPU pressure by running busy loops."""
        def cpu_hog():
            while not self._stop_cpu_hog:
                # Busy loop to consume CPU
                for _ in range(10000):
                    pass
                time.sleep(0.001)  # Small sleep to prevent complete lockup

        self._stop_cpu_hog = False
        self._cpu_hog_thread = threading.Thread(target=cpu_hog, daemon=True)
        self._cpu_hog_thread.start()

    def _create_disk_pressure(self) -> None:
        """Create disk pressure by filling up disk space."""
        # Create temporary files to consume disk space
        temp_dir = Path(tempfile.gettempdir()) / "chaos_disk_pressure"
        temp_dir.mkdir(exist_ok=True)

        def cleanup_disk():
            import shutil
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)

        self.add_cleanup_callback(cleanup_disk)

        # Create some large files (but not too large to avoid system damage)
        for i in range(5):
            file_path = temp_dir / f"chaos_file_{i}.tmp"
            with open(file_path, 'wb') as f:
                f.write(b'0' * (10 * 1024 * 1024))  # 10MB per file


class ChaosTest:
    """Base class for chaos engineering tests."""

    def __init__(self, name: str):
        """Initialize chaos test.

        Args:
            name: Name of the chaos test
        """
        self.name = name
        self.metrics = ChaosMetrics(test_name=name, start_time=time.time())
        self.injectors: List[ChaosInjector] = []
        self._system_monitor = None
        self._monitoring_active = False

    def add_injector(self, injector: ChaosInjector) -> None:
        """Add a chaos injector to the test.

        Args:
            injector: Chaos injector to add
        """
        self.injectors.append(injector)

    async def start_monitoring(self) -> None:
        """Start system monitoring during the test."""
        self._monitoring_active = True

        def monitor_system():
            while self._monitoring_active:
                try:
                    # Collect system metrics
                    cpu_percent = psutil.cpu_percent(interval=1)
                    memory = psutil.virtual_memory()
                    disk = psutil.disk_usage('/')

                    self.metrics.system_metrics.update({
                        'cpu_percent': cpu_percent,
                        'memory_percent': memory.percent,
                        'memory_available_mb': memory.available / (1024 * 1024),
                        'disk_percent': disk.percent,
                        'timestamp': time.time()
                    })

                except Exception as e:
                    logger.error(f"Error collecting system metrics: {e}")

                time.sleep(1)

        self._system_monitor = threading.Thread(target=monitor_system, daemon=True)
        self._system_monitor.start()

    async def stop_monitoring(self) -> None:
        """Stop system monitoring."""
        self._monitoring_active = False
        if self._system_monitor:
            self._system_monitor.join(timeout=2.0)

    async def inject_chaos(self, **kwargs) -> None:
        """Inject chaos using all configured injectors."""
        self.metrics.failure_injected_at = time.time()

        for injector in self.injectors:
            await injector.inject_chaos(**kwargs)

    async def stop_chaos(self) -> None:
        """Stop all chaos injection."""
        for injector in self.injectors:
            await injector.stop_chaos()
            await injector.cleanup()

    async def wait_for_recovery(self, check_function: Callable[[], bool], timeout: float = 30.0) -> bool:
        """Wait for system recovery after chaos injection.

        Args:
            check_function: Function that returns True when system has recovered
            timeout: Maximum time to wait for recovery

        Returns:
            True if system recovered within timeout
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            if check_function():
                self.metrics.recovery_time = time.time()
                return True

            await asyncio.sleep(0.5)

        return False

    def record_operation(self, success: bool) -> None:
        """Record the result of an operation during the test.

        Args:
            success: Whether the operation was successful
        """
        if success:
            self.metrics.successful_operations += 1
        else:
            self.metrics.failed_operations += 1

    def record_error(self) -> None:
        """Record an error during chaos testing."""
        self.metrics.errors_during_chaos += 1

    def add_custom_metric(self, name: str, value: Any) -> None:
        """Add a custom metric to the test results.

        Args:
            name: Metric name
            value: Metric value
        """
        self.metrics.custom_metrics[name] = value

    async def finalize(self) -> ChaosMetrics:
        """Finalize the test and return metrics.

        Returns:
            Test metrics
        """
        await self.stop_chaos()
        await self.stop_monitoring()

        self.metrics.end_time = time.time()
        return self.metrics


@contextlib.asynccontextmanager
async def chaos_test_context(name: str) -> AsyncGenerator[ChaosTest, None]:
    """Context manager for chaos tests with automatic cleanup.

    Args:
        name: Name of the chaos test

    Yields:
        ChaosTest instance
    """
    test = ChaosTest(name)

    try:
        await test.start_monitoring()
        yield test
    finally:
        await test.finalize()


# Utility functions for common chaos scenarios
def create_network_chaos(latency_ms: int = 100, packet_loss: float = 0.1) -> NetworkChaosInjector:
    """Create a network chaos injector with common settings."""
    return NetworkChaosInjector()


def create_service_chaos(failure_rate: float = 0.3) -> ServiceDependencyChaosInjector:
    """Create a service dependency chaos injector with common settings."""
    return ServiceDependencyChaosInjector()


def create_resource_chaos(memory_mb: int = 100, cpu_pressure: bool = True) -> ResourceExhaustionInjector:
    """Create a resource exhaustion injector with common settings."""
    return ResourceExhaustionInjector()
