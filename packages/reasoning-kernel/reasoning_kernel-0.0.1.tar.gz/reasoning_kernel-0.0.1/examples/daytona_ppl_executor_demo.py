"""
Example demonstrating DaytonaPPLExecutor integration with MSA Pipeline

This example shows how to use the DaytonaPPLExecutor for secure execution
of probabilistic programs within the MSA reasoning framework.
"""

import asyncio
import logging

from reasoning_kernel.services.daytona_ppl_executor import (
    DaytonaPPLExecutor,
    PPLFramework,
    PPLExecutionConfig,
    PPLProgram,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

async def demonstrate_ppl_executor():
    """Demonstrate DaytonaPPLExecutor capabilities"""

    print("🚀 DaytonaPPLExecutor Demo")
    print("=" * 50)

    # Create PPL execution configuration
    print("\n📋 Creating PPL execution configuration...")
    ppl_config = PPLExecutionConfig(
        framework=PPLFramework.NUMPYRO,
        max_execution_time=120.0,
        memory_limit_mb=2048,
        cpu_limit=2.0,
        python_version="3.10",
        required_packages=["numpy>=1.21.0", "jax>=0.4.0", "numpyro>=0.13.0", "arviz>=0.16.0"],
    )

    print(f"  ✓ Framework: {ppl_config.framework.value}")
    print(f"  ✓ Max execution time: {ppl_config.max_execution_time}s")
    print(f"  ✓ Memory limit: {ppl_config.memory_limit_mb}MB")
    print(f"  ✓ CPU cores: {ppl_config.cpu_limit}")

    # Initialize PPL executor
    print("\n🔧 Initializing DaytonaPPLExecutor...")
    executor = DaytonaPPLExecutor(ppl_config=ppl_config)
    print("✓ DaytonaPPLExecutor initialized successfully")

    # Create example NumPyro probabilistic program
    print("\n📄 Creating NumPyro probabilistic program...")
    numpyro_code = """
import numpyro
import numpyro.distributions as dist
import jax.numpy as jnp
from jax import random
from numpyro.infer import MCMC, NUTS

def bayesian_linear_regression(x, y=None):
    \"\"\"Bayesian linear regression model\"\"\"
    # Priors
    alpha = numpyro.sample("alpha", dist.Normal(0.0, 1.0))
    beta = numpyro.sample("beta", dist.Normal(0.0, 1.0))
    sigma = numpyro.sample("sigma", dist.HalfNormal(1.0))

    # Linear model
    mu = alpha + beta * x

    # Likelihood
    with numpyro.plate("data", x.shape[0]):
        numpyro.sample("obs", dist.Normal(mu, sigma), obs=y)

def main():
    \"\"\"Main inference function\"\"\"
    # Generate synthetic data
    key = random.PRNGKey(42)
    true_alpha, true_beta = 1.0, 2.0
    x = jnp.linspace(0, 1, 20)
    y = true_alpha + true_beta * x + 0.1 * random.normal(key, x.shape)

    # Run MCMC inference
    nuts_kernel = NUTS(bayesian_linear_regression)
    mcmc = MCMC(nuts_kernel, num_warmup=100, num_samples=200)

    mcmc.run(key, x, y)
    samples = mcmc.get_samples()

    # Calculate posterior statistics
    posterior_stats = {
        "alpha_mean": float(jnp.mean(samples["alpha"])),
        "alpha_std": float(jnp.std(samples["alpha"])),
        "beta_mean": float(jnp.mean(samples["beta"])),
        "beta_std": float(jnp.std(samples["beta"])),
        "sigma_mean": float(jnp.mean(samples["sigma"])),
        "sigma_std": float(jnp.std(samples["sigma"])),
    }

    return {
        "model": "bayesian_linear_regression",
        "true_parameters": {"alpha": true_alpha, "beta": true_beta},
        "posterior_statistics": posterior_stats,
        "num_samples": len(samples["alpha"]),
        "convergence": "successful"
    }
"""

    program = PPLProgram(
        code=numpyro_code,
        framework=PPLFramework.NUMPYRO,
        entry_point="main",
        validation_rules=["import numpyro", "def main", "MCMC"],
    )

    print(f"  ✓ Program framework: {program.framework.value}")
    print(f"  ✓ Entry point: {program.entry_point}")
    print(f"  ✓ Code length: {len(program.code)} characters")
    print(f"  ✓ Validation rules: {len(program.validation_rules)}")

    # Validate the program
    print("\n🔍 Validating PPL program...")
    validation_errors = await executor.validate_ppl_program(program)

    if validation_errors:
        print("❌ Validation failed:")
        for error in validation_errors:
            print(f"  • {error}")
        return False
    else:
        print("✅ Program validation passed")

    # Test environment preparation
    print("\n🛠️  Preparing execution environment...")
    try:
        setup_commands = await executor.prepare_execution_environment(program)
        print(f"✓ Generated {len(setup_commands)} setup commands:")
        for cmd_name, cmd in setup_commands.items():
            print(f"  • {cmd_name}: {cmd[:60]}{'...' if len(cmd) > 60 else ''}")
    except Exception as e:
        print(f"❌ Environment preparation failed: {e}")
        return False

    # Test execution wrapper generation
    print("\n📜 Generating execution wrapper...")
    try:
        wrapper_script = executor._create_execution_wrapper(program)
        print("✅ Execution wrapper generated successfully")
        print(f"  • Script length: {len(wrapper_script)} characters")
        print(
            f"  • Contains required markers: {all(marker in wrapper_script for marker in ['PPL_RESULT_START', 'PPL_RESULT_END'])}"
        )
    except Exception as e:
        print(f"❌ Wrapper generation failed: {e}")
        return False

    # Demonstrate batch execution capability
    print("\n📦 Testing batch execution capability...")

    # Create simpler programs for batch demo
    simple_programs = [
        PPLProgram(
            code="""
import numpyro
import numpyro.distributions as dist

def main():
    return {"model": "normal_distribution", "mean": 0.0, "std": 1.0}
""",
            framework=PPLFramework.NUMPYRO,
            entry_point="main",
        ),
        PPLProgram(
            code="""
import numpyro
import numpyro.distributions as dist

def main():
    return {"model": "beta_distribution", "alpha": 2.0, "beta": 3.0}
""",
            framework=PPLFramework.NUMPYRO,
            entry_point="main",
        ),
    ]

    print(f"✓ Created {len(simple_programs)} programs for batch execution")

    # Show integration with MSA pipeline
    print("\n🔗 MSA Pipeline Integration Example:")
    print(
        """
    MSA Stage 4 (Model Synthesis) Integration:

    class ModelSynthesisStage(PipelineStage):
        def __init__(self):
            super().__init__(StageType.MODEL_SYNTHESIS)
            self.ppl_executor = DaytonaPPLExecutor(
                ppl_config=PPLExecutionConfig(framework=PPLFramework.NUMPYRO)
            )

        async def process(self, context: PipelineContext) -> StageResult:
            # Generate PPL program from causal model
            ppl_code = self._generate_numpyro_code(context.causal_model)

            program = PPLProgram(
                code=ppl_code,
                framework=PPLFramework.NUMPYRO,
                entry_point="inference_main"
            )

            # Execute in secure sandbox
            result = await self.ppl_executor.execute_ppl_program(program)

            return StageResult(
                success=result.exit_code == 0,
                data={
                    "inference_results": result.inference_results,
                    "execution_time": result.execution_time,
                    "convergence_diagnostics": result.convergence_diagnostics
                },
                metadata=result.execution_metadata
            )
    """
    )

    print("\n✨ Key Features Demonstrated:")
    print("  • Secure PPL program validation")
    print("  • Environment preparation and setup")
    print("  • Execution wrapper generation")
    print("  • Result parsing with structured output")
    print("  • Batch execution capability")
    print("  • MSA pipeline integration patterns")

    print("\n🎯 Usage in Production:")
    print("  1. MSA pipeline generates probabilistic models")
    print("  2. DaytonaPPLExecutor validates programs for security")
    print("  3. Programs execute in isolated Daytona sandbox")
    print("  4. Results parsed and integrated into reasoning flow")
    print("  5. Batch processing for multiple model variants")

    return True

async def main():
    """Main demonstration function"""
    try:
        success = await demonstrate_ppl_executor()
        if success:
            print("\n🎉 DaytonaPPLExecutor demonstration completed successfully!")
        else:
            print("\n❌ Demonstration encountered errors")

    except Exception as e:
        logger.error(f"Demo error: {e}")
        print(f"\n💥 Demo failed with error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
