"""
Redis Integration for Thinking Exploration Framework
===================================================

Manages Redis storage for world models, exploration patterns, and memory integration
with TTL policies and embedding-based retrieval for the MSA framework.

TASK-006: Configure Redis collections for storing world models and exploration patterns
"""

from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from reasoning_kernel.core.exploration_triggers import ExplorationTrigger
from reasoning_kernel.core.exploration_triggers import TriggerDetectionResult
from reasoning_kernel.models.world_model import WorldModel
from reasoning_kernel.models.world_model import WorldModelLevel

from ..utils.datetime_utils import utc_now


logger = logging.getLogger(__name__)


@dataclass
class RedisCollectionConfig:
    """Configuration for Redis collections and storage policies"""

    # Collection names
    world_models_collection: str = "thinking_exploration:world_models"
    exploration_patterns_collection: str = "thinking_exploration:patterns"
    trigger_history_collection: str = "thinking_exploration:triggers"
    model_hierarchies_collection: str = "thinking_exploration:hierarchies"

    # TTL policies by model level (seconds)
    instance_model_ttl: int = 3600  # 1 hour
    category_model_ttl: int = 86400  # 1 day
    domain_model_ttl: int = 604800  # 1 week
    abstract_model_ttl: int = 2592000  # 1 month

    # Exploration pattern TTL
    pattern_ttl: int = 86400  # 1 day
    trigger_history_ttl: int = 604800  # 1 week

    # Vector search configuration
    embedding_dimension: int = 768
    similarity_threshold: float = 0.7
    max_search_results: int = 20

    # Storage limits
    max_models_per_domain: int = 1000
    max_patterns_per_trigger: int = 100

    def get_ttl_for_level(self, level: WorldModelLevel) -> int:
        """Get TTL based on world model level"""
        ttl_mapping = {
            WorldModelLevel.INSTANCE: self.instance_model_ttl,
            WorldModelLevel.CATEGORY: self.category_model_ttl,
            WorldModelLevel.DOMAIN: self.domain_model_ttl,
            WorldModelLevel.ABSTRACT: self.abstract_model_ttl,
        }
        return ttl_mapping.get(level, self.instance_model_ttl)


