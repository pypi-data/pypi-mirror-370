"""
Visualization API Endpoints
===========================

Endpoints for causal graph visualization and uncertainty decomposition.
"""

from typing import Any, Dict, Optional

from fastapi import APIRouter
from fastapi import HTTPException
import structlog

from ...learning.adaptive_learning import AdaptiveLearningSystem
from ...learning.adaptive_learning import UserFeedback
from ...visualization.causal_graph import CausalGraphGenerator
from ...visualization.uncertainty_decomposition import UncertaintyAnalyzer


# Import will be done dynamically to avoid circular imports

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/visualization", tags=["visualization"])

# Initialize services
causal_graph_generator = CausalGraphGenerator()
uncertainty_analyzer = UncertaintyAnalyzer()
learning_system = AdaptiveLearningSystem()

# Get Redis service instance
async def get_redis_service():
    """Get Redis service instance"""
    from ...services.redis_service import redis_service
    return redis_service

@router.post("/causal-graph")
async def generate_causal_graph(
    reasoning_result: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate interactive causal graph from reasoning results"""
    
    try:
        # Generate causal graph
        graph = causal_graph_generator.create_graph_from_reasoning(reasoning_result)
        
        # Export for visualization
        vis_data = causal_graph_generator.export_for_visualization(graph)
        
        # Analyze graph structure
        analysis = causal_graph_generator.analyze_causal_structure()
        
        # Store in Redis for quick access
        session_id = reasoning_result.get('session_id', 'unknown')
        cache_key = f"causal_graph:{session_id}"
        try:
            redis_service = await get_redis_service()
            await redis_service.set_data(cache_key, vis_data, ttl=3600)
        except Exception as e:
            logger.warning(f"Could not cache graph data: {e}")
        
        response = {
            "status": "success",
            "graph_data": vis_data,
            "analysis": analysis,
            "graph_metadata": {
                "node_count": len(graph.nodes),
                "edge_count": len(graph.edges),
                "confidence_score": graph.confidence_score,
                "scenario_name": graph.scenario_name
            }
        }
        
        logger.info("Causal graph generated successfully",
                   session_id=session_id,
                   nodes=len(graph.nodes),
                   edges=len(graph.edges))
        
        return response
        
    except Exception as e:
        logger.error(f"Failed to generate causal graph: {e}")
        raise HTTPException(status_code=500, detail=f"Graph generation failed: {str(e)}")

@router.post("/causal-graph/intervention")
async def simulate_intervention(
    node_id: str,
    new_value: float,
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """Simulate what-if scenario by intervening on a graph node"""
    
    try:
        # Load graph if session provided
        if session_id:
            cache_key = f"causal_graph:{session_id}"
            try:
                redis_service = await get_redis_service()
                cached_data = await redis_service.get_data(cache_key)
                if not cached_data:
                    logger.warning(f"Graph not found for session {session_id}, proceeding with intervention")
            except Exception as e:
                logger.warning(f"Could not load cached data: {e}")
        
        # Simulate intervention
        intervention_result = causal_graph_generator.simulate_intervention(node_id, new_value)
        
        if 'error' in intervention_result:
            raise HTTPException(status_code=400, detail=intervention_result['error'])
        
        logger.info("Intervention simulation completed",
                   node_id=node_id,
                   new_value=new_value,
                   affected_nodes=intervention_result['total_affected'])
        
        return {
            "status": "success",
            "intervention_result": intervention_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to simulate intervention: {e}")
        raise HTTPException(status_code=500, detail=f"Intervention simulation failed: {str(e)}")

@router.post("/uncertainty-decomposition")
async def decompose_uncertainty(
    reasoning_result: Dict[str, Any]
) -> Dict[str, Any]:
    """Decompose uncertainty into specific components"""
    
    try:
        # Analyze uncertainty
        decomposition = uncertainty_analyzer.decompose_uncertainty(reasoning_result)
        
        # Export for visualization
        vis_data = uncertainty_analyzer.export_for_visualization(decomposition)
        
        # Store in Redis
        session_id = reasoning_result.get('session_id', 'unknown')
        cache_key = f"uncertainty:{session_id}"
        try:
            redis_service = await get_redis_service()
            await redis_service.set_data(cache_key, vis_data, ttl=3600)
        except Exception as e:
            logger.warning(f"Could not cache uncertainty data: {e}")
        
        response = {
            "status": "success",
            "uncertainty_data": vis_data,
            "summary": {
                "total_uncertainty": decomposition.total_uncertainty,
                "dominant_sources": decomposition.dominant_sources,
                "reducible_uncertainty": sum(
                    comp.contribution for comp in decomposition.components if comp.reducible
                ),
                "irreducible_uncertainty": sum(
                    comp.contribution for comp in decomposition.components if not comp.reducible
                )
            },
            "recommendations": decomposition.reduction_recommendations
        }
        
        logger.info("Uncertainty decomposition completed",
                   session_id=session_id,
                   total_uncertainty=decomposition.total_uncertainty,
                   components=len(decomposition.components))
        
        return response
        
    except Exception as e:
        logger.error(f"Failed to decompose uncertainty: {e}")
        raise HTTPException(status_code=500, detail=f"Uncertainty analysis failed: {str(e)}")

@router.post("/feedback")
async def submit_feedback(
    feedback_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Submit user feedback for adaptive learning"""
    
    try:
        # Create feedback object
        feedback = UserFeedback(
            session_id=feedback_data['session_id'],
            reasoning_stage=feedback_data['reasoning_stage'],
            rating=feedback_data['rating'],
            feedback_type=feedback_data['feedback_type'],
            comments=feedback_data.get('comments'),
            user_id=feedback_data.get('user_id')
        )
        
        # Record feedback
        redis_service = await get_redis_service()
        learning_system.redis_service = redis_service
        success = await learning_system.record_feedback(feedback)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to record feedback")
        
        logger.info("User feedback recorded",
                   session_id=feedback.session_id,
                   stage=feedback.reasoning_stage,
                   rating=feedback.rating)
        
        return {
            "status": "success",
            "message": "Feedback recorded successfully",
            "feedback_id": f"{feedback.session_id}_{feedback.reasoning_stage}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to submit feedback: {e}")
        raise HTTPException(status_code=500, detail=f"Feedback submission failed: {str(e)}")

@router.get("/user/{user_id}/recommendations")
async def get_user_recommendations(
    user_id: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Get personalized recommendations for a user"""
    
    try:
        # Get recommendations  
        redis_service = await get_redis_service()
        learning_system.redis_service = redis_service
        recommendations = await learning_system.get_personalized_recommendations(
            user_id, context or {}
        )
        
        logger.info("User recommendations generated",
                   user_id=user_id,
                   detail_level=recommendations['detail_level'])
        
        return {
            "status": "success",
            "user_id": user_id,
            "recommendations": recommendations
        }
        
    except Exception as e:
        logger.error(f"Failed to get user recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Recommendation generation failed: {str(e)}")

@router.get("/analytics/patterns")
async def analyze_reasoning_patterns() -> Dict[str, Any]:
    """Analyze patterns in reasoning success and failures"""
    
    try:
        # Analyze patterns
        redis_service = await get_redis_service()
        learning_system.redis_service = redis_service
        patterns = await learning_system.analyze_reasoning_success_patterns()
        
        logger.info("Reasoning patterns analyzed",
                   successful_strategies=len(patterns['successful_strategies']),
                   problematic_areas=len(patterns['problematic_areas']))
        
        return {
            "status": "success",
            "analysis": patterns
        }
        
    except Exception as e:
        logger.error(f"Failed to analyze patterns: {e}")
        raise HTTPException(status_code=500, detail=f"Pattern analysis failed: {str(e)}")

@router.get("/analytics/confidence-calibration")
async def get_confidence_calibration() -> Dict[str, Any]:
    """Get confidence calibration adjustments"""
    
    try:
        # Get calibration
        redis_service = await get_redis_service()
        learning_system.redis_service = redis_service
        calibration = await learning_system.get_confidence_calibration()
        
        logger.info("Confidence calibration retrieved")
        
        return {
            "status": "success",
            "calibration": calibration,
            "description": "Confidence adjustments based on historical accuracy"
        }
        
    except Exception as e:
        logger.error(f"Failed to get confidence calibration: {e}")
        raise HTTPException(status_code=500, detail=f"Calibration retrieval failed: {str(e)}")

@router.post("/export/graph")
async def export_graph(
    session_id: str,
    export_format: str = "json"
) -> Dict[str, Any]:
    """Export causal graph for presentations and reports"""
    
    try:
        # Load graph data
        cache_key = f"causal_graph:{session_id}"
        try:
            redis_service = await get_redis_service()
            graph_data = await redis_service.get_data(cache_key)
        except Exception as e:
            logger.error(f"Could not load graph data: {e}")
            graph_data = None
        
        if not graph_data:
            raise HTTPException(status_code=404, detail="Graph not found for session")
        
        # Format for export
        if export_format.lower() == "json":
            export_data = graph_data
        elif export_format.lower() == "csv":
            # Convert to CSV format for nodes and edges
            export_data = {
                "nodes_csv": self._convert_nodes_to_csv(graph_data['nodes']),
                "edges_csv": self._convert_edges_to_csv(graph_data['links'])
            }
        else:
            raise HTTPException(status_code=400, detail="Unsupported export format")
        
        logger.info("Graph exported successfully",
                   session_id=session_id,
                   format=export_format)
        
        return {
            "status": "success",
            "export_format": export_format,
            "data": export_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export graph: {e}")
        raise HTTPException(status_code=500, detail=f"Graph export failed: {str(e)}")

def _convert_nodes_to_csv(nodes: list) -> str:
    """Convert nodes to CSV format"""
    if not nodes:
        return ""
    
    headers = ["id", "label", "type", "confidence", "value", "uncertainty"]
    csv_lines = [",".join(headers)]
    
    for node in nodes:
        row = [
            str(node.get('id', '')),
            str(node.get('label', '')),
            str(node.get('type', '')),
            str(node.get('confidence', '')),
            str(node.get('value', '')),
            str(node.get('uncertainty', ''))
        ]
        csv_lines.append(",".join(row))
    
    return "\n".join(csv_lines)

def _convert_edges_to_csv(edges: list) -> str:
    """Convert edges to CSV format"""
    if not edges:
        return ""
    
    headers = ["source", "target", "strength", "confidence", "type", "mechanism"]
    csv_lines = [",".join(headers)]
    
    for edge in edges:
        row = [
            str(edge.get('source', '')),
            str(edge.get('target', '')),
            str(edge.get('strength', '')),
            str(edge.get('confidence', '')),
            str(edge.get('type', '')),
            str(edge.get('mechanism', ''))
        ]
        csv_lines.append(",".join(row))
    
    return "\n".join(csv_lines)