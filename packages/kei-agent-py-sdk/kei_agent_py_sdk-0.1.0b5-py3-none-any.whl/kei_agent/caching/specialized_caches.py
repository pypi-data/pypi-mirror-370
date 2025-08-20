# kei_agent/caching/specialized_caches.py
"""
Specialized Cache Implementations for KEI-Agent Python SDK.

Provides domain-specific caches for:
- API response caching with smart invalidation
- Authentication token caching with refresh logic
- Configuration caching with hot-reload support
- Protocol-specific caching (RPC, Stream, Bus, MCP)
- Metrics and telemetry data caching
"""

import asyncio
import hashlib
import logging
import time
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime

from .cache_framework import CacheKeyGenerator, get_cache_event_manager
from .multi_level_cache import MultiLevelCache

logger = logging.getLogger(__name__)


@dataclass
class CachePolicy:
    """Cache policy configuration."""

    ttl: Optional[float] = None
    max_size: Optional[int] = None
    invalidation_tags: List[str] = None
    refresh_ahead: bool = False
    refresh_threshold: float = 0.8  # Refresh when 80% of TTL elapsed

    def __post_init__(self):
        if self.invalidation_tags is None:
            self.invalidation_tags = []


class ResponseCache:
    """Specialized cache for API responses and RPC calls."""

    def __init__(self, cache: MultiLevelCache, default_policy: CachePolicy = None):
        """Initialize response cache.

        Args:
            cache: Underlying multi-level cache
            default_policy: Default cache policy
        """
        self.cache = cache
        self.default_policy = default_policy or CachePolicy(ttl=300)  # 5 minutes
        self._event_manager = get_cache_event_manager()

        # Response-specific settings
        self.cache_key_prefix = "response"
        self.vary_headers = ["Authorization", "User-Agent", "Accept-Language"]

        # Background refresh tasks
        self._refresh_tasks: Dict[str, asyncio.Task] = {}

    async def get_response(
        self,
        method: str,
        url: str,
        params: Dict[str, Any] = None,
        headers: Dict[str, str] = None,
        policy: CachePolicy = None,
    ) -> Optional[Dict[str, Any]]:
        """Get cached response.

        Args:
            method: HTTP method
            url: Request URL
            params: Request parameters
            headers: Request headers
            policy: Cache policy override

        Returns:
            Cached response or None
        """
        cache_key = self._generate_response_key(method, url, params, headers)

        cached_response = await self.cache.get(cache_key)
        if cached_response is None:
            return None

        # Check if refresh ahead is needed
        policy = policy or self.default_policy
        if policy.refresh_ahead:
            await self._check_refresh_ahead(cache_key, cached_response, policy)

        # Update response metadata
        cached_response["cache_metadata"] = {
            "hit": True,
            "timestamp": time.time(),
            "key": cache_key,
        }

        return cached_response

    async def set_response(
        self,
        method: str,
        url: str,
        response: Dict[str, Any],
        params: Dict[str, Any] = None,
        headers: Dict[str, str] = None,
        policy: CachePolicy = None,
    ) -> bool:
        """Cache response.

        Args:
            method: HTTP method
            url: Request URL
            response: Response to cache
            params: Request parameters
            headers: Request headers
            policy: Cache policy override

        Returns:
            True if cached successfully
        """
        policy = policy or self.default_policy
        cache_key = self._generate_response_key(method, url, params, headers)

        # Add cache metadata
        cached_response = {
            **response,
            "cache_metadata": {
                "cached_at": time.time(),
                "ttl": policy.ttl,
                "key": cache_key,
            },
        }

        # Generate tags for invalidation
        tags = policy.invalidation_tags.copy()
        tags.extend(
            [f"url:{self._hash_url(url)}", f"method:{method.lower()}", "response_cache"]
        )

        return await self.cache.set(cache_key, cached_response, policy.ttl, tags)

    async def invalidate_by_url_pattern(self, url_pattern: str) -> int:
        """Invalidate responses matching URL pattern."""
        tag = f"url:{self._hash_url(url_pattern)}"
        results = await self.cache.invalidate_by_tags([tag])
        return sum(results.values())

    async def invalidate_by_method(self, method: str) -> int:
        """Invalidate responses by HTTP method."""
        tag = f"method:{method.lower()}"
        results = await self.cache.invalidate_by_tags([tag])
        return sum(results.values())

    def _generate_response_key(
        self, method: str, url: str, params: Dict[str, Any], headers: Dict[str, str]
    ) -> str:
        """Generate cache key for response."""
        # Include vary headers in key generation
        vary_values = {}
        if headers:
            for header in self.vary_headers:
                if header in headers:
                    vary_values[header] = headers[header]

        return CacheKeyGenerator.generate_key(
            self.cache_key_prefix, method.upper(), url, params or {}, vary_values
        )

    def _hash_url(self, url: str) -> str:
        """Generate hash for URL."""
        return hashlib.md5(url.encode(), usedforsecurity=False).hexdigest()[:16]

    async def _check_refresh_ahead(
        self, cache_key: str, cached_response: Dict[str, Any], policy: CachePolicy
    ) -> None:
        """Check if refresh ahead is needed."""
        if cache_key in self._refresh_tasks:
            return  # Already refreshing

        cache_metadata = cached_response.get("cache_metadata", {})
        cached_at = cache_metadata.get("cached_at", 0)
        ttl = cache_metadata.get("ttl", policy.ttl)

        if not ttl:
            return

        elapsed = time.time() - cached_at
        if elapsed >= (ttl * policy.refresh_threshold):
            # Schedule background refresh
            self._refresh_tasks[cache_key] = asyncio.create_task(
                self._background_refresh(cache_key, cached_response)
            )

    async def _background_refresh(
        self, cache_key: str, cached_response: Dict[str, Any]
    ) -> None:
        """Background refresh of cached response."""
        try:
            # This would trigger the original request to refresh the cache
            # Implementation depends on the specific use case
            self._event_manager.emit(
                "cache_refresh_needed", key=cache_key, response=cached_response
            )
        except Exception as e:
            logger.error(f"Error in background refresh for {cache_key}: {e}")
        finally:
            self._refresh_tasks.pop(cache_key, None)


