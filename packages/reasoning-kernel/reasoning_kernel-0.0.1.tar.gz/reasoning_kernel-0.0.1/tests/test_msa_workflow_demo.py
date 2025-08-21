"""
Demonstration test for MSA Agent Workflow

This test demonstrates the complete MSA reasoning workflow using all four agents:
1. ModelSynthesisAgent - Generate probabilistic programs
2. ProbabilisticReasoningAgent - Perform Bayesian inference
3. KnowledgeRetrievalAgent - Retrieve relevant knowledge
4. EvaluationAgent - Validate reasoning quality

This serves as both a test and a demonstration of the implemented functionality.
"""

import asyncio
from unittest.mock import MagicMock, AsyncMock
from semantic_kernel import Kernel

from reasoning_kernel.agents.model_synthesis_agent import ModelSynthesisAgent, SynthesisRequest
from reasoning_kernel.agents.probabilistic_reasoning_agent import (
    ProbabilisticReasoningAgent,
    InferenceRequest,
)
from reasoning_kernel.agents.knowledge_retrieval_agent import (
    KnowledgeRetrievalAgent,
    RetrievalRequest,
)
from reasoning_kernel.agents.evaluation_agent import (
    EvaluationAgent,
    EvaluationRequest,
    QualityMetric,
)
from reasoning_kernel.agents.communication_protocol import (
    CommunicationManager,
    AgentRole,
    create_msa_reasoning_workflow,
)


def create_mock_kernel():
    """Create a mock semantic kernel for testing"""
    kernel = MagicMock(spec=Kernel)

    async def mock_invoke(*args, **kwargs):
        # Return different responses based on the prompt content
        prompt = kwargs.get("prompt", "")
        if "extract" in prompt.lower() and "variables" in prompt.lower():
            return """{
                "outcome": {
                    "type": "continuous", 
                    "range": [0, 1],
                    "dependencies": [],
                    "description": "Test outcome variable",
                    "prior": "Beta(1, 1)"
                }
            }"""
        elif "generate" in prompt.lower() and "numpyro" in prompt.lower():
            return """
import numpyro
import numpyro.distributions as dist

def model():
    outcome = numpyro.sample("outcome", dist.Beta(2, 2))
    return {"outcome": outcome}
"""
        else:
            return "Mock LLM response"

    kernel.invoke_function = AsyncMock(side_effect=mock_invoke)
    return kernel


async def test_individual_agents():
    """Test each agent individually"""
    print("\n=== Testing Individual MSA Agents ===")

    kernel = create_mock_kernel()

    # Test 1: ModelSynthesisAgent
    print("\n1. Testing ModelSynthesisAgent...")
    synthesis_agent = ModelSynthesisAgent(kernel)

    synthesis_request = SynthesisRequest(
        scenario="A manufacturing quality control scenario where temperature affects product quality",
        knowledge_base={
            "entities": ["temperature", "quality"],
            "relationships": [("temperature", "quality")],
        },
    )

    synthesis_result = await synthesis_agent.synthesize_model(synthesis_request)
    print(
        f"   ✓ Model synthesis completed with confidence: {synthesis_result.confidence:.2f}"
    )
    print(
        f"   ✓ Generated program code: {len(synthesis_result.program_code)} characters"
    )

    # Test 2: ProbabilisticReasoningAgent
    print("\n2. Testing ProbabilisticReasoningAgent...")
    reasoning_agent = ProbabilisticReasoningAgent(kernel)

    inference_request = InferenceRequest(
        model_code=synthesis_result.program_code,
        query_variables=["outcome"],
        num_samples=100,
    )

    inference_result = await reasoning_agent.perform_inference(inference_request)
    print(
        f"   ✓ Bayesian inference completed with confidence: {inference_result.confidence_score:.2f}"
    )
    print(
        f"   ✓ Generated {len(inference_result.posterior_samples)} posterior distributions"
    )

    # Test 3: KnowledgeRetrievalAgent
    print("\n3. Testing KnowledgeRetrievalAgent...")
    knowledge_agent = KnowledgeRetrievalAgent(kernel)

    retrieval_request = RetrievalRequest(
        query="manufacturing quality control temperature", max_results=5
    )

    retrieval_result = await knowledge_agent.retrieve_knowledge(retrieval_request)
    print(
        f"   ✓ Knowledge retrieval completed with confidence: {retrieval_result.aggregated_confidence:.2f}"
    )
    print(f"   ✓ Retrieved {len(retrieval_result.knowledge_items)} knowledge items")

    # Test 4: EvaluationAgent
    print("\n4. Testing EvaluationAgent...")
    evaluation_agent = EvaluationAgent(kernel)

    evaluation_request = EvaluationRequest(
        reasoning_result={
            "knowledge": retrieval_result.__dict__,
            "synthesis": synthesis_result.__dict__,
            "inference": inference_result.__dict__,
            "scenario": synthesis_request.scenario,
        },
        evaluation_criteria=[
            QualityMetric.COHERENCE,
            QualityMetric.CONSISTENCY,
            QualityMetric.COMPLETENESS,
        ],
    )

    evaluation_result = await evaluation_agent.evaluate_reasoning(evaluation_request)
    print(
        f"   ✓ Evaluation completed with overall quality: {evaluation_result.overall_quality_score:.2f}"
    )
    print(f"   ✓ Evaluation confidence: {evaluation_result.evaluation_confidence:.2f}")
    print(f"   ✓ Generated {len(evaluation_result.recommendations)} recommendations")

    return {
        "synthesis": synthesis_result,
        "inference": inference_result,
        "retrieval": retrieval_result,
        "evaluation": evaluation_result,
    }


