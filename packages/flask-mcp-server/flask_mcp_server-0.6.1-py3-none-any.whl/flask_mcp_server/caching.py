from __future__ import annotations
import time
import threading
import logging
from typing import Any, Optional, Dict, Tuple

logger = logging.getLogger(__name__)


class MemoryTTLCache:
    """
    Thread-safe in-memory cache with TTL (Time To Live) support and automatic cleanup.

    Features:
    - Automatic expiration of entries based on TTL
    - Periodic cleanup to prevent memory leaks
    - Thread-safe operations
    - LRU-style eviction when max size is reached
    """

    def __init__(self, max_size: int = 10000, cleanup_interval: int = 300):
        """
        Initialize the cache.

        Args:
            max_size: Maximum number of entries before LRU eviction
            cleanup_interval: Seconds between automatic cleanup runs
        """
        self.store: Dict[str, Tuple[Any, Optional[float], float]] = {}  # key -> (value, expiry, access_time)
        self.max_size = max_size
        self.cleanup_interval = cleanup_interval
        self._lock = threading.RLock()
        self._last_cleanup = time.time()

        logger.debug(f"Initialized MemoryTTLCache with max_size={max_size}, cleanup_interval={cleanup_interval}")

    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        with self._lock:
            self._maybe_cleanup()

            record = self.store.get(key)
            if not record:
                return None

            value, expiry, _ = record
            current_time = time.time()

            # Check if expired
            if expiry and expiry < current_time:
                del self.store[key]
                logger.debug(f"Cache key expired: {key}")
                return None

            # Update access time for LRU
            self.store[key] = (value, expiry, current_time)
            return value

    def set(self, key: str, value: Any, ttl: int) -> None:
        """
        Set a value in the cache with TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        """
        with self._lock:
            current_time = time.time()
            expiry = current_time + ttl if ttl > 0 else None

            self.store[key] = (value, expiry, current_time)

            # Enforce max size with LRU eviction
            if len(self.store) > self.max_size:
                self._evict_lru()

            self._maybe_cleanup()

            logger.debug(f"Cache set: {key} (TTL: {ttl}s)")

    def delete(self, key: str) -> bool:
        """
        Delete a key from the cache.

        Args:
            key: Cache key to delete

        Returns:
            True if key was deleted, False if not found
        """
        with self._lock:
            if key in self.store:
                del self.store[key]
                logger.debug(f"Cache key deleted: {key}")
                return True
            return False

    def clear(self) -> None:
        """Clear all entries from the cache."""
        with self._lock:
            self.store.clear()
            logger.debug("Cache cleared")

    def size(self) -> int:
        """Get the current number of entries in the cache."""
        with self._lock:
            return len(self.store)

    def _maybe_cleanup(self) -> None:
        """Run cleanup if enough time has passed since last cleanup."""
        current_time = time.time()
        if current_time - self._last_cleanup > self.cleanup_interval:
            self._cleanup_expired()
            self._last_cleanup = current_time

    def _cleanup_expired(self) -> None:
        """Remove all expired entries from the cache."""
        current_time = time.time()
        expired_keys = []

        for key, (_, expiry, _) in self.store.items():
            if expiry and expiry < current_time:
                expired_keys.append(key)

        for key in expired_keys:
            del self.store[key]

        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")

    def _evict_lru(self) -> None:
        """Evict the least recently used entry."""
        if not self.store:
            return

        # Find the entry with the oldest access time
        lru_key = min(self.store.keys(), key=lambda k: self.store[k][2])
        del self.store[lru_key]
        logger.debug(f"Evicted LRU cache entry: {lru_key}")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            current_time = time.time()
            expired_count = sum(
                1 for _, expiry, _ in self.store.values()
                if expiry and expiry < current_time
            )

            return {
                "size": len(self.store),
                "max_size": self.max_size,
                "expired_entries": expired_count,
                "last_cleanup": self._last_cleanup,
                "cleanup_interval": self.cleanup_interval
            }


def make_cache(max_size: int = 10000, cleanup_interval: int = 300) -> MemoryTTLCache:
    """
    Create a new MemoryTTLCache instance.

    Args:
        max_size: Maximum number of entries before LRU eviction
        cleanup_interval: Seconds between automatic cleanup runs

    Returns:
        New MemoryTTLCache instance
    """
    return MemoryTTLCache(max_size=max_size, cleanup_interval=cleanup_interval)
