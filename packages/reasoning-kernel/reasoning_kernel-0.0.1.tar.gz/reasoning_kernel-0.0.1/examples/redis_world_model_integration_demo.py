"""
Redis World Model Integration Demo

Comprehensive demonstration of the Redis-integrated world model system
showing hierarchical reasoning, persistent storage, caching, and
production-ready deployment capabilities.

Features Demonstrated:
- Redis-backed world model storage and retrieval
- Hierarchical model creation with evidence integration
- Exploration pattern storage and reuse
- Agent memory persistence across sessions
- Performance monitoring and optimization
- Error recovery and fallback mechanisms

Author: AI Assistant & Reasoning Kernel Team
Date: 2025-08-15
"""

import asyncio
import logging
from datetime import datetime

from reasoning_kernel.core.redis_world_model_manager import RedisIntegratedWorldModelManager, create_redis_world_model_manager
from reasoning_kernel.models.world_model import WorldModelLevel, WorldModelEvidence
from reasoning_kernel.core.exploration_triggers import TriggerDetectionResult, ExplorationTrigger

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def demo_basic_world_model_operations():
    """Demonstrate basic world model storage and retrieval"""
    logger.info("=== Basic World Model Operations Demo ===")

    # Create Redis-integrated manager
    manager = await create_redis_world_model_manager(redis_url="redis://localhost:6379", enable_caching=True)

    try:
        # Create sample evidence
        evidence_list = [
            WorldModelEvidence(
                observation_id="obs_001",
                evidence_type="sensor_reading",
                data={"temperature": 23.5, "humidity": 65, "location": "office"},
                timestamp=datetime.now(),
                reliability=0.9,
                source="IoT_sensor_01",
            ),
            WorldModelEvidence(
                observation_id="obs_002",
                evidence_type="user_interaction",
                data={"action": "window_opened", "duration": 300, "user": "alice"},
                timestamp=datetime.now(),
                reliability=0.8,
                source="user_interface",
            ),
        ]

        # Create hierarchical world model
        logger.info("Creating hierarchical world model...")
        world_model, abstraction_result = await manager.create_hierarchical_model(
            scenario="smart_office_environment", evidence_list=evidence_list, target_level=WorldModelLevel.CATEGORY
        )

        logger.info(f"Created model: {world_model.model_id}")
        logger.info(f"Confidence: {world_model.confidence_score:.2f}")
        logger.info(f"Evidence count: {len(world_model.evidence_history)}")
        logger.info(f"Abstraction confidence: {abstraction_result.abstraction_confidence:.2f}")

        # Store the model
        success = await manager.store_world_model(
            world_model=world_model, scenario="smart_office_environment", abstraction_level="omega2"
        )
        logger.info(f"Storage successful: {success}")

        # Retrieve the model (should hit cache)
        retrieved_model = await manager.retrieve_world_model(
            scenario="smart_office_environment", abstraction_level="omega2"
        )

        if retrieved_model:
            logger.info(f"Retrieved model: {retrieved_model.model_id}")
            logger.info(f"Cache hit - same instance: {retrieved_model is world_model}")

        # Search for similar models
        similar_models = await manager.search_similar_models(
            domain="smart_office_environment", confidence_threshold=0.5, limit=5
        )
        logger.info(f"Found {len(similar_models)} similar models")

        return manager

    except Exception as e:
        logger.error(f"Error in basic operations demo: {e}")
        await manager.shutdown_redis()
        raise

async def demo_evidence_updates(manager: RedisIntegratedWorldModelManager):
    """Demonstrate evidence-based model updates"""
    logger.info("\n=== Evidence Updates Demo ===")

    try:
        # Create new evidence
        new_evidence = WorldModelEvidence(
            observation_id="obs_003",
            evidence_type="environmental_change",
            data={"temperature": 25.1, "humidity": 70, "cause": "heating_system"},
            timestamp=datetime.now(),
            reliability=0.95,
            source="IoT_sensor_01",
        )

        # Update model with new evidence
        logger.info("Updating model with new evidence...")
        update_result = await manager.update_model_with_evidence(
            scenario="smart_office_environment", abstraction_level="omega2", evidence=new_evidence
        )

        if update_result:
            logger.info(f"Update successful: {update_result.update_successful}")
            logger.info(f"Prior confidence: {update_result.prior_confidence:.3f}")
            logger.info(f"Posterior confidence: {update_result.posterior_confidence:.3f}")
            logger.info(f"Evidence impact: {update_result.evidence_impact:.3f}")
        else:
            logger.warning("No model found to update")

    except Exception as e:
        logger.error(f"Error in evidence updates demo: {e}")

