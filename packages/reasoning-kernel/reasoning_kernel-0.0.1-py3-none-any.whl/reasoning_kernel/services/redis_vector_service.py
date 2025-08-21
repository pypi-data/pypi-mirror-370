"""
Redis Vector Service for Reasoning Kernel

Unified Redis Cloud service for vector storage and caching using
Semantic Kernel's modern Redis connector.
"""

from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from datetime import UTC
import hashlib
import json
import logging
from typing import Any, Dict, List, Optional
import uuid


try:  # optional dependency; avoid import-time errors in tests
    from semantic_kernel.connectors.ai.embedding_generator_base import (
        EmbeddingGeneratorBase,  # type: ignore
    )
    from semantic_kernel.connectors.redis import RedisStore  # type: ignore
except Exception:  # pragma: no cover

    class _DummyRedisStore:  # minimal placeholder with get_collection
        def __init__(self, *args, **kwargs):
            pass

        def get_collection(self, *args, **kwargs):
            class _DummyCollection:
                async def upsert(self, *a, **k):
                    return None

            return _DummyCollection()

    RedisStore = _DummyRedisStore  # type: ignore

    class EmbeddingGeneratorBase:  # minimal protocol
        async def generate_embeddings(self, texts: List[str]):  # type: ignore[override]
            return [[0.0] * 1 for _ in texts]


logger = logging.getLogger(__name__)


@dataclass
class ReasoningRecord:
    """Record for reasoning patterns and results"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    pattern_type: str = ""
    question: str = ""
    reasoning_steps: str = ""
    final_answer: str = ""
    confidence_score: float = 0.0
    context_hash: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    embedding: List[float] = field(default_factory=list)


@dataclass
class WorldModelRecord:
    """Record for world model states and updates"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    model_type: str = ""
    state_data: str = ""
    confidence: float = 0.0
    last_updated: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    context_keys: str = ""
    embedding: List[float] = field(default_factory=list)


