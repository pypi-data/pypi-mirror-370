"""
Compatibility wrapper for ThinkingReasoningKernel (legacy agents namespace)
----------------------------------------------------------------------------

This module preserves the legacy import path and types used by tests while
delegating core behavior to `reasoning_kernel.core.thinking_reasoning_kernel`.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from enum import Enum
import logging
from typing import Any, Dict, List, Optional


try:  # optional dependency for types only
    from semantic_kernel import Kernel  # type: ignore
except Exception:

    class Kernel:  # minimal stand-in
        ...


from ..core.exploration_triggers import ExplorationTrigger
from ..models.world_model import WorldModel


logger = logging.getLogger(__name__)


class ReasoningMode(Enum):
    STANDARD = "standard"
    EXPLORATION = "exploration"
    SYNTHESIS = "synthesis"
    EVALUATION = "evaluation"
    HYBRID = "hybrid"


@dataclass
class ThinkingResult:
    scenario: str
    trigger_detected: bool
    trigger_type: Optional[ExplorationTrigger]
    reasoning_mode: ReasoningMode
    world_models: List[WorldModel] = field(default_factory=list)
    synthesis_result: Optional[Dict[str, Any]] = None
    confidence_score: float = 0.0
    execution_time: float = 0.0
    memory_operations: List[str] = field(default_factory=list)
    agent_interactions: List[Dict[str, Any]] = field(default_factory=list)
    error_details: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scenario": self.scenario,
            "trigger_detected": self.trigger_detected,
            "trigger_type": self.trigger_type.value if self.trigger_type else None,
            "reasoning_mode": self.reasoning_mode.value,
            "world_models": [getattr(m, "to_dict", lambda: m)() for m in self.world_models],
            "synthesis_result": self.synthesis_result,
            "confidence_score": self.confidence_score,
            "execution_time": self.execution_time,
            "memory_operations": self.memory_operations,
            "agent_interactions": self.agent_interactions,
            "error_details": self.error_details,
        }


class ModelSynthesisAgent:
    def __init__(self, kernel: Kernel):
        self.kernel = kernel

    async def analyze_problem_structure(self, problem_description: str, domain_context: str = "") -> Dict[str, Any]:
        analysis = {
            "problem_type": "open_world_reasoning",
            "complexity_level": "high",
            "domain": domain_context or "general",
            "key_variables": [],
            "constraints": [],
            "uncertainty_factors": [],
            "reasoning_approach": "hierarchical_synthesis",
        }
        text = problem_description.lower()
        if "novel" in text or "new" in text:
            analysis["exploration_required"] = True
            analysis["novelty_score"] = 0.8
        if "uncertain" in text or "unknown" in text:
            analysis["uncertainty_level"] = "high"
        return analysis

    async def synthesize_reasoning_model(
        self, problem_analysis: Dict[str, Any], background_knowledge: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        model = {
            "model_type": "hierarchical_world_model",
            "synthesis_approach": "msa_based",
            "model_structure": {
                "variables": problem_analysis.get("key_variables", []),
                "relationships": [],
                "priors": {},
                "likelihood": {},
            },
            "execution_ready": True,
            "confidence": 0.85,
        }
        if background_knowledge:
            model["background_knowledge_used"] = True
        return model


class ProbabilisticReasoningAgent:
    def __init__(self, kernel: Kernel, sandbox_client: Any = None):
        self.kernel = kernel
        self.sandbox_client = sandbox_client


class EvaluationAgent:
    def __init__(self, kernel: Kernel):
        self.kernel = kernel


class KnowledgeRetrievalAgent:
    def __init__(self, kernel: Kernel):
        self.kernel = kernel


# Placeholders so tests can patch these symbols on this module path
class ThinkingExplorationPlugin:  # pragma: no cover - patched in tests
    pass


class HierarchicalWorldModelManager:  # pragma: no cover - patched in tests
    pass


class SampleEfficientLearningPlugin:  # pragma: no cover - patched in tests
    pass


class ThinkingReasoningKernel:
    """Thin wrapper delegating to the canonical core implementation."""

    def __init__(
        self,
        kernel: Kernel,
        memory_store: Optional[Any] = None,
        sandbox_client: Optional[Any] = None,
        cache_config: Optional[Dict[str, Any]] = None,
        **_: Any,
    ) -> None:
        self.kernel = kernel
        self.memory_store = memory_store
        self.sandbox_client = sandbox_client

        # Attributes referenced by tests
        self.result_cache: Dict[str, Any] = {}
        self.model_cache: Dict[str, Any] = {}
        self.agents = [
            ModelSynthesisAgent(kernel),
            ProbabilisticReasoningAgent(kernel, sandbox_client),
            EvaluationAgent(kernel),
            KnowledgeRetrievalAgent(kernel),
        ]

        # Lazy import to avoid importing heavy core dependencies during simple type-only imports
        from reasoning_kernel.core.thinking_reasoning_kernel import (
            ThinkingReasoningKernel as CoreThinkingReasoningKernel,
        )

        self._core = CoreThinkingReasoningKernel(kernel=kernel, redis_client=memory_store, config=cache_config or {})

        logger.info("ThinkingReasoningKernel (agents wrapper) initialized using core implementation")

    async def reason_with_thinking(
        self,
        scenario: str,
        domain_context: str = "",
        reasoning_mode: ReasoningMode = ReasoningMode.HYBRID,
        enable_caching: bool = True,
    ) -> Any:
        context = {"domain": domain_context} if domain_context else {}
        return await self._core.reason_with_thinking(
            scenario=scenario, context=context, force_mode=None, confidence_threshold=0.6
        )

    # Back-compat helper used by tests
    def _determine_reasoning_mode(
        self, trigger_type: Optional[ExplorationTrigger], requested_mode: ReasoningMode
    ) -> ReasoningMode:
        if requested_mode != ReasoningMode.HYBRID:
            return requested_mode
        if trigger_type == ExplorationTrigger.NOVEL_SITUATION:
            return ReasoningMode.EXPLORATION
        if trigger_type == ExplorationTrigger.DYNAMIC_ENVIRONMENT:
            return ReasoningMode.SYNTHESIS
        if trigger_type == ExplorationTrigger.SPARSE_INTERACTION:
            return ReasoningMode.EVALUATION
        return ReasoningMode.STANDARD
