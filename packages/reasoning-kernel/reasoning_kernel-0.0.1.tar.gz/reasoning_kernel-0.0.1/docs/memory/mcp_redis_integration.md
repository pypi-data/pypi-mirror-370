# MCP Redis Cloud Integration

## Overview

The MSA Reasoning Engine now includes integration with Redis Cloud through the Model Context Protocol (MCP). This integration provides AI assistants with direct access to Redis Cloud databases for knowledge storage, retrieval, and vector search operations.

## Features

- **Knowledge Storage**: Store extracted knowledge and reasoning artifacts in Redis Cloud
- **Vector Search**: Perform semantic similarity searches using Redis Cloud's vector capabilities
- **Text Search**: Full-text search across stored knowledge and documents
- **MCP Protocol**: Standard Model Context Protocol interface for AI assistant integration
- **Async Operations**: Non-blocking Redis operations for high performance

## Architecture

The integration consists of:

1. **Vendored MCP Redis Cloud Tools** (`third_party/mcp-redis-cloud/`)
   - Complete MCP server implementation for Redis Cloud
   - Client library for Redis operations
   - Tool definitions for MCP protocol
   - MIT licensed (license preserved)

2. **MSA Integration Wrapper** (`app/integrations/mcp_redis.py`)
   - Lightweight wrapper for easy integration with reasoning engine
   - Async context managers for connection management
   - Knowledge-specific methods for reasoning workflows

3. **Example Usage** (`examples/mcp_redis_example.py`)
   - Comprehensive examples of Redis operations
   - Integration patterns with reasoning engine
   - Vector and text search demonstrations

## Configuration

### Environment Variables

Set up your Redis Cloud connection:

```bash
export REDIS_URL="redis://your-redis-cloud-instance:port"
export REDIS_PASSWORD="your-password"
```

### MCP Server Configuration

The MCP server is configured in `.gemini/mcp.json`:

```json
{
  "mcpServers": {
    "redis-cloud": {
      "command": "python",
      "args": ["-m", "third_party.mcp-redis-cloud.src.mcp_redis_cloud.server"],
      "env": {
        "REDIS_URL": "$REDIS_URL",
        "REDIS_PASSWORD": "$REDIS_PASSWORD"
      },
      "cwd": "./",
      "timeout": 30000,
      "trust": true
    }
  }
}
```

## Usage

### Basic Integration

```python
from reasoning_kernel.integrations.mcp_redis import MCPRedisWrapper

async with MCPRedisWrapper() as redis:
    # Store knowledge
    knowledge = {"topic": "ml", "content": "Machine learning concepts"}
    await redis.store_knowledge("knowledge:ml:001", knowledge)
    
    # Retrieve knowledge
    data = await redis.retrieve_knowledge("knowledge:ml:001")
    
    # Vector search
    results = await redis.search_similar_knowledge(embedding_vector)
```

### Reasoning Engine Integration

The Redis integration can be used throughout the reasoning pipeline:

1. **Knowledge Extraction Phase**: Store extracted entities, relationships, and constraints
2. **Model Synthesis Phase**: Retrieve relevant knowledge for probabilistic model construction
3. **Inference Phase**: Cache intermediate results and final predictions
4. **Memory Management**: Long-term storage of reasoning sessions and outcomes

### Available Tools

The MCP server provides the following tools:

- `redis_get`: Retrieve values by key
- `redis_set`: Store key-value pairs with optional TTL
- `redis_delete`: Delete keys
- `redis_search_vector`: Vector similarity search
- `redis_search_text`: Full-text search
- `redis_json_get`: Retrieve JSON documents
- `redis_json_set`: Store JSON documents
- `redis_list_keys`: List keys by pattern

## Testing

Run the example to test the integration:

```bash
python examples/mcp_redis_example.py
```

Note: The current implementation includes simulated Redis operations for demonstration. In production, ensure you have a Redis Cloud instance configured.

## Dependencies

The integration requires the following packages (already included in project dependencies):

- `redis>=5.0.0`
- `hiredis>=2.3.0`
- `asyncio` (built-in)

## License

The vendored MCP Redis Cloud tools maintain their original MIT license. See `third_party/mcp-redis-cloud/LICENSE` for details.

## Contributing

This is a vendored integration. For improvements to the core MCP Redis tools, contribute to the upstream repository. For MSA-specific integration improvements, submit PRs to this repository.
