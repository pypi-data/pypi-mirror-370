"""
Model Olympics API endpoints for testing MSA reasoning with sports vignettes
Based on research paper 2507.12547 evaluation methodology
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from fastapi import HTTPException
from pydantic import BaseModel
from reasoning_kernel.examples.model_olympics_scenarios import (
    create_custom_scenario,
)
from reasoning_kernel.examples.model_olympics_scenarios import (
    get_scenario_by_id,
)
from reasoning_kernel.examples.model_olympics_scenarios import (
    get_scenarios_by_sport,
)
from reasoning_kernel.examples.model_olympics_scenarios import (
    MODEL_OLYMPICS_SCENARIOS,
)
from reasoning_kernel.examples.model_olympics_scenarios import get_all_scenarios
from reasoning_kernel.utils.security import get_secure_logger


logger = get_secure_logger(__name__)
router = APIRouter(prefix="/api/v1/model-olympics", tags=["Model Olympics"])

class ModelOlympicsRequest(BaseModel):
    scenario_id: str
    reasoning_mode: Optional[str] = "both"  # "knowledge", "probabilistic", "both", "neural_synthesis"
    additional_context: Optional[Dict[str, Any]] = None

class ModelOlympicsResponse(BaseModel):
    scenario_id: str
    scenario_info: Dict[str, Any]
    reasoning_results: Dict[str, Any]
    msa_analysis: Dict[str, Any]
    processing_time: float
    success: bool
    error: Optional[str] = None

class CustomScenarioRequest(BaseModel):
    title: str
    scenario_text: str
    novel_variables: List[str]
    causal_structure: str
    expected_reasoning: str

@router.get("/scenarios", response_model=List[Dict[str, Any]])
async def list_scenarios():
    """Get all Model Olympics scenarios for testing MSA reasoning"""
    try:
        scenarios = get_all_scenarios()
        return [
            {
                "id": s["id"],
                "title": s["title"],
                "novel_variables": s["novel_variables"],
                "sport": _extract_sport(s["title"]),
                "causal_complexity": len(s["causal_structure"].split(",")),
                "description": s["scenario"][:200] + "..." if len(s["scenario"]) > 200 else s["scenario"]
            }
            for s in scenarios
        ]
    except Exception as e:
        logger.error(f"Failed to list scenarios: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scenarios/{scenario_id}", response_model=Dict[str, Any])
async def get_scenario(scenario_id: str):
    """Get details of a specific Model Olympics scenario"""
    try:
        scenario = get_scenario_by_id(scenario_id)
        if not scenario:
            raise HTTPException(status_code=404, detail=f"Scenario {scenario_id} not found")
        return scenario
    except Exception as e:
        logger.error("Failed to get scenario %s: %s", scenario_id, e)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sports/{sport}/scenarios", response_model=List[Dict[str, Any]])
async def get_scenarios_by_sport_name(sport: str):
    """Get all scenarios for a specific sport"""
    try:
        scenarios = get_scenarios_by_sport(sport)
        return scenarios
    except Exception as e:
        logger.error("Failed to get scenarios for sport %s: %s", sport, e)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reason", response_model=ModelOlympicsResponse)
async def reason_about_scenario(request: ModelOlympicsRequest):
    """
    Apply MSA reasoning to a Model Olympics scenario.
    This tests the system's ability to handle novel causal structures and variables.
    """
    import time

    from reasoning_kernel.main import msa_engine
    
    start_time = time.time()
    
    try:
        # Get the scenario
        scenario_info = get_scenario_by_id(request.scenario_id)
        if not scenario_info:
            raise HTTPException(status_code=404, detail=f"Scenario {request.scenario_id} not found")
        
        scenario_text = scenario_info["scenario"]
        
        # Prepare context with scenario metadata
        context = {
            "scenario_type": "model_olympics",
            "novel_variables": scenario_info.get("novel_variables", []),
            "causal_structure": scenario_info.get("causal_structure", ""),
            "expected_reasoning": scenario_info.get("expected_reasoning", ""),
            "reasoning_mode": request.reasoning_mode
        }
        
        if request.additional_context:
            context.update(request.additional_context)
        
        # Apply MSA reasoning based on mode
        if request.reasoning_mode == "neural_synthesis":
            # Use neural program synthesis approach
            if not msa_engine or not msa_engine.knowledge_extractor or not msa_engine.neural_program_synthesizer:
                raise HTTPException(status_code=500, detail="MSA Engine components not properly initialized")
            
            knowledge_base = await msa_engine.knowledge_extractor.extract_scenario_knowledge(scenario_text)
            neural_program = await msa_engine.neural_program_synthesizer.synthesize_probabilistic_program(
                scenario_text, knowledge_base
            )
            reasoning_results = {
                "knowledge_extraction": knowledge_base,
                "neural_program_synthesis": neural_program,
                "reasoning_approach": "neurally_guided_msa"
            }
        else:
            # Use standard MSA reasoning
            reasoning_results = await msa_engine.reason_about_scenario(
                scenario_text, 
                session_id=f"olympics_{request.scenario_id}",
                context=context
            )
        
        # Analyze MSA-specific aspects
        msa_analysis = {
            "novel_variable_handling": _analyze_novel_variables(
                reasoning_results, scenario_info.get("novel_variables", [])
            ),
            "causal_structure_learning": _analyze_causal_learning(
                reasoning_results, scenario_info.get("causal_structure", "")
            ),
            "open_world_adaptation": _analyze_open_world_reasoning(reasoning_results),
            "reasoning_coherence": _analyze_reasoning_coherence(reasoning_results)
        }
        
        processing_time = time.time() - start_time
        
        return ModelOlympicsResponse(
            scenario_id=request.scenario_id,
            scenario_info=scenario_info,
            reasoning_results=reasoning_results,
            msa_analysis=msa_analysis,
            processing_time=processing_time,
            success=True
        )
        
    except Exception as e:
        logger.error(f"Failed to reason about scenario {request.scenario_id}: {e}")
        processing_time = time.time() - start_time
        return ModelOlympicsResponse(
            scenario_id=request.scenario_id,
            scenario_info={},
            reasoning_results={},
            msa_analysis={},
            processing_time=processing_time,
            success=False,
            error=str(e)
        )

@router.post("/custom-scenario", response_model=Dict[str, Any])
async def create_custom_olympics_scenario(request: CustomScenarioRequest):
    """Create a custom Model Olympics-style scenario"""
    try:
        scenario = create_custom_scenario(
            title=request.title,
            scenario_text=request.scenario_text,
            novel_variables=request.novel_variables,
            causal_structure=request.causal_structure,
            expected_reasoning=request.expected_reasoning
        )
        return scenario
    except Exception as e:
        logger.error(f"Failed to create custom scenario: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analysis/novel-variables")
async def analyze_novel_variable_patterns():
    """Analyze patterns in novel variables across all scenarios"""
    try:
        all_variables = []
        for scenario in MODEL_OLYMPICS_SCENARIOS:
            all_variables.extend(scenario.get("novel_variables", []))
        
        # Count variable types
        variable_analysis = {}
        for var in all_variables:
            var_type = _categorize_variable(var)
            if var_type not in variable_analysis:
                variable_analysis[var_type] = []
            variable_analysis[var_type].append(var)
        
        return {
            "total_novel_variables": len(all_variables),
            "unique_variables": len(set(all_variables)),
            "variable_categories": {k: len(v) for k, v in variable_analysis.items()},
            "most_common": sorted(set(all_variables), key=all_variables.count, reverse=True)[:10]
        }
    except Exception as e:
        logger.error(f"Failed to analyze novel variables: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def _extract_sport(title: str) -> str:
    """Extract sport from scenario title"""
    title_lower = title.lower()
    if "basketball" in title_lower:
        return "basketball"
    elif "soccer" in title_lower:
        return "soccer"
    elif "tennis" in title_lower:
        return "tennis"
    elif "swimming" in title_lower:
        return "swimming"
    elif "volleyball" in title_lower:
        return "volleyball"
    else:
        return "unknown"

def _analyze_novel_variables(reasoning_results: Dict, novel_variables: List[str]) -> Dict:
    """Analyze how well the MSA handled novel variables"""
    entities = reasoning_results.get("knowledge_extraction", {}).get("entities", [])
    entity_names = [e.get("name", "").lower() for e in entities]
    
    detected_variables = []
    for novel_var in novel_variables:
        var_words = novel_var.lower().replace("_", " ").split()
        if any(word in " ".join(entity_names) for word in var_words):
            detected_variables.append(novel_var)
    
    return {
        "total_novel_variables": len(novel_variables),
        "detected_variables": detected_variables,
        "detection_rate": len(detected_variables) / len(novel_variables) if novel_variables else 0,
        "variable_integration": len(detected_variables) > 0
    }

def _analyze_causal_learning(reasoning_results: Dict, expected_causal: str) -> Dict:
    """Analyze causal structure learning capability"""
    relationships = reasoning_results.get("knowledge_extraction", {}).get("relationships", [])
    causal_factors = reasoning_results.get("knowledge_extraction", {}).get("causal_factors", [])
    
    return {
        "relationships_identified": len(relationships),
        "causal_factors_identified": len(causal_factors),
        "has_causal_reasoning": len(relationships) > 0 or len(causal_factors) > 0,
        "expected_structure": expected_causal,
        "structure_complexity": len(expected_causal.split(",")) if expected_causal else 0
    }

def _analyze_open_world_reasoning(reasoning_results: Dict) -> Dict:
    """Analyze open-world reasoning capabilities"""
    model_synthesis = reasoning_results.get("model_synthesis", {})
    confidence = reasoning_results.get("confidence_analysis", {})
    
    return {
        "model_created": model_synthesis.get("success", False),
        "uncertainty_quantified": "uncertainty_analysis" in model_synthesis,
        "confidence_assessed": len(confidence) > 0,
        "adaptive_modeling": model_synthesis.get("model_type", "") != "generic"
    }

def _analyze_reasoning_coherence(reasoning_results: Dict) -> Dict:
    """Analyze coherence of reasoning across modes"""
    mode1_entities = len(reasoning_results.get("knowledge_extraction", {}).get("entities", []))
    mode2_variables = len(reasoning_results.get("model_synthesis", {}).get("model_structure", {}).get("variables", []))
    
    return {
        "mode1_entities": mode1_entities,
        "mode2_variables": mode2_variables,
        "cross_mode_coherence": abs(mode1_entities - mode2_variables) <= 2,
        "reasoning_chain_complete": "reasoning_chain" in reasoning_results
    }

def _categorize_variable(variable: str) -> str:
    """Categorize a variable by type"""
    var_lower = variable.lower()
    if any(word in var_lower for word in ["pressure", "stress", "anxiety"]):
        return "psychological"
    elif any(word in var_lower for word in ["environment", "lighting", "noise", "surface"]):
        return "environmental"
    elif any(word in var_lower for word in ["strategy", "technique", "adaptation"]):
        return "strategic"
    elif any(word in var_lower for word in ["team", "chemistry", "interaction"]):
        return "social"
    else:
        return "other"