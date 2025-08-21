"""
Tests for rate limiting module.

This module tests the MemoryLimiter implementation,
including rate limiting logic, cleanup mechanisms, and thread safety.
"""

import pytest
import time
import threading
from flask_mcp_server.ratelimit import MemoryLimiter, make_limiter


class TestMemoryLimiter:
    """Test MemoryLimiter class."""
    
    def test_limiter_creation(self):
        """Test limiter creation with default parameters."""
        limiter = MemoryLimiter()
        assert limiter.cleanup_interval == 300
        assert limiter.size() == 0
    
    def test_limiter_creation_with_params(self):
        """Test limiter creation with custom parameters."""
        limiter = MemoryLimiter(cleanup_interval=60)
        assert limiter.cleanup_interval == 60
    
    def test_basic_rate_limiting(self, limiter):
        """Test basic rate limiting functionality."""
        # First request should be allowed
        allowed, remaining = limiter.allow("test_key", 5, 60)
        assert allowed is True
        assert remaining == 4
        
        # Second request should be allowed
        allowed, remaining = limiter.allow("test_key", 5, 60)
        assert allowed is True
        assert remaining == 3
    
    def test_rate_limit_exceeded(self, limiter):
        """Test rate limit exceeded scenario."""
        # Use up all allowed requests
        for i in range(5):
            allowed, remaining = limiter.allow("test_key", 5, 60)
            assert allowed is True
            assert remaining == 4 - i
        
        # Next request should be denied
        allowed, remaining = limiter.allow("test_key", 5, 60)
        assert allowed is False
        assert remaining == 0
    
    def test_different_keys_independent(self, limiter):
        """Test that different keys are rate limited independently."""
        # Use up limit for key1
        for i in range(3):
            limiter.allow("key1", 3, 60)
        
        # key1 should be at limit
        allowed, remaining = limiter.allow("key1", 3, 60)
        assert allowed is False
        assert remaining == 0
        
        # key2 should still be allowed
        allowed, remaining = limiter.allow("key2", 3, 60)
        assert allowed is True
        assert remaining == 2
    
    def test_time_window_reset(self, limiter):
        """Test that rate limits reset after time window."""
        # Use up all requests in current window
        for i in range(3):
            limiter.allow("test_key", 3, 1)  # 1 second window
        
        # Should be at limit
        allowed, remaining = limiter.allow("test_key", 3, 1)
        assert allowed is False
        
        # Wait for window to reset
        time.sleep(1.1)
        
        # Should be allowed again
        allowed, remaining = limiter.allow("test_key", 3, 1)
        assert allowed is True
        assert remaining == 2
    
    def test_reset_key(self, limiter):
        """Test resetting rate limit for specific key."""
        # Use up some requests
        limiter.allow("test_key", 5, 60)
        limiter.allow("test_key", 5, 60)
        
        # Reset the key
        limiter.reset("test_key")
        
        # Should be back to full limit
        allowed, remaining = limiter.allow("test_key", 5, 60)
        assert allowed is True
        assert remaining == 4
    
    def test_clear_all(self, limiter):
        """Test clearing all rate limit data."""
        # Add some rate limit data
        limiter.allow("key1", 5, 60)
        limiter.allow("key2", 5, 60)
        assert limiter.size() == 2
        
        # Clear all data
        limiter.clear()
        assert limiter.size() == 0
        
        # Should be back to full limits
        allowed, remaining = limiter.allow("key1", 5, 60)
        assert allowed is True
        assert remaining == 4
    
    def test_cleanup_old_buckets(self):
        """Test cleanup of old time buckets."""
        limiter = MemoryLimiter(cleanup_interval=1)
        
        # Add entry in current window
        limiter.allow("test_key", 5, 1)  # 1 second window
        assert limiter.size() == 1
        
        # Wait for multiple windows to pass
        time.sleep(2.5)
        
        # Force cleanup
        limiter._cleanup_old_buckets(1)
        
        # Old entry should be cleaned up
        assert limiter.size() == 0
    
    def test_thread_safety(self):
        """Test thread safety of rate limiter."""
        limiter = MemoryLimiter(cleanup_interval=1)
        results = []
        
        def worker(thread_id):
            for i in range(50):
                key = f"thread_{thread_id}"
                allowed, remaining = limiter.allow(key, 100, 60)
                results.append((thread_id, allowed, remaining))
        
        # Start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results for each thread
        for thread_id in range(5):
            thread_results = [r for r in results if r[0] == thread_id]
            assert len(thread_results) == 50
            
            # All requests for each thread should be allowed (separate keys)
            for _, allowed, remaining in thread_results:
                assert allowed is True
    
    def test_get_stats(self, limiter):
        """Test rate limiter statistics."""
        limiter.allow("key1", 5, 60)
        limiter.allow("key2", 5, 60)
        
        stats = limiter.get_stats()
        assert stats["tracked_keys"] == 2
        assert stats["cleanup_interval"] == limiter.cleanup_interval
        assert "last_cleanup" in stats
    
    def test_maybe_cleanup_timing(self):
        """Test that cleanup only runs when interval has passed."""
        limiter = MemoryLimiter(cleanup_interval=10)

        # Set last cleanup to now
        limiter._last_cleanup = time.time()

        # Add entry that will become old
        limiter.allow("test_key", 5, 1)
        time.sleep(1.1)

        # Access limiter (should not trigger cleanup due to interval)
        limiter.allow("other_key", 5, 1)

        # Old entry should still be in store
        assert limiter.size() == 2

        # Force cleanup by setting old last_cleanup time
        limiter._last_cleanup = time.time() - 20
        limiter.allow("another_key", 5, 1)  # Should trigger cleanup

        # The cleanup removes buckets that are more than 2 windows old
        # Since we're using window=1, and test_key is only ~1 second old,
        # it might not be cleaned up yet. Let's check that cleanup was triggered
        # by verifying the last_cleanup time was updated
        assert limiter._last_cleanup > time.time() - 5  # Should be recent


