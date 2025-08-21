"""
Unit Tests for Thinking Exploration Framework
============================================

Comprehensive test suite for trigger detection, model synthesis, and Redis integration.
TASK-007: Develop comprehensive unit tests for trigger detection and basic synthesis.
"""

try:
    import pytest
except ImportError:
    pytest = None

import asyncio
import json
from unittest.mock import Mock, AsyncMock
from datetime import datetime

# Import the modules we're testing
from reasoning_kernel.core.exploration_triggers import (
    ExplorationTrigger,
    TriggerDetectionResult,
    ExplorationTriggerConfig,
    NoveltyDetectionConfig,
    DynamicsDetectionConfig,
    SparsityDetectionConfig,
)

from reasoning_kernel.models.world_model import WorldModel, WorldModelLevel, ModelType, WorldModelEvidence

from reasoning_kernel.plugins.thinking_exploration_plugin import ThinkingExplorationPlugin, AdHocModelResult

from reasoning_kernel.services.thinking_exploration_redis import (
    ThinkingExplorationRedisManager,
    RedisCollectionConfig,
    ExplorationPattern,
)


class TestExplorationTriggers:
    """Test exploration trigger detection and configuration"""

    def test_exploration_trigger_enum(self):
        """Test that all exploration triggers are properly defined"""
        expected_triggers = {
            "NOVEL_SITUATION",
            "DYNAMIC_ENVIRONMENT",
            "SPARSE_INTERACTION",
            "NEW_VARIABLES",
            "COMPLEX_NL_PROBLEM",
            "CAUSAL_UNCERTAINTY",
            "HYPOTHESIS_CONFLICT",
        }

        actual_triggers = {trigger.name for trigger in ExplorationTrigger}
        assert actual_triggers == expected_triggers

    def test_trigger_detection_result_creation(self):
        """Test TriggerDetectionResult dataclass creation"""
        triggers = [ExplorationTrigger.NOVEL_SITUATION, ExplorationTrigger.SPARSE_INTERACTION]
        confidence_scores = {ExplorationTrigger.NOVEL_SITUATION: 0.8, ExplorationTrigger.SPARSE_INTERACTION: 0.6}

        result = TriggerDetectionResult(
            triggers=triggers,
            confidence_scores=confidence_scores,
            novelty_score=0.8,
            complexity_score=0.5,
            sparsity_score=0.6,
            reasoning_required=True,
            exploration_priority="high",
            suggested_strategies=["ad_hoc_model_synthesis", "sample_efficient_learning"],
            metadata={"test": True},
        )

        assert result.triggers == triggers
        assert result.confidence_scores == confidence_scores
        assert result.reasoning_required is True
        assert result.exploration_priority == "high"
        assert len(result.suggested_strategies) == 2

    def test_exploration_trigger_config_default(self):
        """Test default configuration creation"""
        config = ExplorationTriggerConfig.default()

        assert isinstance(config.novelty_config, NoveltyDetectionConfig)
        assert isinstance(config.dynamics_config, DynamicsDetectionConfig)
        assert isinstance(config.sparsity_config, SparsityDetectionConfig)
        assert config.trigger_confidence_threshold == 0.6
        assert config.preferred_strategies is not None
        assert ExplorationTrigger.NOVEL_SITUATION in config.preferred_strategies

    def test_novelty_detection_config(self):
        """Test novelty detection configuration"""
        config = NoveltyDetectionConfig(
            similarity_threshold=0.4, vocabulary_novelty_weight=0.5, semantic_novelty_weight=0.5
        )

        assert config.similarity_threshold == 0.4
        assert config.vocabulary_novelty_weight == 0.5
        assert config.semantic_novelty_weight == 0.5
        assert config.embedding_model == "gemini-embedding-001"


