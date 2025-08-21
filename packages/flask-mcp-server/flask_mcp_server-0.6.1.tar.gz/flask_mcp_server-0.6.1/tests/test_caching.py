"""
Tests for caching module.

This module tests the MemoryTTLCache implementation,
including TTL functionality, cleanup mechanisms, and LRU eviction.
"""

import pytest
import time
import threading
from flask_mcp_server.caching import MemoryTTLCache, make_cache


class TestMemoryTTLCache:
    """Test MemoryTTLCache class."""
    
    def test_cache_creation(self):
        """Test cache creation with default parameters."""
        cache = MemoryTTLCache()
        assert cache.max_size == 10000
        assert cache.cleanup_interval == 300
        assert cache.size() == 0
    
    def test_cache_creation_with_params(self):
        """Test cache creation with custom parameters."""
        cache = MemoryTTLCache(max_size=100, cleanup_interval=60)
        assert cache.max_size == 100
        assert cache.cleanup_interval == 60
    
    def test_basic_set_get(self, cache):
        """Test basic set and get operations."""
        cache.set("key1", "value1", 60)
        assert cache.get("key1") == "value1"
        assert cache.size() == 1
    
    def test_get_nonexistent_key(self, cache):
        """Test getting non-existent key."""
        assert cache.get("nonexistent") is None
    
    def test_ttl_expiration(self, cache):
        """Test TTL expiration."""
        cache.set("key1", "value1", 1)  # 1 second TTL
        assert cache.get("key1") == "value1"
        
        time.sleep(1.1)  # Wait for expiration
        assert cache.get("key1") is None
        assert cache.size() == 0
    
    def test_zero_ttl(self, cache):
        """Test zero TTL (no expiration)."""
        cache.set("key1", "value1", 0)
        assert cache.get("key1") == "value1"
        
        # Should still be there after some time
        time.sleep(0.1)
        assert cache.get("key1") == "value1"
    
    def test_update_existing_key(self, cache):
        """Test updating existing key."""
        cache.set("key1", "value1", 60)
        cache.set("key1", "value2", 60)
        assert cache.get("key1") == "value2"
        assert cache.size() == 1
    
    def test_delete_key(self, cache):
        """Test deleting keys."""
        cache.set("key1", "value1", 60)
        assert cache.delete("key1") is True
        assert cache.get("key1") is None
        assert cache.size() == 0
        
        # Deleting non-existent key
        assert cache.delete("nonexistent") is False
    
    def test_clear_cache(self, cache):
        """Test clearing all cache entries."""
        cache.set("key1", "value1", 60)
        cache.set("key2", "value2", 60)
        assert cache.size() == 2
        
        cache.clear()
        assert cache.size() == 0
        assert cache.get("key1") is None
        assert cache.get("key2") is None
    
    def test_lru_eviction(self):
        """Test LRU eviction when max size is reached."""
        cache = MemoryTTLCache(max_size=3, cleanup_interval=1)
        
        # Fill cache to max size
        cache.set("key1", "value1", 60)
        cache.set("key2", "value2", 60)
        cache.set("key3", "value3", 60)
        assert cache.size() == 3
        
        # Access key1 to make it more recently used
        cache.get("key1")
        
        # Add another key, should evict key2 (least recently used)
        cache.set("key4", "value4", 60)
        assert cache.size() == 3
        assert cache.get("key1") == "value1"  # Should still be there
        assert cache.get("key2") is None      # Should be evicted
        assert cache.get("key3") == "value3"  # Should still be there
        assert cache.get("key4") == "value4"  # Should be there
    
    def test_cleanup_expired_entries(self):
        """Test automatic cleanup of expired entries."""
        cache = MemoryTTLCache(max_size=100, cleanup_interval=1)
        
        # Add entries with different TTLs
        cache.set("key1", "value1", 1)   # Will expire
        cache.set("key2", "value2", 60)  # Won't expire
        
        # Force cleanup by waiting and accessing
        time.sleep(1.1)
        cache._cleanup_expired()
        
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
    
    def test_thread_safety(self):
        """Test thread safety of cache operations."""
        cache = MemoryTTLCache(max_size=1000, cleanup_interval=1)
        results = []
        
        def worker(thread_id):
            for i in range(100):
                key = f"thread_{thread_id}_key_{i}"
                value = f"thread_{thread_id}_value_{i}"
                cache.set(key, value, 60)
                retrieved = cache.get(key)
                results.append(retrieved == value)
        
        # Start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All operations should have succeeded
        assert all(results)
        assert len(results) == 500  # 5 threads * 100 operations
    
    def test_get_stats(self, cache):
        """Test cache statistics."""
        cache.set("key1", "value1", 1)   # Will expire
        cache.set("key2", "value2", 60)  # Won't expire
        
        stats = cache.get_stats()
        assert stats["size"] == 2
        assert stats["max_size"] == cache.max_size
        assert stats["cleanup_interval"] == cache.cleanup_interval
        assert "last_cleanup" in stats
        
        # Wait for expiration and check expired count
        time.sleep(1.1)
        stats = cache.get_stats()
        assert stats["expired_entries"] == 1
    
    def test_maybe_cleanup_timing(self):
        """Test that cleanup only runs when interval has passed."""
        cache = MemoryTTLCache(max_size=100, cleanup_interval=10)
        
        # Set last cleanup to now
        cache._last_cleanup = time.time()
        
        # Add expired entry
        cache.set("key1", "value1", 1)
        time.sleep(1.1)
        
        # Access cache (should not trigger cleanup due to interval)
        cache.get("key2")
        
        # Expired entry should still be in store (not cleaned up)
        assert "key1" in cache.store
        
        # Force cleanup by setting old last_cleanup time
        cache._last_cleanup = time.time() - 20
        cache.get("key2")  # Should trigger cleanup
        
        # Now expired entry should be gone
        assert "key1" not in cache.store


class TestMakeCache:
    """Test make_cache function."""
    
    def test_make_cache_default(self):
        """Test make_cache with default parameters."""
        cache = make_cache()
        assert isinstance(cache, MemoryTTLCache)
        assert cache.max_size == 10000
        assert cache.cleanup_interval == 300
    
    def test_make_cache_custom(self):
        """Test make_cache with custom parameters."""
        cache = make_cache(max_size=500, cleanup_interval=120)
        assert isinstance(cache, MemoryTTLCache)
        assert cache.max_size == 500
        assert cache.cleanup_interval == 120


class TestCacheEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_large_values(self, cache):
        """Test caching large values."""
        large_value = "x" * 10000  # 10KB string
        cache.set("large_key", large_value, 60)
        assert cache.get("large_key") == large_value
    
    def test_none_values(self, cache):
        """Test caching None values."""
        cache.set("none_key", None, 60)
        assert cache.get("none_key") is None
        # Should be able to distinguish between None value and missing key
        assert "none_key" in cache.store
    
    def test_complex_objects(self, cache):
        """Test caching complex objects."""
        complex_obj = {
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
            "tuple": (1, 2, 3)
        }
        cache.set("complex_key", complex_obj, 60)
        retrieved = cache.get("complex_key")
        assert retrieved == complex_obj
        assert retrieved is complex_obj  # Should be same object reference
    
    def test_unicode_keys_and_values(self, cache):
        """Test Unicode keys and values."""
        unicode_key = "ключ_测试_🔑"
        unicode_value = "значение_测试_💎"
        cache.set(unicode_key, unicode_value, 60)
        assert cache.get(unicode_key) == unicode_value
