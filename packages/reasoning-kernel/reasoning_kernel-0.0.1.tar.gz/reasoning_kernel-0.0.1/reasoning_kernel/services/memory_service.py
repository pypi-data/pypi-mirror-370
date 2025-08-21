"""
Long-term memory service integrating PostgreSQL and Redis
PostgreSQL for permanent storage, Redis for fast caching
"""

from datetime import datetime
import hashlib
import logging
from typing import Any, Dict, List, Optional

from reasoning_kernel.database.models import KnowledgeEntity
from reasoning_kernel.database.models import ModelCache
from reasoning_kernel.database.models import ReasoningChain
from reasoning_kernel.database.models import ReasoningPattern
from reasoning_kernel.database.models import Session as DBSession
from reasoning_kernel.services.redis_service import RedisMemoryService
from sqlalchemy import desc
from sqlalchemy import func
from sqlalchemy.orm import Session


logger = logging.getLogger(__name__)


class LongTermMemoryService:
    """
    Hybrid memory service: PostgreSQL for persistence, Redis for speed
    """

    def __init__(self, db_session: Session, redis_service: RedisMemoryService):
        self.db = db_session
        self.redis = redis_service
        logger.info("Long-term memory service initialized")

    # ============================================
    # REASONING CHAIN OPERATIONS
    # ============================================

    async def store_reasoning_chain(self, chain_data: Dict[str, Any]) -> str:
        """Store reasoning chain in both PostgreSQL and Redis"""
        try:
            # Create database record
            chain = ReasoningChain(
                session_id=chain_data.get("session_id"),
                scenario=chain_data.get("scenario", ""),
                mode1_entities=chain_data.get("knowledge_base", {}).get("entities", []),
                mode1_relationships=chain_data.get("knowledge_base", {}).get("relationships", []),
                mode1_causal_factors=chain_data.get("knowledge_base", {}).get("causal_factors", []),
                mode1_constraints=chain_data.get("knowledge_base", {}).get("constraints", []),
                mode1_domain_knowledge=chain_data.get("knowledge_base", {}).get("domain_knowledge", []),
                mode2_model_structure=chain_data.get("probabilistic_analysis", {}).get("model_structure", {}),
                mode2_predictions=chain_data.get("probabilistic_analysis", {}).get("predictions", {}),
                mode2_uncertainties=chain_data.get("probabilistic_analysis", {}).get("uncertainty_analysis", {}),
                mode2_success=str(chain_data.get("probabilistic_analysis", {}).get("success", False)),
                final_summary=chain_data.get("final_reasoning", {}).get("summary", ""),
                final_insights=chain_data.get("final_reasoning", {}).get("key_insights", {}),
                final_recommendations=chain_data.get("final_reasoning", {}).get("recommendations", []),
                final_uncertainty=chain_data.get("final_reasoning", {}).get("uncertainty_assessment", {}),
                reasoning_steps=chain_data.get("reasoning_chain", []),
                total_duration_ms=chain_data.get("metadata", {}).get("total_duration_ms", 0),
            )

            self.db.add(chain)
            self.db.commit()

            # Also store in Redis for fast access (1 hour TTL)
            await self.redis.store_reasoning_chain(
                chain_id=chain.id,
                chain_data=chain_data,
                session_id=chain_data.get("session_id"),
            )

            # Extract and store knowledge entities
            await self._extract_and_store_knowledge(chain_data, chain.id)

            # Update session statistics
            await self._update_session_stats(chain_data.get("session_id"))

            logger.info(f"Stored reasoning chain {chain.id} in long-term memory")
            return chain.id

        except Exception as e:
            logger.error(f"Error storing reasoning chain: {e}")
            self.db.rollback()
            raise

    async def get_reasoning_chain(self, chain_id: str) -> Optional[Dict[str, Any]]:
        """Get reasoning chain from cache or database"""
        # Try Redis first
        cached = await self.redis.get_reasoning_chain(chain_id)
        if cached:
            return cached

        # Fallback to database
        chain = self.db.query(ReasoningChain).filter_by(id=chain_id).first()
        if chain:
            chain_data = self._serialize_reasoning_chain(chain)
            # Re-cache in Redis
            await self.redis.store_reasoning_chain(chain_id, chain_data, chain.session_id)
            return chain_data

        return None

    async def search_similar_chains(self, scenario: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Find similar reasoning chains from history"""
        # Search in database using text similarity
        chains = (
            self.db.query(ReasoningChain)
            .filter(ReasoningChain.scenario.ilike(f"%{scenario}%"))
            .order_by(desc(ReasoningChain.created_at))
            .limit(limit)
            .all()
        )

        return [self._serialize_reasoning_chain(chain) for chain in chains]

    # ============================================
    # KNOWLEDGE OPERATIONS
    # ============================================

    async def _extract_and_store_knowledge(self, chain_data: Dict[str, Any], chain_id: str):
        """Extract and store knowledge entities from reasoning chain"""
        knowledge_base = chain_data.get("knowledge_base", {})

        # Process entities
        for entity_data in knowledge_base.get("entities", []):
            await self._store_knowledge_entity(entity_data, "entity", chain_id)

        # Process relationships as knowledge
        for rel in knowledge_base.get("relationships", []):
            await self._store_knowledge_entity(rel, "relationship", chain_id)

        # Process causal factors
        for factor in knowledge_base.get("causal_factors", []):
            await self._store_knowledge_entity(factor, "causal_factor", chain_id)

    async def _store_knowledge_entity(self, entity_data: Dict[str, Any], entity_type: str, chain_id: str):
        """Store or update a knowledge entity"""
        try:
            # Check if entity already exists
            name = entity_data.get("name", "") or entity_data.get("factor", "") or str(entity_data)

            existing = self.db.query(KnowledgeEntity).filter_by(name=name, entity_type=entity_type).first()

            if existing:
                # Update usage count
                existing.usage_count += 1
                existing.last_used = datetime.utcnow()
            else:
                # Create new entity
                entity = KnowledgeEntity(
                    entity_type=entity_type,
                    name=name,
                    description=entity_data.get("description", ""),
                    domain=entity_data.get("domain", ""),
                    properties=entity_data,
                )
                self.db.add(entity)

            self.db.commit()

            # Store in Redis for fast access
            await self.redis.store_knowledge(
                knowledge_type=entity_type,
                knowledge_id=name,
                data=entity_data,
                tags=entity_data.get("_tags", []),
            )

        except Exception as e:
            logger.error(f"Error storing knowledge entity: {e}")

    async def get_knowledge_by_type(self, entity_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all knowledge of a specific type"""
        # Try Redis first
        cached = await self.redis.get_knowledge_by_type(entity_type)
        if cached:
            return cached[:limit]

        # Fallback to database
        entities = (
            self.db.query(KnowledgeEntity)
            .filter_by(entity_type=entity_type)
            .order_by(desc(KnowledgeEntity.usage_count))
            .limit(limit)
            .all()
        )

        return [self._serialize_knowledge_entity(e) for e in entities]

    # ============================================
    # SESSION OPERATIONS
    # ============================================

    async def create_session(self, session_id: str, metadata: Dict[str, Any]) -> bool:
        """Create a new reasoning session"""
        try:
            session = DBSession(
                id=session_id,
                user_id=metadata.get("user_id", "anonymous"),
                purpose=metadata.get("purpose", ""),
                context=metadata,
                status="active",
            )

            self.db.add(session)
            self.db.commit()

            # Also create in Redis
            await self.redis.create_session(session_id, metadata)

            logger.info(f"Created session {session_id}")
            return True

        except Exception as e:
            logger.error(f"Error creating session: {e}")
            self.db.rollback()
            return False

    async def _update_session_stats(self, session_id: str):
        """Update session statistics"""
        if not session_id:
            return

        session = self.db.query(DBSession).filter_by(id=session_id).first()
        if session:
            session.total_reasoning_chains += 1
            session.last_activity = datetime.utcnow()
            self.db.commit()

    # ============================================
    # PATTERN LEARNING
    # ============================================

    async def learn_pattern(self, chain_data: Dict[str, Any]) -> Optional[str]:
        """Learn and store successful reasoning patterns"""
        try:
            # Check if this was a successful reasoning
            if not chain_data.get("success", False):
                return None

            # Extract pattern template
            pattern_data = {
                "scenario_type": self._classify_scenario(chain_data.get("scenario", "")),
                "entities": len(chain_data.get("knowledge_base", {}).get("entities", [])),
                "relationships": len(chain_data.get("knowledge_base", {}).get("relationships", [])),
                "model_type": chain_data.get("model_specifications", {}).get("model_type", ""),
            }

            # Check if similar pattern exists
            # Stable hash of the learned pattern for idempotent storage
            pattern_hash = hashlib.sha256(json.dumps(pattern_data, sort_keys=True).encode()).hexdigest()

            existing = self.db.query(ReasoningPattern).filter_by(pattern_name=pattern_hash).first()

            if existing:
                # Update statistics
                existing.usage_count += 1
                existing.last_updated = datetime.utcnow()
            else:
                # Create new pattern
                pattern = ReasoningPattern(
                    pattern_name=pattern_hash,
                    pattern_type=pattern_data["scenario_type"],
                    scenario_template=chain_data.get("scenario", ""),
                    entity_patterns=chain_data.get("knowledge_base", {}).get("entities", []),
                    relationship_patterns=chain_data.get("knowledge_base", {}).get("relationships", []),
                    model_specifications=chain_data.get("model_specifications", {}),
                    success_rate=1.0,
                    avg_duration_ms=chain_data.get("metadata", {}).get("total_duration_ms", 0),
                    usage_count=1,
                    confidence_score=0.8,
                )
                self.db.add(pattern)

            self.db.commit()
            return pattern_hash

        except Exception as e:
            logger.error(f"Error learning pattern: {e}")
            return None

    def _classify_scenario(self, scenario: str) -> str:
        """Classify scenario type"""
        scenario_lower = scenario.lower()

        if "decision" in scenario_lower or "choose" in scenario_lower:
            return "decision"
        elif "predict" in scenario_lower or "forecast" in scenario_lower:
            return "prediction"
        elif "analyze" in scenario_lower or "understand" in scenario_lower:
            return "analysis"
        elif "optimize" in scenario_lower or "improve" in scenario_lower:
            return "optimization"
        else:
            return "general"

    # ============================================
    # SERIALIZATION HELPERS
    # ============================================

    def _serialize_reasoning_chain(self, chain: ReasoningChain) -> Dict[str, Any]:
        """Convert database model to dictionary"""
        return {
            "id": chain.id,
            "session_id": chain.session_id,
            "scenario": chain.scenario,
            "knowledge_base": {
                "entities": chain.mode1_entities or [],
                "relationships": chain.mode1_relationships or [],
                "causal_factors": chain.mode1_causal_factors or [],
                "constraints": chain.mode1_constraints or [],
                "domain_knowledge": chain.mode1_domain_knowledge or [],
            },
            "probabilistic_analysis": {
                "model_structure": chain.mode2_model_structure or {},
                "predictions": chain.mode2_predictions or {},
                "uncertainty_analysis": chain.mode2_uncertainties or {},
                "success": chain.mode2_success == "True",
            },
            "final_reasoning": {
                "summary": chain.final_summary or "",
                "key_insights": chain.final_insights or {},
                "recommendations": chain.final_recommendations or [],
                "uncertainty_assessment": chain.final_uncertainty or {},
            },
            "reasoning_chain": chain.reasoning_steps or [],
            "metadata": {
                "total_duration_ms": chain.total_duration_ms,
                "created_at": chain.created_at.isoformat() if chain.created_at else None,
            },
        }

    def _serialize_knowledge_entity(self, entity: KnowledgeEntity) -> Dict[str, Any]:
        """Convert knowledge entity to dictionary"""
        return {
            "id": entity.id,
            "type": entity.entity_type,
            "name": entity.name,
            "description": entity.description,
            "domain": entity.domain,
            "properties": entity.properties or {},
            "usage_count": entity.usage_count,
            "last_used": entity.last_used.isoformat() if entity.last_used else None,
        }

    # ============================================
    # MEMORY STATISTICS
    # ============================================

    async def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory usage statistics"""
        stats = {
            "postgresql": {
                "reasoning_chains": self.db.query(func.count(ReasoningChain.id)).scalar(),
                "knowledge_entities": self.db.query(func.count(KnowledgeEntity.id)).scalar(),
                "sessions": self.db.query(func.count(DBSession.id)).scalar(),
                "patterns": self.db.query(func.count(ReasoningPattern.id)).scalar(),
                "cache_entries": self.db.query(func.count(ModelCache.id)).scalar(),
            },
            "redis": await self.redis.get_stats() if hasattr(self.redis, "get_stats") else {},
        }

        return stats
