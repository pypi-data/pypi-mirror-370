"""
Test script for HierarchicalWorldModelManager
============================================

Simple test to verify the hierarchical world model manager functionality.
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import AsyncMock
from reasoning_kernel.services.hierarchical_world_model_manager import HierarchicalWorldModelManager
from reasoning_kernel.models.world_model import WorldModel, WorldModelLevel, ModelType, WorldModelEvidence
from datetime import datetime


async def test_hierarchical_manager():
    """Test basic functionality of hierarchical world model manager"""

    print("🧠 Testing HierarchicalWorldModelManager...")

    # Create mock redis manager
    mock_redis = AsyncMock()
    mock_redis.store_world_model = AsyncMock(return_value=True)
    mock_redis.get_models_by_level = AsyncMock(return_value=[])

    # Create manager
    manager = HierarchicalWorldModelManager(mock_redis)

    # Test 1: Construct instance model
    print("📝 Test 1: Constructing instance model...")
    try:
        instance_model = await manager.construct_instance_model(
            scenario_id="test_scenario_001",
            scenario_description="A novel medical condition with bioluminescent symptoms",
            context={"domain": "medical", "urgency": "high"},
        )

        assert instance_model is not None
        assert instance_model.model_level == WorldModelLevel.INSTANCE
        assert instance_model.domain == "test_scenario_001"
        assert "medical condition" in instance_model.context_description
        print("✅ Instance model construction successful")

    except Exception as e:
        print(f"❌ Instance model construction failed: {e}")
        return False

    # Test 2: Model similarity computation
    print("📝 Test 2: Computing model similarity...")
    try:
        # Create two test models
        model1 = WorldModel(
            model_level=WorldModelLevel.INSTANCE,
            model_type=ModelType.PROBABILISTIC,
            domain="medical",
            context_description="Rare disease with unusual symptoms",
            parameters={"severity": 0.8, "contagion": 0.2},
        )

        model2 = WorldModel(
            model_level=WorldModelLevel.INSTANCE,
            model_type=ModelType.PROBABILISTIC,
            domain="medical",
            context_description="Uncommon illness with strange manifestations",
            parameters={"severity": 0.7, "contagion": 0.3},
        )

        similarity = await manager.compute_model_similarity(model1, model2)

        assert similarity is not None
        assert 0.0 <= similarity.similarity_score <= 1.0
        assert similarity.model_id == model2.model_id
        print(f"✅ Model similarity computed: {similarity.similarity_score:.3f}")

    except Exception as e:
        print(f"❌ Model similarity computation failed: {e}")
        return False

    # Test 3: Bayesian update
    print("📝 Test 3: Testing Bayesian update...")
    try:
        # Create test evidence
        evidence = WorldModelEvidence(
            observation_id="obs_001",
            evidence_type="observation",
            data={"finding": "positive response to treatment", "confidence": 0.9},
            timestamp=datetime.now(),
            reliability=0.85,
            source="clinical_trial",
        )

        # Mock retrieve to return our test model
        mock_redis.retrieve_world_model = AsyncMock(return_value=model1)

        updated_model = await manager.bayesian_update(
            model_id=model1.model_id, new_evidence=evidence, learning_rate=0.1
        )

        assert updated_model is not None
        assert len(updated_model.evidence_history) > 0
        print("✅ Bayesian update successful")

    except Exception as e:
        print(f"❌ Bayesian update failed: {e}")
        return False

    print("🎉 All hierarchical world model manager tests passed!")
    return True


async def main():
    """Run all tests"""
    success = await test_hierarchical_manager()

    if success:
        print("\n🚀 HierarchicalWorldModelManager is ready for Phase 2!")
        exit(0)
    else:
        print("\n💥 Some tests failed")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
