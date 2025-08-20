# kei_agent/caching/memory_cache.py
"""
L1 Memory Cache Implementation for KEI-Agent Python SDK.

High-performance in-memory cache with:
- LRU/LFU eviction policies
- Thread-safe operations
- Memory pressure monitoring
- Async support with non-blocking operations
"""

import asyncio
import gc
import logging
import pickle
import sys
import threading
import time
from collections import OrderedDict
from typing import Any, Dict, List, Optional, Set
import psutil

from .cache_framework import (
    CacheInterface,
    CacheEntry,
    CacheStats,
    CacheConfig,
    InvalidationStrategy,
    CacheMetrics,
    CircuitBreaker,
    get_cache_event_manager,
)

logger = logging.getLogger(__name__)


class MemoryCache(CacheInterface):
    """High-performance in-memory cache implementation."""

    def __init__(self, config: CacheConfig):
        """Initialize memory cache.

        Args:
            config: Cache configuration
        """
        self.config = config
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order: OrderedDict[str, float] = OrderedDict()  # For LRU
        self.access_frequency: Dict[str, int] = {}  # For LFU
        self.tag_index: Dict[str, Set[str]] = {}  # Tag to keys mapping

        self._lock = threading.RLock()
        self._metrics = CacheMetrics()
        self._circuit_breaker = (
            CircuitBreaker() if config.circuit_breaker_enabled else None
        )
        self._event_manager = get_cache_event_manager()

        # Background cleanup task
        self._cleanup_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()

        # Memory monitoring
        self._memory_pressure_threshold = 0.85  # 85% memory usage
        self._last_gc_time = time.time()
        self._gc_interval = 60  # Force GC every 60 seconds

        # Start background tasks
        self._start_background_tasks()

    def _start_background_tasks(self) -> None:
        """Start background maintenance tasks."""
        if self.config.background_cleanup_interval > 0:
            self._cleanup_task = asyncio.create_task(self._background_cleanup())

    async def _background_cleanup(self) -> None:
        """Background task for cache maintenance."""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(self.config.background_cleanup_interval)
                await self._cleanup_expired_entries()
                await self._check_memory_pressure()
                self._maybe_force_gc()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in background cleanup: {e}")

    async def _cleanup_expired_entries(self) -> None:
        """Remove expired cache entries."""
        expired_keys = []

        with self._lock:
            for key, entry in self.cache.items():
                if entry.is_expired:
                    expired_keys.append(key)

        for key in expired_keys:
            await self._evict_entry(key, reason="expired")

    async def _check_memory_pressure(self) -> None:
        """Check system memory pressure and evict if necessary."""
        try:
            memory = psutil.virtual_memory()
            if memory.percent > self._memory_pressure_threshold * 100:
                # Evict 10% of cache entries
                evict_count = max(1, len(self.cache) // 10)
                await self._evict_entries(evict_count, reason="memory_pressure")
        except Exception as e:
            logger.warning(f"Error checking memory pressure: {e}")

    def _maybe_force_gc(self) -> None:
        """Force garbage collection if needed."""
        current_time = time.time()
        if current_time - self._last_gc_time > self._gc_interval:
            gc.collect()
            self._last_gc_time = current_time

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        start_time = time.time()

        try:
            if self._circuit_breaker:
                result = self._circuit_breaker.call(self._get_internal, key)
            else:
                result = self._get_internal(key)

            access_time_ms = (time.time() - start_time) * 1000

            if result is not None:
                self._metrics.record_hit(access_time_ms)
                self._event_manager.emit("cache_hit", key=key, level="L1")
            else:
                self._metrics.record_miss(access_time_ms)
                self._event_manager.emit("cache_miss", key=key, level="L1")

            return result

        except Exception as e:
            self._metrics.record_error()
            self._event_manager.emit("cache_error", key=key, level="L1", error=str(e))
            logger.error(f"Error getting cache key {key}: {e}")
            return None

    def _get_internal(self, key: str) -> Optional[Any]:
        """Internal get method without metrics."""
        with self._lock:
            entry = self.cache.get(key)

            if entry is None:
                return None

            if entry.is_expired:
                # Remove expired entry
                self._remove_entry(key)
                return None

            # Update access patterns
            entry.touch()
            self._update_access_patterns(key)

            return entry.value

    async def set(
        self, key: str, value: Any, ttl: Optional[float] = None, tags: List[str] = None
    ) -> bool:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            tags: Tags for invalidation

        Returns:
            True if successful
        """
        try:
            if self._circuit_breaker:
                return self._circuit_breaker.call(
                    self._set_internal, key, value, ttl, tags
                )
            else:
                return self._set_internal(key, value, ttl, tags)

        except Exception as e:
            self._metrics.record_error()
            self._event_manager.emit("cache_error", key=key, level="L1", error=str(e))
            logger.error(f"Error setting cache key {key}: {e}")
            return False

    def _set_internal(
        self, key: str, value: Any, ttl: Optional[float], tags: List[str]
    ) -> bool:
        """Internal set method without circuit breaker."""
        with self._lock:
            # Calculate entry size
            try:
                size_bytes = len(pickle.dumps(value))
            except Exception:
                size_bytes = sys.getsizeof(value)

            # Check if we need to evict entries
            if self._should_evict(size_bytes):
                self._evict_for_space(size_bytes)

            # Create cache entry
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=time.time(),
                last_accessed=time.time(),
                ttl=ttl or self.config.default_ttl,
                size_bytes=size_bytes,
                tags=tags or [],
            )

            # Remove old entry if exists
            if key in self.cache:
                self._remove_entry(key)

            # Add new entry
            self.cache[key] = entry
            self._update_access_patterns(key)

            # Update tag index
            for tag in entry.tags:
                if tag not in self.tag_index:
                    self.tag_index[tag] = set()
                self.tag_index[tag].add(key)

            # Update metrics
            self._update_size_metrics()

            self._event_manager.emit(
                "cache_set", key=key, level="L1", size_bytes=size_bytes
            )

            return True

    def _should_evict(self, new_entry_size: int) -> bool:
        """Check if eviction is needed for new entry."""
        current_size = sum(entry.size_bytes for entry in self.cache.values())
        current_count = len(self.cache)

        return (
            current_size + new_entry_size > self.config.max_size_bytes
            or current_count >= self.config.max_entries
        )

    def _evict_for_space(self, needed_size: int) -> None:
        """Evict entries to make space for new entry."""
        current_size = sum(entry.size_bytes for entry in self.cache.values())
        target_size = self.config.max_size_bytes - needed_size

        # Evict until we have enough space
        while current_size > target_size and self.cache:
            key_to_evict = self._select_eviction_candidate()
            if key_to_evict:
                entry = self.cache[key_to_evict]
                current_size -= entry.size_bytes
                self._remove_entry(key_to_evict)
                self._metrics.record_eviction()
                self._event_manager.emit(
                    "cache_eviction", key=key_to_evict, level="L1", reason="space"
                )
            else:
                break

    async def _evict_entries(self, count: int, reason: str = "policy") -> None:
        """Evict specified number of entries."""
        evicted = 0
        while evicted < count and self.cache:
            key_to_evict = self._select_eviction_candidate()
            if key_to_evict:
                await self._evict_entry(key_to_evict, reason)
                evicted += 1
            else:
                break

    async def _evict_entry(self, key: str, reason: str = "policy") -> None:
        """Evict a specific entry."""
        with self._lock:
            if key in self.cache:
                self._remove_entry(key)
                self._metrics.record_eviction()
                self._event_manager.emit(
                    "cache_eviction", key=key, level="L1", reason=reason
                )

    def _select_eviction_candidate(self) -> Optional[str]:
        """Select a key for eviction based on strategy."""
        if not self.cache:
            return None

        if self.config.invalidation_strategy == InvalidationStrategy.LRU:
            return self._select_lru_candidate()
        elif self.config.invalidation_strategy == InvalidationStrategy.LFU:
            return self._select_lfu_candidate()
        else:
            # Default to LRU
            return self._select_lru_candidate()

    def _select_lru_candidate(self) -> Optional[str]:
        """Select least recently used key."""
        if not self.access_order:
            return next(iter(self.cache.keys())) if self.cache else None
        return next(iter(self.access_order))

    def _select_lfu_candidate(self) -> Optional[str]:
        """Select least frequently used key."""
        if not self.access_frequency:
            return next(iter(self.cache.keys())) if self.cache else None

        min_frequency = min(self.access_frequency.values())
        for key, frequency in self.access_frequency.items():
            if frequency == min_frequency and key in self.cache:
                return key

        return None

    def _update_access_patterns(self, key: str) -> None:
        """Update access patterns for eviction policies."""
        current_time = time.time()

        # Update LRU order
        if key in self.access_order:
            del self.access_order[key]
        self.access_order[key] = current_time

        # Update LFU frequency
        self.access_frequency[key] = self.access_frequency.get(key, 0) + 1

    def _remove_entry(self, key: str) -> None:
        """Remove entry and update indices."""
        if key not in self.cache:
            return

        entry = self.cache[key]

        # Remove from cache
        del self.cache[key]

        # Remove from access patterns
        self.access_order.pop(key, None)
        self.access_frequency.pop(key, None)

        # Remove from tag index
        for tag in entry.tags:
            if tag in self.tag_index:
                self.tag_index[tag].discard(key)
                if not self.tag_index[tag]:
                    del self.tag_index[tag]

        # Update metrics
        self._update_size_metrics()

    def _update_size_metrics(self) -> None:
        """Update size-related metrics."""
        total_size = sum(entry.size_bytes for entry in self.cache.values())
        entry_count = len(self.cache)
        self._metrics.update_size_stats(total_size, entry_count)

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        try:
            with self._lock:
                if key in self.cache:
                    self._remove_entry(key)
                    self._event_manager.emit("cache_delete", key=key, level="L1")
                    return True
                return False
        except Exception as e:
            self._metrics.record_error()
            logger.error(f"Error deleting cache key {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            with self._lock:
                entry = self.cache.get(key)
                return entry is not None and not entry.is_expired
        except Exception as e:
            logger.error(f"Error checking cache key existence {key}: {e}")
            return False

    async def clear(self) -> bool:
        """Clear all cache entries."""
        try:
            with self._lock:
                self.cache.clear()
                self.access_order.clear()
                self.access_frequency.clear()
                self.tag_index.clear()
                self._update_size_metrics()
                self._event_manager.emit("cache_clear", level="L1")
                return True
        except Exception as e:
            self._metrics.record_error()
            logger.error(f"Error clearing cache: {e}")
            return False

    async def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        return self._metrics.get_stats()

    async def invalidate_by_tags(self, tags: List[str]) -> int:
        """Invalidate cache entries by tags."""
        invalidated_count = 0
        keys_to_remove = set()

        with self._lock:
            for tag in tags:
                if tag in self.tag_index:
                    keys_to_remove.update(self.tag_index[tag])

        for key in keys_to_remove:
            if await self.delete(key):
                invalidated_count += 1

        self._event_manager.emit(
            "cache_invalidate_tags", tags=tags, level="L1", count=invalidated_count
        )
        return invalidated_count

    async def shutdown(self) -> None:
        """Shutdown cache and cleanup resources."""
        self._shutdown_event.set()

        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        await self.clear()
        logger.info("Memory cache shutdown complete")
