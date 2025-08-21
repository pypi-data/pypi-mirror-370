"""
MSA Pipeline Orchestrator

This module implements the main MSA pipeline that orchestrates the 5-stage
reasoning process with proper error handling and stage transitions.
"""

from datetime import datetime
import time
from typing import Any, Dict, List, Optional

from reasoning_kernel.core.profiling import performance_monitor
from reasoning_kernel.core.settings import settings
from reasoning_kernel.core.tracing import correlation_context
from reasoning_kernel.core.tracing import get_correlation_id
from reasoning_kernel.core.tracing import get_logger
from reasoning_kernel.core.tracing import MSAStageTracer
from reasoning_kernel.core.tracing import trace_operation
from reasoning_kernel.msa.pipeline.pipeline_stage import PipelineContext
from reasoning_kernel.msa.pipeline.pipeline_stage import PipelineStage
from reasoning_kernel.msa.pipeline.pipeline_stage import StageResult
from reasoning_kernel.msa.pipeline.pipeline_stage import StageStatus
from reasoning_kernel.msa.pipeline.pipeline_stage import StageType
from reasoning_kernel.msa.pipeline.pipeline_stage import StageValidationError


logger = get_logger(__name__)


class PipelineExecutionResult:
    """Complete MSA pipeline execution result"""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
        self.total_execution_time: float = 0
        self.status: str = "running"
        self.stage_results: Dict[StageType, StageResult] = {}
        self.final_result: Optional[Dict[str, Any]] = None
        self.error: Optional[str] = None

    def mark_completed(self, final_result: Dict[str, Any]):
        """Mark pipeline as successfully completed"""
        self.end_time = datetime.now()
        self.total_execution_time = (self.end_time - self.start_time).total_seconds()
        self.status = "completed"
        self.final_result = final_result

    def mark_failed(self, error: str):
        """Mark pipeline as failed"""
        self.end_time = datetime.now()
        self.total_execution_time = (self.end_time - self.start_time).total_seconds()
        self.status = "failed"
        self.error = error


