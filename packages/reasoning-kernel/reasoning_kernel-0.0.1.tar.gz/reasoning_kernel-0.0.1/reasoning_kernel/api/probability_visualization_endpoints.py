"""
Probability Visualization API Endpoints
=======================================

FastAPI endpoints for interactive probability visualization functionality.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from fastapi import Body
from fastapi import HTTPException
from fastapi import Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pydantic import Field
from reasoning_kernel.visualization.probability_visualizer import (
    DecisionScenario,
)
from reasoning_kernel.visualization.probability_visualizer import (
    InteractiveProbabilityVisualizer,
)
from reasoning_kernel.visualization.probability_visualizer import (
    VisualizationConfig,
)
from reasoning_kernel.visualization.probability_visualizer import (
    VisualizationType,
)
import structlog


logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/api/v2/probability-visualization", tags=["Probability Visualization"])

# Global visualizer instance
visualizer = InteractiveProbabilityVisualizer()

# Pydantic models for request/response

class DecisionPointModel(BaseModel):
    """Decision variable with prior probability and optional value metadata."""
    id: str = Field(..., description="Unique identifier for decision point")
    name: str = Field(..., description="Human-readable name")
    probability: float = Field(0.5, ge=0, le=1, description="Probability value")
    value: Optional[float] = Field(None, description="Expected value")
    metadata: Dict[str, Any] = Field(default_factory=dict)

class OutcomeModel(BaseModel):
    """Outcome node dependent on decisions with probability and value."""
    id: str = Field(..., description="Unique identifier for outcome")
    name: str = Field(..., description="Human-readable name")
    probability: float = Field(..., ge=0, le=1, description="Probability of occurrence")
    value: float = Field(..., description="Outcome value")
    depends_on: List[str] = Field(default_factory=list, description="Decision point dependencies")
    min_value: Optional[float] = Field(None)
    max_value: Optional[float] = Field(None)
    expected_value: Optional[float] = Field(None)

class DecisionScenarioModel(BaseModel):
    """Complete scenario specification for decision analysis and visualization."""
    scenario_id: str = Field(..., description="Unique scenario identifier")
    title: str = Field(..., description="Scenario title")
    description: str = Field(..., description="Detailed description")
    decision_points: List[DecisionPointModel] = Field(..., description="Decision points")
    outcomes: List[OutcomeModel] = Field(..., description="Possible outcomes")
    probabilities: Dict[str, float] = Field(default_factory=dict)
    expected_values: Dict[str, float] = Field(default_factory=dict)
    confidence_intervals: Dict[str, List[float]] = Field(default_factory=dict)

class VisualizationConfigModel(BaseModel):
    """Rendering and interactivity options for visualization generation."""
    visualization_type: str = Field(..., description="Type of visualization")
    width: int = Field(800, gt=0, description="Visualization width")
    height: int = Field(600, gt=0, description="Visualization height")
    interactive: bool = Field(True, description="Enable interactivity")
    color_scheme: str = Field("viridis", description="Color scheme")
    animation_enabled: bool = Field(True, description="Enable animations")
    show_confidence_intervals: bool = Field(True, description="Show confidence intervals")
    monte_carlo_samples: int = Field(10000, gt=0, description="Number of Monte Carlo samples")

class ParameterUpdateModel(BaseModel):
    """Request payload to update an existing visualization's parameters."""
    visualization_id: str = Field(..., description="Visualization to update")
    parameters: Dict[str, Any] = Field(..., description="Parameter updates")

# API Endpoints

@router.post("/create-decision-tree")
async def create_decision_tree_visualization(
    scenario: DecisionScenarioModel = Body(...),
    config: VisualizationConfigModel = Body(...)
) -> JSONResponse:
    """
    Create an interactive decision tree visualization
    """
    try:
        logger.info("Creating decision tree visualization", scenario_id=scenario.scenario_id)
        
        # Convert Pydantic models to internal objects
        decision_scenario = DecisionScenario(
            scenario_id=scenario.scenario_id,
            title=scenario.title,
            description=scenario.description,
            decision_points=[dp.dict() for dp in scenario.decision_points],
            outcomes=[o.dict() for o in scenario.outcomes],
            probabilities=scenario.probabilities,
            expected_values=scenario.expected_values,
            confidence_intervals={k: (v[0], v[1]) if len(v) >= 2 else (0.0, 1.0) for k, v in scenario.confidence_intervals.items()}
        )
        
        viz_config = VisualizationConfig(
            visualization_type=VisualizationType(config.visualization_type),
            width=config.width,
            height=config.height,
            interactive=config.interactive,
            color_scheme=config.color_scheme,
            animation_enabled=config.animation_enabled,
            show_confidence_intervals=config.show_confidence_intervals,
            monte_carlo_samples=config.monte_carlo_samples
        )
        
        # Generate visualization
        visualization_data = visualizer.create_decision_tree_visualization(
            decision_scenario, viz_config
        )
        
        # Generate interactive controls
        controls = visualizer.generate_interactive_controls(
            decision_scenario, VisualizationType.DECISION_TREE
        )
        
        # Store visualization
        viz_id = f"decision_tree_{scenario.scenario_id}"
        visualizer.visualizations[viz_id] = visualization_data
        
        return JSONResponse({
            "success": True,
            "visualization_id": viz_id,
            "visualization": visualization_data,
            "controls": controls,
            "message": "Decision tree visualization created successfully"
        })
        
    except Exception as e:
        logger.error("Failed to create decision tree visualization", error=str(e))
        raise HTTPException(status_code=500, detail=f"Visualization creation failed: {str(e)}")