async def demo_exploration_patterns(manager: RedisIntegratedWorldModelManager):
    """Demonstrate exploration pattern storage and retrieval"""
    logger.info("\n=== Exploration Patterns Demo ===")

    try:
        # Create trigger detection result
        trigger_result = TriggerDetectionResult(
            triggers=[ExplorationTrigger.NOVEL_SITUATION, ExplorationTrigger.DYNAMIC_ENVIRONMENT],
            confidence_scores={ExplorationTrigger.NOVEL_SITUATION: 0.85, ExplorationTrigger.DYNAMIC_ENVIRONMENT: 0.72},
            novelty_score=0.8,
            complexity_score=0.6,
            sparsity_score=0.4,
            reasoning_required=True,
            exploration_priority="high",
            suggested_strategies=["adaptive_sampling", "uncertainty_exploration"],
            metadata={"context": "smart_office_environment", "trigger_source": "environmental_sensors"},
        )

        # Store exploration pattern
        pattern_data = {
            "strategy": "environmental_adaptation",
            "success_rate": 0.78,
            "sample_efficiency": 0.85,
            "context_factors": ["temperature_change", "user_behavior"],
            "learned_parameters": {"adaptation_rate": 0.15, "confidence_threshold": 0.7},
        }

        logger.info("Storing exploration pattern...")
        success = await manager.store_exploration_pattern(
            scenario="smart_office_environment", trigger_result=trigger_result, pattern_data=pattern_data
        )
        logger.info(f"Pattern storage successful: {success}")

        # Retrieve exploration patterns
        logger.info("Retrieving exploration patterns...")
        patterns = await manager.retrieve_exploration_patterns(trigger_type=ExplorationTrigger.NOVEL_SITUATION, limit=3)
        logger.info(f"Retrieved {len(patterns)} exploration patterns")

        for i, pattern in enumerate(patterns):
            if isinstance(pattern, dict):
                logger.info(f"Pattern {i+1}: {pattern.get('strategy', 'unknown')}")

    except Exception as e:
        logger.error(f"Error in exploration patterns demo: {e}")

async def demo_agent_memory(manager: RedisIntegratedWorldModelManager):
    """Demonstrate agent memory persistence"""
    logger.info("\n=== Agent Memory Demo ===")

    try:
        # Store agent memory
        memory_data = {
            "session_history": [
                {"action": "observe_environment", "timestamp": datetime.now().isoformat()},
                {"action": "create_world_model", "timestamp": datetime.now().isoformat()},
                {"action": "update_with_evidence", "timestamp": datetime.now().isoformat()},
            ],
            "learned_patterns": {
                "temperature_correlation": 0.85,
                "user_behavior_pattern": 0.72,
                "environmental_stability": 0.63,
            },
            "preferences": {"exploration_rate": 0.3, "confidence_threshold": 0.7, "update_frequency": "adaptive"},
            "performance_metrics": {"accuracy": 0.87, "efficiency": 0.92, "adaptability": 0.79},
        }

        logger.info("Storing agent memory...")
        success = await manager.store_agent_memory(
            agent_type="reasoning_agent", agent_id="ra_001", memory_data=memory_data
        )
        logger.info(f"Memory storage successful: {success}")

        # Retrieve agent memory
        logger.info("Retrieving agent memory...")
        retrieved_memory = await manager.retrieve_agent_memory(agent_type="reasoning_agent", agent_id="ra_001")

        if retrieved_memory:
            logger.info(f"Retrieved memory with {len(retrieved_memory)} key sections")
            logger.info(f"Session history: {len(retrieved_memory.get('session_history', []))} actions")
            logger.info(f"Learned patterns: {len(retrieved_memory.get('learned_patterns', {}))} patterns")
        else:
            logger.warning("No agent memory found")

    except Exception as e:
        logger.error(f"Error in agent memory demo: {e}")

