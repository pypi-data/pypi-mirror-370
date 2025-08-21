"""
Tests for Redis-Integrated Hierarchical World Model Manager

Comprehensive test suite for the Redis-backed world model manager,
including persistence, caching, performance metrics, and integration
with exploration patterns and agent memory.

Author: AI Assistant & Reasoning Kernel Team
Date: 2025-08-15
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from reasoning_kernel.core.redis_world_model_manager import (
    RedisIntegratedWorldModelManager,
    create_redis_world_model_manager,
)
from reasoning_kernel.services.unified_redis_service import UnifiedRedisService as ProductionRedisManager
from reasoning_kernel.models.world_model import WorldModel, WorldModelLevel, ModelType, WorldModelEvidence
from reasoning_kernel.core.exploration_triggers import TriggerDetectionResult, ExplorationTrigger


class TestRedisIntegratedWorldModelManager:
    """Test suite for Redis-integrated world model manager"""

    @pytest.fixture
    async def mock_redis_manager(self):
        """Create a mock Redis manager for testing"""
        mock_manager = Mock(spec=ProductionRedisManager)

        # Mock async methods
        mock_manager.store_world_model = AsyncMock(return_value=True)
        mock_manager.retrieve_world_model = AsyncMock(return_value=None)
        mock_manager.search_similar_world_models = AsyncMock(return_value=[])
        mock_manager.store_exploration_pattern = AsyncMock(return_value=True)
        mock_manager.retrieve_exploration_patterns = AsyncMock(return_value=[])
        mock_manager.store_agent_memory = AsyncMock(return_value=True)
        mock_manager.retrieve_agent_memory = AsyncMock(return_value=None)
        mock_manager.get_storage_stats = AsyncMock(
            return_value={"connection_status": "active", "total_keys": 0, "memory_usage": "0B"}
        )
        mock_manager.cleanup_expired_keys = AsyncMock(return_value=0)
        mock_manager.disconnect = AsyncMock()

        return mock_manager

    @pytest.fixture
    async def world_model_manager(self, mock_redis_manager):
        """Create a Redis-integrated world model manager for testing"""
        manager = RedisIntegratedWorldModelManager(
            redis_manager=mock_redis_manager, enable_caching=True, cache_prefetch=True
        )
        return manager

    @pytest.fixture
    def sample_world_model(self):
        """Create a sample world model for testing"""
        return WorldModel(
            domain="test_domain",
            confidence_score=0.8,
            model_level=WorldModelLevel.INSTANCE,
            model_type=ModelType.PROBABILISTIC,
            structure={"nodes": ["A", "B"], "edges": [("A", "B")]},
            parameters={"learning_rate": 0.01, "threshold": 0.5},
            dependencies=["dependency1", "dependency2"],
            variables=["var1", "var2"],
            parent_models=["parent1"],
            child_models=["child1", "child2"],
        )

    @pytest.fixture
    def sample_evidence(self):
        """Create sample evidence for testing"""
        return WorldModelEvidence(
            observation_id="test_obs_001",
            evidence_type="sensor_data",
            data={"value": 42, "status": "active"},
            timestamp=datetime.now(),
            reliability=0.9,
            source="test_sensor",
        )

    @pytest.fixture
    def sample_trigger_result(self):
        """Create sample trigger result for testing"""
        return TriggerDetectionResult(
            triggers=[ExplorationTrigger.NOVEL_SITUATION],
            confidence_scores={ExplorationTrigger.NOVEL_SITUATION: 0.85},
            novelty_score=0.8,
            complexity_score=0.7,
            sparsity_score=0.6,
            reasoning_required=True,
            exploration_priority="high",
            suggested_strategies=["explore_alternative", "gather_more_data"],
            metadata={"uncertainty_source": "model_prediction", "action_recommendation": "explore_alternative"},
        )

    @pytest.mark.asyncio
    async def test_initialization(self, mock_redis_manager):
        """Test Redis manager initialization"""
        manager = RedisIntegratedWorldModelManager(redis_manager=mock_redis_manager, enable_caching=True)

        assert manager.redis_manager is mock_redis_manager
        assert manager.enable_caching is True
        assert manager._cache_hits == 0
        assert manager._cache_misses == 0

    @pytest.mark.asyncio
    async def test_initialize_redis_new_connection(self):
        """Test creating new Redis connection"""
        manager = RedisIntegratedWorldModelManager(redis_url="redis://localhost:6379")
        with patch("reasoning_kernel.core.redis_world_model_manager.create_production_redis_manager") as mock_create:
            mock_redis = Mock()
            mock_redis.get_storage_stats = AsyncMock(return_value={"connection_status": "active"})
            mock_create.return_value = mock_redis

            await manager.initialize_redis()

            mock_create.assert_called_once_with("redis://localhost:6379")
            assert manager.redis_manager is mock_redis

    @pytest.mark.asyncio
    async def test_store_world_model(self, world_model_manager, sample_world_model):
        """Test storing world model with Redis persistence"""
        result = await world_model_manager.store_world_model(
            world_model=sample_world_model, scenario="test_scenario", abstraction_level="omega1"
        )

        assert result is True
        world_model_manager.redis_manager.store_world_model.assert_called_once()

        # Check in-memory cache
        cache_key = "test_scenario:omega1"
        assert cache_key in world_model_manager.world_models
        assert world_model_manager.world_models[cache_key] is sample_world_model
        assert world_model_manager._storage_operations == 1

    @pytest.mark.asyncio
    async def test_retrieve_world_model_cache_hit(self, world_model_manager, sample_world_model):
        """Test retrieving world model from in-memory cache"""
        # Pre-populate cache
        cache_key = "test_scenario:omega1"
        world_model_manager.world_models[cache_key] = sample_world_model

        result = await world_model_manager.retrieve_world_model(scenario="test_scenario", abstraction_level="omega1")

        assert result is sample_world_model
        assert world_model_manager._cache_hits == 1
        # Redis should not be called for cache hit
        world_model_manager.redis_manager.retrieve_world_model.assert_not_called()

    @pytest.mark.asyncio
    async def test_retrieve_world_model_redis_fallback(self, world_model_manager):
        """Test retrieving world model from Redis when not in cache"""
        # Mock Redis return data
        redis_data = {
            "domain": "test_domain",
            "confidence_score": "0.8",
            "model_level": "INSTANCE",
            "model_type": "PROBABILISTIC",
            "structure": '{"nodes": ["A", "B"]}',
            "parameters": '{"learning_rate": 0.01}',
            "dependencies": '["dep1"]',
            "variables": '["var1"]',
            "parent_models": '["parent1"]',
            "child_models": '["child1"]',
            "last_updated": datetime.now().isoformat(),
        }
        world_model_manager.redis_manager.retrieve_world_model.return_value = redis_data

        result = await world_model_manager.retrieve_world_model(scenario="test_scenario", abstraction_level="omega1")

        assert result is not None
        assert result.domain == "test_domain"
        assert result.confidence_score == 0.8
        assert world_model_manager._cache_misses == 1

        # Should now be cached
        cache_key = "test_scenario:omega1"
        assert cache_key in world_model_manager.world_models

    @pytest.mark.asyncio
    async def test_search_similar_models(self, world_model_manager):
        """Test searching for similar world models"""
        # Mock Redis return data
        similar_data = [
            {
                "domain": "similar_domain_1",
                "confidence_score": "0.75",
                "model_level": "INSTANCE",
                "model_type": "PROBABILISTIC",
                "structure": "{}",
                "parameters": "{}",
                "dependencies": "[]",
                "variables": "[]",
                "parent_models": "[]",
                "child_models": "[]",
                "last_updated": datetime.now().isoformat(),
            },
            {
                "domain": "similar_domain_2",
                "confidence_score": "0.85",
                "model_level": "CATEGORY",
                "model_type": "DETERMINISTIC",
                "structure": "{}",
                "parameters": "{}",
                "dependencies": "[]",
                "variables": "[]",
                "parent_models": "[]",
                "child_models": "[]",
                "last_updated": datetime.now().isoformat(),
            },
        ]
        world_model_manager.redis_manager.search_similar_world_models.return_value = similar_data

        results = await world_model_manager.search_similar_models(
            domain="test_domain", confidence_threshold=0.7, limit=5
        )

        assert len(results) == 2
        assert results[0].domain == "similar_domain_1"
        assert results[1].domain == "similar_domain_2"
        assert results[1].model_level == WorldModelLevel.CATEGORY

        world_model_manager.redis_manager.search_similar_world_models.assert_called_once_with(
            domain="test_domain", confidence_threshold=0.7, limit=5
        )

    @pytest.mark.asyncio
    async def test_store_exploration_pattern(self, world_model_manager, sample_trigger_result):
        """Test storing exploration patterns"""
        pattern_data = {
            "exploration_strategy": "random_walk",
            "success_rate": 0.75,
            "context": "high_uncertainty_environment",
        }

        result = await world_model_manager.store_exploration_pattern(
            scenario="test_scenario", trigger_result=sample_trigger_result, pattern_data=pattern_data
        )

        assert result is True
        world_model_manager.redis_manager.store_exploration_pattern.assert_called_once_with(
            scenario="test_scenario", trigger_result=sample_trigger_result, pattern_data=pattern_data
        )

    @pytest.mark.asyncio
    async def test_retrieve_exploration_patterns(self, world_model_manager):
        """Test retrieving exploration patterns"""
        mock_patterns = [
            {"pattern_id": "pattern1", "strategy": "random"},
            {"pattern_id": "pattern2", "strategy": "greedy"},
        ]
        world_model_manager.redis_manager.retrieve_exploration_patterns.return_value = mock_patterns

        patterns = await world_model_manager.retrieve_exploration_patterns(
            trigger_type=ExplorationTrigger.NOVEL_SITUATION, limit=5
        )

        assert patterns == mock_patterns
        world_model_manager.redis_manager.retrieve_exploration_patterns.assert_called_once_with(
            trigger_type=ExplorationTrigger.NOVEL_SITUATION, limit=5
        )

    @pytest.mark.asyncio
    async def test_agent_memory_operations(self, world_model_manager):
        """Test agent memory storage and retrieval"""
        memory_data = {
            "session_history": ["action1", "action2"],
            "learned_patterns": {"pattern1": 0.8},
            "preferences": {"exploration_rate": 0.3},
        }

        # Test storage
        store_result = await world_model_manager.store_agent_memory(
            agent_type="reasoning_agent", agent_id="agent_001", memory_data=memory_data
        )
        assert store_result is True

        # Mock retrieval
        world_model_manager.redis_manager.retrieve_agent_memory.return_value = memory_data

        # Test retrieval
        retrieved_memory = await world_model_manager.retrieve_agent_memory(
            agent_type="reasoning_agent", agent_id="agent_001"
        )

        assert retrieved_memory == memory_data
        world_model_manager.redis_manager.store_agent_memory.assert_called_once()
        world_model_manager.redis_manager.retrieve_agent_memory.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_hierarchical_model_with_caching(self, world_model_manager, sample_evidence):
        """Test creating hierarchical model with pattern caching"""
        evidence_list = [sample_evidence]

        # Mock similar models search results from Redis
        world_model_manager.redis_manager.search_similar_world_models.return_value = [
            {
                "domain": "cached_domain",
                "confidence_score": "0.7",
                "model_level": "INSTANCE",
                "model_type": "PROBABILISTIC",
                "structure": "{}",
                "parameters": "{}",
                "dependencies": "[]",
                "variables": "[]",
                "parent_models": "[]",
                "child_models": "[]",
                "last_updated": datetime.now().isoformat(),
            }
        ]

        # Mock base class method
        with patch.object(world_model_manager.__class__.__bases__[0], "create_hierarchical_model") as mock_super:
            mock_world_model = WorldModel(domain="test_domain")
            mock_abstraction_result = Mock()
            mock_super.return_value = (mock_world_model, mock_abstraction_result)

            world_model, abstraction_result = await world_model_manager.create_hierarchical_model(
                scenario="test_scenario",
                evidence_list=evidence_list,
                target_level=WorldModelLevel.CATEGORY,
                use_cached_patterns=True,
            )

            assert world_model is mock_world_model
            assert abstraction_result is mock_abstraction_result

            # Should search for similar models
            world_model_manager.redis_manager.search_similar_world_models.assert_called_once()

            # Should store the new model
            world_model_manager.redis_manager.store_world_model.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_model_with_evidence(self, world_model_manager, sample_world_model, sample_evidence):
        """Test updating model with new evidence"""
        # Mock model retrieval
        world_model_manager.redis_manager.retrieve_world_model.return_value = {
            "domain": "test_domain",
            "confidence_score": "0.8",
            "model_level": "INSTANCE",
            "model_type": "PROBABILISTIC",
            "structure": "{}",
            "parameters": "{}",
            "dependencies": "[]",
            "variables": "[]",
            "parent_models": "[]",
            "child_models": "[]",
            "last_updated": datetime.now().isoformat(),
        }

        # Mock base class update method
        with patch.object(world_model_manager.__class__.__bases__[0], "update_model_with_evidence") as mock_super:
            mock_update_result = Mock()
            mock_update_result.update_successful = True
            mock_super.return_value = mock_update_result

            result = await world_model_manager.update_model_with_evidence(
                scenario="test_scenario", abstraction_level="omega1", evidence=sample_evidence
            )

            assert result is mock_update_result

            # Should call retrieve, update, and store
            world_model_manager.redis_manager.retrieve_world_model.assert_called_once()
            world_model_manager.redis_manager.store_world_model.assert_called()

    @pytest.mark.asyncio
    async def test_performance_metrics(self, world_model_manager):
        """Test getting comprehensive performance metrics"""
        # Mock base class metrics
        with patch.object(world_model_manager.__class__.__bases__[0], "get_performance_metrics") as mock_super:
            mock_super.return_value = {"models_created": 5, "abstraction_operations": 10}

            # Set some cache metrics
            world_model_manager._cache_hits = 15
            world_model_manager._cache_misses = 5
            world_model_manager._storage_operations = 20

            metrics = await world_model_manager.get_performance_metrics()

            assert "models_created" in metrics
            assert "redis_metrics" in metrics
            assert "cache_performance" in metrics
            assert metrics["cache_performance"]["cache_hits"] == 15
            assert metrics["cache_performance"]["cache_misses"] == 5
            assert metrics["cache_performance"]["hit_ratio"] == 0.75
            assert metrics["cache_performance"]["storage_operations"] == 20

    @pytest.mark.asyncio
    async def test_cleanup_operations(self, world_model_manager):
        """Test cleanup of expired models"""
        # Mock Redis cleanup
        world_model_manager.redis_manager.cleanup_expired_keys.return_value = 10

        # Add some entries to memory cache
        for i in range(150):  # More than 100 to trigger memory cleanup
            world_model_manager.world_models[f"test_key_{i}"] = WorldModel(domain=f"domain_{i}")

        cleanup_count = await world_model_manager.cleanup_expired_models()

        assert cleanup_count >= 10  # At least Redis cleanup count
        world_model_manager.redis_manager.cleanup_expired_keys.assert_called_once()

        # Memory cache should be reduced
        assert len(world_model_manager.world_models) < 150

    @pytest.mark.asyncio
    async def test_shutdown_redis(self, world_model_manager):
        """Test graceful Redis shutdown"""
        await world_model_manager.shutdown_redis()
        world_model_manager.redis_manager.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_reconstruct_world_model_error_handling(self, world_model_manager):
        """Test error handling in world model reconstruction"""
        # Invalid Redis data
        invalid_data = {
            "domain": "test_domain",
            "confidence_score": "invalid_float",  # This will cause error
            "structure": "invalid_json",
        }

        result = world_model_manager._reconstruct_world_model_from_redis(invalid_data)

        # Should return fallback model
        assert result is not None
        assert result.domain == "test_domain"
        assert isinstance(result, WorldModel)

    @pytest.mark.asyncio
    async def test_extract_domain_from_evidence(self, world_model_manager):
        """Test domain extraction from evidence"""
        # Test with evidence containing source
        evidence1 = WorldModelEvidence(
            observation_id="obs1",
            evidence_type="sensor",
            data={},
            timestamp=datetime.now(),
            reliability=0.8,
            source="test_source",
        )

        evidence2 = WorldModelEvidence(
            observation_id="obs2",
            evidence_type="sensor",
            data={},
            timestamp=datetime.now(),
            reliability=0.7,
            source="",  # Empty source
        )

        # Test with valid source
        domain1 = world_model_manager._extract_domain_from_evidence([evidence1, evidence2])
        assert domain1 == "test_source"

        # Test with empty evidence
        domain2 = world_model_manager._extract_domain_from_evidence([])
        assert domain2 == "general"

        # Test with evidence without source
        domain3 = world_model_manager._extract_domain_from_evidence([evidence2])
        assert domain3 == "general"


class TestRedisWorldModelManagerFactory:
    """Test the factory function for creating Redis world model managers"""

    @pytest.mark.asyncio
    async def test_create_redis_world_model_manager(self):
        """Test factory function for creating manager"""
        with patch("reasoning_kernel.core.redis_world_model_manager.create_production_redis_manager") as mock_create:
            mock_redis = Mock()
            mock_redis.get_storage_stats = AsyncMock(return_value={"connection_status": "active"})
            mock_create.return_value = mock_redis

            manager = await create_redis_world_model_manager(redis_url="redis://test:6379", enable_caching=False)

            assert isinstance(manager, RedisIntegratedWorldModelManager)
            assert manager.redis_url == "redis://test:6379"
            assert manager.enable_caching is False
            assert manager.redis_manager is mock_redis

            mock_create.assert_called_once_with("redis://test:6379")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
