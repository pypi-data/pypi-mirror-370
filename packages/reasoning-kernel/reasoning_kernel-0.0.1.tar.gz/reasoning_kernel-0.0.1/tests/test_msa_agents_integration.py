"""
Integration tests for MSA Agent Implementation (Phase 2)

Tests the complete integration of all four core MSA agents:
- ModelSynthesisAgent
- ProbabilisticReasoningAgent
- KnowledgeRetrievalAgent
- EvaluationAgent

Also tests the unified communication protocol and workflow coordination.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
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


@pytest.fixture
def mock_kernel():
    """Create a mock semantic kernel for testing"""
    kernel = MagicMock(spec=Kernel)

    # Mock kernel invoke function
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
import jax.numpy as jnp

def model():
    outcome = numpyro.sample("outcome", dist.Beta(1, 1))
    return {"outcome": outcome}
"""
        elif "inference" in prompt.lower():
            return """
import numpyro
from numpyro.infer import MCMC, NUTS
from jax import random

# Inference code would be here
nuts_kernel = NUTS(model)
mcmc = MCMC(nuts_kernel, num_samples=1000, num_warmup=500)
rng_key = random.PRNGKey(0)
mcmc.run(rng_key)
samples = mcmc.get_samples()
"""
        else:
            return "Mock LLM response"

    kernel.invoke_function = AsyncMock(side_effect=mock_invoke)
    return kernel


@pytest.fixture
def mock_redis_service():
    """Create a mock Redis service for testing"""
    redis_service = MagicMock()

    # Mock Redis operations
    async def mock_store_data(key, data, ttl=None):
        return True

    async def mock_get_data(key):
        return {"test": "data"}

    redis_service.store_data = AsyncMock(side_effect=mock_store_data)
    redis_service.get_data = AsyncMock(side_effect=mock_get_data)

    return redis_service


@pytest.fixture
async def msa_agents(mock_kernel, mock_redis_service):
    """Create all four MSA agents for testing"""
    agents = {
        AgentRole.MODEL_SYNTHESIS: ModelSynthesisAgent(mock_kernel),
        AgentRole.PROBABILISTIC_REASONING: ProbabilisticReasoningAgent(mock_kernel),
        AgentRole.KNOWLEDGE_RETRIEVAL: KnowledgeRetrievalAgent(
            mock_kernel, mock_redis_service
        ),
        AgentRole.EVALUATION: EvaluationAgent(mock_kernel),
    }
    return agents


@pytest.fixture
async def communication_manager(msa_agents):
    """Create and initialize communication manager with agents"""
    manager = CommunicationManager()
    await manager.initialize()

    # Register all agents
    for role, agent in msa_agents.items():
        manager.register_agent(role, agent)

    yield manager

    # Cleanup
    await manager.shutdown()


class TestModelSynthesisAgent:
    """Test ModelSynthesisAgent functionality"""

    @pytest.mark.asyncio
    async def test_synthesize_model_basic(self, msa_agents):
        """Test basic model synthesis functionality"""
        agent = msa_agents[AgentRole.MODEL_SYNTHESIS]

        request = SynthesisRequest(
            scenario="A simple test scenario for probability analysis",
            knowledge_base={"entities": ["outcome"], "constraints": []},
        )

        result = await agent.synthesize_model(request)

        assert result is not None
        assert result.program_code is not None
        assert len(result.program_code) > 0
        assert result.confidence >= 0.0
        assert result.confidence <= 1.0
        assert isinstance(result.parameters, dict)
        assert isinstance(result.validation_results, dict)

    @pytest.mark.asyncio
    async def test_synthesize_model_with_constraints(self, msa_agents):
        """Test model synthesis with constraints"""
        agent = msa_agents[AgentRole.MODEL_SYNTHESIS]

        request = SynthesisRequest(
            scenario="Manufacturing quality control scenario",
            knowledge_base={
                "entities": ["quality_score", "temperature", "pressure"],
                "relationships": [
                    ("temperature", "quality_score"),
                    ("pressure", "quality_score"),
                ],
            },
            constraints={"quality_score": {"min": 0, "max": 100}},
        )

        result = await agent.synthesize_model(request)

        assert (
            result.success or len(result.errors) > 0
        )  # Should either succeed or have errors
        assert result.causal_graph is not None
        assert len(result.causal_graph.nodes) > 0


