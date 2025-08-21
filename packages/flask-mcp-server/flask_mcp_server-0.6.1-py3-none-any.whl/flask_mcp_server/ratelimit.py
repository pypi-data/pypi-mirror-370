from __future__ import annotations
import time
import threading
import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class MemoryLimiter:
    """
    Thread-safe in-memory rate limiter with automatic cleanup.

    Uses a sliding window approach with automatic cleanup of old entries
    to prevent memory leaks.
    """

    def __init__(self, cleanup_interval: int = 300):
        """
        Initialize the rate limiter.

        Args:
            cleanup_interval: Seconds between automatic cleanup runs
        """
        self.store: Dict[str, Tuple[int, int]] = {}  # key -> (bucket, count)
        self.cleanup_interval = cleanup_interval
        self._lock = threading.RLock()
        self._last_cleanup = time.time()

        logger.debug(f"Initialized MemoryLimiter with cleanup_interval={cleanup_interval}")

    def allow(self, key: str, limit: int, window: int) -> Tuple[bool, int]:
        """
        Check if a request should be allowed based on rate limits.

        Args:
            key: Unique identifier for the rate limit (e.g., IP address, API key)
            limit: Maximum number of requests allowed in the window
            window: Time window in seconds

        Returns:
            Tuple of (allowed, remaining_requests)
        """
        # Validate inputs
        if limit <= 0:
            logger.warning(f"Invalid rate limit: {limit} (must be > 0)")
            return False, 0

        if window <= 0:
            logger.warning(f"Invalid time window: {window} (must be > 0)")
            return False, 0

        with self._lock:
            self._maybe_cleanup(window)

            now = int(time.time())
            bucket = now // window

            record = self.store.get(key)

            if not record or record[0] != bucket:
                # New bucket or first request
                self.store[key] = (bucket, 1)
                remaining = limit - 1
                logger.debug(f"Rate limit: {key} - new bucket, remaining: {remaining}")
                return True, remaining

            # Existing bucket
            current_count = record[1] + 1
            self.store[key] = (bucket, current_count)

            allowed = current_count <= limit
            remaining = max(0, limit - current_count)

            if not allowed:
                logger.warning(f"Rate limit exceeded: {key} - {current_count}/{limit}")
            else:
                logger.debug(f"Rate limit: {key} - {current_count}/{limit}, remaining: {remaining}")

            return allowed, remaining

    def reset(self, key: str) -> None:
        """
        Reset rate limit for a specific key.

        Args:
            key: Rate limit key to reset
        """
        with self._lock:
            if key in self.store:
                del self.store[key]
                logger.debug(f"Rate limit reset: {key}")

    def clear(self) -> None:
        """Clear all rate limit data."""
        with self._lock:
            self.store.clear()
            logger.debug("Rate limiter cleared")

    def size(self) -> int:
        """Get the current number of tracked keys."""
        with self._lock:
            return len(self.store)

    def _maybe_cleanup(self, current_window: int) -> None:
        """Run cleanup if enough time has passed since last cleanup."""
        current_time = time.time()
        if current_time - self._last_cleanup > self.cleanup_interval:
            self._cleanup_old_buckets(current_window)
            self._last_cleanup = current_time

    def _cleanup_old_buckets(self, current_window: int) -> None:
        """Remove entries from old time buckets."""
        current_time = int(time.time())
        current_bucket = current_time // current_window

        # Remove entries older than 2 windows to be safe
        cutoff_bucket = current_bucket - 2

        old_keys = []
        for key, (bucket, _) in self.store.items():
            if bucket < cutoff_bucket:
                old_keys.append(key)

        for key in old_keys:
            del self.store[key]

        if old_keys:
            logger.debug(f"Cleaned up {len(old_keys)} old rate limit entries")

    def get_stats(self) -> Dict[str, any]:
        """Get rate limiter statistics."""
        with self._lock:
            return {
                "tracked_keys": len(self.store),
                "last_cleanup": self._last_cleanup,
                "cleanup_interval": self.cleanup_interval
            }


def make_limiter(cleanup_interval: int = 300) -> MemoryLimiter:
    """
    Create a new MemoryLimiter instance.

    Args:
        cleanup_interval: Seconds between automatic cleanup runs

    Returns:
        New MemoryLimiter instance
    """
    return MemoryLimiter(cleanup_interval=cleanup_interval)
