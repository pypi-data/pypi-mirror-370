"""
Simple Test Runner for Thinking Exploration Framework
====================================================

Basic test runner that doesn't require pytest for essential validation.
Runs core functionality tests to verify the framework components.
"""

import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock

# Import framework components
from reasoning_kernel.core.exploration_triggers import (
    ExplorationTrigger,
    TriggerDetectionResult,
    ExplorationTriggerConfig,
    NoveltyDetectionConfig,
)

from reasoning_kernel.models.world_model import WorldModel, WorldModelLevel, ModelType, WorldModelEvidence

from reasoning_kernel.plugins.thinking_exploration_plugin import ThinkingExplorationPlugin, AdHocModelResult

from reasoning_kernel.services.thinking_exploration_redis import (
    ThinkingExplorationRedisManager,
    RedisCollectionConfig,
    ExplorationPattern,
)


def test_exploration_triggers():
    """Test exploration trigger enumeration and configuration"""
    print("Testing exploration triggers...")

    # Test enum exists and has expected values
    assert ExplorationTrigger.NOVEL_SITUATION
    assert ExplorationTrigger.DYNAMIC_ENVIRONMENT
    assert ExplorationTrigger.SPARSE_INTERACTION

    # Test configuration creation
    config = ExplorationTriggerConfig.default()
    assert config.trigger_confidence_threshold > 0
    assert config.novelty_config is not None

    # Test novelty config
    novelty_config = NoveltyDetectionConfig()
    assert novelty_config.similarity_threshold > 0
    assert novelty_config.embedding_model == "gemini-embedding-001"

    # Test trigger detection result
    result = TriggerDetectionResult(
        triggers=[ExplorationTrigger.NOVEL_SITUATION],
        confidence_scores={ExplorationTrigger.NOVEL_SITUATION: 0.8},
        novelty_score=0.8,
        complexity_score=0.6,
        sparsity_score=0.4,
        reasoning_required=True,
        exploration_priority="high",
        suggested_strategies=["ad_hoc_model_synthesis"],
        metadata={},
    )
    assert len(result.triggers) == 1
    assert result.reasoning_required is True

    print("✅ Exploration triggers tests passed")


def test_world_model():
    """Test world model data structures"""
    print("Testing world model...")

    # Test basic creation
    model = WorldModel(
        model_level=WorldModelLevel.INSTANCE,
        model_type=ModelType.PROBABILISTIC,
        domain="test",
        context_description="Test model",
    )

    assert model.model_level == WorldModelLevel.INSTANCE
    assert model.model_type == ModelType.PROBABILISTIC
    assert model.domain == "test"
    assert model.storage_key is not None
    assert model.ttl_seconds is None or model.ttl_seconds > 0  # TTL may be None by default

    # Test evidence handling
    evidence = WorldModelEvidence(
        observation_id="obs_1",
        evidence_type="test",
        data={"test": True},
        timestamp=datetime.utcnow(),
        reliability=0.9,
        source="test",
    )

    model.add_evidence(evidence)
    assert len(model.evidence_history) == 1

    # Test confidence updates
    model.update_confidence(0.9)
    assert model.confidence_score == 0.9

    # Test serialization
    model_dict = model.to_dict()
    assert model_dict["domain"] == "test"
    assert model_dict["model_level"] == "INSTANCE"

    restored_model = WorldModel.from_dict(model_dict)
    assert restored_model.domain == model.domain
    assert restored_model.model_level == model.model_level

    print("✅ World model tests passed")