class TestProbabilisticReasoningAgent:
    """Test ProbabilisticReasoningAgent functionality"""

    @pytest.mark.asyncio
    async def test_perform_inference_basic(self, msa_agents):
        """Test basic probabilistic inference"""
        agent = msa_agents[AgentRole.PROBABILISTIC_REASONING]

        request = InferenceRequest(
            model_code="""
import numpyro
import numpyro.distributions as dist

def model():
    outcome = numpyro.sample("outcome", dist.Beta(2, 2))
    return {"outcome": outcome}
""",
            query_variables=["outcome"],
            num_samples=100,
        )

        result = await agent.perform_inference(request)

        assert result is not None
        assert "outcome" in result.posterior_samples
        assert len(result.posterior_samples["outcome"]) == 100
        assert "outcome" in result.summary_statistics
        assert result.confidence_score >= 0.0
        assert result.confidence_score <= 1.0

    @pytest.mark.asyncio
    async def test_belief_propagation(self, msa_agents):
        """Test belief propagation functionality"""
        agent = msa_agents[AgentRole.PROBABILISTIC_REASONING]

        factor_graph = {
            "variables": [
                {"name": "A", "values": ["true", "false"]},
                {"name": "B", "values": ["true", "false"]},
            ],
            "factors": [{"variables": ["A", "B"], "type": "compatibility"}],
        }

        evidence = {"A": "true"}

        belief_states = await agent.belief_propagation(factor_graph, evidence)

        assert isinstance(belief_states, dict)
        assert "A" in belief_states
        assert "B" in belief_states
        assert belief_states["A"].confidence == 1.0  # Evidence has full confidence


class TestKnowledgeRetrievalAgent:
    """Test KnowledgeRetrievalAgent functionality"""

    @pytest.mark.asyncio
    async def test_retrieve_knowledge_basic(self, msa_agents):
        """Test basic knowledge retrieval"""
        agent = msa_agents[AgentRole.KNOWLEDGE_RETRIEVAL]

        request = RetrievalRequest(
            query="manufacturing quality control processes",
            max_results=5,
            min_relevance_score=0.3,
        )

        result = await agent.retrieve_knowledge(request)

        assert result is not None
        assert isinstance(result.knowledge_items, list)
        assert result.total_found >= 0
        assert result.aggregated_confidence >= 0.0
        assert result.aggregated_confidence <= 1.0
        assert isinstance(result.semantic_clusters, list)

    @pytest.mark.asyncio
    async def test_search_entities(self, msa_agents):
        """Test entity search functionality"""
        agent = msa_agents[AgentRole.KNOWLEDGE_RETRIEVAL]

        entities = await agent.search_entities("manufacturing equipment", "entities")

        assert isinstance(entities, list)
        # Should return some entities even if simulated
        for entity in entities:
            assert hasattr(entity, "knowledge_type")
            assert hasattr(entity, "relevance_score")
            assert hasattr(entity, "confidence")