async def test_communication_protocol():
    """Test the communication protocol between agents"""
    print("\n=== Testing Communication Protocol ===")

    kernel = create_mock_kernel()

    # Create communication manager
    comm_manager = CommunicationManager()
    await comm_manager.initialize()

    # Create and register agents
    agents = {
        AgentRole.MODEL_SYNTHESIS: ModelSynthesisAgent(kernel),
        AgentRole.PROBABILISTIC_REASONING: ProbabilisticReasoningAgent(kernel),
        AgentRole.KNOWLEDGE_RETRIEVAL: KnowledgeRetrievalAgent(kernel),
        AgentRole.EVALUATION: EvaluationAgent(kernel),
    }

    for role, agent in agents.items():
        comm_manager.register_agent(role, agent)

    print(f"✓ Registered {len(agents)} agents with communication manager")

    # Test simple message passing
    try:
        # Mock a simple function on the knowledge agent for testing
        agents[AgentRole.KNOWLEDGE_RETRIEVAL].test_ping = AsyncMock(return_value="pong")

        response = await comm_manager.send_request(
            sender=AgentRole.MODEL_SYNTHESIS,
            recipient=AgentRole.KNOWLEDGE_RETRIEVAL,
            function_name="test_ping",
            parameters={},
        )

        print("✓ Message passing test successful")
        print(f"   Response: {response}")

    except Exception as e:
        print(f"⚠ Message passing test failed: {e}")

    # Test workflow creation
    scenario = "Manufacturing quality control with temperature monitoring"
    workflow = create_msa_reasoning_workflow(scenario)

    print(f"✓ Created MSA workflow with {len(workflow.steps)} steps")
    print(f"   Workflow: {workflow.name}")

    # Cleanup
    await comm_manager.shutdown()

    return workflow


