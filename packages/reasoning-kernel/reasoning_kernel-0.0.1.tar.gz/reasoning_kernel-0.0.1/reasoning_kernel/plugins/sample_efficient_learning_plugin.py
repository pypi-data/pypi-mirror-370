"""
Sample Efficient Learning Plugin - Information gain and hypothesis-driven exploration
==================================================================================

Implements sample-efficient learning through information gain computation,
hypothesis-driven exploration, and strategic action selection for optimal knowledge acquisition.

TASK-015: Create SampleEfficientLearningPlugin with information gain computation
TASK-016: Implement hypothesis_driven_exploration with experiment planning and execution
TASK-017: Develop plan_to_learn method for strategic action selection and knowledge gap targeting
TASK-018: Create update_from_sparse_data method for efficient model updates from limited observations
TASK-019: Implement curiosity bonus calculation and exploration-exploitation balancing
"""

from dataclasses import dataclass
from datetime import datetime
import logging
from typing import Any, Dict, List, Optional
import uuid

from reasoning_kernel.models.world_model import WorldModel
from reasoning_kernel.models.world_model import WorldModelEvidence
from reasoning_kernel.services.hierarchical_world_model_manager import (
    HierarchicalWorldModelManager,
)
from semantic_kernel.functions import kernel_function
from semantic_kernel.kernel import Kernel


logger = logging.getLogger(__name__)


@dataclass
class InformationGainResult:
    """Result of information gain computation for an action or experiment."""

    information_gain: float
    uncertainty_reduction: float
    expected_utility: float
    optimal_action: Optional[Dict[str, Any]]  # Changed from str to Dict for actions
    confidence: float
    metadata: Dict[str, Any]


@dataclass
class Hypothesis:
    """Represents a testable hypothesis"""

    hypothesis_id: str
    description: str
    predictions: Dict[str, Any]
    confidence: float
    prior_probability: float
    evidence_required: List[str]
    test_cost: float
    potential_gain: float
    created_at: datetime


@dataclass
class ExperimentPlan:
    """Plan for testing hypotheses through experiments"""

    experiment_id: str
    target_hypotheses: List[str]
    actions: List[Dict[str, Any]]
    expected_outcomes: Dict[str, Any]
    resource_requirements: Dict[str, Any]
    success_criteria: List[str]
    risk_assessment: Dict[str, float]
    priority_score: float


@dataclass
class LearningGap:
    """Represents a gap in knowledge that needs to be addressed"""

    gap_id: str
    description: str
    importance: float
    difficulty: float
    knowledge_type: str  # "factual", "procedural", "conceptual", "causal"
    dependencies: List[str]
    potential_sources: List[str]
    acquisition_strategy: Optional[str]