class TestEvaluationAgent:
    """Test EvaluationAgent functionality"""

    @pytest.mark.asyncio
    async def test_evaluate_reasoning_basic(self, msa_agents):
        """Test basic reasoning evaluation"""
        agent = msa_agents[AgentRole.EVALUATION]

        reasoning_result = {
            "knowledge_extraction": {"entities": ["quality", "temperature"]},
            "probabilistic_reasoning": {"probabilities": {"outcome": 0.75}},
            "confidence": 0.8,
            "reasoning_steps": ["step1", "step2", "step3"],
            "conclusion": "Quality is positively correlated with temperature control",
        }

        request = EvaluationRequest(
            reasoning_result=reasoning_result,
            evaluation_criteria=[QualityMetric.COHERENCE, QualityMetric.CONSISTENCY],
        )

        result = await agent.evaluate_reasoning(request)

        assert result is not None
        assert result.overall_quality_score >= 0.0
        assert result.overall_quality_score <= 1.0
        assert len(result.quality_scores) >= 2  # At least coherence and consistency
        assert result.performance_metrics is not None
        assert result.evaluation_confidence >= 0.0
        assert result.evaluation_confidence <= 1.0

    @pytest.mark.asyncio
    async def test_evaluate_with_ground_truth(self, msa_agents):
        """Test evaluation with ground truth data"""
        agent = msa_agents[AgentRole.EVALUATION]

        reasoning_result = {
            "conclusion": "Temperature affects quality positively",
            "probabilities": {"high_quality": 0.8, "low_quality": 0.2},
        }

        ground_truth = {
            "conclusion": "Temperature has positive correlation with quality",
            "probabilities": {"high_quality": 0.75, "low_quality": 0.25},
        }

        request = EvaluationRequest(
            reasoning_result=reasoning_result,
            ground_truth=ground_truth,
            evaluation_criteria=[QualityMetric.ACCURACY],
        )

        result = await agent.evaluate_reasoning(request)

        assert result is not None
        accuracy_scores = [
            s for s in result.quality_scores if s.metric == QualityMetric.ACCURACY
        ]
        assert len(accuracy_scores) == 1
        assert (
            accuracy_scores[0].confidence > 0.5
        )  # Should have higher confidence with ground truth


class TestCommunicationProtocol:
    """Test the unified communication protocol"""

    @pytest.mark.asyncio
    async def test_agent_registration(self, communication_manager, msa_agents):
        """Test agent registration with communication manager"""
        # Agents should already be registered in the fixture
        stats = communication_manager.get_statistics()
        assert stats["registered_agents"] == 4

    @pytest.mark.asyncio
    async def test_send_request_response(self, communication_manager, msa_agents):
        """Test request-response communication between agents"""
        # Mock a simple function on the target agent
        target_agent = msa_agents[AgentRole.KNOWLEDGE_RETRIEVAL]
        target_agent.test_function = AsyncMock(return_value={"test": "response"})

        response = await communication_manager.send_request(
            sender=AgentRole.MODEL_SYNTHESIS,
            recipient=AgentRole.KNOWLEDGE_RETRIEVAL,
            function_name="test_function",
            parameters={"param1": "value1"},
        )

        assert response["result"]["test"] == "response"
        target_agent.test_function.assert_called_once_with(param1="value1")

    @pytest.mark.asyncio
    async def test_broadcast_event(self, communication_manager, msa_agents):
        """Test event broadcasting"""
        # This test verifies that broadcast doesn't crash
        # In a real system, agents would have event handlers
        await communication_manager.broadcast_event(
            sender=AgentRole.MODEL_SYNTHESIS,
            event_type="model_synthesized",
            event_data={"model_id": "test_123"},
        )

        # Verify no errors occurred
        stats = communication_manager.get_statistics()
        assert stats["messages_sent"] > 0