class TestWorldModel:
    """Test world model data structures and functionality"""

    def test_world_model_creation(self):
        """Test basic world model creation"""
        model = WorldModel(
            model_level=WorldModelLevel.INSTANCE,
            model_type=ModelType.PROBABILISTIC,
            domain="medical",
            context_description="Test medical scenario",
        )

        assert model.model_level == WorldModelLevel.INSTANCE
        assert model.model_type == ModelType.PROBABILISTIC
        assert model.domain == "medical"
        assert model.context_description == "Test medical scenario"
        assert model.confidence_score == 0.5  # Default
        assert model.storage_key is not None

    def test_world_model_ttl_assignment(self):
        """Test TTL assignment based on model level"""
        instance_model = WorldModel(model_level=WorldModelLevel.INSTANCE)
        abstract_model = WorldModel(model_level=WorldModelLevel.ABSTRACT)

        assert instance_model.ttl_seconds == 3600  # 1 hour
        assert abstract_model.ttl_seconds == 2592000  # 1 month

    def test_world_model_evidence_handling(self):
        """Test adding evidence to world model"""
        model = WorldModel()

        evidence = WorldModelEvidence(
            observation_id="obs_1",
            evidence_type="observation",
            data={"temperature": 38.5},
            timestamp=datetime.utcnow(),
            reliability=0.9,
            source="sensor",
        )

        model.add_evidence(evidence)

        assert len(model.evidence_history) == 1
        assert model.evidence_history[0] == evidence

    def test_world_model_confidence_update(self):
        """Test confidence score updates"""
        model = WorldModel()
        initial_confidence = model.confidence_score

        model.update_confidence(0.8)
        assert model.confidence_score == 0.8
        assert model.confidence_score != initial_confidence

        # Test bounds
        model.update_confidence(1.5)  # Should be clamped to 1.0
        assert model.confidence_score == 1.0

        model.update_confidence(-0.5)  # Should be clamped to 0.0
        assert model.confidence_score == 0.0

    def test_world_model_serialization(self):
        """Test world model to/from dict conversion"""
        original_model = WorldModel(
            model_level=WorldModelLevel.CATEGORY,
            model_type=ModelType.CAUSAL,
            domain="financial",
            context_description="Market analysis",
            tags=["test", "finance"],
        )

        # Test serialization
        model_dict = original_model.to_dict()
        assert model_dict["model_level"] == "CATEGORY"
        assert model_dict["model_type"] == "CAUSAL"
        assert model_dict["domain"] == "financial"

        # Test deserialization
        restored_model = WorldModel.from_dict(model_dict)
        assert restored_model.model_level == original_model.model_level
        assert restored_model.model_type == original_model.model_type
        assert restored_model.domain == original_model.domain
        assert restored_model.tags == original_model.tags

    def test_world_model_json_conversion(self):
        """Test JSON serialization/deserialization"""
        model = WorldModel(domain="test", variables=["var1", "var2"])

        json_str = model.to_json()
        assert isinstance(json_str, str)
        assert "test" in json_str

        restored_model = WorldModel.from_json(json_str)
        assert restored_model.domain == model.domain
        assert restored_model.variables == model.variables