@router.post("/create-probability-distribution")
async def create_probability_distribution_visualization(
    distributions: Dict[str, List[float]] = Body(..., description="Distribution data"),
    config: VisualizationConfigModel = Body(...)
) -> JSONResponse:
    """
    Create interactive probability distribution visualization
    """
    try:
        logger.info("Creating probability distribution visualization", 
                   num_distributions=len(distributions))
        
        viz_config = VisualizationConfig(
            visualization_type=VisualizationType(config.visualization_type),
            width=config.width,
            height=config.height,
            interactive=config.interactive,
            color_scheme=config.color_scheme,
            animation_enabled=config.animation_enabled,
            show_confidence_intervals=config.show_confidence_intervals
        )
        
        visualization_data = visualizer.create_probability_distribution_visualization(
            distributions, viz_config
        )
        
        viz_id = f"prob_dist_{hash(str(distributions))}"
        visualizer.visualizations[viz_id] = visualization_data
        
        return JSONResponse({
            "success": True,
            "visualization_id": viz_id,
            "visualization": visualization_data,
            "message": "Probability distribution visualization created successfully"
        })
        
    except Exception as e:
        logger.error("Failed to create probability distribution visualization", error=str(e))
        raise HTTPException(status_code=500, detail=f"Visualization creation failed: {str(e)}")

@router.post("/create-monte-carlo")
async def create_monte_carlo_visualization(
    simulation_data: Dict[str, Any] = Body(..., description="Monte Carlo simulation data"),
    config: VisualizationConfigModel = Body(...)
) -> JSONResponse:
    """
    Create Monte Carlo simulation visualization
    """
    try:
        logger.info("Creating Monte Carlo visualization")
        
        viz_config = VisualizationConfig(
            visualization_type=VisualizationType.MONTE_CARLO,
            width=config.width,
            height=config.height,
            interactive=config.interactive,
            color_scheme=config.color_scheme,
            animation_enabled=config.animation_enabled,
            monte_carlo_samples=config.monte_carlo_samples
        )
        
        visualization_data = visualizer.create_monte_carlo_visualization(
            simulation_data, viz_config
        )
        
        viz_id = f"monte_carlo_{hash(str(simulation_data))}"
        visualizer.visualizations[viz_id] = visualization_data
        
        return JSONResponse({
            "success": True,
            "visualization_id": viz_id,
            "visualization": visualization_data,
            "message": "Monte Carlo visualization created successfully"
        })
        
    except Exception as e:
        logger.error("Failed to create Monte Carlo visualization", error=str(e))
        raise HTTPException(status_code=500, detail=f"Visualization creation failed: {str(e)}")

@router.post("/create-bayesian-network")
async def create_bayesian_network_visualization(
    network_structure: Dict[str, Any] = Body(..., description="Bayesian network structure"),
    config: VisualizationConfigModel = Body(...)
) -> JSONResponse:
    """
    Create interactive Bayesian network visualization
    """
    try:
        logger.info("Creating Bayesian network visualization")
        
        viz_config = VisualizationConfig(
            visualization_type=VisualizationType.BAYESIAN_NETWORK,
            width=config.width,
            height=config.height,
            interactive=config.interactive,
            color_scheme=config.color_scheme
        )
        
        visualization_data = visualizer.create_bayesian_network_visualization(
            network_structure, viz_config
        )
        
        viz_id = f"bayesian_net_{hash(str(network_structure))}"
        visualizer.visualizations[viz_id] = visualization_data
        
        return JSONResponse({
            "success": True,
            "visualization_id": viz_id,
            "visualization": visualization_data,
            "message": "Bayesian network visualization created successfully"
        })
        
    except Exception as e:
        logger.error("Failed to create Bayesian network visualization", error=str(e))
        raise HTTPException(status_code=500, detail=f"Visualization creation failed: {str(e)}")

