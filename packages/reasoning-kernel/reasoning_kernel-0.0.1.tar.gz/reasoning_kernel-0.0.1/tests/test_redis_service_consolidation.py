"""
Integration test for Redis service consolidation

Tests that the UnifiedRedisService successfully replaces the three separate
Redis implementations with equivalent functionality and performance improvements.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from reasoning_kernel.services.unified_redis_service import (
    UnifiedRedisService,
    RedisConnectionConfig,
    create_unified_redis_service,
)


class TestRedisServiceConsolidation:
    """Integration test for Redis service consolidation"""

    async def test_consolidation_basic_functionality(self):
        """Test that unified service provides all essential methods"""
        service = UnifiedRedisService()

        # Test that all key methods from the three original services exist
        essential_methods = [
            # From RedisMemoryService
            "store_reasoning_chain",
            "get_reasoning_chain",
            "store_knowledge",
            "retrieve_knowledge_by_type",
            "cache_model_result",
            "get_cached_model_result",
            "create_session",
            "get_session",
            # From RedisVectorService
            "initialize_vector_store",
            "similarity_search",
            # From ProductionRedisManager
            "store_world_model",
            "retrieve_world_model",
            "get_performance_metrics",
            "batch_store",
            "cleanup_expired_keys",
            # Connection management
            "connect",
            "disconnect",
            "health_check",
        ]

        for method_name in essential_methods:
            assert hasattr(service, method_name), f"Missing method: {method_name}"
            assert callable(getattr(service, method_name)), f"Not callable: {method_name}"

    async def test_connection_pooling_configuration(self):
        """Test that connection pooling is properly configured"""
        config = RedisConnectionConfig(host="test-host", port=6380, max_connections=100, timeout=60.0)

        service = UnifiedRedisService(config=config)

        assert service.config.host == "test-host"
        assert service.config.port == 6380
        assert service.config.max_connections == 100
        assert service.config.timeout == 60.0

    @patch("reasoning_kernel.services.unified_redis_service.aioredis")
    async def test_connection_management(self, mock_aioredis):
        """Test connection management with pooling"""
        mock_pool = AsyncMock()
        mock_client = AsyncMock()
        mock_client.ping.return_value = True

        mock_aioredis.ConnectionPool.return_value = mock_pool
        mock_aioredis.Redis.return_value = mock_client

        service = UnifiedRedisService()

        # Test connection
        result = await service.connect()
        assert result is True
        assert service._is_connected
        assert service.redis_client == mock_client

        # Test disconnection
        await service.disconnect()
        assert not service._is_connected
        assert service.redis_client is None

        mock_client.aclose.assert_called_once()
        mock_pool.aclose.assert_called_once()

    async def test_monitoring_capabilities(self):
        """Test comprehensive monitoring features"""
        service = UnifiedRedisService(enable_monitoring=True)

        # Test monitoring is enabled
        assert service.enable_monitoring
        assert service._operation_count == 0
        assert service._error_count == 0
        assert service._cache_hits == 0
        assert service._cache_misses == 0

        # Test increment methods
        service._increment_operation_count("test")
        assert service._operation_count == 1

        service._increment_error_count()
        assert service._error_count == 1

        # Test performance metrics
        metrics = await service.get_performance_metrics()
        assert "operations" in metrics
        assert "cache" in metrics
        assert "connection" in metrics
        assert "timestamp" in metrics

    async def test_error_handling_consistency(self):
        """Test consistent error handling across operations"""
        service = UnifiedRedisService()

        # Test operations without connection return appropriate defaults
        assert await service.store_reasoning_chain("test", {}) is False
        assert await service.get_reasoning_chain("test") is None
        assert await service.store_knowledge("test", {}) is False
        assert await service.retrieve_knowledge_by_type("test") == []
        assert await service.cache_model_result("model", "hash", {}) is False
        assert await service.get_cached_model_result("model", "hash") is None
        assert await service.create_session("test", {}) is False
        assert await service.get_session("test") is None
        assert await service.store_world_model("scenario", MagicMock()) is False
        assert await service.retrieve_world_model("scenario") is None
        assert await service.similarity_search("collection", "query") == []
        assert await service.cleanup_expired_keys() == 0
        assert await service.batch_store([]) == {}

    async def test_factory_functions(self):
        """Test factory functions for service creation"""
        with patch("reasoning_kernel.services.unified_redis_service.UnifiedRedisService") as mock_class:
            mock_service = AsyncMock()
            mock_class.return_value = mock_service

            # Test production service creation
            await create_unified_redis_service(redis_url="redis://test:6379", environment="production")

            mock_class.assert_called_once()
            mock_service.connect.assert_called_once()

    async def test_schema_integration(self):
        """Test that schema integration works for key generation"""
        service = UnifiedRedisService()

        # Test that schema is available
        assert service.schema is not None
        assert hasattr(service.schema, "config")

        # Test key generation utilities
        scenario_hash = service._generate_scenario_hash("test scenario")
        assert isinstance(scenario_hash, str)
        assert len(scenario_hash) == 16

        cache_key = service.generate_cache_key("test", "arg1", "arg2")
        assert isinstance(cache_key, str)
        assert "test" in cache_key

    async def test_ttl_management(self):
        """Test TTL management for different abstraction levels"""
        service = UnifiedRedisService()

        # Test TTL calculation
        ttl_omega1 = service._get_ttl_for_abstraction_level("omega1")
        ttl_omega2 = service._get_ttl_for_abstraction_level("omega2")
        ttl_omega3 = service._get_ttl_for_abstraction_level("omega3")
        ttl_default = service._get_ttl_for_abstraction_level("unknown")

        assert ttl_omega1 > ttl_omega2
        assert ttl_omega2 > ttl_omega3
        assert ttl_default == ttl_omega2  # Should be default

        # All should be positive integers
        assert all(isinstance(ttl, int) and ttl > 0 for ttl in [ttl_omega1, ttl_omega2, ttl_omega3, ttl_default])

    async def test_data_structures(self):
        """Test that all data structures are properly defined"""
        from reasoning_kernel.services.unified_redis_service import (
            ReasoningRecord,
            WorldModelRecord,
            ExplorationRecord,
            RedisConnectionConfig,
        )

        # Test ReasoningRecord
        reasoning_record = ReasoningRecord(
            pattern_type="test", question="What?", reasoning_steps="Step 1", final_answer="Answer", confidence_score=0.9
        )
        assert reasoning_record.pattern_type == "test"
        assert reasoning_record.confidence_score == 0.9
        assert reasoning_record.id  # Should be auto-generated

        # Test WorldModelRecord
        world_record = WorldModelRecord(model_type="PROBABILISTIC", state_data='{"test": "data"}', confidence=0.8)
        assert world_record.model_type == "PROBABILISTIC"
        assert world_record.confidence == 0.8

        # Test ExplorationRecord
        exploration_record = ExplorationRecord(
            exploration_type="hypothesis",
            hypothesis="Test hypothesis",
            evidence="Test evidence",
            conclusion="Test conclusion",
        )
        assert exploration_record.exploration_type == "hypothesis"

        # Test RedisConnectionConfig
        config = RedisConnectionConfig(host="test-host", port=6380, max_connections=20)
        assert config.host == "test-host"
        assert config.port == 6380
        assert config.max_connections == 20

    async def test_backwards_compatibility_interface(self):
        """Test that the interface is compatible with existing code"""
        service = UnifiedRedisService()

        # Test method signatures match expectations
        import inspect

        # Check key method signatures
        store_chain_sig = inspect.signature(service.store_reasoning_chain)
        assert "chain_id" in store_chain_sig.parameters
        assert "chain_data" in store_chain_sig.parameters
        assert "ttl" in store_chain_sig.parameters

        get_chain_sig = inspect.signature(service.get_reasoning_chain)
        assert "chain_id" in get_chain_sig.parameters

        store_knowledge_sig = inspect.signature(service.store_knowledge)
        assert "knowledge_id" in store_knowledge_sig.parameters
        assert "knowledge_data" in store_knowledge_sig.parameters
        assert "knowledge_type" in store_knowledge_sig.parameters

        health_check_sig = inspect.signature(service.health_check)
        assert len(health_check_sig.parameters) == 0  # No parameters for health check


class TestPerformanceFeatures:
    """Test performance optimization features"""

    async def test_batch_operations_interface(self):
        """Test batch operations interface"""
        service = UnifiedRedisService()

        # Test batch_store signature
        import inspect

        batch_sig = inspect.signature(service.batch_store)
        assert "items" in batch_sig.parameters

        # Test with empty list (should work without connection)
        result = await service.batch_store([])
        assert result == {}

    async def test_connection_pooling_config(self):
        """Test connection pooling configuration"""
        config = RedisConnectionConfig(max_connections=100, timeout=30.0, retry_attempts=5)

        service = UnifiedRedisService(config=config)
        assert service.config.max_connections == 100
        assert service.config.timeout == 30.0
        # retry_attempts is handled in the connection logic

    async def test_monitoring_performance_tracking(self):
        """Test performance monitoring capabilities"""
        service = UnifiedRedisService(enable_monitoring=True)

        # Test that monitoring attributes exist
        assert hasattr(service, "_operation_count")
        assert hasattr(service, "_error_count")
        assert hasattr(service, "_cache_hits")
        assert hasattr(service, "_cache_misses")

        # Test metrics collection
        metrics = await service.get_performance_metrics()

        required_keys = ["operations", "cache", "connection", "timestamp"]
        assert all(key in metrics for key in required_keys)

        # Test operation metrics
        ops_metrics = metrics["operations"]
        assert "total_operations" in ops_metrics
        assert "total_errors" in ops_metrics
        assert "error_rate" in ops_metrics

        # Test cache metrics
        cache_metrics = metrics["cache"]
        assert "cache_hits" in cache_metrics
        assert "cache_misses" in cache_metrics
        assert "hit_ratio" in cache_metrics


if __name__ == "__main__":
    pytest.main([__file__])