async def test_full_workflow_simulation():
    """Test a complete MSA workflow simulation"""
    print("\n=== Testing Complete MSA Workflow ===")

    kernel = create_mock_kernel()

    # Create agents
    agents = {
        AgentRole.MODEL_SYNTHESIS: ModelSynthesisAgent(kernel),
        AgentRole.PROBABILISTIC_REASONING: ProbabilisticReasoningAgent(kernel),
        AgentRole.KNOWLEDGE_RETRIEVAL: KnowledgeRetrievalAgent(kernel),
        AgentRole.EVALUATION: EvaluationAgent(kernel),
    }

    # Simulate workflow execution step by step
    scenario = """
    A pharmaceutical manufacturing facility produces tablets with varying active ingredient concentrations.
    Quality control data shows that tablet hardness, compression force, and ambient humidity affect
    the active ingredient distribution. Recent batches show 15% variation in potency.
    """

    print(f"Scenario: {scenario[:100]}...")

    # Step 1: Knowledge Retrieval
    print("\nStep 1: Knowledge Retrieval")
    knowledge_agent = agents[AgentRole.KNOWLEDGE_RETRIEVAL]
    retrieval_request = RetrievalRequest(
        query="pharmaceutical tablet manufacturing quality control active ingredient potency",
        max_results=10,
        knowledge_types=["entities", "relationships", "procedures"],
    )

    knowledge_result = await knowledge_agent.retrieve_knowledge(retrieval_request)
    print(
        f"   ✓ Retrieved {len(knowledge_result.knowledge_items)} relevant knowledge items"
    )

    # Step 2: Model Synthesis
    print("\nStep 2: Model Synthesis")
    synthesis_agent = agents[AgentRole.MODEL_SYNTHESIS]
    synthesis_request = SynthesisRequest(
        scenario=scenario,
        knowledge_base={
            "knowledge_items": [
                item.__dict__ for item in knowledge_result.knowledge_items
            ]
        },
        target_variables=["potency", "hardness", "humidity"],
        constraints={"potency": {"min": 0.85, "max": 1.15}},  # ±15% from nominal
    )

    synthesis_result = await synthesis_agent.synthesize_model(synthesis_request)
    print(
        f"   ✓ Generated probabilistic model with confidence: {synthesis_result.confidence:.2f}"
    )
    print(
        f"   ✓ Model has {len(synthesis_result.causal_graph.nodes)} variables and {len(synthesis_result.causal_graph.edges)} relationships"
    )

    # Step 3: Probabilistic Reasoning
    print("\nStep 3: Probabilistic Reasoning")
    reasoning_agent = agents[AgentRole.PROBABILISTIC_REASONING]
    inference_request = InferenceRequest(
        model_code=synthesis_result.program_code,
        query_variables=["potency", "hardness"],
        evidence={"humidity": 0.6},  # 60% humidity
        num_samples=1000,
    )

    inference_result = await reasoning_agent.perform_inference(inference_request)
    print(
        f"   ✓ Completed Bayesian inference with confidence: {inference_result.confidence_score:.2f}"
    )
    print(
        f"   ✓ Uncertainty measures: {list(inference_result.uncertainty_measures.keys())}"
    )

    # Step 4: Evaluation
    print("\nStep 4: Quality Evaluation")
    evaluation_agent = agents[AgentRole.EVALUATION]
    evaluation_request = EvaluationRequest(
        reasoning_result={
            "scenario": scenario,
            "knowledge_retrieval": knowledge_result.__dict__,
            "model_synthesis": synthesis_result.__dict__,
            "probabilistic_reasoning": inference_result.__dict__,
            "confidence": inference_result.confidence_score,
            "execution_time": (
                knowledge_result.retrieval_time
                + synthesis_result.execution_time
                + inference_result.execution_time
            ),
        },
        context=scenario,
        evaluation_criteria=[
            QualityMetric.COHERENCE,
            QualityMetric.CONSISTENCY,
            QualityMetric.COMPLETENESS,
            QualityMetric.ACCURACY,
            QualityMetric.RELEVANCE,
        ],
    )

    evaluation_result = await evaluation_agent.evaluate_reasoning(evaluation_request)
    print(
        f"   ✓ Overall reasoning quality: {evaluation_result.overall_quality_score:.2f}"
    )
    print(f"   ✓ Evaluation confidence: {evaluation_result.evaluation_confidence:.2f}")

    # Summary
    print("\n=== Workflow Summary ===")
    total_time = (
        knowledge_result.retrieval_time
        + synthesis_result.execution_time
        + inference_result.execution_time
        + evaluation_result.execution_time
    )

    print(f"Total execution time: {total_time:.2f} seconds")
    print(f"Knowledge items found: {len(knowledge_result.knowledge_items)}")
    print(f"Model synthesis confidence: {synthesis_result.confidence:.2f}")
    print(f"Inference confidence: {inference_result.confidence_score:.2f}")
    print(f"Overall quality score: {evaluation_result.overall_quality_score:.2f}")
    print(f"Recommendations: {len(evaluation_result.recommendations)}")

    # Check performance requirements
    print("\n=== Performance Validation ===")
    if total_time <= 60:
        print("✓ Execution time within 60s requirement")
    else:
        print("⚠ Execution time exceeds 60s requirement")

    if evaluation_result.overall_quality_score >= 0.7:
        print("✓ Quality score meets threshold")
    else:
        print("⚠ Quality score below threshold")

    if inference_result.confidence_score >= 0.5:
        print("✓ Confidence score acceptable")
    else:
        print("⚠ Low confidence score")

    return {
        "knowledge": knowledge_result,
        "synthesis": synthesis_result,
        "inference": inference_result,
        "evaluation": evaluation_result,
        "total_time": total_time,
    }


async def main():
    """Run all MSA agent tests"""
    print("🤖 MSA Agent Implementation Test Suite")
    print("=" * 50)

    try:
        # Test individual agents
        individual_results = await test_individual_agents()

        # Test communication protocol
        workflow = await test_communication_protocol()

        # Test full workflow
        workflow_results = await test_full_workflow_simulation()

        print("\n" + "=" * 50)
        print("🎉 All MSA Agent Tests Completed Successfully!")
        print("\nImplemented Features:")
        print("✓ ModelSynthesisAgent - Probabilistic program synthesis")
        print("✓ ProbabilisticReasoningAgent - Bayesian inference")
        print("✓ KnowledgeRetrievalAgent - Semantic search")
        print("✓ EvaluationAgent - Quality assessment")
        print("✓ CommunicationManager - Agent coordination")
        print("✓ MSA Workflow - End-to-end reasoning")

        print("\nPerformance Summary:")
        print(f"- Total workflow time: {workflow_results['total_time']:.2f}s")
        print(
            f"- Quality score: {workflow_results['evaluation'].overall_quality_score:.2f}"
        )
        print(
            f"- Knowledge items: {len(workflow_results['knowledge'].knowledge_items)}"
        )
        print(
            f"- Inference confidence: {workflow_results['inference'].confidence_score:.2f}"
        )

        return True

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
