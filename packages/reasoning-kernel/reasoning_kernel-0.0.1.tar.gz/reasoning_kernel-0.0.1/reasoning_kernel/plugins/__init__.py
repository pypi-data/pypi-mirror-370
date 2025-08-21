"""
Reasoning Kernel Plugin Architecture
====================================

This module implements the five-stage MSA pipeline through specialized plugins:
1. ParsingPlugin - Transform vignettes into structured constraints
2. KnowledgePlugin - Retrieve relevant background knowledge
3. SynthesisPlugin - Generate dependency graphs and probabilistic programs
4. InferencePlugin - Execute inference in secure sandboxed environment

Each plugin integrates with Semantic Kernel for orchestration and Azure AI Foundry for LLM access.
"""

from .inference_plugin import InferencePlugin
from .knowledge_plugin import KnowledgePlugin
from .parsing_plugin import ParsingPlugin
from .synthesis_plugin import SynthesisPlugin


__all__ = [
    "ParsingPlugin",
    "KnowledgePlugin", 
    "SynthesisPlugin",
    "InferencePlugin"
]