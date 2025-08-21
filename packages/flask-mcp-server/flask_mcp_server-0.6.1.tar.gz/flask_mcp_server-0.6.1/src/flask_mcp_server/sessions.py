from __future__ import annotations
import time
import threading
import logging
from typing import Dict, Tuple, Optional, Any

logger = logging.getLogger(__name__)


class MemorySessionStore:
    """
    Thread-safe in-memory session store with automatic cleanup.

    Features:
    - Automatic expiration of sessions based on TTL
    - Periodic cleanup to prevent memory leaks
    - Thread-safe operations
    """

    def __init__(self, cleanup_interval: int = 300):
        """
        Initialize the session store.

        Args:
            cleanup_interval: Seconds between automatic cleanup runs
        """
        self.store: Dict[str, Tuple[Dict[str, Any], float]] = {}  # sid -> (data, expiry)
        self.cleanup_interval = cleanup_interval
        self._lock = threading.RLock()
        self._last_cleanup = time.time()

        logger.debug(f"Initialized MemorySessionStore with cleanup_interval={cleanup_interval}")

    def get(self, sid: str) -> Optional[Dict[str, Any]]:
        """
        Get session data by session ID.

        Args:
            sid: Session ID

        Returns:
            Session data or None if not found/expired
        """
        with self._lock:
            self._maybe_cleanup()

            record = self.store.get(sid)
            if not record:
                return None

            data, expiry = record
            current_time = time.time()

            # Check if expired
            if expiry < current_time:
                del self.store[sid]
                logger.debug(f"Session expired: {sid}")
                return None

            return data.copy()  # Return a copy to prevent external modification

    def set(self, sid: str, data: Dict[str, Any], ttl: int = 3600) -> None:
        """
        Set session data with TTL.

        Args:
            sid: Session ID
            data: Session data
            ttl: Time to live in seconds
        """
        with self._lock:
            expiry = time.time() + ttl
            self.store[sid] = (data.copy(), expiry)  # Store a copy
            self._maybe_cleanup()

            logger.debug(f"Session set: {sid} (TTL: {ttl}s)")

    def delete(self, sid: str) -> bool:
        """
        Delete a session.

        Args:
            sid: Session ID to delete

        Returns:
            True if session was deleted, False if not found
        """
        with self._lock:
            if sid in self.store:
                del self.store[sid]
                logger.debug(f"Session deleted: {sid}")
                return True
            return False

    def clear(self) -> None:
        """Clear all sessions."""
        with self._lock:
            self.store.clear()
            logger.debug("All sessions cleared")

    def size(self) -> int:
        """Get the current number of sessions."""
        with self._lock:
            return len(self.store)

    def _maybe_cleanup(self) -> None:
        """Run cleanup if enough time has passed since last cleanup."""
        current_time = time.time()
        if current_time - self._last_cleanup > self.cleanup_interval:
            self._cleanup_expired()
            self._last_cleanup = current_time

    def _cleanup_expired(self) -> None:
        """Remove all expired sessions."""
        current_time = time.time()
        expired_sids = []

        for sid, (_, expiry) in self.store.items():
            if expiry < current_time:
                expired_sids.append(sid)

        for sid in expired_sids:
            del self.store[sid]

        if expired_sids:
            logger.debug(f"Cleaned up {len(expired_sids)} expired sessions")

    def get_stats(self) -> Dict[str, Any]:
        """Get session store statistics."""
        with self._lock:
            current_time = time.time()
            expired_count = sum(
                1 for _, expiry in self.store.values()
                if expiry < current_time
            )

            return {
                "active_sessions": len(self.store),
                "expired_sessions": expired_count,
                "last_cleanup": self._last_cleanup,
                "cleanup_interval": self.cleanup_interval
            }


def make_session_store(cleanup_interval: int = 300) -> MemorySessionStore:
    """
    Create a new MemorySessionStore instance.

    Args:
        cleanup_interval: Seconds between automatic cleanup runs

    Returns:
        New MemorySessionStore instance

    Note:
        This is a placeholder for future Redis-backed sessions.
        TODO: Add Redis backend support in future versions.
    """
    return MemorySessionStore(cleanup_interval=cleanup_interval)
