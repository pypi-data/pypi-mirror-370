# kei_agent/caching/cache_framework.py
"""
Advanced Multi-Level Caching Framework for KEI-Agent Python SDK.

This module provides a comprehensive caching system with:
- Multi-level caching (L1: Memory, L2: Redis, L3: Persistent)
- Advanced invalidation strategies
- Performance monitoring and analytics
- Thread-safe operations with async support
"""

import asyncio
import hashlib
import json
import logging
import time
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Callable

logger = logging.getLogger(__name__)


class CacheLevel(Enum):
    """Cache level enumeration."""

    L1_MEMORY = "l1_memory"
    L2_DISTRIBUTED = "l2_distributed"
    L3_PERSISTENT = "l3_persistent"


class InvalidationStrategy(Enum):
    """Cache invalidation strategy enumeration."""

    TTL = "ttl"
    LRU = "lru"
    LFU = "lfu"
    EVENT_DRIVEN = "event_driven"
    MANUAL = "manual"


@dataclass
class CacheEntry:
    """Represents a cache entry with metadata."""

    key: str
    value: Any
    created_at: float
    last_accessed: float
    access_count: int = 0
    ttl: Optional[float] = None
    size_bytes: int = 0
    tags: List[str] = field(default_factory=list)

    @property
    def is_expired(self) -> bool:
        """Check if the cache entry is expired."""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl

    @property
    def age_seconds(self) -> float:
        """Get the age of the cache entry in seconds."""
        return time.time() - self.created_at

    def touch(self) -> None:
        """Update last accessed time and increment access count."""
        self.last_accessed = time.time()
        self.access_count += 1


@dataclass
class CacheStats:
    """Cache statistics and performance metrics."""

    hits: int = 0
    misses: int = 0
    evictions: int = 0
    errors: int = 0
    total_size_bytes: int = 0
    entry_count: int = 0
    avg_access_time_ms: float = 0.0
    hit_ratio: float = 0.0

    def update_hit_ratio(self) -> None:
        """Update the hit ratio based on hits and misses."""
        total = self.hits + self.misses
        self.hit_ratio = self.hits / total if total > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "errors": self.errors,
            "total_size_bytes": self.total_size_bytes,
            "entry_count": self.entry_count,
            "avg_access_time_ms": self.avg_access_time_ms,
            "hit_ratio": self.hit_ratio,
        }


@dataclass
class CacheConfig:
    """Configuration for cache behavior."""

    max_size_bytes: int = 100 * 1024 * 1024  # 100MB default
    max_entries: int = 10000
    default_ttl: Optional[float] = 3600  # 1 hour default
    invalidation_strategy: InvalidationStrategy = InvalidationStrategy.LRU
    enable_compression: bool = True
    enable_encryption: bool = False
    background_cleanup_interval: float = 300  # 5 minutes
    cache_warming_enabled: bool = True
    circuit_breaker_enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "max_size_bytes": self.max_size_bytes,
            "max_entries": self.max_entries,
            "default_ttl": self.default_ttl,
            "invalidation_strategy": self.invalidation_strategy.value,
            "enable_compression": self.enable_compression,
            "enable_encryption": self.enable_encryption,
            "background_cleanup_interval": self.background_cleanup_interval,
            "cache_warming_enabled": self.cache_warming_enabled,
            "circuit_breaker_enabled": self.circuit_breaker_enabled,
        }


class CacheInterface(ABC):
    """Abstract interface for cache implementations."""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass

    @abstractmethod
    async def set(
        self, key: str, value: Any, ttl: Optional[float] = None, tags: List[str] = None
    ) -> bool:
        """Set value in cache."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        pass

    @abstractmethod
    async def clear(self) -> bool:
        """Clear all cache entries."""
        pass

    @abstractmethod
    async def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        pass

    @abstractmethod
    async def invalidate_by_tags(self, tags: List[str]) -> int:
        """Invalidate cache entries by tags."""
        pass


class CircuitBreaker:
    """Circuit breaker for cache operations."""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0):
        """Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Time to wait before attempting recovery
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "closed"  # closed, open, half_open
        self._lock = threading.Lock()

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        with self._lock:
            if self.state == "open":
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    self.state = "half_open"
                else:
                    raise Exception("Circuit breaker is open")

            try:
                result = func(*args, **kwargs)
                if self.state == "half_open":
                    self.state = "closed"
                    self.failure_count = 0
                return result

            except Exception as e:
                self.failure_count += 1
                self.last_failure_time = time.time()

                if self.failure_count >= self.failure_threshold:
                    self.state = "open"

                raise e


