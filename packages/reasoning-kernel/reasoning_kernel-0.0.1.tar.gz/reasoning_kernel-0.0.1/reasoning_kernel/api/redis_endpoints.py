"""
Redis-related API endpoints for memory and retrieval operations
"""

from datetime import datetime
import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request
from pydantic import BaseModel


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/redis", tags=["Redis Memory & Retrieval"])


class StoreKnowledgeRequest(BaseModel):
    """Request model for storing knowledge"""

    knowledge_type: str
    knowledge_id: str
    knowledge_data: Dict[str, Any]
    tags: Optional[List[str]] = None
    ttl: Optional[int] = None


class StoreReasoningChainRequest(BaseModel):
    """Request model for storing reasoning chains"""

    chain_id: str
    chain_data: Dict[str, Any]
    ttl: Optional[int] = None


class SearchRequest(BaseModel):
    """Request model for semantic search"""

    query: str
    search_type: str = "knowledge"
    limit: int = 10
    similarity_threshold: float = 0.7


@router.get("/health")
async def redis_health(request: Request):
    """Check Redis service health"""
    try:
        redis_memory = request.app.state.redis_memory
        redis_retrieval = request.app.state.redis_retrieval

        # Check if Redis is available
        if redis_memory.redis_client:
            try:
                redis_memory.redis_client.ping()
                redis_status = "connected"
            except Exception:
                redis_status = "disconnected"
        else:
            redis_status = "using in-memory fallback"

        return {
            "status": "healthy",
            "redis_status": redis_status,
            "memory_service": "active",
            "retrieval_service": "active",
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/knowledge/store")
async def store_knowledge(request: Request, data: StoreKnowledgeRequest):
    """Store knowledge in Redis"""
    try:
        redis_memory = request.app.state.redis_memory

        success = await redis_memory.store_knowledge(
            knowledge_type=data.knowledge_type,
            knowledge_id=data.knowledge_id,
            knowledge_data=data.knowledge_data,
            tags=data.tags,
            ttl=data.ttl,
        )

        if success:
            return {
                "status": "success",
                "message": f"Knowledge stored: {data.knowledge_type}:{data.knowledge_id}",
                "timestamp": datetime.now().isoformat(),
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to store knowledge")

    except Exception as e:
        logger.error(f"Failed to store knowledge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge/type/{knowledge_type}")
async def retrieve_knowledge_by_type(request: Request, knowledge_type: str):
    """Retrieve all knowledge of a specific type"""
    try:
        redis_memory = request.app.state.redis_memory

        results = await redis_memory.retrieve_knowledge_by_type(knowledge_type)

        return {
            "status": "success",
            "knowledge_type": knowledge_type,
            "count": len(results),
            "results": results,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to retrieve knowledge by type: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge/tag/{tag}")
async def retrieve_knowledge_by_tag(request: Request, tag: str):
    """Retrieve all knowledge with a specific tag"""
    try:
        redis_memory = request.app.state.redis_memory

        results = await redis_memory.retrieve_knowledge_by_tag(tag)

        return {
            "status": "success",
            "tag": tag,
            "count": len(results),
            "results": results,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to retrieve knowledge by tag: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reasoning-chain/store")
async def store_reasoning_chain(request: Request, data: StoreReasoningChainRequest):
    """Store a reasoning chain"""
    try:
        redis_memory = request.app.state.redis_memory

        success = await redis_memory.store_reasoning_chain(
            chain_id=data.chain_id, chain_data=data.chain_data, ttl=data.ttl
        )

        if success:
            return {
                "status": "success",
                "message": f"Reasoning chain stored: {data.chain_id}",
                "timestamp": datetime.now().isoformat(),
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to store reasoning chain")

    except Exception as e:
        logger.error(f"Failed to store reasoning chain: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reasoning-chain/{chain_id}")
async def get_reasoning_chain(request: Request, chain_id: str):
    """Retrieve a specific reasoning chain"""
    try:
        redis_memory = request.app.state.redis_memory

        chain = await redis_memory.get_reasoning_chain(chain_id)

        if chain:
            return {"status": "success", "chain_id": chain_id, "chain": chain, "timestamp": datetime.now().isoformat()}
        else:
            raise HTTPException(status_code=404, detail=f"Reasoning chain not found: {chain_id}")

    except Exception as e:
        logger.error(f"Failed to retrieve reasoning chain: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reasoning-chains")
async def list_reasoning_chains(request: Request):
    """List all stored reasoning chain IDs"""
    try:
        redis_memory = request.app.state.redis_memory

        chain_ids = await redis_memory.list_reasoning_chains()

        return {
            "status": "success",
            "count": len(chain_ids),
            "chain_ids": chain_ids,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to list reasoning chains: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
async def semantic_search(request: Request, data: SearchRequest):
    """Perform semantic search across stored items"""
    try:
        redis_retrieval = request.app.state.redis_retrieval

        results = await redis_retrieval.semantic_search(
            query=data.query,
            search_type=data.search_type,
            limit=data.limit,
            similarity_threshold=data.similarity_threshold,
        )

        return {
            "status": "success",
            "query": data.query,
            "count": len(results),
            "results": results,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Semantic search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search/similar-chains")
async def find_similar_chains(request: Request, current_chain: Dict[str, Any]):
    """Find similar reasoning chains"""
    try:
        redis_retrieval = request.app.state.redis_retrieval

        similar = await redis_retrieval.find_similar_reasoning_chains(current_chain=current_chain, limit=5)

        return {
            "status": "success",
            "count": len(similar),
            "similar_chains": similar,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to find similar chains: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}")
async def get_session(request: Request, session_id: str):
    """Get session data"""
    try:
        redis_memory = request.app.state.redis_memory

        session = await redis_memory.get_session(session_id)

        if session:
            return {
                "status": "success",
                "session_id": session_id,
                "session": session,
                "timestamp": datetime.now().isoformat(),
            }
        else:
            raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")

    except Exception as e:
        logger.error(f"Failed to retrieve session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/session/{session_id}/create")
async def create_session(request: Request, session_id: str, session_data: Dict[str, Any]):
    """Create a new session"""
    try:
        redis_memory = request.app.state.redis_memory

        success = await redis_memory.create_session(session_id=session_id, session_data=session_data)

        if success:
            return {
                "status": "success",
                "message": f"Session created: {session_id}",
                "timestamp": datetime.now().isoformat(),
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create session")

    except Exception as e:
        logger.error(f"Failed to create session: {e}")
        raise HTTPException(status_code=500, detail=str(e))
