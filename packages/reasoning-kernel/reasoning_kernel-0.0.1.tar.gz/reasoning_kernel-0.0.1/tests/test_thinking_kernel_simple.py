"""
Simple integration test for ThinkingReasoningKernel

This test validates the basic functionality without complex agent mocking.
"""

import pytest
from reasoning_kernel.agents.thinking_kernel import ReasoningMode, ThinkingResult
from reasoning_kernel.core.exploration_triggers import ExplorationTrigger


def test_reasoning_mode_enum():
    """Test ReasoningMode enum has correct values"""
    assert ReasoningMode.STANDARD.value == "standard"
    assert ReasoningMode.EXPLORATION.value == "exploration"
    assert ReasoningMode.SYNTHESIS.value == "synthesis"
    assert ReasoningMode.EVALUATION.value == "evaluation"
    assert ReasoningMode.HYBRID.value == "hybrid"


def test_thinking_result_dataclass():
    """Test ThinkingResult dataclass functionality"""
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


def test_thinking_result_to_dict():
    """Test ThinkingResult conversion to dictionary"""
    result = ThinkingResult(
        scenario="test scenario",
        trigger_detected=True,
        trigger_type=ExplorationTrigger.NOVEL_SITUATION,
        reasoning_mode=ReasoningMode.EXPLORATION,
    )

    result_dict = result.to_dict()

    assert isinstance(result_dict, dict)
    assert result_dict["scenario"] == "test scenario"
    assert result_dict["trigger_detected"] is True
    assert result_dict["reasoning_mode"] == ReasoningMode.EXPLORATION.value
    assert "world_models" in result_dict
    assert "confidence_score" in result_dict


if __name__ == "__main__":
    pytest.main([__file__])
