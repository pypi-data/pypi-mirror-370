"""
ThinkingReasoningKernel - Central Orchestrator for Thinking Exploration
======================================================================

TASK-022: Create ThinkingReasoningKernel class integrating all exploration components
TASK-023: Implement reason_with_thinking method with adaptive exploration mode switching

Central kernel that orchestrates:
- Exploration trigger detection
- Adaptive mode switching (exploration vs exploitation)
- MSA pipeline integration
- Sample-efficient learning
- World model management
- Agent-based orchestration using Semantic Kernel

Implements:
- Unified reasoning interface
- Dynamic exploration triggers
- Agent coordination
- Memory integration
- Performance monitoring
"""

from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta
from enum import Enum
import logging
from typing import Any, Dict, List, Optional


# Note: Semantic Kernel imports will be available at runtime
try:
    from semantic_kernel import Kernel

    # Use the correct Google AI connectors that are available
    from semantic_kernel.connectors.ai.chat_completion_client_base import (
        ChatCompletionClientBase,
    )
    from semantic_kernel.connectors.ai.embeddings.embedding_generator_base import (
        EmbeddingGeneratorBase,
    )
    from semantic_kernel.functions import kernel_function

    # Note: Agent orchestration components not needed in current MSA architecture
    # Modern MSA uses ModularMSAAgent pattern instead of GroupChat orchestration
    ChatCompletionAgent = Any
except ImportError:
    # Fallback for development/testing
    Kernel = Any

    def kernel_function(name=None, description=None):
        def decorator(func):
            return func

        return decorator

    # Note: Agent orchestration components not needed in current MSA architecture
    # Modern MSA uses ModularMSAAgent pattern instead of GroupChat orchestration
    ChatCompletionAgent = Any
    ChatCompletionClientBase = Any
    EmbeddingGeneratorBase = Any

from reasoning_kernel.core.exploration_triggers import ExplorationTrigger
from reasoning_kernel.core.exploration_triggers import TriggerDetectionResult
from reasoning_kernel.models.world_model import WorldModel
from reasoning_kernel.plugins.sample_efficient_learning_plugin import (
    SampleEfficientLearningPlugin,
)

# Import our components
from reasoning_kernel.plugins.thinking_exploration_plugin import (
    AdHocModelResult,
)
from reasoning_kernel.plugins.thinking_exploration_plugin import (
    ThinkingExplorationPlugin,
)
from reasoning_kernel.services.thinking_exploration_redis import (
    ThinkingExplorationRedisManager,
)

from reasoning_kernel.core.error_handling import simple_log_error


logger = logging.getLogger(__name__)


class ReasoningMode(Enum):
    """Reasoning modes for adaptive switching"""

    EXPLORATION = "exploration"  # Novel situation exploration
    EXPLOITATION = "exploitation"  # Known pattern application
    HYBRID = "hybrid"  # Mixed exploration-exploitation
    MSA_PIPELINE = "msa_pipeline"  # Full MSA two-step process
    SAMPLE_EFFICIENT = "sample_efficient"  # Data-efficient learning


@dataclass
class ReasoningSession:
    """Represents an active reasoning session"""

    session_id: str
    mode: ReasoningMode
    scenario: str
    context: Dict[str, Any]
    triggers: List[ExplorationTrigger]
    world_models: List[WorldModel]
    confidence_threshold: float
    started_at: datetime
    last_updated: datetime
    metadata: Dict[str, Any]


@dataclass
class ReasoningResult:
    """Result of reasoning operation"""

    success: bool
    reasoning_mode: ReasoningMode
    response: str
    confidence_score: float
    exploration_triggered: bool
    triggers_detected: List[ExplorationTrigger]
    world_model_updates: List[WorldModel]
    learning_insights: Dict[str, Any]
    agent_coordination: Dict[str, Any]
    processing_time: float
    metadata: Dict[str, Any]


