"""
FastAPI endpoints for MSA Reasoning Engine
"""

import time
from typing import Any, Dict

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from reasoning_kernel.models.requests import KnowledgeExtractionRequest
from reasoning_kernel.models.requests import MSAReasoningRequest
from reasoning_kernel.models.requests import ProbabilisticModelRequest
from reasoning_kernel.models.responses import KnowledgeExtractionResponse
from reasoning_kernel.models.responses import MSAReasoningResponse
from reasoning_kernel.models.responses import ProbabilisticModelResponse
from reasoning_kernel.models.responses import SessionListResponse
from reasoning_kernel.utils.security import get_secure_logger


logger = get_secure_logger(__name__)

router = APIRouter()


def get_msa_engine(request: Request):
    """Dependency to get MSA engine from app state"""
    if (
        not hasattr(request.app.state, "msa_engine")
        or request.app.state.msa_engine is None
    ):
        raise HTTPException(
            status_code=503,
            detail="MSA Engine not initialized. Please check system health.",
        )
    return request.app.state.msa_engine


def get_kernel_manager(request: Request):
    """Dependency to get kernel manager from app state"""
    if (
        not hasattr(request.app.state, "kernel_manager")
        or request.app.state.kernel_manager is None
    ):
        raise HTTPException(
            status_code=503,
            detail="Semantic Kernel not initialized. Please check system health.",
        )
    return request.app.state.kernel_manager


@router.post("/reason", response_model=MSAReasoningResponse)
async def reason_about_scenario(
    request: MSAReasoningRequest, msa_engine=Depends(get_msa_engine)
):
    """
    Main MSA reasoning endpoint that orchestrates both Mode 1 and Mode 2

    This endpoint provides complete MSA reasoning including:
    - Mode 1: LLM-powered knowledge extraction
    - Mode 2: Dynamic probabilistic model synthesis
    - Integrated reasoning and recommendations
    """
    try:
        logger.info(
            f"Received reasoning request for scenario: {request.scenario[:100]}..."
        )

        start_time = time.time()

        # Handle different reasoning modes
        if request.mode == "knowledge":
            # Only run Mode 1 (knowledge extraction)
            result = await _run_knowledge_only(msa_engine, request)
        elif request.mode == "probabilistic":
            # Only run Mode 2 (requires specifications)
            raise HTTPException(
                status_code=400,
                detail="Probabilistic-only mode requires model specifications. Use /extract-knowledge first or use 'both' mode.",
            )
        else:  # "both" - default full MSA reasoning
            result = await msa_engine.reason_about_scenario(
                scenario=request.scenario,
                session_id=request.session_id,
                context=request.context,
            )

        processing_time = time.time() - start_time
        logger.info(f"Reasoning completed in {processing_time:.2f}s")

        if result.get("success", False):
            return MSAReasoningResponse(**result)
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Reasoning failed: {result.get('error', 'Unknown error')}",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reasoning endpoint error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Internal server error during reasoning: {str(e)}"
        )


@router.post("/extract-knowledge", response_model=KnowledgeExtractionResponse)
async def extract_knowledge(
    request: KnowledgeExtractionRequest, msa_engine=Depends(get_msa_engine)
):
    """
    Mode 1 only: Extract knowledge from scenario using LLM capabilities

    This endpoint runs only the knowledge extraction phase and returns
    the knowledge base and model specifications for potential use in
    probabilistic modeling.
    """
    try:
        logger.info(f"Extracting knowledge for scenario: {request.scenario[:100]}...")

        start_time = time.time()

        # Extract knowledge using Mode 1
        knowledge_base = (
            await msa_engine.knowledge_extractor.extract_scenario_knowledge(
                request.scenario
            )
        )

        # Generate model specifications
        model_specs = (
            await msa_engine.knowledge_extractor.generate_model_specifications(
                knowledge_base
            )
        )

        processing_time = time.time() - start_time

        return KnowledgeExtractionResponse(
            knowledge_base=knowledge_base,
            model_specifications=model_specs,
            processing_time_seconds=processing_time,
            success=True,
        )

    except Exception as e:
        logger.error(f"Knowledge extraction error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to extract knowledge: {str(e)}"
        )


@router.post("/synthesize-model", response_model=ProbabilisticModelResponse)
async def synthesize_probabilistic_model(
    request: ProbabilisticModelRequest, msa_engine=Depends(get_msa_engine)
):
    """
    Mode 2 only: Synthesize probabilistic model from specifications

    This endpoint runs only the probabilistic model synthesis using
    provided model specifications (typically from knowledge extraction).
    """
    try:
        logger.info("Synthesizing probabilistic model from specifications...")

        start_time = time.time()

        # Prepare scenario data
        scenario_data = {
            "observations": request.observations or {},
            "inference_samples": request.inference_samples,
        }

        # Run probabilistic synthesis
        synthesis_results = await msa_engine.probabilistic_synthesizer.synthesize_model(
            request.model_specifications, scenario_data
        )

        processing_time = time.time() - start_time

        return ProbabilisticModelResponse(
            probabilistic_analysis=synthesis_results,
            processing_time_seconds=processing_time,
            success=synthesis_results.get("success", False),
        )

    except Exception as e:
        logger.error(f"Probabilistic synthesis error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to synthesize probabilistic model: {str(e)}",
        )


