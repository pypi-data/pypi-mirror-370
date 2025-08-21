"""
ModelSynthesisAgent: Probabilistic program synthesis and graph representation

This agent is responsible for:
- Generating probabilistic programs from scenario descriptions
- Building graph representations of causal relationships
- Parameter inference from sparse data
- Integration with Gemini 2.5 Pro for code generation
- Validation and error handling of synthesized models
"""

from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
import json
from typing import Any, Dict, List, Optional

from reasoning_kernel.agents.base_reasoning_agent import BaseReasoningAgent
from reasoning_kernel.utils.security import get_secure_logger
from semantic_kernel import Kernel
from semantic_kernel.functions import kernel_function


logger = get_secure_logger(__name__)


@dataclass
class CausalGraph:
    """Simple causal graph representation for model synthesis"""

    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]


@dataclass
class SynthesisRequest:
    """Request for model synthesis"""

    scenario: str
    knowledge_base: Dict[str, Any]
    constraints: Optional[Dict[str, Any]] = None
    target_variables: Optional[List[str]] = None
    evidence: Optional[Dict[str, Any]] = None


@dataclass
class SynthesisResult:
    """Result of model synthesis"""

    program_code: str
    causal_graph: CausalGraph
    parameters: Dict[str, Any]
    confidence: float
    validation_results: Dict[str, Any]
    execution_time: float
    success: bool = True
    errors: List[str] = field(default_factory=list)