@dataclass
class ExplorationPattern:
    """Pattern extracted from exploration experiences"""

    pattern_id: str
    trigger_type: ExplorationTrigger
    scenario_hash: str
    success_rate: float
    strategy_used: str
    domain: str
    context_features: Dict[str, Any]
    created_at: datetime
    usage_count: int = 0
    last_used: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Redis storage"""
        return {
            "pattern_id": self.pattern_id,
            "trigger_type": self.trigger_type.name,
            "scenario_hash": self.scenario_hash,
            "success_rate": self.success_rate,
            "strategy_used": self.strategy_used,
            "domain": self.domain,
            "context_features": self.context_features,
            "created_at": self.created_at.isoformat(),
            "usage_count": self.usage_count,
            "last_used": self.last_used.isoformat() if self.last_used else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExplorationPattern":
        """Create from dictionary"""
        return cls(
            pattern_id=data["pattern_id"],
            trigger_type=ExplorationTrigger[data["trigger_type"]],
            scenario_hash=data["scenario_hash"],
            success_rate=data["success_rate"],
            strategy_used=data["strategy_used"],
            domain=data["domain"],
            context_features=data["context_features"],
            created_at=datetime.fromisoformat(data["created_at"]),
            usage_count=data.get("usage_count", 0),
            last_used=datetime.fromisoformat(data["last_used"]) if data.get("last_used") else None,
        )


class ThinkingExplorationRedisManager:
    """
    Redis manager for thinking exploration framework storage and retrieval.

    Handles world model storage, exploration pattern management, and
    hierarchical model relationships with appropriate TTL policies.
    """

    def __init__(self, redis_client, embeddings_service=None, config: Optional[RedisCollectionConfig] = None):
        self.redis = redis_client
        self.embeddings_service = embeddings_service
        self.config = config or RedisCollectionConfig()

        # Initialize collections
        self._initialize_collections()
        logger.info("ThinkingExplorationRedisManager initialized")

    def _initialize_collections(self):
        """Initialize Redis collections and indexes"""
        try:
            # Create collection metadata
            collections_info = {
                "world_models": {
                    "description": "Hierarchical world models for thinking exploration",
                    "created": utc_now().isoformat(),
                    "index_fields": ["model_level", "domain", "tags", "confidence_score"],
                },
                "exploration_patterns": {
                    "description": "Successful exploration patterns and strategies",
                    "created": utc_now().isoformat(),
                    "index_fields": ["trigger_type", "domain", "success_rate"],
                },
                "trigger_history": {
                    "description": "History of trigger detection results",
                    "created": utc_now().isoformat(),
                    "index_fields": ["triggers", "priority", "timestamp"],
                },
            }

            # Store collection metadata
            for name, info in collections_info.items():
                key = f"thinking_exploration:collections:{name}"
                self.redis.hset(key, mapping=info)
                self.redis.expire(key, self.config.abstract_model_ttl)

            logger.info("Redis collections initialized")
        except Exception as e:
            logger.error(f"Failed to initialize collections: {e}")

    async def store_world_model(self, model: WorldModel) -> bool:
        """Store world model with appropriate TTL and indexing"""
        try:
            # Get TTL based on model level
            ttl = self.config.get_ttl_for_level(model.model_level)

            # Store main model data
            model_key = f"{self.config.world_models_collection}:{model.model_id}"
            model_data = model.to_json()

            # Store model
            await self.redis.setex(model_key, ttl, model_data)

            # Add to level-specific index
            level_index_key = f"{self.config.world_models_collection}:level:{model.model_level.name.lower()}"
            await self.redis.sadd(level_index_key, model.model_id)
            await self.redis.expire(level_index_key, ttl)

            # Add to domain index
            domain_index_key = f"{self.config.world_models_collection}:domain:{model.domain}"
            await self.redis.sadd(domain_index_key, model.model_id)
            await self.redis.expire(domain_index_key, ttl)

            # Store tags index
            for tag in model.tags:
                tag_index_key = f"{self.config.world_models_collection}:tag:{tag}"
                await self.redis.sadd(tag_index_key, model.model_id)
                await self.redis.expire(tag_index_key, ttl)

            # Store hierarchical relationships
            await self._store_model_relationships(model)

            # Store embedding if available
            if self.embeddings_service and model.context_description:
                await self._store_model_embedding(model)

            logger.info(f"Stored world model {model.model_id} with TTL {ttl}s")
            return True

        except Exception as e:
            sanitized_model_id = model.model_id.replace("\r", "").replace("\n", "")
            logger.error(f"Failed to store world model {sanitized_model_id}: {e}")
            return False

    async def _store_model_relationships(self, model: WorldModel):
        """Store hierarchical relationships between models"""
        try:
            # Store parent relationships
            for parent_id in model.parent_models:
                parent_key = f"{self.config.model_hierarchies_collection}:parents:{model.model_id}"
                await self.redis.sadd(parent_key, parent_id)
                await self.redis.expire(parent_key, self.config.domain_model_ttl)

                # Reverse relationship - children
                child_key = f"{self.config.model_hierarchies_collection}:children:{parent_id}"
                await self.redis.sadd(child_key, model.model_id)
                await self.redis.expire(child_key, self.config.domain_model_ttl)

            # Store similar model relationships
            for similar_id, similarity_score in model.similar_models:
                similarity_key = f"{self.config.model_hierarchies_collection}:similar:{model.model_id}"
                await self.redis.zadd(similarity_key, {similar_id: similarity_score})
                await self.redis.expire(similarity_key, self.config.category_model_ttl)

        except Exception as e:
            logger.error(f"Failed to store model relationships: {e}")

    async def _store_model_embedding(self, model: WorldModel):
        """Store model embedding for semantic search"""
        try:
            if not self.embeddings_service:
                return

            # Generate embedding for model context
            text_to_embed = f"{model.context_description} {' '.join(model.applicable_situations[:3])}"
            embedding = await self._generate_embedding(text_to_embed)

            if embedding is not None:
                # Store embedding as vector
                embedding_key = f"{self.config.world_models_collection}:embeddings:{model.model_id}"
                embedding_data = {
                    "vector": embedding.tolist(),
                    "text": text_to_embed,
                    "model_id": model.model_id,
                    "model_level": model.model_level.name,
                    "domain": model.domain,
                    "confidence": model.confidence_score,
                }

                await self.redis.setex(
                    embedding_key, self.config.get_ttl_for_level(model.model_level), json.dumps(embedding_data)
                )

                # Add to embedding index
                embedding_index_key = f"{self.config.world_models_collection}:embeddings:index"
                await self.redis.sadd(embedding_index_key, model.model_id)

        except Exception as e:
            logger.error(f"Failed to store model embedding: {e}")

    async def retrieve_world_model(self, model_id: str) -> Optional[WorldModel]:
        """Retrieve world model by ID"""
        try:
            model_key = f"{self.config.world_models_collection}:{model_id}"
            model_data = await self.redis.get(model_key)

            if model_data:
                return WorldModel.from_json(model_data.decode("utf-8"))
            return None

        except Exception as e:
            sanitized_model_id = model_id.replace("\r", "").replace("\n", "")
            logger.error(f"Failed to retrieve world model {sanitized_model_id}: {e}")
            return None

    async def search_similar_models(
        self,
        query_text: str,
        domain: Optional[str] = None,
        model_level: Optional[WorldModelLevel] = None,
        limit: int = 10,
    ) -> List[Tuple[WorldModel, float]]:
        """Search for similar world models using embedding similarity"""
        try:
            if not self.embeddings_service:
                logger.warning("No embeddings service available for similarity search")
                return []

            # Generate query embedding
            query_embedding = await self._generate_embedding(query_text)
            if query_embedding is None:
                return []

            # Get all embedding keys
            embedding_index_key = f"{self.config.world_models_collection}:embeddings:index"
            model_ids = await self.redis.smembers(embedding_index_key)

            similarities = []

            for model_id in model_ids:
                try:
                    embedding_key = f"{self.config.world_models_collection}:embeddings:{model_id.decode('utf-8') if isinstance(model_id, bytes) else model_id}"
                    embedding_data = await self.redis.get(embedding_key)

                    if embedding_data:
                        data = json.loads(embedding_data.decode("utf-8"))

                        # Filter by domain and level if specified
                        if domain and data.get("domain") != domain:
                            continue
                        if model_level and data.get("model_level") != model_level.name:
                            continue

                        # Calculate similarity
                        stored_embedding = np.array(data["vector"])
                        similarity = self._cosine_similarity(query_embedding, stored_embedding)

                        if similarity >= self.config.similarity_threshold:
                            similarities.append((data["model_id"], similarity))

                except Exception as e:
                    logger.debug(f"Error processing embedding for {model_id}: {e}")
                    continue

            # Sort by similarity and limit results
            similarities.sort(key=lambda x: x[1], reverse=True)
            similarities = similarities[:limit]

            # Retrieve full world models
            results = []
            for model_id, similarity in similarities:
                model = await self.retrieve_world_model(model_id)
                if model:
                    results.append((model, similarity))

            logger.info(f"Found {len(results)} similar models for query")
            return results

        except Exception as e:
            logger.error(f"Failed to search similar models: {e}")
            return []

    async def store_exploration_pattern(self, pattern: ExplorationPattern) -> bool:
        """Store exploration pattern for future reuse"""
        try:
            pattern_key = f"{self.config.exploration_patterns_collection}:{pattern.pattern_id}"
            pattern_data = json.dumps(pattern.to_dict())

            # Store pattern
            await self.redis.setex(pattern_key, self.config.pattern_ttl, pattern_data)

            # Add to trigger type index
            trigger_index_key = f"{self.config.exploration_patterns_collection}:trigger:{pattern.trigger_type.name}"
            await self.redis.sadd(trigger_index_key, pattern.pattern_id)
            await self.redis.expire(trigger_index_key, self.config.pattern_ttl)

            # Add to domain index
            domain_index_key = f"{self.config.exploration_patterns_collection}:domain:{pattern.domain}"
            await self.redis.sadd(domain_index_key, pattern.pattern_id)
            await self.redis.expire(domain_index_key, self.config.pattern_ttl)

            logger.info(f"Stored exploration pattern {pattern.pattern_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to store exploration pattern: {e}")
            return False

    async def get_exploration_patterns(
        self,
        trigger_type: Optional[ExplorationTrigger] = None,
        domain: Optional[str] = None,
        min_success_rate: float = 0.5,
    ) -> List[ExplorationPattern]:
        """Retrieve exploration patterns matching criteria"""
        try:
            pattern_ids = set()

            # Get patterns by trigger type
            if trigger_type:
                trigger_index_key = f"{self.config.exploration_patterns_collection}:trigger:{trigger_type.name}"
                trigger_patterns = await self.redis.smembers(trigger_index_key)
                pattern_ids.update(trigger_patterns)

            # Get patterns by domain
            if domain:
                domain_index_key = f"{self.config.exploration_patterns_collection}:domain:{domain}"
                domain_patterns = await self.redis.smembers(domain_index_key)
                if pattern_ids:
                    pattern_ids.intersection_update(domain_patterns)
                else:
                    pattern_ids.update(domain_patterns)

            # If no filters, get all patterns (limit to prevent overload)
            if not pattern_ids and not trigger_type and not domain:
                all_patterns_key = f"{self.config.exploration_patterns_collection}:*"
                pattern_keys = await self.redis.keys(all_patterns_key)
                pattern_ids = {key.decode("utf-8").split(":")[-1] for key in pattern_keys if ":" in key.decode("utf-8")}

            # Retrieve and filter patterns
            patterns = []
            for pattern_id in pattern_ids:
                if isinstance(pattern_id, bytes):
                    pattern_id = pattern_id.decode("utf-8")

                pattern_key = f"{self.config.exploration_patterns_collection}:{pattern_id}"
                pattern_data = await self.redis.get(pattern_key)

                if pattern_data:
                    try:
                        data = json.loads(pattern_data.decode("utf-8"))
                        pattern = ExplorationPattern.from_dict(data)

                        if pattern.success_rate >= min_success_rate:
                            patterns.append(pattern)
                    except Exception as e:
                        sanitized_pattern_id = pattern_id.replace("\r", "").replace("\n", "")
                        logger.debug(f"Error loading pattern {sanitized_pattern_id}: {e}")

            # Sort by success rate
            patterns.sort(key=lambda p: p.success_rate, reverse=True)

            logger.info(f"Retrieved {len(patterns)} exploration patterns")
            return patterns

        except Exception as e:
            logger.error(f"Failed to retrieve exploration patterns: {e}")
            return []

    async def store_trigger_history(self, trigger_result: TriggerDetectionResult, scenario_text: str) -> bool:
        """Store trigger detection history for analysis"""
        try:
            # Create unique ID for this trigger event
            trigger_id = hashlib.md5(f"{scenario_text}{utc_now().isoformat()}".encode()).hexdigest()

            history_data = {
                "trigger_id": trigger_id,
                "scenario_hash": hashlib.md5(scenario_text.encode()).hexdigest(),
                "scenario_length": len(scenario_text),
                "triggers": [t.name for t in trigger_result.triggers],
                "confidence_scores": {t.name: score for t, score in trigger_result.confidence_scores.items()},
                "novelty_score": trigger_result.novelty_score,
                "complexity_score": trigger_result.complexity_score,
                "sparsity_score": trigger_result.sparsity_score,
                "exploration_priority": trigger_result.exploration_priority,
                "suggested_strategies": trigger_result.suggested_strategies,
                "timestamp": utc_now().isoformat(),
                "metadata": trigger_result.metadata,
            }

            # Store trigger history
            history_key = f"{self.config.trigger_history_collection}:{trigger_id}"
            await self.redis.setex(history_key, self.config.trigger_history_ttl, json.dumps(history_data))

            # Add to priority index
            priority_index_key = (
                f"{self.config.trigger_history_collection}:priority:{trigger_result.exploration_priority}"
            )
            await self.redis.sadd(priority_index_key, trigger_id)
            await self.redis.expire(priority_index_key, self.config.trigger_history_ttl)

            logger.info(f"Stored trigger history {trigger_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to store trigger history: {e}")
            return False

    async def cleanup_expired_models(self) -> int:
        """Clean up expired models and update indexes"""
        cleaned_count = 0
        try:
            # Get all model keys
            pattern = f"{self.config.world_models_collection}:*"
            model_keys = await self.redis.keys(pattern)

            for key in model_keys:
                ttl = await self.redis.ttl(key)
                if ttl == -2:  # Key doesn't exist (expired)
                    cleaned_count += 1
                elif ttl == -1:  # Key exists but no TTL set
                    # Set appropriate TTL based on key type
                    key_str = key.decode("utf-8") if isinstance(key, bytes) else key
                    if ":embeddings:" in key_str:
                        await self.redis.expire(key, self.config.category_model_ttl)
                    elif ":hierarchies:" in key_str:
                        await self.redis.expire(key, self.config.domain_model_ttl)

            logger.info(f"Cleaned up {cleaned_count} expired models")
            return cleaned_count

        except Exception as e:
            logger.error(f"Failed to cleanup expired models: {e}")
            return 0

    async def get_models_by_level(self, level: WorldModelLevel) -> List[WorldModel]:
        """Retrieve all world models of a specific hierarchical level"""
        try:
            models = []
            pattern = f"{self.config.world_models_collection}:*"
            keys = await self.redis.keys(pattern)

            for key in keys:
                try:
                    data = await self.redis.get(key)
                    if data:
                        model_data = json.loads(data)
                        model = WorldModel.from_dict(model_data)
                        if model.model_level == level:
                            models.append(model)
                except Exception as e:
                    logger.warning(f"Failed to parse model from key {key}: {e}")
                    continue

            logger.info(f"Retrieved {len(models)} models of level {level.name}")
            return models

        except Exception as e:
            logger.error(f"Failed to get models by level {level}: {e}")
            return []

    async def _generate_embedding(self, text: str) -> Optional[np.ndarray]:
        """Generate embedding for text using the embeddings service"""
        try:
            if not self.embeddings_service:
                return None

            # This would use the actual embeddings service
            # For now, return a dummy embedding
            return np.random.rand(self.config.embedding_dimension)

        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return None

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            dot_product = np.dot(a, b)
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)

            if norm_a == 0 or norm_b == 0:
                return 0.0

            return dot_product / (norm_a * norm_b)
        except Exception:
            return 0.0

    async def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics for monitoring"""
        try:
            stats = {
                "collections": {},
                "total_keys": 0,
                "memory_usage": await self._get_memory_usage(),
                "timestamp": utc_now().isoformat(),
            }

            # Count keys in each collection
            for collection_name in [
                self.config.world_models_collection,
                self.config.exploration_patterns_collection,
                self.config.trigger_history_collection,
                self.config.model_hierarchies_collection,
            ]:
                pattern = f"{collection_name}:*"
                keys = await self.redis.keys(pattern)
                stats["collections"][collection_name] = len(keys)
                stats["total_keys"] += len(keys)

            return stats

        except Exception as e:
            logger.error(f"Failed to get storage stats: {e}")
            return {}

    async def _get_memory_usage(self) -> Dict[str, Any]:
        """Get Redis memory usage information"""
        try:
            info = await self.redis.info("memory")
            return {
                "used_memory": info.get("used_memory", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "used_memory_peak": info.get("used_memory_peak", 0),
                "used_memory_peak_human": info.get("used_memory_peak_human", "0B"),
            }
        except Exception:
            return {"used_memory": 0, "used_memory_human": "0B"}
