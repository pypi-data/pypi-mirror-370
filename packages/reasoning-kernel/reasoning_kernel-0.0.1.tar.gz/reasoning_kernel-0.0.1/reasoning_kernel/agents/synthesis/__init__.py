"""
MSA Synthesis Agents Module

This module contains the individual stages of the Model Synthesis Architecture:
- ProblemParser: Stage 1 - Parse natural language problems
- KnowledgeRetriever: Stage 2 - Retrieve relevant knowledge
- GraphBuilder: Stage 3 - Build causal dependency graphs
- ProgramSynthesizer: Stage 4 - Generate NumPyro programs
- ModelValidator: Stage 5 - Validate and refine programs
"""

from .problem_parser import ProblemParser
from .protocols import CausalGraph
from .protocols import GraphBuilderProtocol
from .protocols import KnowledgeContext
from .protocols import KnowledgeRetrieverProtocol
from .protocols import ModelValidatorProtocol
from .protocols import MSAStageProtocol
from .protocols import ParsedProblem
from .protocols import ProblemParserProtocol
from .protocols import ProgramSynthesizerProtocol
from .protocols import SynthesizedProgram
from .protocols import ValidationResult


__all__ = [
    # Data classes
    "ParsedProblem",
    "KnowledgeContext",
    "CausalGraph",
    "SynthesizedProgram",
    "ValidationResult",
    # Protocols
    "ProblemParserProtocol",
    "KnowledgeRetrieverProtocol",
    "GraphBuilderProtocol",
    "ProgramSynthesizerProtocol",
    "ModelValidatorProtocol",
    "MSAStageProtocol",
    # Implementations
    "ProblemParser",
]
