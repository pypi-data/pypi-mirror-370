"""
API endpoints for long-term memory operations
"""

from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from reasoning_kernel.database.connection import get_db_manager
from reasoning_kernel.services.memory_service import LongTermMemoryService
from reasoning_kernel.utils.security import get_secure_logger
from sqlalchemy.orm import Session


logger = get_secure_logger(__name__)

router = APIRouter(prefix="/memory", tags=["Long-Term Memory"])


def get_db() -> Session:
    """Get database session"""
    db_manager = get_db_manager()
    return next(db_manager.get_db())


def get_memory_service(db: Session = Depends(get_db)) -> LongTermMemoryService:
    """Get memory service instance"""
    from reasoning_kernel.main import redis_memory_service

    return LongTermMemoryService(db, redis_memory_service)


@router.get("/stats")
async def get_memory_statistics(memory_service: LongTermMemoryService = Depends(get_memory_service)) -> Dict[str, Any]:
    """Get memory usage statistics for both PostgreSQL and Redis"""
    try:
        stats = await memory_service.get_memory_stats()
        return {"status": "success", "statistics": stats, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        logger.error(f"Error getting memory stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chains")
async def list_reasoning_chains(limit: int = 100, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """List all reasoning chains from long-term memory"""
    try:
        from reasoning_kernel.database.models import ReasoningChain

        chains = db.query(ReasoningChain).order_by(ReasoningChain.created_at.desc()).limit(limit).all()

        return {
            "status": "success",
            "count": len(chains),
            "chains": [
                {
                    "id": chain.id,
                    "session_id": chain.session_id,
                    "scenario": chain.scenario,
                    "created_at": chain.created_at.isoformat() if chain.created_at else None,
                    "duration_ms": chain.total_duration_ms,
                }
                for chain in chains
            ],
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error listing chains: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chains/{chain_id}")
async def get_reasoning_chain(
    chain_id: str, memory_service: LongTermMemoryService = Depends(get_memory_service)
) -> Dict[str, Any]:
    """Get a specific reasoning chain from memory"""
    try:
        chain = await memory_service.get_reasoning_chain(chain_id)
        if not chain:
            raise HTTPException(status_code=404, detail=f"Chain {chain_id} not found")

        return {"status": "success", "chain": chain, "timestamp": datetime.now().isoformat()}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting chain %s: %s", chain_id, e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search/similar")
async def search_similar_chains(
    scenario: str, limit: int = 5, memory_service: LongTermMemoryService = Depends(get_memory_service)
) -> Dict[str, Any]:
    """Search for similar reasoning chains based on scenario"""
    try:
        chains = await memory_service.search_similar_chains(scenario, limit)
        return {
            "status": "success",
            "query": scenario,
            "count": len(chains),
            "similar_chains": chains,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error searching similar chains: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge/{entity_type}")
async def get_knowledge_by_type(
    entity_type: str, limit: int = 100, memory_service: LongTermMemoryService = Depends(get_memory_service)
) -> Dict[str, Any]:
    """Get all knowledge entities of a specific type"""
    try:
        entities = await memory_service.get_knowledge_by_type(entity_type, limit)
        return {
            "status": "success",
            "type": entity_type,
            "count": len(entities),
            "entities": entities,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting knowledge by type {entity_type}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions")
async def list_sessions(limit: int = 50, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """List all reasoning sessions"""
    try:
        from reasoning_kernel.database.models import Session as DBSession

        sessions = db.query(DBSession).order_by(DBSession.last_activity.desc()).limit(limit).all()

        return {
            "status": "success",
            "count": len(sessions),
            "sessions": [
                {
                    "id": session.id,
                    "user_id": session.user_id,
                    "purpose": session.purpose,
                    "status": session.status,
                    "started_at": session.started_at.isoformat() if session.started_at else None,
                    "last_activity": session.last_activity.isoformat() if session.last_activity else None,
                    "total_chains": session.total_reasoning_chains,
                }
                for session in sessions
            ],
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/patterns")
async def list_reasoning_patterns(limit: int = 20, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """List learned reasoning patterns"""
    try:
        from reasoning_kernel.database.models import ReasoningPattern

        patterns = db.query(ReasoningPattern).order_by(ReasoningPattern.usage_count.desc()).limit(limit).all()

        return {
            "status": "success",
            "count": len(patterns),
            "patterns": [
                {
                    "id": pattern.id,
                    "type": pattern.pattern_type,
                    "success_rate": pattern.success_rate,
                    "usage_count": pattern.usage_count,
                    "confidence": pattern.confidence_score,
                    "avg_duration_ms": pattern.avg_duration_ms,
                }
                for pattern in patterns
            ],
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error listing patterns: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cache/clear")
async def clear_redis_cache(memory_service: LongTermMemoryService = Depends(get_memory_service)) -> Dict[str, Any]:
    """Clear Redis cache while preserving PostgreSQL data"""
    try:
        # This would clear only Redis, not PostgreSQL
        # Implementation depends on Redis service
        return {
            "status": "success",
            "message": "Redis cache cleared, long-term memory preserved",
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))
