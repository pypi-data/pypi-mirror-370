"""
Knowledge Retriever Stage - MSA Stage 2

Retrieves relevant knowledge from Redis memory store and external sources
to provide context for model synthesis.
"""

import logging
from typing import Any, Dict, List, Optional

from semantic_kernel import Kernel
from semantic_kernel.functions import kernel_function
from semantic_kernel.memory import SemanticTextMemory

from .protocols import KnowledgeContext
from .protocols import ParsedProblem


logger = logging.getLogger(__name__)


class KnowledgeRetriever:
    """Stage 2: Retrieve relevant knowledge for model synthesis"""

    def __init__(self, kernel: Kernel):
        self.kernel = kernel
        self.memory: Optional[SemanticTextMemory] = getattr(kernel, "memory", None)
        self.collection_name = "msa_knowledge"

    async def retrieve_knowledge(
        self, parsed_problem: ParsedProblem, top_k: int = 5, threshold: float = 0.7
    ) -> KnowledgeContext:
        """Retrieve relevant knowledge for the parsed problem"""
        try:
            relevant_documents = []
            patterns = []
            relevance_scores = []
            domain_knowledge = {}
            search_queries = []

            # If memory is configured, search for relevant knowledge
            if self.memory:
                # Search for problem-specific knowledge
                search_queries = self._generate_search_queries(parsed_problem)

                for query in search_queries:
                    try:
                        # Use the correct SemanticTextMemory API
                        search_results = await self.memory.search(
                            collection=self.collection_name, query=query, limit=top_k, min_relevance_score=threshold
                        )

                        for result in search_results:
                            relevant_documents.append(
                                {
                                    "content": result.text,
                                    "relevance": result.relevance,
                                    "metadata": getattr(result, "metadata", {}),
                                    "query": query,
                                }
                            )
                            relevance_scores.append(result.relevance)

                    except Exception as e:
                        logger.warning(f"Memory search failed for query '{query}': {e}")
            else:
                # Generate search queries even if no memory is available
                search_queries = self._generate_search_queries(parsed_problem)

            # Extract domain patterns from variables and constraints
            patterns = self._extract_patterns(parsed_problem)

            # Build domain knowledge based on problem type
            domain_knowledge = self._build_domain_knowledge(parsed_problem)

            # Calculate overall retrieval confidence
            avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.5

            result = KnowledgeContext(
                relevant_documents=relevant_documents,
                patterns=patterns,
                domain_knowledge=domain_knowledge,
                relevance_scores=relevance_scores,
                metadata={
                    "search_queries": search_queries,
                    "top_k": top_k,
                    "threshold": threshold,
                    "avg_relevance": avg_relevance,
                    "memory_available": self.memory is not None,
                    "total_documents": len(relevant_documents),
                },
            )

            logger.info(f"Retrieved {len(relevant_documents)} relevant documents")
            return result

        except Exception as e:
            logger.error(f"Error retrieving knowledge: {e}")
            # Return minimal fallback result
            return KnowledgeContext(
                relevant_documents=[],
                patterns=[],
                domain_knowledge={},
                relevance_scores=[],
                metadata={"error": str(e), "retrieval_failed": True},
            )

    def _generate_search_queries(self, parsed_problem: ParsedProblem) -> List[str]:
        """Generate search queries based on parsed problem"""
        queries = []

        # Add variable-based queries
        for var_name, var_info in parsed_problem.variables.items():
            queries.append(f"{var_name} {var_info.get('type', '')} distribution")
            queries.append(f"{var_info.get('description', var_name)} modeling")

        # Add constraint-based queries
        for constraint in parsed_problem.constraints:
            if "description" in constraint:
                queries.append(constraint["description"])

        # Add problem type query
        queries.append(f"{parsed_problem.problem_type} probabilistic modeling")

        # Add general queries from user queries
        queries.extend(parsed_problem.queries)

        return queries[:10]  # Limit to avoid too many API calls

    def _extract_patterns(self, parsed_problem: ParsedProblem) -> List[str]:
        """Extract common patterns from the problem structure"""
        patterns = []

        # Variable type patterns
        var_types = [info.get("type") for info in parsed_problem.variables.values()]
        if "continuous" in var_types:
            patterns.append("continuous_variables")
        if "discrete" in var_types:
            patterns.append("discrete_variables")
        if "categorical" in var_types:
            patterns.append("categorical_variables")

        # Dependency patterns
        has_dependencies = any(info.get("dependencies", []) for info in parsed_problem.variables.values())
        if has_dependencies:
            patterns.append("variable_dependencies")

        # Constraint patterns
        constraint_types = [c.get("type") for c in parsed_problem.constraints]
        if "equality" in constraint_types:
            patterns.append("equality_constraints")
        if "inequality" in constraint_types:
            patterns.append("inequality_constraints")

        # Problem type patterns
        patterns.append(f"{parsed_problem.problem_type}_pattern")

        return patterns

    def _build_domain_knowledge(self, parsed_problem: ParsedProblem) -> Dict[str, Any]:
        """Build domain-specific knowledge based on problem characteristics"""
        knowledge = {
            "problem_type": parsed_problem.problem_type,
            "variable_count": len(parsed_problem.variables),
            "constraint_count": len(parsed_problem.constraints),
            "suggested_distributions": {},
            "modeling_approaches": [],
        }

        # Suggest appropriate distributions based on variable types
        for var_name, var_info in parsed_problem.variables.items():
            var_type = var_info.get("type", "unknown")
            var_range = var_info.get("range", [])

            if var_type == "continuous":
                if var_range and len(var_range) == 2:
                    knowledge["suggested_distributions"][var_name] = "Normal or Uniform"
                else:
                    knowledge["suggested_distributions"][var_name] = "Normal"
            elif var_type == "discrete":
                knowledge["suggested_distributions"][var_name] = "Poisson or Categorical"
            elif var_type == "binary":
                knowledge["suggested_distributions"][var_name] = "Bernoulli"
            elif var_type == "categorical":
                knowledge["suggested_distributions"][var_name] = "Categorical"

        # Suggest modeling approaches
        if parsed_problem.problem_type == "classification":
            knowledge["modeling_approaches"].append("logistic_regression")
            knowledge["modeling_approaches"].append("naive_bayes")
        elif parsed_problem.problem_type == "regression":
            knowledge["modeling_approaches"].append("linear_regression")
            knowledge["modeling_approaches"].append("polynomial_regression")
        elif parsed_problem.problem_type == "causal_inference":
            knowledge["modeling_approaches"].append("structural_causal_model")
            knowledge["modeling_approaches"].append("instrumental_variables")

        return knowledge

    @kernel_function(name="retrieve_knowledge", description="Retrieve relevant knowledge for model synthesis")
    async def kernel_retrieve_knowledge(self, parsed_problem_json: str, top_k: int = 5) -> str:
        """Kernel function wrapper for knowledge retrieval"""
        import json

        # Parse the input JSON
        parsed_data = json.loads(parsed_problem_json)
        parsed_problem = ParsedProblem(
            variables=parsed_data.get("variables", {}),
            constraints=parsed_data.get("constraints", []),
            queries=parsed_data.get("queries", []),
            problem_type=parsed_data.get("problem_type", "unknown"),
            confidence=parsed_data.get("confidence", 0.5),
            metadata=parsed_data.get("metadata", {}),
        )

        result = await self.retrieve_knowledge(parsed_problem, top_k=top_k)

        return json.dumps(
            {
                "relevant_documents": result.relevant_documents,
                "patterns": result.patterns,
                "domain_knowledge": result.domain_knowledge,
                "relevance_scores": result.relevance_scores,
                "metadata": result.metadata,
            },
            indent=2,
        )


# Export the class
__all__ = ["KnowledgeRetriever"]
