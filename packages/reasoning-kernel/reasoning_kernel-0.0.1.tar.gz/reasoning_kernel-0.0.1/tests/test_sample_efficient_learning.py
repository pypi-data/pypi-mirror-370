"""
Tests for Sample Efficient Learning Plugin
==========================================

Tests for information gain computation, hypothesis-driven exploration,
and sample-efficient learning capabilities.
"""

import pytest
from unittest.mock import AsyncMock
from datetime import datetime

from reasoning_kernel.plugins.sample_efficient_learning_plugin import (
    SampleEfficientLearningPlugin,
    InformationGainResult,
    Hypothesis,
    ExperimentPlan,
    LearningGap,
)
from reasoning_kernel.models.world_model import WorldModel, WorldModelEvidence, WorldModelLevel, ModelType


@pytest.fixture
def sample_world_model():
    """Create a sample world model for testing."""
    return WorldModel(
        model_id="test_model_001",
        model_level=WorldModelLevel.INSTANCE,
        model_type=ModelType.PROBABILISTIC,
        structure={"symptom_severity": 0.8, "patient_age": 45, "diagnosis_confidence": 0.3},
        parameters={
            "age_severity": {"type": "correlation", "strength": 0.6},
            "symptoms_diagnosis": {"type": "causal", "strength": 0.4},
        },
        confidence_score=0.7,
        domain="medical",
        context_description="Test medical scenario with novel symptoms",
        evidence_history=[
            WorldModelEvidence(
                observation_id="obs_001",
                evidence_type="observation",
                data={"symptom": "bioluminescent fingernails"},
                timestamp=datetime.now(),
                reliability=0.9,
                source="clinical_exam",
            )
        ],
    )


@pytest.fixture
def learning_plugin():
    """Create a sample efficient learning plugin for testing."""
    # Mock the hierarchical manager
    mock_manager = AsyncMock()
    plugin = SampleEfficientLearningPlugin(hierarchical_manager=mock_manager)
    return plugin


