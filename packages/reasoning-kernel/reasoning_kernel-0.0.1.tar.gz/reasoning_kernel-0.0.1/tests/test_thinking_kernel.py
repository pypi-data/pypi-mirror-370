"""
Tests for ThinkingReasoningKernel: MSA-Native Agent Orchestration

This module tests the ThinkingReasoningKernel class and its agent ecosystem,
including agent coordination, reasoning mode switching, memory integration,
and end-to-end thinking exploration workflows.

Author: AI Assistant & Reasoning Kernel Team
Date: 2025-08-15
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# Test imports
from reasoning_kernel.agents.thinking_kernel import (
    ThinkingReasoningKernel,
    ModelSynthesisAgent,
    ReasoningMode,
    ThinkingResult,
)
from reasoning_kernel.core.exploration_triggers import ExplorationTrigger


class TestModelSynthesisAgent:
    """Test ModelSynthesisAgent functionality"""

    @pytest.fixture
    def mock_kernel(self):
        """Create mock Semantic Kernel"""
        kernel = MagicMock()
        return kernel

    @pytest.fixture
    def agent(self, mock_kernel):
        """Create ModelSynthesisAgent instance"""
        return ModelSynthesisAgent(mock_kernel)

    @pytest.mark.asyncio
    async def test_analyze_problem_structure(self, agent):
        """Test problem structure analysis"""
        problem = "A novel situation requiring adaptive reasoning"
        context = "medical_diagnosis"

        result = await agent.analyze_problem_structure(problem, context)

        assert isinstance(result, dict)
        assert result["problem_type"] == "open_world_reasoning"
        assert result["domain"] == "medical_diagnosis"
        assert result["exploration_required"] is True
        assert result["novelty_score"] == 0.8


class TestThinkingKernelSimplified:
    """Simplified test for ThinkingReasoningKernel"""

    @pytest.fixture
    def mock_kernel(self):
        """Create mock Semantic Kernel"""
        kernel = MagicMock()
        return kernel

    @pytest.fixture
    def mock_memory_store(self):
        """Create mock Redis memory store"""
        store = AsyncMock()
        return store

    @pytest.fixture
    async def thinking_kernel(self, mock_kernel, mock_memory_store):
        """Create ThinkingReasoningKernel instance with mocked dependencies"""
        with (
            patch("reasoning_kernel.agents.thinking_kernel.ThinkingExplorationPlugin") as mock_plugin,
            patch("reasoning_kernel.agents.thinking_kernel.HierarchicalWorldModelManager") as mock_manager,
            patch("reasoning_kernel.agents.thinking_kernel.SampleEfficientLearningPlugin") as mock_learning,
        ):

            # Setup mocks
            mock_plugin.return_value = AsyncMock()
            mock_manager.return_value = AsyncMock()
            mock_learning.return_value = AsyncMock()

            kernel = ThinkingReasoningKernel(
                kernel=mock_kernel,
                memory_store=mock_memory_store,
                cache_config={"result_cache_size": 10, "result_ttl": 300},
            )
            return kernel

    @pytest.mark.asyncio
    async def test_initialization(self, thinking_kernel):
        """Test ThinkingReasoningKernel initialization"""
        assert thinking_kernel.kernel is not None
        assert thinking_kernel.memory_store is not None
        assert thinking_kernel.result_cache is not None
        assert thinking_kernel.model_cache is not None
        assert len(thinking_kernel.agents) == 4

    @pytest.mark.asyncio
    async def test_determine_reasoning_mode(self, thinking_kernel):
        """Test reasoning mode determination logic"""
        # Test specific mode request
        mode = thinking_kernel._determine_reasoning_mode(ExplorationTrigger.NOVEL_SITUATION, ReasoningMode.STANDARD)
        assert mode == ReasoningMode.STANDARD

        # Test hybrid mode with novelty trigger
        mode = thinking_kernel._determine_reasoning_mode(ExplorationTrigger.NOVEL_SITUATION, ReasoningMode.HYBRID)
        assert mode == ReasoningMode.EXPLORATION


class TestReasoningModeEnum:
    """Test ReasoningMode enum functionality"""

    def test_reasoning_mode_values(self):
        """Test ReasoningMode enum values"""
        assert ReasoningMode.STANDARD.value == "standard"
        assert ReasoningMode.EXPLORATION.value == "exploration"
        assert ReasoningMode.SYNTHESIS.value == "synthesis"
        assert ReasoningMode.EVALUATION.value == "evaluation"
        assert ReasoningMode.HYBRID.value == "hybrid"


class TestThinkingResult:
    """Test ThinkingResult dataclass functionality"""

    def test_thinking_result_creation(self):
        """Test ThinkingResult creation and default values"""
        result = ThinkingResult(
            scenario="test scenario",
            trigger_detected=True,
            trigger_type=ExplorationTrigger.NOVEL_SITUATION,
            reasoning_mode=ReasoningMode.EXPLORATION,
        )

        assert result.scenario == "test scenario"
        assert result.trigger_detected is True
        assert result.trigger_type == ExplorationTrigger.NOVEL_SITUATION
        assert result.reasoning_mode == ReasoningMode.EXPLORATION
        assert result.world_models == []
        assert result.confidence_score == 0.0
        assert result.execution_time == 0.0
        assert result.memory_operations == []
        assert result.agent_interactions == []
