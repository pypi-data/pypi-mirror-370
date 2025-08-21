#!/usr/bin/env python3
"""
GEMINI Integration Demo
======================

Demonstrates how to use Google's GEMINI models with the MSA Reasoning Engine.

This example shows:
- Basic GEMINI configuration
- Different model variants
- Streaming analysis with real-time updates
- Error handling and fallback strategies

Prerequisites:
- Set GOOGLE_AI_API_KEY environment variable
- Install google extras: pip install -e ".[google]"
"""

import asyncio
import os
import sys

# Add the project root to the Python path
# Ensure the 'app' package is discoverable by installing the project in editable mode:
# pip install -e .

from reasoning_kernel.reasoning_kernel import ReasoningKernel, ReasoningConfig
from reasoning_kernel.core.kernel_config import KernelManager

class GeminiDemo:
    """Demonstration class for GEMINI integration"""

    def __init__(self):
        self.kernel_manager = None
        self.reasoning_kernel = None

    async def initialize(self):
        """Initialize the GEMINI-powered reasoning kernel"""
        print("🔧 Initializing GEMINI-powered MSA Reasoning Engine...")

        # Check for required environment variables
        if not os.getenv('GOOGLE_AI_API_KEY'):
            print("❌ Error: GOOGLE_AI_API_KEY environment variable not set")
            print("Please set your GEMINI API key: export GOOGLE_AI_API_KEY='your_key_here'")
            return False

        try:
            # Initialize Semantic Kernel with GEMINI support
            self.kernel_manager = KernelManager()
            await self.kernel_manager.initialize()

            # Create reasoning kernel with GEMINI configuration
            config = ReasoningConfig(
                parse_model="gemini-2.5-pro",
                synthesis_model="gemini-2.5-pro",
                graph_model="phi-4-reasoning",
                enable_thinking_mode=True,
                thinking_detail_level="detailed",
                max_retries=2
            )

            self.reasoning_kernel = ReasoningKernel(
                kernel=self.kernel_manager.kernel,
                redis_client=None,  # Optional Redis for caching
                config=config
            )

            print("✅ GEMINI integration initialized successfully!")
            return True

        except Exception as e:
            print(f"❌ Failed to initialize GEMINI integration: {e}")
            return False

    async def demo_basic_analysis(self):
        """Demonstrate basic reasoning analysis with GEMINI"""
        print("\n" + "="*60)
        print("📊 DEMO 1: Basic Manufacturing Analysis")
        print("="*60)

        scenario = """
        Our electronics manufacturing plant has experienced a 15% drop in production
        efficiency over the past week. The main assembly line, which normally produces
        2,000 units per day, is now producing only 1,700 units. Quality control reports
        show a slight increase in defect rates from 2% to 3.5%. Worker attendance is
        normal, and no equipment failures have been reported.
        """

        print(f"Scenario: {scenario.strip()}")
        print("\n🧠 Starting GEMINI-powered analysis...")

        try:
            result = await self.reasoning_kernel.reason(scenario)

            print("\n📈 Analysis Results:")
            print(f"   Success: {result.success}")
            print(f"   Confidence: {result.overall_confidence:.2f}")
            print(f"   Execution Time: {result.total_execution_time:.2f}s")
            print(f"   Stages Completed: {len(result.stage_timings or {})}")

            if result.thinking_process:
                print("\n💭 GEMINI Reasoning Process:")
                for i, thought in enumerate(result.thinking_process[:3], 1):
                    print(f"   {i}. {thought}")

            return result

        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            return None

    async def demo_streaming_analysis(self):
        """Demonstrate streaming analysis with real-time updates"""
        print("\n" + "="*60)
        print("🌊 DEMO 2: Streaming Financial Analysis")
        print("="*60)

        scenario = """
        Our company's stock price has dropped 12% following a competitor's product
        announcement. We have $2M in cash reserves, quarterly revenue of $8M, and
        our main product accounts for 65% of revenue. The competitor's product offers
        similar features at 20% lower cost but requires 6-month implementation time.
        """

        print(f"Scenario: {scenario.strip()}")
        print("\n🎯 Starting streaming analysis with real-time updates...\n")

        # Callback functions for streaming
        async def on_stage_start(stage_name):
            print(f"🚀 Stage Starting: {stage_name}")

        async def on_stage_complete(stage_name, payload):
            confidence = payload.get('confidence', 0)
            time_taken = payload.get('execution_time', 0)
            print(f"✅ Stage Complete: {stage_name} (confidence: {confidence:.2f}, time: {time_taken:.1f}s)")

        async def on_thinking_sentence(sentence):
            print(f"💭 {sentence}")

        try:
            result = await self.reasoning_kernel.reason_with_streaming(
                vignette=scenario,
                session_id="gemini_demo_streaming",
                on_stage_start=on_stage_start,
                on_stage_complete=on_stage_complete,
                on_thinking_sentence=on_thinking_sentence
            )

            print("\n📊 Final Results:")
            print(f"   Overall Success: {result.success}")
            print(f"   Final Confidence: {result.overall_confidence:.2f}")
            print(f"   Total Time: {result.total_execution_time:.2f}s")

            return result

        except Exception as e:
            print(f"❌ Streaming analysis failed: {e}")
            return None

    async def demo_model_comparison(self):
        """Compare different GEMINI model variants"""
        print("\n" + "="*60)
        print("⚖️  DEMO 3: GEMINI Model Comparison")
        print("="*60)

        scenario = """
        Supply chain analysis: Raw material costs have increased 25% due to global
        commodity price volatility. Our inventory lasts 3 weeks at current production.
        Alternative suppliers offer materials at 15% premium with 2-week delivery.
        """

        models_to_test = [
            ("gemini-2.5-pro", "High-quality reasoning"),
            ("gemini-2.5-flash", "Fast processing"),
        ]

        results = {}

        for model_name, description in models_to_test:
            print(f"\n🔍 Testing {model_name} ({description})...")

            # Configure for this model
            config = ReasoningConfig(
                parse_model=model_name,
                synthesis_model=model_name,
                thinking_detail_level="moderate"
            )

            kernel = ReasoningKernel(
                kernel=self.kernel_manager.kernel,
                redis_client=None,
                config=config
            )

            try:
                result = await kernel.reason(scenario)
                results[model_name] = {
                    'success': result.success,
                    'confidence': result.overall_confidence,
                    'time': result.total_execution_time,
                    'stages': len(result.stage_timings or {})
                }

                print(f"   ✅ Success: {result.success}")
                print(f"   📊 Confidence: {result.overall_confidence:.2f}")
                print(f"   ⏱️  Time: {result.total_execution_time:.2f}s")

            except Exception as e:
                print(f"   ❌ Failed: {e}")
                results[model_name] = {'error': str(e)}

        print("\n📈 Model Comparison Summary:")
        for model, data in results.items():
            if 'error' not in data:
                print(f"   {model}: {data['confidence']:.2f} confidence, {data['time']:.1f}s")
            else:
                print(f"   {model}: Error - {data['error']}")

        return results

    async def demo_error_handling(self):
        """Demonstrate error handling and fallback strategies"""
        print("\n" + "="*60)
        print("🛡️  DEMO 4: Error Handling & Fallback")
        print("="*60)

        # Configuration with fallback models
        config = ReasoningConfig(
            parse_model="gemini-2.5-pro",
            synthesis_model="gemini-2.5-pro",
            fallback_models={
                "parse": "gemini-2.5-flash",
                "synthesis": "gemini-1.5-pro"
            },
            max_retries=2,
            timeout_per_stage=60
        )

        kernel = ReasoningKernel(
            kernel=self.kernel_manager.kernel,
            redis_client=None,
            config=config
        )

        print("Configuration:")
        print(f"   Primary models: {config.parse_model}, {config.synthesis_model}")
        print(f"   Fallback models: {config.fallback_models}")
        print(f"   Max retries: {config.max_retries}")
        print(f"   Timeout per stage: {config.timeout_per_stage}s")

        scenario = "Analyze the impact of a 30% increase in energy costs on our operations."

        try:
            result = await kernel.reason(scenario)
            print("\n✅ Analysis completed successfully!")
            print(f"   Success: {result.success}")
            print(f"   Confidence: {result.overall_confidence:.2f}")

            return result

        except Exception as e:
            print(f"\n❌ Analysis failed even with fallbacks: {e}")
            return None