class TestSampleEfficientLearningPlugin:
    """Test cases for the sample efficient learning plugin."""

    @pytest.mark.asyncio
    async def test_plugin_initialization(self, learning_plugin):
        """Test plugin initializes correctly."""
        assert learning_plugin is not None
        assert hasattr(learning_plugin, "active_hypotheses")
        assert hasattr(learning_plugin, "experiment_history")
        assert hasattr(learning_plugin, "learning_gaps")
        assert isinstance(learning_plugin.active_hypotheses, dict)
        assert hasattr(learning_plugin, "hierarchical_manager")

    @pytest.mark.asyncio
    async def test_compute_information_gain_basic(self, learning_plugin, sample_world_model):
        """Test basic information gain computation."""
        potential_actions = [
            {"type": "test", "target": "blood_work", "cost": 0.2},
            {"type": "observe", "target": "symptom_progression", "cost": 0.1},
            {"type": "interview", "target": "family_history", "cost": 0.3},
        ]

        # Mock the helper methods
        learning_plugin._calculate_expected_gain = AsyncMock(side_effect=[0.7, 0.5, 0.3])
        learning_plugin._calculate_value_of_information = AsyncMock(return_value=0.8)
        learning_plugin._calculate_gain_confidence = AsyncMock(return_value=0.9)

        result = await learning_plugin.compute_information_gain(sample_world_model, potential_actions)

        assert isinstance(result, InformationGainResult)
        assert result.information_gain == 0.7  # Max gain from blood_work
        assert result.confidence == 0.9
        assert result.optimal_action is not None
        assert result.optimal_action["type"] == "test"
        assert result.metadata["n_actions_evaluated"] == 3

    @pytest.mark.asyncio
    async def test_hypothesis_driven_exploration(self, learning_plugin, sample_world_model):
        """Test hypothesis-driven exploration."""
        observed_patterns = [
            "Bioluminescent fingernails appear at night",
            "Condition correlates with recent travel to deep caves",
            "Patient shows no other symptoms",
        ]

        available_resources = {"time": 5.0, "budget": 1000, "equipment": ["microscope", "spectrometer"]}

        # Mock the helper methods
        sample_hypotheses = [
            Hypothesis(
                hypothesis_id="hyp_001",
                description="Fungal infection with bioluminescent properties",
                predictions={"growth_pattern": "radial", "luminosity": "blue-green"},
                confidence=0.7,
                prior_probability=0.3,
                evidence_required=["culture_test", "spore_analysis"],
                test_cost=100.0,
                potential_gain=0.9,
                created_at=datetime.now(),
            )
        ]

        learning_plugin._generate_hypotheses = AsyncMock(return_value=sample_hypotheses)
        learning_plugin._prioritize_hypotheses = AsyncMock(return_value=sample_hypotheses)
        learning_plugin._create_experiment_plan = AsyncMock(
            return_value=ExperimentPlan(
                experiment_id="exp_001",
                target_hypotheses=["hyp_001"],
                actions=[{"type": "culture_test", "sample": "fingernail"}],
                expected_outcomes={"growth": 0.7},
                resource_requirements={"time": 2.0},
                success_criteria=["fungal_growth_detected"],
                risk_assessment={"contamination_risk": 0.1},
                priority_score=0.9,
            )
        )

        result = await learning_plugin.hypothesis_driven_exploration(
            sample_world_model, observed_patterns, available_resources
        )

        assert isinstance(result, ExperimentPlan)
        assert result.experiment_id == "exp_001"
        assert len(result.target_hypotheses) == 1
        assert result.priority_score == 0.9

    @pytest.mark.asyncio
    async def test_plan_to_learn(self, learning_plugin, sample_world_model):
        """Test strategic learning plan generation."""
        goal = "Achieve 90% diagnostic confidence for the bioluminescent condition"
        current_capabilities = {
            "diagnostic_tools": ["visual_exam", "basic_blood_work"],
            "expertise_level": 0.6,
            "time_available": 3.0,
        }

        # Mock the helper methods
        sample_gaps = [
            LearningGap(
                gap_id="gap_001",
                description="Need advanced fungal identification techniques",
                importance=0.9,
                difficulty=0.7,
                knowledge_type="procedural",
                dependencies=["fungal_expertise"],
                potential_sources=["mycology_lab", "expert_consultation"],
                acquisition_strategy="expert_consultation",
            )
        ]

        learning_plugin._identify_knowledge_gaps = AsyncMock(return_value=sample_gaps)
        learning_plugin._prioritize_learning_gaps = AsyncMock(return_value=sample_gaps)
        learning_plugin._create_gap_specific_actions = AsyncMock(
            return_value=[{"type": "consult", "target": "mycologist", "urgency": "high"}]
        )
        learning_plugin._optimize_learning_sequence = AsyncMock(
            return_value=[{"type": "consult", "target": "mycologist", "urgency": "high"}]
        )

        result = await learning_plugin.plan_to_learn(sample_world_model, goal, current_capabilities)

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["type"] == "consult"

    @pytest.mark.asyncio
    async def test_update_from_sparse_data(self, learning_plugin, sample_world_model):
        """Test model updates from sparse observations."""
        sparse_observations = [
            {
                "type": "lab_result",
                "data": {"fungal_culture": "positive", "species": "unknown"},
                "confidence": 0.8,
                "timestamp": datetime.now().isoformat(),
            }
        ]

        # Mock the hierarchical manager
        learning_plugin.hierarchical_manager.bayesian_update = AsyncMock(return_value=sample_world_model)
        learning_plugin._calculate_observation_weight = AsyncMock(return_value=0.7)
        learning_plugin._propagate_uncertainty = AsyncMock(return_value={"uncertainty": 0.3})

        result = await learning_plugin.update_from_sparse_data(sample_world_model, sparse_observations)

        assert isinstance(result, WorldModel)
        # Verify the hierarchical manager was called
        learning_plugin.hierarchical_manager.bayesian_update.assert_called_once()

    @pytest.mark.asyncio
    async def test_calculate_curiosity_bonus(self, learning_plugin, sample_world_model):
        """Test curiosity bonus calculation."""
        action = {"type": "novel_test", "unexplored": True, "complexity": 0.8}
        historical_actions = [{"type": "routine_test", "unexplored": False, "complexity": 0.3}]

        # Mock the helper methods
        learning_plugin._calculate_novelty_bonus = AsyncMock(return_value=0.8)
        learning_plugin._calculate_complexity_bonus = AsyncMock(return_value=0.7)
        learning_plugin._calculate_diversity_bonus = AsyncMock(return_value=0.6)

        result = await learning_plugin.calculate_curiosity_bonus(sample_world_model, action, historical_actions)

        assert isinstance(result, float)
        assert result > 0.0  # Should have positive curiosity bonus


