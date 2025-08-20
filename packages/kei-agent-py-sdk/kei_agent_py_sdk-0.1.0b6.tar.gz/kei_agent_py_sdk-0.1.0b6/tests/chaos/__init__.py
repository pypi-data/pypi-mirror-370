# tests/chaos/__init__.py
"""
Chaos Engineering Test Suite for KEI-Agent Python SDK.

This package provides comprehensive chaos engineering tests to validate
system resilience and fault tolerance under various failure conditions.
"""

from .chaos_framework import (
    ChaosTest, ChaosInjector, ChaosMetrics,
    NetworkChaosInjector, ServiceDependencyChaosInjector, ResourceExhaustionInjector,
    chaos_test_context, create_network_chaos, create_service_chaos, create_resource_chaos
)

from .chaos_metrics import (
    ChaosMetricsCollector, ResilienceScore,
    get_chaos_metrics_collector, reset_chaos_metrics_collector
)

from .chaos_integration import ChaosTestSuite

__all__ = [
    # Framework classes
    'ChaosTest',
    'ChaosInjector',
    'ChaosMetrics',

    # Chaos injectors
    'NetworkChaosInjector',
    'ServiceDependencyChaosInjector',
    'ResourceExhaustionInjector',

    # Context managers and utilities
    'chaos_test_context',
    'create_network_chaos',
    'create_service_chaos',
    'create_resource_chaos',

    # Metrics and analysis
    'ChaosMetricsCollector',
    'ResilienceScore',
    'get_chaos_metrics_collector',
    'reset_chaos_metrics_collector',

    # Integration
    'ChaosTestSuite'
]