class MSAPipeline:
    """
    Main MSA Pipeline orchestrator that manages the 5-stage reasoning process:

    1. Knowledge Extraction Stage - Extract relevant knowledge from LLM
    2. Model Specification Stage - Define probabilistic model structure
    3. Model Synthesis Stage - Generate executable probabilistic programs
    4. Probabilistic Inference Stage - Run probabilistic inference and sampling
    5. Result Integration Stage - Synthesize results with confidence metrics
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.stages: List[PipelineStage] = []
        self.stage_map: Dict[StageType, PipelineStage] = {}
        self.execution_history: Dict[str, PipelineExecutionResult] = {}

        # Pipeline configuration from settings
        self.max_reasoning_steps = settings.max_reasoning_steps
        self.max_iterations = settings.max_iterations
        self.confidence_threshold = settings.confidence_threshold
        self.uncertainty_threshold = settings.uncertainty_threshold

        # Timeouts from settings
        self.reasoning_timeout = settings.reasoning_timeout
        self.knowledge_extraction_timeout = settings.knowledge_extraction_timeout
        self.probabilistic_synthesis_timeout = settings.probabilistic_synthesis_timeout

    def register_stage(self, stage: PipelineStage):
        """Register a pipeline stage"""
        if stage.stage_type in self.stage_map:
            logger.warning(f"Overriding existing stage: {stage.stage_type.value}")

        self.stage_map[stage.stage_type] = stage

        # Maintain ordered list of stages
        stage_order = [
            StageType.KNOWLEDGE_EXTRACTION,
            StageType.MODEL_SPECIFICATION,
            StageType.MODEL_SYNTHESIS,
            StageType.PROBABILISTIC_INFERENCE,
            StageType.RESULT_INTEGRATION,
        ]

        # Rebuild stages list in proper order
        self.stages = [self.stage_map[stage_type] for stage_type in stage_order if stage_type in self.stage_map]

        logger.info(f"Registered stage: {stage.stage_type.value}")

    def is_complete(self) -> bool:
        """Check if all required stages are registered"""
        required_stages = {
            StageType.KNOWLEDGE_EXTRACTION,
            StageType.MODEL_SPECIFICATION,
            StageType.MODEL_SYNTHESIS,
            StageType.PROBABILISTIC_INFERENCE,
            StageType.RESULT_INTEGRATION,
        }

        registered_stages = set(self.stage_map.keys())
        return required_stages.issubset(registered_stages)

    async def execute(
        self, scenario: str, session_id: Optional[str] = None, user_context: Optional[Dict[str, Any]] = None
    ) -> PipelineExecutionResult:
        """
        Execute the complete MSA pipeline with full tracing.

        Args:
            scenario: The reasoning scenario or question
            session_id: Optional session identifier
            user_context: Optional user-provided context

        Returns:
            PipelineExecutionResult with complete execution details
        """
        # Generate session ID if not provided
        if session_id is None:
            session_id = f"msa_session_{int(time.time() * 1000)}"

        # Use session_id as correlation_id for tracing
        correlation_id = get_correlation_id()

        with correlation_context(correlation_id, session_id=session_id, scenario=scenario[:100]):
            # Temporarily disabled performance monitoring to fix CLI
            # with performance_monitor("msa.pipeline.execute", log_threshold=10.0, monitor_memory=True):
                with trace_operation(
                    "msa.pipeline.execute",
                    attributes={
                        "msa.session_id": session_id,
                        "msa.scenario_length": len(scenario),
                        "msa.has_user_context": user_context is not None,
                    },
                ) as span:
                    logger.info(f"Starting MSA pipeline execution for session: {session_id}")

                    # Initialize execution result
                    execution_result = PipelineExecutionResult(session_id)
                    self.execution_history[session_id] = execution_result

                    try:
                        # Validate pipeline completeness
                        if not self.is_complete():
                            missing_stages = self._get_missing_stages()
                            error_msg = f"Pipeline incomplete. Missing stages: {missing_stages}"
                            span.add_event("pipeline_validation_failed", {"missing_stages": str(missing_stages)})
                            execution_result.mark_failed(error_msg)
                            return execution_result

                        # Initialize pipeline context
                        context = PipelineContext(
                            scenario=scenario,
                            session_id=session_id,
                            user_context=user_context or {},
                            stage_results={},
                            global_metadata={
                                "pipeline_start_time": datetime.now().isoformat(),
                                "max_reasoning_steps": self.max_reasoning_steps,
                                "confidence_threshold": self.confidence_threshold,
                                "settings_environment": settings.environment.value,
                                "correlation_id": correlation_id,
                            },
                        )

                        span.add_event("pipeline_context_initialized")

                        # Execute stages sequentially with tracing
                        for stage in self.stages:
                            span.add_event(f"executing_stage_{stage.stage_type.value}")

                            stage_result = await self._execute_stage(stage, context)

                            # Add result to context and execution result
                            context.add_result(stage_result)
                            execution_result.stage_results[stage.stage_type] = stage_result

                            # Record stage completion in span
                            span.set_attribute(f"msa.stage.{stage.stage_type.value}.status", stage_result.status.value)
                            span.set_attribute(
                                f"msa.stage.{stage.stage_type.value}.duration", str(stage_result.execution_time)
                            )

                            # Handle stage failure
                            if stage_result.status == StageStatus.FAILED:
                                error_msg = f"Stage {stage.stage_type.value} failed: {stage_result.error}"
                                span.add_event(
                                    "stage_failed",
                                    {"stage": stage.stage_type.value, "error": stage_result.error or "Unknown error"},
                                )
                                execution_result.mark_failed(error_msg)
                                return execution_result

                            # Check if we should continue
                            if not self._should_continue_pipeline(stage_result, context):
                                logger.info(f"Pipeline execution stopped after stage: {stage.stage_type.value}")
                                span.add_event("pipeline_stopped_early", {"last_stage": stage.stage_type.value})
                                break

                        # Generate final integrated result
                        span.add_event("generating_final_result")
                        final_result = await self._generate_final_result(context)
                        execution_result.mark_completed(final_result)

                        # Record success metrics
                        span.set_attribute("msa.pipeline.status", "completed")
                        span.set_attribute("msa.pipeline.total_stages", str(len(self.stages)))
                        span.set_attribute("msa.pipeline.execution_time", str(execution_result.total_execution_time))

                        logger.info(f"MSA pipeline completed successfully for session: {session_id}")
                        logger.info(f"Total execution time: {execution_result.total_execution_time:.2f}s")

                        return execution_result

                    except Exception as e:
                        error_msg = f"Pipeline execution failed: {str(e)}"
                        span.add_event("pipeline_execution_failed", {"error": error_msg})
                        logger.error(error_msg, exc_info=True)
                        execution_result.mark_failed(error_msg)
                        return execution_result

    async def _execute_stage(self, stage: PipelineStage, context: PipelineContext) -> StageResult:
        """Execute a single pipeline stage with proper error handling and tracing"""
        stage_tracer = MSAStageTracer(stage.stage_type.value, stage.stage_type.value)

        # Temporarily disabled performance monitoring to fix CLI
        # with performance_monitor(f"msa.stage.{stage.stage_type.value}", log_threshold=5.0, monitor_memory=True):
        with stage_tracer.trace_stage_execution(
                input_data={"scenario": context.scenario}, metadata={"session_id": context.session_id}
            ) as stage_span:
                try:
                    stage_span.add_event("validating_dependencies")

                    # Validate stage dependencies
                    if not stage.validate_dependencies(context):
                        missing_deps = self._get_missing_dependencies(stage, context)
                        stage_span.add_event("validation_failed", {"missing_dependencies": str(missing_deps)})
                        raise StageValidationError(stage.stage_type, missing_deps)

                    stage_span.add_event("dependencies_validated")

                    # Check if stage can be skipped
                    if stage.can_skip(context):
                        logger.info(f"Skipping stage: {stage.stage_type.value}")
                        stage_span.add_event("stage_skipped")
                        return StageResult(
                            stage_type=stage.stage_type,
                            status=StageStatus.SKIPPED,
                            data={},
                            execution_time=0,
                            metadata={"skip_reason": "Stage conditions met for skipping"},
                        )

                    stage_span.add_event("executing_stage")

                    # Execute stage with timeout and tracing
                    stage_result = await stage.run_with_timeout(context)

                    # Record stage result in span
                    stage_span.record_output(
                        {
                            "status": stage_result.status.value,
                            "execution_time": stage_result.execution_time,
                            "has_data": len(stage_result.data) > 0,
                            "has_error": stage_result.error is not None,
                        }
                    )

                    stage_span.add_event(
                        "stage_completed",
                        {"status": stage_result.status.value, "execution_time": str(stage_result.execution_time)},
                    )

                    return stage_result

                except StageValidationError as e:
                    stage_span.add_event("stage_validation_error", {"error": str(e)})
                    logger.error(f"Stage validation failed: {e}")
                    return StageResult(
                        stage_type=stage.stage_type, status=StageStatus.FAILED, data={}, execution_time=0, error=str(e)
                    )
                except Exception as e:
                    stage_span.add_event("stage_unexpected_error", {"error": str(e)})
                    logger.error(f"Unexpected error executing stage {stage.stage_type.value}: {e}", exc_info=True)
                    return StageResult(
                        stage_type=stage.stage_type,
                        status=StageStatus.FAILED,
                        data={},
                        execution_time=0,
                        error=f"Unexpected error: {str(e)}",
                    )

    def _should_continue_pipeline(self, stage_result: StageResult, context: PipelineContext) -> bool:
        """Determine if pipeline should continue after current stage"""
        # Always continue if stage succeeded
        if stage_result.status == StageStatus.COMPLETED:
            return True

        # Stop on failure (already handled above)
        if stage_result.status == StageStatus.FAILED:
            return False

        # Continue if stage was skipped
        if stage_result.status == StageStatus.SKIPPED:
            return True

        return True

    async def _generate_final_result(self, context: PipelineContext) -> Dict[str, Any]:
        """Generate final integrated result from all stage outputs"""
        final_result = {
            "session_id": context.session_id,
            "scenario": context.scenario,
            "execution_summary": {
                "total_stages": len(context.stage_results),
                "completed_stages": len(
                    [r for r in context.stage_results.values() if r.status == StageStatus.COMPLETED]
                ),
                "failed_stages": len([r for r in context.stage_results.values() if r.status == StageStatus.FAILED]),
                "skipped_stages": len([r for r in context.stage_results.values() if r.status == StageStatus.SKIPPED]),
                "total_execution_time": sum(r.execution_time for r in context.stage_results.values()),
            },
            "stage_results": {},
            "integrated_reasoning": {},
            "confidence_metrics": {},
            "metadata": context.global_metadata,
        }

        # Add stage results
        for stage_type, stage_result in context.stage_results.items():
            final_result["stage_results"][stage_type.value] = {
                "status": stage_result.status.value,
                "execution_time": stage_result.execution_time,
                "data": stage_result.data,
                "error": stage_result.error,
                "metadata": stage_result.metadata,
            }

        # Extract key results from integration stage
        integration_result = context.get_result(StageType.RESULT_INTEGRATION)
        if integration_result and integration_result.status == StageStatus.COMPLETED:
            final_result["integrated_reasoning"] = integration_result.data.get("integrated_reasoning", {})
            final_result["confidence_metrics"] = integration_result.data.get("confidence_metrics", {})

        return final_result

    def _get_missing_stages(self) -> List[str]:
        """Get list of missing required stages"""
        required_stages = {
            StageType.KNOWLEDGE_EXTRACTION,
            StageType.MODEL_SPECIFICATION,
            StageType.MODEL_SYNTHESIS,
            StageType.PROBABILISTIC_INFERENCE,
            StageType.RESULT_INTEGRATION,
        }

        registered_stages = set(self.stage_map.keys())
        missing = required_stages - registered_stages
        return [stage.value for stage in missing]

    def _get_missing_dependencies(self, stage: PipelineStage, context: PipelineContext) -> List[StageType]:
        """Get missing dependencies for a stage - override in subclasses for specific logic"""
        # This is a placeholder - individual stages should implement their own dependency validation
        return []

    def get_execution_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get execution status for a session"""
        execution_result = self.execution_history.get(session_id)
        if not execution_result:
            return None

        return {
            "session_id": session_id,
            "status": execution_result.status,
            "start_time": execution_result.start_time.isoformat(),
            "end_time": execution_result.end_time.isoformat() if execution_result.end_time else None,
            "execution_time": execution_result.total_execution_time,
            "completed_stages": len(
                [r for r in execution_result.stage_results.values() if r.status == StageStatus.COMPLETED]
            ),
            "total_stages": len(execution_result.stage_results),
            "error": execution_result.error,
        }
