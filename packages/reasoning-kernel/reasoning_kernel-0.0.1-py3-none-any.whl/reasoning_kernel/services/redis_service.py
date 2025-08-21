"""
Redis service for memory storage and retrieval in MSA Reasoning Engine
"""

from datetime import datetime
import hashlib
import json
import logging
from typing import Any, Dict, List, Optional


try:
    import redis
    from redis import asyncio as aioredis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None
    aioredis = None

# Import unified error handling
from ..core.error_handling import handle_errors

logger = logging.getLogger(__name__)


class RedisMemoryService:
    """
    Redis-based memory service for storing reasoning chains,
    intermediate results, and knowledge graphs
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        decode_responses: bool = True,
        max_connections: int = 50,
        ttl_seconds: int = 3600,  # Default TTL of 1 hour
    ):
        """Initialize Redis memory service"""
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.decode_responses = decode_responses
        self.max_connections = max_connections
        self.ttl_seconds = ttl_seconds
        self.redis_client = None
        self.async_redis_client = None
        # Always initialize in-memory cache as fallback
        self._memory_cache = {}

        if REDIS_AVAILABLE:
            self._init_sync_client()
            self._init_async_client()
        else:
            logger.warning("Redis is not installed. Memory service will use in-memory fallback.")

    def _init_sync_client(self):
        """Initialize synchronous Redis client"""
        with handle_errors("init_sync_client", logger=logger):
            if not REDIS_AVAILABLE:
                logger.warning("Redis not available, sync client not initialized")
                return
            self.redis_client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=self.decode_responses,
                connection_pool=redis.ConnectionPool(
                    host=self.host,
                    port=self.port,
                    db=self.db,
                    password=self.password,
                    max_connections=self.max_connections,
                ),
            )
            # Test connection
            self.redis_client.ping()
            logger.info(f"✅ Connected to Redis at {self.host}:{self.port}")

    def _init_async_client(self):
        """Initialize asynchronous Redis client"""
        with handle_errors("init_async_client", logger=logger):
            if not REDIS_AVAILABLE:
                logger.warning("Redis not available, async client not initialized")
                return
            self.async_redis_client = aioredis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=self.decode_responses,
                connection_pool=aioredis.ConnectionPool(
                    host=self.host,
                    port=self.port,
                    db=self.db,
                    password=self.password,
                    max_connections=self.max_connections,
                ),
            )
            logger.info("✅ Async Redis client initialized")

    # Reasoning Chain Storage
    async def store_reasoning_chain(self, chain_id: str, chain_data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Store a reasoning chain with optional TTL"""
        key = f"reasoning_chain:{chain_id}"
        ttl = ttl or self.ttl_seconds

        with handle_errors("store_reasoning_chain", logger=logger, include_performance=True):
            if self.async_redis_client:
                serialized = json.dumps(chain_data)
                await self.async_redis_client.setex(key, ttl, serialized)
                # Also store in a set for tracking
                await self.async_redis_client.sadd("reasoning_chains", chain_id)
                logger.debug(f"Stored reasoning chain: {chain_id}")
                return True
            else:
                # Fallback to in-memory storage
                self._memory_cache[key] = chain_data
                if "reasoning_chains" not in self._memory_cache:
                    self._memory_cache["reasoning_chains"] = set()
                self._memory_cache["reasoning_chains"].add(chain_id)
                return True

    async def get_reasoning_chain(self, chain_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a reasoning chain by ID"""
        key = f"reasoning_chain:{chain_id}"

        with handle_errors("get_reasoning_chain", logger=logger, include_performance=True):
            if self.async_redis_client:
                data = await self.async_redis_client.get(key)
                if data:
                    return json.loads(data) if isinstance(data, str) else data
            else:
                return self._memory_cache.get(key)

            return None

    async def list_reasoning_chains(self) -> List[str]:
        """List all stored reasoning chain IDs"""
        with handle_errors("list_reasoning_chains", logger=logger, include_performance=True):
            if self.async_redis_client:
                chains = await self.async_redis_client.smembers("reasoning_chains")
                return list(chains) if chains else []
            else:
                if "reasoning_chains" in self._memory_cache:
                    return list(self._memory_cache["reasoning_chains"])
                return [
                    k.replace("reasoning_chain:", "") for k in self._memory_cache.keys() if k.startswith("reasoning_chain:")
                ]

    # Knowledge Storage
    async def store_knowledge(
        self,
        knowledge_type: str,
        knowledge_id: str,
        knowledge_data: Dict[str, Any],
        tags: Optional[List[str]] = None,
        ttl: Optional[int] = None,
    ) -> bool:
        """Store knowledge with type and tags for retrieval"""
        key = f"knowledge:{knowledge_type}:{knowledge_id}"
        ttl = ttl or self.ttl_seconds * 24  # Knowledge lasts longer

        with handle_errors("store_knowledge", logger=logger, include_performance=True):
            if self.async_redis_client:
                # Store the knowledge
                knowledge_data["_type"] = knowledge_type
                knowledge_data["_tags"] = tags or []
                knowledge_data["_timestamp"] = datetime.now().isoformat()

                serialized = json.dumps(knowledge_data)
                await self.async_redis_client.setex(key, ttl, serialized)

                # Index by type
                await self.async_redis_client.sadd(f"knowledge_type:{knowledge_type}", knowledge_id)

                # Index by tags
                if tags:
                    for tag in tags:
                        await self.async_redis_client.sadd(f"knowledge_tag:{tag}", f"{knowledge_type}:{knowledge_id}")

                logger.debug(f"Stored knowledge: {knowledge_type}:{knowledge_id}")
                return True
            else:
                knowledge_data["_type"] = knowledge_type
                knowledge_data["_tags"] = tags or []
                knowledge_data["_timestamp"] = datetime.now().isoformat()

                self._memory_cache[key] = knowledge_data

                # Index by type in memory
                type_key = f"knowledge_type:{knowledge_type}"
                if type_key not in self._memory_cache:
                    self._memory_cache[type_key] = set()
                self._memory_cache[type_key].add(knowledge_id)

                # Index by tags in memory
                if tags:
                    for tag in tags:
                        tag_key = f"knowledge_tag:{tag}"
                        if tag_key not in self._memory_cache:
                            self._memory_cache[tag_key] = set()
                        self._memory_cache[tag_key].add(f"{knowledge_type}:{knowledge_id}")

                return True

    async def retrieve_knowledge_by_type(self, knowledge_type: str) -> List[Dict[str, Any]]:
        """Retrieve all knowledge of a specific type"""
        with handle_errors("retrieve_knowledge_by_type", logger=logger, include_performance=True):
            if self.async_redis_client:
                type_key = f"knowledge_type:{knowledge_type}"
                knowledge_ids = await self.async_redis_client.smembers(type_key)
                logger.debug(f"Retrieved {len(knowledge_ids)} IDs from {type_key}: {knowledge_ids}")
                results = []

                for kid in knowledge_ids:
                    # Decode if bytes
                    if isinstance(kid, bytes):
                        kid = kid.decode("utf-8")
                    key = f"knowledge:{knowledge_type}:{kid}"
                    data = await self.async_redis_client.get(key)
                    logger.debug(f"Retrieved data for {key}: {data is not None}")
                    if data:
                        # Parse JSON if string
                        if isinstance(data, str):
                            results.append(json.loads(data))
                        elif isinstance(data, bytes):
                            results.append(json.loads(data.decode("utf-8")))
                        else:
                            results.append(data)

                logger.debug(f"Returning {len(results)} results for type {knowledge_type}")
                return results
            else:
                type_key = f"knowledge_type:{knowledge_type}"
                if type_key in self._memory_cache:
                    results = []
                    for kid in self._memory_cache[type_key]:
                        key = f"knowledge:{knowledge_type}:{kid}"
                        if key in self._memory_cache:
                            results.append(self._memory_cache[key])
                    return results
                # Fallback to searching by prefix
                results = []
                for key, value in self._memory_cache.items():
                    if key.startswith(f"knowledge:{knowledge_type}:"):
                        results.append(value)
                return results

    async def retrieve_knowledge_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """Retrieve all knowledge with a specific tag"""
        with handle_errors("retrieve_knowledge_by_tag", logger=logger, include_performance=True):
            if self.async_redis_client:
                knowledge_refs = await self.async_redis_client.smembers(f"knowledge_tag:{tag}")
                results = []

                for ref in knowledge_refs:
                    key = f"knowledge:{ref}"
                    data = await self.async_redis_client.get(key)
                    if data:
                        results.append(json.loads(data) if isinstance(data, str) else data)

                return results
            else:
                results = []
                for key, value in self._memory_cache.items():
                    if key.startswith("knowledge:") and tag in value.get("_tags", []):
                        results.append(value)
                return results

    # Probabilistic Model Cache
    async def cache_model_result(
        self, model_name: str, input_hash: str, result: Dict[str, Any], ttl: Optional[int] = None
    ) -> bool:
        """Cache probabilistic model results"""
        key = f"model_cache:{model_name}:{input_hash}"
        ttl = ttl or self.ttl_seconds

        with handle_errors("cache_model_result", logger=logger, include_performance=True):
            if self.async_redis_client:
                result["_cached_at"] = datetime.now().isoformat()
                serialized = json.dumps(result)
                await self.async_redis_client.setex(key, ttl, serialized)
                logger.debug(f"Cached model result: {model_name}:{input_hash}")
                return True
            else:
                self._memory_cache[key] = result
                return True

    async def get_cached_model_result(self, model_name: str, input_hash: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached model result"""
        key = f"model_cache:{model_name}:{input_hash}"

        with handle_errors("get_cached_model_result", logger=logger, include_performance=True):
            if self.async_redis_client:
                data = await self.async_redis_client.get(key)
                if data:
                    return json.loads(data) if isinstance(data, str) else data
            else:
                return self._memory_cache.get(key)

            return None

    # Session Management
    async def create_session(self, session_id: str, session_data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Create a new reasoning session"""
        key = f"session:{session_id}"
        ttl = ttl or self.ttl_seconds * 2  # Sessions last longer

        with handle_errors("create_session", logger=logger, include_performance=True):
            if self.async_redis_client:
                session_data["created_at"] = datetime.now().isoformat()
                session_data["last_accessed"] = datetime.now().isoformat()
                serialized = json.dumps(session_data)
                await self.async_redis_client.setex(key, ttl, serialized)
                await self.async_redis_client.sadd("active_sessions", session_id)
                logger.debug(f"Created session: {session_id}")
                return True
            else:
                self._memory_cache[key] = session_data
                return True

    async def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update session data"""
        with handle_errors("update_session", logger=logger, include_performance=True):
            session = await self.get_session(session_id)
            if session:
                session.update(updates)
                session["last_accessed"] = datetime.now().isoformat()
                return await self.create_session(session_id, session)
            return False

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session data"""
        key = f"session:{session_id}"

        with handle_errors("get_session", logger=logger, include_performance=True):
            if self.async_redis_client:
                data = await self.async_redis_client.get(key)
                if data:
                    return json.loads(data) if isinstance(data, str) else data
            else:
                return self._memory_cache.get(key)

            return None

    # Additional utility methods for compatibility
    async def keys(self, pattern: str = "*") -> List[str]:
        """Get keys matching pattern (for compatibility with KnowledgePlugin)"""
        with handle_errors("keys", logger=logger, include_performance=True):
            if self.async_redis_client:
                keys = await self.async_redis_client.keys(pattern)
                return [key.decode("utf-8") if isinstance(key, bytes) else key for key in keys]
            else:
                return [k for k in self._memory_cache.keys() if self._match_pattern(k, pattern)]

    async def get(self, key: str) -> Optional[Any]:
        """Get value by key (for compatibility with KnowledgePlugin)"""
        with handle_errors("get", logger=logger, include_performance=True):
            if self.async_redis_client:
                data = await self.async_redis_client.get(key)
                if data:
                    # Try to parse as JSON first, fall back to string
                    try:
                        return json.loads(data) if isinstance(data, str) else data
                    except json.JSONDecodeError:
                        return data
            else:
                return self._memory_cache.get(key)

            return None

    def _match_pattern(self, key: str, pattern: str) -> bool:
        """Simple pattern matching for keys (supports * wildcard)"""
        import re

        # Convert shell-style wildcards to regex
        regex_pattern = pattern.replace("*", ".*").replace("?", ".")
        return re.match(f"^{regex_pattern}$", key) is not None

    async def setex(self, key: str, ttl: int, value: Any) -> bool:
        """Set key with expiration (for compatibility)"""
        with handle_errors("setex", logger=logger, include_performance=True):
            if self.async_redis_client:
                if isinstance(value, (dict, list)):
                    value = json.dumps(value)
                await self.async_redis_client.setex(key, ttl, value)
                return True
            else:
                self._memory_cache[key] = value
                return True

    async def sadd(self, key: str, *values) -> int:
        """Add members to a set (for compatibility)"""
        with handle_errors("sadd", logger=logger, include_performance=True):
            if self.async_redis_client:
                return await self.async_redis_client.sadd(key, *values)
            else:
                if key not in self._memory_cache:
                    self._memory_cache[key] = set()
                if isinstance(self._memory_cache[key], set):
                    self._memory_cache[key].update(values)
                    return len(values)
                return 0

    async def smembers(self, key: str) -> set:
        """Get all members of a set (for compatibility)"""
        with handle_errors("smembers", logger=logger, include_performance=True):
            if self.async_redis_client:
                members = await self.async_redis_client.smembers(key)
                return members if members else set()
            else:
                return self._memory_cache.get(key, set())

    # Cleanup
    async def cleanup_expired(self) -> int:
        """Clean up expired entries (for in-memory cache)"""
        with handle_errors("cleanup_expired", logger=logger, include_performance=True):
            if not REDIS_AVAILABLE:
                # Simple cleanup for in-memory cache
                initial_size = len(self._memory_cache)
                # In production, you'd want to track expiry times
                return initial_size - len(self._memory_cache)
            return 0

    async def close(self):
        """Close Redis connections"""
        with handle_errors("close", logger=logger):
            if self.async_redis_client:
                await self.async_redis_client.close()
            if self.redis_client:
                self.redis_client.close()


class RedisRetrievalService:
    """
    Advanced retrieval service using Redis for semantic search and similarity matching
    """

    def __init__(self, memory_service: RedisMemoryService):
        """Initialize retrieval service with memory service"""
        self.memory_service = memory_service
        self.embeddings_cache = {}  # Local cache for embeddings

    @staticmethod
    def compute_hash(content: str) -> str:
        """Compute hash for content"""
        return hashlib.sha256(content.encode()).hexdigest()

    async def semantic_search(
        self, query: str, search_type: str = "knowledge", limit: int = 10, similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search across stored items
        Note: This is a simplified version. In production, you'd use vector embeddings
        """
        with handle_errors("semantic_search", logger=logger, include_performance=True):
            results = []

            if search_type == "knowledge":
                # Search across all knowledge types
                all_knowledge = []
                if self.memory_service.async_redis_client:
                    # Get all knowledge keys
                    keys = await self.memory_service.async_redis_client.keys("knowledge:*")
                    for key in keys[: limit * 2]:  # Sample more than needed
                        data = await self.memory_service.async_redis_client.get(key)
                        if data:
                            knowledge = json.loads(data) if isinstance(data, str) else data
                            # Simple text matching for now
                            if self._simple_similarity(query, str(knowledge)) > similarity_threshold:
                                results.append(knowledge)
                                if len(results) >= limit:
                                    break
                else:
                    # Fallback to in-memory search
                    for key, value in self.memory_service._memory_cache.items():
                        if key.startswith("knowledge:"):
                            if self._simple_similarity(query, str(value)) > similarity_threshold:
                                results.append(value)
                                if len(results) >= limit:
                                    break

            return results

    def _simple_similarity(self, text1: str, text2: str) -> float:
        """Simple text similarity (placeholder for real embedding similarity)"""
        text1_lower = text1.lower()
        text2_lower = text2.lower()

        # Count matching words
        words1 = set(text1_lower.split())
        words2 = set(text2_lower.split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union) if union else 0.0

    async def find_similar_reasoning_chains(
        self, current_chain: Dict[str, Any], limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Find similar reasoning chains based on structure and content"""
        with handle_errors("find_similar_reasoning_chains", logger=logger, include_performance=True):
            chain_ids = await self.memory_service.list_reasoning_chains()
            similar_chains = []

            for chain_id in chain_ids:
                chain = await self.memory_service.get_reasoning_chain(chain_id)
                if chain:
                    similarity = self._compute_chain_similarity(current_chain, chain)
                    if similarity > 0.5:  # Threshold
                        similar_chains.append({"chain": chain, "similarity": similarity, "chain_id": chain_id})

            # Sort by similarity and return top results
            similar_chains.sort(key=lambda x: x["similarity"], reverse=True)
            return similar_chains[:limit]

    def _compute_chain_similarity(self, chain1: Dict[str, Any], chain2: Dict[str, Any]) -> float:
        """Compute similarity between two reasoning chains"""
        # This is a simplified version
        # In production, you'd use more sophisticated methods

        score = 0.0
        total_weight = 0.0

        # Compare structure
        if chain1.get("type") == chain2.get("type"):
            score += 0.3
        total_weight += 0.3

        # Compare steps
        steps1 = chain1.get("steps", [])
        steps2 = chain2.get("steps", [])
        if steps1 and steps2:
            step_similarity = min(len(steps1), len(steps2)) / max(len(steps1), len(steps2))
            score += 0.4 * step_similarity
        total_weight += 0.4

        # Compare outcomes
        outcome1 = str(chain1.get("outcome", ""))
        outcome2 = str(chain2.get("outcome", ""))
        if outcome1 and outcome2:
            outcome_similarity = self._simple_similarity(outcome1, outcome2)
            score += 0.3 * outcome_similarity
        total_weight += 0.3

        return score / total_weight if total_weight > 0 else 0.0

    async def get_context_window(self, session_id: str, window_size: int = 5) -> List[Dict[str, Any]]:
        """Get recent context from session"""
        with handle_errors("get_context_window", logger=logger, include_performance=True):
            session = await self.memory_service.get_session(session_id)
            if not session:
                return []

            history = session.get("history", [])
            return history[-window_size:] if len(history) > window_size else history

    async def aggregate_knowledge(
        self, knowledge_types: List[str], tags: Optional[List[str]] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Aggregate knowledge from multiple sources"""
        with handle_errors("aggregate_knowledge", logger=logger, include_performance=True):
            aggregated = {}

            for k_type in knowledge_types:
                knowledge = await self.memory_service.retrieve_knowledge_by_type(k_type)

                # Filter by tags if provided
                if tags:
                    knowledge = [k for k in knowledge if any(tag in k.get("_tags", []) for tag in tags)]

                aggregated[k_type] = knowledge

            return aggregated


# Factory function for creating services
def create_redis_services(
    host: str = "localhost", port: int = 6379, password: Optional[str] = None, **kwargs
) -> tuple[RedisMemoryService, RedisRetrievalService]:
    """Create and return both Redis services"""
    with handle_errors("create_redis_services", logger=logger):
        memory_service = RedisMemoryService(host=host, port=port, password=password, **kwargs)
        retrieval_service = RedisRetrievalService(memory_service)

        return memory_service, retrieval_service
