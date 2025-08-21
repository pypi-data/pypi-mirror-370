"""
Redis Operations Reference Implementation
Example code showing all Redis operations used in MSA Reasoning Engine
"""

import redis
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib


class RedisSchemaOperations:
    """
    Reference implementation of Redis operations following the schema design
    """

    def __init__(self, redis_url: str):
        self.redis_client = redis.from_url(redis_url, decode_responses=True)

    # ============================================
    # REASONING CHAIN OPERATIONS
    # ============================================

    def store_reasoning_chain(
        self, chain_id: str, chain_data: Dict[str, Any], ttl: int = 3600
    ) -> bool:
        """Store a reasoning chain with automatic indexing"""
        try:
            # Primary storage
            key = f"reasoning_chain:{chain_id}"
            self.redis_client.setex(key, ttl, json.dumps(chain_data))

            # Add to global index
            self.redis_client.sadd("reasoning_chains", chain_id)

            # Add to session index if session_id exists
            if "session_id" in chain_data:
                session_key = f"session:{chain_data['session_id']}:chains"
                self.redis_client.sadd(session_key, chain_id)

            return True
        except Exception as e:
            print(f"Error storing reasoning chain: {e}")
            return False

    def get_reasoning_chain(self, chain_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a reasoning chain by ID"""
        key = f"reasoning_chain:{chain_id}"
        data = self.redis_client.get(key)
        return json.loads(data) if data else None

    def list_all_chains(self) -> List[str]:
        """List all reasoning chain IDs"""
        return list(self.redis_client.smembers("reasoning_chains"))

    # ============================================
    # KNOWLEDGE ENTITY OPERATIONS
    # ============================================

    def store_knowledge(
        self,
        knowledge_type: str,
        knowledge_id: str,
        data: Dict[str, Any],
        tags: List[str] = None,
        ttl: int = 86400,
    ) -> bool:
        """Store knowledge with type and tag indexing"""
        try:
            # Add metadata
            data["_type"] = knowledge_type
            data["_tags"] = tags or []
            data["_timestamp"] = datetime.now().isoformat()

            # Primary storage
            key = f"knowledge:{knowledge_type}:{knowledge_id}"
            self.redis_client.setex(key, ttl, json.dumps(data))

            # Type index
            self.redis_client.sadd(f"knowledge_type:{knowledge_type}", knowledge_id)

            # Tag indexes
            if tags:
                for tag in tags:
                    self.redis_client.sadd(
                        f"knowledge_tag:{tag}", f"{knowledge_type}:{knowledge_id}"
                    )

            return True
        except Exception as e:
            print(f"Error storing knowledge: {e}")
            return False

    def get_knowledge_by_type(self, knowledge_type: str) -> List[Dict[str, Any]]:
        """Retrieve all knowledge of a specific type"""
        results = []
        ids = self.redis_client.smembers(f"knowledge_type:{knowledge_type}")

        for kid in ids:
            key = f"knowledge:{knowledge_type}:{kid}"
            data = self.redis_client.get(key)
            if data:
                results.append(json.loads(data))

        return results

    def get_knowledge_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """Retrieve all knowledge with a specific tag"""
        results = []
        refs = self.redis_client.smembers(f"knowledge_tag:{tag}")

        for ref in refs:
            key = f"knowledge:{ref}"
            data = self.redis_client.get(key)
            if data:
                results.append(json.loads(data))

        return results

    # ============================================
    # SESSION OPERATIONS
    # ============================================

    def create_session(
        self, session_id: str, metadata: Dict[str, Any], ttl: int = 7200
    ) -> bool:
        """Create a new session"""
        try:
            session_data = {
                "metadata": metadata,
                "created_at": datetime.now().isoformat(),
                "last_accessed": datetime.now().isoformat(),
                "reasoning_chains": [],
                "status": "active",
            }

            key = f"session:{session_id}"
            self.redis_client.setex(key, ttl, json.dumps(session_data))

            # Add to active sessions
            self.redis_client.sadd("active_sessions", session_id)

            return True
        except Exception as e:
            print(f"Error creating session: {e}")
            return False

    def update_session_access(self, session_id: str) -> bool:
        """Update session last accessed time"""
        key = f"session:{session_id}"
        data = self.redis_client.get(key)

        if data:
            session_data = json.loads(data)
            session_data["last_accessed"] = datetime.now().isoformat()

            # Get current TTL and preserve it
            ttl = self.redis_client.ttl(key)
            if ttl > 0:
                self.redis_client.setex(key, ttl, json.dumps(session_data))
                return True

        return False

    # ============================================
    # MODEL CACHE OPERATIONS
    # ============================================

    def cache_model_result(
        self,
        model_name: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        ttl: int = 1800,
    ) -> bool:
        """Cache model inference results"""
        try:
            # Create hash of input for key
            input_hash = hashlib.sha256(
                json.dumps(input_data, sort_keys=True).encode()
            ).hexdigest()

            cache_data = {
                "input": input_data,
                "output": output_data,
                "model_version": "1.0",
                "inference_time_ms": 0,  # Would be calculated in real implementation
                "cached_at": datetime.now().isoformat(),
            }

            key = f"model_cache:{model_name}:{input_hash}"
            self.redis_client.setex(key, ttl, json.dumps(cache_data))

            return True
        except Exception as e:
            print(f"Error caching model result: {e}")
            return False

    def get_cached_model_result(
        self, model_name: str, input_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Retrieve cached model result"""
        input_hash = hashlib.sha256(
            json.dumps(input_data, sort_keys=True).encode()
        ).hexdigest()
        key = f"model_cache:{model_name}:{input_hash}"

        data = self.redis_client.get(key)
        return json.loads(data) if data else None

    # ============================================
    # SEARCH OPERATIONS
    # ============================================

    def semantic_search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Perform semantic search across knowledge entities using vector similarity.
        Production implementation should use RediSearch with vector indexing for better performance.
        """
        results = []
        cursor = 0

        while True:
            cursor, keys = self.redis_client.scan(
                cursor, match="knowledge:*", count=100
            )

            for key in keys:
                data = self.redis_client.get(key)
                if data:
                    knowledge = json.loads(data)
                    # Simple relevance check (would use embeddings in production)
                    if query.lower() in json.dumps(knowledge).lower():
                        results.append(knowledge)
                        if len(results) >= limit:
                            return results

            if cursor == 0:
                break

        return results

    # ============================================
    # MAINTENANCE OPERATIONS
    # ============================================

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get Redis memory statistics"""
        info = self.redis_client.info("memory")
        return {
            "used_memory_human": info.get("used_memory_human"),
            "used_memory_peak_human": info.get("used_memory_peak_human"),
            "memory_fragmentation_ratio": info.get("mem_fragmentation_ratio"),
            "total_keys": self.redis_client.dbsize(),
        }

    def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions from active set"""
        active_sessions = self.redis_client.smembers("active_sessions")
        removed = 0

        for session_id in active_sessions:
            key = f"session:{session_id}"
            if not self.redis_client.exists(key):
                self.redis_client.srem("active_sessions", session_id)
                removed += 1

        return removed

    def rebuild_indexes(self) -> Dict[str, int]:
        """Rebuild all indexes from existing data"""
        stats = {"knowledge_types": 0, "knowledge_tags": 0, "reasoning_chains": 0}

        # Clear existing indexes
        for key in self.redis_client.scan_iter("knowledge_type:*"):
            self.redis_client.delete(key)
        for key in self.redis_client.scan_iter("knowledge_tag:*"):
            self.redis_client.delete(key)
        self.redis_client.delete("reasoning_chains")

        # Rebuild from data
        for key in self.redis_client.scan_iter("knowledge:*"):
            data = json.loads(self.redis_client.get(key))
            parts = key.split(":")
            if len(parts) >= 3:
                knowledge_type = parts[1]
                knowledge_id = parts[2]

                # Rebuild type index
                self.redis_client.sadd(f"knowledge_type:{knowledge_type}", knowledge_id)
                stats["knowledge_types"] += 1

                # Rebuild tag indexes
                for tag in data.get("_tags", []):
                    self.redis_client.sadd(
                        f"knowledge_tag:{tag}", f"{knowledge_type}:{knowledge_id}"
                    )
                    stats["knowledge_tags"] += 1

        # Rebuild reasoning chain index
        for key in self.redis_client.scan_iter("reasoning_chain:*"):
            chain_id = key.split(":", 1)[1]
            self.redis_client.sadd("reasoning_chains", chain_id)
            stats["reasoning_chains"] += 1

        return stats


# Example usage
if __name__ == "__main__":
    # Initialize with Redis URL
    redis_ops = RedisSchemaOperations("redis://localhost:6379")

    # Store a reasoning chain
    chain_data = {
        "session_id": "session_123",
        "scenario": "Test scenario",
        "mode1_output": {
            "entities": ["entity1", "entity2"],
            "relationships": ["rel1", "rel2"],
        },
        "timestamp": datetime.now().isoformat(),
    }
    redis_ops.store_reasoning_chain("chain_001", chain_data)

    # Store knowledge with tags
    knowledge_data = {
        "name": "Bayesian Networks",
        "description": "Probabilistic graphical models",
        "domain": "machine_learning",
    }
    redis_ops.store_knowledge(
        "concept",
        "bayesian_networks",
        knowledge_data,
        tags=["ml", "statistics", "probability"],
    )

    # Retrieve by type
    concepts = redis_ops.get_knowledge_by_type("concept")
    print(f"Found {len(concepts)} concepts")

    # Get memory stats
    stats = redis_ops.get_memory_stats()
    print(f"Memory usage: {stats}")