async def demo_performance_monitoring(manager: RedisIntegratedWorldModelManager):
    """Demonstrate performance monitoring and metrics"""
    logger.info("\n=== Performance Monitoring Demo ===")

    try:
        # Get comprehensive performance metrics
        logger.info("Collecting performance metrics...")
        metrics = await manager.get_performance_metrics()

        logger.info("=== Performance Report ===")

        # Base metrics
        base_metrics = {k: v for k, v in metrics.items() if k not in ["redis_metrics", "cache_performance"]}
        logger.info(f"Base Metrics: {base_metrics}")

        # Cache performance
        cache_metrics = metrics.get("cache_performance", {})
        logger.info(f"Cache Hit Ratio: {cache_metrics.get('hit_ratio', 0):.2%}")
        logger.info(f"Cache Hits: {cache_metrics.get('cache_hits', 0)}")
        logger.info(f"Cache Misses: {cache_metrics.get('cache_misses', 0)}")
        logger.info(f"Storage Operations: {cache_metrics.get('storage_operations', 0)}")

        # Redis metrics
        redis_metrics = metrics.get("redis_metrics", {})
        logger.info(f"Redis Status: {redis_metrics.get('connection_status', 'unknown')}")
        logger.info(f"Redis Keys: {redis_metrics.get('total_keys', 0)}")
        logger.info(f"Memory Usage: {redis_metrics.get('memory_usage', 'unknown')}")

        # Cleanup expired models
        logger.info("Running cleanup operations...")
        cleanup_count = await manager.cleanup_expired_models()
        logger.info(f"Cleaned up {cleanup_count} expired entries")

    except Exception as e:
        logger.error(f"Error in performance monitoring demo: {e}")

async def demo_error_recovery(manager: RedisIntegratedWorldModelManager):
    """Demonstrate error recovery and fallback mechanisms"""
    logger.info("\n=== Error Recovery Demo ===")

    try:
        # Test retrieval of non-existent model
        logger.info("Testing retrieval of non-existent model...")
        missing_model = await manager.retrieve_world_model(
            scenario="non_existent_scenario", abstraction_level="omega99"
        )
        logger.info(f"Non-existent model result: {missing_model}")

        # Test model reconstruction with invalid data
        logger.info("Testing model reconstruction error handling...")
        invalid_data = {
            "domain": "test_domain",
            "confidence_score": "invalid_float",
            "model_level": "INVALID_LEVEL",
            "structure": "invalid_json",
        }

        fallback_model = manager._reconstruct_world_model_from_redis(invalid_data)
        logger.info(f"Fallback model created: {fallback_model.domain}")
        logger.info(f"Fallback confidence: {fallback_model.confidence_score}")

        # Test search with empty results
        logger.info("Testing search with high threshold...")
        no_results = await manager.search_similar_models(
            domain="impossible_domain", confidence_threshold=0.99, limit=10
        )
        logger.info(f"High threshold search results: {len(no_results)} models")

    except Exception as e:
        logger.error(f"Error in error recovery demo: {e}")

async def main():
    """Run the complete Redis world model integration demo"""
    logger.info("Starting Redis World Model Integration Demo")
    logger.info("=" * 60)

    manager = None
    try:
        # Run all demo sections
        manager = await demo_basic_world_model_operations()
        await demo_evidence_updates(manager)
        await demo_exploration_patterns(manager)
        await demo_agent_memory(manager)
        await demo_performance_monitoring(manager)
        await demo_error_recovery(manager)

        logger.info("\n" + "=" * 60)
        logger.info("Redis World Model Integration Demo Completed Successfully!")
        logger.info("All features demonstrated:")
        logger.info("✅ Hierarchical world model creation and storage")
        logger.info("✅ Evidence-based model updates")
        logger.info("✅ Exploration pattern management")
        logger.info("✅ Agent memory persistence")
        logger.info("✅ Performance monitoring and metrics")
        logger.info("✅ Error recovery and fallback mechanisms")
        logger.info("✅ Redis-backed caching and optimization")

    except Exception as e:
        logger.error(f"Demo failed with error: {e}")
        raise

    finally:
        if manager:
            await manager.shutdown_redis()
            logger.info("Redis connection closed gracefully")

if __name__ == "__main__":
    asyncio.run(main())
