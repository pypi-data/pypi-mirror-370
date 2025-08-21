"""
MSA Stage Protocols for Model Synthesis Architecture

This module defines the protocols (interfaces) for each stage of the MSA pipeline,
ensuring type safety and clear separation of concerns.
"""

from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable


@dataclass
class ParsedProblem:
    """Result of problem parsing stage"""

    variables: Dict[str, Dict[str, Any]]
    constraints: List[Dict[str, Any]]
    queries: List[str]
    problem_type: str
    confidence: float
    metadata: Dict[str, Any]


@dataclass
class KnowledgeContext:
    """Result of knowledge retrieval stage"""

    relevant_documents: List[Dict[str, Any]]
    patterns: List[str]
    domain_knowledge: Dict[str, Any]
    relevance_scores: List[float]
    metadata: Dict[str, Any]


@dataclass
class CausalGraph:
    """Causal dependency graph representation"""

    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    reasoning_paths: List[List[str]]
    metadata: Dict[str, Any]


@dataclass
class SynthesizedProgram:
    """Result of program synthesis stage"""

    program_code: str
    parameters: Dict[str, Any]
    imports: List[str]
    functions: List[str]
    confidence: float
    metadata: Dict[str, Any]


@dataclass
class ValidationResult:
    """Result of model validation stage"""

    success: bool
    errors: List[str]
    warnings: List[str]
    checks: Dict[str, bool]
    suggestions: List[str]
    confidence_adjustment: float


@runtime_checkable
class ProblemParserProtocol(Protocol):
    """Protocol for Stage 1: Problem parsing and variable extraction"""

    @abstractmethod
    async def parse_problem(self, problem: str, context: Optional[str] = None) -> ParsedProblem:
        """Parse natural language problem into structured format"""
        ...


@runtime_checkable
class KnowledgeRetrieverProtocol(Protocol):
    """Protocol for Stage 2: Knowledge retrieval and context building"""

    @abstractmethod
    async def retrieve_knowledge(self, parsed_problem: ParsedProblem, top_k: int = 5) -> KnowledgeContext:
        """Retrieve relevant knowledge for the parsed problem"""
        ...


@runtime_checkable
class GraphBuilderProtocol(Protocol):
    """Protocol for Stage 3: Causal graph construction"""

    @abstractmethod
    async def build_graph(self, parsed_problem: ParsedProblem, knowledge_context: KnowledgeContext) -> CausalGraph:
        """Build causal dependency graph from parsed problem and knowledge"""
        ...


@runtime_checkable
class ProgramSynthesizerProtocol(Protocol):
    """Protocol for Stage 4: PPL program generation"""

    @abstractmethod
    async def synthesize_program(self, causal_graph: CausalGraph, parsed_problem: ParsedProblem) -> SynthesizedProgram:
        """Generate NumPyro probabilistic program from causal graph"""
        ...


@runtime_checkable
class ModelValidatorProtocol(Protocol):
    """Protocol for Stage 5: Model validation and refinement"""

    @abstractmethod
    async def validate_model(self, program: SynthesizedProgram, parsed_problem: ParsedProblem) -> ValidationResult:
        """Validate synthesized program for correctness and completeness"""
        ...


@runtime_checkable
class MSAStageProtocol(Protocol):
    """Unified protocol for all MSA synthesis stages"""

    async def parse_problem(self, problem: str, context: Optional[str] = None) -> ParsedProblem:
        """Stage 1: Parse natural language problem"""
        ...

    async def retrieve_knowledge(self, parsed_problem: ParsedProblem) -> KnowledgeContext:
        """Stage 2: Retrieve relevant knowledge"""
        ...

    async def build_graph(self, parsed_problem: ParsedProblem, knowledge: KnowledgeContext) -> CausalGraph:
        """Stage 3: Create dependency graph"""
        ...

    async def synthesize_program(self, graph: CausalGraph, problem: ParsedProblem) -> SynthesizedProgram:
        """Stage 4: Generate PPL program"""
        ...

    async def validate_model(self, program: SynthesizedProgram, problem: ParsedProblem) -> ValidationResult:
        """Stage 5: Validate and refine program"""
        ...
