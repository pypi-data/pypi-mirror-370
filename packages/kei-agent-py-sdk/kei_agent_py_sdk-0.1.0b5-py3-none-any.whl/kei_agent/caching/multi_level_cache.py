# kei_agent/caching/multi_level_cache.py
"""
Multi-Level Cache Manager for KEI-Agent Python SDK.

Coordinates L1 (Memory), L2 (Redis), and L3 (Persistent) caches with:
- Intelligent cache promotion and demotion
- Cache warming strategies
- Coherence management across levels
- Performance optimization and analytics
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

from .cache_framework import (
    CacheInterface,
    CacheLevel,
    CacheStats,
    CacheConfig,
    get_cache_event_manager,
    CacheMetrics,
)
from .memory_cache import MemoryCache
from .redis_cache import RedisCache
from .persistent_cache import PersistentCache

logger = logging.getLogger(__name__)


class CacheStrategy(Enum):
    """Cache strategy enumeration."""

    WRITE_THROUGH = "write_through"
    WRITE_BACK = "write_back"
    WRITE_AROUND = "write_around"


class CachePromotionPolicy(Enum):
    """Cache promotion policy enumeration."""

    ACCESS_COUNT = "access_count"
    ACCESS_FREQUENCY = "access_frequency"
    SIZE_BASED = "size_based"
    HYBRID = "hybrid"


@dataclass
class CacheOperation:
    """Represents a cache operation for analytics."""

    operation: str  # get, set, delete, etc.
    key: str
    level: CacheLevel
    hit: bool
    latency_ms: float
    size_bytes: int = 0
    timestamp: float = 0.0

    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()


@dataclass
class MultiLevelCacheConfig:
    """Configuration for multi-level cache."""

    # Cache level configurations
    l1_config: CacheConfig
    l2_config: Optional[CacheConfig] = None
    l3_config: Optional[CacheConfig] = None

    # Redis configuration
    redis_config: Optional[Dict[str, Any]] = None

    # Persistent storage configuration
    storage_config: Optional[Dict[str, Any]] = None

    # Multi-level behavior
    cache_strategy: CacheStrategy = CacheStrategy.WRITE_THROUGH
    promotion_policy: CachePromotionPolicy = CachePromotionPolicy.HYBRID

    # Promotion thresholds
    l2_to_l1_access_threshold: int = 3
    l3_to_l2_access_threshold: int = 5
    promotion_size_limit_bytes: int = 1024 * 1024  # 1MB

    # Cache warming
    enable_cache_warming: bool = True
    warming_batch_size: int = 100
    warming_concurrency: int = 5

    # Analytics
    enable_analytics: bool = True
    analytics_sample_rate: float = 0.1  # 10% sampling
    max_analytics_entries: int = 10000


class MultiLevelCache(CacheInterface):
    """Multi-level cache manager coordinating L1, L2, and L3 caches."""

    def __init__(self, config: MultiLevelCacheConfig):
        """Initialize multi-level cache.

        Args:
            config: Multi-level cache configuration
        """
        self.config = config

        # Initialize cache levels
        self.l1_cache = MemoryCache(config.l1_config)

        self.l2_cache: Optional[RedisCache] = None
        if config.l2_config and config.redis_config:
            try:
                self.l2_cache = RedisCache(config.l2_config, config.redis_config)
            except ImportError:
                logger.warning("Redis not available, L2 cache disabled")

        self.l3_cache: Optional[PersistentCache] = None
        if config.l3_config:
            self.l3_cache = PersistentCache(
                config.l3_config, config.storage_config or {}
            )

        # Cache level mapping
        self.cache_levels = {
            CacheLevel.L1_MEMORY: self.l1_cache,
            CacheLevel.L2_DISTRIBUTED: self.l2_cache,
            CacheLevel.L3_PERSISTENT: self.l3_cache,
        }

        # Analytics and monitoring
        self._metrics = CacheMetrics()
        self._event_manager = get_cache_event_manager()
        self._operation_history: List[CacheOperation] = []
        self._access_patterns: Dict[str, Dict[str, Any]] = {}

        # Cache warming
        self._warming_queue: asyncio.Queue = asyncio.Queue()
        self._warming_tasks: List[asyncio.Task] = []

        # Setup event handlers
        self._setup_event_handlers()

        # Start background tasks
        self._start_background_tasks()

    def _setup_event_handlers(self) -> None:
        """Setup event handlers for cache coordination."""
        self._event_manager.subscribe("cache_hit", self._handle_cache_hit)
        self._event_manager.subscribe("cache_miss", self._handle_cache_miss)
        self._event_manager.subscribe("cache_set", self._handle_cache_set)
        self._event_manager.subscribe("cache_eviction", self._handle_cache_eviction)

    def _start_background_tasks(self) -> None:
        """Start background tasks for cache management."""
        if self.config.enable_cache_warming:
            for _ in range(self.config.warming_concurrency):
                task = asyncio.create_task(self._cache_warming_worker())
                self._warming_tasks.append(task)

    async def get(self, key: str) -> Optional[Any]:
        """Get value from multi-level cache with promotion logic."""
        start_time = time.time()

        # Try L1 first
        value = await self.l1_cache.get(key)
        if value is not None:
            await self._record_operation(
                "get", key, CacheLevel.L1_MEMORY, True, start_time
            )
            await self._update_access_pattern(key, CacheLevel.L1_MEMORY)
            return value

        # Try L2 if available
        if self.l2_cache:
            value = await self.l2_cache.get(key)
            if value is not None:
                await self._record_operation(
                    "get", key, CacheLevel.L2_DISTRIBUTED, True, start_time
                )
                await self._update_access_pattern(key, CacheLevel.L2_DISTRIBUTED)

                # Consider promotion to L1
                if await self._should_promote_to_l1(key, value):
                    await self.l1_cache.set(key, value)

                return value

        # Try L3 if available
        if self.l3_cache:
            value = await self.l3_cache.get(key)
            if value is not None:
                await self._record_operation(
                    "get", key, CacheLevel.L3_PERSISTENT, True, start_time
                )
                await self._update_access_pattern(key, CacheLevel.L3_PERSISTENT)

                # Consider promotion to L2 and L1
                if await self._should_promote_to_l2(key, value):
                    if self.l2_cache:
                        await self.l2_cache.set(key, value)

                if await self._should_promote_to_l1(key, value):
                    await self.l1_cache.set(key, value)

                return value

        # Cache miss at all levels
        await self._record_operation(
            "get", key, CacheLevel.L1_MEMORY, False, start_time
        )
        return None

    async def set(
        self, key: str, value: Any, ttl: Optional[float] = None, tags: List[str] = None
    ) -> bool:
        """Set value in multi-level cache according to strategy."""
        start_time = time.time()
        success = True

        if self.config.cache_strategy == CacheStrategy.WRITE_THROUGH:
            # Write to all levels
            success &= await self.l1_cache.set(key, value, ttl, tags)

            if self.l2_cache:
                success &= await self.l2_cache.set(key, value, ttl, tags)

            if self.l3_cache:
                success &= await self.l3_cache.set(key, value, ttl, tags)

        elif self.config.cache_strategy == CacheStrategy.WRITE_BACK:
            # Write to L1 only, propagate later
            success = await self.l1_cache.set(key, value, ttl, tags)

            # Schedule background write to lower levels
            if success:
                await self._schedule_background_write(key, value, ttl, tags)

        elif self.config.cache_strategy == CacheStrategy.WRITE_AROUND:
            # Write to L2 and L3, skip L1
            if self.l2_cache:
                success &= await self.l2_cache.set(key, value, ttl, tags)

            if self.l3_cache:
                success &= await self.l3_cache.set(key, value, ttl, tags)

        if success:
            await self._record_operation(
                "set", key, CacheLevel.L1_MEMORY, True, start_time, len(str(value))
            )
            await self._update_access_pattern(key, CacheLevel.L1_MEMORY)

        return success

    async def delete(self, key: str) -> bool:
        """Delete value from all cache levels."""
        success = True

        # Delete from all levels
        success &= await self.l1_cache.delete(key)

        if self.l2_cache:
            success &= await self.l2_cache.delete(key)

        if self.l3_cache:
            success &= await self.l3_cache.delete(key)

        # Remove from access patterns
        self._access_patterns.pop(key, None)

        return success

    async def exists(self, key: str) -> bool:
        """Check if key exists in any cache level."""
        if await self.l1_cache.exists(key):
            return True

        if self.l2_cache and await self.l2_cache.exists(key):
            return True

        if self.l3_cache and await self.l3_cache.exists(key):
            return True

        return False

    async def clear(self) -> bool:
        """Clear all cache levels."""
        success = True

        success &= await self.l1_cache.clear()

        if self.l2_cache:
            success &= await self.l2_cache.clear()

        if self.l3_cache:
            success &= await self.l3_cache.clear()

        # Clear analytics
        self._operation_history.clear()
        self._access_patterns.clear()

        return success

    async def get_stats(self) -> Dict[CacheLevel, CacheStats]:
        """Get statistics for all cache levels."""
        stats = {}

        stats[CacheLevel.L1_MEMORY] = await self.l1_cache.get_stats()

        if self.l2_cache:
            stats[CacheLevel.L2_DISTRIBUTED] = await self.l2_cache.get_stats()

        if self.l3_cache:
            stats[CacheLevel.L3_PERSISTENT] = await self.l3_cache.get_stats()

        return stats

    async def invalidate_by_tags(self, tags: List[str]) -> Dict[CacheLevel, int]:
        """Invalidate cache entries by tags across all levels."""
        results = {}

        results[CacheLevel.L1_MEMORY] = await self.l1_cache.invalidate_by_tags(tags)

        if self.l2_cache:
            results[CacheLevel.L2_DISTRIBUTED] = await self.l2_cache.invalidate_by_tags(
                tags
            )

        if self.l3_cache:
            results[CacheLevel.L3_PERSISTENT] = await self.l3_cache.invalidate_by_tags(
                tags
            )

        return results

    async def warm_cache(
        self, keys: List[str], source_level: CacheLevel = CacheLevel.L3_PERSISTENT
    ) -> int:
        """Warm cache by promoting keys from lower levels."""
        if not self.config.enable_cache_warming:
            return 0

        warmed_count = 0

        # Process keys in batches
        for i in range(0, len(keys), self.config.warming_batch_size):
            batch = keys[i : i + self.config.warming_batch_size]

            for key in batch:
                await self._warming_queue.put((key, source_level))

            warmed_count += len(batch)

        return warmed_count

    async def _cache_warming_worker(self) -> None:
        """Background worker for cache warming."""
        while True:
            try:
                key, source_level = await self._warming_queue.get()
                await self._warm_single_key(key, source_level)
                self._warming_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cache warming worker: {e}")

    async def _warm_single_key(self, key: str, source_level: CacheLevel) -> None:
        """Warm a single key from source level to higher levels."""
        try:
            source_cache = self.cache_levels.get(source_level)
            if not source_cache:
                return

            value = await source_cache.get(key)
            if value is None:
                return

            # Promote to higher levels
            if source_level == CacheLevel.L3_PERSISTENT:
                if self.l2_cache:
                    await self.l2_cache.set(key, value)
                await self.l1_cache.set(key, value)
            elif source_level == CacheLevel.L2_DISTRIBUTED:
                await self.l1_cache.set(key, value)

        except Exception as e:
            logger.error(f"Error warming cache key {key}: {e}")

    async def _should_promote_to_l1(self, key: str, value: Any) -> bool:
        """Determine if key should be promoted to L1."""
        if self.config.promotion_policy == CachePromotionPolicy.ACCESS_COUNT:
            pattern = self._access_patterns.get(key, {})
            return (
                pattern.get("access_count", 0) >= self.config.l2_to_l1_access_threshold
            )

        elif self.config.promotion_policy == CachePromotionPolicy.SIZE_BASED:
            size = len(str(value))
            return size <= self.config.promotion_size_limit_bytes

        elif self.config.promotion_policy == CachePromotionPolicy.HYBRID:
            pattern = self._access_patterns.get(key, {})
            size = len(str(value))
            access_count = pattern.get("access_count", 0)

            return (
                access_count >= self.config.l2_to_l1_access_threshold
                and size <= self.config.promotion_size_limit_bytes
            )

        return False

    async def _should_promote_to_l2(self, key: str, value: Any) -> bool:
        """Determine if key should be promoted to L2."""
        if not self.l2_cache:
            return False

        pattern = self._access_patterns.get(key, {})
        return pattern.get("access_count", 0) >= self.config.l3_to_l2_access_threshold

    async def _schedule_background_write(
        self, key: str, value: Any, ttl: Optional[float], tags: List[str]
    ) -> None:
        """Schedule background write to lower cache levels."""

        async def background_write():
            try:
                if self.l2_cache:
                    await self.l2_cache.set(key, value, ttl, tags)

                if self.l3_cache:
                    await self.l3_cache.set(key, value, ttl, tags)
            except Exception as e:
                logger.error(f"Error in background write for key {key}: {e}")

        asyncio.create_task(background_write())

    async def _record_operation(
        self,
        operation: str,
        key: str,
        level: CacheLevel,
        hit: bool,
        start_time: float,
        size_bytes: int = 0,
    ) -> None:
        """Record cache operation for analytics."""
        if not self.config.enable_analytics:
            return

        # Sample operations to avoid memory bloat
        if (
            len(self._operation_history) > 0
            and hash(key) % int(1 / self.config.analytics_sample_rate) != 0
        ):
            return

        latency_ms = (time.time() - start_time) * 1000

        operation_record = CacheOperation(
            operation=operation,
            key=key,
            level=level,
            hit=hit,
            latency_ms=latency_ms,
            size_bytes=size_bytes,
        )

        self._operation_history.append(operation_record)

        # Limit history size
        if len(self._operation_history) > self.config.max_analytics_entries:
            self._operation_history = self._operation_history[
                -self.config.max_analytics_entries // 2 :
            ]

    async def _update_access_pattern(self, key: str, level: CacheLevel) -> None:
        """Update access patterns for promotion decisions."""
        if key not in self._access_patterns:
            self._access_patterns[key] = {
                "access_count": 0,
                "last_access": time.time(),
                "access_levels": set(),
            }

        pattern = self._access_patterns[key]
        pattern["access_count"] += 1
        pattern["last_access"] = time.time()
        pattern["access_levels"].add(level)

    async def _handle_cache_hit(self, **kwargs) -> None:
        """Handle cache hit events."""
        self._metrics.record_hit(kwargs.get("latency_ms", 0))

    async def _handle_cache_miss(self, **kwargs) -> None:
        """Handle cache miss events."""
        self._metrics.record_miss(kwargs.get("latency_ms", 0))

    async def _handle_cache_set(self, **kwargs) -> None:
        """Handle cache set events."""
        pass  # Could trigger cache warming or other optimizations

    async def _handle_cache_eviction(self, **kwargs) -> None:
        """Handle cache eviction events."""
        self._metrics.record_eviction()

    async def get_analytics(self) -> Dict[str, Any]:
        """Get cache analytics and performance insights."""
        if not self.config.enable_analytics:
            return {}

        # Calculate hit ratios by level
        level_stats = {}
        for level in CacheLevel:
            level_ops = [op for op in self._operation_history if op.level == level]
            if level_ops:
                hits = sum(1 for op in level_ops if op.hit)
                total = len(level_ops)
                level_stats[level.value] = {
                    "hit_ratio": hits / total,
                    "avg_latency_ms": sum(op.latency_ms for op in level_ops) / total,
                    "total_operations": total,
                }

        # Top accessed keys
        key_access_counts = {}
        for key, pattern in self._access_patterns.items():
            key_access_counts[key] = pattern["access_count"]

        top_keys = sorted(key_access_counts.items(), key=lambda x: x[1], reverse=True)[
            :10
        ]

        return {
            "level_statistics": level_stats,
            "top_accessed_keys": top_keys,
            "total_operations": len(self._operation_history),
            "cache_warming_queue_size": self._warming_queue.qsize(),
            "access_patterns_count": len(self._access_patterns),
        }

    async def shutdown(self) -> None:
        """Shutdown all cache levels and cleanup resources."""
        try:
            # Cancel warming tasks
            for task in self._warming_tasks:
                task.cancel()

            await asyncio.gather(*self._warming_tasks, return_exceptions=True)

            # Shutdown cache levels
            await self.l1_cache.shutdown()

            if self.l2_cache:
                await self.l2_cache.shutdown()

            if self.l3_cache:
                await self.l3_cache.shutdown()

            logger.info("Multi-level cache shutdown complete")

        except Exception as e:
            logger.error(f"Error during multi-level cache shutdown: {e}")