class AuthTokenCache:
    """Specialized cache for authentication tokens with refresh logic."""

    def __init__(self, cache: MultiLevelCache):
        """Initialize auth token cache.

        Args:
            cache: Underlying multi-level cache
        """
        self.cache = cache
        self.cache_key_prefix = "auth_token"
        self._refresh_callbacks: Dict[str, Callable] = {}
        self._refresh_locks: Dict[str, asyncio.Lock] = {}

    async def get_token(
        self, user_id: str, scope: str = "default"
    ) -> Optional[Dict[str, Any]]:
        """Get authentication token.

        Args:
            user_id: User identifier
            scope: Token scope

        Returns:
            Token data or None
        """
        cache_key = self._generate_token_key(user_id, scope)

        token_data = await self.cache.get(cache_key)
        if token_data is None:
            return None

        # Check if token is expired or needs refresh
        if self._is_token_expired(token_data):
            await self.cache.delete(cache_key)
            return None

        if self._should_refresh_token(token_data):
            # Trigger background refresh
            asyncio.create_task(self._refresh_token(user_id, scope))

        return token_data

    async def set_token(
        self, user_id: str, token_data: Dict[str, Any], scope: str = "default"
    ) -> bool:
        """Cache authentication token.

        Args:
            user_id: User identifier
            token_data: Token data including access_token, expires_at, etc.
            scope: Token scope

        Returns:
            True if cached successfully
        """
        cache_key = self._generate_token_key(user_id, scope)

        # Calculate TTL based on token expiration
        expires_at = token_data.get("expires_at")
        ttl = None
        if expires_at:
            if isinstance(expires_at, (int, float)):
                ttl = max(0, expires_at - time.time())
            elif isinstance(expires_at, datetime):
                ttl = max(0, (expires_at - datetime.now()).total_seconds())

        # Add cache metadata
        enhanced_token_data = {
            **token_data,
            "cached_at": time.time(),
            "user_id": user_id,
            "scope": scope,
        }

        tags = [f"user:{user_id}", f"scope:{scope}", "auth_token"]

        return await self.cache.set(cache_key, enhanced_token_data, ttl, tags)

    async def invalidate_user_tokens(self, user_id: str) -> int:
        """Invalidate all tokens for a user."""
        tag = f"user:{user_id}"
        results = await self.cache.invalidate_by_tags([tag])
        return sum(results.values())

    async def invalidate_scope_tokens(self, scope: str) -> int:
        """Invalidate all tokens for a scope."""
        tag = f"scope:{scope}"
        results = await self.cache.invalidate_by_tags([tag])
        return sum(results.values())

    def register_refresh_callback(self, scope: str, callback: Callable) -> None:
        """Register callback for token refresh.

        Args:
            scope: Token scope
            callback: Async function to refresh token
        """
        self._refresh_callbacks[scope] = callback

    def _generate_token_key(self, user_id: str, scope: str) -> str:
        """Generate cache key for token."""
        return CacheKeyGenerator.generate_key(self.cache_key_prefix, user_id, scope)

    def _is_token_expired(self, token_data: Dict[str, Any]) -> bool:
        """Check if token is expired."""
        expires_at = token_data.get("expires_at")
        if not expires_at:
            return False

        if isinstance(expires_at, (int, float)):
            return time.time() >= expires_at
        elif isinstance(expires_at, datetime):
            return datetime.now() >= expires_at

        return False

    def _should_refresh_token(self, token_data: Dict[str, Any]) -> bool:
        """Check if token should be refreshed proactively."""
        expires_at = token_data.get("expires_at")
        if not expires_at:
            return False

        # Refresh when 80% of lifetime has elapsed
        refresh_threshold = 0.8

        if isinstance(expires_at, (int, float)):
            cached_at = token_data.get("cached_at", time.time())
            lifetime = expires_at - cached_at
            elapsed = time.time() - cached_at
            return elapsed >= (lifetime * refresh_threshold)

        return False

    async def _refresh_token(self, user_id: str, scope: str) -> None:
        """Refresh token in background."""
        cache_key = self._generate_token_key(user_id, scope)

        # Use lock to prevent concurrent refreshes
        if cache_key not in self._refresh_locks:
            self._refresh_locks[cache_key] = asyncio.Lock()

        async with self._refresh_locks[cache_key]:
            try:
                callback = self._refresh_callbacks.get(scope)
                if callback:
                    new_token_data = await callback(user_id, scope)
                    if new_token_data:
                        await self.set_token(user_id, new_token_data, scope)
            except Exception as e:
                logger.error(f"Error refreshing token for {user_id}:{scope}: {e}")


