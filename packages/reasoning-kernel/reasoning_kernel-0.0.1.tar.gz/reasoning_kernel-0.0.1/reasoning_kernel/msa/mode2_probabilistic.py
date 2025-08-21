"""
Mode 2: Dynamic probabilistic model synthesis using NumPyro
This mode acts as the "logical planner" building custom models for inference
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
from typing import Any, Dict, List

import jax
import jax.numpy as jnp
import numpy as np
import numpyro
import numpyro.distributions as dist
from numpyro.handlers import seed
from numpyro.infer import MCMC
from numpyro.infer import NUTS
from numpyro.infer import Predictive
from reasoning_kernel.core.config import settings


logger = logging.getLogger(__name__)


class ProbabilisticModelSynthesizer:
    """Mode 2 of MSA - Dynamic probabilistic model synthesis"""

    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.models_cache = {}

    async def synthesize_model(self, specifications: Dict[str, Any], scenario_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesize a probabilistic model based on specifications from Mode 1

        Args:
            specifications: Model specifications from knowledge extraction
            scenario_data: Additional data about the scenario

        Returns:
            Synthesized model results and inferences
        """
        try:
            logger.info("Synthesizing probabilistic model...")

            # Extract model components
            variables = specifications.get("variables", [])
            dependencies = specifications.get("dependencies", [])
            uncertainties = specifications.get("uncertainties", [])
            model_type = specifications.get("model_type", "generic_bayesian")

            # Create model structure
            model_structure = await self._create_model_structure(variables, dependencies, uncertainties)

            # Generate synthetic model if no data provided
            if not scenario_data.get("observations"):
                scenario_data = await self._generate_scenario_data(model_structure)

            # Run inference
            inference_results = await self._run_inference(model_structure, scenario_data)

            # Generate predictions
            predictions = await self._generate_predictions(model_structure, inference_results, scenario_data)

            # Calculate uncertainty measures
            uncertainty_analysis = await self._analyze_uncertainty(inference_results, predictions)

            result = {
                "model_structure": model_structure,
                "inference_results": inference_results,
                "predictions": predictions,
                "uncertainty_analysis": uncertainty_analysis,
                "model_type": model_type,
                "success": True,
            }

            logger.info("Probabilistic model synthesis completed successfully")
            return result

        except Exception as e:
            logger.error(f"Failed to synthesize probabilistic model: {e}")
            return {
                "error": str(e),
                "model_structure": {},
                "inference_results": {},
                "predictions": {},
                "uncertainty_analysis": {},
                "success": False,
            }

    async def _create_model_structure(
        self, variables: List[Dict], dependencies: List[Dict], uncertainties: List[Dict]
    ) -> Dict[str, Any]:
        """Create the structure of the probabilistic model"""

        def create_model():
            """NumPyro model definition"""
            var_samples = {}

            # Create variables based on specifications
            for var in variables:
                var_name = var.get("name", f"var_{len(var_samples)}")
                var_type = var.get("type", "continuous")

                if var_type == "continuous":
                    # Use normal distribution as default for continuous variables
                    var_samples[var_name] = numpyro.sample(var_name, dist.Normal(0.0, 1.0))
                elif var_type == "discrete":
                    # Use Poisson for discrete variables
                    var_samples[var_name] = numpyro.sample(var_name, dist.Poisson(2.0))
                elif var_type == "categorical":
                    # Use Beta distribution as a simpler alternative for categorical-like behavior
                    var_samples[var_name] = numpyro.sample(var_name, dist.Beta(1.0, 1.0))

            # Add dependencies between variables
            for dep in dependencies:
                parent = dep.get("parent")
                child = dep.get("child")

                if parent in var_samples and child and child not in var_samples:
                    # Create dependent variable
                    parent_val = var_samples[parent]
                    var_samples[child] = numpyro.sample(child, dist.Normal(parent_val * 0.5, 0.3))

            return var_samples

        # Run model structure creation in thread pool
        loop = asyncio.get_event_loop()
        model_structure = await loop.run_in_executor(
            self.executor,
            lambda: {
                "variables": variables,
                "dependencies": dependencies,
                "uncertainties": uncertainties,
                "model_function": create_model,
            },
        )

        return model_structure

    async def _generate_scenario_data(self, model_structure: Dict[str, Any]) -> Dict[str, Any]:
        """Generate synthetic data for the scenario when no observations are provided"""

        def generate_data():
            model_fn = model_structure["model_function"]

            # Generate prior samples
            rng_key = jax.random.PRNGKey(42)
            prior_samples = {}

            with seed(rng_seed=42):
                # Sample from prior
                trace = numpyro.handlers.trace(model_fn).get_trace()
                for name, site in trace.items():
                    if site["type"] == "sample":
                        prior_samples[name] = float(site["value"])

            return {"observations": prior_samples, "data_type": "synthetic_prior", "sample_size": 1}

        loop = asyncio.get_event_loop()
        scenario_data = await loop.run_in_executor(self.executor, generate_data)

        return scenario_data

    async def _run_inference(self, model_structure: Dict[str, Any], scenario_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run Bayesian inference on the synthesized model"""

        def run_mcmc():
            model_fn = model_structure["model_function"]
            observations = scenario_data.get("observations", {})

            # Condition model on observations
            conditioned_model = numpyro.handlers.condition(model_fn, observations)

            # Set up MCMC
            nuts_kernel = NUTS(conditioned_model)
            mcmc = MCMC(nuts_kernel, num_warmup=500, num_samples=settings.probabilistic_samples, num_chains=1)

            # Run inference
            rng_key = jax.random.PRNGKey(0)
            mcmc.run(rng_key)

            # Extract samples
            samples = mcmc.get_samples()

            # Convert to Python types for JSON serialization
            processed_samples = {}
            for key, value in samples.items():
                if hasattr(value, "shape") and value.shape:
                    processed_samples[key] = {
                        "mean": float(jnp.mean(value)),
                        "std": float(jnp.std(value)),
                        "samples": value.tolist()[:100],  # Limit samples for response size
                    }
                else:
                    processed_samples[key] = {"mean": float(value), "std": 0.0, "samples": [float(value)]}

            return {
                "posterior_samples": processed_samples,
                "num_samples": settings.probabilistic_samples,
                "inference_method": "NUTS",
            }

        loop = asyncio.get_event_loop()
        inference_results = await loop.run_in_executor(self.executor, run_mcmc)

        return inference_results

    async def _generate_predictions(
        self, model_structure: Dict[str, Any], inference_results: Dict[str, Any], scenario_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate predictions using the inferred model"""

        def make_predictions():
            model_fn = model_structure["model_function"]
            posterior_samples = inference_results.get("posterior_samples", {})

            # Convert back to JAX arrays for prediction
            jax_samples = {}
            for key, stats in posterior_samples.items():
                if "samples" in stats:
                    jax_samples[key] = jnp.array(stats["samples"][:100])  # Use subset for prediction

            # Generate predictive samples
            predictive = Predictive(model_fn, jax_samples)
            rng_key = jax.random.PRNGKey(1)

            predictions = predictive(rng_key)

            # Process predictions
            processed_predictions = {}
            for key, value in predictions.items():
                if hasattr(value, "shape") and value.shape:
                    processed_predictions[key] = {
                        "mean": float(jnp.mean(value)),
                        "std": float(jnp.std(value)),
                        "percentile_25": float(jnp.percentile(value, 25)),
                        "percentile_75": float(jnp.percentile(value, 75)),
                        "min": float(jnp.min(value)),
                        "max": float(jnp.max(value)),
                    }

            return {"predictive_distributions": processed_predictions, "prediction_method": "posterior_predictive"}

        loop = asyncio.get_event_loop()
        predictions = await loop.run_in_executor(self.executor, make_predictions)

        return predictions

    async def _analyze_uncertainty(
        self, inference_results: Dict[str, Any], predictions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze uncertainty in the model and predictions"""

        def calculate_uncertainty():
            posterior_samples = inference_results.get("posterior_samples", {})
            predictive_dists = predictions.get("predictive_distributions", {})

            uncertainty_analysis = {
                "epistemic_uncertainty": {},
                "aleatory_uncertainty": {},
                "total_uncertainty": {},
                "confidence_intervals": {},
            }

            # Calculate epistemic uncertainty (parameter uncertainty)
            for var_name, stats in posterior_samples.items():
                std_dev = stats.get("std", 0.0)
                uncertainty_analysis["epistemic_uncertainty"][var_name] = {
                    "standard_deviation": std_dev,
                    "coefficient_of_variation": (
                        std_dev / abs(stats.get("mean", 1.0)) if stats.get("mean", 0.0) != 0 else float("inf")
                    ),
                }

            # Calculate predictive uncertainty
            for var_name, stats in predictive_dists.items():
                pred_std = stats.get("std", 0.0)
                uncertainty_analysis["total_uncertainty"][var_name] = {
                    "predictive_std": pred_std,
                    "prediction_interval_50": [stats.get("percentile_25", 0), stats.get("percentile_75", 0)],
                }

            # Overall uncertainty assessment
            avg_epistemic = (
                np.mean([v["standard_deviation"] for v in uncertainty_analysis["epistemic_uncertainty"].values()])
                if uncertainty_analysis["epistemic_uncertainty"]
                else 0.0
            )

            uncertainty_analysis["overall_assessment"] = {
                "average_epistemic_uncertainty": float(avg_epistemic),
                "uncertainty_level": (
                    "high"
                    if avg_epistemic > settings.uncertainty_threshold
                    else "moderate" if avg_epistemic > 0.3 else "low"
                ),
                "model_confidence": max(0.0, 1.0 - float(avg_epistemic)),
            }

            return uncertainty_analysis

        loop = asyncio.get_event_loop()
        uncertainty_analysis = await loop.run_in_executor(self.executor, calculate_uncertainty)

        return uncertainty_analysis

    async def cleanup(self):
        """Cleanup resources"""
        if hasattr(self, "executor"):
            self.executor.shutdown(wait=True)
            logger.info("Probabilistic model synthesizer cleanup completed")
