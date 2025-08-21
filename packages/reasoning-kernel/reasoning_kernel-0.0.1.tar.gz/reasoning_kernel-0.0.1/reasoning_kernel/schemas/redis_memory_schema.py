"""
Redis Memory Schema for Reasoning Kernel

This module defines the comprehensive Redis schema for storing hierarchical world models,
exploration patterns, agent memories, and reasoning artifacts. Optimized for MSA pipeline
performance with proper TTL policies and indexing strategies.

Key Components:
- Hierarchical World Model Storage (Ω1 to Ωn levels)
- Exploration Pattern Caching and Retrieval
- Agent Memory and Context Management
- Reasoning Session Tracking
- Performance Metrics and Analytics

Author: AI Assistant & Reasoning Kernel Team
Date: 2025-08-15
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class RedisCollectionType(Enum):
    """Types of Redis collections for different data structures"""

    HASH = "hash"  # For structured data with fields
    ZSET = "zset"  # For ranked/scored data
    SET = "set"  # For unique collections
    LIST = "list"  # For ordered sequences
    STRING = "string"  # For simple values
    STREAM = "stream"  # For event streams


class TTLPolicy(Enum):
    """TTL policies for different types of data"""

    SHORT = "short"  # 1 hour - temporary computations
    MEDIUM = "medium"  # 24 hours - session data
    LONG = "long"  # 7 days - exploration patterns
    PERMANENT = "permanent"  # No expiry - core knowledge
    ADAPTIVE = "adaptive"  # Based on access patterns


@dataclass
class RedisKeyPattern:
    """Defines a Redis key pattern with metadata"""

    pattern: str
    description: str
    collection_type: RedisCollectionType
    ttl_policy: TTLPolicy
    indexing_fields: List[str]
    example_key: str


@dataclass
class RedisSchemaConfig:
    """Configuration for Redis schema with TTL values"""

    short_ttl: int = 3600  # 1 hour
    medium_ttl: int = 86400  # 24 hours
    long_ttl: int = 604800  # 7 days
    adaptive_base_ttl: int = 43200  # 12 hours
    adaptive_max_ttl: int = 2592000  # 30 days
    namespace_prefix: str = "reasoning:"


class ReasoningKernelRedisSchema:
    """
    Comprehensive Redis schema for the Reasoning Kernel system.

    This schema is designed for:
    - High-performance hierarchical world model storage
    - Efficient exploration pattern caching
    - Scalable agent memory management
    - Production-ready reasoning pipelines
    """

    def __init__(self, config: Optional[RedisSchemaConfig] = None):
        self.config = config or RedisSchemaConfig()
        self._define_schema()

    def _define_schema(self):
        """Define all Redis key patterns and their configurations"""

        # Hierarchical World Models (Core Knowledge Storage)
        self.world_models = {
            "instance_models": RedisKeyPattern(
                pattern=f"{self.config.namespace_prefix}world_model:instance:{{scenario_hash}}:{{level}}",
                description="Instance-level world models (Ω1) for specific scenarios",
                collection_type=RedisCollectionType.HASH,
                ttl_policy=TTLPolicy.LONG,
                indexing_fields=["scenario_type", "confidence", "last_updated", "abstraction_level"],
                example_key=f"{self.config.namespace_prefix}world_model:instance:abc123:omega1",
            ),
            "abstract_models": RedisKeyPattern(
                pattern=f"{self.config.namespace_prefix}world_model:abstract:{{domain}}:{{level}}:{{model_id}}",
                description="Abstract hierarchical models (Ω2-Ωn) for domain generalizations",
                collection_type=RedisCollectionType.HASH,
                ttl_policy=TTLPolicy.PERMANENT,
                indexing_fields=["domain", "abstraction_level", "generalization_count", "accuracy"],
                example_key=f"{self.config.namespace_prefix}world_model:abstract:physics:omega3:model_456",
            ),
            "model_relationships": RedisKeyPattern(
                pattern=f"{self.config.namespace_prefix}world_model:relations:{{parent_id}}",
                description="Hierarchical relationships between world models",
                collection_type=RedisCollectionType.ZSET,
                ttl_policy=TTLPolicy.LONG,
                indexing_fields=["similarity_score", "abstraction_distance"],
                example_key=f"{self.config.namespace_prefix}world_model:relations:model_123",
            ),
            "model_evidence": RedisKeyPattern(
                pattern=f"{self.config.namespace_prefix}world_model:evidence:{{model_id}}",
                description="Evidence and support data for world model validation",
                collection_type=RedisCollectionType.LIST,
                ttl_policy=TTLPolicy.MEDIUM,
                indexing_fields=["evidence_type", "reliability", "timestamp"],
                example_key=f"{self.config.namespace_prefix}world_model:evidence:model_789",
            ),
        }

        # Exploration Patterns and Triggers
        self.exploration = {
            "trigger_patterns": RedisKeyPattern(
                pattern=f"{self.config.namespace_prefix}exploration:triggers:{{trigger_type}}:{{pattern_id}}",
                description="Exploration trigger patterns for novelty, dynamics, sparsity detection",
                collection_type=RedisCollectionType.HASH,
                ttl_policy=TTLPolicy.LONG,
                indexing_fields=["trigger_type", "success_rate", "domain", "complexity"],
                example_key=f"{self.config.namespace_prefix}exploration:triggers:novelty:pattern_abc",
            ),
            "exploration_sessions": RedisKeyPattern(
                pattern=f"{self.config.namespace_prefix}exploration:session:{{session_id}}",
                description="Active exploration session data and state",
                collection_type=RedisCollectionType.HASH,
                ttl_policy=TTLPolicy.MEDIUM,
                indexing_fields=["start_time", "session_type", "progress", "agent_count"],
                example_key=f"{self.config.namespace_prefix}exploration:session:sess_20250815_001",
            ),
            "adhoc_models": RedisKeyPattern(
                pattern=f"{self.config.namespace_prefix}exploration:adhoc:{{scenario_hash}}",
                description="Ad-hoc synthesized models for novel situations",
                collection_type=RedisCollectionType.HASH,
                ttl_policy=TTLPolicy.ADAPTIVE,
                indexing_fields=["synthesis_quality", "reuse_count", "performance"],
                example_key=f"{self.config.namespace_prefix}exploration:adhoc:novel_xyz789",
            ),
            "pattern_library": RedisKeyPattern(
                pattern=f"{self.config.namespace_prefix}exploration:library:{{domain}}",
                description="Curated library of successful exploration patterns by domain",
                collection_type=RedisCollectionType.ZSET,
                ttl_policy=TTLPolicy.PERMANENT,
                indexing_fields=["success_score", "usage_frequency", "effectiveness"],
                example_key=f"{self.config.namespace_prefix}exploration:library:robotics",
            ),
        }

        # Agent Memory and Context Management
        self.agents = {
            "agent_memories": RedisKeyPattern(
                pattern=f"{self.config.namespace_prefix}agent:memory:{{agent_type}}:{{agent_id}}",
                description="Individual agent memory stores for context and learning",
                collection_type=RedisCollectionType.HASH,
                ttl_policy=TTLPolicy.LONG,
                indexing_fields=["agent_type", "memory_size", "last_access", "priority"],
                example_key=f"{self.config.namespace_prefix}agent:memory:synthesis:agent_001",
            ),
            "agent_conversations": RedisKeyPattern(
                pattern=f"{self.config.namespace_prefix}agent:conversation:{{session_id}}:{{turn_id}}",
                description="Agent conversation history for multi-agent interactions",
                collection_type=RedisCollectionType.LIST,
                ttl_policy=TTLPolicy.MEDIUM,
                indexing_fields=["timestamp", "agent_id", "message_type"],
                example_key=f"{self.config.namespace_prefix}agent:conversation:sess_123:turn_05",
            ),
            "agent_capabilities": RedisKeyPattern(
                pattern=f"{self.config.namespace_prefix}agent:capabilities:{{agent_type}}",
                description="Agent capability profiles and performance metrics",
                collection_type=RedisCollectionType.HASH,
                ttl_policy=TTLPolicy.PERMANENT,
                indexing_fields=["capability_type", "performance_score", "specialization"],
                example_key=f"{self.config.namespace_prefix}agent:capabilities:probabilistic",
            ),
            "coordination_state": RedisKeyPattern(
                pattern=f"{self.config.namespace_prefix}agent:coordination:{{session_id}}",
                description="Multi-agent coordination state and workflow management",
                collection_type=RedisCollectionType.HASH,
                ttl_policy=TTLPolicy.SHORT,
                indexing_fields=["coordinator", "active_agents", "workflow_state"],
                example_key=f"{self.config.namespace_prefix}agent:coordination:coord_456",
            ),
        }

        # Reasoning Sessions and Results
        self.reasoning = {
            "reasoning_sessions": RedisKeyPattern(
                pattern=f"{self.config.namespace_prefix}reasoning:session:{{session_id}}",
                description="Complete reasoning session data and metadata",
                collection_type=RedisCollectionType.HASH,
                ttl_policy=TTLPolicy.LONG,
                indexing_fields=["session_type", "duration", "success", "complexity"],
                example_key=f"{self.config.namespace_prefix}reasoning:session:reasoning_abc123",
            ),
            "reasoning_results": RedisKeyPattern(
                pattern=f"{self.config.namespace_prefix}reasoning:results:{{session_id}}:{{step_id}}",
                description="Step-by-step reasoning results and intermediate outputs",
                collection_type=RedisCollectionType.HASH,
                ttl_policy=TTLPolicy.MEDIUM,
                indexing_fields=["step_type", "confidence", "processing_time"],
                example_key=f"{self.config.namespace_prefix}reasoning:results:sess_123:step_002",
            ),
            "reasoning_cache": RedisKeyPattern(
                pattern=f"{self.config.namespace_prefix}reasoning:cache:{{scenario_hash}}",
                description="Cached reasoning results for performance optimization",
                collection_type=RedisCollectionType.HASH,
                ttl_policy=TTLPolicy.ADAPTIVE,
                indexing_fields=["cache_hits", "last_access", "result_quality"],
                example_key=f"{self.config.namespace_prefix}reasoning:cache:cache_xyz789",
            ),
            "reasoning_analytics": RedisKeyPattern(
                pattern=f"{self.config.namespace_prefix}reasoning:analytics:{{date}}",
                description="Daily reasoning analytics and performance metrics",
                collection_type=RedisCollectionType.HASH,
                ttl_policy=TTLPolicy.LONG,
                indexing_fields=["total_sessions", "avg_duration", "success_rate"],
                example_key=f"{self.config.namespace_prefix}reasoning:analytics:20250815",
            ),
        }

        # Performance and Monitoring
        self.monitoring = {
            "performance_metrics": RedisKeyPattern(
                pattern=f"{self.config.namespace_prefix}metrics:performance:{{component}}:{{timestamp}}",
                description="Real-time performance metrics for system components",
                collection_type=RedisCollectionType.HASH,
                ttl_policy=TTLPolicy.MEDIUM,
                indexing_fields=["component", "metric_type", "value", "timestamp"],
                example_key=f"{self.config.namespace_prefix}metrics:performance:worldmodel:1692057600",
            ),
            "system_health": RedisKeyPattern(
                pattern=f"{self.config.namespace_prefix}health:{{service}}",
                description="System health indicators and status information",
                collection_type=RedisCollectionType.HASH,
                ttl_policy=TTLPolicy.SHORT,
                indexing_fields=["status", "last_heartbeat", "error_count"],
                example_key=f"{self.config.namespace_prefix}health:thinking_kernel",
            ),
            "usage_patterns": RedisKeyPattern(
                pattern=f"{self.config.namespace_prefix}usage:{{feature}}:{{timeframe}}",
                description="Feature usage patterns and access analytics",
                collection_type=RedisCollectionType.ZSET,
                ttl_policy=TTLPolicy.LONG,
                indexing_fields=["usage_count", "user_id", "feature_type"],
                example_key=f"{self.config.namespace_prefix}usage:exploration:daily",
            ),
        }

    def get_ttl_seconds(self, ttl_policy: TTLPolicy, access_count: int = 0) -> Optional[int]:
        """Get TTL in seconds based on policy and usage patterns"""
        if ttl_policy == TTLPolicy.PERMANENT:
            return None
        elif ttl_policy == TTLPolicy.SHORT:
            return self.config.short_ttl
        elif ttl_policy == TTLPolicy.MEDIUM:
            return self.config.medium_ttl
        elif ttl_policy == TTLPolicy.LONG:
            return self.config.long_ttl
        elif ttl_policy == TTLPolicy.ADAPTIVE:
            # Adaptive TTL based on access patterns
            base_ttl = self.config.adaptive_base_ttl
            if access_count > 10:
                # Frequently accessed items get longer TTL
                return min(base_ttl * (1 + access_count // 10), self.config.adaptive_max_ttl)
            return base_ttl
        return self.config.medium_ttl

    def generate_key(self, pattern: RedisKeyPattern, **kwargs) -> str:
        """Generate a Redis key from a pattern with provided parameters"""
        try:
            return pattern.pattern.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing required parameter for key pattern: {e}")

    def get_all_patterns(self) -> Dict[str, RedisKeyPattern]:
        """Get all defined Redis key patterns across all categories"""
        all_patterns = {}
        all_patterns.update(self.world_models)
        all_patterns.update(self.exploration)
        all_patterns.update(self.agents)
        all_patterns.update(self.reasoning)
        all_patterns.update(self.monitoring)
        return all_patterns

    def generate_schema_documentation(self) -> str:
        """Generate comprehensive documentation for the Redis schema"""
        doc = "# Reasoning Kernel Redis Schema Documentation\n\n"
        doc += f"**Namespace Prefix:** `{self.config.namespace_prefix}`\n\n"

        categories = [
            ("World Models", self.world_models),
            ("Exploration Patterns", self.exploration),
            ("Agent Management", self.agents),
            ("Reasoning Sessions", self.reasoning),
            ("Monitoring & Analytics", self.monitoring),
        ]

        for category_name, patterns in categories:
            doc += f"## {category_name}\n\n"
            for pattern_name, pattern in patterns.items():
                doc += f"### {pattern_name}\n"
                doc += f"- **Pattern:** `{pattern.pattern}`\n"
                doc += f"- **Type:** {pattern.collection_type.value}\n"
                doc += f"- **TTL Policy:** {pattern.ttl_policy.value}\n"
                doc += f"- **Description:** {pattern.description}\n"
                doc += f"- **Example:** `{pattern.example_key}`\n"
                doc += f"- **Indexed Fields:** {', '.join(pattern.indexing_fields)}\n\n"

        return doc


# Convenience factory functions
def create_production_schema() -> ReasoningKernelRedisSchema:
    """Create a production-optimized Redis schema"""
    config = RedisSchemaConfig(
        short_ttl=3600,  # 1 hour
        medium_ttl=86400,  # 24 hours
        long_ttl=604800,  # 7 days
        adaptive_base_ttl=43200,  # 12 hours
        adaptive_max_ttl=2592000,  # 30 days
        namespace_prefix="reasoning:prod:",
    )
    return ReasoningKernelRedisSchema(config)


def create_development_schema() -> ReasoningKernelRedisSchema:
    """Create a development-optimized Redis schema with shorter TTLs"""
    config = RedisSchemaConfig(
        short_ttl=300,  # 5 minutes
        medium_ttl=3600,  # 1 hour
        long_ttl=86400,  # 24 hours
        adaptive_base_ttl=1800,  # 30 minutes
        adaptive_max_ttl=604800,  # 7 days
        namespace_prefix="reasoning:dev:",
    )
    return ReasoningKernelRedisSchema(config)


def create_testing_schema() -> ReasoningKernelRedisSchema:
    """Create a testing-optimized Redis schema with very short TTLs"""
    config = RedisSchemaConfig(
        short_ttl=60,  # 1 minute
        medium_ttl=300,  # 5 minutes
        long_ttl=3600,  # 1 hour
        adaptive_base_ttl=180,  # 3 minutes
        adaptive_max_ttl=7200,  # 2 hours
        namespace_prefix="reasoning:test:",
    )
    return ReasoningKernelRedisSchema(config)
