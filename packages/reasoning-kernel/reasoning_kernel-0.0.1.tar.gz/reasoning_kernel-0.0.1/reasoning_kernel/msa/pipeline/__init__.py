"""
MSA Pipeline Package

Clean 5-stage MSA pipeline architecture:
1. Knowledge Extraction Stage - Extract domain knowledge from LLM
2. Model Specification Stage - Define probabilistic model structure
3. Model Synthesis Stage - Generate executable probabilistic programs
4. Probabilistic Inference Stage - Run inference and sampling
5. Result Integration Stage - Synthesize results with confidence metrics
"""

from reasoning_kernel.msa.pipeline.msa_pipeline import MSAPipeline
from reasoning_kernel.msa.pipeline.pipeline_stage import PipelineContext
from reasoning_kernel.msa.pipeline.pipeline_stage import PipelineStage
from reasoning_kernel.msa.pipeline.pipeline_stage import StageExecutionError
from reasoning_kernel.msa.pipeline.pipeline_stage import StageResult
from reasoning_kernel.msa.pipeline.pipeline_stage import StageStatus
from reasoning_kernel.msa.pipeline.pipeline_stage import StageType
from reasoning_kernel.msa.pipeline.pipeline_stage import StageValidationError


__all__ = [
    "MSAPipeline",
    "PipelineStage",
    "PipelineContext",
    "StageResult",
    "StageStatus",
    "StageType",
    "StageExecutionError",
    "StageValidationError",
]