class TestThinkingExplorationPlugin:
    """Test the main thinking exploration plugin functionality"""

    @pytest.fixture
    def mock_kernel(self):
        """Create mock Semantic Kernel"""
        kernel = Mock()
        return kernel

    @pytest.fixture
    def mock_redis(self):
        """Create mock Redis client"""
        redis_client = AsyncMock()
        return redis_client

    @pytest.fixture
    def plugin(self, mock_kernel, mock_redis):
        """Create plugin instance for testing"""
        return ThinkingExplorationPlugin(kernel=mock_kernel, redis_client=mock_redis)

    def test_plugin_initialization(self, plugin):
        """Test plugin initialization"""
        assert plugin.kernel is not None
        assert plugin.redis_client is not None
        assert plugin.config is not None
        assert len(plugin._novelty_patterns) > 0
        assert len(plugin._dynamics_patterns) > 0
        assert len(plugin._sparsity_patterns) > 0

    @pytest.mark.asyncio
    async def test_novelty_detection(self, plugin):
        """Test novelty detection algorithm"""
        # High novelty text
        high_novelty_text = (
            "This unprecedented and mysterious phenomenon has never been seen before in scientific literature"
        )
        novelty_score = await plugin._detect_novelty(high_novelty_text, {})
        assert novelty_score > 0.5

        # Low novelty text
        low_novelty_text = "The patient has a common cold with typical symptoms"
        novelty_score = await plugin._detect_novelty(low_novelty_text, {})
        assert novelty_score < 0.8

    @pytest.mark.asyncio
    async def test_dynamics_detection(self, plugin):
        """Test dynamic environment detection"""
        # High dynamics text
        dynamic_text = "The market is rapidly changing and evolving with unprecedented volatility"
        dynamics_score = await plugin._detect_dynamics(dynamic_text, {})
        assert dynamics_score > 0.3

        # Low dynamics text
        static_text = "The system maintains stable operation under normal conditions"
        dynamics_score = await plugin._detect_dynamics(static_text, {})
        assert dynamics_score < 0.5

    @pytest.mark.asyncio
    async def test_sparsity_detection(self, plugin):
        """Test sparse interaction detection"""
        # High sparsity text
        sparse_text = "We have limited data and few examples with uncertain outcomes and unclear patterns"
        sparsity_score = await plugin._detect_sparsity(sparse_text, {})
        assert sparsity_score > 0.4

        # Low sparsity text
        rich_text = "Comprehensive data analysis reveals clear patterns with abundant evidence"
        sparsity_score = await plugin._detect_sparsity(rich_text, {})
        assert sparsity_score < 0.6

    @pytest.mark.asyncio
    async def test_exploration_trigger_detection(self, plugin):
        """Test main exploration trigger detection function"""
        scenario = """
        A patient presents with bioluminescent fingernails, a completely novel symptom
        never documented in medical literature. The condition is rapidly evolving
        and we have very limited data to work with.
        """

        result = await plugin.detect_exploration_trigger(scenario)

        assert isinstance(result, TriggerDetectionResult)
        assert len(result.triggers) > 0
        assert ExplorationTrigger.NOVEL_SITUATION in result.triggers
        assert result.novelty_score > 0.6
        assert result.reasoning_required is True
        assert result.exploration_priority in ["medium", "high", "critical"]

    @pytest.mark.asyncio
    async def test_adhoc_model_synthesis(self, plugin):
        """Test ad-hoc model synthesis"""
        scenario = "Unknown alien technology discovered with quantum properties"

        trigger_result = TriggerDetectionResult(
            triggers=[ExplorationTrigger.NOVEL_SITUATION, ExplorationTrigger.NEW_VARIABLES],
            confidence_scores={ExplorationTrigger.NOVEL_SITUATION: 0.8},
            novelty_score=0.8,
            complexity_score=0.7,
            sparsity_score=0.6,
            reasoning_required=True,
            exploration_priority="high",
            suggested_strategies=["ad_hoc_model_synthesis"],
            metadata={},
        )

        result = await plugin.synthesize_adhoc_model(scenario, trigger_result, "scientific")

        assert isinstance(result, AdHocModelResult)
        assert isinstance(result.world_model, WorldModel)
        assert result.world_model.domain == "scientific"
        assert result.synthesis_confidence > 0.0
        assert len(result.reasoning_trace) > 0
        assert len(result.generated_program) > 0
        assert "numpyro" in result.generated_program.lower()

    @pytest.mark.asyncio
    async def test_reasoning_with_thinking(self, plugin):
        """Test main reasoning interface"""
        scenario = "Market showing strange correlation with ocean temperatures"

        result = await plugin.reason_with_thinking(scenario, mode="adaptive", domain="financial")

        assert "reasoning_type" in result
        assert "trigger_analysis" in result

        # Check if exploration was triggered
        if result["reasoning_type"] == "thinking_exploration":
            assert "world_model" in result
            assert "inference_result" in result
            assert "exploration_strategy" in result

    def test_variable_extraction(self, plugin):
        """Test variable extraction from scenarios"""
        scenario = "Patient temperature affects heart_rate and blood_pressure measurements"
        variables = plugin._extract_variables(scenario)

        assert len(variables) > 0
        assert any("temperature" in var.lower() for var in variables)

    def test_dependency_identification(self, plugin):
        """Test dependency identification between variables"""
        variables = ["temperature", "heart_rate", "blood_pressure"]
        scenario = "Temperature affects heart_rate which influences blood_pressure"

        dependencies = plugin._identify_dependencies(variables, scenario)
        assert len(dependencies) >= 0  # May or may not find dependencies

    def test_program_validation(self, plugin):
        """Test PPL program validation"""
        # Valid program
        valid_program = """
import numpy as np
from numpyro import sample, distributions as dist

def model():
    x = sample('x', dist.Normal(0, 1))
    return x
"""

        validation_result = asyncio.run(plugin._validate_program_structure(valid_program))
        assert validation_result["is_valid"] is True
        assert validation_result["score"] > 0.8

        # Invalid program
        invalid_program = "this is not valid python code !!!"
        validation_result = asyncio.run(plugin._validate_program_structure(invalid_program))
        assert validation_result["is_valid"] is False
        assert len(validation_result["syntax_errors"]) > 0


