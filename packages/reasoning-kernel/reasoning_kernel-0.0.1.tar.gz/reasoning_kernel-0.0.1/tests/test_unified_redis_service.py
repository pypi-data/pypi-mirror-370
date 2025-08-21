"""
Comprehensive tests for UnifiedRedisService

Tests consolidation of RedisMemoryService, RedisVectorService, and ProductionRedisManager
functionality into a single unified service with connection pooling and performance optimization.
"""

import json
import pytest
from typing import List
from unittest.mock import AsyncMock, MagicMock, patch

from reasoning_kernel.services.unified_redis_service import (
    UnifiedRedisService,
    RedisConnectionConfig,
    ReasoningRecord,
    WorldModelRecord,
    ExplorationRecord,
    create_unified_redis_service,
    create_redis_service_from_config,
)


# Mock embedding generator for testing
class MockEmbeddingGenerator:
    async def generate_embeddings(self, texts: List[str]):
        # Return mock embeddings with consistent dimensions
        return [[0.1, 0.2, 0.3] * 10 for _ in texts]  # 30-dimensional vectors


class TestUnifiedRedisService:
    """Test suite for unified Redis service consolidation"""

    @pytest.fixture
    def mock_redis_client(self):
        """Mock Redis client for testing"""
        client = AsyncMock()
        client.ping.return_value = True
        client.set.return_value = True
        client.get.return_value = None
        client.setex.return_value = True
        client.sadd.return_value = 1
        client.smembers.return_value = set()
        client.keys.return_value = []
        client.ttl.return_value = -1
        client.expire.return_value = True
        client.pipeline.return_value = AsyncMock()
        return client

    @pytest.fixture
    def redis_config(self):
        """Test Redis configuration"""
        return RedisConnectionConfig(host="localhost", port=6379, db=0, max_connections=10, timeout=5.0)

    @pytest.fixture
    def embedding_generator(self):
        """Mock embedding generator"""
        return MockEmbeddingGenerator()

    @pytest.fixture
    async def redis_service(self, redis_config, embedding_generator):
        """Create test Redis service"""
        service = UnifiedRedisService(
            config=redis_config, embedding_generator=embedding_generator, enable_monitoring=True
        )
        return service

    # Connection Management Tests
    async def test_service_initialization(self, redis_service):
        """Test service initialization"""
        assert redis_service.config.host == "localhost"
        assert redis_service.config.port == 6379
        assert redis_service.enable_monitoring is True
        assert not redis_service._is_connected
        assert not redis_service._vector_initialized
        assert redis_service._operation_count == 0

    @patch("reasoning_kernel.services.unified_redis_service.aioredis")
    async def test_successful_connection(self, mock_aioredis, redis_service):
        """Test successful Redis connection"""
        # Mock connection pool and client
        mock_pool = AsyncMock()
        mock_client = AsyncMock()
        mock_client.ping.return_value = True

        mock_aioredis.ConnectionPool.return_value = mock_pool
        mock_aioredis.Redis.return_value = mock_client

        result = await redis_service.connect()

        assert result is True
        assert redis_service._is_connected is True
        assert redis_service.redis_client == mock_client
        mock_client.ping.assert_called_once()

    @patch("reasoning_kernel.services.unified_redis_service.aioredis")
    async def test_connection_failure(self, mock_aioredis, redis_service):
        """Test Redis connection failure handling"""
        mock_aioredis.ConnectionPool.side_effect = Exception("Connection failed")

        result = await redis_service.connect()

        assert result is False
        assert redis_service._is_connected is False
        assert redis_service.redis_client is None

    @patch("reasoning_kernel.services.unified_redis_service.aioredis")
    async def test_disconnection(self, mock_aioredis, redis_service):
        """Test Redis disconnection and cleanup"""
        # Set up connected state
        mock_client = AsyncMock()
        mock_pool = AsyncMock()
        redis_service.redis_client = mock_client
        redis_service._connection_pool = mock_pool
        redis_service._is_connected = True
        redis_service._vector_initialized = True
        redis_service._collections = {"test": "collection"}

        await redis_service.disconnect()

        mock_client.aclose.assert_called_once()
        mock_pool.aclose.assert_called_once()
        assert redis_service.redis_client is None
        assert redis_service._connection_pool is None
        assert redis_service._is_connected is False
        assert redis_service._vector_initialized is False
        assert len(redis_service._collections) == 0

    # Reasoning Chain Operations Tests
    async def test_store_reasoning_chain(self, redis_service, mock_redis_client):
        """Test storing reasoning chain"""
        redis_service.redis_client = mock_redis_client
        redis_service._is_connected = True

        chain_data = {
            "question": "What is AI?",
            "steps": ["Define AI", "Explain applications"],
            "conclusion": "AI is machine intelligence",
            "confidence": 0.9,
        }

        result = await redis_service.store_reasoning_chain("test_chain", chain_data, ttl=3600)

        assert result is True
        mock_redis_client.setex.assert_called_once()
        call_args = mock_redis_client.setex.call_args
        assert "reasoning:chain:test_chain" in call_args[0][0]  # Check key format
        assert call_args[0][1] == 3600  # TTL

        # Verify data serialization
        stored_data = json.loads(call_args[0][2])
        assert stored_data["question"] == "What is AI?"
        assert stored_data["confidence"] == 0.9

    async def test_get_reasoning_chain_success(self, redis_service, mock_redis_client):
        """Test successful reasoning chain retrieval"""
        redis_service.redis_client = mock_redis_client
        redis_service._is_connected = True

        chain_data = {"question": "Test", "answer": "Result"}
        mock_redis_client.get.return_value = json.dumps(chain_data)

        result = await redis_service.get_reasoning_chain("test_chain")

        assert result == chain_data
        assert redis_service._cache_hits == 1
        mock_redis_client.get.assert_called_once()

    async def test_get_reasoning_chain_miss(self, redis_service, mock_redis_client):
        """Test reasoning chain cache miss"""
        redis_service.redis_client = mock_redis_client
        redis_service._is_connected = True
        mock_redis_client.get.return_value = None

        result = await redis_service.get_reasoning_chain("nonexistent")

        assert result is None
        assert redis_service._cache_misses == 1

    # World Model Operations Tests
    async def test_store_world_model(self, redis_service, mock_redis_client):
        """Test world model storage with schema-aware keys"""
        redis_service.redis_client = mock_redis_client
        redis_service._is_connected = True

        # Mock world model
        world_model = MagicMock()
        world_model.model_type = "PROBABILISTIC"
        world_model.model_level = "INSTANCE"
        world_model.confidence = 0.85
        world_model.state = {"entities": ["A", "B"]}
        world_model.evidence = ["Evidence 1", "Evidence 2"]

        result = await redis_service.store_world_model("test_scenario", world_model, "omega1")

        assert result is True
        mock_redis_client.setex.assert_called_once()
        call_args = mock_redis_client.setex.call_args
        assert "world_model:" in call_args[0][0]
        assert "omega1" in call_args[0][0]

        # Verify TTL is set appropriately
        assert call_args[0][1] > 0  # TTL should be positive

    async def test_retrieve_world_model_success(self, redis_service, mock_redis_client):
        """Test successful world model retrieval"""
        redis_service.redis_client = mock_redis_client
        redis_service._is_connected = True

        model_data = {
            "scenario": "test_scenario",
            "model_type": "PROBABILISTIC",
            "confidence": 0.85,
            "state": {"entities": ["A", "B"]},
        }
        mock_redis_client.get.return_value = json.dumps(model_data)

        result = await redis_service.retrieve_world_model("test_scenario", "omega1")

        assert result == model_data
        assert redis_service._cache_hits == 1

    # Knowledge Operations Tests
    async def test_store_knowledge_with_tags(self, redis_service, mock_redis_client):
        """Test knowledge storage with tagging"""
        redis_service.redis_client = mock_redis_client
        redis_service._is_connected = True

        knowledge_data = {
            "title": "AI Concepts",
            "content": "Machine learning fundamentals",
            "source": "Research paper",
        }
        tags = {"AI", "ML", "concepts"}

        result = await redis_service.store_knowledge("knowledge_1", knowledge_data, "research", tags, ttl=7200)

        assert result is True
        # Verify main storage call
        mock_redis_client.setex.assert_called()
        # Verify type indexing
        type_call_found = False
        tag_calls_found = 0

        for call in mock_redis_client.sadd.call_args_list:
            if "knowledge:type:research" in call[0][0]:
                type_call_found = True
            if "knowledge:tag:" in call[0][0]:
                tag_calls_found += 1

        assert type_call_found
        assert tag_calls_found == 3  # Three tags

    async def test_retrieve_knowledge_by_type(self, redis_service, mock_redis_client):
        """Test knowledge retrieval by type"""
        redis_service.redis_client = mock_redis_client
        redis_service._is_connected = True

        # Mock knowledge IDs for type
        mock_redis_client.smembers.return_value = {"knowledge_1", "knowledge_2"}

        # Mock knowledge data
        knowledge_data_1 = {"title": "AI Concepts", "knowledge_type": "research"}
        knowledge_data_2 = {"title": "ML Algorithms", "knowledge_type": "research"}

        def mock_get(key):
            if "knowledge_1" in key:
                return json.dumps(knowledge_data_1)
            elif "knowledge_2" in key:
                return json.dumps(knowledge_data_2)
            return None

        mock_redis_client.get.side_effect = mock_get

        result = await redis_service.retrieve_knowledge_by_type("research")

        assert len(result) == 2
        assert any(item["title"] == "AI Concepts" for item in result)
        assert any(item["title"] == "ML Algorithms" for item in result)

    # Session Management Tests
    async def test_create_session(self, redis_service, mock_redis_client):
        """Test session creation with metadata"""
        redis_service.redis_client = mock_redis_client
        redis_service._is_connected = True

        session_data = {"user_id": "user123", "context": {"reasoning_mode": "analytical"}}

        result = await redis_service.create_session("session_abc", session_data, ttl=1800)

        assert result is True
        mock_redis_client.setex.assert_called_once()
        call_args = mock_redis_client.setex.call_args
        assert "session:session_abc" in call_args[0][0]
        assert call_args[0][1] == 1800  # TTL

        # Verify enhanced data
        stored_data = json.loads(call_args[0][2])
        assert stored_data["session_id"] == "session_abc"
        assert stored_data["user_id"] == "user123"
        assert "created_at" in stored_data
        assert "last_accessed" in stored_data

    async def test_get_session_with_access_update(self, redis_service, mock_redis_client):
        """Test session retrieval with last_accessed update"""
        redis_service.redis_client = mock_redis_client
        redis_service._is_connected = True

        session_data = {
            "session_id": "session_abc",
            "user_id": "user123",
            "created_at": "2025-01-01T00:00:00Z",
            "last_accessed": "2025-01-01T00:00:00Z",
        }
        mock_redis_client.get.return_value = json.dumps(session_data)

        result = await redis_service.get_session("session_abc")

        assert result["session_id"] == "session_abc"
        assert result["user_id"] == "user123"
        # Verify last_accessed was updated
        assert result["last_accessed"] != "2025-01-01T00:00:00Z"

        # Verify the update was written back
        mock_redis_client.set.assert_called_once()

    # Caching Operations Tests
    async def test_cache_model_result(self, redis_service, mock_redis_client):
        """Test model result caching"""
        redis_service.redis_client = mock_redis_client
        redis_service._is_connected = True

        model_result = {"prediction": "positive sentiment", "confidence": 0.92, "processing_time": 0.15}

        result = await redis_service.cache_model_result("sentiment_model", "input_hash_123", model_result, ttl=1800)

        assert result is True
        mock_redis_client.setex.assert_called_once()
        call_args = mock_redis_client.setex.call_args
        assert "cache:model:sentiment_model:input_hash_123" in call_args[0][0]
        assert call_args[0][1] == 1800

        # Verify cached data structure
        cached_data = json.loads(call_args[0][2])
        assert cached_data["result"] == model_result
        assert cached_data["model_name"] == "sentiment_model"
        assert cached_data["input_hash"] == "input_hash_123"
        assert "cached_at" in cached_data

    async def test_get_cached_model_result_hit(self, redis_service, mock_redis_client):
        """Test successful cache retrieval"""
        redis_service.redis_client = mock_redis_client
        redis_service._is_connected = True

        cached_data = {
            "result": {"prediction": "positive", "confidence": 0.92},
            "model_name": "sentiment_model",
            "input_hash": "input_hash_123",
            "cached_at": "2025-01-01T12:00:00Z",
        }
        mock_redis_client.get.return_value = json.dumps(cached_data)

        result = await redis_service.get_cached_model_result("sentiment_model", "input_hash_123")

        assert result == {"prediction": "positive", "confidence": 0.92}
        assert redis_service._cache_hits == 1

    async def test_get_cached_model_result_miss(self, redis_service, mock_redis_client):
        """Test cache miss"""
        redis_service.redis_client = mock_redis_client
        redis_service._is_connected = True
        mock_redis_client.get.return_value = None

        result = await redis_service.get_cached_model_result("nonexistent_model", "hash")

        assert result is None
        assert redis_service._cache_misses == 1

    # Utility Methods Tests
    def test_generate_scenario_hash(self, redis_service):
        """Test scenario hash generation for consistency"""
        scenario = "complex reasoning scenario"
        hash1 = redis_service._generate_scenario_hash(scenario)
        hash2 = redis_service._generate_scenario_hash(scenario)

        assert hash1 == hash2  # Deterministic
        assert len(hash1) == 16  # Expected length
        assert isinstance(hash1, str)

        # Different scenarios should produce different hashes
        different_hash = redis_service._generate_scenario_hash("different scenario")
        assert hash1 != different_hash

    def test_get_ttl_for_abstraction_level(self, redis_service):
        """Test TTL mapping for different abstraction levels"""
        assert redis_service._get_ttl_for_abstraction_level("omega1") == 7200  # 2 hours
        assert redis_service._get_ttl_for_abstraction_level("omega2") == 3600  # 1 hour
        assert redis_service._get_ttl_for_abstraction_level("omega3") == 300  # 5 minutes
        assert redis_service._get_ttl_for_abstraction_level("unknown") == 3600  # default

    def test_generate_cache_key(self, redis_service):
        """Test cache key generation"""
        key1 = redis_service.generate_cache_key("test", "arg1", "arg2")
        key2 = redis_service.generate_cache_key("test", "arg1", "arg2")
        key3 = redis_service.generate_cache_key("test", "arg1", "different")

        assert key1 == key2  # Same arguments
        assert key1 != key3  # Different arguments
        # Updated assertion to match actual schema namespace
        namespace = redis_service.schema.config.namespace_prefix
        assert key1.startswith(f"{namespace}:cache:test:")  # Proper prefix

    # Batch Operations Tests
    async def test_batch_store(self, redis_service, mock_redis_client):
        """Test batch storage operations"""
        redis_service.redis_client = mock_redis_client
        redis_service._is_connected = True

        # Mock pipeline
        mock_pipeline = AsyncMock()
        mock_redis_client.pipeline.return_value = mock_pipeline
        # Mock the pipeline methods to return coroutines that resolve to None
        mock_pipeline.setex = AsyncMock(return_value=None)
        mock_pipeline.set = AsyncMock(return_value=None)
        # Mock the execute method to return an empty list (successful execution)
        mock_pipeline.execute = AsyncMock(return_value=[])

        items = [
            {"type": "test", "id": "item1", "data": {"value": 1}, "ttl": 3600},
            {"type": "test", "id": "item2", "data": {"value": 2}},
            {"type": "test", "id": "item3", "data": {"value": 3}, "ttl": 1800},
        ]

        result = await redis_service.batch_store(items)

        assert len(result) == 3
        # All values in result should be True, indicating successful batch store operations for each item
        assert all(result.values()), f"Expected all True, got {result}"

        # Verify pipeline usage
        mock_redis_client.pipeline.assert_called_once()
        mock_pipeline.execute.assert_called_once()

        # Verify correct number of operations
        setex_calls = len([call for call in mock_pipeline.setex.call_args_list])
        set_calls = len([call for call in mock_pipeline.set.call_args_list])
        assert setex_calls == 2  # Items with TTL
        assert set_calls == 1  # Item without TTL

    # Health and Monitoring Tests
    async def test_health_check_healthy(self, redis_service, mock_redis_client):
        """Test health check when service is healthy"""
        redis_service.redis_client = mock_redis_client
        redis_service._is_connected = True
        redis_service._vector_initialized = True
        redis_service._collections = {"test": "collection"}
        redis_service._operation_count = 100
        redis_service._cache_hits = 80
        redis_service._cache_misses = 20

        health = await redis_service.health_check()

        assert health["status"] == "healthy"
        assert health["redis_connected"] is True
        assert health["vector_store_initialized"] is True
        assert health["collections"] == ["test"]
        assert health["operation_count"] == 100
        assert health["cache_hits"] == 80
        assert health["cache_misses"] == 20
        assert health["cache_hit_ratio"] == 0.8

    async def test_health_check_disconnected(self, redis_service):
        """Test health check when disconnected"""
        redis_service._is_connected = False

        health = await redis_service.health_check()

        assert health["status"] == "disconnected"
        assert health["redis_connected"] is False

    async def test_get_performance_metrics(self, redis_service):
        """Test performance metrics collection"""
        redis_service._operation_count = 1000
        redis_service._error_count = 50
        redis_service._cache_hits = 800
        redis_service._cache_misses = 200
        redis_service._is_connected = True
        redis_service._vector_initialized = True
        redis_service._collections = {"reasoning": "col1", "world_models": "col2"}

        metrics = await redis_service.get_performance_metrics()

        assert metrics["operations"]["total_operations"] == 1000
        assert metrics["operations"]["total_errors"] == 50
        assert metrics["operations"]["error_rate"] == 0.05
        assert metrics["cache"]["cache_hits"] == 800
        assert metrics["cache"]["cache_misses"] == 200
        assert metrics["cache"]["hit_ratio"] == 0.8
        assert metrics["connection"]["is_connected"] is True
        assert metrics["connection"]["vector_initialized"] is True
        assert metrics["connection"]["active_collections"] == 2

    async def test_cleanup_expired_keys(self, redis_service, mock_redis_client):
        """Test cleanup of expired keys"""
        redis_service.redis_client = mock_redis_client
        redis_service._is_connected = True

        # Mock keys and TTL responses
        mock_redis_client.keys.return_value = ["rk:cache:model1", "rk:session:sess1", "rk:knowledge:item1"]

        def mock_ttl(key):
            if "cache" in key or "session" in key:
                return -1  # No TTL set, needs cleanup
            return 3600  # Has TTL

        mock_redis_client.ttl.side_effect = mock_ttl

        cleaned_count = await redis_service.cleanup_expired_keys()

        assert cleaned_count == 2  # cache and session keys
        # Verify expire was called for keys without TTL
        assert mock_redis_client.expire.call_count == 2

    # Factory Function Tests
    @patch("reasoning_kernel.services.unified_redis_service.UnifiedRedisService")
    async def test_create_unified_redis_service(self, mock_service_class):
        """Test factory function for creating unified service"""
        mock_service = AsyncMock()
        mock_service_class.return_value = mock_service

        # Use None embedding generator to avoid type issues
        await create_unified_redis_service(
            redis_url="redis://test:6379", embedding_generator=None, environment="development"
        )

        # Verify service was created and initialized
        mock_service_class.assert_called_once()
        mock_service.connect.assert_called_once()

    @patch("reasoning_kernel.services.unified_redis_service.UnifiedRedisService")
    async def test_create_redis_service_from_config(self, mock_service_class):
        """Test factory function with individual config parameters"""
        mock_service = AsyncMock()
        mock_service_class.return_value = mock_service

        await create_redis_service_from_config(
            host="test-host", port=6380, db=1, password="test-pass", max_connections=20
        )

        mock_service_class.assert_called_once()
        # Verify config was created with correct parameters
        call_args = mock_service_class.call_args[1]
        config = call_args["config"]
        assert config.host == "test-host"
        assert config.port == 6380
        assert config.db == 1
        assert config.password == "test-pass"
        assert config.max_connections == 20

        mock_service.connect.assert_called_once()

    # Error Handling Tests
    async def test_error_handling_store_operation(self, redis_service, mock_redis_client):
        """Test error handling in store operations"""
        redis_service.redis_client = mock_redis_client
        redis_service._is_connected = True
        mock_redis_client.setex.side_effect = Exception("Redis error")

        result = await redis_service.store_reasoning_chain("test", {"data": "test"})

        assert result is False
        assert redis_service._error_count == 1

    async def test_error_handling_retrieve_operation(self, redis_service, mock_redis_client):
        """Test error handling in retrieve operations"""
        redis_service.redis_client = mock_redis_client
        redis_service._is_connected = True
        mock_redis_client.get.side_effect = Exception("Redis error")

        result = await redis_service.get_reasoning_chain("test")

        assert result is None
        assert redis_service._error_count == 1

    async def test_operation_without_connection(self, redis_service):
        """Test operations when not connected"""
        redis_service._is_connected = False

        # All operations should return appropriate failure values
        assert await redis_service.store_reasoning_chain("test", {}) is False
        assert await redis_service.get_reasoning_chain("test") is None
        assert await redis_service.store_knowledge("test", {}) is False
        assert await redis_service.create_session("test", {}) is False
        assert await redis_service.get_session("test") is None
        assert await redis_service.cache_model_result("model", "hash", {}) is False
        assert await redis_service.get_cached_model_result("model", "hash") is None

        # Performance monitoring should still work
        health = await redis_service.health_check()
        assert health["status"] == "disconnected"

    # Data Structure Tests
    def test_reasoning_record_creation(self):
        """Test ReasoningRecord dataclass"""
        record = ReasoningRecord(
            pattern_type="analytical",
            question="What is X?",
            reasoning_steps="Step 1, Step 2",
            final_answer="X is Y",
            confidence_score=0.9,
        )

        assert record.pattern_type == "analytical"
        assert record.confidence_score == 0.9
        assert record.id  # Should have auto-generated ID
        assert record.created_at  # Should have timestamp
        assert isinstance(record.embedding, list)

    def test_world_model_record_creation(self):
        """Test WorldModelRecord dataclass"""
        record = WorldModelRecord(
            model_type="PROBABILISTIC",
            state_data='{"entities": ["A", "B"]}',
            confidence=0.85,
            context_keys='["key1", "key2"]',
        )

        assert record.model_type == "PROBABILISTIC"
        assert record.confidence == 0.85
        assert record.id  # Auto-generated
        assert record.last_updated  # Auto-generated timestamp
        assert isinstance(record.embedding, list)

    def test_exploration_record_creation(self):
        """Test ExplorationRecord dataclass"""
        record = ExplorationRecord(
            exploration_type="hypothesis_testing",
            hypothesis="H1: X causes Y",
            evidence="Evidence supporting H1",
            conclusion="H1 is likely true",
            exploration_path='["step1", "step2"]',
        )

        assert record.exploration_type == "hypothesis_testing"
        assert record.hypothesis == "H1: X causes Y"
        assert record.id  # Auto-generated
        assert record.created_at  # Auto-generated
        assert isinstance(record.embedding, list)

    def test_redis_connection_config(self):
        """Test RedisConnectionConfig"""
        config = RedisConnectionConfig(
            host="custom-host",
            port=6380,
            db=2,
            password="secret",
            max_connections=100,
            timeout=60.0,
            redis_url="redis://custom:6380",
        )

        assert config.host == "custom-host"
        assert config.port == 6380
        assert config.db == 2
        assert config.password == "secret"
        assert config.max_connections == 100
        assert config.timeout == 60.0
        assert config.redis_url == "redis://custom:6380"
        assert config.decode_responses is True  # Default


