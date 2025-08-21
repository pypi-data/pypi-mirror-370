"""
Unified Redis Service for Reasoning Kernel

This module consolidates three separate Redis implementations into a single,
production-ready service with connection pooling, vector operations, and
comprehensive functionality for the MSA Reasoning Engine.

Consolidates:
- RedisMemoryService: General purpose Redis operations
- RedisVectorService: Vector storage with Semantic Kernel
- ProductionRedisManager: Production-ready schema-aware operations

Key Features:
- Connection pooling with async operations
- Vector storage and similarity search
- World model operations with hierarchical support
- Reasoning chain storage and retrieval
- Knowledge management with tagging
- Session management and caching
- Production-ready error handling and monitoring
- Schema-aware key generation with TTL policies
- Batch operations for performance
- Circuit breaker integration

Author: AI Assistant & Reasoning Kernel Team
Date: 2025-08-15
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone, UTC
import hashlib
import json
import logging
import time
from typing import Any, Dict, List, Optional, Set
import uuid

# Import circuit breaker
from ..core.circuit_breaker import CircuitBreaker

from ..core.logging_utils import simple_log_error


try:
    import redis
    from redis import asyncio as aioredis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None
    aioredis = None

try:
    from semantic_kernel.connectors.ai.embedding_generator_base import (
        EmbeddingGeneratorBase,
    )
    from semantic_kernel.connectors.redis import RedisStore
except Exception:
    # Fallback implementations
    class _DummyRedisStore:
        def __init__(self, *args, **kwargs):
            pass

        def get_collection(self, *args, **kwargs):
            class _DummyCollection:
                async def upsert(self, *a, **k):
                    return None

            return _DummyCollection()

    RedisStore = _DummyRedisStore

    class EmbeddingGeneratorBase:
        async def generate_embeddings(self, texts: List[str]):
            return [[0.0] * 1 for _ in texts]


from ..core.constants import (
    DEFAULT_CACHE_TTL,
    SHORT_CACHE_TTL,
    REASONING_RESULT_TTL,
)

# Schema imports
try:
    from ..schemas.redis_memory_schema import (
        ReasoningKernelRedisSchema,
        create_production_schema,
        create_development_schema,
        TTLPolicy,
    )
except ImportError:
    # Fallback for missing schema
    class TTLPolicy:
        pass

    class ReasoningKernelRedisSchema:
        def __init__(self):
            self.config = type("config", (), {"namespace_prefix": "rk"})()


# World model imports
try:
    from ..models.world_model import WorldModel, WorldModelEvidence
    from ..core.exploration_triggers import ExplorationTrigger, TriggerDetectionResult
except ImportError:
    # Fallback classes for missing models
    class WorldModel:
        pass

    class WorldModelEvidence:
        pass

    class ExplorationTrigger:
        pass

    class TriggerDetectionResult:
        pass


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
    context: str = "{}"
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    embedding: List[float] = field(default_factory=list)


@dataclass
class WorldModelRecord:
    """Record for world model states and contexts"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    model_type: str = ""
    state_data: str = "{}"
    confidence: float = 0.0
    context_keys: str = "[]"
    last_updated: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    embedding: List[float] = field(default_factory=list)


