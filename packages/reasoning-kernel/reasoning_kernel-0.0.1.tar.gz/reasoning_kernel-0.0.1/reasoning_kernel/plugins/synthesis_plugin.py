"""
SynthesisPlugin - Stages 3 & 4 of the Reasoning Kernel
======================================================

Stage 3: Graph - Build conceptual dependency graph (G)
Stage 4: Synthesize - Translate G into probabilistic program (NumPyro)

Uses Azure LLM models for graph generation and code synthesis with validation.
"""

import json
from typing import Any, Dict, List, Tuple, TYPE_CHECKING


if TYPE_CHECKING:
    import networkx as nx

import ast
from dataclasses import dataclass
from enum import Enum
import subprocess

from semantic_kernel import Kernel
from semantic_kernel.functions import KernelArguments
import structlog


logger = structlog.get_logger(__name__)

try:
    import black  # type: ignore[import-untyped]
except ImportError:
    black = None
    logger.warning("black formatter not available")

try:
    import networkx as nx
except ImportError:
    # Create a minimal NetworkX replacement
    logger.warning("NetworkX not available, using minimal graph implementation")
    class MinimalDigraph:
        def __init__(self):
            self.nodes_data = {}
            self.edges_data = []
        
        def add_node(self, node_id, **kwargs):
            self.nodes_data[node_id] = kwargs
        
        def add_edge(self, source, target, **kwargs):
            self.edges_data.append((source, target, kwargs))
    
    # Create nx namespace
    nx = type('nx', (), {'DiGraph': MinimalDigraph})()

class NodeType(Enum):
    VARIABLE = "variable"
    PARAMETER = "parameter"
    OBSERVED = "observed"
    LATENT = "latent"
    DECISION = "decision"

class EdgeType(Enum):
    CAUSAL = "causal"
    CORRELATION = "correlation"
    DEPENDENCY = "dependency"
    CONSTRAINT = "constraint"

@dataclass
class GraphNode:
    """Node in the dependency graph"""
    id: str
    name: str
    node_type: NodeType
    properties: Dict[str, Any]
    metadata: Dict[str, Any]

@dataclass
class GraphEdge:
    """Edge in the dependency graph"""
    source: str
    target: str
    edge_type: EdgeType
    strength: float
    properties: Dict[str, Any]
    metadata: Dict[str, Any]

@dataclass
class DependencyGraph:
    """Complete dependency graph structure"""
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    graph_confidence: float
    networkx_graph: Any  # nx.DiGraph when networkx is available
    metadata: Dict[str, Any]

@dataclass
class ProbabilisticProgram:
    """Generated probabilistic program"""
    program_code: str
    model_name: str
    parameters: Dict[str, Any]
    validation_status: bool
    confidence: float
    metadata: Dict[str, Any]

