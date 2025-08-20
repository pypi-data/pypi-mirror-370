# tests/performance/__init__.py
"""
Performance testing framework for KEI-Agent Python SDK.

This package contains comprehensive performance tests that establish:
- Baseline performance metrics for all core operations
- Automated performance regression detection
- Load testing scenarios for concurrent operations
- Resource usage monitoring and optimization
- Performance budgets and SLA validation
"""

import os
import time
import psutil
import asyncio
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from pathlib import Path
import json

# Performance test configuration
PERFORMANCE_CONFIG = {
    "enabled": os.getenv("ENABLE_PERFORMANCE_TESTING", "false").lower() == "true",
    "baseline_file": os.getenv("PERFORMANCE_BASELINE_FILE", "performance-baselines.json"),
    "regression_threshold": float(os.getenv("PERFORMANCE_REGRESSION_THRESHOLD", "0.2")),  # 20% regression
    "warmup_iterations": int(os.getenv("PERFORMANCE_WARMUP_ITERATIONS", "5")),
    "test_iterations": int(os.getenv("PERFORMANCE_TEST_ITERATIONS", "10")),
    "concurrent_users": int(os.getenv("PERFORMANCE_CONCURRENT_USERS", "10")),
    "test_duration": int(os.getenv("PERFORMANCE_TEST_DURATION", "30")),  # seconds
}

# Performance budgets (maximum acceptable values)
PERFORMANCE_BUDGETS = {
    "client_initialization": {"max_time": 1.0, "max_memory_mb": 50},
    "simple_request": {"max_time": 0.1, "max_memory_mb": 10},
    "authentication": {"max_time": 0.5, "max_memory_mb": 20},
    "message_sending": {"max_time": 0.2, "max_memory_mb": 15},
    "stream_connection": {"max_time": 2.0, "max_memory_mb": 30},
    "concurrent_requests": {"max_time": 5.0, "max_memory_mb": 100},
}


@dataclass
class PerformanceMetrics:
    """Container for performance measurement results."""

    operation: str
    duration: float
    memory_usage_mb: float
    cpu_usage_percent: float
    iterations: int
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "operation": self.operation,
            "duration": self.duration,
            "memory_usage_mb": self.memory_usage_mb,
            "cpu_usage_percent": self.cpu_usage_percent,
            "iterations": self.iterations,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PerformanceMetrics':
        """Create metrics from dictionary."""
        return cls(**data)


class PerformanceMonitor:
    """Monitors system resources during performance tests."""

    def __init__(self):
        """Initialize performance monitor."""
        self.process = psutil.Process()
        self.start_time = None
        self.start_memory = None
        self.start_cpu = None
        self.measurements = []

    def start_monitoring(self):
        """Start performance monitoring."""
        self.start_time = time.time()
        self.start_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        self.start_cpu = self.process.cpu_percent()
        self.measurements = []

    def record_measurement(self, label: str = "measurement"):
        """Record a performance measurement."""
        current_time = time.time()
        current_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        current_cpu = self.process.cpu_percent()

        measurement = {
            "label": label,
            "elapsed_time": current_time - self.start_time,
            "memory_mb": current_memory,
            "memory_delta_mb": current_memory - self.start_memory,
            "cpu_percent": current_cpu,
            "timestamp": current_time
        }

        self.measurements.append(measurement)
        return measurement

    def stop_monitoring(self) -> PerformanceMetrics:
        """Stop monitoring and return final metrics."""
        end_time = time.time()
        end_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        end_cpu = self.process.cpu_percent()

        return PerformanceMetrics(
            operation="monitored_operation",
            duration=end_time - self.start_time,
            memory_usage_mb=end_memory - self.start_memory,
            cpu_usage_percent=end_cpu,
            iterations=1,
            metadata={"measurements": self.measurements}
        )


