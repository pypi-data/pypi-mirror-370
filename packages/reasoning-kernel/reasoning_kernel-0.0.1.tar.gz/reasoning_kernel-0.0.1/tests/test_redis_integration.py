"""
Test Redis Cloud Vector Service Integration

This script tests the Redis Cloud vector service integration with
the modern kernel manager.
"""

import asyncio
import os
import logging
from datetime import datetime, UTC

from reasoning_kernel.core.modern_kernel_manager import ModernKernelManager

async def test_redis_integration():
    """Test Redis Cloud integration with reasoning kernel"""
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Configuration for testing
    config = {
        "openai_api_key": os.environ.get("OPENAI_API_KEY"),
        "redis_url": os.environ.get("REDIS_URL", "redis://localhost:6379"),
    }

    if not config["openai_api_key"]:
        logger.warning("OPENAI_API_KEY not found - using mock embedding")
        return

    # Initialize manager outside try block
    manager = None

    try:
        # Initialize modern kernel manager
        logger.info("Initializing Modern Kernel Manager...")
        manager = ModernKernelManager(config)

        # Initialize the kernel and Redis service
        await manager.initialize()

        # Test Redis service initialization
        if manager.redis_service:
            logger.info("✓ Redis Vector Service initialized")

            # Test health check
            health = await manager.redis_service.health_check()
            logger.info(f"Redis Health: {health}")

            # Test storing a reasoning pattern
            logger.info("Testing reasoning pattern storage...")
            pattern_id = await manager.store_reasoning_pattern(
                question="What is the capital of France?",
                reasoning_steps="Looking at geographical and political facts about France",
                final_answer="Paris is the capital of France",
                pattern_type="factual_lookup",
                confidence=0.95,
                context={"domain": "geography", "difficulty": "basic"},
            )

            if pattern_id:
                logger.info(f"✓ Stored reasoning pattern: {pattern_id}")

                # Test similarity search
                logger.info("Testing similarity search...")
                results = await manager.search_similar_reasoning(query="What is the capital city?", limit=3)
                logger.info(f"Search results: {len(results)} patterns found")

            # Test storing world model
            logger.info("Testing world model storage...")
            model_id = await manager.store_world_model(
                model_type="geographic_knowledge",
                state_data={
                    "facts": {"France": {"capital": "Paris", "continent": "Europe"}},
                    "updated": datetime.now(UTC).isoformat(),
                },
                confidence=0.9,
                context_keys=["geography", "capitals"],
            )

            if model_id:
                logger.info(f"✓ Stored world model: {model_id}")

            # Test system stats
            logger.info("Getting system statistics...")
            stats = await manager.get_system_stats()
            logger.info(f"System Stats: {stats}")

            # Test health check
            logger.info("Performing health check...")
            health_check = await manager.health_check()
            logger.info(f"Health Check: {health_check}")

        else:
            logger.warning("Redis service not available")

        logger.info("✓ Redis Cloud integration test completed successfully")

    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)

    finally:
        # Cleanup
        try:
            if manager and hasattr(manager, "redis_service") and manager.redis_service:
                await manager.redis_service.close()
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

if __name__ == "__main__":
    print("🧪 Testing Redis Cloud Vector Service Integration")
    print("=" * 50)
    asyncio.run(test_redis_integration())
