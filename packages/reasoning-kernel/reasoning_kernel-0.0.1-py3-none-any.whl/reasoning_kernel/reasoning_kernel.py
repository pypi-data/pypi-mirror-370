"""
Reasoning Kernel - Main Orchestrator
====================================

Implements the five-stage MSA pipeline:
1. Parse - Transform vignettes into structured constraints
2. Retrieve - Gather relevant background knowledge
3. Graph - Build causal dependency graphs
4. Synthesize - Generate probabilistic programs
5. Infer - Execute inference in secure sandbox

Integrates all plugins with error handling, retry logic, and comprehensive logging.
"""

import asyncio
from dataclasses import asdict
from dataclasses import dataclass
from enum import Enum
import json
import time
from typing import Any, cast, Dict, List, Optional

from semantic_kernel import Kernel  # type: ignore[import-untyped]
import structlog  # type: ignore[import-untyped]

from .plugins import InferencePlugin
from .plugins import KnowledgePlugin
from .plugins import ParsingPlugin
from .plugins import SynthesisPlugin
from .utils.reasoning_chains import ReasoningChain
from .utils.reasoning_chains import ReasoningStep


try:
    from .api.annotation_endpoints import manager as annotation_manager
except Exception:  # Make optional for test environments
    annotation_manager = None  # type: ignore[assignment]

logger = structlog.get_logger(__name__)


class ReasoningStage(Enum):
    PARSE = "parse"
    RETRIEVE = "retrieve"
    GRAPH = "graph"
    SYNTHESIZE = "synthesize"
    INFER = "infer"


@dataclass
class ReasoningConfig:
    """Configuration for reasoning pipeline"""

    # Model selection per stage
    parse_model: str = "gemini-2.5-pro"
    retrieve_top_k: int = 5
    graph_model: str = "phi-4-reasoning"
    synthesis_model: str = "gemini-2.5-pro"
    inference_samples: int = 1000

    # Error handling
    max_retries: int = 3
    fallback_models: Optional[Dict[str, str]] = None

    # Performance settings
    timeout_per_stage: int = 120
    enable_parallel_processing: bool = True

    # Thinking mode settings
    enable_thinking_mode: bool = True
    thinking_detail_level: str = "detailed"  # "minimal", "moderate", "detailed"
    generate_reasoning_sentences: bool = True
    include_step_by_step_thinking: bool = True

    def __post_init__(self):
        if self.fallback_models is None:
            self.fallback_models = {
                "parse": "o4-mini",
                "graph": "o4-mini",
                "synthesis": "o4-mini",
            }


@dataclass
class ReasoningResult:
    """Complete result from five-stage reasoning pipeline"""

    # Stage results
    parsed_vignette: Optional[Any] = None
    retrieval_context: Optional[Any] = None
    dependency_graph: Optional[Any] = None
    probabilistic_program: Optional[Any] = None
    inference_result: Optional[Any] = None

    # Meta information
    reasoning_chain: Optional[ReasoningChain] = None
    total_execution_time: float = 0.0
    overall_confidence: float = 0.0
    success: bool = False
    error_message: Optional[str] = None

    # Stage-specific metadata
    stage_timings: Optional[Dict[str, float]] = None
    stage_confidences: Optional[Dict[str, float]] = None

    # Thinking mode outputs
    thinking_process: Optional[List[str]] = None
    reasoning_sentences: Optional[List[str]] = None
    step_by_step_analysis: Optional[Dict[str, List[str]]] = None

    def __post_init__(self):
        if self.stage_timings is None:
            self.stage_timings = {}
        if self.stage_confidences is None:
            self.stage_confidences = {}
        if self.thinking_process is None:
            self.thinking_process = []
        if self.reasoning_sentences is None:
            self.reasoning_sentences = []
        if self.step_by_step_analysis is None:
            self.step_by_step_analysis = {}


# --- Pipeline callback/dataclass abstractions (moved to module scope for reuse) ---
@dataclass
class CallbackBundle:
    """Holds optional callback callables for pipeline execution.

    Each attribute should be an awaitable callable or None.
    Names mirror existing streaming interface to preserve behavior.
    """

    on_stage_start: Optional[Any] = None
    on_stage_complete: Optional[Any] = None
    on_thinking_sentence: Optional[Any] = None
    on_sandbox_event: Optional[Any] = None


