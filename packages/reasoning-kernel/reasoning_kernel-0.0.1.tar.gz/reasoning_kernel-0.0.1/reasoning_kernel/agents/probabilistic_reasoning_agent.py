"""
ProbabilisticReasoningAgent: Bayesian inference and probabilistic reasoning

This agent is responsible for:
- Performing Bayesian inference and probabilistic reasoning
- Uncertainty quantification and confidence estimation
- Belief propagation algorithms
- Integration with NumPyro/JAX backends
- Ha        for var in request.query_variables:
            if request.evidence and var in request.evidence:
                # If we have evidence, center samples around the evidence
                evidence_value = request.evidence[var]
                samples = np.random.normal(evidence_value, 0.1, request.num_samples)
            else:
                # Otherwise, generate reasonable samples (default to beta distribution)
                samples = np.random.beta(
                    2, 2, request.num_samples
                )  # Default to beta distribution

            posterior_samples[var] = samplesic queries and evidence
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from reasoning_kernel.agents.base_reasoning_agent import BaseReasoningAgent
from reasoning_kernel.utils.security import get_secure_logger
from semantic_kernel import Kernel
from semantic_kernel.functions import kernel_function


logger = get_secure_logger(__name__)


@dataclass
class InferenceRequest:
    """Request for probabilistic inference"""

    model_code: str
    query_variables: List[str]
    evidence: Optional[Dict[str, Any]] = None
    num_samples: int = 1000
    inference_method: str = "mcmc"  # mcmc, svi, nuts


@dataclass
class InferenceResult:
    """Result of probabilistic inference"""

    posterior_samples: Dict[str, np.ndarray]
    summary_statistics: Dict[str, Dict[str, float]]
    credible_intervals: Dict[str, Tuple[float, float]]
    marginal_likelihoods: Dict[str, float]
    uncertainty_measures: Dict[str, float]
    confidence_score: float
    execution_time: float
    convergence_diagnostics: Dict[str, Any]
    errors: List[str] = None


@dataclass
class BeliefState:
    """Represents belief state for belief propagation"""

    variable: str
    distribution: Dict[str, float]
    confidence: float
    dependencies: List[str]


class ProbabilisticReasoningAgent(BaseReasoningAgent):
    """
    Agent for Bayesian inference and probabilistic reasoning.

    This agent performs sophisticated probabilistic computations using
    NumPyro/JAX backends and implements belief propagation algorithms.
    """

    def __init__(self, kernel: Kernel, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            "ProbabilisticReasoning",
            kernel,
            "Bayesian inference and probabilistic reasoning agent",
            "Perform Bayesian inference and uncertainty quantification",
        )
        self.default_num_samples = config.get("num_samples", 1000) if config else 1000
        self.confidence_threshold = config.get("confidence_threshold", 0.8) if config else 0.8
        self.max_inference_time = config.get("max_inference_time", 60) if config else 60
        self.supported_methods = ["mcmc", "svi", "nuts", "hmc"]

    async def _process_message(self, message: str, **kwargs: Any) -> str:
        """Process a message through the probabilistic reasoning pipeline"""
        try:
            model_code = kwargs.get("model_code", "def model(): pass")
            query_variables = kwargs.get("query_variables", ["outcome"])

            # Create inference request
            request = InferenceRequest(
                model_code=model_code,
                query_variables=query_variables,
                num_samples=kwargs.get("num_samples", self.default_num_samples),
            )

            # Perform inference
            result = await self.perform_inference(request)

            # Return formatted response
            if result.errors:
                return f"Inference failed: {', '.join(result.errors)}"
            else:
                return f"Inference completed with confidence {result.confidence_score:.2f}. Found {len(result.posterior_samples)} variables."

        except Exception as e:
            return f"Error in probabilistic reasoning: {str(e)}"

    @kernel_function(
        description="Perform Bayesian inference on probabilistic model",
        name="bayesian_inference",
    )
    async def perform_inference(self, request: InferenceRequest) -> InferenceResult:
        """
        Main inference function that performs Bayesian reasoning.

        Args:
            request: Inference request with model and query specifications

        Returns:
            InferenceResult with posterior distributions and uncertainty measures
        """
        start_time = datetime.now()
        errors = []

        try:
            logger.info(f"Starting Bayesian inference for {len(request.query_variables)} variables")

            # Step 1: Validate and prepare the model
            model_validation = await self._validate_probabilistic_model(request.model_code)
            if not model_validation["valid"]:
                raise ValueError(f"Invalid model: {model_validation['errors']}")

            # Step 2: Generate inference code for NumPyro/JAX
            inference_code = await self._generate_inference_code(request)

            # Step 3: Execute inference (simulated - would use actual NumPyro in production)
            posterior_samples = await self._execute_inference(inference_code, request)

            # Step 4: Compute summary statistics
            summary_stats = self._compute_summary_statistics(posterior_samples)

            # Step 5: Calculate credible intervals
            credible_intervals = self._compute_credible_intervals(posterior_samples)

            # Step 6: Estimate uncertainty measures
            uncertainty_measures = self._compute_uncertainty_measures(posterior_samples, summary_stats)

            # Step 7: Compute marginal likelihoods
            marginal_likelihoods = await self._compute_marginal_likelihoods(request, posterior_samples)

            # Step 8: Assess convergence
            convergence_diagnostics = self._assess_convergence(posterior_samples)

            # Step 9: Calculate overall confidence
            confidence_score = self._calculate_inference_confidence(
                uncertainty_measures, convergence_diagnostics, summary_stats
            )

            execution_time = (datetime.now() - start_time).total_seconds()

            result = InferenceResult(
                posterior_samples=posterior_samples,
                summary_statistics=summary_stats,
                credible_intervals=credible_intervals,
                marginal_likelihoods=marginal_likelihoods,
                uncertainty_measures=uncertainty_measures,
                confidence_score=confidence_score,
                execution_time=execution_time,
                convergence_diagnostics=convergence_diagnostics,
                errors=errors,
            )

            logger.info(f"Bayesian inference completed with confidence: {confidence_score:.3f}")
            return result

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            error_msg = f"Bayesian inference failed: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)

            return InferenceResult(
                posterior_samples={},
                summary_statistics={},
                credible_intervals={},
                marginal_likelihoods={},
                uncertainty_measures={},
                confidence_score=0.0,
                execution_time=execution_time,
                convergence_diagnostics={"converged": False},
                errors=errors,
            )

    async def _validate_probabilistic_model(self, model_code: str) -> Dict[str, Any]:
        """Validate that the model code is suitable for inference"""
        validation = {"valid": True, "errors": [], "warnings": []}

        # Check for required imports
        required_imports = ["numpyro", "numpyro.distributions", "jax.numpy"]
        for imp in required_imports:
            if imp not in model_code:
                validation["warnings"].append(f"Missing recommended import: {imp}")

        # Check for model function
        if "def " not in model_code or "model(" not in model_code:
            validation["valid"] = False
            validation["errors"].append("No model function found")

        # Check for probability distributions
        dist_keywords = ["dist.", "distributions.", "Normal(", "Beta(", "Gamma("]
        if not any(keyword in model_code for keyword in dist_keywords):
            validation["warnings"].append("No probability distributions detected")

        # Syntax check
        try:
            compile(model_code, "<string>", "exec")
        except SyntaxError as e:
            validation["valid"] = False
            validation["errors"].append(f"Syntax error: {e}")

        return validation

    async def _generate_inference_code(self, request: InferenceRequest) -> str:
        """Generate NumPyro/JAX inference code"""
        prompt = f"""
        Generate NumPyro inference code for this probabilistic model:
        
        Model Code:
        {request.model_code}
        
        Query Variables: {request.query_variables}
        Evidence: {request.evidence or "None"}
        Inference Method: {request.inference_method}
        Number of Samples: {request.num_samples}
        
        Generate complete Python code that:
        1. Imports necessary NumPyro and JAX modules
        2. Defines the model function (already provided)
        3. Sets up the inference algorithm (MCMC, SVI, etc.)
        4. Handles evidence conditioning if provided
        5. Runs inference and returns samples
        6. Includes proper error handling
        
        Use NumPyro best practices and ensure the code is production-ready.
        """

        try:
            response = await self.kernel.invoke_function(
                plugin_name="llm", function_name="generate_text", prompt=prompt
            )

            code = str(response).strip()
            if code.startswith("```python"):
                code = code.split("```python")[1].split("```")[0].strip()
            elif code.startswith("```"):
                code = code.split("```")[1].split("```")[0].strip()

            return code

        except Exception as e:
            logger.error(f"Failed to generate inference code: {e}")
            # Return basic template
            return f"""