class CacheKeyGenerator:
    """Generates consistent cache keys."""

    @staticmethod
    def generate_key(prefix: str, *args, **kwargs) -> str:
        """Generate a cache key from prefix and arguments.

        Args:
            prefix: Key prefix
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Generated cache key
        """
        # Create a consistent string representation
        key_parts = [prefix]

        # Add positional arguments
        for arg in args:
            if isinstance(arg, (str, int, float, bool)):
                key_parts.append(str(arg))
            else:
                # For complex objects, use JSON representation
                key_parts.append(json.dumps(arg, sort_keys=True, default=str))

        # Add keyword arguments
        if kwargs:
            sorted_kwargs = sorted(kwargs.items())
            for k, v in sorted_kwargs:
                if isinstance(v, (str, int, float, bool)):
                    key_parts.append(f"{k}:{v}")
                else:
                    key_parts.append(
                        f"{k}:{json.dumps(v, sort_keys=True, default=str)}"
                    )

        # Join and hash for consistent length
        key_string = "|".join(key_parts)
        return hashlib.sha256(key_string.encode()).hexdigest()[:32]

    @staticmethod
    def generate_tag_key(tag: str) -> str:
        """Generate a key for tag-based invalidation."""
        return f"tag:{hashlib.md5(tag.encode(), usedforsecurity=False).hexdigest()}"


class CacheEventManager:
    """Manages cache events and notifications."""

    def __init__(self):
        """Initialize event manager."""
        self.listeners: Dict[str, List[Callable]] = {}
        self._lock = threading.Lock()

    def subscribe(self, event_type: str, callback: Callable) -> None:
        """Subscribe to cache events.

        Args:
            event_type: Type of event (hit, miss, eviction, error)
            callback: Callback function to execute
        """
        with self._lock:
            if event_type not in self.listeners:
                self.listeners[event_type] = []
            self.listeners[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback: Callable) -> None:
        """Unsubscribe from cache events."""
        with self._lock:
            if event_type in self.listeners:
                try:
                    self.listeners[event_type].remove(callback)
                except ValueError:
                    pass

    def emit(self, event_type: str, **kwargs) -> None:
        """Emit a cache event.

        Args:
            event_type: Type of event
            **kwargs: Event data
        """
        with self._lock:
            listeners = self.listeners.get(event_type, [])

        for listener in listeners:
            try:
                if asyncio.iscoroutinefunction(listener):
                    asyncio.create_task(listener(**kwargs))
                else:
                    listener(**kwargs)
            except Exception as e:
                logger.error(f"Error in cache event listener: {e}")


class CacheMetrics:
    """Collects and manages cache metrics."""

    def __init__(self):
        """Initialize metrics collector."""
        self.stats = CacheStats()
        self.access_times: List[float] = []
        self.max_access_times = 1000  # Keep last 1000 access times
        self._lock = threading.Lock()

    def record_hit(self, access_time_ms: float) -> None:
        """Record a cache hit."""
        with self._lock:
            self.stats.hits += 1
            self._record_access_time(access_time_ms)
            self.stats.update_hit_ratio()

    def record_miss(self, access_time_ms: float) -> None:
        """Record a cache miss."""
        with self._lock:
            self.stats.misses += 1
            self._record_access_time(access_time_ms)
            self.stats.update_hit_ratio()

    def record_eviction(self) -> None:
        """Record a cache eviction."""
        with self._lock:
            self.stats.evictions += 1

    def record_error(self) -> None:
        """Record a cache error."""
        with self._lock:
            self.stats.errors += 1

    def update_size_stats(self, total_size_bytes: int, entry_count: int) -> None:
        """Update size statistics."""
        with self._lock:
            self.stats.total_size_bytes = total_size_bytes
            self.stats.entry_count = entry_count

    def _record_access_time(self, access_time_ms: float) -> None:
        """Record access time and update average."""
        self.access_times.append(access_time_ms)

        # Keep only recent access times
        if len(self.access_times) > self.max_access_times:
            self.access_times = self.access_times[-self.max_access_times :]

        # Update average
        if self.access_times:
            self.stats.avg_access_time_ms = sum(self.access_times) / len(
                self.access_times
            )

    def get_stats(self) -> CacheStats:
        """Get current statistics."""
        with self._lock:
            return CacheStats(
                hits=self.stats.hits,
                misses=self.stats.misses,
                evictions=self.stats.evictions,
                errors=self.stats.errors,
                total_size_bytes=self.stats.total_size_bytes,
                entry_count=self.stats.entry_count,
                avg_access_time_ms=self.stats.avg_access_time_ms,
                hit_ratio=self.stats.hit_ratio,
            )

    def reset(self) -> None:
        """Reset all statistics."""
        with self._lock:
            self.stats = CacheStats()
            self.access_times.clear()


# Global cache event manager
_cache_event_manager = CacheEventManager()


def get_cache_event_manager() -> CacheEventManager:
    """Get the global cache event manager."""
    return _cache_event_manager
