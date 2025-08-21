"""
Graph Builder Stage - MSA Stage 3

Builds causal dependency graphs from parsed problems and retrieved knowledge.
Creates structured representations for probabilistic program generation.
"""

import json
import logging
from typing import Any, Dict, List

from semantic_kernel import Kernel
from semantic_kernel.contents import AuthorRole
from semantic_kernel.contents import ChatMessageContent
from semantic_kernel.functions import kernel_function

from .protocols import CausalGraph
from .protocols import KnowledgeContext
from .protocols import ParsedProblem


logger = logging.getLogger(__name__)


class GraphBuilder:
    """Stage 3: Build causal dependency graphs from parsed problems"""

    def __init__(self, kernel: Kernel):
        self.kernel = kernel
        self._setup_graph_templates()

    def _setup_graph_templates(self):
        """Setup templates for graph construction"""
        self.graph_prompt_template = """
        Build a causal dependency graph for this probabilistic modeling problem.
        
        Parsed Problem:
        - Variables: {variables}
        - Constraints: {constraints}
        - Problem Type: {problem_type}
        
        Retrieved Knowledge:
        - Domain Knowledge: {domain_knowledge}
        - Relevant Patterns: {patterns}
        
        Create a causal graph with:
        1. Nodes: Each variable with its properties
        2. Edges: Causal relationships between variables
        3. Reasoning paths: Logical flow from inputs to outputs
        
        Return as JSON with this exact structure:
        {{
            "nodes": [
                {{
                    "id": "variable_name",
                    "type": "continuous|discrete|categorical|binary",
                    "role": "input|intermediate|output",
                    "description": "brief description",
                    "properties": {{
                        "distribution": "suggested prior",
                        "range": [min, max] or ["option1", "option2"],
                        "dependencies": ["parent1", "parent2"]
                    }}
                }}
            ],
            "edges": [
                {{
                    "from": "parent_variable",
                    "to": "child_variable", 
                    "type": "causal|observational|confounding",
                    "strength": 0.0-1.0,
                    "description": "relationship description"
                }}
            ],
            "reasoning_paths": [
                ["input_var1", "intermediate_var", "output_var"],
                ["input_var2", "output_var"]
            ],
            "confidence": 0.8,
            "complexity": "low|medium|high"
        }}
        """

    async def build_graph(self, parsed_problem: ParsedProblem, knowledge_context: KnowledgeContext) -> CausalGraph:
        """Build causal dependency graph from parsed problem and knowledge"""
        try:
            # Format the graph building prompt
            prompt = self.graph_prompt_template.format(
                variables=json.dumps(parsed_problem.variables, indent=2),
                constraints=json.dumps(parsed_problem.constraints, indent=2),
                problem_type=parsed_problem.problem_type,
                domain_knowledge=json.dumps(knowledge_context.domain_knowledge, indent=2),
                patterns=knowledge_context.patterns,
            )

            # Get chat service from kernel
            chat_service = self.kernel.get_service(type=None)

            # Create chat message
            messages = [ChatMessageContent(role=AuthorRole.USER, content=prompt)]

            # Get response
            response = await chat_service.complete_chat_async(messages)
            response_text = str(response)

            # Parse JSON response
            graph_json = self._extract_json_from_response(response_text)

            # Validate and process the graph
            nodes = self._validate_nodes(graph_json.get("nodes", []), parsed_problem)
            edges = self._validate_edges(graph_json.get("edges", []), nodes)
            reasoning_paths = self._validate_reasoning_paths(graph_json.get("reasoning_paths", []), nodes)

            # Create CausalGraph object
            result = CausalGraph(
                nodes=nodes,
                edges=edges,
                reasoning_paths=reasoning_paths,
                metadata={
                    "problem_type": parsed_problem.problem_type,
                    "variable_count": len(nodes),
                    "edge_count": len(edges),
                    "path_count": len(reasoning_paths),
                    "confidence": graph_json.get("confidence", 0.7),
                    "complexity": graph_json.get("complexity", "medium"),
                    "knowledge_sources": len(knowledge_context.relevant_documents),
                    "graph_generation_success": True,
                },
            )

            logger.info(f"Built causal graph with {len(nodes)} nodes and {len(edges)} edges")
            return result

        except Exception as e:
            logger.error(f"Error building causal graph: {e}")
            # Return minimal fallback graph
            fallback_nodes = []
            for var_name, var_info in parsed_problem.variables.items():
                fallback_nodes.append(
                    {
                        "id": var_name,
                        "type": var_info.get("type", "unknown"),
                        "role": "unknown",
                        "description": var_info.get("description", var_name),
                        "properties": {
                            "distribution": var_info.get("prior", "unknown"),
                            "range": var_info.get("range", []),
                            "dependencies": var_info.get("dependencies", []),
                        },
                    }
                )

            return CausalGraph(
                nodes=fallback_nodes,
                edges=[],
                reasoning_paths=[],
                metadata={"error": str(e), "graph_generation_failed": True},
            )

    def _extract_json_from_response(self, response_text: str) -> Dict[str, Any]:
        """Extract JSON from LLM response, handling markdown code blocks"""
        try:
            # Try direct JSON parsing first
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract from markdown code blocks
            if "```json" in response_text:
                json_part = response_text.split("```json")[1].split("```")[0].strip()
                return json.loads(json_part)
            elif "```" in response_text:
                json_part = response_text.split("```")[1].split("```")[0].strip()
                return json.loads(json_part)
            else:
                # Fallback: try to find JSON-like content
                import re

                json_pattern = r"\{.*\}"
                matches = re.findall(json_pattern, response_text, re.DOTALL)
                if matches:
                    return json.loads(matches[0])
                else:
                    raise ValueError("No valid JSON found in response")

    def _validate_nodes(self, nodes: List[Dict[str, Any]], parsed_problem: ParsedProblem) -> List[Dict[str, Any]]:
        """Validate and clean node definitions"""
        validated_nodes = []
        expected_vars = set(parsed_problem.variables.keys())
        found_vars = set()

        for node in nodes:
            if not isinstance(node, dict) or "id" not in node:
                continue

            node_id = node["id"]
            found_vars.add(node_id)

            # Ensure required fields are present
            validated_node = {
                "id": node_id,
                "type": node.get("type", "unknown"),
                "role": node.get("role", "unknown"),
                "description": node.get("description", node_id),
                "properties": node.get("properties", {}),
            }

            validated_nodes.append(validated_node)

        # Add any missing variables from the parsed problem
        for var_name in expected_vars - found_vars:
            var_info = parsed_problem.variables[var_name]
            validated_nodes.append(
                {
                    "id": var_name,
                    "type": var_info.get("type", "unknown"),
                    "role": "unknown",
                    "description": var_info.get("description", var_name),
                    "properties": {
                        "distribution": var_info.get("prior", "unknown"),
                        "range": var_info.get("range", []),
                        "dependencies": var_info.get("dependencies", []),
                    },
                }
            )

        return validated_nodes

    def _validate_edges(self, edges: List[Dict[str, Any]], nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate edge definitions against available nodes"""
        validated_edges = []
        node_ids = {node["id"] for node in nodes}

        for edge in edges:
            if not isinstance(edge, dict):
                continue

            from_node = edge.get("from")
            to_node = edge.get("to")

            # Check if both nodes exist
            if from_node in node_ids and to_node in node_ids:
                validated_edge = {
                    "from": from_node,
                    "to": to_node,
                    "type": edge.get("type", "causal"),
                    "strength": max(0.0, min(1.0, edge.get("strength", 0.5))),  # Clamp to [0,1]
                    "description": edge.get("description", f"{from_node} -> {to_node}"),
                }
                validated_edges.append(validated_edge)

        return validated_edges

    def _validate_reasoning_paths(self, paths: List[List[str]], nodes: List[Dict[str, Any]]) -> List[List[str]]:
        """Validate reasoning paths against available nodes"""
        validated_paths = []
        node_ids = {node["id"] for node in nodes}

        for path in paths:
            if not isinstance(path, list):
                continue

            # Check if all nodes in path exist
            if all(node_id in node_ids for node_id in path):
                validated_paths.append(path)

        return validated_paths

    @kernel_function(name="build_graph", description="Build causal dependency graph from parsed problem and knowledge")
    async def kernel_build_graph(self, parsed_problem_json: str, knowledge_context_json: str) -> str:
        """Kernel function wrapper for graph building"""
        # Parse input JSON
        parsed_data = json.loads(parsed_problem_json)
        parsed_problem = ParsedProblem(
            variables=parsed_data.get("variables", {}),
            constraints=parsed_data.get("constraints", []),
            queries=parsed_data.get("queries", []),
            problem_type=parsed_data.get("problem_type", "unknown"),
            confidence=parsed_data.get("confidence", 0.5),
            metadata=parsed_data.get("metadata", {}),
        )

        knowledge_data = json.loads(knowledge_context_json)
        knowledge_context = KnowledgeContext(
            relevant_documents=knowledge_data.get("relevant_documents", []),
            patterns=knowledge_data.get("patterns", []),
            domain_knowledge=knowledge_data.get("domain_knowledge", {}),
            relevance_scores=knowledge_data.get("relevance_scores", []),
            metadata=knowledge_data.get("metadata", {}),
        )

        result = await self.build_graph(parsed_problem, knowledge_context)

        return json.dumps(
            {
                "nodes": result.nodes,
                "edges": result.edges,
                "reasoning_paths": result.reasoning_paths,
                "metadata": result.metadata,
            },
            indent=2,
        )


# Export the class
__all__ = ["GraphBuilder"]