class PerformanceBenchmark:
    """Base class for performance benchmarks."""

    def __init__(self, name: str, description: str = ""):
        """Initialize benchmark.

        Args:
            name: Benchmark name
            description: Benchmark description
        """
        self.name = name
        self.description = description
        self.monitor = PerformanceMonitor()
        self.results = []

    async def setup(self):
        """Setup benchmark environment."""
        pass

    async def teardown(self):
        """Cleanup benchmark environment."""
        pass

    async def run_single_iteration(self) -> Any:
        """Run a single benchmark iteration. Override in subclasses."""
        raise NotImplementedError("Subclasses must implement run_single_iteration")

    async def run_benchmark(self, iterations: int = None) -> PerformanceMetrics:
        """Run the complete benchmark.

        Args:
            iterations: Number of iterations to run

        Returns:
            Performance metrics
        """
        iterations = iterations or PERFORMANCE_CONFIG["test_iterations"]

        await self.setup()

        try:
            # Warmup
            warmup_iterations = PERFORMANCE_CONFIG["warmup_iterations"]
            for _ in range(warmup_iterations):
                await self.run_single_iteration()

            # Actual benchmark
            self.monitor.start_monitoring()

            start_time = time.time()
            for i in range(iterations):
                await self.run_single_iteration()
                self.monitor.record_measurement(f"iteration_{i}")

            end_time = time.time()

            metrics = self.monitor.stop_monitoring()
            metrics.operation = self.name
            metrics.duration = end_time - start_time
            metrics.iterations = iterations

            self.results.append(metrics)
            return metrics

        finally:
            await self.teardown()

    def validate_performance_budget(self, metrics: PerformanceMetrics) -> bool:
        """Validate metrics against performance budget.

        Args:
            metrics: Performance metrics to validate

        Returns:
            True if within budget, False otherwise
        """
        budget = PERFORMANCE_BUDGETS.get(self.name)
        if not budget:
            return True  # No budget defined

        if metrics.duration > budget.get("max_time", float('inf')):
            return False

        if metrics.memory_usage_mb > budget.get("max_memory_mb", float('inf')):
            return False

        return True


class PerformanceBaseline:
    """Manages performance baselines and regression detection."""

    def __init__(self, baseline_file: str = None):
        """Initialize baseline manager.

        Args:
            baseline_file: Path to baseline file
        """
        self.baseline_file = Path(baseline_file or PERFORMANCE_CONFIG["baseline_file"])
        self.baselines = self._load_baselines()

    def _load_baselines(self) -> Dict[str, PerformanceMetrics]:
        """Load performance baselines from file."""
        if not self.baseline_file.exists():
            return {}

        try:
            with open(self.baseline_file, 'r') as f:
                data = json.load(f)

            baselines = {}
            for operation, metrics_data in data.items():
                baselines[operation] = PerformanceMetrics.from_dict(metrics_data)

            return baselines
        except Exception as e:
            print(f"Warning: Could not load baselines: {e}")
            return {}

    def save_baselines(self):
        """Save baselines to file."""
        try:
            self.baseline_file.parent.mkdir(parents=True, exist_ok=True)

            data = {}
            for operation, metrics in self.baselines.items():
                data[operation] = metrics.to_dict()

            with open(self.baseline_file, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            print(f"Warning: Could not save baselines: {e}")

    def update_baseline(self, metrics: PerformanceMetrics):
        """Update baseline for an operation.

        Args:
            metrics: New performance metrics
        """
        self.baselines[metrics.operation] = metrics
        self.save_baselines()

    def check_regression(self, metrics: PerformanceMetrics) -> Dict[str, Any]:
        """Check for performance regression.

        Args:
            metrics: Current performance metrics

        Returns:
            Regression analysis results
        """
        baseline = self.baselines.get(metrics.operation)
        if not baseline:
            return {
                "has_regression": False,
                "reason": "No baseline available",
                "recommendation": "Set as new baseline"
            }

        threshold = PERFORMANCE_CONFIG["regression_threshold"]

        # Check duration regression
        duration_regression = (metrics.duration - baseline.duration) / baseline.duration
        memory_regression = (metrics.memory_usage_mb - baseline.memory_usage_mb) / baseline.memory_usage_mb

        regressions = []

        if duration_regression > threshold:
            regressions.append({
                "metric": "duration",
                "baseline": baseline.duration,
                "current": metrics.duration,
                "regression_percent": duration_regression * 100
            })

        if memory_regression > threshold:
            regressions.append({
                "metric": "memory_usage_mb",
                "baseline": baseline.memory_usage_mb,
                "current": metrics.memory_usage_mb,
                "regression_percent": memory_regression * 100
            })

        return {
            "has_regression": len(regressions) > 0,
            "regressions": regressions,
            "threshold_percent": threshold * 100,
            "baseline_timestamp": baseline.timestamp,
            "current_timestamp": metrics.timestamp
        }


def skip_if_performance_disabled():
    """Decorator to skip performance tests if disabled."""
    import pytest

    def decorator(func):
        return pytest.mark.skipif(
            not PERFORMANCE_CONFIG["enabled"],
            reason="Performance testing disabled (set ENABLE_PERFORMANCE_TESTING=true)"
        )(func)
    return decorator


def performance_test(name: str, budget: Dict[str, float] = None):
    """Decorator for performance test functions.

    Args:
        name: Performance test name
        budget: Performance budget (max_time, max_memory_mb)
    """
    def decorator(func):
        func._performance_test_name = name
        func._performance_budget = budget
        return func
    return decorator


# Export commonly used items
__all__ = [
    "PERFORMANCE_CONFIG",
    "PERFORMANCE_BUDGETS",
    "PerformanceMetrics",
    "PerformanceMonitor",
    "PerformanceBenchmark",
    "PerformanceBaseline",
    "skip_if_performance_disabled",
    "performance_test",
]