@router.post("/create-uncertainty-bands")
async def create_uncertainty_visualization(
    uncertainty_data: Dict[str, Any] = Body(..., description="Uncertainty analysis data"),
    config: VisualizationConfigModel = Body(...)
) -> JSONResponse:
    """
    Create uncertainty quantification visualization
    """
    try:
        logger.info("Creating uncertainty visualization")
        
        viz_config = VisualizationConfig(
            visualization_type=VisualizationType.UNCERTAINTY_BANDS,
            width=config.width,
            height=config.height,
            interactive=config.interactive,
            color_scheme=config.color_scheme,
            show_confidence_intervals=config.show_confidence_intervals
        )
        
        visualization_data = visualizer.create_uncertainty_visualization(
            uncertainty_data, viz_config
        )
        
        viz_id = f"uncertainty_{hash(str(uncertainty_data))}"
        visualizer.visualizations[viz_id] = visualization_data
        
        return JSONResponse({
            "success": True,
            "visualization_id": viz_id,
            "visualization": visualization_data,
            "message": "Uncertainty visualization created successfully"
        })
        
    except Exception as e:
        logger.error("Failed to create uncertainty visualization", error=str(e))
        raise HTTPException(status_code=500, detail=f"Visualization creation failed: {str(e)}")

@router.post("/update-visualization")
async def update_visualization(
    update_request: ParameterUpdateModel = Body(...)
) -> JSONResponse:
    """
    Update visualization based on parameter changes
    """
    try:
        logger.info("Updating visualization", 
                   visualization_id=update_request.visualization_id)
        
        updated_data = visualizer.update_visualization(
            update_request.visualization_id,
            update_request.parameters
        )
        
        if not updated_data:
            raise HTTPException(status_code=404, detail="Visualization not found")
        
        return JSONResponse({
            "success": True,
            "visualization_id": update_request.visualization_id,
            "updated_data": updated_data,
            "message": "Visualization updated successfully"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update visualization", error=str(e))
        raise HTTPException(status_code=500, detail=f"Visualization update failed: {str(e)}")

@router.get("/visualizations")
async def list_visualizations() -> JSONResponse:
    """
    List all active visualizations
    """
    try:
        visualizations = {
            viz_id: {
                "type": viz_data.get("type", "unknown"),
                "created": viz_data.get("metadata", {}).get("created"),
                "title": viz_data.get("layout", {}).get("title", "Untitled")
            }
            for viz_id, viz_data in visualizer.visualizations.items()
        }
        
        return JSONResponse({
            "success": True,
            "visualizations": visualizations,
            "count": len(visualizations)
        })
        
    except Exception as e:
        logger.error("Failed to list visualizations", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to list visualizations: {str(e)}")

@router.get("/visualization/{visualization_id}")
async def get_visualization(visualization_id: str) -> JSONResponse:
    """
    Get specific visualization data
    """
    try:
        if visualization_id not in visualizer.visualizations:
            raise HTTPException(status_code=404, detail="Visualization not found")
        
        visualization_data = visualizer.visualizations[visualization_id]
        
        return JSONResponse({
            "success": True,
            "visualization_id": visualization_id,
            "visualization": visualization_data
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get visualization", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get visualization: {str(e)}")

@router.delete("/visualization/{visualization_id}")
async def delete_visualization(visualization_id: str) -> JSONResponse:
    """
    Delete a visualization
    """
    try:
        if visualization_id not in visualizer.visualizations:
            raise HTTPException(status_code=404, detail="Visualization not found")
        
        del visualizer.visualizations[visualization_id]
        
        return JSONResponse({
            "success": True,
            "message": f"Visualization {visualization_id} deleted successfully"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete visualization", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to delete visualization: {str(e)}")

@router.post("/run-monte-carlo")
async def run_monte_carlo_simulation(
    parameters: Dict[str, Any] = Body(..., description="Simulation parameters"),
    num_samples: int = Query(10000, gt=0, description="Number of samples")
) -> JSONResponse:
    """
    Run Monte Carlo simulation and return results
    """
    try:
        logger.info("Running Monte Carlo simulation", num_samples=num_samples)
        
        # Simple Monte Carlo simulation example
        import numpy as np

        # Extract parameters
        mean = parameters.get("mean", 0)
        std = parameters.get("std", 1)
        
        # Generate samples
        samples = np.random.normal(mean, std, num_samples)
        
        # Calculate statistics
        outcomes = samples.tolist()
        probabilities = [1.0/num_samples] * num_samples  # Uniform probability
        
        # Calculate running average for convergence
        convergence = []
        running_sum = 0
        for i, sample in enumerate(samples):
            running_sum += sample
            convergence.append(running_sum / (i + 1))
        
        simulation_data = {
            "outcomes": outcomes,
            "probabilities": probabilities,
            "convergence": convergence,
            "statistics": {
                "mean": float(np.mean(samples)),
                "std": float(np.std(samples)),
                "min": float(np.min(samples)),
                "max": float(np.max(samples)),
                "percentiles": {
                    "5": float(np.percentile(samples, 5)),
                    "25": float(np.percentile(samples, 25)),
                    "50": float(np.percentile(samples, 50)),
                    "75": float(np.percentile(samples, 75)),
                    "95": float(np.percentile(samples, 95))
                }
            }
        }
        
        return JSONResponse({
            "success": True,
            "simulation_data": simulation_data,
            "message": f"Monte Carlo simulation completed with {num_samples} samples"
        })
        
    except Exception as e:
        logger.error("Monte Carlo simulation failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")