@dataclass
class StageDescriptor:
    """Descriptor for a single pipeline stage used by unified executor.

    exec_factory returns an awaitable that performs the stage work when awaited.
    completion_payload is a callable(result_obj) -> Dict used for callbacks.
    """

    name: str
    stage: ReasoningStage
    exec_factory: Any  # () -> awaitable
    completion_payload: Any  # (result_obj) -> Dict[str, Any]
    predicate: Optional[Any] = None  # (ReasoningResult) -> bool
    sandbox_events: Optional[Dict[str, str]] = None  # optional messages for sandbox lifecycle

    def should_run(self, result: "ReasoningResult") -> bool:
        if self.predicate is None:
            return True
        try:
            return bool(self.predicate(result))
        except Exception:
            return False

    # convenience
    def build_payload(self, stage_result: Any) -> Dict[str, Any]:
        try:
            return self.completion_payload(stage_result) if self.completion_payload else {}
        except Exception:
            return {}


class ReasoningKernel:
    """
    Main orchestrator for the five-stage reasoning pipeline

    Coordinates ParsingPlugin, KnowledgePlugin, SynthesisPlugin, and InferencePlugin
    to implement the complete MSA reasoning process with error handling and monitoring.
    """

    def __init__(self, kernel: Kernel, redis_client, config: Optional[ReasoningConfig] = None):
        self.kernel = kernel
        self.redis_client = redis_client
        self.config = config or ReasoningConfig()

        # Initialize plugins
        self.parsing_plugin = ParsingPlugin(kernel, redis_client)
        self.knowledge_plugin = KnowledgePlugin(redis_client)
        self.synthesis_plugin = SynthesisPlugin(kernel)
        self.inference_plugin = InferencePlugin()

        logger.info("Reasoning Kernel initialized", config=asdict(self.config))

    async def reason_with_streaming(
        self,
        vignette: str,
        session_id: str,
        config: Optional[ReasoningConfig] = None,
        on_stage_start=None,
        on_stage_complete=None,
        on_thinking_sentence=None,
        on_sandbox_event=None,
        **kwargs,
    ) -> ReasoningResult:
        """Public streaming entrypoint delegating to unified pipeline."""
        self.config = config or self.config
        callbacks = CallbackBundle(
            on_stage_start=on_stage_start,
            on_stage_complete=on_stage_complete,
            on_thinking_sentence=on_thinking_sentence,
            on_sandbox_event=on_sandbox_event,
        )
        return await self._run_pipeline(
            vignette=vignette,
            data=kwargs.get("data"),
            session_id=session_id,
            callbacks=callbacks,
            streaming=True,
        )

    async def _reason_with_callbacks(self, *args, **kwargs):  # Backwards compatibility shim
        return await self._run_pipeline(*args, **kwargs)

    async def _generate_streaming_thoughts(
        self, result: ReasoningResult, vignette: str, chain: ReasoningChain, on_thinking_sentence
    ):
        """Generate natural language thinking sentences in real-time"""
        if not on_thinking_sentence:
            return

        thoughts = [
            "Let me analyze this scenario step by step using probabilistic reasoning...",
            f"The key question here involves understanding {vignette[:50]}...",
            "I'll need to model the uncertainty and causal relationships involved.",
        ]

        # Add stage-specific thoughts
        if result.parsed_vignette:
            thoughts.append("I've identified the main entities and constraints that define this problem space.")

        if result.retrieval_context:
            thoughts.append("My knowledge base provides relevant context from similar scenarios.")

        if result.dependency_graph:
            thoughts.append("The causal structure reveals how different factors influence each other.")

        if result.probabilistic_program:
            thoughts.append("I've constructed a probabilistic model to quantify the uncertainties.")

        if result.inference_result:
            thoughts.append("The Bayesian inference results provide probability distributions for key outcomes.")

        thoughts.append(
            f"Based on this cognitive modeling, I can provide insights with {result.overall_confidence:.0%} confidence."
        )

        # Stream thoughts with delays for natural feel
        for thought in thoughts:
            if on_thinking_sentence:
                await on_thinking_sentence(thought)
                await asyncio.sleep(0.5)  # Natural pacing

    async def reason(self, vignette: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> ReasoningResult:
        logger.info("Starting five-stage reasoning", vignette_length=len(vignette))
        return await self._run_pipeline(
            vignette=vignette,
            data=data,
            session_id=None,
            callbacks=CallbackBundle(),
            streaming=False,
        )

    # --- Unified internal pipeline executor ---
    async def _run_pipeline(
        self,
        vignette: str,
        data: Optional[Dict[str, Any]],
        session_id: Optional[str],
        callbacks: CallbackBundle,
        streaming: bool = False,
    ) -> ReasoningResult:
        logger.info(
            "Running unified reasoning pipeline",
            session_id=session_id,
            streaming=streaming,
        )
        chain = ReasoningChain(session_id=session_id)
        chain.start_reasoning(vignette, {"data_provided": data is not None})
        result = ReasoningResult(reasoning_chain=chain)
        start_time = time.time()

        def _queries_from_parsed(parsed_obj):
            if not parsed_obj:
                return [vignette]
            q_attr = getattr(parsed_obj, "queries", []) or []
            if q_attr:
                return [getattr(q, "content", str(q)) for q in q_attr]
            return [vignette]

        descriptors: List[StageDescriptor] = [
            StageDescriptor(
                name="parse",
                stage=ReasoningStage.PARSE,
                exec_factory=lambda: self.parsing_plugin.parse_vignette(vignette),
                completion_payload=self._build_parse_payload,
            ),
            StageDescriptor(
                name="retrieve",
                stage=ReasoningStage.RETRIEVE,
                predicate=lambda r: r.parsed_vignette is not None,
                exec_factory=lambda: self.knowledge_plugin.retrieve_context(
                    _queries_from_parsed(result.parsed_vignette),
                    top_k=self.config.retrieve_top_k,
                ),
                completion_payload=self._build_retrieve_payload,
            ),
            StageDescriptor(
                name="graph",
                stage=ReasoningStage.GRAPH,
                predicate=lambda r: r.retrieval_context is not None,
                exec_factory=lambda: self.synthesis_plugin.generate_dependency_graph(
                    getattr(result.retrieval_context, "augmented_context", str(result.retrieval_context))
                ),
                completion_payload=self._build_graph_payload,
            ),
            StageDescriptor(
                name="synthesize",
                stage=ReasoningStage.SYNTHESIZE,
                predicate=lambda r: r.dependency_graph is not None,
                exec_factory=lambda: self.synthesis_plugin.generate_probabilistic_program(
                    cast(Any, result.dependency_graph)  # predicate ensures not None
                ),
                completion_payload=self._build_synthesize_payload,
                sandbox_events={
                    "start": "Initializing Daytona sandbox for probabilistic program synthesis...",
                },
            ),
            StageDescriptor(
                name="infer",
                stage=ReasoningStage.INFER,
                predicate=lambda r: (
                    r.probabilistic_program and getattr(r.probabilistic_program, "validation_status", False)
                ),
                exec_factory=lambda: self.inference_plugin.execute_inference(
                    getattr(result.probabilistic_program, "program_code", ""),
                    data=data,
                    num_samples=self.config.inference_samples,
                ),
                completion_payload=self._build_infer_payload,
                sandbox_events={
                    "exec": "Executing probabilistic inference in secure Daytona sandbox...",
                    "complete": "Inference completed successfully in Daytona sandbox",
                },
            ),
        ]

        try:
            for desc in descriptors:
                if not desc.should_run(result):
                    continue

                if callbacks.on_stage_start:
                    try:
                        await callbacks.on_stage_start(desc.name)
                    except Exception:
                        logger.warning("on_stage_start callback failed", stage=desc.name)

                if callbacks.on_sandbox_event and desc.sandbox_events and "start" in desc.sandbox_events:
                    await callbacks.on_sandbox_event(
                        {"type": "sandbox_starting", "message": desc.sandbox_events["start"]}
                    )

                stage_result = await self._execute_stage(desc.stage, chain, result, desc.exec_factory)

                if desc.stage is ReasoningStage.PARSE:
                    result.parsed_vignette = stage_result
                elif desc.stage is ReasoningStage.RETRIEVE:
                    result.retrieval_context = stage_result
                elif desc.stage is ReasoningStage.GRAPH:
                    result.dependency_graph = stage_result
                elif desc.stage is ReasoningStage.SYNTHESIZE:
                    result.probabilistic_program = stage_result
                elif desc.stage is ReasoningStage.INFER:
                    result.inference_result = stage_result

                if callbacks.on_sandbox_event and desc.sandbox_events and desc.name == "infer":
                    await callbacks.on_sandbox_event(
                        {"type": "sandbox_executing", "message": desc.sandbox_events.get("exec")}
                    )

                if (
                    callbacks.on_sandbox_event
                    and desc.sandbox_events
                    and "complete" in desc.sandbox_events
                    and desc.name == "infer"
                ):
                    await callbacks.on_sandbox_event(
                        {"type": "sandbox_complete", "message": desc.sandbox_events["complete"]}
                    )

                if callbacks.on_stage_complete:
                    payload = desc.build_payload(stage_result)
                    payload.update(
                        {
                            "execution_time": result.stage_timings.get(desc.name, 0) if result.stage_timings else 0,
                            "confidence": result.stage_confidences.get(desc.name, 0) if result.stage_confidences else 0,
                        }
                    )
                    try:
                        await callbacks.on_stage_complete(desc.name, payload)
                    except Exception:
                        logger.warning("on_stage_complete callback failed", stage=desc.name)

                if streaming and callbacks.on_thinking_sentence:
                    try:
                        await callbacks.on_thinking_sentence(
                            self._get_stage_completion_description(desc.name, stage_result)
                        )
                    except Exception:
                        pass

            if self.config.enable_thinking_mode:
                if streaming and callbacks.on_thinking_sentence:
                    await self._generate_streaming_thoughts(result, vignette, chain, callbacks.on_thinking_sentence)
                else:
                    await self._generate_thinking_output(result, vignette, chain)

            result.total_execution_time = time.time() - start_time
            result.overall_confidence = self._calculate_overall_confidence(result)
            result.success = self._determine_success(result)
            chain.complete_reasoning(
                {
                    "success": result.success,
                    "total_time": result.total_execution_time,
                    "confidence": result.overall_confidence,
                    "stages_completed": len(result.stage_timings or {}),
                },
                result.total_execution_time,
            )
            logger.info(
                "Unified reasoning completed",
                success=result.success,
                confidence=result.overall_confidence,
                total_time=result.total_execution_time,
            )
            return result
        except (
            Exception
        ) as e:  # Broad exception handling is intentional here to ensure all errors are logged and reported in the result object, preventing crashes in the main orchestration pipeline.
            result.error_message = str(e)
            result.total_execution_time = time.time() - start_time
            result.success = False
            chain.complete_reasoning({"success": False, "error": str(e)}, result.total_execution_time)
            logger.error("Unified reasoning failed", error=str(e), execution_time=result.total_execution_time)
            return result

    async def _execute_stage(
        self, stage: ReasoningStage, chain: ReasoningChain, result: ReasoningResult, stage_function
    ) -> Any:
        """Execute a single stage with error handling and timing"""

        stage_step = ReasoningStep(
            step_id=f"stage_{stage.value}",
            step_type="reasoning_stage",
            description=f"Executing {stage.value} stage",
            data={},
        )
        chain.steps.append(stage_step)

        start_time = time.time()

        # Send real-time progress update
        await self._send_progress_update(
            chain.session_id,
            stage.value,
            "starting",
            {"description": self._get_stage_description(stage.value), "start_time": start_time},
        )

        try:
            # Execute stage with timeout
            stage_result = await asyncio.wait_for(stage_function(), timeout=self.config.timeout_per_stage)

            # Record timing and confidence
            execution_time = time.time() - start_time
            if result.stage_timings is None:
                result.stage_timings = {}
            result.stage_timings[stage.value] = execution_time

            if result.stage_confidences is None:
                result.stage_confidences = {}
            if hasattr(stage_result, "parsing_confidence"):
                result.stage_confidences[stage.value] = getattr(stage_result, "parsing_confidence")
            elif hasattr(stage_result, "retrieval_confidence"):
                result.stage_confidences[stage.value] = getattr(stage_result, "retrieval_confidence")
            elif hasattr(stage_result, "graph_confidence"):
                result.stage_confidences[stage.value] = getattr(stage_result, "graph_confidence")
            elif hasattr(stage_result, "confidence"):
                result.stage_confidences[stage.value] = getattr(stage_result, "confidence")
            else:
                result.stage_confidences[stage.value] = 0.8  # Default

            stage_step.complete(
                {
                    "stage": stage.value,
                    "execution_time": execution_time,
                    "confidence": result.stage_confidences.get(stage.value, 0),
                    "status": "completed",
                }
            )

            logger.info(
                f"Stage {stage.value} completed",
                execution_time=execution_time,
                confidence=result.stage_confidences.get(stage.value, 0),
            )

            # Send completion update
            await self._send_progress_update(
                chain.session_id,
                stage.value,
                "completed",
                {
                    "execution_time": execution_time,
                    "confidence": result.stage_confidences.get(stage.value, 0),
                    "description": self._get_stage_completion_description(stage.value, stage_result),
                },
            )

            return stage_result

        except asyncio.TimeoutError:
            stage_step.complete(
                {"stage": stage.value, "status": "timeout", "timeout_limit": self.config.timeout_per_stage}
            )

            logger.error(f"Stage {stage.value} timed out", timeout=self.config.timeout_per_stage)
            raise Exception(f"Stage {stage.value} timed out")

        except Exception as e:
            stage_step.complete({"stage": stage.value, "status": "failed", "error": str(e)})

            logger.error(f"Stage {stage.value} failed", error=str(e))
            raise

    def _calculate_overall_confidence(self, result: ReasoningResult) -> float:
        """Calculate overall confidence from stage confidences"""
        confidences = list((result.stage_confidences or {}).values())
        if not confidences:
            return 0.0
        weights = [1.0, 1.2, 1.4, 1.6, 1.8][: len(confidences)]
        weighted_sum = sum(c * w for c, w in zip(confidences, weights))
        weight_total = sum(weights)
        return weighted_sum / weight_total if weight_total > 0 else 0.0

    def _determine_success(self, result: ReasoningResult) -> bool:
        """Determine if reasoning was successful based on stages completed"""

        # Must complete at least parse and retrieve stages
        if not result.parsed_vignette or not result.retrieval_context:
            return False

        # If probabilistic program was generated but failed validation, partial success
        if result.probabilistic_program and not result.probabilistic_program.validation_status:
            return result.overall_confidence >= 0.5

        # Full success requires inference completion
        if result.inference_result and hasattr(result.inference_result, "inference_status"):
            if hasattr(result.inference_result.inference_status, "name"):
                return result.inference_result.inference_status.name == "COMPLETED"
            elif str(result.inference_result.inference_status) == "COMPLETED":
                return True
        # Partial success if most stages completed with reasonable confidence
        return len(result.stage_timings or {}) >= 3 and result.overall_confidence >= 0.6

    async def _send_progress_update(self, session_id: Optional[str], stage: str, status: str, details: dict):
        """Send real-time progress update via WebSocket.

        No-ops when session_id is not provided (e.g., non-streaming runs).
        """
        if not session_id:
            return
        try:
            message = {
                "type": "reasoning_progress",
                "session_id": session_id,
                "stage": stage,
                "status": status,
                "details": details,
                "timestamp": time.time(),
            }

            # Use the existing annotation manager to broadcast progress
            reasoning_chain_id = f"reasoning_{session_id}"
            if annotation_manager is not None:
                await annotation_manager.broadcast_to_chain(reasoning_chain_id, message)

        except Exception as e:
            logger.warning(f"Failed to send progress update: {e}")

    def _get_stage_description(self, stage: str) -> str:
        """Get declarative description for stage start"""
        descriptions = {
            "parse": "Analyzing the scenario to extract key entities, relationships, and constraints...",
            "retrieve": "Searching knowledge base for relevant background information and similar cases...",
            "graph": "Building causal dependency graph to understand factor interactions...",
            "synthesize": "Generating custom probabilistic model based on extracted knowledge...",
            "infer": "Running Bayesian inference to compute probability distributions and recommendations...",
        }
        return descriptions.get(stage, f"Processing {stage} stage...")

    def _get_stage_completion_description(self, stage: str, stage_result) -> str:
        """Get declarative description for stage completion"""
        descriptions = {
            "parse": f"Successfully identified {getattr(stage_result, 'entities_count', 0)} entities and {getattr(stage_result, 'constraints_count', 0)} constraints",
            "retrieve": f"Found {len(getattr(stage_result, 'documents', []))} relevant documents from knowledge base",
            "graph": f"Generated dependency graph with {getattr(stage_result, 'nodes_count', 0)} nodes and {getattr(stage_result, 'edges_count', 0)} causal relationships",
            "synthesize": f"Created probabilistic model with {getattr(stage_result, 'variables_count', 0)} variables ({getattr(stage_result, 'code_lines', 0)} lines of code)",
            "infer": f"Generated {getattr(stage_result, 'num_samples', 0)} posterior samples with {len(getattr(stage_result, 'posterior_samples', {}))} inferred parameters",
        }
        return descriptions.get(stage, f"Completed {stage} stage successfully")

    # --- Stage payload builders (used by unified pipeline) ---
    def _build_parse_payload(self, parsed) -> Dict[str, Any]:
        return {
            "confidence": getattr(parsed, "parsing_confidence", 0),
            "entities_count": getattr(
                parsed, "entities_count", getattr(parsed, "entities", []) and len(getattr(parsed, "entities", [])) or 0
            ),
            "constraints_count": getattr(
                parsed,
                "constraints_count",
                getattr(parsed, "constraints", []) and len(getattr(parsed, "constraints", [])) or 0,
            ),
        }

    def _build_retrieve_payload(self, retrieval) -> Dict[str, Any]:
        return {
            "confidence": getattr(retrieval, "retrieval_confidence", getattr(retrieval, "confidence", 0)),
            "documents_count": len(getattr(retrieval, "documents", []) or []),
        }

    def _build_graph_payload(self, graph) -> Dict[str, Any]:
        return {
            "confidence": getattr(graph, "graph_confidence", getattr(graph, "confidence", 0)),
            "nodes_count": getattr(graph, "nodes_count", len(getattr(graph, "nodes", []) or [])),
            "edges_count": getattr(graph, "edges_count", len(getattr(graph, "edges", []) or [])),
        }

    def _build_synthesize_payload(self, program) -> Dict[str, Any]:
        code = getattr(program, "program_code", "") or ""
        return {
            "confidence": getattr(program, "confidence", 0),
            "lines_count": len(code.split("\n")) if code else 0,
            "variables_count": getattr(program, "variables_count", len(getattr(program, "variables", []) or [])),
            "validation_status": getattr(program, "validation_status", None),
        }

    def _build_infer_payload(self, inference) -> Dict[str, Any]:
        return {
            "confidence": getattr(inference, "confidence", 0),
            "samples_count": getattr(inference, "num_samples", 0),
            "parameters_count": len(getattr(inference, "posterior_samples", {}) or {}),
            "inference_status": getattr(
                getattr(inference, "inference_status", None), "name", getattr(inference, "inference_status", None)
            ),
        }

    async def get_reasoning_status(self, session_id: str) -> Dict[str, Any]:
        """Get status of ongoing reasoning process"""
        # Implementation for tracking ongoing reasoning sessions
        # Would interface with Redis to get status
        try:
            status_key = f"reasoning:status:{session_id}"
            status_data = await self.redis_client.get(status_key)

            if status_data:
                return json.loads(status_data)
            else:
                return {"status": "not_found"}

        except Exception as e:
            logger.error("Failed to get reasoning status", error=str(e))
            return {"status": "error", "message": str(e)}

    async def cancel_reasoning(self, session_id: str) -> bool:
        """Cancel ongoing reasoning process"""
        try:
            status_key = f"reasoning:status:{session_id}"
            await self.redis_client.set(status_key, json.dumps({"status": "cancelled"}))
            logger.info("Reasoning cancelled", session_id=session_id)
            return True

        except Exception as e:
            logger.error("Failed to cancel reasoning", error=str(e))
            return False

    async def _generate_thinking_output(self, result: ReasoningResult, vignette: str, chain: ReasoningChain):
        """Generate sentence-based thinking process and reasoning output"""
        if not self.config.enable_thinking_mode:
            return

        logger.info("Generating thinking mode output", detail_level=self.config.thinking_detail_level)

        # Initialize thinking outputs
        result.thinking_process = []
        result.reasoning_sentences = []
        result.step_by_step_analysis = {}

        try:
            # Generate overall reasoning narrative
            if self.config.generate_reasoning_sentences:
                await self._generate_reasoning_sentences(result, vignette, chain)

            # Generate step-by-step thinking analysis
            if self.config.include_step_by_step_thinking:
                await self._generate_step_by_step_analysis(result, vignette, chain)

            # Generate thinking process summary
            await self._generate_thinking_summary(result, vignette, chain)

            logger.info(
                "Thinking mode output generated successfully",
                sentences_count=len(result.reasoning_sentences),
                thinking_steps=len(result.thinking_process),
            )

        except Exception as e:
            logger.error("Failed to generate thinking output", error=str(e))
            # Provide fallback thinking output
            result.thinking_process = [
                f"I'm analyzing the scenario: {vignette[:100]}...",
                "Processing the information through multiple reasoning stages...",
                f"Generated insights with {result.overall_confidence:.2f} confidence level.",
            ]

    async def _generate_reasoning_sentences(self, result: ReasoningResult, vignette: str, chain: ReasoningChain):
        """Generate coherent reasoning sentences that explain the thinking process"""

        reasoning_sentences = []

        # Analyze what we've learned at each stage
        if result.parsed_vignette:
            entities_count = getattr(result.parsed_vignette, "entities_count", 0)
            constraints_count = getattr(result.parsed_vignette, "constraints_count", 0)
            reasoning_sentences.append(
                f"I began by parsing the scenario and identified {entities_count} key entities and {constraints_count} important constraints that shape this situation."
            )

        if result.retrieval_context:
            docs_count = len(getattr(result.retrieval_context, "documents", []))
            reasoning_sentences.append(
                f"I then searched my knowledge base and found {docs_count} relevant documents that provide background context for this type of scenario."
            )

        if result.dependency_graph:
            nodes_count = getattr(result.dependency_graph, "nodes_count", 0)
            edges_count = getattr(result.dependency_graph, "edges_count", 0)
            reasoning_sentences.append(
                f"Next, I built a causal dependency graph with {nodes_count} factors and {edges_count} relationships to understand how different elements influence each other."
            )

        if result.probabilistic_program:
            variables_count = getattr(result.probabilistic_program, "variables_count", 0)
            reasoning_sentences.append(
                f"I synthesized this knowledge into a probabilistic model with {variables_count} variables that can quantify uncertainty and make predictions."
            )

        if result.inference_result:
            samples_count = getattr(result.inference_result, "num_samples", 0)
            params_count = len(getattr(result.inference_result, "posterior_samples", {}))
            reasoning_sentences.append(
                f"Finally, I ran Bayesian inference with {samples_count} samples to estimate {params_count} key parameters and their probability distributions."
            )

        # Add confidence assessment
        confidence_level = (
            "high" if result.overall_confidence > 0.8 else "moderate" if result.overall_confidence > 0.6 else "limited"
        )
        reasoning_sentences.append(
            f"Based on this analysis, I have {confidence_level} confidence (score: {result.overall_confidence:.2f}) in these conclusions."
        )

        # Add insights based on detail level
        if self.config.thinking_detail_level == "detailed":
            reasoning_sentences.extend(
                [
                    "The scenario involves complex interactions between multiple factors, requiring careful probabilistic reasoning.",
                    "Key uncertainties have been identified and quantified to provide actionable insights.",
                    f"This analysis took {result.total_execution_time:.1f} seconds across {len(result.stage_timings or {})} reasoning stages.",
                ]
            )
        elif self.config.thinking_detail_level == "moderate":
            reasoning_sentences.append(
                "The analysis reveals important patterns and relationships that inform decision-making."
            )

        result.reasoning_sentences = reasoning_sentences

    async def _generate_step_by_step_analysis(self, result: ReasoningResult, vignette: str, chain: ReasoningChain):
        """Generate detailed step-by-step analysis for each stage"""

        step_analysis = {}

        # Parse stage analysis
        if result.parsed_vignette:
            timings = result.stage_timings or {}
            confs = result.stage_confidences or {}
            step_analysis["parse"] = [
                "I started by carefully reading and parsing the scenario text.",
                "Extracted key entities and identified their roles and relationships.",
                "Found constraints and limitations that affect possible outcomes.",
                f"This parsing stage completed in {timings.get('parse', 0):.2f} seconds with {confs.get('parse', 0):.2f} confidence.",
            ]

        # Retrieve stage analysis
        if result.retrieval_context:
            timings = result.stage_timings or {}
            confs = result.stage_confidences or {}
            step_analysis["retrieve"] = [
                "I searched my knowledge base for similar scenarios and relevant information.",
                "Retrieved background knowledge about the domain and context.",
                "Cross-referenced findings with established patterns and research.",
                f"Knowledge retrieval took {timings.get('retrieve', 0):.2f} seconds with {confs.get('retrieve', 0):.2f} confidence.",
            ]

        # Graph stage analysis
        if result.dependency_graph:
            timings = result.stage_timings or {}
            confs = result.stage_confidences or {}
            step_analysis["graph"] = [
                "I constructed a causal dependency graph to model factor interactions.",
                "Identified direct and indirect causal relationships between variables.",
                "Analyzed feedback loops and emergent dependencies.",
                f"Graph generation completed in {timings.get('graph', 0):.2f} seconds with {confs.get('graph', 0):.2f} confidence.",
            ]

        # Synthesis stage analysis
        if result.probabilistic_program:
            timings = result.stage_timings or {}
            confs = result.stage_confidences or {}
            step_analysis["synthesize"] = [
                "I synthesized the knowledge into a custom probabilistic model.",
                "Defined probability distributions for uncertain variables.",
                "Specified causal relationships and conditional dependencies.",
                f"Model synthesis took {timings.get('synthesize', 0):.2f} seconds with {confs.get('synthesize', 0):.2f} confidence.",
            ]

        # Inference stage analysis
        if result.inference_result:
            timings = result.stage_timings or {}
            confs = result.stage_confidences or {}
            step_analysis["infer"] = [
                "I ran Bayesian inference to estimate parameter distributions.",
                "Generated posterior samples using Monte Carlo methods.",
                "Computed credible intervals and statistical summaries.",
                f"Inference completed in {timings.get('infer', 0):.2f} seconds with {confs.get('infer', 0):.2f} confidence.",
            ]

        result.step_by_step_analysis = step_analysis

    async def _generate_thinking_summary(self, result: ReasoningResult, vignette: str, chain: ReasoningChain):
        """Generate overall thinking process summary"""
        thinking_steps: List[str] = []

        # High-level reasoning approach
        thinking_steps.append("I approached this scenario using a systematic five-stage reasoning pipeline.")

        # Identify key challenges
        if result.overall_confidence < 0.7:
            thinking_steps.append(
                "I encountered some uncertainty in this analysis due to limited information or complex interactions."
            )
        else:
            thinking_steps.append(
                "I was able to analyze this scenario with good confidence given the available information."
            )

        # Describe reasoning strategy
        stage_timings = result.stage_timings or {}
        stages_completed = len([s for s in stage_timings.keys() if stage_timings.get(s, 0) > 0])
        if stages_completed >= 4:
            thinking_steps.append(
                "I completed a comprehensive analysis including knowledge extraction, causal modeling, and probabilistic inference."
            )
        elif stages_completed >= 2:
            thinking_steps.append(
                "I completed the initial analysis stages and extracted key insights from the available information."
            )
        else:
            thinking_steps.append(
                "I began the analysis but encountered limitations that prevented full reasoning completion."
            )

        # Highlight key insights
        if result.dependency_graph and hasattr(result.dependency_graph, "key_insights"):
            thinking_steps.append("The most important insight is understanding how the key factors interact causally.")

        # Decision-making guidance
        if result.inference_result:
            thinking_steps.append(
                "The probabilistic analysis provides quantified guidance for decision-making under uncertainty."
            )

        # Meta-cognitive reflection
        thinking_steps.append(
            "This reasoning process demonstrates how I systematically break down complex scenarios into manageable components."
        )

        result.thinking_process = thinking_steps
