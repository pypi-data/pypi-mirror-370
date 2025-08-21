"""
Mode 1: LLM-powered knowledge retrieval using Semantic Kernel
This mode acts as the "savvy librarian" extracting relevant knowledge
"""

import asyncio
import json
import logging
from typing import Any, Dict, List

from reasoning_kernel.core.kernel_config import KernelManager


logger = logging.getLogger(__name__)


class KnowledgeExtractor:
    """Mode 1 of MSA - Knowledge extraction using LLM capabilities"""

    def __init__(self, kernel_manager: KernelManager):
        self.kernel_manager = kernel_manager

    async def extract_scenario_knowledge(self, scenario: str) -> Dict[str, Any]:
        """
        Extract comprehensive knowledge about a scenario

        Args:
            scenario: Description of the scenario to analyze

        Returns:
            Dictionary containing extracted knowledge components
        """
        try:
            logger.info(f"Extracting knowledge for scenario: {scenario[:100]}...")

            # Extract different types of knowledge in parallel
            knowledge_tasks = [
                self._extract_entities(scenario),
                self._extract_relationships(scenario),
                self._extract_causal_factors(scenario),
                self._extract_constraints(scenario),
                self._extract_domain_knowledge(scenario),
            ]

            results = await asyncio.gather(*knowledge_tasks, return_exceptions=True)

            # Compile knowledge base
            knowledge_base = {
                "entities": results[0] if not isinstance(results[0], Exception) else [],
                "relationships": results[1] if not isinstance(results[1], Exception) else [],
                "causal_factors": results[2] if not isinstance(results[2], Exception) else [],
                "constraints": results[3] if not isinstance(results[3], Exception) else [],
                "domain_knowledge": results[4] if not isinstance(results[4], Exception) else [],
                "scenario": scenario,
            }

            logger.info("Knowledge extraction completed successfully")
            return knowledge_base

        except Exception as e:
            logger.error(f"Failed to extract scenario knowledge: {e}")
            raise

    async def _extract_entities(self, scenario: str) -> List[Dict[str, str]]:
        """Extract key entities from the scenario"""
        prompt = f"""
        Analyze the following scenario and identify all key entities (people, objects, concepts, variables).
        For each entity, provide its type and role in the scenario.
        
        Scenario: {scenario}
        
        Return a JSON list of entities with the format:
        [
            {{"name": "entity_name", "type": "entity_type", "role": "description_of_role"}},
            ...
        ]
        
        Provide only the JSON, no additional text.
        """

        try:
            result = await self.kernel_manager.invoke_prompt(prompt)
            entities = json.loads(result.strip())
            return entities if isinstance(entities, list) else []
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Failed to parse entities: {e}")
            return []

    async def _extract_relationships(self, scenario: str) -> List[Dict[str, str]]:
        """Extract relationships between entities"""
        prompt = f"""
        Analyze the following scenario and identify relationships between entities.
        Focus on dependencies, influences, and interactions.
        
        Scenario: {scenario}
        
        Return a JSON list of relationships with the format:
        [
            {{"from": "entity1", "to": "entity2", "type": "relationship_type", "strength": "weak/moderate/strong"}},
            ...
        ]
        
        Provide only the JSON, no additional text.
        """

        try:
            result = await self.kernel_manager.invoke_prompt(prompt)
            relationships = json.loads(result.strip())
            return relationships if isinstance(relationships, list) else []
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Failed to parse relationships: {e}")
            return []

    async def _extract_causal_factors(self, scenario: str) -> List[Dict[str, str]]:
        """Extract causal factors and their potential effects"""
        prompt = f"""
        Analyze the following scenario and identify causal factors - things that can cause or influence outcomes.
        Include both direct causes and contributing factors.
        
        Scenario: {scenario}
        
        Return a JSON list of causal factors with the format:
        [
            {{"factor": "causal_factor", "effect": "potential_effect", "probability": "low/medium/high"}},
            ...
        ]
        
        Provide only the JSON, no additional text.
        """

        try:
            result = await self.kernel_manager.invoke_prompt(prompt)
            factors = json.loads(result.strip())
            return factors if isinstance(factors, list) else []
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Failed to parse causal factors: {e}")
            return []

    async def _extract_constraints(self, scenario: str) -> List[Dict[str, str]]:
        """Extract constraints and limitations in the scenario"""
        prompt = f"""
        Analyze the following scenario and identify constraints, limitations, or boundary conditions.
        Include physical, logical, temporal, and resource constraints.
        
        Scenario: {scenario}
        
        Return a JSON list of constraints with the format:
        [
            {{"constraint": "constraint_description", "type": "physical/logical/temporal/resource", "impact": "description"}},
            ...
        ]
        
        Provide only the JSON, no additional text.
        """

        try:
            result = await self.kernel_manager.invoke_prompt(prompt)
            constraints = json.loads(result.strip())
            return constraints if isinstance(constraints, list) else []
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Failed to parse constraints: {e}")
            return []

    async def _extract_domain_knowledge(self, scenario: str) -> List[str]:
        """Extract relevant domain knowledge and principles"""
        prompt = f"""
        Analyze the following scenario and identify relevant domain knowledge, principles, or theories
        that could help understand or model this situation.
        
        Scenario: {scenario}
        
        Return a JSON list of relevant knowledge areas:
        [
            "knowledge_area_1",
            "knowledge_area_2",
            ...
        ]
        
        Provide only the JSON, no additional text.
        """

        try:
            result = await self.kernel_manager.invoke_prompt(prompt)
            knowledge = json.loads(result.strip())
            return knowledge if isinstance(knowledge, list) else []
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Failed to parse domain knowledge: {e}")
            return []

    async def generate_model_specifications(self, knowledge_base: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate specifications for probabilistic model construction

        Args:
            knowledge_base: Extracted knowledge from Mode 1

        Returns:
            Model specifications for Mode 2
        """
        try:
            prompt = f"""
            Based on the following extracted knowledge, generate specifications for a probabilistic model.
            Focus on variables, their relationships, and uncertainty characteristics.
            
            Knowledge Base:
            - Entities: {knowledge_base.get('entities', [])}
            - Relationships: {knowledge_base.get('relationships', [])}
            - Causal Factors: {knowledge_base.get('causal_factors', [])}
            - Constraints: {knowledge_base.get('constraints', [])}
            
            Return a JSON object with the format:
            {{
                "variables": [
                    {{"name": "variable_name", "type": "continuous/discrete/categorical", "range": "description"}},
                    ...
                ],
                "dependencies": [
                    {{"parent": "parent_var", "child": "child_var", "relationship": "description"}},
                    ...
                ],
                "uncertainties": [
                    {{"variable": "var_name", "source": "source_of_uncertainty", "type": "epistemic/aleatory"}},
                    ...
                ],
                "model_type": "suggested_model_type"
            }}
            
            Provide only the JSON, no additional text.
            """

            result = await self.kernel_manager.invoke_prompt(prompt)
            specifications = json.loads(result.strip())

            logger.info("Model specifications generated successfully")
            return specifications

        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Failed to generate model specifications: {e}")
            # Return default structure
            return {"variables": [], "dependencies": [], "uncertainties": [], "model_type": "generic_bayesian"}
