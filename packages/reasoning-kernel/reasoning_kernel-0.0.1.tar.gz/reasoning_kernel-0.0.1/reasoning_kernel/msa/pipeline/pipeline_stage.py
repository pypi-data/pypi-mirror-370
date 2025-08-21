"""
MSA Pipeline Stage Base Class

This module defines the base interface for MSA pipeline stages, providing
a clean architecture for the 5-stage MSA reasoning process.
"""

from abc import ABC, abstractmethod
import asyncio
from dataclasses import dataclass
from enum import Enum
import logging
import time
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)


class StageStatus(Enum):
    """Stage execution status"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class StageType(Enum):
    """MSA Pipeline stage types"""

    KNOWLEDGE_EXTRACTION = "knowledge_extraction"
    MODEL_SPECIFICATION = "model_specification"
    MODEL_SYNTHESIS = "model_synthesis"
    PROBABILISTIC_INFERENCE = "probabilistic_inference"
    RESULT_INTEGRATION = "result_integration"


@dataclass
class StageResult:
    """Result from a pipeline stage execution"""

    stage_type: StageType
    status: StageStatus
    data: Dict[str, Any]
    execution_time: float
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class PipelineContext:
    """Context passed between pipeline stages"""

    scenario: str
    session_id: str
    user_context: Dict[str, Any]
    stage_results: Dict[StageType, StageResult]
    global_metadata: Dict[str, Any]

    def get_result(self, stage_type: StageType) -> Optional[StageResult]:
        """Get result from a previous stage"""
        return self.stage_results.get(stage_type)

    def add_result(self, result: StageResult):
        """Add result from a completed stage"""
        self.stage_results[result.stage_type] = result


class PipelineStage(ABC):
    """
    Base class for MSA pipeline stages.

    Each stage implements a specific part of the MSA reasoning process:
    - Knowledge Extraction: Extract domain knowledge from LLM
    - Model Specification: Define probabilistic model structure
    - Model Synthesis: Generate executable probabilistic programs
    - Probabilistic Inference: Run inference and sampling
    - Result Integration: Synthesize results with confidence metrics
    """

    def __init__(self, stage_type: StageType, config: Optional[Dict[str, Any]] = None):
        self.stage_type = stage_type
        self.config = config or {}
        self.timeout = self.config.get("timeout", 300)  # 5 minutes default
        self.retry_count = self.config.get("retry_count", 3)

    @abstractmethod
    async def execute(self, context: PipelineContext) -> StageResult:
        """
        Execute the stage with the given context.

        Args:
            context: Pipeline context containing scenario and previous results

        Returns:
            StageResult with execution status and output data

        Raises:
            StageExecutionError: If stage execution fails
        """
        pass

    async def run_with_timeout(self, context: PipelineContext) -> StageResult:
        """Execute stage with timeout and error handling"""
        start_time = time.time()

        try:
            logger.info(f"Starting stage: {self.stage_type.value}")

            # Execute with timeout
            result = await asyncio.wait_for(self.execute(context), timeout=self.timeout)

            result.execution_time = time.time() - start_time
            logger.info(f"Stage {self.stage_type.value} completed in {result.execution_time:.2f}s")

            return result

        except asyncio.TimeoutError:
            execution_time = time.time() - start_time
            error_msg = f"Stage {self.stage_type.value} timed out after {execution_time:.2f}s"
            logger.error(error_msg)

            return StageResult(
                stage_type=self.stage_type,
                status=StageStatus.FAILED,
                data={},
                execution_time=execution_time,
                error=error_msg,
            )

        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Stage {self.stage_type.value} failed: {str(e)}"
            logger.error(error_msg, exc_info=True)

            return StageResult(
                stage_type=self.stage_type,
                status=StageStatus.FAILED,
                data={},
                execution_time=execution_time,
                error=error_msg,
            )

    def validate_dependencies(self, context: PipelineContext) -> bool:
        """
        Validate that required previous stages have completed successfully.
        Override in subclasses to define stage dependencies.
        """
        return True

    def can_skip(self, context: PipelineContext) -> bool:
        """
        Determine if this stage can be skipped based on context.
        Override in subclasses to implement skip logic.
        """
        return False


class StageExecutionError(Exception):
    """Exception raised when a pipeline stage fails to execute"""

    def __init__(self, stage_type: StageType, message: str, original_error: Optional[Exception] = None):
        self.stage_type = stage_type
        self.original_error = original_error
        super().__init__(f"Stage {stage_type.value} failed: {message}")


class StageValidationError(Exception):
    """Exception raised when stage validation fails"""

    def __init__(self, stage_type: StageType, missing_dependencies: List[StageType]):
        self.stage_type = stage_type
        self.missing_dependencies = missing_dependencies
        deps_str = ", ".join([dep.value for dep in missing_dependencies])
        super().__init__(f"Stage {stage_type.value} requires completed stages: {deps_str}")
