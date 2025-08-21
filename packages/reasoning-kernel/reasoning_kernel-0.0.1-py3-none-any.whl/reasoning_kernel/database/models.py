"""
Database models for long-term memory storage
PostgreSQL models for persistent storage of reasoning chains and knowledge
"""

import uuid

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import JSON
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy import Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


Base = declarative_base()

# Association tables for many-to-many relationships
knowledge_tags = Table(
    'knowledge_tags',
    Base.metadata,
    Column('knowledge_id', String(36), ForeignKey('knowledge_entities.id', ondelete='CASCADE')),
    Column('tag_id', String(36), ForeignKey('tags.id', ondelete='CASCADE')),
    Index('idx_knowledge_tags', 'knowledge_id', 'tag_id')
)

reasoning_knowledge = Table(
    'reasoning_knowledge',
    Base.metadata,
    Column('reasoning_id', String(36), ForeignKey('reasoning_chains.id', ondelete='CASCADE')),
    Column('knowledge_id', String(36), ForeignKey('knowledge_entities.id', ondelete='CASCADE')),
    Index('idx_reasoning_knowledge', 'reasoning_id', 'knowledge_id')
)

class ReasoningChain(Base):
    """Store complete reasoning chains for long-term memory"""
    __tablename__ = 'reasoning_chains'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(100), ForeignKey('sessions.id'), nullable=True, index=True)
    scenario = Column(Text, nullable=False)
    
    # Mode 1 outputs
    mode1_entities = Column(JSON)
    mode1_relationships = Column(JSON)
    mode1_causal_factors = Column(JSON)
    mode1_constraints = Column(JSON)
    mode1_domain_knowledge = Column(JSON)
    
    # Mode 2 outputs
    mode2_model_structure = Column(JSON)
    mode2_predictions = Column(JSON)
    mode2_uncertainties = Column(JSON)
    mode2_success = Column(String(10))
    
    # Final reasoning
    final_summary = Column(Text)
    final_insights = Column(JSON)
    final_recommendations = Column(JSON)
    final_uncertainty = Column(JSON)
    
    # Metadata
    reasoning_steps = Column(JSON)
    total_duration_ms = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    knowledge_entities = relationship(
        "KnowledgeEntity",
        secondary=reasoning_knowledge,
        back_populates="reasoning_chains"
    )
    session = relationship("Session", back_populates="reasoning_chains")
    
    __table_args__ = (
        Index('idx_reasoning_created', 'created_at'),
        Index('idx_reasoning_scenario', 'scenario'),
    )

class KnowledgeEntity(Base):
    """Store extracted knowledge entities for reuse"""
    __tablename__ = 'knowledge_entities'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_type = Column(String(50), nullable=False, index=True)  # concept, entity, process, etc.
    name = Column(String(200), nullable=False)
    description = Column(Text)
    domain = Column(String(100), index=True)
    
    # Properties and attributes
    properties = Column(JSON)
    relationships = Column(JSON)
    
    # Embedding for semantic search (stored as JSON array)
    embedding = Column(JSON)
    
    # Usage tracking
    usage_count = Column(Integer, default=1)
    last_used = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    tags = relationship("Tag", secondary=knowledge_tags, back_populates="knowledge_entities")
    reasoning_chains = relationship(
        "ReasoningChain",
        secondary=reasoning_knowledge,
        back_populates="knowledge_entities"
    )
    
    __table_args__ = (
        Index('idx_knowledge_type_name', 'entity_type', 'name'),
        Index('idx_knowledge_domain', 'domain'),
        Index('idx_knowledge_usage', 'usage_count'),
    )

class Tag(Base):
    """Tags for categorizing knowledge"""
    __tablename__ = 'tags'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(50), unique=True, nullable=False, index=True)
    category = Column(String(50))  # ml, statistics, business, etc.
    usage_count = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    knowledge_entities = relationship(
        "KnowledgeEntity",
        secondary=knowledge_tags,
        back_populates="tags"
    )

class Session(Base):
    """User sessions for tracking reasoning history"""
    __tablename__ = 'sessions'
    
    id = Column(String(100), primary_key=True)
    user_id = Column(String(100), index=True)
    purpose = Column(String(200))
    context = Column(JSON)
    
    # Session state
    status = Column(String(20), default='active')  # active, completed, failed
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True))
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    
    # Statistics
    total_reasoning_chains = Column(Integer, default=0)
    total_knowledge_extracted = Column(Integer, default=0)
    
    # Relationships
    reasoning_chains = relationship("ReasoningChain", back_populates="session")
    
    __table_args__ = (
        Index('idx_session_user', 'user_id'),
        Index('idx_session_status', 'status'),
        Index('idx_session_activity', 'last_activity'),
    )

class ModelCache(Base):
    """Cache for model predictions to avoid recomputation"""
    __tablename__ = 'model_cache'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    model_name = Column(String(100), nullable=False, index=True)
    model_version = Column(String(50))
    input_hash = Column(String(64), nullable=False, unique=True, index=True)
    
    # Input/Output
    input_data = Column(JSON, nullable=False)
    output_data = Column(JSON, nullable=False)
    
    # Performance metrics
    inference_time_ms = Column(Float)
    token_count = Column(Integer)
    
    # Cache management
    hit_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
    
    __table_args__ = (
        Index('idx_cache_model_hash', 'model_name', 'input_hash'),
        Index('idx_cache_expires', 'expires_at'),
    )

class ReasoningPattern(Base):
    """Store successful reasoning patterns for learning"""
    __tablename__ = 'reasoning_patterns'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    pattern_name = Column(String(200), nullable=False)
    pattern_type = Column(String(50))  # decision, analysis, prediction, etc.
    
    # Pattern structure
    scenario_template = Column(Text)
    entity_patterns = Column(JSON)
    relationship_patterns = Column(JSON)
    model_specifications = Column(JSON)
    
    # Performance metrics
    success_rate = Column(Float)
    avg_duration_ms = Column(Float)
    usage_count = Column(Integer, default=0)
    
    # Learning
    confidence_score = Column(Float)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_pattern_type', 'pattern_type'),
        Index('idx_pattern_success', 'success_rate'),
        Index('idx_pattern_usage', 'usage_count'),
    )

class MemoryIndex(Base):
    """Index for fast memory retrieval using embeddings"""
    __tablename__ = 'memory_index'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    memory_type = Column(String(50), nullable=False, index=True)  # reasoning, knowledge, pattern
    memory_id = Column(String(36), nullable=False)
    
    # Search optimization
    summary = Column(Text)
    keywords = Column(JSON)
    embedding = Column(JSON)  # Vector embedding for semantic search
    
    # Relevance scoring
    relevance_score = Column(Float)
    access_count = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_memory_type_id', 'memory_type', 'memory_id'),
        Index('idx_memory_relevance', 'relevance_score'),
    )