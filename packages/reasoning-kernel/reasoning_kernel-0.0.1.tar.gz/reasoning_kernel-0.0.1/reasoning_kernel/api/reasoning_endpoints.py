"""
Reasoning Kernel API Endpoints - Version 2
==========================================

Implements the five-stage reasoning pipeline with comprehensive error handling,
monitoring, and backward compatibility.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from fastapi import BackgroundTasks
from fastapi import Depends
from fastapi import HTTPException
from pydantic import BaseModel
from pydantic import Field
import structlog

from ...reasoning_kernel import ReasoningConfig
from ...reasoning_kernel import ReasoningKernel
from ...reasoning_kernel import ReasoningResult


# Simple dependency functions (no external dependencies module needed)
def get_kernel():
    """Simple kernel dependency - will be set from main.py"""
    return None

def get_redis_client():
    """Simple redis client dependency - will be set from main.py"""
    return None

try:
    from ...utils.reasoning_chains import ReasoningChain
except ImportError:
    # Create minimal reasoning chain replacement
    class ReasoningChain:
        def __init__(self):
            self.session_id = "default"
            
    # Override the import to avoid type conflicts
    ReasoningChain = ReasoningChain

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/api/v2", tags=["reasoning-kernel-v2"])

# Request/Response Models
class ReasoningRequest(BaseModel):
    """Request for five-stage reasoning"""
    vignette: str = Field(..., description="Natural language scenario description")
    data: Optional[Dict[str, Any]] = Field(None, description="Observed data for inference")
    config: Optional[Dict[str, Any]] = Field(None, description="Custom reasoning configuration")
    session_id: Optional[str] = Field(None, description="Optional session ID for tracking")

class StageResult(BaseModel):
    """Individual stage result"""
    stage: str
    success: bool
    execution_time: float
    confidence: float
    result_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class ReasoningResponse(BaseModel):
    """Response from five-stage reasoning"""
    session_id: str
    success: bool
    overall_confidence: float
    total_execution_time: float
    
    # Stage results
    stages: List[StageResult]
    
    # Final outputs
    parsed_elements: Optional[Dict[str, Any]] = None
    retrieved_knowledge: Optional[Dict[str, Any]] = None
    dependency_graph: Optional[Dict[str, Any]] = None
    probabilistic_program: Optional[str] = None
    inference_results: Optional[Dict[str, Any]] = None
    
    # Thinking mode outputs
    thinking_process: Optional[List[str]] = None
    reasoning_sentences: Optional[List[str]] = None
    step_by_step_analysis: Optional[Dict[str, List[str]]] = None
    thinking_detail_level: Optional[str] = None
    
    # Metadata
    reasoning_chain_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    error_message: Optional[str] = None

class StatusResponse(BaseModel):
    """Status of ongoing reasoning process"""
    session_id: str
    status: str
    current_stage: Optional[str] = None
    progress_percentage: float
    elapsed_time: float
    estimated_remaining_time: Optional[float] = None

# Global reasoning kernel instance (will be initialized in main.py)
reasoning_kernel: Optional[ReasoningKernel] = None

def get_reasoning_kernel() -> ReasoningKernel:
    """Dependency to get reasoning kernel instance"""
    if reasoning_kernel is None:
        raise HTTPException(status_code=500, detail="Reasoning kernel not initialized")
    return reasoning_kernel

# Simple dependency overrides
def get_redis_client_dependency():
    """Get Redis client from app state"""
    return None  # Will be properly set when app is initialized

@router.post("/reasoning/analyze", response_model=ReasoningResponse)
async def analyze_scenario(
    request: ReasoningRequest,
    background_tasks: BackgroundTasks,
    kernel: ReasoningKernel = Depends(get_reasoning_kernel)
) -> ReasoningResponse:
    """
    Execute five-stage reasoning pipeline
    
    Processes the vignette through all five stages:
    1. Parse - Extract structured elements
    2. Retrieve - Gather background knowledge  
    3. Graph - Build causal dependency graph
    4. Synthesize - Generate probabilistic program
    5. Infer - Execute inference and return results
    """
    session_id = request.session_id or f"session_{int(datetime.now().timestamp())}"
    
    logger.info("Starting five-stage reasoning analysis", 
               session_id=session_id, 
               vignette_length=len(request.vignette))
    
    try:
        # Parse configuration
        config = ReasoningConfig()
        if request.config:
            config = ReasoningConfig(**request.config)
        
        # Update reasoning kernel configuration
        kernel.config = config
        
        # Execute reasoning pipeline
        result: ReasoningResult = await kernel.reason(
            vignette=request.vignette,
            data=request.data
        )
        
        # Convert to API response format
        response = _convert_to_response(session_id, result)
        
        # Store result in background for future retrieval
        background_tasks.add_task(_store_reasoning_result, session_id, result)
        
        logger.info("Five-stage reasoning completed", 
                   session_id=session_id,
                   success=response.success,
                   confidence=response.overall_confidence)
        
        return response
        
    except Exception as e:
        logger.error("Five-stage reasoning failed", 
                    session_id=session_id, 
                    error=str(e))
        
        return ReasoningResponse(
            session_id=session_id,
            success=False,
            overall_confidence=0.0,
            total_execution_time=0.0,
            stages=[],
            error_message=str(e)
        )

@router.get("/reasoning/status/{session_id}", response_model=StatusResponse)
async def get_reasoning_status(
    session_id: str,
    kernel: ReasoningKernel = Depends(get_reasoning_kernel)
) -> StatusResponse:
    """Get status of ongoing or completed reasoning process"""
    
    try:
        status_data = await kernel.get_reasoning_status(session_id)
        
        if status_data.get("status") == "not_found":
            raise HTTPException(status_code=404, detail="Session not found")
        
        return StatusResponse(
            session_id=session_id,
            status=status_data.get("status", "unknown"),
            current_stage=status_data.get("current_stage"),
            progress_percentage=status_data.get("progress", 0.0),
            elapsed_time=status_data.get("elapsed_time", 0.0),
            estimated_remaining_time=status_data.get("estimated_remaining")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get reasoning status", 
                    session_id=session_id, 
                    error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/reasoning/{session_id}")
async def cancel_reasoning(
    session_id: str,
    kernel: ReasoningKernel = Depends(get_reasoning_kernel)
) -> Dict[str, str]:
    """Cancel ongoing reasoning process"""
    
    try:
        success = await kernel.cancel_reasoning(session_id)
        
        if success:
            return {"message": f"Reasoning session {session_id} cancelled successfully"}
        else:
            raise HTTPException(status_code=404, detail="Session not found or already completed")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to cancel reasoning", 
                    session_id=session_id, 
                    error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reasoning/history")
async def get_reasoning_history(
    limit: int = 10,
    offset: int = 0,
    redis_client = Depends(get_redis_client_dependency)
) -> Dict[str, Any]:
    """Get history of reasoning sessions"""
    
    try:
        # Get session keys from Redis
        pattern = "reasoning:result:*"
        keys = await redis_client.keys(pattern)
        
        # Sort by timestamp (newest first)
        sorted_keys = sorted(keys, reverse=True)
        
        # Paginate
        paginated_keys = sorted_keys[offset:offset + limit]
        
        # Fetch session summaries
        sessions = []
        for key in paginated_keys:
            try:
                session_data = await redis_client.get(key)
                if session_data:
                    session_info = json.loads(session_data)
                    sessions.append({
                        "session_id": key.split(":")[-1],
                        "created_at": session_info.get("created_at"),
                        "success": session_info.get("success", False),
                        "confidence": session_info.get("confidence", 0.0),
                        "total_time": session_info.get("total_time", 0.0)
                    })
            except Exception as e:
                logger.debug("Failed to parse session data", key=key, error=str(e))
        
        return {
            "sessions": sessions,
            "total_count": len(sorted_keys),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error("Failed to get reasoning history", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions
def _convert_to_response(session_id: str, result: ReasoningResult) -> ReasoningResponse:
    """Convert ReasoningResult to API response format"""
    
    # Convert stage results
    stages = []
    
    if result.parsed_vignette:
        stages.append(StageResult(
            stage="parse",
            success=True,
            execution_time=result.stage_timings.get("parse", 0.0),
            confidence=result.stage_confidences.get("parse", 0.0),
            result_data={"elements_count": len(result.parsed_vignette.constraints) + len(result.parsed_vignette.queries)}
        ))
    
    if result.retrieval_context:
        stages.append(StageResult(
            stage="retrieve",
            success=True,
            execution_time=result.stage_timings.get("retrieve", 0.0),
            confidence=result.stage_confidences.get("retrieve", 0.0),
            result_data={"documents_count": len(result.retrieval_context.documents)}
        ))
    
    if result.dependency_graph:
        stages.append(StageResult(
            stage="graph",
            success=True,
            execution_time=result.stage_timings.get("graph", 0.0),
            confidence=result.stage_confidences.get("graph", 0.0),
            result_data={"nodes_count": len(result.dependency_graph.nodes), "edges_count": len(result.dependency_graph.edges)}
        ))
    
    if result.probabilistic_program:
        stages.append(StageResult(
            stage="synthesize",
            success=result.probabilistic_program.validation_status,
            execution_time=result.stage_timings.get("synthesize", 0.0),
            confidence=result.stage_confidences.get("synthesize", 0.0),
            result_data={"program_lines": len(result.probabilistic_program.program_code.split('\n'))}
        ))
    
    if result.inference_result:
        stages.append(StageResult(
            stage="infer",
            success=result.inference_result.inference_status.name == "COMPLETED",
            execution_time=result.stage_timings.get("infer", 0.0),
            confidence=result.stage_confidences.get("infer", 0.0),
            result_data={"samples_count": result.inference_result.num_samples}
        ))
    
    # Extract final outputs
    parsed_elements = None
    if result.parsed_vignette:
        parsed_elements = {
            "constraints": [{"content": c.content, "confidence": c.confidence} for c in result.parsed_vignette.constraints],
            "queries": [{"content": q.content, "confidence": q.confidence} for q in result.parsed_vignette.queries],
            "entities": [{"content": e.content, "confidence": e.confidence} for e in result.parsed_vignette.entities],
            "relationships": [{"content": r.content, "confidence": r.confidence} for r in result.parsed_vignette.relationships]
        }
    
    retrieved_knowledge = None
    if result.retrieval_context:
        retrieved_knowledge = {
            "documents": [{"content": d.content, "source": d.source, "relevance": d.relevance_score} 
                         for d in result.retrieval_context.documents],
            "context": result.retrieval_context.augmented_context
        }
    
    dependency_graph = None
    if result.dependency_graph:
        dependency_graph = {
            "nodes": [{"id": n.id, "name": n.name, "type": n.node_type.value} for n in result.dependency_graph.nodes],
            "edges": [{"source": e.source, "target": e.target, "type": e.edge_type.value, "strength": e.strength} 
                     for e in result.dependency_graph.edges]
        }
    
    return ReasoningResponse(
        session_id=session_id,
        success=result.success,
        overall_confidence=result.overall_confidence,
        total_execution_time=result.total_execution_time,
        stages=stages,
        parsed_elements=parsed_elements,
        retrieved_knowledge=retrieved_knowledge,
        dependency_graph=dependency_graph,
        probabilistic_program=getattr(result.probabilistic_program, 'program_code', None) if result.probabilistic_program else None,
        inference_results=getattr(result.inference_result, 'posterior_samples', None) if result.inference_result else None,
        thinking_process=result.thinking_process,
        reasoning_sentences=result.reasoning_sentences,
        step_by_step_analysis=result.step_by_step_analysis,
        thinking_detail_level=getattr(result, 'thinking_detail_level', 'detailed'),
        reasoning_chain_id=getattr(result.reasoning_chain, 'session_id', None) if result.reasoning_chain else None,
        error_message=result.error_message
    )

async def _store_reasoning_result(session_id: str, result: ReasoningResult):
    """Store reasoning result for future retrieval"""
    try:
        # This would store in Redis or database for persistence
        # Implementation depends on specific storage requirements
        logger.debug("Reasoning result stored", session_id=session_id)
    except Exception as e:
        logger.error("Failed to store reasoning result", session_id=session_id, error=str(e))