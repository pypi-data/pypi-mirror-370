# Redis Memory Schema Design for Reasoning Kernel

**Author:** AI Assistant & Reasoning Kernel Team  
**Date:** 2025-01-27  
**Status:** Design Complete  

## Overview

This document defines the Redis memory schema for the Reasoning Kernel's hierarchical world model storage, thinking exploration patterns, and MSA pipeline integration. The schema supports:

- Hierarchical world models with level-based organization
- Thinking exploration patterns and triggers
- MSA pipeline results and intermediate states
- TTL-based lifecycle management
- Vector similarity search capabilities

## Core Data Types

### 1. World Models

World models are stored with hierarchical organization supporting four levels:

**Key Pattern:** `wm:{level}:{domain}:{model_id}`

**Levels:**

- `instance` - Specific situation instances (TTL: 1 hour)
- `category` - Categories of similar situations (TTL: 1 day)  
- `domain` - Domain-level models (TTL: 1 week)
- `abstract` - Abstract reasoning patterns (TTL: 1 month)

**Structure:**

```json
{
  "model_id": "wm_instance_medical_001",
  "model_level": "instance",
  "model_type": "diagnostic",
  "structure": {
    "variables": ["symptoms", "tests", "diagnosis"],
    "dependencies": [["symptoms", "tests"], ["tests", "diagnosis"]]
  },
  "parameters": {
    "prior_distributions": {...},
    "likelihood_functions": {...}
  },
  "confidence_score": 0.85,
  "evidence_history": [
    {
      "evidence_id": "ev_001",
      "evidence_type": "observational", 
      "content": "Patient presents with fever",
      "reliability": 0.9,
      "source": "clinical_observation",
      "timestamp": "2025-01-27T10:00:00Z"
    }
  ],
  "parent_models": ["wm_category_medical_002"],
  "child_models": [],
  "created_at": "2025-01-27T09:00:00Z",
  "last_updated": "2025-01-27T10:30:00Z",
  "metadata": {
    "domain": "medical_diagnosis",
    "context_tags": ["symptoms", "differential_diagnosis"],
    "usage_count": 5
  }
}
```

### 2. Exploration Triggers

**Key Pattern:** `trigger:{trigger_type}:{scenario_hash}`

**Trigger Types:**

- `novelty` - Novel situation detection
- `dynamics` - Dynamic pattern changes
- `sparsity` - Sparse data conditions
- `complexity` - High complexity scenarios

**Structure:**

```json
{
  "trigger_id": "trig_novelty_001",
  "trigger_type": "novelty",
  "scenario_text": "Patient with rare genetic condition",
  "domain_context": "medical_genetics",
  "detection_confidence": 0.92,
  "trigger_context": {
    "novelty_score": 0.88,
    "similarity_threshold": 0.3,
    "reference_models": ["wm_category_genetics_001"],
    "detection_method": "embedding_similarity"
  },
  "analysis_timestamp": "2025-01-27T10:00:00Z",
  "metadata": {
    "processing_time_ms": 150,
    "trigger_strength": "high"
  }
}
```

### 3. Exploration Patterns

**Key Pattern:** `pattern:{pattern_type}:{pattern_id}`

**Pattern Types:**

- `reasoning` - Common reasoning patterns
- `solution` - Solution approaches
- `heuristic` - Problem-solving heuristics

**Structure:**

```json
{
  "pattern_id": "pat_reasoning_001",
  "pattern_type": "reasoning",
  "name": "differential_diagnosis_pattern",
  "description": "Systematic approach to medical differential diagnosis",
  "pattern_structure": {
    "steps": [
      "gather_symptoms",
      "identify_key_features", 
      "generate_hypotheses",
      "order_diagnostic_tests",
      "refine_diagnosis"
    ],
    "decision_points": [
      {
        "step": "generate_hypotheses",
        "criteria": "symptom_compatibility",
        "threshold": 0.7
      }
    ]
  },
  "usage_frequency": 15,
  "success_rate": 0.89,
  "applicable_domains": ["medical_diagnosis", "clinical_reasoning"],
  "created_at": "2025-01-27T08:00:00Z",
  "last_used": "2025-01-27T10:15:00Z"
}
```

