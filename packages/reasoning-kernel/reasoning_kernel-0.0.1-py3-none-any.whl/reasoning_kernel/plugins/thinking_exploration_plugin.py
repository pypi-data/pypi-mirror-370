"""
ThinkingExplorationPlugin - Advanced Thinking Exploration Framework
==================================================================

Core plugin for MSA-based thinking exploration with on-demand synthesis
of bespoke probabilistic mental models for novel situations.

Implements:
- Exploration trigger detection (TASK-001, TASK-004)
- Ad-hoc model synthesis (TASK-005)
- Integration with Semantic Kernel agent patterns
"""

from dataclasses import dataclass
import logging
import re
from typing import Any, Dict, List, Optional, Tuple

from ..utils.datetime_utils import utc_now


# Note: Semantic Kernel imports will be available at runtime
try:
    from semantic_kernel import Kernel
    from semantic_kernel.connectors.ai.google.google_ai import (
        GoogleAITextEmbedding,
    )
    from semantic_kernel.functions import kernel_function
except ImportError:
    # Fallback for development/testing
    Kernel = type("Kernel", (), {})  # Create a dummy class instead of using Any

    def kernel_function(func=None, name=None, description=None):
        def decorator(f):
            return f

        if func is not None:
            return decorator(func)
        return decorator

    GoogleAITextEmbedding = None  # Use None for fallback

from reasoning_kernel.core.exploration_triggers import ExplorationTrigger
from reasoning_kernel.core.exploration_triggers import ExplorationTriggerConfig
from reasoning_kernel.core.exploration_triggers import TriggerDetectionResult
from reasoning_kernel.models.world_model import BayesianPrior
from reasoning_kernel.models.world_model import ModelType
from reasoning_kernel.models.world_model import WorldModel
from reasoning_kernel.models.world_model import WorldModelLevel


logger = logging.getLogger(__name__)


@dataclass
class AdHocModelResult:
    """Result of ad-hoc model synthesis"""

    world_model: WorldModel
    synthesis_confidence: float
    reasoning_trace: List[str]
    generated_program: str
    validation_result: Dict[str, Any]
    exploration_strategy: str
    metadata: Dict[str, Any]


@dataclass
class ThinkingExplorationContext:
    """Context for thinking exploration analysis"""

    input_text: str
    domain: str = "general"
    user_context: Optional[Dict[str, Any]] = None
    prior_knowledge: Optional[List[str]] = None
    confidence_threshold: float = 0.6
    max_synthesis_attempts: int = 3

    def __post_init__(self):
        if self.user_context is None:
            self.user_context = {}
        if self.prior_knowledge is None:
            self.prior_knowledge = []