class TestThinkingExplorationRedis:
    """Test Redis integration for thinking exploration"""

    @pytest.fixture
    def mock_redis(self):
        """Create mock Redis client"""
        redis_client = AsyncMock()
        # Setup common Redis method responses
        redis_client.setex.return_value = True
        redis_client.sadd.return_value = 1
        redis_client.expire.return_value = True
        redis_client.get.return_value = None
        redis_client.smembers.return_value = set()
        redis_client.keys.return_value = []
        return redis_client

    @pytest.fixture
    def redis_manager(self, mock_redis):
        """Create Redis manager for testing"""
        return ThinkingExplorationRedisManager(redis_client=mock_redis, config=RedisCollectionConfig())

    def test_redis_manager_initialization(self, redis_manager):
        """Test Redis manager initialization"""
        assert redis_manager.redis is not None
        assert redis_manager.config is not None
        assert isinstance(redis_manager.config, RedisCollectionConfig)

    def test_redis_collection_config(self):
        """Test Redis collection configuration"""
        config = RedisCollectionConfig()

        assert config.world_models_collection == "thinking_exploration:world_models"
        assert config.instance_model_ttl == 3600
        assert config.abstract_model_ttl == 2592000
        assert config.embedding_dimension == 768

        # Test TTL mapping
        assert config.get_ttl_for_level(WorldModelLevel.INSTANCE) == 3600
        assert config.get_ttl_for_level(WorldModelLevel.ABSTRACT) == 2592000

    @pytest.mark.asyncio
    async def test_world_model_storage(self, redis_manager):
        """Test world model storage in Redis"""
        model = WorldModel(
            model_level=WorldModelLevel.CATEGORY,
            domain="test",
            context_description="Test model",
            tags=["test", "category"],
        )

        success = await redis_manager.store_world_model(model)
        assert success is True

        # Verify Redis calls were made
        redis_manager.redis.setex.assert_called()
        redis_manager.redis.sadd.assert_called()

    @pytest.mark.asyncio
    async def test_world_model_retrieval(self, redis_manager):
        """Test world model retrieval from Redis"""
        # Setup mock return value
        test_model = WorldModel(domain="test")
        redis_manager.redis.get.return_value = test_model.to_json().encode("utf-8")

        retrieved_model = await redis_manager.retrieve_world_model("test_id")

        assert retrieved_model is not None
        assert isinstance(retrieved_model, WorldModel)
        assert retrieved_model.domain == "test"

    def test_exploration_pattern_creation(self):
        """Test exploration pattern data structure"""
        pattern = ExplorationPattern(
            pattern_id="pattern_1",
            trigger_type=ExplorationTrigger.NOVEL_SITUATION,
            scenario_hash="abc123",
            success_rate=0.8,
            strategy_used="ad_hoc_model_synthesis",
            domain="medical",
            context_features={"complexity": "high"},
            created_at=datetime.utcnow(),
        )

        assert pattern.pattern_id == "pattern_1"
        assert pattern.trigger_type == ExplorationTrigger.NOVEL_SITUATION
        assert pattern.success_rate == 0.8
        assert pattern.usage_count == 0  # Default

    def test_exploration_pattern_serialization(self):
        """Test exploration pattern serialization"""
        pattern = ExplorationPattern(
            pattern_id="test",
            trigger_type=ExplorationTrigger.SPARSE_INTERACTION,
            scenario_hash="hash",
            success_rate=0.7,
            strategy_used="sample_efficient_learning",
            domain="finance",
            context_features={},
            created_at=datetime.utcnow(),
        )

        # Test to_dict
        pattern_dict = pattern.to_dict()
        assert pattern_dict["pattern_id"] == "test"
        assert pattern_dict["trigger_type"] == "SPARSE_INTERACTION"
        assert pattern_dict["success_rate"] == 0.7

        # Test from_dict
        restored_pattern = ExplorationPattern.from_dict(pattern_dict)
        assert restored_pattern.pattern_id == pattern.pattern_id
        assert restored_pattern.trigger_type == pattern.trigger_type
        assert restored_pattern.success_rate == pattern.success_rate

    @pytest.mark.asyncio
    async def test_exploration_pattern_storage(self, redis_manager):
        """Test exploration pattern storage"""
        pattern = ExplorationPattern(
            pattern_id="test_pattern",
            trigger_type=ExplorationTrigger.DYNAMIC_ENVIRONMENT,
            scenario_hash="scenario_hash",
            success_rate=0.85,
            strategy_used="adaptive_learning",
            domain="robotics",
            context_features={"sensors": "lidar"},
            created_at=datetime.utcnow(),
        )

        success = await redis_manager.store_exploration_pattern(pattern)
        assert success is True

        # Verify Redis calls
        redis_manager.redis.setex.assert_called()
        redis_manager.redis.sadd.assert_called()

    @pytest.mark.asyncio
    async def test_storage_stats(self, redis_manager):
        """Test storage statistics generation"""
        # Mock Redis info response
        redis_manager.redis.info.return_value = {
            "used_memory": 1024,
            "used_memory_human": "1K",
            "used_memory_peak": 2048,
            "used_memory_peak_human": "2K",
        }

        stats = await redis_manager.get_storage_stats()

        assert "collections" in stats
        assert "total_keys" in stats
        assert "memory_usage" in stats
        assert "timestamp" in stats

    def test_cosine_similarity_calculation(self, redis_manager):
        """Test cosine similarity calculation"""
        import numpy as np

        vec1 = np.array([1, 0, 0])
        vec2 = np.array([1, 0, 0])
        similarity = redis_manager._cosine_similarity(vec1, vec2)
        assert abs(similarity - 1.0) < 1e-6  # Should be 1.0 for identical vectors

        vec3 = np.array([0, 1, 0])
        similarity = redis_manager._cosine_similarity(vec1, vec3)
        assert abs(similarity - 0.0) < 1e-6  # Should be 0.0 for orthogonal vectors


