"""Example usage of MCP Redis Cloud integration

This example demonstrates how to use the MCP Redis Cloud tools
with the MSA Reasoning Engine for knowledge storage and retrieval.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from reasoning_kernel.integrations.mcp_redis import MCPRedisWrapper

async def basic_redis_operations():
    """Demonstrate basic Redis operations using MCP wrapper."""
    print("=== Basic Redis Operations ===")

    async with MCPRedisWrapper() as redis:
        # Store some knowledge
        knowledge = {
            "topic": "machine_learning",
            "content": "Machine learning is a subset of AI that focuses on algorithms that improve through experience",
            "confidence": 0.95,
            "sources": ["textbook", "research_paper"]
        }

        success = await redis.store_knowledge("knowledge:ml:001", knowledge, ttl=3600)
        print(f"Stored knowledge: {success}")

        # Retrieve knowledge
        retrieved = await redis.retrieve_knowledge("knowledge:ml:001")
        print(f"Retrieved knowledge: {json.dumps(retrieved, indent=2)}")

        # List available tools
        tools = redis.get_available_tools()
        print(f"Available tools: {', '.join(tools)}")

async def vector_search_example():
    """Demonstrate vector similarity search."""
    print("\n=== Vector Similarity Search ===")

    async with MCPRedisWrapper() as redis:
        # Example query embedding (in practice, this would come from your embedding model)
        query_embedding = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]

        # Search for similar knowledge
        similar_items = await redis.search_similar_knowledge(
            embedding=query_embedding,
            index="knowledge_embeddings",
            limit=3
        )

        print(f"Found {len(similar_items)} similar knowledge items:")
        for item in similar_items:
            print(f"  - {item}")

async def text_search_example():
    """Demonstrate text search functionality."""
    print("\n=== Text Search ===")

    async with MCPRedisWrapper() as redis:
        # Search for knowledge by text
        results = await redis.search_knowledge_text(
            query="machine learning algorithms",
            index="knowledge_text",
            limit=5
        )

        print(f"Text search results: {json.dumps(results, indent=2)}")

async def reasoning_engine_integration():
    """Example of integrating with the reasoning engine workflow."""
    print("\n=== Reasoning Engine Integration ===")

    # This would typically be called from within the reasoning engine
    async with MCPRedisWrapper() as redis:
        # Store extracted knowledge from LLM processing
        extracted_knowledge = {
            "scenario": "factory_machine_failure",
            "entities": ["machine", "production_line", "maintenance_team"],
            "relationships": [
                {"from": "machine", "to": "production_line", "type": "part_of"},
                {"from": "maintenance_team", "to": "machine", "type": "responsible_for"}
            ],
            "constraints": ["48_hour_deadline", "order_backlog"],
            "uncertainty_factors": ["repair_time", "part_availability"]
        }

        # Store in Redis for later retrieval by probabilistic model
        await redis.store_knowledge(
            "reasoning:factory_failure:entities",
            extracted_knowledge,
            ttl=7200  # 2 hours
        )

        print("Stored extracted knowledge for reasoning engine")

        # Later, retrieve for probabilistic model synthesis
        retrieved_knowledge = await redis.retrieve_knowledge("reasoning:factory_failure:entities")

        if retrieved_knowledge:
            print("Knowledge available for probabilistic model synthesis:")
            print(f"  Entities: {retrieved_knowledge['entities']}")
            print(f"  Constraints: {retrieved_knowledge['constraints']}")
            print(f"  Uncertainty factors: {retrieved_knowledge['uncertainty_factors']}")

async def mcp_server_example():
    """Example of using the MCP server directly."""
    print("\n=== MCP Server Direct Usage ===")

    # This would typically be used when integrating with MCP clients
    from third_party.mcp_redis_cloud.src.mcp_redis_cloud import RedisCloudMCPServer

    server = RedisCloudMCPServer()
    await server.start()

    try:
        # List available tools
        tools = server.list_tools()
        print(f"MCP Server provides {len(tools)} tools:")
        for tool in tools:
            print(f"  - {tool['name']}: {tool['description']}")

        # Call a tool
        result = await server.call_tool("redis_set", {
            "key": "mcp:test",
            "value": "Hello from MCP!",
            "ttl": 300
        })
        print(f"Tool call result: {json.dumps(result, indent=2)}")

    finally:
        await server.stop()

async def main():
    """Run all examples."""
    try:
        await basic_redis_operations()
        await vector_search_example()
        await text_search_example()
        await reasoning_engine_integration()
        await mcp_server_example()

    except ImportError as e:
        print(f"Error: {e}")
        print("Make sure the MCP Redis Cloud tools are properly vendored.")
    except Exception as e:
        print(f"Example error: {e}")
        print("Note: These examples use simulated Redis operations for demonstration.")

if __name__ == "__main__":
    asyncio.run(main())