class ThinkingExplorationPlugin:
    """
    Core plugin for advanced thinking exploration and adaptive reasoning.

    Detects when novel situations require exploration and synthesizes
    bespoke mental models using the MSA framework approach.
    """

    def __init__(self, kernel, redis_client=None, config: Optional[ExplorationTriggerConfig] = None):
        self.kernel = kernel
        self.redis_client = redis_client
        self.config = config or ExplorationTriggerConfig.default()
        self.embeddings_service = None
        self._initialize_ai_services()

        # Trigger detection patterns
        self._novelty_patterns = self._compile_novelty_patterns()
        self._dynamics_patterns = self._compile_dynamics_patterns()
        self._sparsity_patterns = self._compile_sparsity_patterns()

        logger.info("ThinkingExplorationPlugin initialized with MSA framework")

    def _initialize_ai_services(self):
        """Initialize Google AI services for embeddings and synthesis"""
        try:
            # Check if GoogleAITextEmbedding is available (not None from fallback)
            if GoogleAITextEmbedding is not None:
                self.embeddings_service = GoogleAITextEmbedding(
                    model_id="models/embedding-001",  # Fix: Use 'model_id' instead of 'ai_model_id'
                    api_key=None,  # Will be loaded from environment/config
                )
                logger.info("Google AI embedding service initialized")
            else:
                logger.info("Google AI services not available, using fallback")
                self.embeddings_service = None
        except Exception as e:
            logger.warning(
                f"Failed to initialize embedding service: {e}. "
                "Embedding-based model synthesis and advanced exploration features will be unavailable."
            )
            self.embeddings_service = None

    def _compile_novelty_patterns(self) -> List[re.Pattern]:
        """Compile regex patterns for novelty detection"""
        novelty_indicators = [
            r"\b(never\s+seen|unprecedented|unknown|novel|new|unfamiliar)\b",
            r"\b(first\s+time|never\s+before|never\s+encountered|never\s+documented)\b",
            r"\b(mysterious|unexplained|puzzling|baffling)\b",
            r"\b(strange|weird|odd|peculiar|unusual)\b",
            r"\b(breakthrough|revolutionary|paradigm|game[_\s]chang(?:ing|er))\b",
            r"\b(completely\s+(?:novel|new|unknown|unprecedented))\b",
        ]
        return [re.compile(pattern, re.IGNORECASE) for pattern in novelty_indicators]

    def _compile_dynamics_patterns(self) -> List[re.Pattern]:
        """Compile regex patterns for dynamics detection"""
        temporal_indicators = self.config.dynamics_config.temporal_indicators or []
        dynamics_indicators = temporal_indicators + [
            r"\b(rapid(?:ly)?|quick(?:ly)?|fast|sudden(?:ly)?)\b",
            r"\b(real[_\s]time|live|ongoing|continuous(?:ly)?)\b",
            r"\b(evolv(?:ing|es|ed)|chang(?:ing|es|ed)|shift(?:ing|s|ed))\b",
            r"\b(volatile|unstable|fluctuat(?:ing|es|ed))\b",
        ]
        return [re.compile(pattern, re.IGNORECASE) for pattern in dynamics_indicators]

    def _compile_sparsity_patterns(self) -> List[re.Pattern]:
        """Compile regex patterns for sparsity detection"""
        uncertainty_indicators = self.config.sparsity_config.uncertainty_indicators or []
        sparsity_indicators = uncertainty_indicators + [
            r"\b(limited\s+(?:data|information|evidence))\b",
            r"\b(few\s+(?:examples|cases|instances))\b",
            r"\b(sparse|scarce|insufficient|minimal)\b",
            r"\b(uncertain|unclear|ambiguous|unknown)\b",
        ]
        return [re.compile(pattern, re.IGNORECASE) for pattern in sparsity_indicators]

    @kernel_function(
        name="detect_exploration_trigger",
        description="Detect situations requiring thinking exploration and adaptive reasoning",
    )
    async def detect_exploration_trigger(
        self, input_text: str, context: Optional[Dict[str, Any]] = None
    ) -> TriggerDetectionResult:
        """
        Core function to detect exploration triggers for novel situations.

        TASK-004: Implement detect_exploration_trigger kernel function with
        novelty, dynamics, and sparsity assessment.
        """
        if context is None:
            context = {}

        logger.info(f"Analyzing text for exploration triggers: {input_text[:100]}...")

        # Initialize scores
        trigger_scores = {trigger: 0.0 for trigger in ExplorationTrigger}
        detected_triggers = []

        # Novelty detection
        novelty_score = await self._detect_novelty(input_text, context)
        if novelty_score > self.config.trigger_confidence_threshold:
            trigger_scores[ExplorationTrigger.NOVEL_SITUATION] = novelty_score
            detected_triggers.append(ExplorationTrigger.NOVEL_SITUATION)

        # Dynamics detection
        dynamics_score = await self._detect_dynamics(input_text, context)
        if dynamics_score > self.config.trigger_confidence_threshold:
            trigger_scores[ExplorationTrigger.DYNAMIC_ENVIRONMENT] = dynamics_score
            detected_triggers.append(ExplorationTrigger.DYNAMIC_ENVIRONMENT)

        # Sparsity detection
        sparsity_score = await self._detect_sparsity(input_text, context)
        if sparsity_score > self.config.trigger_confidence_threshold:
            trigger_scores[ExplorationTrigger.SPARSE_INTERACTION] = sparsity_score
            detected_triggers.append(ExplorationTrigger.SPARSE_INTERACTION)

        # Additional trigger detection
        new_variables_score = await self._detect_new_variables(input_text, context)
        if new_variables_score > self.config.trigger_confidence_threshold:
            trigger_scores[ExplorationTrigger.NEW_VARIABLES] = new_variables_score
            detected_triggers.append(ExplorationTrigger.NEW_VARIABLES)

        complex_nl_score = await self._detect_complex_reasoning(input_text, context)
        if complex_nl_score > self.config.trigger_confidence_threshold:
            trigger_scores[ExplorationTrigger.COMPLEX_NL_PROBLEM] = complex_nl_score
            detected_triggers.append(ExplorationTrigger.COMPLEX_NL_PROBLEM)

        # Determine exploration priority
        max_score = max(trigger_scores.values()) if trigger_scores.values() else 0.0
        priority = self._determine_priority(max_score, len(detected_triggers))

        # Get suggested strategies
        strategies = self._get_exploration_strategies(detected_triggers)

        result = TriggerDetectionResult(
            triggers=detected_triggers,
            confidence_scores=trigger_scores,
            novelty_score=novelty_score,
            complexity_score=complex_nl_score,
            sparsity_score=sparsity_score,
            reasoning_required=len(detected_triggers) > 0,
            exploration_priority=priority,
            suggested_strategies=strategies,
            metadata={
                "analysis_timestamp": utc_now().isoformat(),
                "input_length": len(input_text),
                "context_provided": bool(context),
                "trigger_count": len(detected_triggers),
            },
        )

        logger.info(f"Exploration trigger detection completed: {len(detected_triggers)} triggers, priority: {priority}")
        return result

    async def _detect_novelty(self, text: str, context: Dict[str, Any]) -> float:
        """Detect novelty in the input using pattern matching and embeddings"""
        # Pattern-based detection with improved scoring
        pattern_score = 0.0
        matched_patterns = 0

        for pattern in self._novelty_patterns:
            matches = pattern.findall(text)
            if matches:
                matched_patterns += 1
                pattern_score += len(matches) * 0.3  # Increased weight

        # Boost score for multiple pattern matches
        if matched_patterns >= 2:
            pattern_score *= 1.2  # 20% bonus for multiple novelty indicators

        pattern_score = min(1.0, pattern_score)

        # Context-based novelty assessment
        domain_novelty = 0.5  # Default
        if "domain" in context:
            known_domains = ["medical", "financial", "legal", "scientific", "technical"]
            if context["domain"] not in known_domains:
                domain_novelty = 0.8

        # Combine scores with higher weight on patterns
        novelty_score = (pattern_score * 0.8) + (domain_novelty * 0.2)
        return min(1.0, novelty_score)

    async def _detect_dynamics(self, text: str, context: Dict[str, Any]) -> float:
        """Detect dynamic/changing environment indicators"""
        pattern_score = 0.0
        matched_patterns = 0

        for pattern in self._dynamics_patterns:
            matches = pattern.findall(text)
            if matches:
                matched_patterns += 1
                pattern_score += len(matches) * 0.25  # Increased weight

        # Look for temporal language
        temporal_words = ["changing", "evolving", "shifting", "fluctuating", "adapting", "rapidly"]
        temporal_matches = 0
        for word in temporal_words:
            if word in text.lower():
                temporal_matches += 1
                pattern_score += 0.2

        # Boost for multiple temporal indicators
        if temporal_matches >= 2:
            pattern_score *= 1.1  # 10% bonus for multiple dynamics indicators

        return min(1.0, pattern_score)

    async def _detect_sparsity(self, text: str, context: Dict[str, Any]) -> float:
        """Detect sparse data/interaction indicators"""
        pattern_score = 0.0
        matched_patterns = 0

        for pattern in self._sparsity_patterns:
            matches = pattern.findall(text)
            if matches:
                matched_patterns += 1
                pattern_score += len(matches) * 0.3  # Increased weight

        # Check for uncertainty language
        uncertainty_words = ["unknown", "unclear", "limited", "sparse", "few", "insufficient", "minimal"]
        uncertainty_matches = 0
        for word in uncertainty_words:
            if word in text.lower():
                uncertainty_matches += 1
                pattern_score += 0.2

        # Boost for multiple sparsity indicators
        if uncertainty_matches >= 2:
            pattern_score *= 1.1  # 10% bonus for multiple sparsity indicators

        return min(1.0, pattern_score)

    async def _detect_new_variables(self, text: str, context: Dict[str, Any]) -> float:
        """Detect new/unknown variables or features"""
        new_var_indicators = [
            "new variable",
            "unknown factor",
            "novel feature",
            "unprecedented element",
            "unidentified",
            "mysterious",
        ]

        score = 0.0
        for indicator in new_var_indicators:
            if indicator in text.lower():
                score += 0.3

        return min(1.0, score)

    async def _detect_complex_reasoning(self, text: str, context: Dict[str, Any]) -> float:
        """Detect complex natural language reasoning requirements"""
        complexity_indicators = [
            "complex",
            "complicated",
            "intricate",
            "sophisticated",
            "multi-step",
            "hierarchical",
            "interdependent",
            "nuanced",
        ]

        score = 0.0
        word_count = len(text.split())

        # Length-based complexity
        if word_count > 100:
            score += 0.3
        if word_count > 200:
            score += 0.2

        # Pattern-based complexity
        for indicator in complexity_indicators:
            if indicator in text.lower():
                score += 0.2

        return min(1.0, score)

    def _determine_priority(self, max_score: float, trigger_count: int) -> str:
        """Determine exploration priority based on scores and trigger count"""
        if max_score >= 0.9 or trigger_count >= 4:
            return "critical"
        elif max_score >= 0.7 or trigger_count >= 2:
            return "high"
        elif max_score >= 0.5 or trigger_count >= 1:
            return "medium"
        else:
            return "low"

    def _get_exploration_strategies(self, triggers: List[ExplorationTrigger]) -> List[str]:
        """Get suggested exploration strategies for detected triggers"""
        strategies = set()

        if self.config.preferred_strategies:
            for trigger in triggers:
                if trigger in self.config.preferred_strategies:
                    strategies.update(self.config.preferred_strategies[trigger])

        return list(strategies)

    @kernel_function(
        name="synthesize_adhoc_model", description="Synthesize ad-hoc world model for novel reasoning situations"
    )
    async def synthesize_adhoc_model(
        self, scenario: str, trigger_context: TriggerDetectionResult, domain: str = "general"
    ) -> AdHocModelResult:
        """
        Synthesize bespoke probabilistic mental model for the given scenario.

        TASK-005: Implement basic ad-hoc model synthesis using Gemini 2.5 Pro
        with thinking modes enabled for reasoning model generation.
        """
        logger.info(f"Synthesizing ad-hoc model for scenario in domain: {domain}")

        # Create base world model
        world_model = WorldModel(
            model_level=WorldModelLevel.INSTANCE,
            model_type=ModelType.PROBABILISTIC,
            domain=domain,
            context_description=scenario[:500],  # Truncate for storage
            applicable_situations=[scenario],
            tags=["adhoc", "synthesized", domain],
        )

        # Set up priors based on trigger context
        self._configure_model_priors(world_model, trigger_context)

        # Generate PPL program structure (simplified for now)
        program_structure = await self._generate_program_structure(scenario, trigger_context)
        world_model.structure = program_structure

        # Calculate synthesis confidence
        synthesis_confidence = self._calculate_synthesis_confidence(trigger_context, program_structure)
        world_model.confidence_score = synthesis_confidence

        # Create reasoning trace
        reasoning_trace = [
            f"Detected triggers: {[t.name for t in trigger_context.triggers]}",
            f"Domain: {domain}",
            f"Scenario complexity: {trigger_context.complexity_score:.2f}",
            "Model synthesis approach: probabilistic programming",
            f"Confidence: {synthesis_confidence:.2f}",
        ]

        # Generate simplified PPL program
        generated_program = self._generate_simple_ppl_program(scenario, program_structure)

        # Validate program structure
        validation_result = await self._validate_program_structure(generated_program)

        # Store in Redis if available
        if self.redis_client:
            await self._store_world_model(world_model)

        result = AdHocModelResult(
            world_model=world_model,
            synthesis_confidence=synthesis_confidence,
            reasoning_trace=reasoning_trace,
            generated_program=generated_program,
            validation_result=validation_result,
            exploration_strategy=(
                trigger_context.suggested_strategies[0] if trigger_context.suggested_strategies else "default"
            ),
            metadata={
                "synthesis_timestamp": utc_now().isoformat(),
                "trigger_priority": trigger_context.exploration_priority,
                "scenario_length": len(scenario),
            },
        )

        logger.info(f"Ad-hoc model synthesis completed with confidence: {synthesis_confidence:.2f}")
        return result

    def _configure_model_priors(self, model: WorldModel, trigger_context: TriggerDetectionResult):
        """Configure Bayesian priors based on trigger context"""
        # Set priors based on novelty
        if ExplorationTrigger.NOVEL_SITUATION in trigger_context.triggers:
            model.priors["novelty_factor"] = BayesianPrior(
                distribution_type="beta",
                parameters={"alpha": 2, "beta": 5},
                confidence=trigger_context.novelty_score,
                source="novelty_detection",
            )

        # Set priors based on dynamics
        if ExplorationTrigger.DYNAMIC_ENVIRONMENT in trigger_context.triggers:
            model.priors["adaptation_rate"] = BayesianPrior(
                distribution_type="gamma",
                parameters={"shape": 2, "rate": 1},
                confidence=0.7,
                source="dynamics_detection",
            )

        # Set priors based on sparsity
        if ExplorationTrigger.SPARSE_INTERACTION in trigger_context.triggers:
            model.priors["uncertainty"] = BayesianPrior(
                distribution_type="normal",
                parameters={"mu": 0.5, "sigma": 0.2},
                confidence=trigger_context.sparsity_score,
                source="sparsity_detection",
            )

    async def _generate_program_structure(
        self, scenario: str, trigger_context: TriggerDetectionResult
    ) -> Dict[str, Any]:
        """Generate probabilistic program structure"""
        # Simplified structure generation
        variables = self._extract_variables(scenario)
        dependencies = self._identify_dependencies(variables, scenario)

        structure = {
            "variables": variables,
            "dependencies": dependencies,
            "distributions": {var: "normal" for var in variables},  # Default to normal
            "observations": [],
            "queries": ["prediction", "explanation"],
        }

        return structure

    def _extract_variables(self, scenario: str) -> List[str]:
        """Extract potential variables from scenario"""
        # Simple variable extraction based on nouns and technical terms
        import re

        # Extract capitalized words and technical terms
        words = re.findall(r"\b[A-Z][a-z]+\b|\b[a-z]+(?:_[a-z]+)*\b", scenario)

        # Filter for likely variables
        likely_variables = []
        for word in words:
            if len(word) > 3 and word.lower() not in ["this", "that", "they", "them", "with", "from"]:
                likely_variables.append(word.lower())

        # Return unique variables (max 10)
        return list(set(likely_variables))[:10]

    def _identify_dependencies(self, variables: List[str], scenario: str) -> List[Tuple[str, str]]:
        """Identify potential dependencies between variables"""
        dependencies = []

        # Simple dependency detection based on proximity and causal language
        causal_words = ["causes", "leads to", "results in", "affects", "influences"]

        for i, var1 in enumerate(variables):
            for j, var2 in enumerate(variables):
                if i != j:
                    # Check if variables appear near causal language
                    for causal in causal_words:
                        if f"{var1} {causal} {var2}" in scenario.lower():
                            dependencies.append((var1, var2))

        return dependencies

    def _calculate_synthesis_confidence(
        self, trigger_context: TriggerDetectionResult, structure: Dict[str, Any]
    ) -> float:
        """Calculate confidence in the synthesized model"""
        base_confidence = 0.6

        # Adjust based on trigger strength
        max_trigger_score = (
            max(trigger_context.confidence_scores.values()) if trigger_context.confidence_scores else 0.5
        )
        trigger_adjustment = max_trigger_score * 0.3

        # Adjust based on structure complexity
        structure_complexity = len(structure.get("variables", [])) + len(structure.get("dependencies", []))
        complexity_adjustment = min(0.2, structure_complexity * 0.02)

        confidence = base_confidence + trigger_adjustment - complexity_adjustment
        return max(0.1, min(1.0, confidence))

    def _generate_simple_ppl_program(self, scenario: str, structure: Dict[str, Any]) -> str:
        """Generate a simple probabilistic program"""
        variables = structure.get("variables", [])

        program_lines = [
            "# Generated probabilistic program for adaptive reasoning",
            "import numpy as np",
            "from numpyro import sample, distributions as dist",
            "",
            "def reasoning_model():",
            "    # Scenario: " + scenario[:100] + "...",
            "",
        ]

        # Add variable definitions
        for var in variables[:5]:  # Limit to 5 variables
            program_lines.append(f"    {var} = sample('{var}', dist.Normal(0, 1))")

        program_lines.extend(
            ["", "    # Return main variables", f"    return {', '.join(variables[:3]) if variables else 'prediction'}"]
        )

        return "\n".join(program_lines)

    async def _validate_program_structure(self, program: str) -> Dict[str, Any]:
        """Validate the generated program structure"""
        validation_result = {"is_valid": True, "syntax_errors": [], "warnings": [], "score": 0.8}

        # Basic syntax validation
        try:
            compile(program, "<string>", "exec")
            validation_result["score"] = 0.9
        except SyntaxError as e:
            validation_result["is_valid"] = False
            validation_result["syntax_errors"].append(str(e))
            validation_result["score"] = 0.3

        return validation_result

    async def _store_world_model(self, model: WorldModel):
        """Store world model in Redis"""
        if not self.redis_client:
            return

        try:
            # Store model data
            model_data = model.to_json()
            await self.redis_client.setex(model.storage_key, model.ttl_seconds or 3600, model_data)

            # Store in exploration index
            await self.redis_client.sadd("thinking_exploration:models", model.model_id)

            logger.info(f"Stored world model {model.model_id} in Redis")
        except Exception as e:
            logger.error(f"Failed to store world model: {e}")

    @kernel_function(name="reason_with_thinking", description="Perform reasoning with thinking exploration when needed")
    async def reason_with_thinking(
        self, scenario: str, mode: str = "adaptive", domain: str = "general"
    ) -> Dict[str, Any]:
        """
        Main reasoning function that combines trigger detection and model synthesis.

        This is the high-level interface for thinking exploration reasoning.
        """
        logger.info(f"Starting thinking exploration reasoning in {mode} mode")

        # Step 1: Detect exploration triggers
        trigger_result = await self.detect_exploration_trigger(scenario, {"domain": domain, "mode": mode})

        # Step 2: Decide if exploration is needed
        if not trigger_result.reasoning_required:
            return {
                "reasoning_type": "standard",
                "result": "No exploration triggers detected - using standard reasoning",
                "confidence": 0.8,
                "trigger_analysis": trigger_result,
            }

        # Step 3: Synthesize ad-hoc model
        synthesis_result = await self.synthesize_adhoc_model(scenario, trigger_result, domain)

        # Step 4: Return comprehensive result
        return {
            "reasoning_type": "thinking_exploration",
            "world_model": synthesis_result.world_model.to_dict(),
            "inference_result": {
                "program": synthesis_result.generated_program,
                "confidence": synthesis_result.synthesis_confidence,
                "reasoning_trace": synthesis_result.reasoning_trace,
            },
            "trigger_analysis": trigger_result,
            "exploration_strategy": synthesis_result.exploration_strategy,
            "metadata": synthesis_result.metadata,
        }