class TestInformationGainResult:
    """Test cases for InformationGainResult dataclass."""

    def test_information_gain_result_creation(self):
        """Test creation of InformationGainResult."""
        result = InformationGainResult(
            information_gain=0.8,
            uncertainty_reduction=0.6,
            expected_utility=0.7,
            optimal_action={"type": "test", "target": "sample"},
            confidence=0.9,
            metadata={"method": "expected_value"},
        )

        assert result.information_gain == 0.8
        assert result.confidence == 0.9
        assert result.optimal_action is not None
        assert result.optimal_action["type"] == "test"

    def test_information_gain_result_with_none_action(self):
        """Test InformationGainResult with no optimal action."""
        result = InformationGainResult(
            information_gain=0.0,
            uncertainty_reduction=0.0,
            expected_utility=0.0,
            optimal_action=None,
            confidence=0.0,
            metadata={"error": "no_valid_actions"},
        )

        assert result.optimal_action is None
        assert result.information_gain == 0.0


class TestHypothesis:
    """Test cases for Hypothesis dataclass."""

    def test_hypothesis_creation(self):
        """Test creation of Hypothesis."""
        hypothesis = Hypothesis(
            hypothesis_id="hyp_test_001",
            description="Test hypothesis for bioluminescent condition",
            predictions={"outcome": "positive", "mechanism": "fungal"},
            confidence=0.75,
            prior_probability=0.4,
            evidence_required=["lab_test", "microscopy"],
            test_cost=50.0,
            potential_gain=0.8,
            created_at=datetime.now(),
        )

        assert hypothesis.hypothesis_id == "hyp_test_001"
        assert hypothesis.confidence == 0.75
        assert len(hypothesis.evidence_required) == 2
        assert hypothesis.test_cost == 50.0


class TestExperimentPlan:
    """Test cases for ExperimentPlan dataclass."""

    def test_experiment_plan_creation(self):
        """Test creation of ExperimentPlan."""
        plan = ExperimentPlan(
            experiment_id="exp_test_001",
            target_hypotheses=["hyp_001", "hyp_002"],
            actions=[{"type": "lab_test", "sample": "tissue"}, {"type": "imaging", "method": "fluorescence"}],
            expected_outcomes={"positive_result": 0.7},
            resource_requirements={"time": 2.5, "cost": 500},
            success_criteria=["hypothesis_confirmed", "mechanism_identified"],
            risk_assessment={"false_positive": 0.1, "contamination": 0.05},
            priority_score=0.85,
        )

        assert plan.experiment_id == "exp_test_001"
        assert len(plan.target_hypotheses) == 2
        assert len(plan.actions) == 2
        assert plan.priority_score == 0.85


