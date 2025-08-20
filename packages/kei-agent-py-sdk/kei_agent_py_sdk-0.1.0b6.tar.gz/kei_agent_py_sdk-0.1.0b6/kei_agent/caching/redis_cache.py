# kei_agent/caching/redis_cache.py
"""
L2 Distributed Redis Cache Implementation for KEI-Agent Python SDK.

Redis-based distributed cache with:
- Connection pooling and failover
- Compression and serialization
- Pub/Sub for cache invalidation
- Cluster support and sharding
"""

import asyncio
import json
import logging
import pickle
import time
import zlib
from typing import Any, Dict, List, Optional

try:
    import redis.asyncio as redis
    from redis.asyncio import ConnectionPool, Redis
    from redis.exceptions import RedisError, ConnectionError, TimeoutError

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None
    Redis = None
    ConnectionPool = None
    RedisError = Exception
    ConnectionError = Exception
    TimeoutError = Exception

from .cache_framework import (
    CacheInterface,
    CacheStats,
    CacheConfig,
    CacheMetrics,
    CircuitBreaker,
    get_cache_event_manager,
)

logger = logging.getLogger(__name__)


class RedisCache(CacheInterface):
    """Redis-based distributed cache implementation."""

    def __init__(self, config: CacheConfig, redis_config: Dict[str, Any] = None):
        """Initialize Redis cache.

        Args:
            config: Cache configuration
            redis_config: Redis-specific configuration
        """
        if not REDIS_AVAILABLE:
            raise ImportError("redis package is required for RedisCache")

        self.config = config
        self.redis_config = redis_config or {}

        # Redis connection settings
        self.host = self.redis_config.get("host", "localhost")
        self.port = self.redis_config.get("port", 6379)
        self.db = self.redis_config.get("db", 0)
        self.password = self.redis_config.get("password")
        self.ssl = self.redis_config.get("ssl", False)
        self.key_prefix = self.redis_config.get("key_prefix", "kei_agent:cache:")

        # Connection pool settings
        self.max_connections = self.redis_config.get("max_connections", 20)
        self.connection_timeout = self.redis_config.get("connection_timeout", 5.0)
        self.socket_timeout = self.redis_config.get("socket_timeout", 5.0)

        # Compression settings
        self.compression_threshold = self.redis_config.get(
            "compression_threshold", 1024
        )  # 1KB
        self.compression_level = self.redis_config.get("compression_level", 6)

        # Initialize components
        self._pool: Optional[ConnectionPool] = None
        self._redis: Optional[Redis] = None
        self._metrics = CacheMetrics()
        self._circuit_breaker = (
            CircuitBreaker() if config.circuit_breaker_enabled else None
        )
        self._event_manager = get_cache_event_manager()

        # Pub/Sub for invalidation
        self._pubsub: Optional[redis.client.PubSub] = None
        self._invalidation_channel = f"{self.key_prefix}invalidation"
        self._pubsub_task: Optional[asyncio.Task] = None

        # Initialize connection
        asyncio.create_task(self._initialize_connection())

    async def _initialize_connection(self) -> None:
        """Initialize Redis connection and pool."""
        try:
            # Create connection pool
            self._pool = ConnectionPool(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                ssl=self.ssl,
                max_connections=self.max_connections,
                socket_timeout=self.socket_timeout,
                socket_connect_timeout=self.connection_timeout,
                decode_responses=False,  # We handle encoding ourselves
            )

            # Create Redis client
            self._redis = Redis(connection_pool=self._pool)

            # Test connection
            await self._redis.ping()

            # Setup pub/sub for invalidation
            await self._setup_pubsub()

            logger.info(f"Redis cache connected to {self.host}:{self.port}")

        except Exception as e:
            logger.error(f"Failed to initialize Redis connection: {e}")
            self._redis = None
            self._pool = None

    async def _setup_pubsub(self) -> None:
        """Setup pub/sub for cache invalidation."""
        try:
            if self._redis:
                self._pubsub = self._redis.pubsub()
                await self._pubsub.subscribe(self._invalidation_channel)
                self._pubsub_task = asyncio.create_task(
                    self._handle_invalidation_messages()
                )
        except Exception as e:
            logger.error(f"Failed to setup Redis pub/sub: {e}")

    async def _handle_invalidation_messages(self) -> None:
        """Handle cache invalidation messages from pub/sub."""
        try:
            if not self._pubsub:
                return

            async for message in self._pubsub.listen():
                if message["type"] == "message":
                    try:
                        data = json.loads(message["data"].decode())
                        event_type = data.get("type")

                        if event_type == "invalidate_tags":
                            tags = data.get("tags", [])
                            await self._local_invalidate_by_tags(tags)
                        elif event_type == "invalidate_key":
                            key = data.get("key")
                            if key:
                                self._event_manager.emit(
                                    "cache_invalidate_remote", key=key, level="L2"
                                )

                    except Exception as e:
                        logger.error(f"Error processing invalidation message: {e}")

        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in invalidation message handler: {e}")

    def _make_key(self, key: str) -> str:
        """Create Redis key with prefix."""
        return f"{self.key_prefix}{key}"

    def _make_tag_key(self, tag: str) -> str:
        """Create Redis key for tag index."""
        return f"{self.key_prefix}tags:{tag}"

    def _serialize_value(self, value: Any) -> bytes:
        """Serialize and optionally compress value."""
        # Serialize with pickle
        serialized = pickle.dumps(value)

        # Compress if enabled and above threshold
        if (
            self.config.enable_compression
            and len(serialized) > self.compression_threshold
        ):
            compressed = zlib.compress(serialized, self.compression_level)
            # Add compression marker
            return b"COMPRESSED:" + compressed

        return serialized

    def _deserialize_value(self, data: bytes) -> Any:
        """Deserialize and decompress value."""
        if data.startswith(b"COMPRESSED:"):
            # Remove compression marker and decompress
            compressed_data = data[11:]  # len('COMPRESSED:') = 11
            decompressed = zlib.decompress(compressed_data)
            # WARNING: pickle.loads is used here for internal cache data only
            # This should never be used with untrusted data from external sources
            return pickle.loads(decompressed)  # nosec B301

        # WARNING: pickle.loads is used here for internal cache data only
        # This should never be used with untrusted data from external sources
        return pickle.loads(data)  # nosec B301

    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache."""
        if not self._redis:
            return None

        start_time = time.time()
        redis_key = self._make_key(key)

        try:
            if self._circuit_breaker:
                result = await self._circuit_breaker.call(self._get_internal, redis_key)
            else:
                result = await self._get_internal(redis_key)

            access_time_ms = (time.time() - start_time) * 1000

            if result is not None:
                self._metrics.record_hit(access_time_ms)
                self._event_manager.emit("cache_hit", key=key, level="L2")
            else:
                self._metrics.record_miss(access_time_ms)
                self._event_manager.emit("cache_miss", key=key, level="L2")

            return result

        except Exception as e:
            self._metrics.record_error()
            self._event_manager.emit("cache_error", key=key, level="L2", error=str(e))
            logger.error(f"Error getting Redis cache key {key}: {e}")
            return None

    async def _get_internal(self, redis_key: str) -> Optional[Any]:
        """Internal get method."""
        data = await self._redis.get(redis_key)
        if data is None:
            return None

        return self._deserialize_value(data)

    async def set(
        self, key: str, value: Any, ttl: Optional[float] = None, tags: List[str] = None
    ) -> bool:
        """Set value in Redis cache."""
        if not self._redis:
            return False

        redis_key = self._make_key(key)
        ttl = ttl or self.config.default_ttl

        try:
            if self._circuit_breaker:
                return await self._circuit_breaker.call(
                    self._set_internal, redis_key, key, value, ttl, tags
                )
            else:
                return await self._set_internal(redis_key, key, value, ttl, tags)

        except Exception as e:
            self._metrics.record_error()
            self._event_manager.emit("cache_error", key=key, level="L2", error=str(e))
            logger.error(f"Error setting Redis cache key {key}: {e}")
            return False

    async def _set_internal(
        self, redis_key: str, key: str, value: Any, ttl: float, tags: List[str]
    ) -> bool:
        """Internal set method."""
        # Serialize value
        serialized_value = self._serialize_value(value)

        # Use pipeline for atomic operations
        pipe = self._redis.pipeline()

        # Set the main value
        if ttl:
            pipe.setex(redis_key, int(ttl), serialized_value)
        else:
            pipe.set(redis_key, serialized_value)

        # Update tag indices
        if tags:
            for tag in tags:
                tag_key = self._make_tag_key(tag)
                pipe.sadd(tag_key, key)
                if ttl:
                    pipe.expire(tag_key, int(ttl))

        # Execute pipeline
        await pipe.execute()

        # Calculate size for metrics
        size_bytes = len(serialized_value)
        self._event_manager.emit(
            "cache_set", key=key, level="L2", size_bytes=size_bytes
        )

        return True

    async def delete(self, key: str) -> bool:
        """Delete value from Redis cache."""
        if not self._redis:
            return False

        try:
            redis_key = self._make_key(key)
            result = await self._redis.delete(redis_key)

            if result > 0:
                self._event_manager.emit("cache_delete", key=key, level="L2")

                # Publish invalidation message
                await self._publish_invalidation("invalidate_key", {"key": key})

            return result > 0

        except Exception as e:
            self._metrics.record_error()
            logger.error(f"Error deleting Redis cache key {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis cache."""
        if not self._redis:
            return False

        try:
            redis_key = self._make_key(key)
            result = await self._redis.exists(redis_key)
            return result > 0
        except Exception as e:
            logger.error(f"Error checking Redis cache key existence {key}: {e}")
            return False

    async def clear(self) -> bool:
        """Clear all cache entries with prefix."""
        if not self._redis:
            return False

        try:
            # Find all keys with our prefix
            pattern = f"{self.key_prefix}*"
            keys = []

            async for key in self._redis.scan_iter(match=pattern):
                keys.append(key)

            if keys:
                await self._redis.delete(*keys)

            self._event_manager.emit("cache_clear", level="L2")
            return True

        except Exception as e:
            self._metrics.record_error()
            logger.error(f"Error clearing Redis cache: {e}")
            return False

    async def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        stats = self._metrics.get_stats()

        # Add Redis-specific stats if available
        if self._redis:
            try:
                info = await self._redis.info("memory")
                stats.total_size_bytes = info.get("used_memory", 0)

                # Count keys with our prefix
                pattern = f"{self.key_prefix}*"
                key_count = 0
                async for _ in self._redis.scan_iter(match=pattern):
                    key_count += 1
                stats.entry_count = key_count

            except Exception as e:
                logger.warning(f"Error getting Redis stats: {e}")

        return stats

    async def invalidate_by_tags(self, tags: List[str]) -> int:
        """Invalidate cache entries by tags."""
        if not self._redis:
            return 0

        try:
            invalidated_count = 0
            pipe = self._redis.pipeline()

            # Get all keys for each tag
            all_keys = set()
            for tag in tags:
                tag_key = self._make_tag_key(tag)
                keys = await self._redis.smembers(tag_key)
                all_keys.update(
                    key.decode() if isinstance(key, bytes) else key for key in keys
                )

            # Delete the keys
            if all_keys:
                redis_keys = [self._make_key(key) for key in all_keys]
                deleted_count = await self._redis.delete(*redis_keys)
                invalidated_count = deleted_count

                # Clean up tag indices
                for tag in tags:
                    tag_key = self._make_tag_key(tag)
                    pipe.delete(tag_key)

                await pipe.execute()

            # Publish invalidation message
            await self._publish_invalidation("invalidate_tags", {"tags": tags})

            self._event_manager.emit(
                "cache_invalidate_tags", tags=tags, level="L2", count=invalidated_count
            )
            return invalidated_count

        except Exception as e:
            self._metrics.record_error()
            logger.error(f"Error invalidating Redis cache by tags {tags}: {e}")
            return 0

    async def _local_invalidate_by_tags(self, tags: List[str]) -> None:
        """Handle local invalidation from pub/sub message."""
        # This is called when we receive an invalidation message
        # We don't need to delete from Redis (already done by sender)
        # Just emit local events
        self._event_manager.emit("cache_invalidate_tags_remote", tags=tags, level="L2")

    async def _publish_invalidation(
        self, event_type: str, data: Dict[str, Any]
    ) -> None:
        """Publish cache invalidation message."""
        try:
            if self._redis:
                message = json.dumps({"type": event_type, **data})
                await self._redis.publish(self._invalidation_channel, message)
        except Exception as e:
            logger.error(f"Error publishing invalidation message: {e}")

    async def get_connection_info(self) -> Dict[str, Any]:
        """Get Redis connection information."""
        if not self._redis:
            return {"connected": False}

        try:
            info = await self._redis.info()
            return {
                "connected": True,
                "redis_version": info.get("redis_version"),
                "used_memory": info.get("used_memory"),
                "connected_clients": info.get("connected_clients"),
                "total_commands_processed": info.get("total_commands_processed"),
                "keyspace_hits": info.get("keyspace_hits"),
                "keyspace_misses": info.get("keyspace_misses"),
            }
        except Exception as e:
            logger.error(f"Error getting Redis connection info: {e}")
            return {"connected": False, "error": str(e)}

    async def shutdown(self) -> None:
        """Shutdown Redis cache and cleanup resources."""
        try:
            # Cancel pub/sub task
            if self._pubsub_task:
                self._pubsub_task.cancel()
                try:
                    await self._pubsub_task
                except asyncio.CancelledError:
                    pass

            # Close pub/sub
            if self._pubsub:
                await self._pubsub.unsubscribe(self._invalidation_channel)
                await self._pubsub.close()

            # Close Redis connection
            if self._redis:
                await self._redis.close()

            # Close connection pool
            if self._pool:
                await self._pool.disconnect()

            logger.info("Redis cache shutdown complete")

        except Exception as e:
            logger.error(f"Error during Redis cache shutdown: {e}")