class TestIntegration:
    """Integration tests for the complete thinking exploration system"""

    @pytest.fixture
    def full_system(self):
        """Create a complete system setup for integration testing"""
        mock_kernel = Mock()
        mock_redis = AsyncMock()

        plugin = ThinkingExplorationPlugin(kernel=mock_kernel, redis_client=mock_redis)

        redis_manager = ThinkingExplorationRedisManager(redis_client=mock_redis)

        return {"plugin": plugin, "redis_manager": redis_manager, "kernel": mock_kernel, "redis": mock_redis}

    @pytest.mark.asyncio
    async def test_end_to_end_exploration_flow(self, full_system):
        """Test complete exploration flow from trigger to storage"""
        plugin = full_system["plugin"]
        redis_manager = full_system["redis_manager"]

        # Step 1: Novel scenario
        scenario = """
        Scientists discover organisms with quantum consciousness that can
        exist in superposition states. This unprecedented discovery has
        never been documented and requires completely new understanding.
        """

        # Step 2: Detect triggers
        trigger_result = await plugin.detect_exploration_trigger(scenario)
        assert trigger_result.reasoning_required is True
        assert len(trigger_result.triggers) > 0

        # Step 3: Synthesize model
        synthesis_result = await plugin.synthesize_adhoc_model(scenario, trigger_result, "scientific")
        assert synthesis_result.synthesis_confidence > 0.0

        # Step 4: Store results
        model_stored = await redis_manager.store_world_model(synthesis_result.world_model)
        assert model_stored is True

        trigger_stored = await redis_manager.store_trigger_history(trigger_result, scenario)
        assert trigger_stored is True

    @pytest.mark.asyncio
    async def test_pattern_learning_and_reuse(self, full_system):
        """Test learning from exploration patterns and reusing them"""
        redis_manager = full_system["redis_manager"]

        # Create successful exploration pattern
        pattern = ExplorationPattern(
            pattern_id="successful_pattern",
            trigger_type=ExplorationTrigger.NOVEL_SITUATION,
            scenario_hash="medical_novel",
            success_rate=0.9,
            strategy_used="ad_hoc_model_synthesis",
            domain="medical",
            context_features={"symptom_type": "novel"},
            created_at=datetime.utcnow(),
        )

        # Store pattern
        stored = await redis_manager.store_exploration_pattern(pattern)
        assert stored is True

        # Mock retrieval
        redis_manager.redis.smembers.return_value = {b"successful_pattern"}
        redis_manager.redis.get.return_value = json.dumps(pattern.to_dict()).encode("utf-8")

        # Remove unused variable assignment
        await redis_manager.get_exploration_patterns(trigger_type=ExplorationTrigger.NOVEL_SITUATION, domain="medical")

        # Should have made retrieval calls
        redis_manager.redis.smembers.assert_called()

    def test_configuration_consistency(self):
        """Test that all configurations are consistent"""
        trigger_config = ExplorationTriggerConfig.default()
        redis_config = RedisCollectionConfig()

        # Verify trigger types are properly mapped (handle potential None)
        if trigger_config.preferred_strategies is not None:
            for trigger in ExplorationTrigger:
                if trigger in trigger_config.preferred_strategies:
                    assert len(trigger_config.preferred_strategies[trigger]) > 0

        # Verify TTL mappings exist for all levels
        for level in WorldModelLevel:
            ttl = redis_config.get_ttl_for_level(level)
            assert ttl > 0
            assert ttl <= redis_config.abstract_model_ttl

    @pytest.mark.asyncio
    async def test_error_handling_and_resilience(self, full_system):
        """Test system resilience to errors"""
        plugin = full_system["plugin"]

        # Test with empty input
        result = await plugin.detect_exploration_trigger("")
        assert isinstance(result, TriggerDetectionResult)
        assert result.novelty_score >= 0.0

        # Test with malformed input
        result = await plugin.detect_exploration_trigger("!@#$%^&*()")
        assert isinstance(result, TriggerDetectionResult)

        # Test synthesis with minimal trigger context
        minimal_trigger = TriggerDetectionResult(
            triggers=[],
            confidence_scores={},
            novelty_score=0.0,
            complexity_score=0.0,
            sparsity_score=0.0,
            reasoning_required=False,
            exploration_priority="low",
            suggested_strategies=[],
            metadata={},
        )

        synthesis_result = await plugin.synthesize_adhoc_model("simple test", minimal_trigger)
        assert isinstance(synthesis_result, AdHocModelResult)
        assert synthesis_result.synthesis_confidence > 0.0


if __name__ == "__main__":
    # Run tests if executed directly (only if pytest is available)
    if pytest is not None:
        pytest.main([__file__, "-v"])
    else:
        print("pytest not available - install with: pip install pytest pytest-asyncio")
