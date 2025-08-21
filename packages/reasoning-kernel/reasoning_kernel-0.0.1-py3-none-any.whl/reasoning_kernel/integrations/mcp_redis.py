"""MCP Redis Cloud Integration

Light wrapper for MCP Redis Cloud tools to integrate with the MSA Reasoning Engine.
Provides easy access to Redis Cloud operations through the Model Context Protocol.
"""

import json
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional


# Add third_party/mcp-redis-cloud to Python path
THIRD_PARTY_PATH = Path(__file__).parent.parent.parent / "third_party" / "mcp-redis-cloud" / "src"
sys.path.insert(0, str(THIRD_PARTY_PATH))

try:
    from mcp_redis_cloud import RedisCloudClient
    from mcp_redis_cloud import RedisCloudMCPServer
    from mcp_redis_cloud import RedisTools
except ImportError as e:
    # Fallback if the vendored package is not available
    print(f"Warning: MCP Redis Cloud tools not available: {e}")
    RedisCloudClient = None
    RedisCloudMCPServer = None
    RedisTools = None


class MCPRedisWrapper:
    """Lightweight wrapper for MCP Redis Cloud tools integration."""
    
    def __init__(self, redis_url: Optional[str] = None, password: Optional[str] = None):
        """Initialize the MCP Redis wrapper.
        
        Args:
            redis_url: Redis Cloud connection URL
            password: Redis Cloud password
        """
        if RedisCloudClient is None:
            raise ImportError("MCP Redis Cloud tools are not available. Please check the vendored package.")
        
        self.client = RedisCloudClient(redis_url, password)
        self.server = RedisCloudMCPServer(redis_url, password)
        self._connected = False
    
    async def connect(self) -> bool:
        """Connect to Redis Cloud.
        
        Returns:
            True if connection successful
        """
        try:
            await self.client.connect()
            self._connected = True
            return True
        except Exception as e:
            print(f"Failed to connect to Redis Cloud: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from Redis Cloud."""
        if self._connected:
            await self.client.disconnect()
            self._connected = False
    
    def get_available_tools(self) -> List[str]:
        """Get list of available Redis tools.
        
        Returns:
            List of tool names
        """
        if RedisTools is None:
            return []
        return [tool["name"] for tool in RedisTools.get_tools()]
    
    async def store_knowledge(self, key: str, data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Store knowledge in Redis for the reasoning engine.
        
        Args:
            key: Storage key
            data: Knowledge data to store
            ttl: Time to live in seconds
            
        Returns:
            True if stored successfully
        """
        try:
            json_data = json.dumps(data)
            return await self.client.set(key, json_data, ttl)
        except Exception as e:
            print(f"Error storing knowledge: {e}")
            return False
    
    async def retrieve_knowledge(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve knowledge from Redis.
        
        Args:
            key: Storage key
            
        Returns:
            Knowledge data if found, None otherwise
        """
        try:
            data = await self.client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            print(f"Error retrieving knowledge: {e}")
            return None
    
    async def search_similar_knowledge(self, embedding: List[float], index: str = "knowledge", limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar knowledge using vector similarity.
        
        Args:
            embedding: Query embedding vector
            index: Vector search index name
            limit: Maximum number of results
            
        Returns:
            List of similar knowledge items
        """
        try:
            return await self.client.search_vector(index, embedding, limit)
        except Exception as e:
            print(f"Error searching similar knowledge: {e}")
            return []
    
    async def search_knowledge_text(self, query: str, index: str = "knowledge_text", limit: int = 5) -> List[Dict[str, Any]]:
        """Search knowledge using text search.
        
        Args:
            query: Search query
            index: Text search index name
            limit: Maximum number of results
            
        Returns:
            List of matching knowledge items
        """
        try:
            return await self.client.search_text(index, query, limit)
        except Exception as e:
            print(f"Error searching knowledge text: {e}")
            return []
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()


# Convenience function for easy integration
async def get_redis_client(redis_url: Optional[str] = None, password: Optional[str] = None) -> MCPRedisWrapper:
    """Get a connected Redis MCP client.
    
    Args:
        redis_url: Redis Cloud URL (defaults to REDIS_URL env var)
        password: Redis password (defaults to REDIS_PASSWORD env var)
        
    Returns:
        Connected MCPRedisWrapper instance
    """
    client = MCPRedisWrapper(redis_url, password)
    await client.connect()
    return client