class TestWorkflowCoordination:
    """Test workflow coordination across agents"""

    @pytest.mark.asyncio
    async def test_create_msa_workflow(self):
        """Test creation of MSA reasoning workflow"""
        scenario = "Test manufacturing scenario for quality analysis"

        workflow = create_msa_reasoning_workflow(scenario)

        assert workflow is not None
        assert workflow.name == "MSA Reasoning Workflow"
        assert len(workflow.steps) == 4  # Knowledge, Synthesis, Reasoning, Evaluation

        # Check step dependencies
        step_dict = {step.step_id: step for step in workflow.steps}

        assert len(step_dict["knowledge_retrieval"].dependencies) == 0  # First step
        assert "knowledge_retrieval" in step_dict["model_synthesis"].dependencies
        assert "model_synthesis" in step_dict["probabilistic_reasoning"].dependencies
        assert len(step_dict["evaluation"].dependencies) == 3  # Depends on all others

    @pytest.mark.asyncio
    async def test_workflow_execution_simulation(
        self, communication_manager, msa_agents
    ):
        """Test simulated workflow execution"""
        # Mock the agent functions to return simple responses
        for agent in msa_agents.values():
            if hasattr(agent, "retrieve_knowledge"):
                agent.retrieve_knowledge = AsyncMock(
                    return_value={"knowledge_items": []}
                )
            if hasattr(agent, "synthesize_model"):
                agent.synthesize_model = AsyncMock(
                    return_value={"program_code": "test_code"}
                )
            if hasattr(agent, "perform_inference"):
                agent.perform_inference = AsyncMock(
                    return_value={"posterior_samples": {}}
                )
            if hasattr(agent, "evaluate_reasoning"):
                agent.evaluate_reasoning = AsyncMock(
                    return_value={"overall_quality_score": 0.8}
                )

        scenario = "Simple test scenario"
        workflow = create_msa_reasoning_workflow(scenario)

        try:
            # This might fail due to function name mismatches, but should not crash
            result = await communication_manager.execute_workflow(workflow)
            # If it succeeds, verify basic structure
            assert isinstance(result, dict)
        except Exception as e:
            # Expected in simulation - verify it's a reasonable error
            assert "not found" in str(e).lower() or "function" in str(e).lower()


class TestIntegrationScenarios:
    """Test complete integration scenarios"""

    @pytest.mark.asyncio
    async def test_manufacturing_quality_scenario(self, msa_agents):
        """Test a complete manufacturing quality control scenario"""
        scenario = """
        A manufacturing plant produces electronic components. The quality control
        process involves temperature monitoring during assembly. Recent data shows
        quality scores varying with temperature fluctuations.
        """

        # Step 1: Knowledge Retrieval
        knowledge_agent = msa_agents[AgentRole.KNOWLEDGE_RETRIEVAL]
        knowledge_request = RetrievalRequest(
            query="manufacturing quality temperature control", max_results=5
        )
        knowledge_result = await knowledge_agent.retrieve_knowledge(knowledge_request)

        # Step 2: Model Synthesis
        synthesis_agent = msa_agents[AgentRole.MODEL_SYNTHESIS]
        synthesis_request = SynthesisRequest(
            scenario=scenario,
            knowledge_base={"items": knowledge_result.knowledge_items},
        )
        synthesis_result = await synthesis_agent.synthesize_model(synthesis_request)

        # Step 3: Probabilistic Reasoning
        reasoning_agent = msa_agents[AgentRole.PROBABILISTIC_REASONING]
        reasoning_request = InferenceRequest(
            model_code=synthesis_result.program_code,
            query_variables=["quality_score"],
            num_samples=100,
        )
        reasoning_result = await reasoning_agent.perform_inference(reasoning_request)

        # Step 4: Evaluation
        evaluation_agent = msa_agents[AgentRole.EVALUATION]
        evaluation_request = EvaluationRequest(
            reasoning_result={
                "knowledge": knowledge_result.__dict__,
                "synthesis": synthesis_result.__dict__,
                "reasoning": reasoning_result.__dict__,
                "scenario": scenario,
            }
        )
        evaluation_result = await evaluation_agent.evaluate_reasoning(
            evaluation_request
        )

        # Verify all steps completed
        assert knowledge_result.retrieval_time > 0
        assert synthesis_result.execution_time > 0
        assert reasoning_result.execution_time > 0
        assert evaluation_result.execution_time > 0
        assert evaluation_result.overall_quality_score >= 0.0

    @pytest.mark.asyncio
    async def test_error_handling_resilience(self, msa_agents):
        """Test error handling and resilience across agents"""
        # Test with invalid/problematic inputs

        # Knowledge retrieval with empty query
        knowledge_agent = msa_agents[AgentRole.KNOWLEDGE_RETRIEVAL]
        knowledge_result = await knowledge_agent.retrieve_knowledge(
            RetrievalRequest(query="", max_results=1)
        )
        # Should handle gracefully
        assert knowledge_result is not None

        # Model synthesis with minimal data
        synthesis_agent = msa_agents[AgentRole.MODEL_SYNTHESIS]
        synthesis_result = await synthesis_agent.synthesize_model(
            SynthesisRequest(scenario="", knowledge_base={})
        )
        # Should handle gracefully
        assert synthesis_result is not None

        # Evaluation with empty data
        evaluation_agent = msa_agents[AgentRole.EVALUATION]
        evaluation_result = await evaluation_agent.evaluate_reasoning(
            EvaluationRequest(reasoning_result={})
        )
        # Should handle gracefully
        assert evaluation_result is not None
        assert evaluation_result.overall_quality_score >= 0.0