async def test_thinking_exploration_plugin():
    """Test the main thinking exploration plugin"""
    print("Testing thinking exploration plugin...")

    # Create mock dependencies
    mock_kernel = Mock()
    mock_redis = AsyncMock()

    # Create plugin
    plugin = ThinkingExplorationPlugin(kernel=mock_kernel, redis_client=mock_redis)

    assert plugin.kernel is not None
    assert plugin.redis_client is not None
    assert plugin.config is not None

    # Test novelty detection
    high_novelty_text = "unprecedented mysterious unknown never before seen"
    novelty_score = await plugin._detect_novelty(high_novelty_text, {})
    assert novelty_score > 0.3  # Should detect some novelty

    # Test dynamics detection
    dynamic_text = "rapidly changing evolving fluctuating unstable"
    dynamics_score = await plugin._detect_dynamics(dynamic_text, {})
    assert dynamics_score > 0.2  # Should detect some dynamics

    # Test sparsity detection
    sparse_text = "limited data few examples uncertain unclear"
    sparsity_score = await plugin._detect_sparsity(sparse_text, {})
    assert sparsity_score > 0.2  # Should detect some sparsity

    # Test trigger detection
    scenario = "A novel unprecedented situation with limited data"
    result = await plugin.detect_exploration_trigger(scenario)
    assert isinstance(result, TriggerDetectionResult)
    assert result.novelty_score >= 0.0
    assert result.complexity_score >= 0.0
    assert result.sparsity_score >= 0.0

    # Test ad-hoc model synthesis
    trigger_result = TriggerDetectionResult(
        triggers=[ExplorationTrigger.NOVEL_SITUATION],
        confidence_scores={ExplorationTrigger.NOVEL_SITUATION: 0.8},
        novelty_score=0.8,
        complexity_score=0.6,
        sparsity_score=0.4,
        reasoning_required=True,
        exploration_priority="high",
        suggested_strategies=["ad_hoc_model_synthesis"],
        metadata={},
    )

    synthesis_result = await plugin.synthesize_adhoc_model(scenario, trigger_result, "test")
    assert isinstance(synthesis_result, AdHocModelResult)
    assert synthesis_result.synthesis_confidence > 0.0
    assert len(synthesis_result.reasoning_trace) > 0

    print("✅ Thinking exploration plugin tests passed")


def test_redis_manager():
    """Test Redis storage manager"""
    print("Testing Redis manager...")

    # Test configuration
    config = RedisCollectionConfig()
    assert config.world_models_collection is not None
    assert config.instance_model_ttl > 0
    assert config.abstract_model_ttl > 0

    # Test TTL mapping
    instance_ttl = config.get_ttl_for_level(WorldModelLevel.INSTANCE)
    abstract_ttl = config.get_ttl_for_level(WorldModelLevel.ABSTRACT)
    assert instance_ttl < abstract_ttl  # Abstract models should live longer

    # Test exploration pattern
    pattern = ExplorationPattern(
        pattern_id="test_pattern",
        trigger_type=ExplorationTrigger.NOVEL_SITUATION,
        scenario_hash="test_hash",
        success_rate=0.8,
        strategy_used="test_strategy",
        domain="test",
        context_features={"test": True},
        created_at=datetime.utcnow(),
    )

    assert pattern.pattern_id == "test_pattern"
    assert pattern.trigger_type == ExplorationTrigger.NOVEL_SITUATION
    assert pattern.success_rate == 0.8

    # Test serialization
    pattern_dict = pattern.to_dict()
    assert pattern_dict["pattern_id"] == "test_pattern"
    assert pattern_dict["trigger_type"] == "NOVEL_SITUATION"

    restored_pattern = ExplorationPattern.from_dict(pattern_dict)
    assert restored_pattern.pattern_id == pattern.pattern_id
    assert restored_pattern.trigger_type == pattern.trigger_type

    # Create Redis manager with mock client
    mock_redis = AsyncMock()
    redis_manager = ThinkingExplorationRedisManager(redis_client=mock_redis, config=config)

    assert redis_manager.redis is not None
    assert redis_manager.config is not None

    print("✅ Redis manager tests passed")


async def test_integration():
    """Test basic integration between components"""
    print("Testing integration...")

    # Create system components
    mock_kernel = Mock()
    mock_redis = AsyncMock()

    plugin = ThinkingExplorationPlugin(kernel=mock_kernel, redis_client=mock_redis)

    redis_manager = ThinkingExplorationRedisManager(redis_client=mock_redis)

    # Test scenario
    scenario = "Scientists discover quantum consciousness organisms"

    # Detect triggers
    trigger_result = await plugin.detect_exploration_trigger(scenario)
    assert isinstance(trigger_result, TriggerDetectionResult)

    # Synthesize model
    synthesis_result = await plugin.synthesize_adhoc_model(scenario, trigger_result, "scientific")
    assert isinstance(synthesis_result, AdHocModelResult)
    assert synthesis_result.world_model.domain == "scientific"

    # Mock storage operations
    mock_redis.setex.return_value = True
    mock_redis.sadd.return_value = 1

    # Test storage
    model_stored = await redis_manager.store_world_model(synthesis_result.world_model)
    assert model_stored is True

    print("✅ Integration tests passed")


def run_all_tests():
    """Run all tests in sequence"""
    print("🧪 Running Thinking Exploration Framework Tests")
    print("=" * 50)

    try:
        # Synchronous tests
        test_exploration_triggers()
        test_world_model()
        test_redis_manager()

        # Asynchronous tests
        asyncio.run(test_thinking_exploration_plugin())
        asyncio.run(test_integration())

        print("\n" + "=" * 50)
        print("🎉 All tests passed successfully!")
        print("✅ Thinking exploration framework is ready for Phase 2")

    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback

        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