### 4. MSA Pipeline Results

**Key Pattern:** `msa:{pipeline_id}:{stage}:{result_id}`

**Pipeline Stages:**

- `parsing` - Vignette parsing results
- `knowledge` - Retrieved knowledge
- `synthesis` - Generated models and programs
- `inference` - Execution results

**Structure:**

```json
{
  "pipeline_id": "msa_run_001",
  "stage": "synthesis", 
  "result_id": "synth_001",
  "vignette_id": "vig_medical_001",
  "result_data": {
    "generated_program": "# Probabilistic program for diagnosis...",
    "dependency_graph": {...},
    "confidence_estimates": {...}
  },
  "performance_metrics": {
    "execution_time_ms": 2500,
    "memory_usage_mb": 45,
    "accuracy_score": 0.91
  },
  "created_at": "2025-01-27T09:30:00Z",
  "expires_at": "2025-01-28T09:30:00Z"
}
```

### 5. Agent Coordination State

**Key Pattern:** `agent:{session_id}:{agent_type}:{state_id}`

**Agent Types:**

- `model_synthesis` - Model synthesis agents
- `probabilistic_reasoning` - Reasoning agents
- `evaluation` - Evaluation agents
- `knowledge_retrieval` - Knowledge agents

**Structure:**

```json
{
  "agent_id": "agent_synthesis_001",
  "agent_type": "model_synthesis",
  "session_id": "session_abc123",
  "state": "processing",
  "current_task": {
    "task_id": "task_001",
    "description": "Generate probabilistic model for medical case",
    "assigned_at": "2025-01-27T10:00:00Z",
    "expected_completion": "2025-01-27T10:05:00Z"
  },
  "message_history": [
    {
      "timestamp": "2025-01-27T10:01:00Z",
      "from": "agent_knowledge_001",
      "content": "Retrieved 5 relevant knowledge items",
      "message_type": "info"
    }
  ],
  "performance_stats": {
    "tasks_completed": 12,
    "average_response_time_ms": 800,
    "error_count": 0
  }
}
```

## Index Structures

### 1. Model Similarity Index

**Key Pattern:** `idx:similarity:{domain}:{embedding_hash}`

Used for finding similar world models via vector similarity search.

```json
{
  "model_id": "wm_instance_medical_001",
  "domain": "medical_diagnosis",
  "embedding_vector": [0.1, 0.2, ...],  // 384-dimensional
  "model_level": "instance",
  "confidence_score": 0.85,
  "last_updated": "2025-01-27T10:30:00Z"
}
```

### 2. Pattern Usage Index

**Key Pattern:** `idx:pattern_usage:{domain}:{time_bucket}`

Tracks pattern usage for learning and optimization.

```json
{
  "time_bucket": "2025-01-27T10",  // Hourly buckets
  "domain": "medical_diagnosis",
  "patterns": [
    {
      "pattern_id": "pat_reasoning_001",
      "usage_count": 3,
      "success_rate": 1.0
    }
  ]
}
```

### 3. Trigger History Index

**Key Pattern:** `idx:triggers:{domain}:{date}`

Daily index of exploration triggers for analysis.

```json
{
  "date": "2025-01-27",
  "domain": "medical_diagnosis",
  "triggers": [
    {
      "trigger_id": "trig_novelty_001",
      "trigger_type": "novelty",
      "confidence": 0.92,
      "timestamp": "2025-01-27T10:00:00Z"
    }
  ],
  "summary": {
    "total_triggers": 5,
    "novelty_count": 2,
    "dynamics_count": 2,
    "sparsity_count": 1
  }
}
```

## TTL Policies

### Time-Based Expiration