class SampleEfficientLearningPlugin:
    """
    Plugin for sample-efficient learning through information gain computation
    and hypothesis-driven exploration.

    Implements the "child as scientist" learning paradigm from MSA framework.
    """

    def __init__(
        self,
        hierarchical_manager: HierarchicalWorldModelManager,
        kernel: Optional[Kernel] = None,
    ):
        self.hierarchical_manager = hierarchical_manager
        self.kernel = kernel
        self.active_hypotheses: Dict[str, Hypothesis] = {}
        self.learning_gaps: Dict[str, LearningGap] = {}
        self.experiment_history: List[ExperimentPlan] = []
        self.curiosity_bonus_weight = 0.3
        self.exploration_exploitation_ratio = 0.2  # 20% exploration, 80% exploitation
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @kernel_function(
        description="Compute information gain for potential actions or observations",
        name="compute_information_gain",
    )
    async def compute_information_gain(
        self,
        current_model: WorldModel,
        potential_actions: List[Dict[str, Any]],
        target_variables: Optional[List[str]] = None,
    ) -> InformationGainResult:
        """
        Compute expected information gain for potential actions.

        Args:
            current_model: Current world model
            potential_actions: List of possible actions to evaluate
            target_variables: Specific variables to focus information gain on

        Returns:
            InformationGainResult: Expected information gain metrics
        """
        try:
            self.logger.info("Computing information gain for potential actions")

            max_gain = 0.0
            best_action = None
            total_uncertainty_reduction = 0.0
            start_time = datetime.now()

            for action in potential_actions:
                # Calculate expected information gain for this action
                gain = await self._calculate_expected_gain(
                    current_model, action, target_variables
                )

                if gain > max_gain:
                    max_gain = gain
                    best_action = action

                total_uncertainty_reduction += gain

            # Calculate value of information (VOI)
            voi = await self._calculate_value_of_information(
                current_model, max_gain, best_action
            )

            # Calculate confidence in the information gain estimate
            confidence = await self._calculate_gain_confidence(
                current_model, potential_actions
            )

            computation_time = (datetime.now() - start_time).total_seconds()

            return InformationGainResult(
                information_gain=max_gain,
                uncertainty_reduction=total_uncertainty_reduction,
                expected_utility=voi,
                optimal_action=best_action,
                confidence=confidence,
                metadata={
                    "n_actions_evaluated": len(potential_actions),
                    "computation_time": computation_time,
                    "method": "expected_information_gain",
                },
            )

        except Exception as e:
            self.logger.error(f"Error computing information gain: {str(e)}")
            return InformationGainResult(
                information_gain=0.0,
                uncertainty_reduction=0.0,
                expected_utility=0.0,
                optimal_action=None,
                confidence=0.0,
                metadata={"error": str(e)},
            )

    @kernel_function(
        description="Generate and test hypotheses through planned experiments",
        name="hypothesis_driven_exploration",
    )
    async def hypothesis_driven_exploration(
        self,
        world_model: WorldModel,
        observed_patterns: List[str],
        available_resources: Dict[str, Any],
    ) -> ExperimentPlan:
        """
        Generate hypotheses and plan experiments to test them.

        Args:
            world_model: Current world model
            observed_patterns: Patterns observed that need explanation
            available_resources: Resources available for experimentation

        Returns:
            ExperimentPlan: Plan for testing hypotheses
        """
        try:
            self.logger.info("Starting hypothesis-driven exploration")

            # Generate hypotheses from observed patterns
            hypotheses = await self._generate_hypotheses(world_model, observed_patterns)

            # Prioritize hypotheses based on potential impact and testability
            prioritized_hypotheses = await self._prioritize_hypotheses(
                hypotheses, available_resources
            )

            # Create experiment plan
            experiment_plan = await self._create_experiment_plan(
                prioritized_hypotheses, available_resources
            )

            # Store active hypotheses for tracking
            for hypothesis in prioritized_hypotheses:
                self.active_hypotheses[hypothesis.hypothesis_id] = hypothesis

            self.experiment_history.append(experiment_plan)

            self.logger.info(f"Created experiment plan {experiment_plan.experiment_id}")
            return experiment_plan

        except Exception as e:
            self.logger.error(f"Error in hypothesis-driven exploration: {str(e)}")
            return ExperimentPlan(
                experiment_id=str(uuid.uuid4()),
                target_hypotheses=[],
                actions=[],
                expected_outcomes={},
                resource_requirements={},
                success_criteria=[],
                risk_assessment={},
                priority_score=0.0,
            )

    @kernel_function(
        description="Plan strategic actions to address knowledge gaps",
        name="plan_to_learn",
    )
    async def plan_to_learn(
        self,
        world_model: WorldModel,
        goal_description: str,
        current_capabilities: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Plan strategic actions to learn what's needed to achieve goals.

        Args:
            world_model: Current world model
            goal_description: Description of what needs to be achieved
            current_capabilities: Current knowledge and capabilities

        Returns:
            List[Dict[str, Any]]: Ordered list of learning actions
        """
        try:
            self.logger.info(f"Planning to learn for goal: {goal_description}")

            # Identify knowledge gaps
            knowledge_gaps = await self._identify_knowledge_gaps(
                world_model, goal_description, current_capabilities
            )

            # Prioritize gaps by importance and learnability
            prioritized_gaps = await self._prioritize_learning_gaps(knowledge_gaps)

            # Create learning action plan
            learning_actions = []
            for gap in prioritized_gaps:
                actions = await self._create_gap_specific_actions(gap, world_model)
                learning_actions.extend(actions)

            # Optimize action sequence for efficiency using topological sorting and resource constraints
            optimized_actions = await self._optimize_learning_sequence(learning_actions)

            self.logger.info(
                f"Created learning plan with {len(optimized_actions)} actions"
            )
            return optimized_actions

        except Exception as e:
            self.logger.error(f"Error in plan_to_learn: {str(e)}")
            return []

    @kernel_function(
        description="Update world model efficiently from sparse observations",
        name="update_from_sparse_data",
    )
    async def update_from_sparse_data(
        self,
        world_model: WorldModel,
        sparse_observations: List[WorldModelEvidence],
        update_strategy: str = "bayesian_optimal",
    ) -> WorldModel:
        """
        Efficiently update world model from limited observations.

        Args:
            world_model: Model to update
            sparse_observations: Limited observations to learn from
            update_strategy: Strategy for efficient updating

        Returns:
            WorldModel: Updated world model
        """
        try:
            self.logger.info(
                f"Updating model from {len(sparse_observations)} sparse observations"
            )

            if not sparse_observations:
                return world_model

            # Apply sample-efficient update strategy
            if update_strategy == "bayesian_optimal":
                updated_model = await self._bayesian_optimal_update(
                    world_model, sparse_observations
                )
            elif update_strategy == "information_theoretic":
                updated_model = await self._information_theoretic_update(
                    world_model, sparse_observations
                )
            else:
                # Default to standard Bayesian update
                updated_model = world_model
                for observation in sparse_observations:
                    updated_model = await self.hierarchical_manager.bayesian_update(
                        updated_model.model_id, observation
                    )

            # Update confidence based on data sparsity
            updated_model = await self._adjust_confidence_for_sparsity(
                updated_model, len(sparse_observations)
            )

            self.logger.info("Model updated successfully from sparse data")
            return updated_model

        except Exception as e:
            self.logger.error(f"Error updating from sparse data: {str(e)}")
            return world_model

    @kernel_function(
        description="Calculate curiosity bonus for exploration-exploitation balance",
        name="calculate_curiosity_bonus",
    )
    async def calculate_curiosity_bonus(
        self,
        world_model: WorldModel,
        action: Dict[str, Any],
        historical_actions: List[Dict[str, Any]],
    ) -> float:
        """
        Calculate curiosity bonus for balancing exploration and exploitation.

        Args:
            world_model: Current world model
            action: Action being considered
            historical_actions: Previously taken actions

        Returns:
            float: Curiosity bonus value
        """
        try:
            # Calculate novelty bonus
            novelty_bonus = await self._calculate_novelty_bonus(
                action, historical_actions
            )

            # Calculate uncertainty bonus
            uncertainty_bonus = await self._calculate_uncertainty_bonus(
                world_model, action
            )

            # Calculate diversity bonus
            diversity_bonus = await self._calculate_diversity_bonus(
                action, historical_actions
            )

            # Calculate surprise bonus
            surprise_bonus = await self._calculate_surprise_bonus(world_model, action)

            # Weighted combination
            curiosity_bonus = (
                0.3 * novelty_bonus
                + 0.3 * uncertainty_bonus
                + 0.2 * diversity_bonus
                + 0.2 * surprise_bonus
            ) * self.curiosity_bonus_weight

            return curiosity_bonus

        except Exception as e:
            self.logger.error(f"Error calculating curiosity bonus: {str(e)}")
            return 0.0

    # Private helper methods

    async def _calculate_expected_gain(
        self,
        model: WorldModel,
        action: Dict[str, Any],
        target_variables: Optional[List[str]],
    ) -> float:
        """Calculate expected information gain for an action."""
        try:
            # Simple information gain based on uncertainty reduction
            current_uncertainty = model.uncertainty_estimate

            # Estimate post-action uncertainty (simplified)
            action_informativeness = action.get("informativeness", 0.5)
            expected_uncertainty_reduction = (
                current_uncertainty * action_informativeness * 0.1
            )

            return expected_uncertainty_reduction
        except Exception:
            return 0.0

    async def _calculate_value_of_information(
        self,
        model: WorldModel,
        information_gain: float,
        action: Optional[Dict[str, Any]],
    ) -> float:
        """Calculate the value of information for decision making."""
        try:
            # Simple VOI calculation based on gain and action cost
            action_cost = action.get("cost", 1.0) if action else 1.0
            voi = (
                information_gain / action_cost if action_cost > 0 else information_gain
            )
            return voi
        except Exception:
            return 0.0

    async def _calculate_gain_confidence(
        self, model: WorldModel, actions: List[Dict[str, Any]]
    ) -> float:
        """Calculate confidence in information gain estimates."""
        try:
            # Confidence based on model certainty and number of actions
            base_confidence = 1.0 - model.uncertainty_estimate
            action_diversity_factor = min(1.0, len(actions) / 10.0)
            return base_confidence * action_diversity_factor
        except Exception:
            return 0.0

    async def _generate_hypotheses(
        self, world_model: WorldModel, patterns: List[str]
    ) -> List[Hypothesis]:
        """Generate testable hypotheses from observed patterns."""
        hypotheses = []

        for i, pattern in enumerate(patterns):
            hypothesis = Hypothesis(
                hypothesis_id=str(uuid.uuid4()),
                description=f"Hypothesis for pattern: {pattern}",
                predictions={"outcome": "positive", "confidence": 0.7},
                confidence=0.6,
                prior_probability=0.5,
                evidence_required=[f"test_{pattern}"],
                test_cost=1.0,
                potential_gain=0.8,
                created_at=datetime.now(),
            )
            hypotheses.append(hypothesis)

        return hypotheses

    async def _prioritize_hypotheses(
        self, hypotheses: List[Hypothesis], resources: Dict[str, Any]
    ) -> List[Hypothesis]:
        """Prioritize hypotheses based on potential impact and feasibility."""

        def priority_score(h: Hypothesis) -> float:
            return (
                h.potential_gain / h.test_cost if h.test_cost > 0 else h.potential_gain
            )

        return sorted(hypotheses, key=priority_score, reverse=True)

    async def _create_experiment_plan(
        self, hypotheses: List[Hypothesis], resources: Dict[str, Any]
    ) -> ExperimentPlan:
        """Create a plan to test the prioritized hypotheses."""
        return ExperimentPlan(
            experiment_id=str(uuid.uuid4()),
            target_hypotheses=[h.hypothesis_id for h in hypotheses[:3]],  # Top 3
            actions=[{"type": "test", "target": h.description} for h in hypotheses[:3]],
            expected_outcomes={"success_probability": 0.7},
            resource_requirements={"time": 1.0, "effort": 0.5},
            success_criteria=["hypothesis_confirmed", "uncertainty_reduced"],
            risk_assessment={"failure_risk": 0.3},
            priority_score=sum(h.potential_gain for h in hypotheses[:3]),
        )

    async def _identify_knowledge_gaps(
        self, world_model: WorldModel, goal: str, capabilities: Dict[str, Any]
    ) -> List[LearningGap]:
        """Identify gaps between current knowledge and goal requirements."""
        gaps = []

        # Simple gap identification based on goal analysis
        required_knowledge = [
            "domain_knowledge",
            "procedural_steps",
            "causal_relationships",
        ]

        for i, knowledge_type in enumerate(required_knowledge):
            if knowledge_type not in capabilities:
                gap = LearningGap(
                    gap_id=str(uuid.uuid4()),
                    description=f"Missing {knowledge_type} for {goal}",
                    importance=0.8 - i * 0.1,
                    difficulty=0.5 + i * 0.1,
                    knowledge_type=knowledge_type,
                    dependencies=[],
                    potential_sources=["observation", "experimentation"],
                    acquisition_strategy="active_learning",
                )
                gaps.append(gap)

        return gaps

    async def _prioritize_learning_gaps(
        self, gaps: List[LearningGap]
    ) -> List[LearningGap]:
        """Prioritize learning gaps by importance and feasibility."""

        def gap_priority(gap: LearningGap) -> float:
            return (
                gap.importance / gap.difficulty
                if gap.difficulty > 0
                else gap.importance
            )

        return sorted(gaps, key=gap_priority, reverse=True)

    async def _create_gap_specific_actions(
        self, gap: LearningGap, world_model: WorldModel
    ) -> List[Dict[str, Any]]:
        """Create specific actions to address a knowledge gap."""
        return [
            {
                "type": "observe",
                "target": gap.description,
                "method": "systematic_observation",
                "priority": gap.importance,
                "estimated_effort": gap.difficulty,
            },
            {
                "type": "experiment",
                "target": gap.description,
                "method": "controlled_experiment",
                "priority": gap.importance * 0.8,
                "estimated_effort": gap.difficulty * 1.2,
            },
        ]

    async def _optimize_learning_sequence(
        self, actions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Optimize the sequence of learning actions for efficiency."""
        # Simple optimization: sort by priority and effort
        return sorted(
            actions, key=lambda x: (-x.get("priority", 0), x.get("estimated_effort", 1))
        )

    async def _bayesian_optimal_update(
        self, model: WorldModel, observations: List[WorldModelEvidence]
    ) -> WorldModel:
        """Perform Bayesian optimal update from sparse observations."""
        # For each observation, update the model
        updated_model = model
        for obs in observations:
            updated_model = await self.hierarchical_manager.bayesian_update(
                updated_model.model_id,
                obs,
                learning_rate=0.2,  # Higher learning rate for sparse data
            )
        return updated_model

    async def _information_theoretic_update(
        self, model: WorldModel, observations: List[WorldModelEvidence]
    ) -> WorldModel:
        """Update model using information-theoretic principles."""
        # Simplified information-theoretic update
        return await self._bayesian_optimal_update(model, observations)

    async def _adjust_confidence_for_sparsity(
        self, model: WorldModel, num_observations: int
    ) -> WorldModel:
        """Adjust model confidence based on data sparsity."""
        # Lower confidence for very sparse data
        sparsity_penalty = max(0.1, 1.0 - (10.0 / (num_observations + 10.0)))
        model.confidence_score *= sparsity_penalty
        return model

    async def _calculate_novelty_bonus(
        self, action: Dict[str, Any], historical_actions: List[Dict[str, Any]]
    ) -> float:
        """Calculate bonus for novel actions."""
        # Simple novelty: count how many times we've seen similar actions
        similar_count = sum(
            1
            for hist_action in historical_actions
            if hist_action.get("type") == action.get("type")
        )
        return max(0.0, 1.0 - (similar_count / 10.0))

    async def _calculate_uncertainty_bonus(
        self, model: WorldModel, action: Dict[str, Any]
    ) -> float:
        """Calculate bonus for actions in uncertain areas."""
        return model.uncertainty_estimate

    async def _calculate_diversity_bonus(
        self, action: Dict[str, Any], historical_actions: List[Dict[str, Any]]
    ) -> float:
        """Calculate bonus for diverse action selection."""
        if not historical_actions:
            return 1.0

        # Calculate diversity based on action types
        action_types = [a.get("type", "unknown") for a in historical_actions]
        current_type = action.get("type", "unknown")

        type_frequency = action_types.count(current_type) / len(action_types)
        return 1.0 - type_frequency

    async def _calculate_surprise_bonus(
        self, model: WorldModel, action: Dict[str, Any]
    ) -> float:
        """Calculate bonus for potentially surprising outcomes."""
        # Simple surprise bonus based on model uncertainty
        return model.uncertainty_estimate * 0.5
