# kei_agent/caching/persistent_cache.py
"""
L3 Persistent File Cache Implementation for KEI-Agent Python SDK.

File-based persistent cache with:
- SQLite backend for metadata and indexing
- Configurable storage formats (pickle, JSON, compressed)
- Atomic operations and crash recovery
- Efficient cleanup and maintenance
"""

import asyncio
import hashlib
import json
import logging
import pickle
import sqlite3
import time
import zlib
from pathlib import Path
from typing import Any, Dict, List, Optional
import aiofiles
import aiofiles.os

from .cache_framework import (
    CacheInterface,
    CacheStats,
    CacheConfig,
    CacheMetrics,
    CircuitBreaker,
    get_cache_event_manager,
)

logger = logging.getLogger(__name__)


class PersistentCache(CacheInterface):
    """File-based persistent cache implementation."""

    def __init__(self, config: CacheConfig, storage_config: Dict[str, Any] = None):
        """Initialize persistent cache.

        Args:
            config: Cache configuration
            storage_config: Storage-specific configuration
        """
        self.config = config
        self.storage_config = storage_config or {}

        # Storage settings
        self.cache_dir = Path(self.storage_config.get("cache_dir", "cache"))
        self.db_path = self.cache_dir / "cache_metadata.db"
        self.data_dir = self.cache_dir / "data"

        # Storage format settings
        self.storage_format = self.storage_config.get(
            "format", "pickle"
        )  # pickle, json, compressed
        self.compression_level = self.storage_config.get("compression_level", 6)
        self.sync_interval = self.storage_config.get("sync_interval", 60)  # seconds

        # Initialize components
        self._metrics = CacheMetrics()
        self._circuit_breaker = (
            CircuitBreaker() if config.circuit_breaker_enabled else None
        )
        self._event_manager = get_cache_event_manager()

        # Database connection (thread-local)
        self._db_lock = asyncio.Lock()
        self._db_connection: Optional[sqlite3.Connection] = None

        # Background tasks
        self._sync_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()

        # Initialize storage
        asyncio.create_task(self._initialize_storage())

    async def _initialize_storage(self) -> None:
        """Initialize storage directories and database."""
        try:
            # Create directories
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self.data_dir.mkdir(parents=True, exist_ok=True)

            # Initialize database
            await self._init_database()

            # Start background tasks
            self._start_background_tasks()

            logger.info(f"Persistent cache initialized at {self.cache_dir}")

        except Exception as e:
            logger.error(f"Failed to initialize persistent cache: {e}")

    async def _init_database(self) -> None:
        """Initialize SQLite database for metadata."""
        async with self._db_lock:
            self._db_connection = sqlite3.connect(str(self.db_path))
            self._db_connection.execute("""
                CREATE TABLE IF NOT EXISTS cache_entries (
                    key TEXT PRIMARY KEY,
                    file_path TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    last_accessed REAL NOT NULL,
                    access_count INTEGER DEFAULT 0,
                    ttl REAL,
                    size_bytes INTEGER DEFAULT 0,
                    tags TEXT,
                    format TEXT DEFAULT 'pickle'
                )
            """)

            self._db_connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_created_at ON cache_entries(created_at)
            """)

            self._db_connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_last_accessed ON cache_entries(last_accessed)
            """)

            self._db_connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_ttl ON cache_entries(ttl)
            """)

            self._db_connection.commit()

    def _start_background_tasks(self) -> None:
        """Start background maintenance tasks."""
        if self.sync_interval > 0:
            self._sync_task = asyncio.create_task(self._background_sync())

        if self.config.background_cleanup_interval > 0:
            self._cleanup_task = asyncio.create_task(self._background_cleanup())

    async def _background_sync(self) -> None:
        """Background task for periodic database sync."""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(self.sync_interval)
                await self._sync_database()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in background sync: {e}")

    async def _background_cleanup(self) -> None:
        """Background task for cache cleanup."""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(self.config.background_cleanup_interval)
                await self._cleanup_expired_entries()
                await self._cleanup_orphaned_files()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in background cleanup: {e}")

    async def _sync_database(self) -> None:
        """Sync database to disk."""
        try:
            async with self._db_lock:
                if self._db_connection:
                    self._db_connection.commit()
        except Exception as e:
            logger.error(f"Error syncing database: {e}")

    async def _cleanup_expired_entries(self) -> None:
        """Remove expired cache entries."""
        try:
            current_time = time.time()
            expired_keys = []

            async with self._db_lock:
                if self._db_connection:
                    cursor = self._db_connection.execute(
                        """
                        SELECT key FROM cache_entries
                        WHERE ttl IS NOT NULL AND (created_at + ttl) < ?
                    """,
                        (current_time,),
                    )

                    expired_keys = [row[0] for row in cursor.fetchall()]

            for key in expired_keys:
                await self.delete(key)

        except Exception as e:
            logger.error(f"Error cleaning up expired entries: {e}")

    async def _cleanup_orphaned_files(self) -> None:
        """Remove orphaned data files."""
        try:
            # Get all file paths from database
            db_files = set()
            async with self._db_lock:
                if self._db_connection:
                    cursor = self._db_connection.execute(
                        "SELECT file_path FROM cache_entries"
                    )
                    db_files = {row[0] for row in cursor.fetchall()}

            # Check for orphaned files
            for file_path in self.data_dir.iterdir():
                if file_path.is_file() and str(file_path) not in db_files:
                    try:
                        await aiofiles.os.remove(file_path)
                        logger.debug(f"Removed orphaned cache file: {file_path}")
                    except Exception as e:
                        logger.warning(f"Error removing orphaned file {file_path}: {e}")

        except Exception as e:
            logger.error(f"Error cleaning up orphaned files: {e}")

    def _generate_file_path(self, key: str) -> Path:
        """Generate file path for cache key."""
        # Use hash to avoid filesystem issues with special characters
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return self.data_dir / f"{key_hash}.cache"

    async def _serialize_to_file(self, file_path: Path, value: Any) -> int:
        """Serialize value to file and return size."""
        temp_path = file_path.with_suffix(".tmp")

        try:
            if self.storage_format == "json":
                data = json.dumps(value, default=str).encode()
            elif self.storage_format == "compressed":
                pickled = pickle.dumps(value)
                data = zlib.compress(pickled, self.compression_level)
            else:  # pickle (default)
                data = pickle.dumps(value)

            # Write to temporary file first (atomic operation)
            async with aiofiles.open(temp_path, "wb") as f:
                await f.write(data)

            # Atomic rename
            await aiofiles.os.rename(temp_path, file_path)

            return len(data)

        except Exception as e:
            # Cleanup temp file on error
            try:
                await aiofiles.os.remove(temp_path)
            except Exception as cleanup_error:
                # Log cleanup errors but don't fail the operation
                import logging

                logging.getLogger(__name__).debug(
                    f"Failed to cleanup temp file {temp_path}: {cleanup_error}"
                )
            raise e

    async def _deserialize_from_file(
        self, file_path: Path, format_type: str = "pickle"
    ) -> Any:
        """Deserialize value from file."""
        async with aiofiles.open(file_path, "rb") as f:
            data = await f.read()

        if format_type == "json":
            return json.loads(data.decode())
        elif format_type == "compressed":
            decompressed = zlib.decompress(data)
            # WARNING: pickle.loads is used here for internal cache data only
            # This should never be used with untrusted data from external sources
            return pickle.loads(decompressed)  # nosec B301
        else:  # pickle (default)
            # WARNING: pickle.loads is used here for internal cache data only
            # This should never be used with untrusted data from external sources
            return pickle.loads(data)  # nosec B301

    async def get(self, key: str) -> Optional[Any]:
        """Get value from persistent cache."""
        start_time = time.time()

        try:
            if self._circuit_breaker:
                result = await self._circuit_breaker.call(self._get_internal, key)
            else:
                result = await self._get_internal(key)

            access_time_ms = (time.time() - start_time) * 1000

            if result is not None:
                self._metrics.record_hit(access_time_ms)
                self._event_manager.emit("cache_hit", key=key, level="L3")
            else:
                self._metrics.record_miss(access_time_ms)
                self._event_manager.emit("cache_miss", key=key, level="L3")

            return result

        except Exception as e:
            self._metrics.record_error()
            self._event_manager.emit("cache_error", key=key, level="L3", error=str(e))
            logger.error(f"Error getting persistent cache key {key}: {e}")
            return None

    async def _get_internal(self, key: str) -> Optional[Any]:
        """Internal get method."""
        async with self._db_lock:
            if not self._db_connection:
                return None

            cursor = self._db_connection.execute(
                """
                SELECT file_path, created_at, ttl, format FROM cache_entries WHERE key = ?
            """,
                (key,),
            )

            row = cursor.fetchone()
            if not row:
                return None

            file_path, created_at, ttl, format_type = row

            # Check if expired
            if ttl and (time.time() - created_at) > ttl:
                # Remove expired entry
                await self._remove_entry(key, file_path)
                return None

            # Update access information
            current_time = time.time()
            self._db_connection.execute(
                """
                UPDATE cache_entries
                SET last_accessed = ?, access_count = access_count + 1
                WHERE key = ?
            """,
                (current_time, key),
            )

        # Read from file
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                # File missing, remove from database
                await self._remove_entry(key, file_path)
                return None

            return await self._deserialize_from_file(file_path_obj, format_type)

        except Exception as e:
            logger.error(f"Error reading cache file {file_path}: {e}")
            # Remove corrupted entry
            await self._remove_entry(key, file_path)
            return None

    async def set(
        self, key: str, value: Any, ttl: Optional[float] = None, tags: List[str] = None
    ) -> bool:
        """Set value in persistent cache."""
        try:
            if self._circuit_breaker:
                return await self._circuit_breaker.call(
                    self._set_internal, key, value, ttl, tags
                )
            else:
                return await self._set_internal(key, value, ttl, tags)

        except Exception as e:
            self._metrics.record_error()
            self._event_manager.emit("cache_error", key=key, level="L3", error=str(e))
            logger.error(f"Error setting persistent cache key {key}: {e}")
            return False

    async def _set_internal(
        self, key: str, value: Any, ttl: Optional[float], tags: List[str]
    ) -> bool:
        """Internal set method."""
        file_path = self._generate_file_path(key)

        # Serialize to file
        size_bytes = await self._serialize_to_file(file_path, value)

        # Update database
        current_time = time.time()
        tags_json = json.dumps(tags) if tags else None

        async with self._db_lock:
            if not self._db_connection:
                return False

            # Remove old entry if exists
            old_cursor = self._db_connection.execute(
                "SELECT file_path FROM cache_entries WHERE key = ?", (key,)
            )
            old_row = old_cursor.fetchone()
            if old_row:
                old_file_path = Path(old_row[0])
                if old_file_path.exists() and old_file_path != file_path:
                    try:
                        await aiofiles.os.remove(old_file_path)
                    except Exception as e:
                        logger.warning(f"Error removing old cache file: {e}")

            # Insert/update entry
            self._db_connection.execute(
                """
                INSERT OR REPLACE INTO cache_entries
                (key, file_path, created_at, last_accessed, ttl, size_bytes, tags, format)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    key,
                    str(file_path),
                    current_time,
                    current_time,
                    ttl or self.config.default_ttl,
                    size_bytes,
                    tags_json,
                    self.storage_format,
                ),
            )

        self._event_manager.emit(
            "cache_set", key=key, level="L3", size_bytes=size_bytes
        )
        return True

    async def delete(self, key: str) -> bool:
        """Delete value from persistent cache."""
        try:
            async with self._db_lock:
                if not self._db_connection:
                    return False

                cursor = self._db_connection.execute(
                    "SELECT file_path FROM cache_entries WHERE key = ?", (key,)
                )
                row = cursor.fetchone()

                if row:
                    file_path = row[0]
                    await self._remove_entry(key, file_path)
                    self._event_manager.emit("cache_delete", key=key, level="L3")
                    return True

                return False

        except Exception as e:
            self._metrics.record_error()
            logger.error(f"Error deleting persistent cache key {key}: {e}")
            return False

    async def _remove_entry(self, key: str, file_path: str) -> None:
        """Remove cache entry and associated file."""
        # Remove from database
        async with self._db_lock:
            if self._db_connection:
                self._db_connection.execute(
                    "DELETE FROM cache_entries WHERE key = ?", (key,)
                )

        # Remove file
        try:
            file_path_obj = Path(file_path)
            if file_path_obj.exists():
                await aiofiles.os.remove(file_path_obj)
        except Exception as e:
            logger.warning(f"Error removing cache file {file_path}: {e}")

    async def exists(self, key: str) -> bool:
        """Check if key exists in persistent cache."""
        try:
            async with self._db_lock:
                if not self._db_connection:
                    return False

                cursor = self._db_connection.execute(
                    """
                    SELECT created_at, ttl FROM cache_entries WHERE key = ?
                """,
                    (key,),
                )

                row = cursor.fetchone()
                if not row:
                    return False

                created_at, ttl = row

                # Check if expired
                if ttl and (time.time() - created_at) > ttl:
                    return False

                return True

        except Exception as e:
            logger.error(f"Error checking persistent cache key existence {key}: {e}")
            return False

    async def clear(self) -> bool:
        """Clear all cache entries."""
        try:
            # Remove all files
            for file_path in self.data_dir.iterdir():
                if file_path.is_file():
                    try:
                        await aiofiles.os.remove(file_path)
                    except Exception as e:
                        logger.warning(f"Error removing cache file {file_path}: {e}")

            # Clear database
            async with self._db_lock:
                if self._db_connection:
                    self._db_connection.execute("DELETE FROM cache_entries")

            self._event_manager.emit("cache_clear", level="L3")
            return True

        except Exception as e:
            self._metrics.record_error()
            logger.error(f"Error clearing persistent cache: {e}")
            return False

    async def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        stats = self._metrics.get_stats()

        try:
            async with self._db_lock:
                if self._db_connection:
                    # Get total size and count
                    cursor = self._db_connection.execute("""
                        SELECT COUNT(*), SUM(size_bytes) FROM cache_entries
                    """)
                    row = cursor.fetchone()
                    if row:
                        stats.entry_count = row[0] or 0
                        stats.total_size_bytes = row[1] or 0

        except Exception as e:
            logger.warning(f"Error getting persistent cache stats: {e}")

        return stats

    async def invalidate_by_tags(self, tags: List[str]) -> int:
        """Invalidate cache entries by tags."""
        try:
            invalidated_count = 0

            async with self._db_lock:
                if not self._db_connection:
                    return 0

                # Find entries with matching tags
                for tag in tags:
                    cursor = self._db_connection.execute(
                        """
                        SELECT key, file_path FROM cache_entries
                        WHERE tags LIKE ?
                    """,
                        (f'%"{tag}"%',),
                    )

                    entries = cursor.fetchall()
                    for key, file_path in entries:
                        await self._remove_entry(key, file_path)
                        invalidated_count += 1

            self._event_manager.emit(
                "cache_invalidate_tags", tags=tags, level="L3", count=invalidated_count
            )
            return invalidated_count

        except Exception as e:
            self._metrics.record_error()
            logger.error(f"Error invalidating persistent cache by tags {tags}: {e}")
            return 0

    async def shutdown(self) -> None:
        """Shutdown persistent cache and cleanup resources."""
        try:
            self._shutdown_event.set()

            # Cancel background tasks
            if self._sync_task:
                self._sync_task.cancel()
                try:
                    await self._sync_task
                except asyncio.CancelledError:
                    pass

            if self._cleanup_task:
                self._cleanup_task.cancel()
                try:
                    await self._cleanup_task
                except asyncio.CancelledError:
                    pass

            # Final database sync
            await self._sync_database()

            # Close database connection
            async with self._db_lock:
                if self._db_connection:
                    self._db_connection.close()
                    self._db_connection = None

            logger.info("Persistent cache shutdown complete")

        except Exception as e:
            logger.error(f"Error during persistent cache shutdown: {e}")
