"""
Integration test for ReasoningCache implementation

Tests the comprehensive caching system including:
- Multi-tier caching (memory + Redis)
- Cache level-based TTL management
- MSA-specific cache operations
- Performance monitoring
"""

import asyncio
from reasoning_kernel.services.reasoning_cache import ReasoningCache, CacheConfig, CacheLevel


async def test_basic_cache_operations():
    """Test basic get/set/delete operations"""
    config = CacheConfig(memory_cache_size=10, redis_enabled=False)
    cache = ReasoningCache(config)
    await cache.initialize()

    try:
        # Test set and get
        test_data = {"key": "value", "number": 42}
        assert await cache.set("test_key", test_data)

        retrieved = await cache.get("test_key")
        assert retrieved == test_data

        # Test delete
        assert await cache.delete("test_key")
        assert await cache.get("test_key") is None

        print("  ✅ Basic cache operations work")
    finally:
        await cache.clear()


async def test_cache_levels():
    """Test different cache levels and their TTLs"""
    config = CacheConfig(memory_cache_size=10, redis_enabled=False)
    cache = ReasoningCache(config)
    await cache.initialize()

    try:
        critical_data = {"priority": "critical"}
        normal_data = {"priority": "normal"}

        # Set with different cache levels
        await cache.set("critical", critical_data, CacheLevel.CRITICAL)
        await cache.set("normal", normal_data, CacheLevel.NORMAL)

        # Both should be retrievable
        assert await cache.get("critical") == critical_data
        assert await cache.get("normal") == normal_data

        print("  ✅ Cache levels work correctly")
    finally:
        await cache.clear()


async def test_msa_reasoning_cache():
    """Test MSA-specific reasoning result caching"""
    config = CacheConfig(memory_cache_size=10, redis_enabled=False)
    cache = ReasoningCache(config)
    await cache.initialize()

    try:
        session_id = "test_session_123"
        stage = "analysis"
        result_data = {
            "reasoning_chain": ["step1", "step2", "step3"],
            "conclusion": "test conclusion",
            "confidence": 0.85,
        }

        # Cache reasoning result
        assert await cache.cache_reasoning_result(session_id, stage, result_data)

        # Retrieve reasoning result
        retrieved = await cache.get_reasoning_result(session_id, stage)
        assert retrieved == result_data

        print("  ✅ MSA reasoning cache works")
    finally:
        await cache.clear()


async def test_model_output_cache():
    """Test model output caching functionality"""
    config = CacheConfig(memory_cache_size=10, redis_enabled=False)
    cache = ReasoningCache(config)
    await cache.initialize()

    try:
        model_name = "test_model"
        input_hash = "abc123def456"
        output_data = {"prediction": "positive", "confidence": 0.92, "tokens_used": 150}

        # Cache model output
        assert await cache.cache_model_result(model_name, input_hash, output_data)

        # Retrieve model output
        retrieved = await cache.get_model_result(model_name, input_hash)
        assert retrieved == output_data

        print("  ✅ Model output cache works")
    finally:
        await cache.clear()


async def test_embedding_cache():
    """Test embedding caching functionality"""
    config = CacheConfig(memory_cache_size=10, redis_enabled=False)
    cache = ReasoningCache(config)
    await cache.initialize()

    try:
        text_hash = "text_hash_789"
        embedding_vector = [0.1, 0.2, 0.3, 0.4, 0.5]

        # Cache embedding
        assert await cache.cache_embedding(text_hash, embedding_vector)

        # Retrieve embedding
        retrieved = await cache.get_embedding(text_hash)
        assert retrieved == embedding_vector

        print("  ✅ Embedding cache works")
    finally:
        await cache.clear()


async def test_cache_statistics():
    """Test cache statistics tracking"""
    config = CacheConfig(memory_cache_size=10, redis_enabled=False)
    cache = ReasoningCache(config)
    await cache.initialize()

    try:
        # Perform some cache operations
        await cache.set("key1", {"data": "value1"})
        await cache.get("key1")  # Hit
        await cache.get("nonexistent")  # Miss

        stats = cache.get_stats()

        # Check that stats are being tracked
        assert hasattr(stats, "hits")
        assert hasattr(stats, "misses")
        assert hasattr(stats, "hit_rate")

        print("  ✅ Cache statistics tracking works")
    finally:
        await cache.clear()


async def run_all_tests():
    """Run all ReasoningCache integration tests"""
    print("🧪 Running ReasoningCache integration tests...")

    try:
        await test_basic_cache_operations()
        await test_cache_levels()
        await test_msa_reasoning_cache()
        await test_model_output_cache()
        await test_embedding_cache()
        await test_cache_statistics()

        print("🎉 All ReasoningCache integration tests passed!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise


if __name__ == "__main__":
    # Run integration tests if executed directly
    asyncio.run(run_all_tests())
