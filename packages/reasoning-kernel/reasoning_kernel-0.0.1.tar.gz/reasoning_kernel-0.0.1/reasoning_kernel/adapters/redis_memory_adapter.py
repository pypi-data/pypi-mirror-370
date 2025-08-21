"""
Redis Memory Adapter for Semantic Kernel MemoryStoreBase

This adapter bridges our RedisVectorService to the Semantic Kernel
memory system, implementing the MemoryStoreBase interface.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from reasoning_kernel.services.redis_vector_service import RedisVectorService
from semantic_kernel.memory.memory_record import MemoryRecord
from semantic_kernel.memory.memory_store_base import MemoryStoreBase


logger = logging.getLogger(__name__)


class RedisMemoryAdapter(MemoryStoreBase):
    """
    Redis-backed memory store adapter for Semantic Kernel.

    Implements MemoryStoreBase interface using RedisVectorService
    for persistent, distributed memory storage.
    """

    def __init__(self, redis_vector_service: RedisVectorService):
        """
        Initialize with Redis vector service.

        Args:
            redis_vector_service: Initialized RedisVectorService instance
        """
        self.redis_service = redis_vector_service
        self._collections: Dict[str, str] = {}
        self._initialized = False

    async def _ensure_initialized(self):
        """Ensure Redis service is initialized"""
        if not self._initialized:
            await self.redis_service.initialize()
            self._initialized = True

    # MemoryStoreBase interface implementation

    async def create_collection(self, collection_name: str) -> None:
        """
        Create a memory collection.

        Args:
            collection_name: Name of the collection to create
        """
        await self._ensure_initialized()

        try:
            # Map collection name to Redis collection type
            # Default to reasoning patterns for general memory
            redis_collection_key = self._get_redis_collection_key(collection_name)
            self._collections[collection_name] = redis_collection_key

            logger.info(f"Created memory collection: {collection_name}")

        except Exception as e:
            logger.error(f"Failed to create collection {collection_name}: {e}")
            raise

    async def does_collection_exist(self, collection_name: str) -> bool:
        """
        Check if collection exists.

        Args:
            collection_name: Name of the collection to check

        Returns:
            True if collection exists
        """
        await self._ensure_initialized()

        try:
            # Check if we have this collection registered
            return collection_name in self._collections

        except Exception as e:
            logger.error(f"Failed to check collection existence {collection_name}: {e}")
            return False

    async def delete_collection(self, collection_name: str) -> None:
        """
        Delete a memory collection.

        Args:
            collection_name: Name of the collection to delete
        """
        await self._ensure_initialized()

        try:
            if collection_name in self._collections:
                # Note: RedisVectorService doesn't have explicit collection deletion
                # Collections are managed at the Redis level
                del self._collections[collection_name]
                logger.info(f"Deleted memory collection: {collection_name}")

        except Exception as e:
            logger.error(f"Failed to delete collection {collection_name}: {e}")
            raise

    async def upsert(self, collection_name: str, record: MemoryRecord) -> str:
        """
        Upsert a memory record.

        Args:
            collection_name: Name of the collection
            record: MemoryRecord to store

        Returns:
            The record ID
        """
        await self._ensure_initialized()

        try:
            # Ensure collection exists
            if not await self.does_collection_exist(collection_name):
                await self.create_collection(collection_name)

            # Convert MemoryRecord to our storage format
            record_data = self._memory_record_to_storage_data(record, collection_name)

            # Store using RedisVectorService
            redis_collection_key = self._collections.get(collection_name, "reasoning")

            if redis_collection_key == "reasoning":
                # Store as reasoning pattern
                stored_id = await self.redis_service.store_reasoning_pattern(
                    pattern_type=record_data.get("pattern_type", "memory"),
                    question=record_data.get("question", record.text or ""),
                    reasoning_steps=record_data.get("reasoning_steps", ""),
                    final_answer=record_data.get("final_answer", record.text or ""),
                    confidence_score=record_data.get("confidence_score", 1.0),
                    context=record_data.get("context", {}),
                )
            else:
                # For other collection types, use generic storage
                # This would need to be extended based on specific needs
                stored_id = await self._store_generic_record(record, collection_name)

            logger.debug(f"Upserted record {record.id} to {collection_name}")
            return stored_id

        except Exception as e:
            logger.error(f"Failed to upsert record in {collection_name}: {e}")
            raise

    async def get(self, collection_name: str, key: str, with_embedding: bool) -> MemoryRecord:
        """
        Get a memory record by key.

        Args:
            collection_name: Name of the collection
            key: Record key/ID
            with_embedding: Whether to include embeddings

        Returns:
            MemoryRecord instance
        """
        await self._ensure_initialized()

        try:
            # Get from Redis using the correct collection mapping
            redis_collection_key = self._collections.get(collection_name, "reasoning")

            # Use get_by_id method from RedisVectorService
            record = await self.redis_service.get_by_id(redis_collection_key, key)
            if record:
                return self._storage_data_to_memory_record(record, with_embedding)

            # Record not found
            raise KeyError(f"Record {key} not found in collection {collection_name}")

        except KeyError:
            raise
        except Exception as e:
            logger.error(f"Failed to get record {key} from {collection_name}: {e}")
            raise

    async def remove(self, collection_name: str, key: str) -> None:
        """
        Remove a memory record.

        Args:
            collection_name: Name of the collection
            key: Record key/ID to remove
        """
        await self._ensure_initialized()

        try:
            redis_collection_key = self._collections.get(collection_name, "reasoning")

            # Use delete_by_id method from RedisVectorService
            success = await self.redis_service.delete_by_id(redis_collection_key, key)
            if not success:
                logger.warning(f"Record {key} not found for removal in {collection_name}")

            logger.debug(f"Removed record {key} from {collection_name}")

        except Exception as e:
            logger.error(f"Failed to remove record {key} from {collection_name}: {e}")
            raise

    async def get_nearest_matches(
        self, collection_name: str, embedding: np.ndarray, limit: int, min_relevance_score: float, with_embeddings: bool
    ) -> List[Tuple[MemoryRecord, float]]:
        """
        Get nearest matching records by embedding similarity.

        Args:
            collection_name: Name of the collection
            embedding: Query embedding vector
            limit: Maximum number of results
            min_relevance_score: Minimum similarity score
            with_embeddings: Whether to include embeddings

        Returns:
            List of (MemoryRecord, similarity_score) tuples
        """
        await self._ensure_initialized()

        try:
            redis_collection_key = self._collections.get(collection_name, "reasoning")

            # Use similarity_search method from RedisVectorService
            # Convert embedding to text for search (this is a limitation we'll work with for now)
            query_text = f"embedding_search_{collection_name}"
            results = await self.redis_service.similarity_search(
                collection_name=redis_collection_key, query_text=query_text, limit=limit
            )

            # Convert results to memory records with scores
            memory_results = []
            for i, record in enumerate(results):
                if record:
                    memory_record = self._storage_data_to_memory_record(record, with_embeddings)
                    # For now, use a simple score based on order
                    score = max(min_relevance_score, 1.0 - (i * 0.1))
                    if score >= min_relevance_score:
                        memory_results.append((memory_record, score))

            return memory_results[:limit]

        except Exception as e:
            logger.error(f"Failed to get nearest matches in {collection_name}: {e}")
            raise

    async def get_nearest_match(
        self, collection_name: str, embedding: np.ndarray, min_relevance_score: float, with_embedding: bool
    ) -> Tuple[MemoryRecord, float]:
        """
        Get the single nearest matching record by embedding similarity.

        Args:
            collection_name: Name of the collection
            embedding: Query embedding vector
            min_relevance_score: Minimum similarity score
            with_embedding: Whether to include embeddings

        Returns:
            Tuple of (MemoryRecord, similarity_score)
        """
        matches = await self.get_nearest_matches(
            collection_name=collection_name,
            embedding=embedding,
            limit=1,
            min_relevance_score=min_relevance_score,
            with_embeddings=with_embedding,
        )

        if matches:
            return matches[0]
        else:
            raise KeyError(f"No matching records found in collection {collection_name}")

    async def get_collections(self) -> List[str]:
        """
        Get list of all collection names.

        Returns:
            List of collection names
        """
        await self._ensure_initialized()
        return list(self._collections.keys())

    async def get_batch(self, collection_name: str, keys: List[str], with_embeddings: bool) -> List[MemoryRecord]:
        """
        Get multiple records by keys.

        Args:
            collection_name: Name of the collection
            keys: List of record keys
            with_embeddings: Whether to include embeddings

        Returns:
            List of MemoryRecord instances
        """
        await self._ensure_initialized()

        results = []
        for key in keys:
            try:
                record = await self.get(collection_name, key, with_embeddings)
                results.append(record)
            except KeyError:
                # Skip missing records
                continue

        return results

    async def remove_batch(self, collection_name: str, keys: List[str]) -> None:
        """
        Remove multiple records.

        Args:
            collection_name: Name of the collection
            keys: List of record keys to remove
        """
        await self._ensure_initialized()

        for key in keys:
            try:
                await self.remove(collection_name, key)
            except Exception as e:
                logger.warning(f"Failed to remove key {key}: {e}")

    async def upsert_batch(self, collection_name: str, records: List[MemoryRecord]) -> List[str]:
        """
        Upsert multiple records.

        Args:
            collection_name: Name of the collection
            records: List of MemoryRecord instances

        Returns:
            List of record IDs
        """
        await self._ensure_initialized()

        results = []
        for record in records:
            try:
                record_id = await self.upsert(collection_name, record)
                results.append(record_id)
            except Exception as e:
                logger.error(f"Failed to upsert record {record.id}: {e}")
                results.append("")

        return results

    async def close(self) -> None:
        """Close the memory store connection."""
        # RedisVectorService handles its own connection management
        logger.info("Closed RedisMemoryAdapter")

    # Helper methods

    def _get_redis_collection_key(self, collection_name: str) -> str:
        """Map collection name to Redis collection type."""
        # Map semantic kernel collection names to our Redis collections
        mapping = {
            "reasoning": "reasoning",
            "world_models": "world_models",
            "exploration": "explorations",
            "patterns": "reasoning",  # Default patterns to reasoning
        }

        # Check if collection name matches any mapping
        for key, redis_key in mapping.items():
            if key in collection_name.lower():
                return redis_key

        # Default to reasoning collection
        return "reasoning"

    def _memory_record_to_storage_data(self, record: MemoryRecord, collection_name: str) -> Dict[str, Any]:
        """Convert MemoryRecord to storage format."""

        # Extract additional metadata (handle both dict and str cases)
        metadata = record.additional_metadata
        if isinstance(metadata, str):
            # If it's a string, create a simple dict
            metadata_dict = {"raw_metadata": metadata}
        elif isinstance(metadata, dict):
            metadata_dict = metadata
        else:
            metadata_dict = {}

        return {
            "id": record.id,
            "text": record.text or "",
            "description": record.description or "",
            "pattern_type": metadata_dict.get("pattern_type", "semantic_memory"),
            "question": record.text or record.description or "",
            "reasoning_steps": metadata_dict.get("reasoning_steps", ""),
            "final_answer": record.text or "",
            "confidence_score": metadata_dict.get("confidence_score", 1.0),
            "context": {
                "collection": collection_name,
                "timestamp": record.timestamp.isoformat() if record.timestamp else datetime.now().isoformat(),
                **metadata_dict,
            },
            "embedding": record.embedding.tolist() if record.embedding is not None else None,
        }

    def _storage_data_to_memory_record(self, storage_data: Dict[str, Any], with_embedding: bool) -> MemoryRecord:
        """Convert storage format to MemoryRecord."""

        # Handle both dict and object formats
        if hasattr(storage_data, "__dict__"):
            data = storage_data.__dict__
        else:
            data = storage_data

        # Extract embedding if needed
        embedding = None
        if with_embedding and "embedding" in data and data["embedding"]:
            if isinstance(data["embedding"], list):
                embedding = np.array(data["embedding"], dtype=np.float32)
            else:
                embedding = data["embedding"]

        # Create MemoryRecord with required parameters
        return MemoryRecord(
            is_reference=False,
            external_source_name="redis_vector_service",
            id=data.get("id", data.get("pattern_id", "")),
            text=data.get("text", data.get("final_answer", "")),
            description=data.get("description", ""),
            additional_metadata=str(data.get("context", {})),
            embedding=embedding,
            timestamp=(
                datetime.fromisoformat(data.get("created_at", datetime.now().isoformat()).replace("Z", "+00:00"))
                if "created_at" in data
                else datetime.now()
            ),
        )

    async def _store_generic_record(self, record: MemoryRecord, collection_name: str) -> str:
        """Store record in a generic way for non-reasoning collections."""
        # For now, fallback to reasoning storage
        # This could be extended for specific collection types
        record_data = self._memory_record_to_storage_data(record, collection_name)

        return await self.redis_service.store_reasoning_pattern(
            pattern_type=record_data.get("pattern_type", "generic"),
            question=record_data.get("question", ""),
            reasoning_steps=record_data.get("reasoning_steps", ""),
            final_answer=record_data.get("final_answer", ""),
            confidence_score=record_data.get("confidence_score", 1.0),
            context=record_data.get("context", {}),
        )

    async def _get_generic_record(self, collection_name: str, key: str, with_embedding: bool) -> Optional[MemoryRecord]:
        """Get record in a generic way for non-reasoning collections."""
        # Use get_by_id from RedisVectorService
        redis_collection_key = self._collections.get(collection_name, "reasoning")
        record = await self.redis_service.get_by_id(redis_collection_key, key)
        if record:
            return self._storage_data_to_memory_record(record, with_embedding)
        return None

    async def _remove_generic_record(self, collection_name: str, key: str) -> None:
        """Remove record in a generic way for non-reasoning collections."""
        # Use delete_by_id from RedisVectorService
        redis_collection_key = self._collections.get(collection_name, "reasoning")
        await self.redis_service.delete_by_id(redis_collection_key, key)

    async def _get_nearest_matches_generic(
        self, collection_name: str, embedding: np.ndarray, limit: int, min_relevance_score: float, with_embeddings: bool
    ) -> List[Tuple[MemoryRecord, float]]:
        """Get nearest matches in a generic way for non-reasoning collections."""
        # Use similarity_search from RedisVectorService
        redis_collection_key = self._collections.get(collection_name, "reasoning")
        query_text = f"embedding_search_{collection_name}"
        results = await self.redis_service.similarity_search(
            collection_name=redis_collection_key, query_text=query_text, limit=limit
        )

        memory_results = []
        for i, record in enumerate(results):
            if record:
                memory_record = self._storage_data_to_memory_record(record, with_embeddings)
                # Simple score based on order
                score = max(min_relevance_score, 1.0 - (i * 0.1))
                if score >= min_relevance_score:
                    memory_results.append((memory_record, score))

        return memory_results[:limit]
