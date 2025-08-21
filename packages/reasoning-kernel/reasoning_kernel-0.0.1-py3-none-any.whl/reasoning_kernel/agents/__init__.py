"""
Agents Module for Reasoning Kernel

This module contains specialized agents for MSA-based reasoning and thinking exploration.

Key Components:
- ThinkingReasoningKernel: Central orchestrator for agent-based thinking exploration
- ModelSynthesisAgent: Problem understanding and reasoning model creation
- ProbabilisticReasoningAgent: PPL execution and Bayesian inference
- EvaluationAgent: Quality assessment and feedback loops
- KnowledgeRetrievalAgent: Semantic search and context gathering

Author: AI Assistant & Reasoning Kernel Team
Date: 2025-08-15
"""

from .thinking_kernel import EvaluationAgent
from .thinking_kernel import KnowledgeRetrievalAgent
from .thinking_kernel import ModelSynthesisAgent
from .thinking_kernel import ProbabilisticReasoningAgent
from .thinking_kernel import ReasoningMode
from .thinking_kernel import ThinkingReasoningKernel
from .thinking_kernel import ThinkingResult


__all__ = [
    "ThinkingReasoningKernel",
    "ModelSynthesisAgent",
    "ProbabilisticReasoningAgent",
    "EvaluationAgent",
    "KnowledgeRetrievalAgent",
    "ReasoningMode",
    "ThinkingResult",
]