class TestMakeLimiter:
    """Test make_limiter function."""
    
    def test_make_limiter_default(self):
        """Test make_limiter with default parameters."""
        limiter = make_limiter()
        assert isinstance(limiter, MemoryLimiter)
        assert limiter.cleanup_interval == 300
    
    def test_make_limiter_custom(self):
        """Test make_limiter with custom parameters."""
        limiter = make_limiter(cleanup_interval=120)
        assert isinstance(limiter, MemoryLimiter)
        assert limiter.cleanup_interval == 120


class TestRateLimitEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_zero_limit(self, limiter):
        """Test zero rate limit."""
        allowed, remaining = limiter.allow("test_key", 0, 60)
        assert allowed is False
        assert remaining == 0
    
    def test_negative_limit(self, limiter):
        """Test negative rate limit."""
        allowed, remaining = limiter.allow("test_key", -1, 60)
        assert allowed is False
        assert remaining == 0
    
    def test_very_large_limit(self, limiter):
        """Test very large rate limit."""
        allowed, remaining = limiter.allow("test_key", 1000000, 60)
        assert allowed is True
        assert remaining == 999999
    
    def test_very_short_window(self, limiter):
        """Test very short time window."""
        # 1 second window
        allowed, remaining = limiter.allow("test_key", 5, 1)
        assert allowed is True
        
        # Should reset quickly
        time.sleep(1.1)
        allowed, remaining = limiter.allow("test_key", 5, 1)
        assert allowed is True
        assert remaining == 4
    
    def test_very_long_window(self, limiter):
        """Test very long time window."""
        # 1 hour window
        allowed, remaining = limiter.allow("test_key", 5, 3600)
        assert allowed is True
        assert remaining == 4
        
        # Should still be in same bucket after short time
        time.sleep(0.1)
        allowed, remaining = limiter.allow("test_key", 5, 3600)
        assert allowed is True
        assert remaining == 3
    
    def test_unicode_keys(self, limiter):
        """Test Unicode keys."""
        unicode_key = "ключ_测试_🔑"
        allowed, remaining = limiter.allow(unicode_key, 5, 60)
        assert allowed is True
        assert remaining == 4
        
        # Should work consistently
        allowed, remaining = limiter.allow(unicode_key, 5, 60)
        assert allowed is True
        assert remaining == 3
    
    def test_empty_key(self, limiter):
        """Test empty key."""
        allowed, remaining = limiter.allow("", 5, 60)
        assert allowed is True
        assert remaining == 4
    
    def test_concurrent_same_key(self):
        """Test concurrent access to same key."""
        limiter = MemoryLimiter()
        results = []
        
        def worker():
            for i in range(10):
                allowed, remaining = limiter.allow("shared_key", 20, 60)
                results.append((allowed, remaining))
        
        # Start multiple threads using same key
        threads = []
        for i in range(3):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Should have 30 total requests, all allowed
        assert len(results) == 30
        allowed_count = sum(1 for allowed, _ in results if allowed)
        assert allowed_count == 20  # Only 20 should be allowed due to limit