class ConfigCache:
    """Specialized cache for configuration data with hot-reload support."""

    def __init__(self, cache: MultiLevelCache):
        """Initialize config cache.

        Args:
            cache: Underlying multi-level cache
        """
        self.cache = cache
        self.cache_key_prefix = "config"
        self._event_manager = get_cache_event_manager()

        # Setup event handlers for config changes
        self._event_manager.subscribe("config_changed", self._handle_config_change)

    async def get_config(
        self, config_name: str, version: str = "latest"
    ) -> Optional[Dict[str, Any]]:
        """Get configuration data.

        Args:
            config_name: Configuration name
            version: Configuration version

        Returns:
            Configuration data or None
        """
        cache_key = self._generate_config_key(config_name, version)
        return await self.cache.get(cache_key)

    async def set_config(
        self,
        config_name: str,
        config_data: Dict[str, Any],
        version: str = "latest",
        ttl: Optional[float] = None,
    ) -> bool:
        """Cache configuration data.

        Args:
            config_name: Configuration name
            config_data: Configuration data
            version: Configuration version
            ttl: Time to live (None for no expiration)

        Returns:
            True if cached successfully
        """
        cache_key = self._generate_config_key(config_name, version)

        # Add metadata
        enhanced_config = {
            **config_data,
            "config_metadata": {
                "name": config_name,
                "version": version,
                "cached_at": time.time(),
            },
        }

        tags = [f"config:{config_name}", f"version:{version}", "configuration"]

        return await self.cache.set(cache_key, enhanced_config, ttl, tags)

    async def invalidate_config(self, config_name: str, version: str = None) -> int:
        """Invalidate configuration cache.

        Args:
            config_name: Configuration name
            version: Specific version (None for all versions)

        Returns:
            Number of invalidated entries
        """
        if version:
            tags = [f"config:{config_name}", f"version:{version}"]
        else:
            tags = [f"config:{config_name}"]

        results = await self.cache.invalidate_by_tags(tags)
        return sum(results.values())

    def _generate_config_key(self, config_name: str, version: str) -> str:
        """Generate cache key for configuration."""
        return CacheKeyGenerator.generate_key(
            self.cache_key_prefix, config_name, version
        )

    async def _handle_config_change(self, **kwargs) -> None:
        """Handle configuration change events."""
        config_name = kwargs.get("config_name")
        if config_name:
            await self.invalidate_config(config_name)