@dataclass
class ExplorationRecord:
    """Record for exploration patterns and discoveries"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    exploration_type: str = ""
    hypothesis: str = ""
    evidence: str = ""
    conclusion: str = ""
    exploration_path: str = "[]"
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    embedding: List[float] = field(default_factory=list)


@dataclass
class RedisConnectionConfig:
    """Configuration for Redis connection"""

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    decode_responses: bool = True
    max_connections: int = 50
    retry_attempts: int = 3
    timeout: float = 30.0
    redis_url: Optional[str] = None


class UnifiedRedisService:
    """
    Unified Redis service combining memory operations, vector storage,
    and production-ready schema management.

    This service consolidates functionality from:
    - RedisMemoryService: General Redis operations
    - RedisVectorService: Vector operations with Semantic Kernel
    - ProductionRedisManager: Production schema operations
    """

    def __init__(
        self,
        config: Optional[RedisConnectionConfig] = None,
        embedding_generator: Optional[EmbeddingGeneratorBase] = None,
        schema: Optional[ReasoningKernelRedisSchema] = None,
        enable_monitoring: bool = True,
    ):
        """Initialize unified Redis service"""
        self.config = config or RedisConnectionConfig()
        self.embedding_generator = embedding_generator
        self.schema = schema or create_production_schema()
        self.enable_monitoring = enable_monitoring

        # Connection management
        self.redis_client: Optional[Any] = None
        self._connection_pool: Optional[Any] = None
        self._is_connected = False

        # Vector store components
        self.redis_store = None
        self._collections = {}
        self._vector_initialized = False

        # Monitoring and performance
        self._operation_count = 0
        self._error_count = 0
        self._cache_hits = 0
        self._cache_misses = 0
        self._memory_cache: Dict[str, Any] = {}  # In-memory cache for frequently accessed items
        self._memory_cache_ttl: Dict[str, float] = {}  # TTL for memory cache items
        self._last_cleanup_time = time.time()
        
        # Circuit breaker for Redis operations
        from ..core.circuit_breaker import CircuitBreakerConfig, ServiceType
        circuit_breaker_config = CircuitBreakerConfig(
            service_type=ServiceType.REDIS,
            failure_threshold=5,
            timeout_duration=30.0,
            max_retries=3,
            base_delay=1.0,
            retriable_exceptions=(
                ConnectionError,
                TimeoutError,
                OSError,
            ),
        )
        self._circuit_breaker = CircuitBreaker("redis", circuit_breaker_config)

        logger.info(f"UnifiedRedisService initialized with schema: {self.schema.config.namespace_prefix}")

    # Connection Management
    async def connect(self) -> bool:
        """Establish connection to Redis with connection pooling"""
        if self._is_connected and self.redis_client:
            return True

        if not REDIS_AVAILABLE:
            simple_log_error(logger, "connect", Exception("Redis is not available - install redis-py"))
            return False

        try:
            connection_kwargs = {
                "decode_responses": self.config.decode_responses,
                "retry_on_timeout": True,
                "socket_connect_timeout": self.config.timeout,
                "socket_timeout": self.config.timeout,
            }

            if self.config.redis_url:
                # Use Redis URL if provided
                self._connection_pool = aioredis.ConnectionPool.from_url(
                    self.config.redis_url, max_connections=self.config.max_connections, **connection_kwargs
                )
            else:
                # Use individual parameters
                self._connection_pool = aioredis.ConnectionPool(
                    host=self.config.host,
                    port=self.config.port,
                    db=self.config.db,
                    password=self.config.password,
                    max_connections=self.config.max_connections,
                    **connection_kwargs,
                )

            self.redis_client = aioredis.Redis(connection_pool=self._connection_pool)

            # Test connection
            await self.redis_client.ping()
            self._is_connected = True

            logger.info(f"Connected to Redis at {self.config.host}:{self.config.port}")
            return True

        except Exception as e:
            simple_log_error(logger, "connect", e, redis_url=self.config.redis_url if self.config else "unknown")
            self._is_connected = False
            return False

    async def disconnect(self) -> None:
        """Close Redis connection and cleanup resources"""
        try:
            if self.redis_client:
                await self.redis_client.aclose()
                self.redis_client = None

            if self._connection_pool:
                await self._connection_pool.aclose()
                self._connection_pool = None

            self._is_connected = False
            self._vector_initialized = False
            self._collections.clear()

            logger.info("Disconnected from Redis")

        except Exception as e:
            simple_log_error(logger, "disconnect", e)

    async def _ensure_connected(self) -> bool:
        """Ensure Redis connection is established"""
        if not self._is_connected:
            # Use circuit breaker for connection attempts
            async with self._circuit_breaker:
                return await self.connect()
        return True

    def _increment_operation_count(self, operation_type: str = "general") -> None:
        """Track operation counts for monitoring"""
        if self.enable_monitoring:
            self._operation_count += 1

    def _increment_error_count(self) -> None:
        """Track error counts for monitoring"""
        if self.enable_monitoring:
            self._error_count += 1

    def _cleanup_expired_memory_cache(self):
        """Clean up expired entries in the in-memory cache"""
        current_time = time.time()
        expired_keys = []
        
        for key, timestamp in self._memory_cache_ttl.items():
            if current_time - timestamp >= DEFAULT_CACHE_TTL:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._memory_cache[key]
            del self._memory_cache_ttl[key]
        
        # Update last cleanup time
        self._last_cleanup_time = current_time

    # Vector Operations (from RedisVectorService)
    async def initialize_vector_store(self) -> bool:
        """Initialize Redis vector store for embeddings"""
        if self._vector_initialized or not self.embedding_generator:
            return True

        try:
            connection_string = self.config.redis_url or f"redis://{self.config.host}:{self.config.port}"

            self.redis_store = RedisStore(
                connection_string=connection_string, embedding_generator=self.embedding_generator
            )

            # Initialize collections on-demand to avoid definition issues
            self._vector_initialized = True
            logger.info("Vector store initialized successfully")
            return True

        except Exception as e:
            simple_log_error(logger, "initialize_vector_store", e)
            return False

    async def _get_or_create_collection(self, collection_name: str, record_type: type):
        """Lazy collection creation for vector operations"""
        if collection_name not in self._collections:
            if not self._vector_initialized:
                await self.initialize_vector_store()

            try:
                self._collections[collection_name] = self.redis_store.get_collection(
                    record_type=record_type, collection_name=collection_name
                )
                logger.debug(f"Created collection: {collection_name}")
            except Exception as e:
                simple_log_error(logger, "get_or_create_collection", e, collection_name=collection_name)
                raise

        return self._collections[collection_name]

    # Reasoning Chain Operations (from RedisMemoryService)
    async def store_reasoning_chain(self, chain_id: str, chain_data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Store reasoning chain with optional TTL"""
        if not await self._ensure_connected():
            return False

        try:
            async with self._circuit_breaker:
                key = f"{self.schema.config.namespace_prefix}:reasoning:chain:{chain_id}"
                serialized_data = json.dumps(chain_data, default=str)

                if ttl:
                    await self.redis_client.setex(key, ttl, serialized_data)
                else:
                    await self.redis_client.set(key, serialized_data)

                # Also store with embedding if vector store available
                if self._vector_initialized:
                    try:
                        await self._store_reasoning_pattern_vector(
                            pattern_type="reasoning_chain",
                            question=chain_data.get("question", ""),
                            reasoning_steps=chain_data.get("steps", ""),
                            final_answer=chain_data.get("conclusion", ""),
                            confidence_score=chain_data.get("confidence", 0.0),
                            context=chain_data,
                        )
                    except Exception as vector_error:
                        logger.warning(f"Vector storage failed for reasoning chain {chain_id}: {vector_error}")

                # Update in-memory cache
                cache_key = f"reasoning_chain:{chain_id}"
                self._memory_cache[cache_key] = chain_data
                self._memory_cache_ttl[cache_key] = time.time()

                self._increment_operation_count("store_reasoning_chain")
                logger.debug(f"Stored reasoning chain: {chain_id}")
                return True

        except Exception as e:
            simple_log_error(logger, "store_reasoning_chain", e, chain_id=chain_id)
            self._increment_error_count()
            return False

    async def get_reasoning_chain(self, chain_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve reasoning chain by ID"""
        # Check in-memory cache first
        cache_key = f"reasoning_chain:{chain_id}"
        if cache_key in self._memory_cache:
            # Check if cache entry is still valid
            if time.time() - self._memory_cache_ttl.get(cache_key, 0) < DEFAULT_CACHE_TTL:
                self._cache_hits += 1
                return self._memory_cache[cache_key]
            else:
                # Remove expired entry
                del self._memory_cache[cache_key]
                del self._memory_cache_ttl[cache_key]
        
        if not await self._ensure_connected():
            return None

        try:
            async with self._circuit_breaker:
                key = f"{self.schema.config.namespace_prefix}:reasoning:chain:{chain_id}"
                data = await self.redis_client.get(key)

                if data:
                    self._cache_hits += 1
                    result = json.loads(data)
                    # Store in in-memory cache for faster access next time
                    self._memory_cache[cache_key] = result
                    self._memory_cache_ttl[cache_key] = time.time()
                    self._increment_operation_count("get_reasoning_chain")
                    return result
                else:
                    self._cache_misses += 1
                    return None

        except Exception as e:
            simple_log_error(logger, "get_reasoning_chain", e, chain_id=chain_id)
            self._increment_error_count()
            return None

    async def _store_reasoning_pattern_vector(
        self,
        pattern_type: str,
        question: str,
        reasoning_steps: str,
        final_answer: str,
        confidence_score: float = 0.0,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """Store reasoning pattern with vector embedding"""
        try:
            # Generate embedding from combined text
            combined_text = f"{question} {reasoning_steps} {final_answer}"
            embedding = await self.embedding_generator.generate_embeddings([combined_text])

            # Create record
            record = ReasoningRecord(
                pattern_type=pattern_type,
                question=question,
                reasoning_steps=reasoning_steps,
                final_answer=final_answer,
                confidence_score=confidence_score,
                context=json.dumps(context or {}, default=str),
                embedding=embedding[0] if embedding else [],
            )

            # Store in collection
            collection = await self._get_or_create_collection("reasoning", ReasoningRecord)
            await collection.upsert(record)

            logger.debug(f"Stored reasoning pattern with ID: {record.id}")
            return record.id

        except Exception as e:
            simple_log_error(logger, "store_reasoning_pattern_vector", e)
            return None

    # World Model Operations (from ProductionRedisManager + RedisVectorService)
    async def store_world_model(
        self, scenario: str, world_model: WorldModel, abstraction_level: str = "omega1"
    ) -> bool:
        """Store world model with schema-aware key generation"""
        if not await self._ensure_connected():
            return False

        try:
            async with self._circuit_breaker:
                # Generate schema-aware key
                scenario_hash = self._generate_scenario_hash(scenario)
                key = f"{self.schema.config.namespace_prefix}:world_model:{scenario_hash}:{abstraction_level}"

                # Serialize world model
                model_data = {
                    "scenario": scenario,
                    "abstraction_level": abstraction_level,
                    "model_type": str(world_model.model_type) if hasattr(world_model, "model_type") else "unknown",
                    "model_level": str(world_model.model_level) if hasattr(world_model, "model_level") else "unknown",
                    "confidence": getattr(world_model, "confidence", 0.0),
                    "state": getattr(world_model, "state", {}),
                    "evidence": [str(e) for e in getattr(world_model, "evidence", [])],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

                # Store in Redis with TTL
                ttl = self._get_ttl_for_abstraction_level(abstraction_level)
                await self.redis_client.setex(key, ttl, json.dumps(model_data, default=str))

                # Store vector representation if available
                if self._vector_initialized:
                    await self._store_world_model_vector(
                        model_type=model_data["model_type"],
                        state_data=model_data["state"],
                        confidence=model_data["confidence"],
                    )

                # Update in-memory cache
                cache_key = f"world_model:{scenario}:{abstraction_level}"
                self._memory_cache[cache_key] = model_data
                self._memory_cache_ttl[cache_key] = time.time()

                self._increment_operation_count("store_world_model")
                logger.debug(f"Stored world model for scenario: {scenario}")
                return True

        except Exception as e:
            simple_log_error(logger, "store_world_model", e, scenario=scenario)
            self._increment_error_count()
            return False

    async def _store_world_model_vector(
        self,
        model_type: str,
        state_data: Dict[str, Any],
        confidence: float = 0.0,
        context_keys: Optional[List[str]] = None,
    ) -> Optional[str]:
        """Store world model with vector embedding"""
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
            collection = await self._get_or_create_collection("world_models", WorldModelRecord)
            await collection.upsert(record)

            logger.debug(f"Stored world model with ID: {record.id}")
            return record.id

        except Exception as e:
            simple_log_error(logger, "store_world_model_vector", e)
            return None

    async def retrieve_world_model(self, scenario: str, abstraction_level: str = "omega1") -> Optional[Dict[str, Any]]:
        """Retrieve world model by scenario and abstraction level"""
        # Check in-memory cache first
        cache_key = f"world_model:{scenario}:{abstraction_level}"
        if cache_key in self._memory_cache:
            # Check if cache entry is still valid
            if time.time() - self._memory_cache_ttl.get(cache_key, 0) < DEFAULT_CACHE_TTL:
                self._cache_hits += 1
                return self._memory_cache[cache_key]
            else:
                # Remove expired entry
                del self._memory_cache[cache_key]
                del self._memory_cache_ttl[cache_key]
        
        if not await self._ensure_connected():
            return None

        try:
            async with self._circuit_breaker:
                scenario_hash = self._generate_scenario_hash(scenario)
                key = f"{self.schema.config.namespace_prefix}:world_model:{scenario_hash}:{abstraction_level}"

                data = await self.redis_client.get(key)
                if data:
                    self._cache_hits += 1
                    result = json.loads(data)
                    
                    # Store in in-memory cache for faster access next time
                    self._memory_cache[cache_key] = result
                    self._memory_cache_ttl[cache_key] = time.time()
                    
                    self._increment_operation_count("retrieve_world_model")
                    return result
                else:
                    self._cache_misses += 1
                    return None

        except Exception as e:
            simple_log_error(logger, "retrieve_world_model", e, scenario=scenario)
            self._increment_error_count()
            return None

    # Knowledge Operations (from RedisMemoryService)
    async def store_knowledge(
        self,
        knowledge_id: str,
        knowledge_data: Dict[str, Any],
        knowledge_type: str = "general",
        tags: Optional[Set[str]] = None,
        ttl: Optional[int] = None,
    ) -> bool:
        """Store knowledge with tagging and categorization"""
        if not await self._ensure_connected():
            return False

        try:
            async with self._circuit_breaker:
                # Store main knowledge
                key = f"{self.schema.config.namespace_prefix}:knowledge:{knowledge_id}"

                # Add metadata
                enhanced_data = {
                    **knowledge_data,
                    "knowledge_type": knowledge_type,
                    "tags": list(tags) if tags else [],
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "knowledge_id": knowledge_id,
                }

                serialized_data = json.dumps(enhanced_data, default=str)

                if ttl:
                    await self.redis_client.setex(key, ttl, serialized_data)
                else:
                    await self.redis_client.set(key, serialized_data)

                # Index by type
                type_key = f"{self.schema.config.namespace_prefix}:knowledge:type:{knowledge_type}"
                await self.redis_client.sadd(type_key, knowledge_id)

                # Index by tags
                if tags:
                    for tag in tags:
                        tag_key = f"{self.schema.config.namespace_prefix}:knowledge:tag:{tag}"
                        await self.redis_client.sadd(tag_key, knowledge_id)

                # Update in-memory cache for this knowledge type
                cache_key = f"knowledge_type:{knowledge_type}"
                if cache_key in self._memory_cache:
                    self._memory_cache[cache_key].append(enhanced_data)
                    self._memory_cache_ttl[cache_key] = time.time()
                else:
                    # Create new cache entry
                    self._memory_cache[cache_key] = [enhanced_data]
                    self._memory_cache_ttl[cache_key] = time.time()

                self._increment_operation_count("store_knowledge")
                logger.debug(f"Stored knowledge: {knowledge_id}")
                return True

        except Exception as e:
            simple_log_error(logger, "store_knowledge", e, knowledge_id=knowledge_id)
            self._increment_error_count()
            return False

    async def retrieve_knowledge_by_type(self, knowledge_type: str) -> List[Dict[str, Any]]:
        """Retrieve all knowledge entries by type"""
        # Check in-memory cache first
        cache_key = f"knowledge_type:{knowledge_type}"
        if cache_key in self._memory_cache:
            # Check if cache entry is still valid
            if time.time() - self._memory_cache_ttl.get(cache_key, 0) < DEFAULT_CACHE_TTL:
                self._cache_hits += 1
                return self._memory_cache[cache_key]
            else:
                # Remove expired entry
                del self._memory_cache[cache_key]
                del self._memory_cache_ttl[cache_key]
        
        if not await self._ensure_connected():
            return []

        try:
            async with self._circuit_breaker:
                type_key = f"{self.schema.config.namespace_prefix}:knowledge:type:{knowledge_type}"
                knowledge_ids = await self.redis_client.smembers(type_key)

                results = []
                for knowledge_id in knowledge_ids:
                    key = f"{self.schema.config.namespace_prefix}:knowledge:{knowledge_id}"
                    data = await self.redis_client.get(key)
                    if data:
                        results.append(json.loads(data))

                # Store in in-memory cache for faster access next time
                self._memory_cache[cache_key] = results
                self._memory_cache_ttl[cache_key] = time.time()
                
                self._increment_operation_count("retrieve_knowledge_by_type")
                return results

        except Exception as e:
            simple_log_error(logger, "retrieve_knowledge_by_type", e, knowledge_type=knowledge_type)
            self._increment_error_count()
            return []

    # Session Management (from RedisMemoryService)
    async def create_session(self, session_id: str, session_data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Create a new session with optional TTL"""
        if not await self._ensure_connected():
            return False

        try:
            async with self._circuit_breaker:
                key = f"{self.schema.config.namespace_prefix}:session:{session_id}"

                enhanced_data = {
                    **session_data,
                    "session_id": session_id,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "last_accessed": datetime.now(timezone.utc).isoformat(),
                }

                serialized_data = json.dumps(enhanced_data, default=str)

                if ttl:
                    await self.redis_client.setex(key, ttl, serialized_data)
                else:
                    await self.redis_client.set(key, serialized_data)

                # Update in-memory cache
                cache_key = f"session:{session_id}"
                self._memory_cache[cache_key] = enhanced_data
                self._memory_cache_ttl[cache_key] = time.time()

                self._increment_operation_count("create_session")
                logger.debug(f"Created session: {session_id}")
                return True

        except Exception as e:
            simple_log_error(logger, "create_session", e, session_id=session_id)
            self._increment_error_count()
            return False

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session data and update last accessed"""
        # Check in-memory cache first
        cache_key = f"session:{session_id}"
        if cache_key in self._memory_cache:
            # Check if cache entry is still valid
            if time.time() - self._memory_cache_ttl.get(cache_key, 0) < DEFAULT_CACHE_TTL:
                self._cache_hits += 1
                return self._memory_cache[cache_key]
            else:
                # Remove expired entry
                del self._memory_cache[cache_key]
                del self._memory_cache_ttl[cache_key]
        
        if not await self._ensure_connected():
            return None

        try:
            async with self._circuit_breaker:
                key = f"{self.schema.config.namespace_prefix}:session:{session_id}"
                data = await self.redis_client.get(key)

                if data:
                    session_data = json.loads(data)

                    # Update last accessed timestamp
                    session_data["last_accessed"] = datetime.now(timezone.utc).isoformat()
                    await self.redis_client.set(key, json.dumps(session_data, default=str))

                    # Store in in-memory cache for faster access next time
                    self._memory_cache[cache_key] = session_data
                    self._memory_cache_ttl[cache_key] = time.time()

                    self._cache_hits += 1
                    self._increment_operation_count("get_session")
                    return session_data
                else:
                    self._cache_misses += 1
                    return None

        except Exception as e:
            simple_log_error(logger, "get_session", e, session_id=session_id)
            self._increment_error_count()
            return None

    # Caching Operations (from RedisMemoryService)
    async def cache_model_result(
        self, model_name: str, input_hash: str, result: Dict[str, Any], ttl: Optional[int] = None
    ) -> bool:
        """Cache model result with optional TTL"""
        if not await self._ensure_connected():
            return False

        try:
            async with self._circuit_breaker:
                key = f"{self.schema.config.namespace_prefix}:cache:model:{model_name}:{input_hash}"

                cache_data = {
                    "result": result,
                    "model_name": model_name,
                    "input_hash": input_hash,
                    "cached_at": datetime.now(timezone.utc).isoformat(),
                }

                serialized_data = json.dumps(cache_data, default=str)
                ttl = ttl or DEFAULT_CACHE_TTL

                await self.redis_client.setex(key, ttl, serialized_data)

                # Update in-memory cache
                cache_key = f"model_cache:{model_name}:{input_hash}"
                self._memory_cache[cache_key] = result
                self._memory_cache_ttl[cache_key] = time.time()

                self._increment_operation_count("cache_model_result")
                logger.debug(f"Cached model result for {model_name}:{input_hash}")
                return True

        except Exception as e:
            simple_log_error(logger, "cache_model_result", e, model_name=model_name, input_hash=input_hash)
            self._increment_error_count()
            return False

    async def get_cached_model_result(self, model_name: str, input_hash: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached model result"""
        # Check in-memory cache first
        cache_key = f"model_cache:{model_name}:{input_hash}"
        if cache_key in self._memory_cache:
            # Check if cache entry is still valid
            if time.time() - self._memory_cache_ttl.get(cache_key, 0) < DEFAULT_CACHE_TTL:
                self._cache_hits += 1
                return self._memory_cache[cache_key]
            else:
                # Remove expired entry
                del self._memory_cache[cache_key]
                del self._memory_cache_ttl[cache_key]
        
        if not await self._ensure_connected():
            return None

        try:
            async with self._circuit_breaker:
                key = f"{self.schema.config.namespace_prefix}:cache:model:{model_name}:{input_hash}"
                data = await self.redis_client.get(key)

                if data:
                    self._cache_hits += 1
                    cache_data = json.loads(data)
                    result = cache_data.get("result")
                    
                    # Store in in-memory cache for faster access next time
                    self._memory_cache[cache_key] = result
                    self._memory_cache_ttl[cache_key] = time.time()
                    
                    self._increment_operation_count("get_cached_model_result")
                    return result
                else:
                    self._cache_misses += 1
                    return None

        except Exception as e:
            simple_log_error(logger, "get_cached_model_result", e, model_name=model_name, input_hash=input_hash)
            self._increment_error_count()
            return None

    # Vector Search Operations
    async def similarity_search(self, collection_name: str, query_text: str, limit: int = 10) -> List[Any]:
        """Perform similarity search in specified collection"""
        if not self._vector_initialized:
            return []

        try:
            if collection_name not in self._collections:
                return []

            collection = self._collections[collection_name]
            # Note: Actual similarity search implementation depends on SK Redis connector
            # This is a placeholder for the interface

            self._increment_operation_count("similarity_search")
            return []

        except Exception as e:
            simple_log_error(logger, "similarity_search", e, collection_name=collection_name)
            self._increment_error_count()
            return []

    # Utility Methods
    def _generate_scenario_hash(self, scenario: str) -> str:
        """Generate deterministic hash for scenario identification"""
        return hashlib.sha256(scenario.encode("utf-8")).hexdigest()[:16]

    def _get_ttl_for_abstraction_level(self, level: str) -> int:
        """Get appropriate TTL based on abstraction level"""
        ttl_map = {
            "omega1": REASONING_RESULT_TTL,  # 2 hours
            "omega2": DEFAULT_CACHE_TTL,  # 1 hour
            "omega3": SHORT_CACHE_TTL,  # 5 minutes
            "default": DEFAULT_CACHE_TTL,
        }
        return ttl_map.get(level, ttl_map["default"])

    def generate_cache_key(self, prefix: str, *args) -> str:
        """Generate cache key from prefix and arguments"""
        if args:
            args_hash = hashlib.sha256(json.dumps(args, sort_keys=True, default=str).encode("utf-8")).hexdigest()[:8]
            return f"{self.schema.config.namespace_prefix}:cache:{prefix}:{args_hash}"
        else:
            return f"{self.schema.config.namespace_prefix}:cache:{prefix}"

    # Health and Monitoring
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        # Periodically clean up expired memory cache entries
        if time.time() - self._last_cleanup_time > 60:  # Clean up every minute
            self._cleanup_expired_memory_cache()
        
        health_data = {
            "status": "unknown",
            "redis_connected": self._is_connected,
            "vector_store_initialized": self._vector_initialized,
            "collections": list(self._collections.keys()),
            "memory_cache_size": len(self._memory_cache),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if self.enable_monitoring:
            health_data.update(
                {
                    "operation_count": self._operation_count,
                    "error_count": self._error_count,
                    "cache_hits": self._cache_hits,
                    "cache_misses": self._cache_misses,
                    "cache_hit_ratio": self._cache_hits / max(1, self._cache_hits + self._cache_misses),
                }
            )

        try:
            if await self._ensure_connected():
                await self.redis_client.ping()
                health_data["status"] = "healthy"
            else:
                health_data["status"] = "disconnected"
        except Exception as e:
            health_data["status"] = "error"
            health_data["error"] = str(e)

        return health_data

    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get detailed performance metrics"""
        return {
            "operations": {
                "total_operations": self._operation_count,
                "total_errors": self._error_count,
                "error_rate": self._error_count / max(1, self._operation_count),
            },
            "cache": {
                "cache_hits": self._cache_hits,
                "cache_misses": self._cache_misses,
                "hit_ratio": self._cache_hits / max(1, self._cache_hits + self._cache_misses),
                "memory_cache_size": len(self._memory_cache),
            },
            "connection": {
                "is_connected": self._is_connected,
                "vector_initialized": self._vector_initialized,
                "active_collections": len(self._collections),
                "circuit_breaker_state": str(self._circuit_breaker.state) if hasattr(self._circuit_breaker, 'state') else 'unknown',
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # Batch Operations for Performance
    async def batch_store(self, items: List[Dict[str, Any]]) -> Dict[str, bool]:
        """Store multiple items in batch for better performance"""
        if not await self._ensure_connected():
            return {item.get("id"): False for item in items if item.get("id")}

        results = {}

        try:
            async with self._circuit_breaker:
                pipe = self.redis_client.pipeline()

                for item in items:
                    item_type = item.get("type", "unknown")
                    item_id = item.get("id")
                    data = item.get("data", {})
                    ttl = item.get("ttl")

                    if not item_id:
                        continue

                    key = f"{self.schema.config.namespace_prefix}:{item_type}:{item_id}"
                    serialized_data = json.dumps(data, default=str)

                    if ttl:
                        await pipe.setex(key, ttl, serialized_data)
                    else:
                        await pipe.set(key, serialized_data)

                    results[item_id] = True  # Assume success for now

                await pipe.execute()
                self._increment_operation_count("batch_store")
                logger.debug(f"Batch stored {len(items)} items")
                
                return results  # All successful

        except Exception as e:
            simple_log_error(logger, "batch_store", e)
            self._increment_error_count()
            # Mark all as failed
            for item in items:
                if item.get("id"):
                    results[item["id"]] = False

        return results

    async def cleanup_expired_keys(self, pattern: str = "*") -> int:
        """Clean up expired keys matching pattern"""
        if not await self._ensure_connected():
            return 0

        try:
            full_pattern = f"{self.schema.config.namespace_prefix}:{pattern}"
            keys = await self.redis_client.keys(full_pattern)

            expired_count = 0
            for key in keys:
                ttl = await self.redis_client.ttl(key)
                if ttl == -1:  # No TTL set, check if it should have one
                    # Logic to determine if key should have TTL based on type
                    key_parts = key.split(":")
                    if len(key_parts) > 2:
                        key_type = key_parts[1]
                        if key_type in ["cache", "session"]:
                            await self.redis_client.expire(key, DEFAULT_CACHE_TTL)
                            expired_count += 1

            logger.info(f"Cleaned up {expired_count} keys")
            return expired_count

        except Exception as e:
            simple_log_error(logger, "cleanup_expired_keys", e)
            return 0

    # Exploration Pattern Operations (from ProductionRedisManager)
    async def store_exploration_pattern(
        self, scenario: str, trigger_result: TriggerDetectionResult, pattern_data: Dict[str, Any]
    ) -> bool:
        """Store an exploration pattern with trigger information"""
        if not await self._ensure_connected():
            return False

        try:
            # Use the triggers list from TriggerDetectionResult
            main_trigger = trigger_result.triggers[0] if trigger_result.triggers else ExplorationTrigger.NOVEL_SITUATION


            pattern_id = hashlib.md5(f"{scenario}{main_trigger.value}".encode()).hexdigest()[:8]
            key = f"{self.schema.config.namespace_prefix}:exploration:trigger_patterns:{main_trigger.value}:{pattern_id}"

            pattern_store_data = {
                "scenario": scenario,
                "trigger_type": main_trigger.value,
                "all_triggers": json.dumps([t.value for t in trigger_result.triggers]),
                "novelty_score": str(trigger_result.novelty_score),
                "complexity_score": str(trigger_result.complexity_score),
                "pattern_data": json.dumps(pattern_data),
                "created": datetime.now(timezone.utc).isoformat(),
                "usage_count": "1",
                "success_rate": "1.0",
            }

            ttl = self._get_ttl_for_abstraction_level("omega1")  # Use default TTL for exploration patterns

            await self.redis_client.setex(key, ttl, json.dumps(pattern_store_data, default=str))
            
            self._increment_operation_count("store_exploration_pattern")
            logger.debug(f"Stored exploration pattern: {key}")
            return True

        except Exception as e:
            simple_log_error(logger, "store_exploration_pattern", e, scenario=scenario)
            self._increment_error_count()
            return False

    async def retrieve_exploration_patterns(
        self, trigger_type: ExplorationTrigger, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Retrieve exploration patterns by trigger type"""
        if not await self._ensure_connected():
            return []

        try:
            pattern_key = f"{self.schema.config.namespace_prefix}:exploration:trigger_patterns:{trigger_type.value}*"
            keys = await self.redis_client.keys(pattern_key)

            patterns = []
            for key in keys[:limit]:
                pattern_data = await self.redis_client.get(key)
                if pattern_data:
                    patterns.append(json.loads(pattern_data))

            self._increment_operation_count("retrieve_exploration_patterns")
            logger.debug(f"Retrieved {len(patterns)} patterns for {trigger_type.value}")
            return patterns

        except Exception as e:
            simple_log_error(logger, "retrieve_exploration_patterns", e, trigger_type=trigger_type.value if trigger_type else "unknown")
            self._increment_error_count()
            return []

    # Agent Memory Operations (from ProductionRedisManager)
    async def store_agent_memory(self, agent_type: str, agent_id: str, memory_data: Dict[str, Any]) -> bool:
        """Store agent memory with proper indexing"""
        if not await self._ensure_connected():
            return False

        try:
            key = f"{self.schema.config.namespace_prefix}:agents:agent_memories:{agent_type}:{agent_id}"

            memory_store_data = {
                "agent_type": agent_type,
                "agent_id": agent_id,
                "memory_data": json.dumps(memory_data),
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "memory_size": str(len(json.dumps(memory_data))),
                "access_count": "1",
            }

            ttl = self._get_ttl_for_abstraction_level("omega1")  # Use default TTL for agent memories

            await self.redis_client.setex(key, ttl, json.dumps(memory_store_data, default=str))
            
            self._increment_operation_count("store_agent_memory")
            logger.debug(f"Stored agent memory: {key}")
            return True

        except Exception as e:
            simple_log_error(logger, "store_agent_memory", e, agent_type=agent_type, agent_id=agent_id)
            self._increment_error_count()
            return False

    async def retrieve_agent_memory(self, agent_type: str, agent_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve agent memory data"""
        if not await self._ensure_connected():
            return None

        try:
            key = f"{self.schema.config.namespace_prefix}:agents:agent_memories:{agent_type}:{agent_id}"
            data = await self.redis_client.get(key)

            if data:
                self._cache_hits += 1
                result = json.loads(data)
                # Increment access count
                await self.redis_client.hincrby(key, "access_count", 1)
                self._increment_operation_count("retrieve_agent_memory")
                logger.debug(f"Retrieved agent memory: {key}")
                return result
            else:
                self._cache_misses += 1
                return None

        except Exception as e:
            simple_log_error(logger, "retrieve_agent_memory", e, agent_type=agent_type, agent_id=agent_id)
            self._increment_error_count()
            return None

    # Similar World Models Search (from ProductionRedisManager)
    async def search_similar_world_models(
        self, domain: str, confidence_threshold: float = 0.7, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for similar world models by domain and confidence"""
        if not await self._ensure_connected():
            return []

        try:
            # Use Redis SCAN to find matching keys
            pattern = f"{self.schema.config.namespace_prefix}:world_model:*"
            similar_models = []

            cursor = 0
            while True:
                cursor, keys = await self.redis_client.scan(cursor, match=pattern, count=100)

                for key in keys:
                    model_data = await self.redis_client.get(key)
                    if model_data:
                        decoded_data = json.loads(model_data)
                        if (
                            decoded_data.get("domain") == domain
                            and float(decoded_data.get("confidence", 0)) >= confidence_threshold
                        ):
                            similar_models.append(decoded_data)

                    if len(similar_models) >= limit:
                        break

                if cursor == 0 or len(similar_models) >= limit:
                    break

            search_results = similar_models[:limit]
            logger.debug(f"Found {len(search_results)} similar world models for domain: {domain}")
            return search_results

        except Exception as e:
            simple_log_error(logger, "search_similar_world_models", e, domain=domain)
            return []

    # Factory Functions (from ProductionRedisManager)
    async def create_production_redis_manager(self, redis_url: str = "redis://localhost:6379") -> "UnifiedRedisService":
        """Create and connect a production Redis manager (factory function)"""
        config = RedisConnectionConfig(redis_url=redis_url)
        service = UnifiedRedisService(
            config=config, schema=create_production_schema(), enable_monitoring=True
        )
        await service.connect()
        return service

    async def create_development_redis_manager(self, redis_url: str = "redis://localhost:6379") -> "UnifiedRedisService":
        """Create and connect a development Redis manager (factory function)"""
        config = RedisConnectionConfig(redis_url=redis_url)
        service = UnifiedRedisService(
            config=config, schema=create_development_schema(), enable_monitoring=True
        )
        await service.connect()
        return service


# Factory Functions
async def create_unified_redis_service(
    redis_url: str = "redis://localhost:6379",
    embedding_generator: Optional[EmbeddingGeneratorBase] = None,
    environment: str = "production",
) -> UnifiedRedisService:
    """Create and initialize a unified Redis service"""

    config = RedisConnectionConfig(redis_url=redis_url)

    if environment == "production":
        schema = create_production_schema()
    else:
        schema = create_development_schema()

    service = UnifiedRedisService(
        config=config, embedding_generator=embedding_generator, schema=schema, enable_monitoring=True
    )

    await service.connect()

    if embedding_generator:
        await service.initialize_vector_store()

    return service


async def create_redis_service_from_config(
    host: str = "localhost",
    port: int = 6379,
    db: int = 0,
    password: Optional[str] = None,
    max_connections: int = 50,
    **kwargs,
) -> UnifiedRedisService:
    """Create Redis service from individual config parameters"""

    config = RedisConnectionConfig(
        host=host, port=port, db=db, password=password, max_connections=max_connections, **kwargs
    )

    service = UnifiedRedisService(config=config)
    await service.connect()
    return service