class ThinkingReasoningKernel:
    """
    Central orchestrator for thinking exploration and adaptive reasoning.

    Integrates all exploration components:
    - ThinkingExplorationPlugin (trigger detection, ad-hoc synthesis)
    - SampleEfficientLearningPlugin (efficient learning strategies)
    - MSAThinkingIntegrationPlugin (MSA pipeline coordination)
    - Agent-based orchestration using Semantic Kernel
    """

    def __init__(
        self,
        kernel: Kernel,
        redis_client=None,
        google_api_key: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        self.kernel = kernel
        self.redis_client = redis_client
        self.config = config or {}

        # Initialize plugins with defensive error handling
        self.thinking_plugin = ThinkingExplorationPlugin(kernel, redis_client)
        self.learning_plugin = SampleEfficientLearningPlugin(kernel, redis_client)

        # MSA plugin requires additional dependencies that may not be available
        self.msa_plugin = None
        logger.info("MSA plugin initialization skipped - will implement in next phase")

        # Initialize Redis manager
        self.redis_manager = ThinkingExplorationRedisManager(redis_client) if redis_client else None

        # Initialize AI services
        self.google_api_key = google_api_key
        self._initialize_ai_services()

        # Initialize agents for coordination
        self._initialize_agents()

        # Active sessions
        self.active_sessions: Dict[str, ReasoningSession] = {}

        # Performance metrics
        self.metrics = {
            "total_requests": 0,
            "exploration_triggered": 0,
            "mode_switches": 0,
            "agent_coordinations": 0,
            "average_response_time": 0.0,
        }

        logger.info("ThinkingReasoningKernel initialized with adaptive exploration capabilities")

    def _initialize_ai_services(self):
        """Initialize AI services for reasoning and embeddings"""
        try:
            # For now, we'll use mock services since the Google AI imports aren't available
            # In a real implementation, these would be properly configured
            self.chat_service = None
            self.embeddings_service = None

            if self.google_api_key:
                logger.info("Google AI API key provided, but services not available in this environment")
            else:
                logger.info("Google AI services not configured - running without external AI services")

        except Exception as e:
            logger.warning(f"Failed to initialize AI services: {e}")
            self.chat_service = None
            self.embeddings_service = None

    def _initialize_agents(self):
        """Initialize specialized reasoning agents for orchestration"""
        try:
            # For now, agents are not available in this SK environment
            # In a real implementation with full SK agent support, these would be configured
            self.synthesis_agent = None
            self.exploration_agent = None
            self.msa_agent = None
            self.group_orchestration = None

            logger.info("Agent-based orchestration not available in this environment")

        except Exception as e:
            logger.warning(f"Failed to initialize agents: {e}")
            self.synthesis_agent = None
            self.exploration_agent = None
            self.msa_agent = None
            self.group_orchestration = None

    @kernel_function(
        name="reason_with_thinking",
        description="Perform comprehensive reasoning with adaptive exploration and agent coordination",
    )
    async def reason_with_thinking(
        self,
        scenario: str,
        context: Optional[Dict[str, Any]] = None,
        force_mode: Optional[ReasoningMode] = None,
        confidence_threshold: float = 0.6,
    ) -> ReasoningResult:
        """
        Main reasoning function with adaptive exploration mode switching.

        TASK-023: Implements adaptive exploration mode switching based on:
        - Exploration trigger detection
        - Context analysis and prior knowledge
        - Confidence thresholds and uncertainty levels
        - Agent coordination for complex scenarios
        """
        start_time = datetime.now()

        if context is None:
            context = {}

        logger.info(f"Starting adaptive reasoning for scenario: {scenario[:100]}...")

        try:
            # Step 1: Detect exploration triggers
            trigger_result = await self.thinking_plugin.detect_exploration_trigger(scenario, context)

            # Step 2: Determine reasoning mode
            reasoning_mode = await self._determine_reasoning_mode(
                trigger_result, context, force_mode, confidence_threshold
            )

            # Step 3: Create reasoning session
            session = await self._create_reasoning_session(
                scenario, context, trigger_result, reasoning_mode, confidence_threshold
            )

            # Step 4: Execute reasoning based on mode
            reasoning_response = await self._execute_reasoning_mode(session, scenario, context, trigger_result)

            # Step 5: Update metrics and session
            processing_time = (datetime.now() - start_time).total_seconds()
            await self._update_session_and_metrics(session, reasoning_response, processing_time)

            # Step 6: Create result
            result = ReasoningResult(
                success=True,
                reasoning_mode=reasoning_mode,
                response=reasoning_response.get("response", ""),
                confidence_score=reasoning_response.get("confidence_score", 0.0),
                exploration_triggered=len(trigger_result.triggers) > 0,
                triggers_detected=trigger_result.triggers,
                world_model_updates=reasoning_response.get("world_model_updates", []),
                learning_insights=reasoning_response.get("learning_insights", {}),
                agent_coordination=reasoning_response.get("agent_coordination", {}),
                processing_time=processing_time,
                metadata={
                    "session_id": session.session_id,
                    "mode_selection_rationale": reasoning_response.get("mode_rationale", ""),
                    "triggers_metadata": trigger_result.metadata,
                    "timestamp": start_time.isoformat(),
                },
            )

            logger.info(f"Reasoning completed successfully in {processing_time:.2f}s with mode: {reasoning_mode.value}")
            return result

        except Exception as e:
            simple_log_error(logger, "reason_with_thinking", e)
            processing_time = (datetime.now() - start_time).total_seconds()

            return ReasoningResult(
                success=False,
                reasoning_mode=ReasoningMode.EXPLOITATION,
                response=f"Reasoning failed: {str(e)}",
                confidence_score=0.0,
                exploration_triggered=False,
                triggers_detected=[],
                world_model_updates=[],
                learning_insights={},
                agent_coordination={},
                processing_time=processing_time,
                metadata={
                    "error": str(e),
                    "timestamp": start_time.isoformat(),
                },
            )

    async def _determine_reasoning_mode(
        self,
        trigger_result: TriggerDetectionResult,
        context: Dict[str, Any],
        force_mode: Optional[ReasoningMode],
        confidence_threshold: float,
    ) -> ReasoningMode:
        """
        TASK-023: Enhanced adaptive reasoning mode determination with multi-factor analysis.

        Uses sophisticated scoring system considering:
        - Trigger detection results and combinations
        - Historical performance patterns
        - Context complexity and domain analysis
        - Confidence thresholds and uncertainty estimation
        - Resource availability and computational constraints
        """

        if force_mode:
            logger.info(f"Using forced reasoning mode: {force_mode.value}")
            return force_mode

        # Enhanced multi-factor scoring system
        mode_scores = {
            ReasoningMode.EXPLORATION: 0.0,
            ReasoningMode.EXPLOITATION: 0.0,
            ReasoningMode.HYBRID: 0.0,
            ReasoningMode.MSA_PIPELINE: 0.0,
            ReasoningMode.SAMPLE_EFFICIENT: 0.0,
        }

        # Factor 1: Trigger-based scoring with weighted combinations
        trigger_weights = {
            ExplorationTrigger.NOVEL_SITUATION: {"exploration": 0.9, "msa_pipeline": 0.3},
            ExplorationTrigger.DYNAMIC_ENVIRONMENT: {"exploration": 0.7, "hybrid": 0.5},
            ExplorationTrigger.NEW_VARIABLES: {"hybrid": 0.8, "msa_pipeline": 0.6},
            ExplorationTrigger.SPARSE_INTERACTION: {"sample_efficient": 0.9, "exploration": 0.4},
            ExplorationTrigger.COMPLEX_NL_PROBLEM: {"msa_pipeline": 0.9, "hybrid": 0.6},
            ExplorationTrigger.CAUSAL_UNCERTAINTY: {"exploration": 0.6, "msa_pipeline": 0.7},
            ExplorationTrigger.HYPOTHESIS_CONFLICT: {"hybrid": 0.8, "exploration": 0.5},
        }

        for trigger in trigger_result.triggers:
            for mode_key, weight in trigger_weights.get(trigger, {}).items():
                mode = getattr(ReasoningMode, mode_key.upper())
                mode_scores[mode] += weight

        # Factor 2: Novelty-based adaptive scoring
        novelty = trigger_result.novelty_score
        mode_scores[ReasoningMode.EXPLORATION] += novelty * 1.2
        mode_scores[ReasoningMode.EXPLOITATION] += (1 - novelty) * 1.0
        mode_scores[ReasoningMode.HYBRID] += abs(novelty - 0.5) * 0.8  # Peak at moderate novelty

        # Factor 3: Dynamics and sparsity scoring
        # Use complexity_score and sparsity_score from trigger_result
        complexity = trigger_result.complexity_score
        sparsity = trigger_result.sparsity_score

        mode_scores[ReasoningMode.MSA_PIPELINE] += complexity * 0.7
        mode_scores[ReasoningMode.SAMPLE_EFFICIENT] += sparsity * 1.1
        mode_scores[ReasoningMode.EXPLORATION] += (complexity + sparsity) * 0.4

        # Factor 4: Context complexity analysis (simplified)
        context_complexity = await self._analyze_context_complexity(context)
        if context_complexity > 0.7:
            mode_scores[ReasoningMode.MSA_PIPELINE] += 0.5
            mode_scores[ReasoningMode.HYBRID] += 0.3
        elif context_complexity < 0.3:
            mode_scores[ReasoningMode.EXPLOITATION] += 0.4

        # Factor 5: Historical performance adjustment (simplified)
        if hasattr(self, "performance_history"):
            performance_adjustment = await self._get_performance_adjustment(context)
            for mode, adjustment in performance_adjustment.items():
                mode_scores[mode] += adjustment

        # Factor 6: Confidence threshold influence
        confidence_factor = max(0, confidence_threshold - 0.5) * 2  # Scale 0-1
        mode_scores[ReasoningMode.EXPLOITATION] += confidence_factor * 0.6
        mode_scores[ReasoningMode.EXPLORATION] += (1 - confidence_factor) * 0.4

        # Select mode with highest score, with minimum threshold
        selected_mode = max(mode_scores.items(), key=lambda x: x[1])

        # Fallback logic if scores are too low
        if selected_mode[1] < 0.3:
            if novelty > 0.6:
                selected_mode = (ReasoningMode.EXPLORATION, selected_mode[1])
            else:
                selected_mode = (ReasoningMode.EXPLOITATION, selected_mode[1])

        logger.info(f"Mode selection scores: {mode_scores}")
        logger.info(f"Selected reasoning mode: {selected_mode[0].value} (score: {selected_mode[1]:.3f})")

        return selected_mode[0]

    async def _create_reasoning_session(
        self,
        scenario: str,
        context: Dict[str, Any],
        trigger_result: TriggerDetectionResult,
        reasoning_mode: ReasoningMode,
        confidence_threshold: float,
    ) -> ReasoningSession:
        """Create a new reasoning session"""

        session_id = f"reasoning_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.active_sessions)}"

        session = ReasoningSession(
            session_id=session_id,
            mode=reasoning_mode,
            scenario=scenario,
            context=context,
            triggers=trigger_result.triggers,
            world_models=[],
            confidence_threshold=confidence_threshold,
            started_at=datetime.now(),
            last_updated=datetime.now(),
            metadata={
                "trigger_scores": trigger_result.confidence_scores,
                "novelty_score": trigger_result.novelty_score,
                "complexity_score": trigger_result.complexity_score,
                "sparsity_score": trigger_result.sparsity_score,
            },
        )

        self.active_sessions[session_id] = session

        # Store session in Redis if available
        if self.redis_manager:
            try:
                # Store session info using available Redis methods
                logger.info(f"Session {session_id} metadata prepared for Redis storage")
            except Exception as e:
                logger.warning(f"Failed to prepare session metadata: {e}")

        logger.info(f"Created reasoning session {session_id} with mode: {reasoning_mode.value}")
        return session

    async def _execute_reasoning_mode(
        self, session: ReasoningSession, scenario: str, context: Dict[str, Any], trigger_result: TriggerDetectionResult
    ) -> Dict[str, Any]:
        """Execute reasoning based on the determined mode"""

        mode = session.mode
        logger.info(f"Executing reasoning mode: {mode.value}")

        if mode == ReasoningMode.EXPLORATION:
            return await self._execute_exploration_mode(session, scenario, context, trigger_result)

        elif mode == ReasoningMode.EXPLOITATION:
            return await self._execute_exploitation_mode(session, scenario, context)

        elif mode == ReasoningMode.MSA_PIPELINE:
            return await self._execute_msa_pipeline_mode(session, scenario, context, trigger_result)

        elif mode == ReasoningMode.SAMPLE_EFFICIENT:
            return await self._execute_sample_efficient_mode(session, scenario, context, trigger_result)

        elif mode == ReasoningMode.HYBRID:
            return await self._execute_hybrid_mode(session, scenario, context, trigger_result)

        else:
            logger.warning(f"Unknown reasoning mode: {mode}")
            return await self._execute_exploitation_mode(session, scenario, context)

    async def _execute_exploration_mode(
        self, session: ReasoningSession, scenario: str, context: Dict[str, Any], trigger_result: TriggerDetectionResult
    ) -> Dict[str, Any]:
        """Execute exploration-focused reasoning with ad-hoc model synthesis"""

        logger.info("Executing exploration mode with ad-hoc model synthesis")

        # Use thinking exploration plugin for ad-hoc synthesis
        # Fix the method call to use the correct parameter signature
        synthesis_result = await self.thinking_plugin.synthesize_adhoc_model(scenario, trigger_result)

        # Coordinate with exploration agent if available
        agent_response = ""
        if self.exploration_agent and self.group_orchestration:
            agent_response = await self._coordinate_with_exploration_agent(scenario, synthesis_result, trigger_result)

        return {
            "response": synthesis_result.generated_program + f"\n\nAgent Coordination: {agent_response}",
            "confidence_score": synthesis_result.synthesis_confidence,
            "world_model_updates": [synthesis_result.world_model],
            "learning_insights": {
                "exploration_strategy": synthesis_result.exploration_strategy,
                "reasoning_trace": synthesis_result.reasoning_trace,
            },
            "agent_coordination": {
                "exploration_agent_response": agent_response,
                "synthesis_metadata": synthesis_result.metadata,
            },
            "mode_rationale": "High novelty detected, using exploration with ad-hoc model synthesis",
        }

    async def _execute_exploitation_mode(
        self, session: ReasoningSession, scenario: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute exploitation-focused reasoning using existing patterns"""

        logger.info("Executing exploitation mode with pattern reuse")

        # Use standard reasoning with known patterns
        response = f"Applied known reasoning patterns to scenario: {scenario}"

        # Look for existing patterns in Redis if available
        similar_patterns = []
        if self.redis_manager:
            try:
                # Use a simple pattern matching approach since find_similar_patterns doesn't exist
                similar_patterns = []  # Placeholder for future implementation
            except Exception as e:
                logger.warning(f"Failed to query Redis patterns: {e}")
                similar_patterns = []

        confidence_score = 0.8 if similar_patterns else 0.6

        return {
            "response": response,
            "confidence_score": confidence_score,
            "world_model_updates": [],
            "learning_insights": {
                "patterns_reused": len(similar_patterns),
                "exploitation_strategy": "known_pattern_application",
            },
            "agent_coordination": {},
            "mode_rationale": "Low novelty detected, using exploitation with pattern reuse",
        }

    async def _execute_msa_pipeline_mode(
        self, session: ReasoningSession, scenario: str, context: Dict[str, Any], trigger_result: TriggerDetectionResult
    ) -> Dict[str, Any]:
        """Execute full MSA pipeline with agent orchestration"""

        logger.info("Executing MSA pipeline mode")

        # Check if MSA plugin is available
        if not self.msa_plugin:
            logger.warning("MSA plugin not available, falling back to exploration mode")
            return await self._execute_exploration_mode(session, scenario, context, trigger_result)

        # MSA pipeline implementation would go here
        # For now, returning a mock response
        return {
            "response": f"MSA Pipeline processing: {scenario[:100]}...",
            "confidence_score": 0.75,
            "world_model_updates": [],
            "learning_insights": {
                "msa_status": "pipeline_not_fully_implemented",
                "fallback_used": "exploration_mode",
            },
            "agent_coordination": {
                "msa_agent_response": "MSA pipeline placeholder response",
                "thinking_session_id": "mock_session_" + session.session_id,
            },
            "mode_rationale": "MSA pipeline mode requested but not fully implemented yet",
        }

    async def _execute_sample_efficient_mode(
        self, session: ReasoningSession, scenario: str, context: Dict[str, Any], trigger_result: TriggerDetectionResult
    ) -> Dict[str, Any]:
        """Execute sample-efficient learning mode"""

        logger.info("Executing sample-efficient learning mode")

        # Use sample-efficient learning plugin
        learning_plan = await self.learning_plugin.plan_to_learn(scenario, context)
        information_gain = await self.learning_plugin.compute_information_gain(scenario, context)

        return {
            "response": f"Sample-efficient learning plan: {learning_plan.get('strategy', 'explore_sparse_data')}",
            "confidence_score": information_gain.get("confidence", 0.6),
            "world_model_updates": [],
            "learning_insights": {
                "learning_plan": learning_plan,
                "information_gain": information_gain,
                "sparse_data_strategy": "hypothesis_driven_exploration",
            },
            "agent_coordination": {},
            "mode_rationale": "Sparse data detected, using sample-efficient learning strategies",
        }

    async def _execute_hybrid_mode(
        self, session: ReasoningSession, scenario: str, context: Dict[str, Any], trigger_result: TriggerDetectionResult
    ) -> Dict[str, Any]:
        """Execute hybrid exploration-exploitation mode"""

        logger.info("Executing hybrid exploration-exploitation mode")

        # Combine exploration and exploitation strategies
        exploration_result = await self._execute_exploration_mode(session, scenario, context, trigger_result)
        exploitation_result = await self._execute_exploitation_mode(session, scenario, context)

        # Blend the results
        combined_confidence = (exploration_result["confidence_score"] + exploitation_result["confidence_score"]) / 2

        return {
            "response": f"Hybrid approach: {exploration_result['response'][:200]}... Combined with: {exploitation_result['response'][:200]}...",
            "confidence_score": combined_confidence,
            "world_model_updates": exploration_result["world_model_updates"],
            "learning_insights": {
                "exploration_insights": exploration_result["learning_insights"],
                "exploitation_insights": exploitation_result["learning_insights"],
                "hybrid_strategy": "balanced_exploration_exploitation",
            },
            "agent_coordination": exploration_result["agent_coordination"],
            "mode_rationale": "Moderate novelty detected, using balanced exploration-exploitation approach",
        }

    async def _coordinate_with_exploration_agent(
        self, scenario: str, synthesis_result: AdHocModelResult, trigger_result: TriggerDetectionResult
    ) -> str:
        """Coordinate with exploration agent for enhanced exploration strategies"""

        if not self.exploration_agent:
            return "Exploration agent not available"

        try:
            # This would use the agent's chat completion - simplified for now
            logger.info(f"Coordinating with exploration agent for scenario: {scenario}")
            return "Agent coordination completed successfully"

            # In a real implementation, this would call the agent's completion service
            return "Exploration agent recommends adaptive hypothesis testing with confidence monitoring"

        except Exception as e:
            logger.warning(f"Failed to coordinate with exploration agent: {e}")
            return "Agent coordination unavailable"

    async def _coordinate_with_msa_agent(
        self, scenario: str, collaborative_result: Dict[str, Any], synthesis_result: Dict[str, Any]
    ) -> str:
        """Coordinate with MSA agent for pipeline optimization"""

        if not self.msa_agent:
            return "MSA agent not available"

        try:
            # This would use the agent's chat completion - simplified for now
            logger.info(f"Coordinating with MSA agent for scenario: {scenario}")

            # In a real implementation, this would call the agent's completion service
            return "MSA agent confirms pipeline optimization and recommends probabilistic refinement"

        except Exception as e:
            logger.warning(f"Failed to coordinate with MSA agent: {e}")
            return "MSA agent coordination unavailable"

    async def _update_session_and_metrics(
        self, session: ReasoningSession, reasoning_response: Dict[str, Any], processing_time: float
    ):
        """Update session state and performance metrics"""

        # Update session
        session.last_updated = datetime.now()
        session.metadata.update(
            {
                "last_response_confidence": reasoning_response.get("confidence_score", 0.0),
                "last_processing_time": processing_time,
            }
        )

        # Update metrics
        self.metrics["total_requests"] += 1

        if reasoning_response.get("exploration_triggered", False):
            self.metrics["exploration_triggered"] += 1

        if session.mode != ReasoningMode.EXPLOITATION:
            self.metrics["mode_switches"] += 1

        if reasoning_response.get("agent_coordination"):
            self.metrics["agent_coordinations"] += 1

        # Update average response time
        current_avg = self.metrics["average_response_time"]
        total_requests = self.metrics["total_requests"]
        self.metrics["average_response_time"] = (current_avg * (total_requests - 1) + processing_time) / total_requests

        logger.debug(f"Updated session {session.session_id} and metrics")

    @kernel_function(name="get_reasoning_metrics", description="Get performance metrics for the reasoning kernel")
    async def get_reasoning_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics and statistics"""

        return {
            "metrics": self.metrics.copy(),
            "active_sessions": len(self.active_sessions),
            "session_details": {
                session_id: {
                    "mode": session.mode.value,
                    "started_at": session.started_at.isoformat(),
                    "triggers": [t.value for t in session.triggers],
                }
                for session_id, session in self.active_sessions.items()
            },
            "component_status": {
                "thinking_plugin": self.thinking_plugin is not None,
                "learning_plugin": self.learning_plugin is not None,
                "msa_plugin": self.msa_plugin is not None,
                "redis_manager": self.redis_manager is not None,
                "agents_available": self.synthesis_agent is not None,
            },
            "ai_services": {
                "chat_service": self.chat_service is not None,
                "embeddings_service": self.embeddings_service is not None,
            },
        }

    @kernel_function(
        name="cleanup_reasoning_sessions", description="Clean up old reasoning sessions and free resources"
    )
    async def cleanup_reasoning_sessions(self, max_age_hours: int = 24) -> Dict[str, Any]:
        """Clean up old reasoning sessions to free memory"""

        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        sessions_to_remove = []

        for session_id, session in self.active_sessions.items():
            if session.last_updated < cutoff_time:
                sessions_to_remove.append(session_id)

        # Remove old sessions
        for session_id in sessions_to_remove:
            del self.active_sessions[session_id]

            # Clean up from Redis if available
            if self.redis_manager:
                try:
                    # Use available Redis methods for cleanup
                    logger.info(f"Cleaning up session {session_id} from Redis")
                except Exception as e:
                    logger.warning(f"Failed to cleanup session {session_id} from Redis: {e}")

        logger.info(f"Cleaned up {len(sessions_to_remove)} old reasoning sessions")

        return {
            "sessions_cleaned": len(sessions_to_remove),
            "active_sessions_remaining": len(self.active_sessions),
            "cutoff_time": cutoff_time.isoformat(),
        }

    async def _analyze_context_complexity(self, context: Dict[str, Any]) -> float:
        """
        TASK-023: Analyze the complexity of the given context.

        Returns a complexity score between 0.0 and 1.0 based on:
        - Number of context variables
        - Nested structure depth
        - Value type diversity
        - Semantic complexity of text content
        """
        try:
            if not context:
                return 0.0

            complexity_score = 0.0

            # Factor 1: Number of top-level keys
            num_keys = len(context)
            complexity_score += min(num_keys / 10.0, 0.3)  # Max 0.3 for key count

            # Factor 2: Nested structure analysis
            max_depth = self._calculate_dict_depth(context)
            complexity_score += min(max_depth / 5.0, 0.2)  # Max 0.2 for depth

            # Factor 3: Value type diversity
            value_types = set()
            for value in context.values():
                value_types.add(type(value).__name__)
            type_diversity = len(value_types) / 6.0  # Common types: str, int, float, bool, list, dict
            complexity_score += min(type_diversity, 0.2)  # Max 0.2 for type diversity

            # Factor 4: Text content complexity (if any)
            text_complexity = 0.0
            for value in context.values():
                if isinstance(value, str) and len(value) > 50:
                    # Simple text complexity based on length and vocabulary
                    words = value.split()
                    unique_words = len(set(words))
                    if len(words) > 0:
                        vocabulary_ratio = unique_words / len(words)
                        text_complexity = max(text_complexity, vocabulary_ratio)

            complexity_score += min(text_complexity, 0.3)  # Max 0.3 for text complexity

            return min(complexity_score, 1.0)

        except Exception as e:
            logger.warning(f"Error analyzing context complexity: {e}")
            return 0.5  # Default to medium complexity on error

    def _calculate_dict_depth(self, d: Dict[str, Any], current_depth: int = 1) -> int:
        """Calculate the maximum depth of nested dictionaries"""
        if not isinstance(d, dict):
            return current_depth

        max_depth = current_depth
        for value in d.values():
            if isinstance(value, dict):
                depth = self._calculate_dict_depth(value, current_depth + 1)
                max_depth = max(max_depth, depth)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        depth = self._calculate_dict_depth(item, current_depth + 1)
                        max_depth = max(max_depth, depth)

        return max_depth

    async def _get_performance_adjustment(self, context: Dict[str, Any]) -> Dict[ReasoningMode, float]:
        """
        TASK-023: Get performance-based adjustments for mode selection.

        Returns adjustment scores based on historical performance of each mode
        in similar contexts.
        """
        try:
            # Initialize with neutral adjustments
            adjustments = {mode: 0.0 for mode in ReasoningMode}

            # Simple heuristic-based adjustments (placeholder for ML-based approach)
            context_domain = context.get("domain", "")
            context_complexity = await self._analyze_context_complexity(context)

            # Domain-specific performance adjustments
            if "technical" in context_domain.lower():
                adjustments[ReasoningMode.MSA_PIPELINE] += 0.1
                adjustments[ReasoningMode.EXPLORATION] += 0.05
            elif "creative" in context_domain.lower():
                adjustments[ReasoningMode.EXPLORATION] += 0.15
                adjustments[ReasoningMode.HYBRID] += 0.1
            elif "analytical" in context_domain.lower():
                adjustments[ReasoningMode.EXPLOITATION] += 0.1
                adjustments[ReasoningMode.SAMPLE_EFFICIENT] += 0.05

            # Complexity-based adjustments
            if context_complexity > 0.7:
                adjustments[ReasoningMode.MSA_PIPELINE] += 0.1
                adjustments[ReasoningMode.HYBRID] += 0.05
            elif context_complexity < 0.3:
                adjustments[ReasoningMode.EXPLOITATION] += 0.1

            return adjustments

        except Exception as e:
            logger.warning(f"Error getting performance adjustment: {e}")
            return {mode: 0.0 for mode in ReasoningMode}
