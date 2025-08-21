"""
Schemas Module for Reasoning Kernel

This module contains data schemas, Redis schema definitions, and data structure
specifications for the Reasoning Kernel system.

Key Components:
- Redis Memory Schema: Production-ready Redis key patterns and TTL policies
- Data Models: Pydantic models for structured data validation
- Configuration Schemas: System configuration and settings structures

Author: AI Assistant & Reasoning Kernel Team
Date: 2025-08-15
"""

from .redis_memory_schema import create_development_schema
from .redis_memory_schema import create_production_schema
from .redis_memory_schema import create_testing_schema
from .redis_memory_schema import ReasoningKernelRedisSchema
from .redis_memory_schema import RedisCollectionType
from .redis_memory_schema import RedisKeyPattern
from .redis_memory_schema import RedisSchemaConfig
from .redis_memory_schema import TTLPolicy


__all__ = [
    "ReasoningKernelRedisSchema",
    "RedisSchemaConfig",
    "RedisKeyPattern",
    "RedisCollectionType",
    "TTLPolicy",
    "create_production_schema",
    "create_development_schema",
    "create_testing_schema",
]
