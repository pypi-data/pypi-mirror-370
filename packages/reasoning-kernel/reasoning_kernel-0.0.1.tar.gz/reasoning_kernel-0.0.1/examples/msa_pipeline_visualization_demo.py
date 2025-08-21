"""
MSA Pipeline Visualization Demo

This script demonstrates the MSA pipeline visualization functionality.
"""

import asyncio
import os
import sys
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from reasoning_kernel.msa.pipeline.pipeline_stage import StageType, StageStatus, StageResult, PipelineContext
from reasoning_kernel.cli.visualization import PipelineVisualizer, LivePipelineVisualizer


class MockPipelineStage:
    """Mock pipeline stage for testing"""
    
    def __init__(self, stage_type: StageType):
        self.stage_type = stage_type
        
    async def execute(self, context: PipelineContext) -> StageResult:
        """Execute the mock stage"""
        import random
        
        # Simulate some work
        await asyncio.sleep(random.uniform(0.5, 2.0))
        
        # Return a mock result
        return StageResult(
            stage_type=self.stage_type,
            status=StageStatus.COMPLETED,
            data={"result": f"Mock result for {self.stage_type.value}"},
            execution_time=random.uniform(0.5, 2.0),
            metadata={"test": True}
        )


async def demo_pipeline_visualization():
    """Demonstrate pipeline visualization"""
    print("MSA Pipeline Visualization Demo")
    print("=" * 40)
    
    # Create a visualizer
    visualizer = PipelineVisualizer(verbose=True)
    
    # Create mock stage results
    stage_results = {
        StageType.KNOWLEDGE_EXTRACTION: StageResult(
            stage_type=StageType.KNOWLEDGE_EXTRACTION,
            status=StageStatus.COMPLETED,
            data={"entities": ["A", "B", "C"], "relationships": ["A->B", "B->C"]},
            execution_time=1.25,
            metadata={"confidence": 0.85}
        ),
        StageType.MODEL_SPECIFICATION: StageResult(
            stage_type=StageType.MODEL_SPECIFICATION,
            status=StageStatus.COMPLETED,
            data={"model_structure": "Bayesian Network"},
            execution_time=0.75,
            metadata={"complexity": "medium"}
        ),
        StageType.MODEL_SYNTHESIS: StageResult(
            stage_type=StageType.MODEL_SYNTHESIS,
            status=StageStatus.COMPLETED,
            data={"program": "def model(): pass"},
            execution_time=2.10,
            metadata={"language": "Python"}
        ),
        StageType.PROBABILISTIC_INFERENCE: StageResult(
            stage_type=StageType.PROBABILISTIC_INFERENCE,
            status=StageStatus.COMPLETED,
            data={"samples": 1000, "convergence": 0.95},
            execution_time=3.45,
            metadata={"framework": "PyMC"}
        ),
        StageType.RESULT_INTEGRATION: StageResult(
            stage_type=StageType.RESULT_INTEGRATION,
            status=StageStatus.COMPLETED,
            data={"integrated_result": "Final answer", "confidence_metrics": {"overall_confidence": 0.92}},
            execution_time=0.55,
            metadata={"aggregation_method": "weighted_average"}
        )
    }
    
    # Create a mock execution result
    class MockExecutionResult:
        def __init__(self):
            self.session_id = "demo-session-123"
            self.start_time = datetime.now()
            self.end_time = datetime.now()
            self.total_execution_time = 8.10
            self.status = "completed"
            self.stage_results = stage_results
            self.final_result = {
                "confidence_metrics": {
                    "overall_confidence": 0.92,
                    "knowledge_confidence": 0.85,
                    "model_confidence": 0.90,
                    "inference_confidence": 0.88
                }
            }
            self.error = None
    
    execution_result = MockExecutionResult()
    
    # Display the visualization
    print("\nDisplaying pipeline visualization:")
    visualizer.display_pipeline_status(execution_result)
    
    # Display final results
    print("\nDisplaying final results:")
    visualizer.display_final_results(execution_result)
    
    # Test live visualization
    print("\nTesting live visualization:")
    live_visualizer = LivePipelineVisualizer(verbose=True)
    
    # Simulate stage updates
    for stage_type in [
        StageType.KNOWLEDGE_EXTRACTION,
        StageType.MODEL_SPECIFICATION,
        StageType.MODEL_SYNTHESIS,
        StageType.PROBABILISTIC_INFERENCE,
        StageType.RESULT_INTEGRATION
    ]:
        await live_visualizer.update_stage(
            stage_type, 
            StageStatus.COMPLETED, 
            execution_time=1.0,
            error=None
        )
        await asyncio.sleep(0.5)  # Simulate time between stages
    
    # Finish visualization
    await live_visualizer.finish_visualization(execution_result)


if __name__ == "__main__":
    asyncio.run(demo_pipeline_visualization())