# Integration-style tests for consolidation verification
class TestRedisServiceConsolidation:
    """Test that consolidated service provides all original functionality"""

    async def test_replaces_redis_memory_service_functionality(self):
        """Verify all RedisMemoryService functionality is available"""
        service = UnifiedRedisService()

        # Check all key methods exist
        assert hasattr(service, "store_reasoning_chain")
        assert hasattr(service, "get_reasoning_chain")
        assert hasattr(service, "store_knowledge")
        assert hasattr(service, "retrieve_knowledge_by_type")
        assert hasattr(service, "cache_model_result")
        assert hasattr(service, "get_cached_model_result")
        assert hasattr(service, "create_session")
        assert hasattr(service, "get_session")

        # Check utility methods
        assert hasattr(service, "generate_cache_key")
        assert hasattr(service, "health_check")

    async def test_replaces_redis_vector_service_functionality(self):
        """Verify all RedisVectorService functionality is available"""
        service = UnifiedRedisService()

        # Check vector-specific methods
        assert hasattr(service, "initialize_vector_store")
        assert hasattr(service, "similarity_search")
        assert hasattr(service, "_get_or_create_collection")
        assert hasattr(service, "_store_reasoning_pattern_vector")
        assert hasattr(service, "_store_world_model_vector")

        # Check data structures
        assert ReasoningRecord
        assert WorldModelRecord
        assert ExplorationRecord

    async def test_replaces_production_redis_manager_functionality(self):
        """Verify all ProductionRedisManager functionality is available"""
        service = UnifiedRedisService()

        # Check production features
        assert hasattr(service, "store_world_model")
        assert hasattr(service, "retrieve_world_model")
        assert hasattr(service, "get_performance_metrics")
        assert hasattr(service, "_generate_scenario_hash")
        assert hasattr(service, "_get_ttl_for_abstraction_level")
        assert hasattr(service, "batch_store")
        assert hasattr(service, "cleanup_expired_keys")

        # Check monitoring capabilities
        assert service.enable_monitoring
        assert hasattr(service, "_increment_operation_count")
        assert hasattr(service, "_increment_error_count")

    async def test_connection_pooling_features(self):
        """Test connection pooling and performance features"""
        config = RedisConnectionConfig(max_connections=50)
        service = UnifiedRedisService(config=config)

        assert service.config.max_connections == 50
        assert hasattr(service, "_connection_pool")
        assert hasattr(service, "connect")
        assert hasattr(service, "disconnect")
        assert hasattr(service, "_ensure_connected")

    async def test_unified_configuration_system(self):
        """Test unified configuration handling"""
        service = UnifiedRedisService()

        # Should handle both URL and individual parameters
        assert hasattr(service.config, "redis_url")
        assert hasattr(service.config, "host")
        assert hasattr(service.config, "port")
        assert hasattr(service.config, "password")

        # Should have reasonable defaults
        assert service.config.host == "localhost"
        assert service.config.port == 6379
        assert service.config.max_connections == 50

    async def test_comprehensive_monitoring(self):
        """Test comprehensive monitoring across all operations"""
        service = UnifiedRedisService(enable_monitoring=True)

        # Should track all operation types
        assert service._operation_count == 0
        assert service._error_count == 0
        assert service._cache_hits == 0
        assert service._cache_misses == 0

        # Should have monitoring methods
        assert hasattr(service, "health_check")
        assert hasattr(service, "get_performance_metrics")

        # Test operation counting
        service._increment_operation_count("test_op")
        assert service._operation_count == 1
