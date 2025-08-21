"""
Test implementation for the clean MSA pipeline architecture
"""

import asyncio
import logging

from reasoning_kernel.msa.pipeline.msa_pipeline import MSAPipeline
from reasoning_kernel.msa.pipeline.stages.knowledge_extraction import KnowledgeExtractionStage
from reasoning_kernel.msa.pipeline.pipeline_stage import (
    PipelineStage,
    PipelineContext,
    StageResult,
    StageStatus,
    StageType,
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MockModelSpecificationStage(PipelineStage):
    """Mock implementation of Model Specification stage for testing"""

    def __init__(self, config=None):
        super().__init__(StageType.MODEL_SPECIFICATION, config)

    async def execute(self, context: PipelineContext) -> StageResult:
        # Get knowledge base from previous stage
        knowledge_result = context.get_result(StageType.KNOWLEDGE_EXTRACTION)
        if not knowledge_result or knowledge_result.status != StageStatus.COMPLETED:
            raise Exception("Knowledge extraction stage required")

        knowledge_base = knowledge_result.data["knowledge_base"]

        # Mock model specification
        model_spec = {
            "variables": knowledge_base.get("variables", []),
            "relationships": knowledge_base.get("relationships", []),
            "model_type": "bayesian_network",
            "inference_method": "mcmc",
        }

        return StageResult(
            stage_type=self.stage_type,
            status=StageStatus.COMPLETED,
            data={"model_specification": model_spec},
            execution_time=0,
            metadata={"mock_stage": True},
        )

    def validate_dependencies(self, context: PipelineContext) -> bool:
        """Requires knowledge extraction stage"""
        knowledge_result = context.get_result(StageType.KNOWLEDGE_EXTRACTION)
        return knowledge_result is not None and knowledge_result.status == StageStatus.COMPLETED


class MockModelSynthesisStage(PipelineStage):
    """Mock implementation of Model Synthesis stage for testing"""

    def __init__(self, config=None):
        super().__init__(StageType.MODEL_SYNTHESIS, config)

    async def execute(self, context: PipelineContext) -> StageResult:
        # Get model spec from previous stage
        spec_result = context.get_result(StageType.MODEL_SPECIFICATION)
        if not spec_result or spec_result.status != StageStatus.COMPLETED:
            raise Exception("Model specification stage required")

        model_spec = spec_result.data["model_specification"]

        # Mock synthesis
        synthesized_model = {
            "probabilistic_program": "mock_program",
            "parameters": {"param1": 0.5, "param2": 0.8},
            "model_code": "# Generated probabilistic program",
            "compilation_status": "success",
        }

        return StageResult(
            stage_type=self.stage_type,
            status=StageStatus.COMPLETED,
            data={"synthesized_model": synthesized_model},
            execution_time=0,
            metadata={"mock_stage": True},
        )

    def validate_dependencies(self, context: PipelineContext) -> bool:
        """Requires model specification stage"""
        spec_result = context.get_result(StageType.MODEL_SPECIFICATION)
        return spec_result is not None and spec_result.status == StageStatus.COMPLETED


class MockInferenceStage(PipelineStage):
    """Mock implementation of Probabilistic Inference stage for testing"""

    def __init__(self, config=None):
        super().__init__(StageType.PROBABILISTIC_INFERENCE, config)

    async def execute(self, context: PipelineContext) -> StageResult:
        # Get synthesized model from previous stage
        synthesis_result = context.get_result(StageType.MODEL_SYNTHESIS)
        if not synthesis_result or synthesis_result.status != StageStatus.COMPLETED:
            raise Exception("Model synthesis stage required")

        synthesized_model = synthesis_result.data["synthesized_model"]

        # Mock inference results
        inference_results = {
            "posterior_samples": {"param1": [0.4, 0.6, 0.5], "param2": [0.7, 0.9, 0.8]},
            "marginal_likelihoods": {"param1": 0.75, "param2": 0.82},
            "convergence_diagnostics": {"r_hat": 1.01, "effective_sample_size": 1000},
            "uncertainty_quantification": {"param1_ci": [0.3, 0.7], "param2_ci": [0.6, 1.0]},
        }

        return StageResult(
            stage_type=self.stage_type,
            status=StageStatus.COMPLETED,
            data={"inference_results": inference_results},
            execution_time=0,
            metadata={"mock_stage": True},
        )

    def validate_dependencies(self, context: PipelineContext) -> bool:
        """Requires model synthesis stage"""
        synthesis_result = context.get_result(StageType.MODEL_SYNTHESIS)
        return synthesis_result is not None and synthesis_result.status == StageStatus.COMPLETED


class MockIntegrationStage(PipelineStage):
    """Mock implementation of Result Integration stage for testing"""

    def __init__(self, config=None):
        super().__init__(StageType.RESULT_INTEGRATION, config)

    async def execute(self, context: PipelineContext) -> StageResult:
        # Get all previous results
        knowledge_result = context.get_result(StageType.KNOWLEDGE_EXTRACTION)
        spec_result = context.get_result(StageType.MODEL_SPECIFICATION)
        synthesis_result = context.get_result(StageType.MODEL_SYNTHESIS)
        inference_result = context.get_result(StageType.PROBABILISTIC_INFERENCE)

        # Integrate results
        integrated_reasoning = {
            "scenario": context.scenario,
            "knowledge_summary": {
                "entities_count": len(knowledge_result.data["knowledge_base"]["entities"]),
                "relationships_count": len(knowledge_result.data["knowledge_base"]["relationships"]),
            },
            "model_summary": {
                "model_type": spec_result.data["model_specification"]["model_type"],
                "variables_count": len(spec_result.data["model_specification"]["variables"]),
            },
            "inference_summary": {
                "convergence": inference_result.data["inference_results"]["convergence_diagnostics"]["r_hat"],
                "uncertainty_bounds": inference_result.data["inference_results"]["uncertainty_quantification"],
            },
            "final_answer": "Mock reasoning result based on integrated pipeline",
        }

        confidence_metrics = {
            "overall_confidence": 0.78,
            "knowledge_confidence": 0.80,
            "model_confidence": 0.75,
            "inference_confidence": 0.82,
            "integration_confidence": 0.76,
        }

        return StageResult(
            stage_type=self.stage_type,
            status=StageStatus.COMPLETED,
            data={"integrated_reasoning": integrated_reasoning, "confidence_metrics": confidence_metrics},
            execution_time=0,
            metadata={"mock_stage": True},
        )

    def validate_dependencies(self, context: PipelineContext) -> bool:
        """Requires all previous stages"""
        required_stages = [
            StageType.KNOWLEDGE_EXTRACTION,
            StageType.MODEL_SPECIFICATION,
            StageType.MODEL_SYNTHESIS,
            StageType.PROBABILISTIC_INFERENCE,
        ]

        for stage_type in required_stages:
            result = context.get_result(stage_type)
            if not result or result.status != StageStatus.COMPLETED:
                return False

        return True


class MockKernelManager:
    """Mock kernel manager for testing"""

    pass


async def test_msa_pipeline():
    """Test the complete MSA pipeline with mock stages"""
    logger.info("🚀 Testing MSA Pipeline Architecture")

    # Create pipeline
    pipeline = MSAPipeline()

    # Register mock stages
    mock_kernel = MockKernelManager()

    pipeline.register_stage(KnowledgeExtractionStage(mock_kernel))
    pipeline.register_stage(MockModelSpecificationStage())
    pipeline.register_stage(MockModelSynthesisStage())
    pipeline.register_stage(MockInferenceStage())
    pipeline.register_stage(MockIntegrationStage())

    # Verify pipeline is complete
    assert pipeline.is_complete(), "Pipeline should be complete with all stages registered"
    logger.info("✅ Pipeline registration complete")

    # Test scenario
    scenario = """
    A company is considering whether to launch a new product. The success depends on 
    market demand, competition level, and marketing investment. Historical data shows 
    that similar products had 60% success rate with high marketing investment and 
    30% with low investment. Current market analysis indicates moderate competition.
    """

    # Execute pipeline
    logger.info("🔄 Executing MSA pipeline...")
    result = await pipeline.execute(scenario, session_id="test_session_001")

    # Verify results
    assert result.status == "completed", f"Pipeline should complete successfully, got: {result.status}"
    assert result.final_result is not None, "Should have final result"
    assert len(result.stage_results) == 5, f"Should have 5 stage results, got: {len(result.stage_results)}"

    logger.info("✅ Pipeline execution successful")
    logger.info(f"   Total execution time: {result.total_execution_time:.2f}s")
    logger.info(f"   Session ID: {result.session_id}")

    # Display results
    logger.info("📊 Pipeline Results:")
    for stage_type, stage_result in result.stage_results.items():
        logger.info(f"   {stage_type.value}: {stage_result.status.value} ({stage_result.execution_time:.3f}s)")

    if result.final_result:
        execution_summary = result.final_result.get("execution_summary", {})
        logger.info(
            f"   Summary: {execution_summary.get('completed_stages', 0)}/{execution_summary.get('total_stages', 0)} stages completed"
        )

        integrated_reasoning = result.final_result.get("integrated_reasoning", {})
        if integrated_reasoning:
            logger.info(f"   Final Answer: {integrated_reasoning.get('final_answer', 'No answer')}")

        confidence_metrics = result.final_result.get("confidence_metrics", {})
        if confidence_metrics:
            overall_confidence = confidence_metrics.get("overall_confidence", 0)
            logger.info(f"   Overall Confidence: {overall_confidence:.2f}")

    logger.info("🎉 MSA Pipeline Test Completed Successfully!")
    return result


if __name__ == "__main__":
    # Run the test
    result = asyncio.run(test_msa_pipeline())