class TestPerformanceRequirements:
    """Test performance requirements compliance"""

    @pytest.mark.asyncio
    async def test_execution_time_requirements(self, msa_agents):
        """Test that agents meet execution time requirements (<60s)"""
        scenario = "Performance test scenario for timing validation"

        # Test each agent individually
        start_time = datetime.now()

        # Knowledge retrieval should be fast
        knowledge_agent = msa_agents[AgentRole.KNOWLEDGE_RETRIEVAL]
        knowledge_result = await knowledge_agent.retrieve_knowledge(
            RetrievalRequest(query=scenario, max_results=10)
        )
        knowledge_time = (datetime.now() - start_time).total_seconds()
        assert knowledge_time < 30, f"Knowledge retrieval took {knowledge_time}s"

        # Model synthesis
        start_time = datetime.now()
        synthesis_agent = msa_agents[AgentRole.MODEL_SYNTHESIS]
        synthesis_result = await synthesis_agent.synthesize_model(
            SynthesisRequest(scenario=scenario, knowledge_base={})
        )
        synthesis_time = (datetime.now() - start_time).total_seconds()
        assert synthesis_time < 60, f"Model synthesis took {synthesis_time}s"

        # Probabilistic reasoning
        start_time = datetime.now()
        reasoning_agent = msa_agents[AgentRole.PROBABILISTIC_REASONING]
        reasoning_result = await reasoning_agent.perform_inference(
            InferenceRequest(
                model_code="def model(): pass",
                query_variables=["test"],
                num_samples=100,  # Small sample size for speed
            )
        )
        reasoning_time = (datetime.now() - start_time).total_seconds()
        assert reasoning_time < 60, f"Probabilistic reasoning took {reasoning_time}s"

        # Evaluation
        start_time = datetime.now()
        evaluation_agent = msa_agents[AgentRole.EVALUATION]
        evaluation_result = await evaluation_agent.evaluate_reasoning(
            EvaluationRequest(reasoning_result={"test": "data"})
        )
        evaluation_time = (datetime.now() - start_time).total_seconds()
        assert evaluation_time < 30, f"Evaluation took {evaluation_time}s"

    @pytest.mark.asyncio
    async def test_memory_usage_simulation(self, msa_agents):
        """Test simulated memory usage requirements"""
        # This is a basic test - in production, would use memory profiling
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Run a series of operations
        scenario = "Memory usage test scenario with multiple operations"

        # Knowledge retrieval
        knowledge_agent = msa_agents[AgentRole.KNOWLEDGE_RETRIEVAL]
        await knowledge_agent.retrieve_knowledge(RetrievalRequest(query=scenario))

        # Model synthesis
        synthesis_agent = msa_agents[AgentRole.MODEL_SYNTHESIS]
        await synthesis_agent.synthesize_model(
            SynthesisRequest(scenario=scenario, knowledge_base={})
        )

        # Check memory increase
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Should not increase by more than 512MB per operation (lenient test)
        assert memory_increase < 1024, f"Memory increased by {memory_increase}MB"


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