| Data Type | Default TTL | Configurable |
|-----------|-------------|--------------|
| Instance Models | 1 hour | Yes |
| Category Models | 1 day | Yes |  
| Domain Models | 1 week | Yes |
| Abstract Models | 1 month | Yes |
| Exploration Triggers | 1 day | Yes |
| MSA Pipeline Results | 1 day | Yes |
| Agent Coordination State | 1 hour | Yes |
| Similarity Indices | 1 week | Yes |

### Usage-Based Retention

- Frequently accessed models get TTL extension
- High-confidence models get longer retention
- Successful patterns get priority retention

## Collection Organization

### Hash Tags for Efficient Querying

**Domain Collections:** Group related models by domain

- `domain:medical_diagnosis`
- `domain:financial_analysis`  
- `domain:scientific_reasoning`

**Level Collections:** Group models by abstraction level

- `level:instance`
- `level:category`
- `level:domain`
- `level:abstract`

**Performance Collections:** Group by performance metrics

- `high_confidence` (confidence > 0.8)
- `frequently_used` (usage_count > 10)
- `recently_successful` (recent success rate > 0.9)

## Access Patterns

### 1. Model Retrieval by Similarity

```python
# Find similar models in domain
similar_models = redis.zrangebyscore(
    f"idx:similarity:{domain}:*", 
    min_similarity, 
    max_similarity
)
```

### 2. Hierarchical Model Navigation

```python  
# Get child models
child_models = redis.smembers(f"children:{model_id}")

# Get parent models
parent_models = redis.smembers(f"parents:{model_id}")
```

### 3. Pattern Usage Analysis

```python
# Get pattern usage for domain and time range
usage_data = redis.mget([
    f"idx:pattern_usage:{domain}:{hour}" 
    for hour in time_range
])
```

## Performance Considerations

### Memory Optimization

- Use Redis Hash data types for structured data
- Implement compression for large embedding vectors
- Use pipeline operations for batch updates
- Set appropriate TTL to prevent memory bloat

### Query Performance  

- Pre-compute common similarity indices
- Use Redis Sorted Sets for range queries
- Implement connection pooling for high-concurrency access
- Cache frequently accessed models in application memory

### Scalability

- Support Redis Cluster for horizontal scaling
- Implement data partitioning by domain
- Use Redis Streams for real-time pattern updates
- Design for eventual consistency in distributed scenarios

## Configuration Parameters

```python
REDIS_MEMORY_CONFIG = {
    "connection": {
        "host": "localhost",
        "port": 6379,
        "db": 0,
        "max_connections": 100
    },
    "ttl": {
        "instance_models": 3600,      # 1 hour
        "category_models": 86400,     # 1 day  
        "domain_models": 604800,      # 1 week
        "abstract_models": 2592000,   # 1 month
        "exploration_triggers": 86400, # 1 day
        "msa_results": 86400,         # 1 day
        "agent_state": 3600           # 1 hour
    },
    "indexing": {
        "similarity_threshold": 0.7,
        "max_similar_models": 10,
        "embedding_dimensions": 384
    },
    "performance": {
        "batch_size": 100,
        "pipeline_size": 50,
        "compression_threshold": 1024  # bytes
    }
}
```

## Implementation Status

- [x] **Schema Design Complete** - All data structures defined
- [x] **TTL Policies Defined** - Lifecycle management specified  
- [x] **Index Structures Planned** - Performance optimization covered
- [x] **Access Patterns Documented** - Query patterns identified
- [x] **Configuration Parameterized** - Flexible deployment support

## Next Steps

1. **Implement RedisMemoryManager class** - Core storage operations
2. **Create HierarchicalModelIndex** - Efficient model organization
3. **Add SimilaritySearch service** - Vector-based model retrieval
4. **Build PatternLearning module** - Usage-based optimization
5. **Integrate with existing MSA pipeline** - Seamless data flow

This schema provides a solid foundation for Phase 2 implementation of hierarchical world models and thinking exploration capabilities.