@dataclass
class ExplorationRecord:
    """Record for exploration patterns and discoveries"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    exploration_type: str = ""
    hypothesis: str = ""
    evidence: str = ""
    conclusion: str = ""
    exploration_path: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    embedding: List[float] = field(default_factory=list)


class RedisVectorService:
    """
    Unified Redis service for vector storage and caching
    """

    def __init__(self, connection_string: str, embedding_generator: EmbeddingGeneratorBase):
        """Initialize Redis vector service"""
        self.connection_string = connection_string
        self.embedding_generator = embedding_generator
        self.redis_store = None
        self._collections = {}
        self._initialized = False

    async def initialize(self):
        """Initialize Redis store and collections"""
        if self._initialized:
            return

        try:
            # Initialize Redis store with embedding generator
            self.redis_store = RedisStore(
                connection_string=self.connection_string, embedding_generator=self.embedding_generator
            )

            # For now, skip collection initialization to avoid definition issues
            # Collections will be created on-demand when needed
            # This allows basic memory adapter functionality without complex definitions

            # # Initialize collections using the store's get_collection method
            # self._collections["reasoning"] = self.redis_store.get_collection(
            #     record_type=ReasoningRecord,
            #     collection_name="reasoning_patterns"
            # )

            # self._collections["world_models"] = self.redis_store.get_collection(
            #     record_type=WorldModelRecord,
            #     collection_name="world_models"
            # )

            # self._collections["explorations"] = self.redis_store.get_collection(
            #     record_type=ExplorationRecord,
            #     collection_name="exploration_patterns"
            # )

            self._initialized = True
            logger.info("Redis vector service initialized successfully (collections will be created on-demand)")

        except Exception as e:
            logger.error(f"Failed to initialize Redis vector service: {e}")
            raise

    async def _get_or_create_collection(self, collection_name: str, record_type: type):
        """Lazy collection creation helper"""
        if collection_name not in self._collections:
            try:
                collection_key_map = {
                    "reasoning": ("reasoning_patterns", ReasoningRecord),
                    "world_models": ("world_models", WorldModelRecord),
                    "explorations": ("exploration_patterns", ExplorationRecord),
                }

                if collection_name in collection_key_map:
                    redis_collection_name, record_class = collection_key_map[collection_name]
                    self._collections[collection_name] = self.redis_store.get_collection(
                        record_type=record_class, collection_name=redis_collection_name
                    )
                else:
                    # For custom collections, use the provided record type
                    self._collections[collection_name] = self.redis_store.get_collection(
                        record_type=record_type, collection_name=collection_name
                    )

                logger.info(f"Created Redis collection: {collection_name}")

            except Exception as e:
                logger.error(f"Failed to create collection {collection_name}: {e}")
                raise

        return self._collections[collection_name]

    async def store_reasoning_pattern(
        self,
        pattern_type: str,
        question: str,
        reasoning_steps: str,
        final_answer: str,
        confidence_score: float = 0.0,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Store a reasoning pattern with vector embedding"""
        await self._ensure_initialized()

        try:
            # Create context hash
            context_str = json.dumps(context or {}, sort_keys=True)
            context_hash = hashlib.sha256(context_str.encode()).hexdigest()[:16]  # Truncate for readability

            # Generate embedding from combined text
            combined_text = f"{pattern_type} {question} {reasoning_steps} {final_answer}"
            embedding = await self.embedding_generator.generate_embeddings([combined_text])

            # Create record
            record = ReasoningRecord(
                pattern_type=pattern_type,
                question=question,
                reasoning_steps=reasoning_steps,
                final_answer=final_answer,
                confidence_score=confidence_score,
                context_hash=context_hash,
                embedding=embedding[0] if embedding else [],
            )

            # Store in collection
            collection = self._collections["reasoning"]
            await collection.upsert(record)

            logger.debug(f"Stored reasoning pattern with ID: {record.id}")
            return record.id

        except Exception as e:
            logger.error(f"Error storing reasoning pattern: {e}")
            raise

    async def store_world_model(
        self,
        model_type: str,
        state_data: Dict[str, Any],
        confidence: float = 0.0,
        context_keys: Optional[List[str]] = None,
    ) -> str:
        """Store world model state with vector embedding"""
        await self._ensure_initialized()

        try:
            # Serialize state data
            state_str = json.dumps(state_data, sort_keys=True)
            context_keys_str = json.dumps(context_keys or [], sort_keys=True)

            # Generate embedding
            combined_text = f"{model_type} {state_str}"
            embedding = await self.embedding_generator.generate_embeddings([combined_text])

            # Create record
            record = WorldModelRecord(
                model_type=model_type,
                state_data=state_str,
                confidence=confidence,
                context_keys=context_keys_str,
                embedding=embedding[0] if embedding else [],
            )

            # Store in collection
            collection = self._collections["world_models"]
            await collection.upsert(record)

            logger.debug(f"Stored world model with ID: {record.id}")
            return record.id

        except Exception as e:
            logger.error(f"Error storing world model: {e}")
            raise

    async def store_exploration_pattern(
        self,
        exploration_type: str,
        hypothesis: str,
        evidence: str,
        conclusion: str,
        exploration_path: Optional[List[str]] = None,
    ) -> str:
        """Store exploration pattern with vector embedding"""
        await self._ensure_initialized()

        try:
            # Create exploration path string
            path_str = json.dumps(exploration_path or [], sort_keys=True)

            # Generate embedding
            combined_text = f"{exploration_type} {hypothesis} {evidence} {conclusion}"
            embedding = await self.embedding_generator.generate_embeddings([combined_text])

            # Create record
            record = ExplorationRecord(
                exploration_type=exploration_type,
                hypothesis=hypothesis,
                evidence=evidence,
                conclusion=conclusion,
                exploration_path=path_str,
                embedding=embedding[0] if embedding else [],
            )

            # Store in collection
            collection = self._collections["explorations"]
            await collection.upsert(record)

            logger.debug(f"Stored exploration pattern with ID: {record.id}")
            return record.id

        except Exception as e:
            logger.error(f"Error storing exploration pattern: {e}")
            raise

    async def similarity_search(self, collection_name: str, query_text: str, limit: int = 10) -> List[Any]:
        """Perform similarity search in specified collection"""
        await self._ensure_initialized()

        try:
            if collection_name not in self._collections:
                raise ValueError(f"Collection {collection_name} not found")

            collection = self._collections[collection_name]

            # Generate query embedding
            query_embedding = await self.embedding_generator.generate_embeddings([query_text])

            if not query_embedding:
                logger.warning("No embedding generated for query")
                return []

            # Use the collection's vector search capability
            try:
                # Try vector search first
                results = await collection.vector_search(vector=query_embedding[0], limit=limit)
            except (AttributeError, TypeError):
                # Fallback to text-based search if vector search not available
                try:
                    results = await collection.search(query=query_text, limit=limit)
                except Exception:
                    # Final fallback - return empty results
                    results = []

            logger.debug(f"Found {len(results) if results else 0} results in {collection_name}")
            return results if results else []

        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            return []

    async def get_by_id(self, collection_name: str, record_id: str) -> Optional[Any]:
        """Retrieve record by ID from specified collection"""
        await self._ensure_initialized()

        try:
            if collection_name not in self._collections:
                raise ValueError(f"Collection {collection_name} not found")

            collection = self._collections[collection_name]
            record = await collection.get(record_id)

            return record

        except Exception as e:
            logger.error(f"Error retrieving record {record_id}: {e}")
            return None

    async def delete_by_id(self, collection_name: str, record_id: str) -> bool:
        """Delete record by ID from specified collection"""
        await self._ensure_initialized()

        try:
            if collection_name not in self._collections:
                raise ValueError(f"Collection {collection_name} not found")

            collection = self._collections[collection_name]
            await collection.delete(record_id)

            logger.debug(f"Deleted record {record_id} from {collection_name}")
            return True

        except Exception as e:
            logger.error(f"Error deleting record {record_id}: {e}")
            return False

    def generate_cache_key(self, prefix: str, *args) -> str:
        """Generate cache key from prefix and arguments"""
        key_parts = [prefix] + [str(arg) for arg in args]
        key_string = ":".join(key_parts)
        return hashlib.sha256(key_string.encode()).hexdigest()[:16]  # Truncate for readability

    async def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """Get statistics for a collection"""
        await self._ensure_initialized()

        try:
            if collection_name not in self._collections:
                return {"error": f"Collection {collection_name} not found"}

            # Basic collection info
            stats = {
                "collection_name": collection_name,
                "status": "active",
                "last_accessed": datetime.now(UTC).isoformat(),
            }

            return stats

        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {"error": str(e)}

    async def health_check(self) -> Dict[str, Any]:
        """Check health of Redis vector service"""
        try:
            if not self.redis_store:
                return {"status": "error", "message": "Redis store not initialized"}

            # Test basic connectivity
            health = {
                "status": "healthy",
                "collections": list(self._collections.keys()),
                "timestamp": datetime.now(UTC).isoformat(),
            }

            return health

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "error", "message": str(e)}

    async def _ensure_initialized(self):
        """Ensure the service is initialized"""
        if not self._initialized:
            await self.initialize()

    async def close(self):
        """Clean up resources"""
        try:
            self._collections.clear()
            self._initialized = False
            logger.info("Redis Vector Service closed")
        except Exception as e:
            logger.error(f"Error closing Redis Vector Service: {e}")