class TestLearningGap:
    """Test cases for LearningGap dataclass."""

    def test_learning_gap_creation(self):
        """Test creation of LearningGap."""
        gap = LearningGap(
            gap_id="gap_test_001",
            description="Need expertise in fungal bioluminescence",
            importance=0.9,
            difficulty=0.7,
            knowledge_type="conceptual",
            dependencies=["mycology_basics", "biochemistry"],
            potential_sources=["expert_database", "literature_review"],
            acquisition_strategy="expert_consultation",
        )

        assert gap.gap_id == "gap_test_001"
        assert gap.knowledge_type == "conceptual"
        assert len(gap.dependencies) == 2
        assert len(gap.potential_sources) == 2


class TestIntegration:
    """Integration tests for sample efficient learning."""

    @pytest.mark.asyncio
    async def test_complete_learning_cycle(self, learning_plugin, sample_world_model):
        """Test a complete learning cycle from information gain to model update."""
        # Step 1: Compute information gain
        actions = [{"type": "test", "target": "sample"}]
        learning_plugin._calculate_expected_gain = AsyncMock(return_value=0.8)
        learning_plugin._calculate_value_of_information = AsyncMock(return_value=0.7)
        learning_plugin._calculate_gain_confidence = AsyncMock(return_value=0.9)

        gain_result = await learning_plugin.compute_information_gain(sample_world_model, actions)

        # Step 2: Generate hypotheses
        patterns = ["pattern_1", "pattern_2"]
        resources = {"time": 2.0}

        learning_plugin._generate_hypotheses = AsyncMock(
            return_value=[
                Hypothesis(
                    hypothesis_id="hyp_1",
                    description="Test hypothesis",
                    predictions={"test": "positive"},
                    confidence=0.7,
                    prior_probability=0.4,
                    evidence_required=["test"],
                    test_cost=20.0,
                    potential_gain=0.9,
                    created_at=datetime.now(),
                )
            ]
        )
        learning_plugin._prioritize_hypotheses = AsyncMock(
            return_value=[
                Hypothesis(
                    hypothesis_id="hyp_1",
                    description="Test hypothesis",
                    predictions={"test": "positive"},
                    confidence=0.7,
                    prior_probability=0.4,
                    evidence_required=["test"],
                    test_cost=20.0,
                    potential_gain=0.9,
                    created_at=datetime.now(),
                )
            ]
        )
        learning_plugin._create_experiment_plan = AsyncMock(
            return_value=ExperimentPlan("exp_1", ["hyp_1"], actions, {}, {}, [], {}, 0.8)
        )

        experiment_plan = await learning_plugin.hypothesis_driven_exploration(sample_world_model, patterns, resources)

        # Step 3: Update model from results
        observations = [{"type": "result", "data": {"confirmed": True}}]
        learning_plugin.hierarchical_manager.bayesian_update = AsyncMock(return_value=sample_world_model)
        learning_plugin._calculate_observation_weight = AsyncMock(return_value=0.8)
        learning_plugin._propagate_uncertainty = AsyncMock(return_value={"uncertainty": 0.2})

        updated_model = await learning_plugin.update_from_sparse_data(sample_world_model, observations)

        # Verify the complete cycle
        assert isinstance(gain_result, InformationGainResult)
        assert isinstance(experiment_plan, ExperimentPlan)
        assert isinstance(updated_model, WorldModel)
        assert gain_result.information_gain == 0.8
        assert experiment_plan.priority_score == 0.8

    @pytest.mark.asyncio
    async def test_error_handling(self, learning_plugin, sample_world_model):
        """Test error handling in learning components."""
        # Test with empty actions
        result = await learning_plugin.compute_information_gain(sample_world_model, [])
        assert isinstance(result, InformationGainResult)
        assert result.information_gain == 0.0
        assert result.optimal_action is None

        # Test with invalid patterns
        result = await learning_plugin.hypothesis_driven_exploration(sample_world_model, [], {})
        assert isinstance(result, ExperimentPlan)
        assert len(result.target_hypotheses) == 0