class SynthesisPlugin:
    """
    Stages 3 & 4: Graph generation and probabilistic program synthesis
    
    Uses Azure LLM models to build causal dependency graphs and translate them
    into executable NumPyro probabilistic programs with validation.
    """
    
    def __init__(self, kernel: Kernel):
        self.kernel = kernel
        self.graph_function = None
        self.synthesis_function = None
        self._initialize_functions()
        
    def _initialize_functions(self):
        """Initialize semantic functions for graph generation and code synthesis"""
        
        # Graph generation function
        graph_prompt = """
        You are an expert at building causal dependency graphs from contextual information.
        
        Given the following augmented context, create a dependency graph that captures:
        1. Key variables and their relationships
        2. Causal dependencies and correlations
        3. Observable vs. latent variables
        4. Decision points and constraints
        
        INPUT: {{$context}}
        
        Return a JSON object with:
        {
            "nodes": [
                {
                    "id": "unique_node_id",
                    "name": "Human readable name",
                    "node_type": "variable|parameter|observed|latent|decision",
                    "properties": {"distribution": "normal", "bounds": [0, 100], ...},
                    "metadata": {"description": "...", "uncertainty": 0.2}
                }
            ],
            "edges": [
                {
                    "source": "node_id_1",
                    "target": "node_id_2", 
                    "edge_type": "causal|correlation|dependency|constraint",
                    "strength": 0.8,
                    "properties": {"lag": 0, "mechanism": "linear"},
                    "metadata": {"confidence": 0.7, "evidence": "..."}
                }
            ],
            "metadata": {
                "complexity": "medium",
                "total_nodes": 5,
                "total_edges": 7
            }
        }
        
        Ensure the graph is acyclic and represents realistic causal relationships.
        Return valid JSON only, no additional text.
        """
        
        self.graph_function = self.kernel.add_function(
            function_name="generate_dependency_graph",
            plugin_name="SynthesisPlugin",
            prompt=graph_prompt,
        )
        
        # Code synthesis function
        synthesis_prompt = """
        You are an expert at translating dependency graphs into NumPyro probabilistic programs.
        
        Given the following dependency graph, generate a complete NumPyro model:
        
        GRAPH: {{$graph}}
        
        CRITICAL REQUIREMENTS:
        1. Use only NumPyro distributions and primitives
        2. Implement proper sampling statements with numpyro.sample()
        3. Handle observed data with numpyro.sample(..., obs=data)
        4. Use appropriate priors and likelihood functions
        5. Include proper model validation and inference setup
        6. Add comprehensive docstrings and comments
        7. NEVER use incomplete try-except blocks - if you use try:, you MUST include both except: and/or finally:
        8. Avoid error handling unless absolutely necessary - keep code simple and clean
        9. Test all syntax carefully - every parenthesis, bracket, and colon must be properly closed
        
        Return only complete, syntactically correct Python code ready to execute.
        Do not include markdown code blocks, explanations, or incomplete code fragments.
        
        MANDATORY STRUCTURE (follow exactly):
        ```
        import numpyro
        import numpyro.distributions as dist
        import jax.numpy as jnp
        from jax import random

        def probabilistic_model(data=None):
            # Generated probabilistic model based on dependency graph
            # Prior definitions (use simple, clean syntax)
            param1 = numpyro.sample('param1', dist.Normal(0, 1))
            
            # Likelihood and relationships (no error handling needed)
            outcome = numpyro.sample('outcome', dist.Normal(param1, 0.5), obs=data)
            
            return outcome

        def run_inference(data, num_samples=1000):
            # Run MCMC inference on the model
            from numpyro.infer import MCMC, NUTS
            
            kernel = NUTS(probabilistic_model)
            mcmc = MCMC(kernel, num_warmup=500, num_samples=num_samples)
            rng_key = random.PRNGKey(0)
            mcmc.run(rng_key, data=data)
            
            return mcmc.get_samples()
        ```
        
        REMEMBER: Never write incomplete try-except blocks. Keep code simple without error handling.
        """
        
        self.synthesis_function = self.kernel.add_function(
            function_name="generate_probabilistic_program",
            plugin_name="SynthesisPlugin", 
            prompt=synthesis_prompt,
        )
    
    async def generate_dependency_graph(self, context: str, **kwargs) -> DependencyGraph:
        """
        Stage 3: Generate dependency graph from augmented context
        
        Args:
            context: Augmented context from knowledge retrieval
            **kwargs: Additional graph generation parameters
            
        Returns:
            DependencyGraph object with nodes, edges, and NetworkX representation
        """
        logger.info("Starting dependency graph generation", context_length=len(context))
        
        try:
            # Prepare arguments
            arguments = KernelArguments(context=context)
            
            # Execute graph generation with retry logic
            result = await self._execute_with_retry(self.graph_function, arguments)
            
            # Parse and validate JSON response
            graph_data = self._validate_graph_result(result)
            
            # Convert to structured objects
            dependency_graph = self._convert_to_dependency_graph(graph_data)
            
            logger.info("Dependency graph generated successfully",
                       nodes=len(dependency_graph.nodes),
                       edges=len(dependency_graph.edges))
            
            return dependency_graph
            
        except Exception as e:
            logger.error("Dependency graph generation failed", error=str(e))
            raise
    
    async def generate_probabilistic_program(self, graph: DependencyGraph, **kwargs) -> ProbabilisticProgram:
        """
        Stage 4: Generate NumPyro probabilistic program from dependency graph
        
        Args:
            graph: Dependency graph from stage 3
            **kwargs: Additional synthesis parameters
            
        Returns:
            ProbabilisticProgram with validated NumPyro code
        """
        logger.info("Starting probabilistic program synthesis")
        
        try:
            # Convert graph to JSON for LLM input
            graph_json = self._graph_to_json(graph)
            
            # Prepare arguments
            arguments = KernelArguments(graph=graph_json)
            
            # Execute synthesis with retry logic
            result = await self._execute_with_retry(self.synthesis_function, arguments)
            
            # Clean and validate the generated code
            cleaned_code = self._clean_generated_code(result)
            validated_code, validation_status = await self._validate_code(cleaned_code)
            
            # Calculate confidence based on validation results
            confidence = 0.9 if validation_status else 0.5
            
            program = ProbabilisticProgram(
                program_code=validated_code,
                model_name="generated_model",
                parameters=self._extract_parameters(validated_code),
                validation_status=validation_status,
                confidence=confidence,
                metadata={
                    "graph_nodes": len(graph.nodes),
                    "graph_edges": len(graph.edges),
                    "synthesis_timestamp": __import__("datetime").datetime.now().isoformat()
                }
            )
            
            logger.info("Probabilistic program generated successfully",
                       validation_status=validation_status,
                       code_lines=len(validated_code.split('\n')))
            
            return program
            
        except Exception as e:
            logger.error("Probabilistic program synthesis failed", error=str(e))
            raise
    
    async def _execute_with_retry(self, function, arguments: KernelArguments, max_retries: int = 3) -> str:
        """Execute function with exponential backoff retry logic"""
                
        for attempt in range(max_retries):
            try:
                result = await function.invoke(self.kernel, arguments)
                return str(result)
                
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                    
                wait_time = 2 ** attempt
                logger.warning(f"Synthesis attempt {attempt + 1} failed, retrying in {wait_time}s", 
                              error=str(e))
                await asyncio.sleep(wait_time)
        
        raise Exception("All synthesis attempts failed")
    
    def _validate_graph_result(self, result: str) -> Dict[str, Any]:
        """Validate and parse JSON graph result from LLM"""
        try:
            # Clean up result
            result = result.strip()
            if result.startswith("```json"):
                result = result[7:-3].strip()
            elif result.startswith("```"):
                result = result[3:-3].strip()
            
            graph_data = json.loads(result)
            
            # Validate required fields
            if "nodes" not in graph_data:
                graph_data["nodes"] = []
            if "edges" not in graph_data:
                graph_data["edges"] = []
            if "metadata" not in graph_data:
                graph_data["metadata"] = {}
            
            return graph_data
            
        except json.JSONDecodeError as e:
            logger.error("Failed to parse graph JSON result", result=result, error=str(e))
            return {"nodes": [], "edges": [], "metadata": {}}
    
    def _convert_to_dependency_graph(self, graph_data: Dict[str, Any]) -> DependencyGraph:
        """Convert parsed JSON data to DependencyGraph object"""
        
        # Create nodes
        nodes = []
        for node_data in graph_data.get("nodes", []):
            node = GraphNode(
                id=node_data.get("id", f"node_{len(nodes)}"),
                name=node_data.get("name", "Unknown"),
                node_type=NodeType(node_data.get("node_type", "variable")),
                properties=node_data.get("properties", {}),
                metadata=node_data.get("metadata", {})
            )
            nodes.append(node)
        
        # Create edges
        edges = []
        for edge_data in graph_data.get("edges", []):
            edge = GraphEdge(
                source=edge_data.get("source", ""),
                target=edge_data.get("target", ""),
                edge_type=EdgeType(edge_data.get("edge_type", "dependency")),
                strength=edge_data.get("strength", 0.5),
                properties=edge_data.get("properties", {}),
                metadata=edge_data.get("metadata", {})
            )
            edges.append(edge)
        
        # Create NetworkX graph
        nx_graph = nx.DiGraph()  # type: ignore[attr-defined]
        for node in nodes:
            nx_graph.add_node(node.id, **node.properties)
        for edge in edges:
            nx_graph.add_edge(edge.source, edge.target, **edge.properties)
        
        # Calculate graph confidence
        graph_confidence = self._calculate_graph_confidence(nodes, edges)
        
        return DependencyGraph(
            nodes=nodes,
            edges=edges,
            graph_confidence=graph_confidence,
            networkx_graph=nx_graph,
            metadata=graph_data.get("metadata", {})
        )
    
    def _calculate_graph_confidence(self, nodes: List[GraphNode], edges: List[GraphEdge]) -> float:
        """Calculate overall confidence in the generated graph"""
        if not nodes:
            return 0.0
        
        # Factor in node metadata confidence if available
        node_confidences = []
        for node in nodes:
            conf = node.metadata.get("confidence", 0.8)
            node_confidences.append(conf)
        
        # Factor in edge metadata confidence if available
        edge_confidences = []
        for edge in edges:
            conf = edge.metadata.get("confidence", 0.7)
            edge_confidences.append(conf)
        
        # Combine confidences
        all_confidences = node_confidences + edge_confidences
        if all_confidences:
            return sum(all_confidences) / len(all_confidences)
        else:
            return 0.6  # Default moderate confidence
    
    def _graph_to_json(self, graph: DependencyGraph) -> str:
        """Convert DependencyGraph to JSON string for LLM input"""
        graph_dict = {
            "nodes": [
                {
                    "id": node.id,
                    "name": node.name,
                    "node_type": node.node_type.value,
                    "properties": node.properties,
                    "metadata": node.metadata
                }
                for node in graph.nodes
            ],
            "edges": [
                {
                    "source": edge.source,
                    "target": edge.target,
                    "edge_type": edge.edge_type.value,
                    "strength": edge.strength,
                    "properties": edge.properties,
                    "metadata": edge.metadata
                }
                for edge in graph.edges
            ],
            "metadata": graph.metadata
        }
        return json.dumps(graph_dict, indent=2)
    
    def _clean_generated_code(self, code: str) -> str:
        """Clean and format generated code"""
        # Remove markdown code blocks
        if code.startswith("```python"):
            code = code[9:-3].strip()
        elif code.startswith("```"):
            code = code[3:-3].strip()
        
        return code.strip()
    
    async def _validate_code(self, code: str) -> Tuple[str, bool]:
        """Validate and format the generated NumPyro code"""
        try:
            # Enhanced syntax validation
            try:
                tree = ast.parse(code)
                # Check for incomplete try-except blocks
                self._check_for_incomplete_try_blocks(tree)
                logger.debug("Code syntax validation passed")
            except SyntaxError as e:
                logger.error("Syntax error in generated code", error=str(e), line=e.lineno, text=e.text)
                return self._fix_common_syntax_errors(code), False
            except Exception as e:
                logger.error("AST parsing failed", error=str(e))
                return code, False
            
            # Format with black
            try:
                if black is not None:
                    formatted_code = black.format_str(code, mode=black.Mode())
                    code = formatted_code
                else:
                    logger.warning("Black formatter not available, skipping code formatting")
            except Exception as e:
                logger.warning("Code formatting failed", error=str(e))
            
            # Run flake8 checks (optional, don't fail on this)
            validation_status = await self._run_flake8(code)
            
            return code, True  # Return True if syntax is valid, regardless of flake8
            
        except Exception as e:
            logger.error("Code validation failed", error=str(e))
            return code, False
    
    def _check_for_incomplete_try_blocks(self, tree: ast.AST) -> None:
        """Check AST for incomplete try-except blocks"""
        class TryBlockChecker(ast.NodeVisitor):
            def visit_Try(self, node):
                if not node.handlers and not node.finalbody:
                    raise SyntaxError("Try block without except or finally clause")
                self.generic_visit(node)
        
        checker = TryBlockChecker()
        checker.visit(tree)
    
    def _fix_common_syntax_errors(self, code: str) -> str:
        """Fix common syntax errors in generated code"""
        lines = code.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # Fix incomplete try blocks
            if line.strip().startswith('try:'):
                # Look ahead for except/finally
                has_handler = False
                for j in range(i + 1, len(lines)):
                    if lines[j].strip().startswith(('except', 'finally')):
                        has_handler = True
                        break
                    elif lines[j].strip() and not lines[j].startswith('    '):
                        break
                
                if not has_handler:
                    # Skip malformed try blocks
                    logger.warning("Removing incomplete try block", line_number=i+1)
                    continue
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    async def _run_flake8(self, code: str) -> bool:
        """Run flake8 on generated code"""
        try:
            import os
            import tempfile

            # Write code to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Run flake8
            result = subprocess.run(['flake8', temp_file], 
                                  capture_output=True, text=True)
            
            # Clean up
            os.unlink(temp_file)
            
            # Return True if no errors
            return result.returncode == 0
            
        except Exception as e:
            logger.warning("Flake8 validation failed", error=str(e))
            return True  # Don't fail on flake8 issues
    
    def _extract_parameters(self, code: str) -> Dict[str, Any]:
        """Extract parameters from generated code for metadata"""
        parameters = {}
        try:
            # Simple regex-based extraction of numpyro.sample statements
            import re

            # Find sample statements
            sample_pattern = r"numpyro\.sample\s*\(\s*['\"]([^'\"]+)['\"]"
            matches = re.findall(sample_pattern, code)
            
            for param in matches:
                parameters[param] = {"type": "sampled_parameter"}
            
        except Exception as e:
            logger.debug("Parameter extraction failed", error=str(e))
        
        return parameters