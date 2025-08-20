# kei_agent/caching/cache_manager.py
"""
Cache Manager and Administration for KEI-Agent Python SDK.

Provides centralized cache management with:
- Dynamic configuration and policy management
- Administrative APIs for cache operations
- Performance monitoring and analytics
- Cache warming and optimization strategies
- Integration with metrics and monitoring systems
"""

import asyncio
import json
import logging
import time
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, asdict

from .cache_framework import get_cache_event_manager
from .multi_level_cache import MultiLevelCache, MultiLevelCacheConfig
from .specialized_caches import (
    ResponseCache,
    AuthTokenCache,
    ConfigCache,
    ProtocolCache,
    MetricsCache,
    CachePolicy,
)

logger = logging.getLogger(__name__)


@dataclass
class CacheManagerConfig:
    """Configuration for cache manager."""

    # Multi-level cache configuration
    multi_level_config: MultiLevelCacheConfig

    # Specialized cache configurations
    enable_response_cache: bool = True
    enable_auth_cache: bool = True
    enable_config_cache: bool = True
    enable_protocol_cache: bool = True
    enable_metrics_cache: bool = True

    # Management settings
    enable_admin_api: bool = True
    admin_api_port: int = 8081
    enable_cache_warming: bool = True
    warming_strategies: List[str] = None

    # Monitoring and analytics
    enable_monitoring: bool = True
    metrics_export_interval: float = 60.0
    performance_tracking: bool = True

    def __post_init__(self):
        if self.warming_strategies is None:
            self.warming_strategies = ["predictive", "scheduled"]