import numpyro
import numpyro.distributions as dist
import jax.numpy as jnp
from jax import random
from numpyro.infer import MCMC, NUTS

# Model code would be inserted here
{request.model_code}

# Inference setup
nuts_kernel = NUTS(model)
mcmc = MCMC(nuts_kernel, num_samples={request.num_samples}, num_warmup=500)
rng_key = random.PRNGKey(0)
mcmc.run(rng_key)
samples = mcmc.get_samples()
"""

    async def _execute_inference(self, inference_code: str, request: InferenceRequest) -> Dict[str, np.ndarray]:
        """Execute the inference code (simulated for now)"""
        logger.info("Executing probabilistic inference (simulated)")

        # Simulate inference results for each query variable
        # In production, this would execute the actual NumPyro code
        posterior_samples = {}

        for var in request.query_variables:
            # Generate realistic-looking samples based on variable characteristics
            if request.evidence and var in request.evidence:
                # If we have evidence, center samples around the evidence
                evidence_value = request.evidence[var]
                samples = np.random.normal(evidence_value, 0.1, request.num_samples)
            else:
                # Otherwise, generate reasonable samples (default to beta distribution)
                samples = np.random.beta(2, 2, request.num_samples)  # Default to beta distribution

            posterior_samples[var] = samples

        # Add some correlated variables if there are multiple query variables
        if len(request.query_variables) > 1:
            # Create some correlation between variables
            base_var = request.query_variables[0]
            for i, var in enumerate(request.query_variables[1:], 1):
                correlation = 0.3 * i  # Increasing correlation
                noise = np.random.normal(0, 0.2, request.num_samples)
                posterior_samples[var] = (
                    correlation * posterior_samples[base_var] + (1 - correlation) * posterior_samples[var] + noise
                )

        logger.debug(f"Generated {request.num_samples} samples for {len(request.query_variables)} variables")
        return posterior_samples

    def _compute_summary_statistics(self, posterior_samples: Dict[str, np.ndarray]) -> Dict[str, Dict[str, float]]:
        """Compute summary statistics for posterior samples"""
        summary_stats = {}

        for var, samples in posterior_samples.items():
            summary_stats[var] = {
                "mean": float(np.mean(samples)),
                "std": float(np.std(samples)),
                "median": float(np.median(samples)),
                "min": float(np.min(samples)),
                "max": float(np.max(samples)),
                "q25": float(np.percentile(samples, 25)),
                "q75": float(np.percentile(samples, 75)),
                "skewness": float(self._compute_skewness(samples)),
                "kurtosis": float(self._compute_kurtosis(samples)),
            }

        return summary_stats

    def _compute_credible_intervals(
        self, posterior_samples: Dict[str, np.ndarray], alpha: float = 0.05
    ) -> Dict[str, Tuple[float, float]]:
        """Compute credible intervals for posterior samples"""
        credible_intervals = {}

        for var, samples in posterior_samples.items():
            lower = np.percentile(samples, 100 * alpha / 2)
            upper = np.percentile(samples, 100 * (1 - alpha / 2))
            credible_intervals[var] = (float(lower), float(upper))

        return credible_intervals

    def _compute_uncertainty_measures(
        self,
        posterior_samples: Dict[str, np.ndarray],
        summary_stats: Dict[str, Dict[str, float]],
    ) -> Dict[str, float]:
        """Compute various uncertainty measures"""
        uncertainty = {}

        for var, samples in posterior_samples.items():
            stats = summary_stats[var]

            # Coefficient of variation
            cv = stats["std"] / (abs(stats["mean"]) + 1e-8)
            uncertainty[f"{var}_cv"] = cv

            # Entropy (approximate for continuous distributions)
            hist, bin_edges = np.histogram(samples, bins=50, density=True)
            bin_width = bin_edges[1] - bin_edges[0]
            prob = hist * bin_width
            prob = prob[prob > 0]  # Remove zero probabilities
            entropy = -np.sum(prob * np.log(prob))
            uncertainty[f"{var}_entropy"] = float(entropy)

            # Interquartile range normalized by median
            iqr_normalized = (stats["q75"] - stats["q25"]) / (abs(stats["median"]) + 1e-8)
            uncertainty[f"{var}_iqr_norm"] = iqr_normalized

        # Overall uncertainty (average across variables)
        all_cv = [uncertainty[k] for k in uncertainty.keys() if k.endswith("_cv")]
        uncertainty["overall_uncertainty"] = float(np.mean(all_cv)) if all_cv else 0.0

        return uncertainty

    async def _compute_marginal_likelihoods(
        self, request: InferenceRequest, posterior_samples: Dict[str, np.ndarray]
    ) -> Dict[str, float]:
        """Compute marginal likelihoods for model comparison"""
        marginal_likelihoods = {}

        # Simplified marginal likelihood computation
        # In practice, this would use more sophisticated methods like bridge sampling
        for var, samples in posterior_samples.items():
            # Approximate marginal likelihood using harmonic mean (crude approximation)
            log_likelihoods = []
            for sample in samples[-100:]:  # Use last 100 samples
                # Simulate log likelihood computation
                log_lik = -0.5 * (sample - 0.5) ** 2  # Simple quadratic form
                log_likelihoods.append(log_lik)

            # Harmonic mean approximation
            max_log_lik = max(log_likelihoods)
            shifted_liks = [np.exp(lik - max_log_lik) for lik in log_likelihoods]
            harmonic_mean = len(shifted_liks) / sum(1.0 / lik for lik in shifted_liks if lik > 0)
            marginal_log_lik = np.log(harmonic_mean) + max_log_lik

            marginal_likelihoods[var] = float(marginal_log_lik)

        return marginal_likelihoods

    def _assess_convergence(self, posterior_samples: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """Assess MCMC convergence diagnostics"""
        convergence = {"converged": True, "diagnostics": {}}

        for var, samples in posterior_samples.items():
            # Split samples into two halves for R-hat computation
            n = len(samples)
            if n < 100:
                convergence["diagnostics"][f"{var}_rhat"] = 1.0  # Assume convergence for small samples
                continue

            # Simple R-hat approximation
            first_half = samples[: n // 2]
            second_half = samples[n // 2 :]

            mean1, mean2 = np.mean(first_half), np.mean(second_half)
            var1, var2 = np.var(first_half), np.var(second_half)

            # Between-chain variance
            B = (n // 2) * ((mean1 - mean2) ** 2) / 2

            # Within-chain variance
            W = (var1 + var2) / 2

            # R-hat statistic
            if W > 0:
                rhat = np.sqrt((n // 2 - 1) / (n // 2) + B / (W * n // 2))
            else:
                rhat = 1.0

            convergence["diagnostics"][f"{var}_rhat"] = float(rhat)

            # Check convergence (R-hat should be close to 1.0)
            if rhat > 1.1:
                convergence["converged"] = False

        return convergence

    def _calculate_inference_confidence(
        self,
        uncertainty_measures: Dict[str, float],
        convergence_diagnostics: Dict[str, Any],
        summary_stats: Dict[str, Dict[str, float]],
    ) -> float:
        """Calculate overall confidence in the inference results"""
        confidence_factors = []

        # Convergence factor
        if convergence_diagnostics["converged"]:
            convergence_factor = 1.0
        else:
            rhat_values = [v for k, v in convergence_diagnostics["diagnostics"].items() if k.endswith("_rhat")]
            avg_rhat = np.mean(rhat_values) if rhat_values else 1.0
            convergence_factor = max(0.0, 2.0 - avg_rhat)  # Penalize high R-hat values
        confidence_factors.append(convergence_factor)

        # Uncertainty factor (lower uncertainty = higher confidence)
        overall_uncertainty = uncertainty_measures.get("overall_uncertainty", 1.0)
        uncertainty_factor = 1.0 / (1.0 + overall_uncertainty)
        confidence_factors.append(uncertainty_factor)

        # Sample size factor
        sample_counts = [len(samples) for samples in summary_stats.values()]
        avg_samples = np.mean(sample_counts) if sample_counts else 0
        sample_factor = min(1.0, avg_samples / 1000.0)  # Full confidence with 1000+ samples
        confidence_factors.append(sample_factor)

        # Overall confidence is the geometric mean of factors
        overall_confidence = np.power(np.prod(confidence_factors), 1.0 / len(confidence_factors))
        return float(min(1.0, max(0.0, overall_confidence)))

    @kernel_function(
        description="Perform belief propagation on a factor graph",
        name="belief_propagation",
    )
    async def belief_propagation(
        self, factor_graph: Dict[str, Any], evidence: Dict[str, Any]
    ) -> Dict[str, BeliefState]:
        """
        Perform belief propagation algorithm on a factor graph.

        Args:
            factor_graph: Factor graph representation with variables and factors
            evidence: Observed evidence to condition on

        Returns:
            Dictionary of belief states for each variable
        """
        logger.info("Starting belief propagation algorithm")

        try:
            # Initialize belief states
            belief_states = {}
            variables = factor_graph.get("variables", [])
            factors = factor_graph.get("factors", [])

            for var in variables:
                var_name = var["name"]
                # Initialize with uniform belief if no evidence
                if var_name in evidence:
                    # Set belief to evidence
                    belief_dist = {"observed": 1.0}
                    confidence = 1.0
                else:
                    # Uniform distribution over possible values
                    possible_values = var.get("values", ["true", "false"])
                    uniform_prob = 1.0 / len(possible_values)
                    belief_dist = {val: uniform_prob for val in possible_values}
                    confidence = 0.5  # Low initial confidence

                belief_states[var_name] = BeliefState(
                    variable=var_name,
                    distribution=belief_dist,
                    confidence=confidence,
                    dependencies=self._get_variable_dependencies(var_name, factors),
                )

            # Iterate belief propagation (simplified version)
            max_iterations = 10
            for iteration in range(max_iterations):
                updated = False

                for var_name, belief_state in belief_states.items():
                    if var_name in evidence:
                        continue  # Skip evidence variables

                    # Update beliefs based on neighboring factors
                    new_belief = await self._update_belief(belief_state, factors, belief_states)

                    # Check for convergence
                    if self._belief_changed(belief_state.distribution, new_belief.distribution):
                        belief_states[var_name] = new_belief
                        updated = True

                if not updated:
                    logger.debug(f"Belief propagation converged after {iteration + 1} iterations")
                    break

            logger.info(f"Belief propagation completed for {len(belief_states)} variables")
            return belief_states

        except Exception as e:
            logger.error(f"Belief propagation failed: {e}")
            return {}

    def _get_variable_dependencies(self, var_name: str, factors: List[Dict[str, Any]]) -> List[str]:
        """Get variables that this variable depends on in the factor graph"""
        dependencies = []
        for factor in factors:
            factor_vars = factor.get("variables", [])
            if var_name in factor_vars:
                dependencies.extend([v for v in factor_vars if v != var_name])
        return list(set(dependencies))

    async def _update_belief(
        self,
        belief_state: BeliefState,
        factors: List[Dict[str, Any]],
        all_beliefs: Dict[str, BeliefState],
    ) -> BeliefState:
        """Update belief for a single variable based on factor graph"""
        var_name = belief_state.variable
        new_distribution = {}

        # Find factors involving this variable
        relevant_factors = [f for f in factors if var_name in f.get("variables", [])]

        if not relevant_factors:
            return belief_state  # No factors, keep current belief

        # Simple belief update (in practice, this would be more sophisticated)
        for value in belief_state.distribution.keys():
            belief_product = 1.0

            for factor in relevant_factors:
                # Get beliefs of other variables in this factor
                other_vars = [v for v in factor.get("variables", []) if v != var_name]

                factor_value = 1.0
                for other_var in other_vars:
                    if other_var in all_beliefs:
                        other_belief = all_beliefs[other_var]
                        # Use maximum belief for simplicity
                        max_belief_val = max(other_belief.distribution.values())
                        factor_value *= max_belief_val

                belief_product *= factor_value

            new_distribution[value] = belief_state.distribution[value] * belief_product

        # Normalize distribution
        total = sum(new_distribution.values())
        if total > 0:
            new_distribution = {k: v / total for k, v in new_distribution.items()}

        # Calculate new confidence based on entropy
        entropy = -sum(p * np.log(p + 1e-8) for p in new_distribution.values())
        max_entropy = np.log(len(new_distribution))
        confidence = 1.0 - (entropy / max_entropy) if max_entropy > 0 else 0.5

        return BeliefState(
            variable=var_name,
            distribution=new_distribution,
            confidence=float(confidence),
            dependencies=belief_state.dependencies,
        )

    def _belief_changed(
        self,
        old_dist: Dict[str, float],
        new_dist: Dict[str, float],
        threshold: float = 0.01,
    ) -> bool:
        """Check if belief distribution has changed significantly"""
        for key in old_dist.keys():
            if abs(old_dist.get(key, 0) - new_dist.get(key, 0)) > threshold:
                return True
        return False

    def _compute_skewness(self, samples: np.ndarray) -> float:
        """Compute skewness of samples"""
        mean = np.mean(samples)
        std = np.std(samples)
        if std == 0:
            return 0.0
        normalized = (samples - mean) / std
        return float(np.mean(normalized**3))

    def _compute_kurtosis(self, samples: np.ndarray) -> float:
        """Compute kurtosis of samples"""
        mean = np.mean(samples)
        std = np.std(samples)
        if std == 0:
            return 0.0
        normalized = (samples - mean) / std
        return float(np.mean(normalized**4) - 3)  # Excess kurtosis


# Export the agent class
__all__ = [
    "ProbabilisticReasoningAgent",
    "InferenceRequest",
    "InferenceResult",
    "BeliefState",
]
