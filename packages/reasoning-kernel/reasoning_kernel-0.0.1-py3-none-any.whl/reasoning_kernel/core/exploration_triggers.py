"""
Exploration Triggers - Core types for thinking exploration framework
==================================================================

Defines exploration trigger types and detection criteria for novel situations,
dynamic environments, and sparse interactions that require adaptive reasoning.
"""

from dataclasses import dataclass
from enum import auto
from enum import Enum
import logging
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)


class ExplorationTrigger(Enum):
    """Types of situations that trigger thinking exploration and adaptive reasoning"""

    NOVEL_SITUATION = auto()  # Completely new scenario not in training data
    DYNAMIC_ENVIRONMENT = auto()  # Rapidly changing conditions requiring adaptation
    SPARSE_INTERACTION = auto()  # Limited data requiring sample-efficient learning
    NEW_VARIABLES = auto()  # Previously unseen variables or features
    COMPLEX_NL_PROBLEM = auto()  # Complex natural language reasoning required
    CAUSAL_UNCERTAINTY = auto()  # Unclear causal relationships requiring exploration
    HYPOTHESIS_CONFLICT = auto()  # Conflicting hypotheses requiring resolution


@dataclass
class TriggerDetectionResult:
    """Result of exploration trigger detection analysis"""

    triggers: List[ExplorationTrigger]
    confidence_scores: Dict[ExplorationTrigger, float]
    novelty_score: float
    complexity_score: float
    sparsity_score: float
    reasoning_required: bool
    exploration_priority: str  # "low", "medium", "high", "critical"
    suggested_strategies: List[str]
    metadata: Dict[str, Any]


@dataclass
class NoveltyDetectionConfig:
    """Configuration for novelty detection algorithms"""

    similarity_threshold: float = 0.3  # Below this threshold = novel
    vocabulary_novelty_weight: float = 0.4
    semantic_novelty_weight: float = 0.6
    context_window_size: int = 512
    embedding_model: str = "gemini-embedding-001"


@dataclass
class DynamicsDetectionConfig:
    """Configuration for dynamic environment detection"""

    temporal_indicators: Optional[List[str]] = None
    change_rate_threshold: float = 0.5
    volatility_window: int = 10
    adaptation_keywords: Optional[List[str]] = None

    def __post_init__(self):
        if self.temporal_indicators is None:
            self.temporal_indicators = [
                "changing",
                "evolving",
                "fluctuating",
                "unprecedented",
                "emerging",
                "shifting",
                "volatile",
                "unpredictable",
            ]

        if self.adaptation_keywords is None:
            self.adaptation_keywords = [
                "adapt",
                "adjust",
                "modify",
                "respond",
                "react",
                "accommodate",
                "flexible",
                "dynamic",
            ]


@dataclass
class SparsityDetectionConfig:
    """Configuration for sparse interaction detection"""

    data_availability_threshold: float = 0.2  # Below this = sparse
    uncertainty_indicators: Optional[List[str]] = None
    limited_data_keywords: Optional[List[str]] = None
    sample_efficiency_keywords: Optional[List[str]] = None

    def __post_init__(self):
        if self.uncertainty_indicators is None:
            self.uncertainty_indicators = [
                "unknown",
                "unclear",
                "uncertain",
                "ambiguous",
                "limited data",
                "sparse",
                "few examples",
                "rare",
            ]

        if self.limited_data_keywords is None:
            self.limited_data_keywords = [
                "limited",
                "sparse",
                "few",
                "rare",
                "insufficient",
                "minimal",
                "scarce",
                "incomplete",
                "partial",
            ]

        if self.sample_efficiency_keywords is None:
            self.sample_efficiency_keywords = [
                "learn quickly",
                "few-shot",
                "one-shot",
                "zero-shot",
                "sample efficient",
                "rapid learning",
                "quick adaptation",
            ]


@dataclass
class ExplorationTriggerConfig:
    """Combined configuration for all exploration trigger detection"""

    novelty_config: NoveltyDetectionConfig
    dynamics_config: DynamicsDetectionConfig
    sparsity_config: SparsityDetectionConfig

    # Global thresholds
    trigger_confidence_threshold: float = 0.6
    exploration_urgency_threshold: float = 0.7
    max_triggers_per_analysis: int = 5

    # Exploration strategy preferences
    preferred_strategies: Optional[Dict[ExplorationTrigger, List[str]]] = None

    def __post_init__(self):
        if self.preferred_strategies is None:
            self.preferred_strategies = {
                ExplorationTrigger.NOVEL_SITUATION: [
                    "ad_hoc_model_synthesis",
                    "analogy_based_reasoning",
                    "pattern_extrapolation",
                ],
                ExplorationTrigger.DYNAMIC_ENVIRONMENT: [
                    "adaptive_learning",
                    "real_time_updating",
                    "temporal_modeling",
                ],
                ExplorationTrigger.SPARSE_INTERACTION: [
                    "sample_efficient_learning",
                    "prior_knowledge_integration",
                    "uncertainty_quantification",
                ],
                ExplorationTrigger.NEW_VARIABLES: [
                    "feature_discovery",
                    "variable_importance_analysis",
                    "dimensional_reduction",
                ],
                ExplorationTrigger.COMPLEX_NL_PROBLEM: [
                    "hierarchical_decomposition",
                    "multi_step_reasoning",
                    "natural_language_understanding",
                ],
                ExplorationTrigger.CAUSAL_UNCERTAINTY: [
                    "causal_discovery",
                    "intervention_planning",
                    "counterfactual_reasoning",
                ],
                ExplorationTrigger.HYPOTHESIS_CONFLICT: [
                    "evidence_evaluation",
                    "hypothesis_testing",
                    "bayesian_model_comparison",
                ],
            }

    @classmethod
    def default(cls) -> "ExplorationTriggerConfig":
        """Create default configuration for exploration trigger detection"""
        return cls(
            novelty_config=NoveltyDetectionConfig(),
            dynamics_config=DynamicsDetectionConfig(),
            sparsity_config=SparsityDetectionConfig(),
        )
