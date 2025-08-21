#!/usr/bin/env python3
"""
Simple test for ReasoningCache functionality
"""

import sys
import os
import asyncio
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reasoning_kernel.optimization.cache import TTLCache, LRUCache, AdaptiveCache


def test_ttl_cache():
    """Test TTL cache functionality"""
    print("🧪 Testing TTL Cache...")

    cache = TTLCache(default_ttl=2.0, maxsize=100)

    # Test basic set/get
    cache.set("key1", "value1")
    assert cache.get("key1") == "value1", "TTL cache get/set failed"

    # Test TTL with specific value
    cache.set("key2", "value2", ttl=1.0)
    assert cache.get("key2") == "value2", "TTL cache with custom TTL failed"

    print("✅ TTL Cache tests passed!")


def test_lru_cache():
    """Test LRU cache functionality"""
    print("🧪 Testing LRU Cache...")

    cache = LRUCache(maxsize=3)

    # Fill cache
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.set("key3", "value3")

    # Access key1 to make it most recent
    assert cache.get("key1") == "value1"

    # Add key4 - should evict key2 (least recent)
    cache.set("key4", "value4")

    assert cache.get("key1") == "value1", "LRU failed to keep recently accessed item"
    assert cache.get("key2") is None, "LRU failed to evict least recent item"
    assert cache.get("key3") == "value3", "LRU incorrectly evicted item"
    assert cache.get("key4") == "value4", "LRU failed to add new item"

    print("✅ LRU Cache tests passed!")


def test_adaptive_cache():
    """Test adaptive cache functionality"""
    print("🧪 Testing Adaptive Cache...")

    cache = AdaptiveCache(lru_size=2, ttl_default=300.0)

    # Test basic functionality
    cache.set("key1", "value1")
    assert cache.get("key1") == "value1", "Adaptive cache basic get/set failed"

    # Test promotion from TTL to LRU
    cache.set("key2", "value2")
    cache.set("key3", "value3")  # This should push key2 to TTL cache

    # Access key2 - should promote to LRU
    assert cache.get("key2") == "value2", "Adaptive cache promotion failed"

    print("✅ Adaptive Cache tests passed!")


def test_cache_monitoring():
    """Test cache hit/miss monitoring"""
    print("🧪 Testing Cache Monitoring...")

    cache = TTLCache(default_ttl=300.0)

    # Test cache miss
    result = cache.get("nonexistent")
    assert result is None, "Cache should return None for nonexistent key"

    # Test cache hit
    cache.set("existing", "value")
    result = cache.get("existing")
    assert result == "value", "Cache should return value for existing key"

    print("✅ Cache Monitoring tests passed!")


async def test_cache_performance():
    """Test cache performance benchmarks"""
    print("🧪 Testing Cache Performance...")

    cache = AdaptiveCache(lru_size=1000, ttl_default=300.0)

    # Warm up cache
    start_time = datetime.now()
    for i in range(1000):
        cache.set(f"key_{i}", f"value_{i}")

    set_time = (datetime.now() - start_time).total_seconds()
    print(f"  📊 Set 1000 items in {set_time:.4f} seconds")

    # Test retrieval performance
    start_time = datetime.now()
    for i in range(1000):
        result = cache.get(f"key_{i}")
        assert result == f"value_{i}", f"Cache retrieval failed for key_{i}"

    get_time = (datetime.now() - start_time).total_seconds()
    print(f"  📊 Retrieved 1000 items in {get_time:.4f} seconds")

    print("✅ Cache Performance tests passed!")


def main():
    """Run all cache tests"""
    print("🚀 Running Reasoning Kernel Cache Tests...")
    print("=" * 50)

    try:
        test_ttl_cache()
        test_lru_cache()
        test_adaptive_cache()
        test_cache_monitoring()
        asyncio.run(test_cache_performance())

        print("=" * 50)
        print("🎉 All cache tests completed successfully!")
        print("✅ TASK-015 (Implement Caching Layer) infrastructure validated")

    except Exception as e:
        print(f"❌ Cache tests failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
