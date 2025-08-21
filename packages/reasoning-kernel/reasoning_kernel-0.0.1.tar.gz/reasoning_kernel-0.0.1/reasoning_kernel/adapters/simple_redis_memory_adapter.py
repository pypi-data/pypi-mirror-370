"""
Simple Redis Memory Adapter for Semantic Kernel Memory Integration

This simplified adapter provides basic Redis memory functionality
without requiring complex collection definitions, specifically designed
to integrate SemanticTextMemory with Redis backend.
"""

from datetime import datetime
import json
import logging
from typing import Dict, List, Tuple

from semantic_kernel.memory.memory_record import MemoryRecord
from semantic_kernel.memory.memory_store_base import MemoryStoreBase


logger = logging.getLogger(__name__)


class SimpleRedisMemoryAdapter(MemoryStoreBase):
    """
    Simplified Redis-backed memory store for Semantic Kernel.

    Uses basic Redis operations to implement MemoryStoreBase interface
    without requiring complex collection definitions.
    """

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        """
        Initialize with Redis connection parameters.

        Args:
            redis_url: Redis connection URL
        """
        self.redis_url = redis_url
        self._redis_client = None
        self._collections: Dict[str, str] = {}
        self._initialized = False

    async def _ensure_initialized(self):
        """Ensure Redis client is initialized"""
        if not self._initialized:
            try:
                import redis.asyncio as redis

                self._redis_client = redis.from_url(self.redis_url, decode_responses=True)

                # Test connection
                await self._redis_client.ping()
                self._initialized = True
                logger.info("Simple Redis memory adapter initialized successfully")

            except ImportError:
                raise ImportError("redis package is required. Install with: pip install redis")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                raise

    async def _get_collection_key(self, collection_name: str) -> str:
        """Get Redis key prefix for collection"""
        return f"sk_memory:{collection_name}"

    async def _get_record_key(self, collection_name: str, record_id: str) -> str:
        """Get Redis key for specific record"""
        collection_key = await self._get_collection_key(collection_name)
        return f"{collection_key}:{record_id}"

    # MemoryStoreBase interface implementation

    async def create_collection(self, collection_name: str) -> None:
        """Create a memory collection (in Redis, this is just tracking)"""
        await self._ensure_initialized()

        try:
            # Register collection
            self._collections[collection_name] = await self._get_collection_key(collection_name)

            # Store collection metadata
            collection_key = await self._get_collection_key(collection_name)
            metadata = {"created_at": datetime.utcnow().isoformat(), "collection_name": collection_name}
            await self._redis_client.hset(f"{collection_key}:_meta", mapping=metadata)

            logger.info(f"Created memory collection: {collection_name}")

        except Exception as e:
            logger.error(f"Failed to create collection {collection_name}: {e}")
            raise

    async def does_collection_exist(self, collection_name: str) -> bool:
        """Check if collection exists"""
        await self._ensure_initialized()

        try:
            collection_key = await self._get_collection_key(collection_name)
            exists = await self._redis_client.exists(f"{collection_key}:_meta")
            return bool(exists)

        except Exception as e:
            logger.error(f"Failed to check collection existence {collection_name}: {e}")
            return False

    async def delete_collection(self, collection_name: str) -> None:
        """Delete a memory collection"""
        await self._ensure_initialized()

        try:
            if collection_name in self._collections:
                del self._collections[collection_name]

            # Delete all keys with this collection prefix
            collection_key = await self._get_collection_key(collection_name)
            pattern = f"{collection_key}*"

            cursor = 0
            while True:
                cursor, keys = await self._redis_client.scan(cursor, match=pattern, count=100)
                if keys:
                    await self._redis_client.delete(*keys)
                if cursor == 0:
                    break

            logger.info(f"Deleted memory collection: {collection_name}")

        except Exception as e:
            logger.error(f"Failed to delete collection {collection_name}: {e}")
            raise

    async def upsert(self, collection_name: str, record: MemoryRecord) -> str:
        """Upsert a memory record"""
        await self._ensure_initialized()

        try:
            # Ensure collection exists
            if not await self.does_collection_exist(collection_name):
                await self.create_collection(collection_name)

            # Serialize MemoryRecord
            record_data = {
                "id": record.id,
                "text": record.text or "",
                "description": record.description or "",
                "additional_metadata": record.additional_metadata or "",
                "external_source_name": record.external_source_name or "",
                "is_reference": str(record.is_reference),
                "timestamp": record.timestamp.isoformat() if record.timestamp else datetime.utcnow().isoformat(),
            }

            # Store embedding if present
            if record.embedding is not None:
                # Convert numpy array to list if needed
                if hasattr(record.embedding, "tolist"):
                    record_data["embedding"] = record.embedding.tolist()
                else:
                    record_data["embedding"] = list(record.embedding)

            # Store in Redis
            record_key = await self._get_record_key(collection_name, record.id)
            await self._redis_client.hset(record_key, mapping=record_data)

            logger.debug(f"Upserted record {record.id} to {collection_name}")
            return record.id

        except Exception as e:
            logger.error(f"Failed to upsert record in {collection_name}: {e}")
            raise

    async def get(self, collection_name: str, key: str, with_embedding: bool = False) -> MemoryRecord:
        """Get a memory record by key"""
        await self._ensure_initialized()

        try:
            record_key = await self._get_record_key(collection_name, key)
            record_data = await self._redis_client.hgetall(record_key)

            if not record_data:
                raise KeyError(f"Record {key} not found in collection {collection_name}")

            # Reconstruct MemoryRecord
            embedding = None
            if with_embedding and "embedding" in record_data:
                embedding = json.loads(record_data["embedding"])

            record = MemoryRecord(
                id=record_data["id"],
                text=record_data.get("text", ""),
                description=record_data.get("description", ""),
                additional_metadata=record_data.get("additional_metadata", ""),
                external_source_name=record_data.get("external_source_name", ""),
                is_reference=record_data.get("is_reference", "False").lower() == "true",
                embedding=embedding,
                timestamp=datetime.fromisoformat(record_data.get("timestamp", datetime.utcnow().isoformat())),
            )

            return record

        except KeyError:
            raise
        except Exception as e:
            logger.error(f"Failed to get record {key} from {collection_name}: {e}")
            raise

    async def remove(self, collection_name: str, key: str) -> None:
        """Remove a memory record"""
        await self._ensure_initialized()

        try:
            record_key = await self._get_record_key(collection_name, key)
            result = await self._redis_client.delete(record_key)

            if result == 0:
                logger.warning(f"Record {key} not found in collection {collection_name}")
            else:
                logger.debug(f"Removed record {key} from {collection_name}")

        except Exception as e:
            logger.error(f"Failed to remove record {key} from {collection_name}: {e}")
            raise

    async def get_batch(
        self, collection_name: str, keys: List[str], with_embeddings: bool = False
    ) -> List[MemoryRecord]:
        """Get multiple records"""
        await self._ensure_initialized()

        try:
            records = []
            for key in keys:
                try:
                    record = await self.get(collection_name, key, with_embeddings)
                    records.append(record)
                except KeyError:
                    # Skip missing records
                    continue

            return records

        except Exception as e:
            logger.error(f"Failed to get batch from {collection_name}: {e}")
            raise

    async def upsert_batch(self, collection_name: str, records: List[MemoryRecord]) -> List[str]:
        """Upsert multiple records"""
        await self._ensure_initialized()

        try:
            ids = []
            for record in records:
                record_id = await self.upsert(collection_name, record)
                ids.append(record_id)

            return ids

        except Exception as e:
            logger.error(f"Failed to upsert batch to {collection_name}: {e}")
            raise

    async def remove_batch(self, collection_name: str, keys: List[str]) -> None:
        """Remove multiple records"""
        await self._ensure_initialized()

        try:
            for key in keys:
                await self.remove(collection_name, key)

        except Exception as e:
            logger.error(f"Failed to remove batch from {collection_name}: {e}")
            raise

    async def get_nearest_match(
        self,
        collection_name: str,
        embedding: List[float],
        min_relevance_score: float = 0.0,
        with_embedding: bool = False,
    ) -> Tuple[MemoryRecord, float]:
        """Get single nearest match (required by MemoryStoreBase)"""
        matches = await self.get_nearest_matches(
            collection_name, embedding, limit=1, min_relevance_score=min_relevance_score, with_embeddings=with_embedding
        )

        if matches:
            return matches[0]
        else:
            raise ValueError(
                f"No matches found in collection {collection_name} with min_relevance_score {min_relevance_score}"
            )

    async def get_nearest_matches(
        self,
        collection_name: str,
        embedding: List[float],
        limit: int,
        min_relevance_score: float = 0.0,
        with_embeddings: bool = False,
    ) -> List[Tuple[MemoryRecord, float]]:
        """
        Get nearest matches using cosine similarity.

        Note: This is a simplified implementation that loads all records
        and computes similarity in Python. For production use with large
        datasets, consider using Redis modules like RediSearch with vector similarity.
        """
        await self._ensure_initialized()

        try:
            # Get all records in collection
            collection_key = await self._get_collection_key(collection_name)
            pattern = f"{collection_key}:*"

            cursor = 0
            all_records = []

            while True:
                cursor, keys = await self._redis_client.scan(cursor, match=pattern, count=100)
                for key in keys:
                    if not key.endswith(":_meta"):  # Skip metadata
                        try:
                            record_data = await self._redis_client.hgetall(key)
                            if record_data and "embedding" in record_data:
                                record_embedding = json.loads(record_data["embedding"])

                                # Calculate cosine similarity
                                similarity = self._cosine_similarity(embedding, record_embedding)

                                if similarity >= min_relevance_score:
                                    # Create MemoryRecord
                                    record = MemoryRecord(
                                        id=record_data["id"],
                                        text=record_data.get("text", ""),
                                        description=record_data.get("description", ""),
                                        additional_metadata=record_data.get("additional_metadata", ""),
                                        external_source_name=record_data.get("external_source_name", ""),
                                        is_reference=record_data.get("is_reference", "False").lower() == "true",
                                        embedding=record_embedding if with_embeddings else None,
                                        timestamp=datetime.fromisoformat(
                                            record_data.get("timestamp", datetime.utcnow().isoformat())
                                        ),
                                    )

                                    all_records.append((record, similarity))

                        except Exception as e:
                            logger.debug(f"Error processing record {key}: {e}")
                            continue

                if cursor == 0:
                    break

            # Sort by similarity and limit results
            all_records.sort(key=lambda x: x[1], reverse=True)
            return all_records[:limit]

        except Exception as e:
            logger.error(f"Failed to find nearest matches in {collection_name}: {e}")
            raise

    @staticmethod
    def _cosine_similarity(a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        import math

        if len(a) != len(b):
            return 0.0

        dot_product = sum(x * y for x, y in zip(a, b))
        magnitude_a = math.sqrt(sum(x * x for x in a))
        magnitude_b = math.sqrt(sum(x * x for x in b))

        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0

        return dot_product / (magnitude_a * magnitude_b)

    async def get_collections(self) -> List[str]:
        """Get list of available collections"""
        await self._ensure_initialized()

        try:
            collections = []
            pattern = "sk_memory:*:_meta"

            cursor = 0
            while True:
                cursor, keys = await self._redis_client.scan(cursor, match=pattern, count=100)
                for key in keys:
                    # Extract collection name from key
                    # Format: sk_memory:collection_name:_meta
                    parts = key.split(":")
                    if len(parts) >= 3:
                        collection_name = ":".join(parts[1:-1])  # Handle collection names with colons
                        collections.append(collection_name)

                if cursor == 0:
                    break

            return list(set(collections))  # Remove duplicates

        except Exception as e:
            logger.error(f"Failed to get collections: {e}")
            return []

    async def close(self):
        """Close Redis connection"""
        if self._redis_client:
            await self._redis_client.close()
            self._initialized = False
            logger.info("Redis connection closed")
