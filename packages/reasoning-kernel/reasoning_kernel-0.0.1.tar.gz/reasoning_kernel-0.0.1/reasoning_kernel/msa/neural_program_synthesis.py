"""
Neural Program Synthesis for MSA - Generates probabilistic programs using LLMs
Based on research paper 2507.12547: "Modeling Open-World Cognition as On-Demand Synthesis of Probabilistic Models"
"""

import json
import logging
import re
from typing import Any, Dict, List

from reasoning_kernel.core.kernel_config import KernelManager


logger = logging.getLogger(__name__)


class NeuralProgramSynthesizer:
    """
    Implements neurally-guided program synthesis from the MSA research paper.
    Uses LLMs to generate actual probabilistic program code based on scenario analysis.
    """

    def __init__(self, kernel_manager: KernelManager):
        self.kernel_manager = kernel_manager

    async def synthesize_probabilistic_program(self, scenario: str, knowledge_base: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a probabilistic program using LLM guidance based on extracted knowledge.

        This implements the key innovation from the MSA paper: using neural networks
        to guide the synthesis of symbolic probabilistic programs.

        Args:
            scenario: The scenario description
            knowledge_base: Extracted knowledge from Mode 1

        Returns:
            Generated probabilistic program and metadata
        """
        try:
            logger.info("Starting neurally-guided program synthesis...")

            # Extract key components for program synthesis
            entities = knowledge_base.get("entities", [])
            relationships = knowledge_base.get("relationships", [])
            causal_factors = knowledge_base.get("causal_factors", [])

            # Generate program structure using LLM
            program_structure = await self._generate_program_structure(
                scenario, entities, relationships, causal_factors
            )

            # Generate the actual NumPyro code
            program_code = await self._generate_numpyro_code(program_structure, scenario)

            # Generate prior specifications
            priors = await self._generate_priors(entities, scenario)

            # Generate observation model
            observation_model = await self._generate_observation_model(program_structure, relationships)

            result = {
                "program_structure": program_structure,
                "program_code": program_code,
                "priors": priors,
                "observation_model": observation_model,
                "synthesis_metadata": {
                    "entities_count": len(entities),
                    "relationships_count": len(relationships),
                    "causal_factors_count": len(causal_factors),
                    "synthesis_approach": "neurally_guided_msa",
                },
                "success": True,
            }

            logger.info("✅ Neurally-guided program synthesis completed")
            return result

        except Exception as e:
            logger.error(f"Failed to synthesize probabilistic program: {e}")
            return {"error": str(e), "program_structure": {}, "program_code": "", "success": False}

    async def _generate_program_structure(
        self, scenario: str, entities: List[Dict], relationships: List[Dict], causal_factors: List[Dict]
    ) -> Dict[str, Any]:
        """Generate the high-level structure of the probabilistic program"""

        prompt = f"""
        As an expert in probabilistic programming and causal modeling, analyze this scenario 
        and design a probabilistic program structure that can model the underlying causal relationships.
        
        Scenario: {scenario}
        
        Available Entities: {json.dumps(entities, indent=2)}
        Relationships: {json.dumps(relationships, indent=2)} 
        Causal Factors: {json.dumps(causal_factors, indent=2)}
        
        Design a probabilistic program structure that captures:
        1. Key variables and their types (continuous, discrete, categorical)
        2. Causal dependencies between variables  
        3. Uncertainty sources
        4. Observable vs latent variables
        
        Return a JSON structure with:
        {{
            "variables": [
                {{"name": "var_name", "type": "continuous/discrete/categorical", "role": "latent/observed", "description": "what it represents"}}
            ],
            "causal_graph": [
                {{"parent": "parent_var", "child": "child_var", "mechanism": "description_of_causal_mechanism"}}
            ],
            "uncertainties": [
                {{"variable": "var_name", "source": "epistemic/aleatory", "description": "uncertainty source"}}
            ],
            "model_type": "causal_model/decision_model/predictive_model"
        }}
        
        Provide only the JSON, no additional text.
        """

        try:
            result = await self.kernel_manager.invoke_prompt(prompt)
            program_structure = json.loads(result.strip())
            return program_structure
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Failed to generate program structure: {e}")
            return {"variables": [], "causal_graph": [], "uncertainties": [], "model_type": "generic"}

    async def _generate_numpyro_code(self, program_structure: Dict[str, Any], scenario: str) -> str:
        """Generate actual NumPyro code for the probabilistic program"""

        variables = program_structure.get("variables", [])
        causal_graph = program_structure.get("causal_graph", [])

        prompt = f"""
        Generate NumPyro code for a probabilistic program based on this structure.
        
        Scenario: {scenario}
        Variables: {json.dumps(variables, indent=2)}
        Causal Graph: {json.dumps(causal_graph, indent=2)}
        
        Generate a complete NumPyro model function that:
        1. Defines priors for all variables
        2. Implements causal relationships
        3. Handles observations
        4. Uses appropriate distributions
        
        Example format:
        ```python
        def model(observations=None):
            # Priors
            var1 = numpyro.sample("var1", dist.Normal(0, 1))
            
            # Causal relationships  
            var2 = numpyro.sample("var2", dist.Normal(var1 * 0.5, 0.2))
            
            # Observations
            if observations:
                numpyro.sample("obs", dist.Normal(var2, 0.1), obs=observations.get("obs"))
        ```
        
        Provide only the Python code, no additional text or markdown formatting.
        """

        try:
            result = await self.kernel_manager.invoke_prompt(prompt)
            # Clean the result to extract just the Python code
            code = result.strip()
            # Remove markdown formatting if present
            code = re.sub(r"^```python\n?", "", code, flags=re.MULTILINE)
            code = re.sub(r"\n?```$", "", code, flags=re.MULTILINE)
            return code
        except Exception as e:
            logger.warning(f"Failed to generate NumPyro code: {e}")
            return "def model():\n    pass  # Failed to generate model"

    async def _generate_priors(self, entities: List[Dict], scenario: str) -> Dict[str, Any]:
        """Generate informed priors based on domain knowledge"""

        prompt = f"""
        Based on this scenario and entities, suggest informed priors for probabilistic modeling.
        
        Scenario: {scenario}
        Entities: {json.dumps(entities, indent=2)}
        
        For each entity that could be a variable, suggest:
        1. Appropriate probability distribution
        2. Reasonable parameter values
        3. Justification based on domain knowledge
        
        Return JSON format:
        {{
            "variable_name": {{
                "distribution": "Normal/Beta/Gamma/etc",
                "parameters": {{"param1": value, "param2": value}},
                "justification": "why these priors make sense"
            }}
        }}
        
        Provide only the JSON, no additional text.
        """

        try:
            result = await self.kernel_manager.invoke_prompt(prompt)
            priors = json.loads(result.strip())
            return priors
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Failed to generate priors: {e}")
            return {}

    async def _generate_observation_model(
        self, program_structure: Dict[str, Any], relationships: List[Dict]
    ) -> Dict[str, Any]:
        """Generate observation model connecting latent variables to observables"""

        prompt = f"""
        Design an observation model that connects latent variables to observable quantities.
        
        Program Structure: {json.dumps(program_structure, indent=2)}
        Relationships: {json.dumps(relationships, indent=2)}
        
        Specify how latent variables manifest as observable measurements, considering:
        1. Measurement noise
        2. Observation biases
        3. Missing data patterns
        4. Multiple indicators per latent variable
        
        Return JSON format:
        {{
            "observations": [
                {{
                    "name": "observable_name",
                    "latent_variables": ["var1", "var2"],
                    "observation_function": "mathematical_description",
                    "noise_model": {{"distribution": "Normal", "parameters": {{"scale": 0.1}}}}
                }}
            ]
        }}
        
        Provide only the JSON, no additional text.
        """

        try:
            result = await self.kernel_manager.invoke_prompt(prompt)
            observation_model = json.loads(result.strip())
            return observation_model
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Failed to generate observation model: {e}")
            return {"observations": []}