class ProtocolCache:
    """Specialized cache for protocol-specific data (RPC, Stream, Bus, MCP)."""

    def __init__(self, cache: MultiLevelCache):
        """Initialize protocol cache.

        Args:
            cache: Underlying multi-level cache
        """
        self.cache = cache
        self.protocol_policies = {
            "rpc": CachePolicy(ttl=600, invalidation_tags=["rpc"]),  # 10 minutes
            "stream": CachePolicy(ttl=60, invalidation_tags=["stream"]),  # 1 minute
            "bus": CachePolicy(ttl=300, invalidation_tags=["bus"]),  # 5 minutes
            "mcp": CachePolicy(ttl=1800, invalidation_tags=["mcp"]),  # 30 minutes
        }

    async def get_protocol_data(
        self, protocol: str, operation: str, params: Dict[str, Any] = None
    ) -> Optional[Any]:
        """Get cached protocol data.

        Args:
            protocol: Protocol name (rpc, stream, bus, mcp)
            operation: Operation name
            params: Operation parameters

        Returns:
            Cached data or None
        """
        cache_key = self._generate_protocol_key(protocol, operation, params)
        return await self.cache.get(cache_key)

    async def set_protocol_data(
        self,
        protocol: str,
        operation: str,
        data: Any,
        params: Dict[str, Any] = None,
        custom_policy: CachePolicy = None,
    ) -> bool:
        """Cache protocol data.

        Args:
            protocol: Protocol name
            operation: Operation name
            data: Data to cache
            params: Operation parameters
            custom_policy: Custom cache policy

        Returns:
            True if cached successfully
        """
        cache_key = self._generate_protocol_key(protocol, operation, params)
        policy = custom_policy or self.protocol_policies.get(protocol, CachePolicy())

        tags = policy.invalidation_tags.copy()
        tags.extend([f"protocol:{protocol}", f"operation:{operation}"])

        return await self.cache.set(cache_key, data, policy.ttl, tags)

    async def invalidate_protocol(self, protocol: str) -> int:
        """Invalidate all data for a protocol."""
        tag = f"protocol:{protocol}"
        results = await self.cache.invalidate_by_tags([tag])
        return sum(results.values())

    async def invalidate_operation(self, protocol: str, operation: str) -> int:
        """Invalidate data for a specific operation."""
        tags = [f"protocol:{protocol}", f"operation:{operation}"]
        results = await self.cache.invalidate_by_tags(tags)
        return sum(results.values())

    def _generate_protocol_key(
        self, protocol: str, operation: str, params: Dict[str, Any]
    ) -> str:
        """Generate cache key for protocol data."""
        return CacheKeyGenerator.generate_key(
            "protocol", protocol, operation, params or {}
        )


class MetricsCache:
    """Specialized cache for metrics and telemetry data with batch processing."""

    def __init__(self, cache: MultiLevelCache):
        """Initialize metrics cache.

        Args:
            cache: Underlying multi-level cache
        """
        self.cache = cache
        self.cache_key_prefix = "metrics"
        self.batch_size = 100
        self.batch_timeout = 30  # seconds

        # Batching for metrics
        self._pending_metrics: List[Dict[str, Any]] = []
        self._batch_lock = asyncio.Lock()
        self._batch_task: Optional[asyncio.Task] = None

        self._start_batch_processing()

    def _start_batch_processing(self) -> None:
        """Start background batch processing."""
        self._batch_task = asyncio.create_task(self._batch_processor())

    async def _batch_processor(self) -> None:
        """Process metrics in batches."""
        while True:
            try:
                await asyncio.sleep(self.batch_timeout)
                await self._flush_batch()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in metrics batch processor: {e}")

    async def add_metric(self, metric_data: Dict[str, Any]) -> None:
        """Add metric to batch for caching.

        Args:
            metric_data: Metric data to cache
        """
        async with self._batch_lock:
            self._pending_metrics.append(metric_data)

            if len(self._pending_metrics) >= self.batch_size:
                await self._flush_batch()

    async def _flush_batch(self) -> None:
        """Flush pending metrics to cache."""
        async with self._batch_lock:
            if not self._pending_metrics:
                return

            batch = self._pending_metrics.copy()
            self._pending_metrics.clear()

        # Cache the batch
        cache_key = CacheKeyGenerator.generate_key(
            self.cache_key_prefix, "batch", int(time.time())
        )

        await self.cache.set(cache_key, batch, ttl=3600, tags=["metrics", "batch"])

    async def get_metrics_batch(
        self, start_time: float, end_time: float
    ) -> List[Dict[str, Any]]:
        """Get metrics batches within time range.

        Args:
            start_time: Start timestamp
            end_time: End timestamp

        Returns:
            List of metric batches
        """
        # This would require a more sophisticated query mechanism
        # For now, return empty list as placeholder
        return []

    async def shutdown(self) -> None:
        """Shutdown metrics cache and flush pending data."""
        if self._batch_task:
            self._batch_task.cancel()
            try:
                await self._batch_task
            except asyncio.CancelledError:
                pass

        await self._flush_batch()