@router.get("/session/{session_id}")
async def get_session_status(session_id: str, msa_engine=Depends(get_msa_engine)):
    """
    Get the status of a specific reasoning session
    """
    try:
        session_info = await msa_engine.get_session_status(session_id)

        if session_info is None:
            raise HTTPException(
                status_code=404, detail=f"Session {session_id} not found"
            )

        return session_info

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Session status error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to get session status: {str(e)}"
        )


@router.get("/sessions", response_model=SessionListResponse)
async def list_active_sessions(msa_engine=Depends(get_msa_engine)):
    """
    List all active reasoning sessions
    """
    try:
        sessions = await msa_engine.list_active_sessions()

        return SessionListResponse(active_sessions=sessions, total_count=len(sessions))

    except Exception as e:
        logger.error(f"Session list error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to list sessions: {str(e)}"
        )


@router.get("/capabilities")
async def get_system_capabilities():
    """
    Get information about system capabilities and configuration
    """
    try:
        from reasoning_kernel.core.config import settings

        return {
            "msa_version": "1.0.0",
            "modes": {
                "mode1": {
                    "name": "LLM Knowledge Extraction",
                    "description": "Extract entities, relationships, and causal factors using Semantic Kernel",
                    "capabilities": [
                        "Entity identification",
                        "Relationship mapping",
                        "Causal factor analysis",
                        "Constraint identification",
                        "Domain knowledge extraction",
                    ],
                },
                "mode2": {
                    "name": "Probabilistic Model Synthesis",
                    "description": "Dynamic Bayesian model construction using NumPyro",
                    "capabilities": [
                        "Dynamic model synthesis",
                        "Bayesian inference",
                        "Uncertainty quantification",
                        "Predictive modeling",
                        "Causal reasoning",
                    ],
                },
            },
            "configuration": {
                "max_reasoning_steps": settings.max_reasoning_steps,
                "probabilistic_samples": settings.probabilistic_samples,
                "uncertainty_threshold": settings.uncertainty_threshold,
                "ai_model": settings.openai_model,
            },
            "supported_endpoints": [
                "/api/v1/reason",
                "/api/v1/extract-knowledge",
                "/api/v1/synthesize-model",
                "/api/v1/session/{session_id}",
                "/api/v1/sessions",
                "/api/v1/capabilities",
            ],
        }

    except Exception as e:
        logger.error(f"Capabilities endpoint error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to get system capabilities: {str(e)}"
        )


async def _run_knowledge_only(
    msa_engine, request: MSAReasoningRequest
) -> Dict[str, Any]:
    """Helper function to run knowledge extraction only"""

    # Extract knowledge
    knowledge_base = await msa_engine.knowledge_extractor.extract_scenario_knowledge(
        request.scenario
    )

    # Generate model specifications
    model_specs = await msa_engine.knowledge_extractor.generate_model_specifications(
        knowledge_base
    )

    # Create simplified response structure
    return {
        "session_id": request.session_id or f"knowledge_session_{int(time.time())}",
        "scenario": request.scenario,
        "reasoning_chain": [
            {
                "step_id": "knowledge_extraction",
                "step_type": "mode1_only",
                "description": "Knowledge extraction completed",
                "timestamp": time.time(),
                "data": knowledge_base,
            }
        ],
        "knowledge_base": knowledge_base,
        "model_specifications": model_specs,
        "probabilistic_analysis": {
            "success": False,
            "note": "Mode 2 not executed in knowledge-only mode",
        },
        "final_reasoning": {
            "summary": f"Knowledge extraction completed for scenario. Identified {len(knowledge_base.get('entities', []))} entities and {len(knowledge_base.get('relationships', []))} relationships.",
            "key_insights": {
                "entities_count": len(knowledge_base.get("entities", [])),
                "relationships_count": len(knowledge_base.get("relationships", [])),
                "causal_factors_count": len(knowledge_base.get("causal_factors", [])),
            },
            "recommendations": [
                "Proceed with probabilistic modeling using the /synthesize-model endpoint"
            ],
            "reasoning_quality": {"mode": "knowledge_only", "completeness": "partial"},
        },
        "metadata": {"mode": "knowledge_only", "timestamp": time.time()},
        "success": True,
    }