class ModelSynthesisAgent(BaseReasoningAgent):
    """
    Agent for probabilistic program synthesis and graph representation.

    This agent uses Gemini 2.5 Pro to generate probabilistic programs
    and builds causal graph representations for reasoning scenarios.
    """

    def __init__(self, kernel: Kernel, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            "ModelSynthesis",
            kernel,
            "Probabilistic model synthesis agent",
            "Generate probabilistic programs from scenario descriptions",
        )
        self.synthesis_templates = self._load_synthesis_templates()
        self.validation_rules = self._load_validation_rules()
        self.max_iterations = config.get("max_iterations", 5) if config else 5
        self.confidence_threshold = config.get("confidence_threshold", 0.7) if config else 0.7

    async def _process_message(self, message: str, **kwargs: Any) -> str:
        """Process a message through the model synthesis pipeline"""
        try:
            # Create a synthesis request from the message
            request = SynthesisRequest(
                scenario=message,
                knowledge_base=kwargs.get("knowledge_base", {}),
                constraints=kwargs.get("constraints"),
                target_variables=kwargs.get("target_variables"),
                evidence=kwargs.get("evidence"),
            )

            # Perform synthesis
            result = await self.synthesize_model(request)

            # Return formatted response
            if result.errors:
                return f"Synthesis failed: {', '.join(result.errors)}"
            else:
                return f"Model synthesized with confidence {result.confidence:.2f}. Program code: {result.program_code[:200]}..."

        except Exception as e:
            return f"Error in model synthesis: {str(e)}"

    def _load_synthesis_templates(self) -> Dict[str, str]:
        """Load probabilistic program synthesis templates"""
        return {
            "bayesian_network": """
# Bayesian Network Model for: {scenario_title}
# Generated on: {timestamp}
# Variables: {variables}

import numpyro
import numpyro.distributions as dist
import jax.numpy as jnp
from jax import random

def model(data=None):
    # Prior distributions
{priors}
    
    # Conditional dependencies
{conditionals}
    
    # Observations
{observations}
    
    return return_variables
""",
            "probabilistic_program": """
# Probabilistic Program for: {scenario_title}
# Generated on: {timestamp}

import numpyro
import numpyro.distributions as dist
import jax.numpy as jnp
from jax import random

def probabilistic_model({parameters}):
    # Model structure
{model_body}
    
    # Return sampled values
    return {return_dict}
""",
            "causal_model": """
# Causal Model for: {scenario_title}
# Generated on: {timestamp}

import numpyro
import numpyro.distributions as dist
import jax.numpy as jnp

def causal_model(do_intervention=None):
    # Exogenous variables
{exogenous}
    
    # Structural equations
{structural_equations}
    
    # Interventions
    if do_intervention:
{interventions}
    
    return {causal_variables}
""",
        }

    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load validation rules for synthesized models"""
        return {
            "syntax_checks": [
                "valid_python_syntax",
                "numpyro_imports_present",
                "model_function_defined",
            ],
            "semantic_checks": [
                "variables_defined_before_use",
                "distributions_properly_parameterized",
                "return_statement_present",
            ],
            "performance_checks": [
                "max_variables_limit",
                "computational_complexity_acceptable",
            ],
        }

    @kernel_function(
        description="Synthesize probabilistic program from scenario and knowledge",
        name="synthesize_probabilistic_program",
    )
    async def synthesize_model(self, request: SynthesisRequest) -> SynthesisResult:
        """
        Main synthesis function that generates probabilistic programs.

        Args:
            request: Synthesis request with scenario and knowledge base

        Returns:
            SynthesisResult with generated program and validation results
        """
        start_time = datetime.now()
        errors = []

        try:
            logger.info(f"Starting model synthesis for scenario: {request.scenario[:100]}...")

            # Step 1: Analyze scenario and extract variables
            variables = await self._extract_variables(request.scenario, request.knowledge_base)
            logger.debug(f"Extracted variables: {list(variables.keys())}")

            # Step 2: Build causal graph structure
            causal_graph = await self._build_causal_graph(variables, request.knowledge_base)
            logger.debug(f"Built causal graph with {len(causal_graph.nodes)} nodes")

            # Step 3: Generate probabilistic program
            program_code = await self._generate_program_code(variables, causal_graph, request)

            # Step 4: Perform parameter inference
            parameters = await self._infer_parameters(variables, causal_graph, request.evidence)

            # Step 5: Validate the synthesized model
            validation_results = await self._validate_model(program_code, variables)

            # Step 6: Calculate confidence score
            confidence = self._calculate_confidence(validation_results, variables, causal_graph)

            execution_time = (datetime.now() - start_time).total_seconds()

            result = SynthesisResult(
                program_code=program_code,
                causal_graph=causal_graph,
                parameters=parameters,
                confidence=confidence,
                validation_results=validation_results,
                execution_time=execution_time,
                errors=errors,
            )

            logger.info(f"Model synthesis completed with confidence: {confidence:.3f}")
            return result

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            error_msg = f"Model synthesis failed: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)

            return SynthesisResult(
                program_code="# Synthesis failed",
                causal_graph=CausalGraph(nodes=[], edges=[]),
                parameters={},
                confidence=0.0,
                validation_results={"success": False, "errors": errors},
                execution_time=execution_time,
                success=False,
                errors=errors,
            )

    async def _extract_variables(self, scenario: str, knowledge_base: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Extract variables and their properties from scenario"""
        prompt = f"""
        Analyze this scenario and extract all variables that should be modeled probabilistically:
        
        Scenario: {scenario}
        
        Knowledge Base Context: {json.dumps(knowledge_base, indent=2)}
        
        For each variable, determine:
        1. Variable name (valid Python identifier)
        2. Variable type (continuous, discrete, categorical)
        3. Possible values or range
        4. Dependencies on other variables
        5. Prior knowledge or constraints
        
        Return as JSON with this structure:
        {{
            "variable_name": {{
                "type": "continuous|discrete|categorical",
                "range": [min, max] or ["option1", "option2"],
                "dependencies": ["var1", "var2"],
                "description": "brief description",
                "prior": "suggested prior distribution"
            }}
        }}
        """

        try:
            response = await self.kernel.invoke_function(
                plugin_name="llm", function_name="generate_text", prompt=prompt
            )

            # Parse JSON response
            variables_text = str(response).strip()
            if variables_text.startswith("```json"):
                variables_text = variables_text.split("```json")[1].split("```")[0].strip()
            elif variables_text.startswith("```"):
                variables_text = variables_text.split("```")[1].split("```")[0].strip()

            variables = json.loads(variables_text)
            return variables

        except Exception as e:
            logger.error(f"Failed to extract variables: {e}")
            # Return default structure
            return {
                "outcome": {
                    "type": "continuous",
                    "range": [0, 1],
                    "dependencies": [],
                    "description": "Default outcome variable",
                    "prior": "Beta(1, 1)",
                }
            }

    async def _build_causal_graph(self, variables: Dict[str, Any], knowledge_base: Dict[str, Any]) -> CausalGraph:
        """Build causal graph representation"""
        nodes = []
        edges = []

        # Create nodes for each variable
        for var_name, var_info in variables.items():
            nodes.append(
                {
                    "id": var_name,
                    "name": var_info.get("description", var_name),
                    "type": var_info.get("type", "continuous"),
                    "range": var_info.get("range", [0, 1]),
                }
            )

        # Create edges based on dependencies
        for var_name, var_info in variables.items():
            for dependency in var_info.get("dependencies", []):
                if dependency in variables:
                    edges.append(
                        {
                            "from": dependency,
                            "to": var_name,
                            "strength": 0.7,  # Default strength
                            "type": "causal",
                        }
                    )

        return CausalGraph(nodes=nodes, edges=edges)

    async def _generate_program_code(
        self,
        variables: Dict[str, Any],
        causal_graph: CausalGraph,
        request: SynthesisRequest,
    ) -> str:
        """Generate probabilistic program code using Gemini 2.5 Pro"""
        prompt = f"""
        Generate a NumPyro probabilistic program for this scenario:
        
        Scenario: {request.scenario}
        
        Variables: {json.dumps(variables, indent=2)}
        
        Causal Graph: 
        Nodes: {causal_graph.nodes}
        Edges: {causal_graph.edges}
        
        Generate a complete NumPyro model function that:
        1. Defines prior distributions for all variables
        2. Implements the causal relationships from the graph
        3. Includes proper parameterization
        4. Handles any evidence or constraints
        5. Returns a dictionary of all variables
        
        Use the template structure but adapt it to this specific scenario.
        Make sure the code is syntactically correct and follows NumPyro best practices.
        """

        try:
            response = await self.kernel.invoke_function(
                plugin_name="llm", function_name="generate_text", prompt=prompt
            )

            code = str(response).strip()

            # Clean up code if wrapped in markdown
            if code.startswith("```python"):
                code = code.split("```python")[1].split("```")[0].strip()
            elif code.startswith("```"):
                code = code.split("```")[1].split("```")[0].strip()

            return code

        except Exception as e:
            logger.error(f"Failed to generate program code: {e}")
            # Return basic template
            template = self.synthesis_templates["probabilistic_program"]
            return template.format(
                scenario_title=request.scenario[:50],
                timestamp=datetime.now().isoformat(),
                parameters=", ".join(variables.keys()),
                model_body="    # Generated model structure\n    pass",
                return_dict="{" + ", ".join(f'"{k}": {k}' for k in variables.keys()) + "}",
            )

    async def _infer_parameters(
        self,
        variables: Dict[str, Any],
        causal_graph: CausalGraph,
        evidence: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Infer parameters from sparse data and evidence"""
        parameters = {}

        # Default parameter inference based on variable types
        for var_name, var_info in variables.items():
            var_type = var_info.get("type", "continuous")

            if var_type == "continuous":
                # Use evidence if available, otherwise reasonable defaults
                if evidence and var_name in evidence:
                    obs_value = evidence[var_name]
                    parameters[f"{var_name}_mean"] = obs_value
                    parameters[f"{var_name}_std"] = abs(obs_value * 0.1)  # 10% relative std
                else:
                    var_range = var_info.get("range", [0, 1])
                    parameters[f"{var_name}_mean"] = (var_range[0] + var_range[1]) / 2
                    parameters[f"{var_name}_std"] = (var_range[1] - var_range[0]) / 6  # 3-sigma rule

            elif var_type == "discrete":
                var_range = var_info.get("range", [0, 10])
                parameters[f"{var_name}_rate"] = (var_range[0] + var_range[1]) / 2

            elif var_type == "categorical":
                options = var_info.get("range", ["option1", "option2"])
                # Uniform priors
                parameters[f"{var_name}_probs"] = [1.0 / len(options)] * len(options)

        logger.debug(f"Inferred parameters: {parameters}")
        return parameters

    async def _validate_model(self, program_code: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the synthesized probabilistic model"""
        validation_results = {
            "success": True,
            "errors": [],
            "warnings": [],
            "checks": {},
        }

        # Syntax validation
        try:
            compile(program_code, "<string>", "exec")
            validation_results["checks"]["syntax"] = True
        except SyntaxError as e:
            validation_results["success"] = False
            validation_results["errors"].append(f"Syntax error: {e}")
            validation_results["checks"]["syntax"] = False

        # Check for required imports
        required_imports = ["numpyro", "numpyro.distributions", "jax.numpy"]
        for imp in required_imports:
            if imp in program_code:
                validation_results["checks"][f"import_{imp.replace('.', '_')}"] = True
            else:
                validation_results["warnings"].append(f"Missing import: {imp}")
                validation_results["checks"][f"import_{imp.replace('.', '_')}"] = False

        # Check for model function
        if "def " in program_code and ("model(" in program_code or "probabilistic_model(" in program_code):
            validation_results["checks"]["model_function"] = True
        else:
            validation_results["errors"].append("No model function found")
            validation_results["checks"]["model_function"] = False
            validation_results["success"] = False

        # Check variable coverage
        for var_name in variables.keys():
            if var_name in program_code:
                validation_results["checks"][f"variable_{var_name}"] = True
            else:
                validation_results["warnings"].append(f"Variable {var_name} not found in code")
                validation_results["checks"][f"variable_{var_name}"] = False

        return validation_results

    def _calculate_confidence(
        self,
        validation_results: Dict[str, Any],
        variables: Dict[str, Any],
        causal_graph: CausalGraph,
    ) -> float:
        """Calculate confidence score for the synthesized model"""
        base_confidence = 1.0

        # Reduce confidence for validation errors
        if not validation_results["success"]:
            base_confidence -= 0.5

        # Reduce confidence for missing checks
        checks = validation_results.get("checks", {})
        failed_checks = sum(1 for check in checks.values() if not check)
        total_checks = len(checks) if checks else 1
        check_ratio = 1.0 - (failed_checks / total_checks)

        # Factor in model complexity
        complexity_factor = min(1.0, 1.0 / (len(variables) * 0.1))  # Simpler models get higher confidence

        # Factor in causal graph connectivity
        edge_count = len(causal_graph.edges)
        node_count = len(causal_graph.nodes)
        connectivity = edge_count / max(node_count, 1)
        connectivity_factor = min(1.0, connectivity / 2.0)  # Well-connected graphs get higher confidence

        final_confidence = base_confidence * check_ratio * complexity_factor * connectivity_factor
        return max(0.0, min(1.0, final_confidence))

    @kernel_function(
        description="Refine an existing probabilistic model based on feedback",
        name="refine_model",
    )
    async def refine_model(self, original_result: SynthesisResult, feedback: Dict[str, Any]) -> SynthesisResult:
        """Refine a previously synthesized model based on feedback"""
        logger.info("Refining probabilistic model based on feedback")

        try:
            # Create refinement request
            refinement_prompt = f"""
            Refine this probabilistic program based on the feedback:
            
            Original Code:
            {original_result.program_code}
            
            Feedback: {json.dumps(feedback, indent=2)}
            
            Validation Issues: {original_result.validation_results}
            
            Please fix any issues and improve the model while maintaining its core structure.
            """

            response = await self.kernel.invoke_function(
                plugin_name="llm",
                function_name="generate_text",
                prompt=refinement_prompt,
            )

            refined_code = str(response).strip()
            if refined_code.startswith("```python"):
                refined_code = refined_code.split("```python")[1].split("```")[0].strip()
            elif refined_code.startswith("```"):
                refined_code = refined_code.split("```")[1].split("```")[0].strip()

            # Create refined result
            refined_result = SynthesisResult(
                program_code=refined_code,
                causal_graph=original_result.causal_graph,
                parameters=original_result.parameters,
                confidence=min(original_result.confidence + 0.1, 1.0),  # Slight boost for refinement
                validation_results=await self._validate_model(refined_code, {}),
                execution_time=0.0,
                errors=[],
            )

            logger.info("Model refinement completed")
            return refined_result

        except Exception as e:
            logger.error(f"Model refinement failed: {e}")
            return original_result


# Export the agent class
__all__ = ["ModelSynthesisAgent", "SynthesisRequest", "SynthesisResult"]
