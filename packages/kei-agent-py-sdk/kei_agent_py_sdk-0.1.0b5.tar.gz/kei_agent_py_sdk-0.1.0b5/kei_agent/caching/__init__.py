"""
KEI Agent Caching Module

Dieses Modul stellt verschiedene Caching-Implementierungen für das KEI Agent SDK bereit.
"""

from __future__ import annotations

# Cache Framework
from .cache_framework import CacheFramework, CacheBackend, CacheConfig

# Cache Manager
from .cache_manager import CacheManager, CacheStrategy

# Specific Cache Implementations
from .memory_cache import MemoryCache
from .persistent_cache import PersistentCache
from .redis_cache import RedisCache
from .multi_level_cache import MultiLevelCache

# Specialized Caches
from .specialized_caches import (
    CapabilityCache,
    DiscoveryCache,
    ConfigurationCache,
    MetricsCache,
)

__all__ = [
    # Framework
    "CacheFramework",
    "CacheBackend",
    "CacheConfig",
    # Manager
    "CacheManager",
    "CacheStrategy",
    # Implementations
    "MemoryCache",
    "PersistentCache",
    "RedisCache",
    "MultiLevelCache",
    # Specialized
    "CapabilityCache",
    "DiscoveryCache",
    "ConfigurationCache",
    "MetricsCache",
]