async def main():
    """Run all GEMINI integration demos"""
    demo = GeminiDemo()

    # Initialize the system
    if not await demo.initialize():
        return

    print("\n🎯 Running GEMINI Integration Demonstrations...")

    # Run all demos
    demos = [
        ("Basic Analysis", demo.demo_basic_analysis),
        ("Streaming Analysis", demo.demo_streaming_analysis),
        ("Model Comparison", demo.demo_model_comparison),
        ("Error Handling", demo.demo_error_handling)
    ]

    results = {}

    for demo_name, demo_func in demos:
        try:
            print(f"\n{'='*20} {demo_name} {'='*20}")
            result = await demo_func()
            results[demo_name] = result
        except KeyboardInterrupt:
            print("\n⏹️  Demo interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Demo '{demo_name}' failed: {e}")
            results[demo_name] = {"error": str(e)}

    # Summary
    print("\n" + "="*60)
    print("📋 DEMO SUMMARY")
    print("="*60)

    for demo_name, result in results.items():
        if result and hasattr(result, 'success'):
            status = "✅ Success" if result.success else "⚠️  Partial"
            confidence = f"({result.overall_confidence:.2f} confidence)"
        elif result and isinstance(result, dict) and 'error' not in result:
            status = "✅ Completed"
            confidence = ""
        else:
            status = "❌ Failed"
            confidence = ""

        print(f"   {demo_name}: {status} {confidence}")

    print("\n🎉 GEMINI Integration Demo Complete!")
    print("📖 For more details, see GEMINI.md documentation")

if __name__ == "__main__":
    # Check Python version
    if sys.version_info < MIN_PYTHON_VERSION:
        print("❌ Python 3.10+ required")
        sys.exit(1)

    # Run the demo
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        sys.exit(1)