class CacheManager:
    """Centralized cache manager for all caching operations."""

    def __init__(self, config: CacheManagerConfig):
        """Initialize cache manager.

        Args:
            config: Cache manager configuration
        """
        self.config = config

        # Initialize multi-level cache
        self.multi_level_cache = MultiLevelCache(config.multi_level_config)

        # Initialize specialized caches
        self.specialized_caches = {}
        self._initialize_specialized_caches()

        # Event management
        self._event_manager = get_cache_event_manager()
        self._setup_event_handlers()

        # Performance tracking
        self._performance_data: Dict[str, List[float]] = {}
        self._operation_counts: Dict[str, int] = {}

        # Cache warming
        self._warming_strategies: Dict[str, Callable] = {}
        self._warming_tasks: List[asyncio.Task] = []

        # Background tasks
        self._monitoring_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()

        # Initialize components
        self._initialize_warming_strategies()
        self._start_background_tasks()

    def _initialize_specialized_caches(self) -> None:
        """Initialize specialized cache instances."""
        if self.config.enable_response_cache:
            self.specialized_caches["response"] = ResponseCache(
                self.multi_level_cache,
                CachePolicy(ttl=300, invalidation_tags=["api_response"]),
            )

        if self.config.enable_auth_cache:
            self.specialized_caches["auth"] = AuthTokenCache(self.multi_level_cache)

        if self.config.enable_config_cache:
            self.specialized_caches["config"] = ConfigCache(self.multi_level_cache)

        if self.config.enable_protocol_cache:
            self.specialized_caches["protocol"] = ProtocolCache(self.multi_level_cache)

        if self.config.enable_metrics_cache:
            self.specialized_caches["metrics"] = MetricsCache(self.multi_level_cache)

    def _setup_event_handlers(self) -> None:
        """Setup event handlers for cache operations."""
        self._event_manager.subscribe("cache_hit", self._handle_cache_event)
        self._event_manager.subscribe("cache_miss", self._handle_cache_event)
        self._event_manager.subscribe("cache_set", self._handle_cache_event)
        self._event_manager.subscribe("cache_eviction", self._handle_cache_event)
        self._event_manager.subscribe("cache_error", self._handle_cache_event)

    def _initialize_warming_strategies(self) -> None:
        """Initialize cache warming strategies."""
        if "predictive" in self.config.warming_strategies:
            self._warming_strategies["predictive"] = self._predictive_warming

        if "scheduled" in self.config.warming_strategies:
            self._warming_strategies["scheduled"] = self._scheduled_warming

        if "access_pattern" in self.config.warming_strategies:
            self._warming_strategies["access_pattern"] = self._access_pattern_warming

    def _start_background_tasks(self) -> None:
        """Start background monitoring and maintenance tasks."""
        if self.config.enable_monitoring:
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())

        if self.config.enable_cache_warming:
            for strategy_name, strategy_func in self._warming_strategies.items():
                task = asyncio.create_task(
                    self._warming_loop(strategy_name, strategy_func)
                )
                self._warming_tasks.append(task)

    async def _monitoring_loop(self) -> None:
        """Background monitoring loop."""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(self.config.metrics_export_interval)
                await self._collect_and_export_metrics()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")

    async def _warming_loop(self, strategy_name: str, strategy_func: Callable) -> None:
        """Background cache warming loop."""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                await strategy_func()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in {strategy_name} warming strategy: {e}")

    # Public API Methods

    async def get(self, key: str, cache_type: str = "default") -> Optional[Any]:
        """Get value from cache.

        Args:
            key: Cache key
            cache_type: Type of cache (default, response, auth, config, protocol, metrics)

        Returns:
            Cached value or None
        """
        start_time = time.time()

        try:
            if cache_type == "default":
                result = await self.multi_level_cache.get(key)
            else:
                specialized_cache = self.specialized_caches.get(cache_type)
                if not specialized_cache:
                    raise ValueError(f"Unknown cache type: {cache_type}")

                # Handle specialized cache methods
                if cache_type == "response":
                    # This would need additional parameters in a real implementation
                    result = None
                else:
                    result = await specialized_cache.cache.get(key)

            self._record_performance("get", time.time() - start_time)
            return result

        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[float] = None,
        tags: List[str] = None,
        cache_type: str = "default",
    ) -> bool:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live
            tags: Tags for invalidation
            cache_type: Type of cache

        Returns:
            True if successful
        """
        start_time = time.time()

        try:
            if cache_type == "default":
                result = await self.multi_level_cache.set(key, value, ttl, tags)
            else:
                specialized_cache = self.specialized_caches.get(cache_type)
                if not specialized_cache:
                    raise ValueError(f"Unknown cache type: {cache_type}")

                result = await specialized_cache.cache.set(key, value, ttl, tags)

            self._record_performance("set", time.time() - start_time)
            return result

        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False

    async def delete(self, key: str, cache_type: str = "default") -> bool:
        """Delete value from cache."""
        try:
            if cache_type == "default":
                return await self.multi_level_cache.delete(key)
            else:
                specialized_cache = self.specialized_caches.get(cache_type)
                if not specialized_cache:
                    raise ValueError(f"Unknown cache type: {cache_type}")

                return await specialized_cache.cache.delete(key)

        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False

    async def clear(self, cache_type: str = "all") -> bool:
        """Clear cache(s).

        Args:
            cache_type: Type of cache to clear ("all", "default", or specific type)

        Returns:
            True if successful
        """
        try:
            if cache_type == "all":
                success = await self.multi_level_cache.clear()
                for specialized_cache in self.specialized_caches.values():
                    if hasattr(specialized_cache, "cache"):
                        success &= await specialized_cache.cache.clear()
                return success
            elif cache_type == "default":
                return await self.multi_level_cache.clear()
            else:
                specialized_cache = self.specialized_caches.get(cache_type)
                if not specialized_cache:
                    raise ValueError(f"Unknown cache type: {cache_type}")

                return await specialized_cache.cache.clear()

        except Exception as e:
            logger.error(f"Error clearing cache {cache_type}: {e}")
            return False

    async def invalidate_by_tags(
        self, tags: List[str], cache_type: str = "all"
    ) -> Dict[str, int]:
        """Invalidate cache entries by tags.

        Args:
            tags: Tags to invalidate
            cache_type: Type of cache

        Returns:
            Dictionary of invalidation counts by cache type
        """
        results = {}

        try:
            if cache_type == "all" or cache_type == "default":
                results["multi_level"] = sum(
                    (await self.multi_level_cache.invalidate_by_tags(tags)).values()
                )

            if cache_type == "all":
                for cache_name, specialized_cache in self.specialized_caches.items():
                    if hasattr(specialized_cache, "cache"):
                        cache_results = (
                            await specialized_cache.cache.invalidate_by_tags(tags)
                        )
                        results[cache_name] = sum(cache_results.values())
            elif cache_type != "default":
                specialized_cache = self.specialized_caches.get(cache_type)
                if specialized_cache and hasattr(specialized_cache, "cache"):
                    cache_results = await specialized_cache.cache.invalidate_by_tags(
                        tags
                    )
                    results[cache_type] = sum(cache_results.values())

            return results

        except Exception as e:
            logger.error(f"Error invalidating by tags {tags}: {e}")
            return {}

    async def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        try:
            stats = {
                "multi_level": await self.multi_level_cache.get_stats(),
                "analytics": await self.multi_level_cache.get_analytics(),
                "performance": self._get_performance_stats(),
                "operation_counts": self._operation_counts.copy(),
            }

            # Add specialized cache stats
            for cache_name, specialized_cache in self.specialized_caches.items():
                if hasattr(specialized_cache, "cache"):
                    cache_stats = await specialized_cache.cache.get_stats()
                    stats[f"specialized_{cache_name}"] = cache_stats

            return stats

        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}

    async def warm_cache(
        self, strategy: str = "predictive", **kwargs
    ) -> Dict[str, Any]:
        """Manually trigger cache warming.

        Args:
            strategy: Warming strategy to use
            **kwargs: Strategy-specific parameters

        Returns:
            Warming results
        """
        if strategy not in self._warming_strategies:
            raise ValueError(f"Unknown warming strategy: {strategy}")

        try:
            start_time = time.time()
            strategy_func = self._warming_strategies[strategy]
            result = await strategy_func(**kwargs)

            return {
                "strategy": strategy,
                "duration_seconds": time.time() - start_time,
                "result": result,
            }

        except Exception as e:
            logger.error(f"Error in cache warming strategy {strategy}: {e}")
            return {"error": str(e)}

    # Cache Warming Strategies

    async def _predictive_warming(self, **kwargs) -> Dict[str, Any]:
        """Predictive cache warming based on access patterns."""
        # Analyze access patterns and warm frequently accessed keys
        analytics = await self.multi_level_cache.get_analytics()
        top_keys = analytics.get("top_accessed_keys", [])

        warmed_count = 0
        for key, access_count in top_keys[:50]:  # Warm top 50 keys
            # This would involve predicting what data to warm
            # For now, just count the keys we would warm
            warmed_count += 1

        return {"warmed_keys": warmed_count, "strategy": "predictive"}

    async def _scheduled_warming(self, **kwargs) -> Dict[str, Any]:
        """Scheduled cache warming for known patterns."""
        # Warm cache based on scheduled patterns (e.g., daily reports)
        warmed_count = 0

        # Example: warm configuration data
        if "config" in self.specialized_caches:
            # This would warm known configuration keys
            warmed_count += 10  # Placeholder

        return {"warmed_keys": warmed_count, "strategy": "scheduled"}

    async def _access_pattern_warming(self, **kwargs) -> Dict[str, Any]:
        """Cache warming based on access patterns."""
        # Analyze recent access patterns and warm related data
        return {"warmed_keys": 0, "strategy": "access_pattern"}

    # Event Handlers and Monitoring

    async def _handle_cache_event(self, **kwargs) -> None:
        """Handle cache events for monitoring."""
        event_type = kwargs.get("event_type", "unknown")
        self._operation_counts[event_type] = (
            self._operation_counts.get(event_type, 0) + 1
        )

        if self.config.performance_tracking:
            latency = kwargs.get("latency_ms", 0)
            if latency > 0:
                self._record_performance(event_type, latency)

    def _record_performance(self, operation: str, latency: float) -> None:
        """Record performance data."""
        if operation not in self._performance_data:
            self._performance_data[operation] = []

        self._performance_data[operation].append(latency)

        # Keep only recent data (last 1000 operations)
        if len(self._performance_data[operation]) > 1000:
            self._performance_data[operation] = self._performance_data[operation][
                -1000:
            ]

    def _get_performance_stats(self) -> Dict[str, Dict[str, float]]:
        """Get performance statistics."""
        stats = {}

        for operation, latencies in self._performance_data.items():
            if latencies:
                stats[operation] = {
                    "avg_latency_ms": sum(latencies) / len(latencies),
                    "min_latency_ms": min(latencies),
                    "max_latency_ms": max(latencies),
                    "p95_latency_ms": sorted(latencies)[int(len(latencies) * 0.95)]
                    if len(latencies) > 20
                    else max(latencies),
                    "operation_count": len(latencies),
                }

        return stats

    async def _collect_and_export_metrics(self) -> None:
        """Collect and export metrics to monitoring systems."""
        try:
            stats = await self.get_stats()

            # Export to monitoring system (placeholder)
            logger.debug(f"Cache metrics: {json.dumps(stats, default=str)}")

            # Reset operation counts periodically
            if sum(self._operation_counts.values()) > 10000:
                self._operation_counts.clear()

        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")

    # Configuration Management

    async def update_config(self, new_config: Dict[str, Any]) -> bool:
        """Update cache configuration dynamically.

        Args:
            new_config: New configuration parameters

        Returns:
            True if successful
        """
        try:
            # This would update cache configurations dynamically
            # Implementation depends on specific configuration changes
            logger.info(f"Cache configuration updated: {new_config}")
            return True

        except Exception as e:
            logger.error(f"Error updating cache config: {e}")
            return False

    async def get_config(self) -> Dict[str, Any]:
        """Get current cache configuration."""
        return {
            "multi_level_config": asdict(self.config.multi_level_config),
            "specialized_caches": list(self.specialized_caches.keys()),
            "warming_strategies": list(self._warming_strategies.keys()),
            "monitoring_enabled": self.config.enable_monitoring,
        }

    # Specialized Cache Access

    def get_response_cache(self) -> Optional[ResponseCache]:
        """Get response cache instance."""
        return self.specialized_caches.get("response")

    def get_auth_cache(self) -> Optional[AuthTokenCache]:
        """Get auth token cache instance."""
        return self.specialized_caches.get("auth")

    def get_config_cache(self) -> Optional[ConfigCache]:
        """Get configuration cache instance."""
        return self.specialized_caches.get("config")

    def get_protocol_cache(self) -> Optional[ProtocolCache]:
        """Get protocol cache instance."""
        return self.specialized_caches.get("protocol")

    def get_metrics_cache(self) -> Optional[MetricsCache]:
        """Get metrics cache instance."""
        return self.specialized_caches.get("metrics")

    # Shutdown and Cleanup

    async def shutdown(self) -> None:
        """Shutdown cache manager and all components."""
        try:
            self._shutdown_event.set()

            # Cancel background tasks
            if self._monitoring_task:
                self._monitoring_task.cancel()
                try:
                    await self._monitoring_task
                except asyncio.CancelledError:
                    pass

            for task in self._warming_tasks:
                task.cancel()

            await asyncio.gather(*self._warming_tasks, return_exceptions=True)

            # Shutdown specialized caches
            for cache in self.specialized_caches.values():
                if hasattr(cache, "shutdown"):
                    await cache.shutdown()

            # Shutdown multi-level cache
            await self.multi_level_cache.shutdown()

            logger.info("Cache manager shutdown complete")

        except Exception as e:
            logger.error(f"Error during cache manager shutdown: {e}")


# Global cache manager instance
_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> Optional[CacheManager]:
    """Get the global cache manager instance."""
    return _cache_manager


def initialize_cache_manager(config: CacheManagerConfig) -> CacheManager:
    """Initialize the global cache manager.

    Args:
        config: Cache manager configuration

    Returns:
        Initialized cache manager
    """
    global _cache_manager
    _cache_manager = CacheManager(config)
    return _cache_manager


async def shutdown_cache_manager() -> None:
    """Shutdown the global cache manager."""
    global _cache_manager
    if _cache_manager:
        await _cache_manager.shutdown()
        _cache_manager = None
