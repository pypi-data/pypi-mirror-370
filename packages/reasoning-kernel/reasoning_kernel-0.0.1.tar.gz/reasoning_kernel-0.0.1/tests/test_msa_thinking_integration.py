"""
Tests for MSA Thinking Integration Plugin
========================================

Comprehensive test suite for MSA pipeline integration, multi-agent orchestration,
and collaborative thinking capabilities.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from reasoning_kernel.plugins.msa_thinking_integration_plugin import (
    MSAThinkingIntegrationPlugin,
    ThinkingMode,
    ComplexityLevel,
    ThinkingSession,
    ThinkingActivationResult,
    AgentOrchestrationConfig,
)
from reasoning_kernel.models.world_model import WorldModel, WorldModelLevel, ModelType


@pytest.fixture
def mock_redis_manager():
    """Mock Redis manager for testing"""
    manager = AsyncMock()
    manager.store_exploration_pattern = AsyncMock(return_value=True)
    manager.get_similar_patterns = AsyncMock(return_value=[])
    return manager


@pytest.fixture
def mock_world_model_manager():
    """Mock hierarchical world model manager"""
    manager = AsyncMock()
    manager.get_model_by_id = AsyncMock(return_value=None)
    manager.synthesize_models = AsyncMock(return_value={})
    return manager


@pytest.fixture
def mock_thinking_plugin():
    """Mock thinking exploration plugin"""
    plugin = AsyncMock()
    plugin.reason_with_thinking = AsyncMock(
        return_value={"result": "thinking exploration complete", "triggers": [], "world_models": []}
    )
    return plugin


@pytest.fixture
def mock_learning_plugin():
    """Mock sample efficient learning plugin"""
    plugin = AsyncMock()
    plugin.compute_information_gain = AsyncMock(return_value=0.75)
    plugin.hypothesis_driven_exploration = AsyncMock(
        return_value={"hypotheses": ["test hypothesis"], "confidence": 0.8}
    )
    return plugin


@pytest.fixture
def mock_kernel():
    """Mock semantic kernel for testing"""
    kernel = MagicMock()
    kernel.add_plugin = MagicMock()
    return kernel


@pytest.fixture
async def msa_plugin(
    mock_redis_manager, mock_world_model_manager, mock_thinking_plugin, mock_learning_plugin, mock_kernel
):
    """Create MSA thinking integration plugin instance"""
    plugin = MSAThinkingIntegrationPlugin(
        thinking_plugin=mock_thinking_plugin,
        learning_plugin=mock_learning_plugin,
        hierarchical_manager=mock_world_model_manager,
        redis_manager=mock_redis_manager,
    )

    # Mock kernel registration
    plugin.kernel = mock_kernel
    return plugin


class TestMSAThinkingIntegrationPlugin:
    """Test suite for MSA thinking integration plugin"""

    @pytest.mark.asyncio
    async def test_analyze_thinking_activation_high_complexity(self, msa_plugin):
        """Test thinking activation analysis for high complexity scenarios"""
        scenario = "Complex multi-step reasoning problem with uncertain outcomes"
        context = {"domain": "mathematics", "variables": 10, "constraints": 5}

        result = await msa_plugin.analyze_thinking_activation(scenario, context)

        assert isinstance(result, dict)
        assert "should_activate" in result
        assert "complexity_level" in result
        assert "thinking_mode" in result
        assert "confidence" in result
        assert "reasoning" in result

        # Should activate for complex scenarios
        assert result["should_activate"] is True
        assert result["complexity_level"] in [level.name for level in ComplexityLevel]
        assert result["thinking_mode"] in [mode.name for mode in ThinkingMode]
        assert 0.0 <= result["confidence"] <= 1.0

    @pytest.mark.asyncio
    async def test_analyze_thinking_activation_low_complexity(self, msa_plugin):
        """Test thinking activation analysis for simple scenarios"""
        scenario = "Simple addition: 2 + 2"
        context = {"domain": "arithmetic", "variables": 2}

        result = await msa_plugin.analyze_thinking_activation(scenario, context)

        assert isinstance(result, dict)
        # Should not activate thinking for simple scenarios
        assert result["should_activate"] is False
        assert result["complexity_level"] == ComplexityLevel.LOW.name

    @pytest.mark.asyncio
    async def test_create_thinking_session(self, msa_plugin, mock_redis_manager):
        """Test thinking session creation"""
        scenario = "Test collaborative reasoning scenario"
        complexity = ComplexityLevel.HIGH
        mode = ThinkingMode.COLLABORATIVE
        participants = ["agent1", "agent2"]

        result = await msa_plugin.create_thinking_session(scenario, complexity.name, mode.name, participants)

        assert isinstance(result, dict)
        assert "session_id" in result
        assert "status" in result
        assert "world_model" in result
        assert "participants" in result

        assert result["status"] == "created"
        assert result["participants"] == participants

        # Should store session in Redis
        mock_redis_manager.store_exploration_pattern.assert_called_once()

    @pytest.mark.asyncio
    async def test_orchestrate_collaborative_thinking(self, msa_plugin):
        """Test collaborative thinking orchestration"""
        session_id = "test_session_123"
        prompt = "Solve this complex problem collaboratively"
        agent_configs = [
            {"agent_id": "reasoning_agent", "role": "analyzer"},
            {"agent_id": "creative_agent", "role": "ideator"},
        ]

        result = await msa_plugin.orchestrate_collaborative_thinking(session_id, prompt, agent_configs)

        assert isinstance(result, dict)
        assert "session_id" in result
        assert "consensus_result" in result
        assert "agent_contributions" in result
        assert "synthesis" in result
        assert "confidence" in result

        assert result["session_id"] == session_id
        assert isinstance(result["agent_contributions"], list)
        assert 0.0 <= result["confidence"] <= 1.0

    @pytest.mark.asyncio
    async def test_synthesize_msa_thinking_knowledge(self, msa_plugin):
        """Test MSA thinking knowledge synthesis"""
        session_id = "test_session_456"
        msa_results = {
            "reasoning_chain": ["step1", "step2", "step3"],
            "confidence": 0.85,
            "evidence": ["fact1", "fact2"],
        }
        thinking_insights = {
            "exploration_triggers": ["novel_situation"],
            "world_models": ["model1", "model2"],
            "strategies": ["hypothesis_testing"],
        }

        result = await msa_plugin.synthesize_msa_thinking_knowledge(session_id, msa_results, thinking_insights)

        assert isinstance(result, dict)
        assert "synthesis_id" in result
        assert "integrated_knowledge" in result
        assert "confidence_score" in result
        assert "recommendations" in result

        assert 0.0 <= result["confidence_score"] <= 1.0
        assert isinstance(result["recommendations"], list)

    @pytest.mark.asyncio
    async def test_complexity_scoring(self, msa_plugin):
        """Test complexity scoring algorithm"""
        # High complexity scenario
        high_complexity_context = {
            "variables": 15,
            "constraints": 8,
            "uncertainty_level": 0.9,
            "domain": "quantum_physics",
        }

        high_score = msa_plugin._calculate_complexity_score(
            "Complex quantum entanglement problem", high_complexity_context
        )

        # Low complexity scenario
        low_complexity_context = {"variables": 2, "constraints": 1, "uncertainty_level": 0.1, "domain": "arithmetic"}

        low_score = msa_plugin._calculate_complexity_score("Simple addition", low_complexity_context)

        assert high_score > low_score
        assert 0.0 <= high_score <= 1.0
        assert 0.0 <= low_score <= 1.0

    @pytest.mark.asyncio
    async def test_thinking_benefit_estimation(self, msa_plugin):
        """Test thinking benefit estimation"""
        scenario = "Multi-step reasoning with uncertain outcomes"
        complexity_level = ComplexityLevel.HIGH

        benefit_score = msa_plugin._estimate_thinking_benefit(scenario, complexity_level)

        assert 0.0 <= benefit_score <= 1.0
        assert benefit_score > 0.5  # High complexity should benefit from thinking

    @pytest.mark.asyncio
    async def test_thinking_mode_selection(self, msa_plugin):
        """Test thinking mode selection logic"""
        # Collaborative scenario
        collab_score = msa_plugin._calculate_complexity_score(
            "Multi-agent coordination problem", {"agents": 5, "interactions": 10}
        )
        collab_mode = msa_plugin._select_thinking_mode(collab_score, {"agents": 5})

        # Individual scenario
        individual_score = msa_plugin._calculate_complexity_score(
            "Single person math problem", {"agents": 1, "interactions": 0}
        )
        individual_mode = msa_plugin._select_thinking_mode(individual_score, {"agents": 1})

        assert collab_mode in [mode.name for mode in ThinkingMode]
        assert individual_mode in [mode.name for mode in ThinkingMode]

    @pytest.mark.asyncio
    async def test_consensus_calculation(self, msa_plugin):
        """Test consensus calculation from agent responses"""
        agent_responses = [
            {"agent_id": "agent1", "response": "Option A", "confidence": 0.8},
            {"agent_id": "agent2", "response": "Option A", "confidence": 0.9},
            {"agent_id": "agent3", "response": "Option B", "confidence": 0.6},
        ]

        consensus = msa_plugin._calculate_consensus(agent_responses)

        assert isinstance(consensus, dict)
        assert "consensus_response" in consensus
        assert "confidence" in consensus
        assert "agreement_level" in consensus

        # Should select Option A (higher confidence and majority)
        assert consensus["consensus_response"] == "Option A"
        assert 0.0 <= consensus["confidence"] <= 1.0

    @pytest.mark.asyncio
    async def test_session_management(self, msa_plugin):
        """Test thinking session lifecycle management"""
        # Create session
        session_result = await msa_plugin.create_thinking_session(
            "Test scenario",
            ComplexityLevel.MEDIUM.value,  # Use .value for the integer
            ThinkingMode.MANUAL.name,
            ["agent1"],
        )

        session_id = session_result["session_id"]

        # Orchestrate thinking
        thinking_result = await msa_plugin.orchestrate_collaborative_thinking(
            session_id, "Test prompt", [{"agent_id": "agent1", "role": "analyzer"}]
        )

        # Synthesize knowledge
        synthesis_result = await msa_plugin.synthesize_msa_thinking_knowledge(
            session_id, {"reasoning": "test reasoning"}, {"insights": "test insights"}
        )

        assert session_result["session_id"] == session_id
        assert thinking_result["session_id"] == session_id
        assert "synthesis_id" in synthesis_result

    @pytest.mark.asyncio
    async def test_error_handling(self, msa_plugin):
        """Test error handling in plugin methods"""
        # Test with invalid complexity level
        with pytest.raises(Exception):
            await msa_plugin.create_thinking_session(
                "Test scenario", "INVALID_COMPLEXITY", ThinkingMode.AUTOMATIC.name, ["agent1"]  # Invalid complexity
            )

        # Test with empty scenario
        result = await msa_plugin.analyze_thinking_activation("", {})
        assert result["should_activate"] is False

    @pytest.mark.asyncio
    async def test_integration_with_world_models(self, msa_plugin, mock_world_model_manager):
        """Test integration with hierarchical world models"""
        # Mock world model
        mock_world_model = WorldModel(
            model_id="test_model",
            model_level=WorldModelLevel.DOMAIN,
            domain="test_domain",
            context_description="Test context",
            applicable_situations=["test_situation"],
            confidence_score=0.8,
            model_type=ModelType.HYBRID,
            metadata={},
        )

        mock_world_model_manager.get_model_by_id.return_value = mock_world_model

        session_result = await msa_plugin.create_thinking_session(
            "Test with world model", ComplexityLevel.HIGH.name, ThinkingMode.AUTOMATIC.name, ["agent1"]
        )

        assert "world_model" in session_result
        assert session_result["world_model"] is not None


class TestDataClasses:
    """Test suite for MSA integration data classes"""

    def test_thinking_mode_enum(self):
        """Test ThinkingMode enum values"""
        assert ThinkingMode.AUTOMATIC is not None
        assert ThinkingMode.COLLABORATIVE is not None
        assert ThinkingMode.MANUAL is not None
        assert ThinkingMode.HYBRID is not None

    def test_complexity_level_enum(self):
        """Test ComplexityLevel enum values"""
        assert ComplexityLevel.LOW is not None
        assert ComplexityLevel.MEDIUM is not None
        assert ComplexityLevel.HIGH is not None
        assert ComplexityLevel.CRITICAL is not None

    def test_thinking_session_creation(self):
        """Test ThinkingSession dataclass"""
        session = ThinkingSession(
            session_id="test_123",
            scenario="Test scenario",
            complexity_level=ComplexityLevel.HIGH,
            thinking_mode=ThinkingMode.COLLABORATIVE,
            participants=["agent1", "agent2"],
            world_models={},
            active_hypotheses={},
            learning_progress={},
            session_metadata={"key": "value"},
            created_at=datetime.now(),
            last_updated=datetime.now(),
            status="active",
        )

        assert session.session_id == "test_123"
        assert session.scenario == "Test scenario"
        assert session.complexity_level == ComplexityLevel.HIGH
        assert session.thinking_mode == ThinkingMode.COLLABORATIVE
        assert len(session.participants) == 2
        assert session.status == "active"
        assert isinstance(session.created_at, datetime)
        assert isinstance(session.last_updated, datetime)
        assert session.session_metadata["key"] == "value"

    def test_thinking_activation_result(self):
        """Test ThinkingActivationResult dataclass"""
        result = ThinkingActivationResult(
            should_activate=True,
            reasoning="High complexity detected",
            complexity_score=0.85,
            complexity_level=ComplexityLevel.HIGH,
            recommended_mode=ThinkingMode.MANUAL,
            estimated_benefit=0.9,
            resource_requirements={"cpu": "high", "memory": "medium"},
            confidence=0.85,
        )

        assert result.should_activate is True
        assert result.reasoning == "High complexity detected"
        assert result.complexity_score == 0.85
        assert result.recommended_mode == ThinkingMode.MANUAL
        assert result.estimated_benefit == 0.9
        assert result.confidence == 0.85
        assert "cpu" in result.resource_requirements

    def test_agent_orchestration_config(self):
        """Test AgentOrchestrationConfig dataclass"""
        config = AgentOrchestrationConfig(
            max_agents=5,
            collaboration_strategy="parallel",
            consensus_threshold=0.8,
            max_iterations=15,
            timeout_seconds=600,
            knowledge_sharing_enabled=False,
            conflict_resolution_strategy="expertise_weighted",
        )

        assert config.max_agents == 5
        assert config.collaboration_strategy == "parallel"
        assert config.consensus_threshold == 0.8
        assert config.max_iterations == 15
        assert config.timeout_seconds == 600
        assert config.knowledge_sharing_enabled is False
        assert config.conflict_resolution_strategy == "expertise_weighted"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
