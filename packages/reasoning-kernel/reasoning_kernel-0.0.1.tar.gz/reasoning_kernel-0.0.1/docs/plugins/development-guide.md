# Plugin Development Guide

## Overview

This guide explains how to develop plugins for the Reasoning Kernel using the latest Microsoft Semantic Kernel patterns. All reasoning capabilities are implemented as SK plugins with agent integration, memory support, and secure execution capabilities.

## Modern Plugin Architecture

### Agent-Integrated Plugin Structure

All reasoning plugins are designed to work with SK Chat Completion Agents:

```python
from semantic_kernel import Kernel
from semantic_kernel.functions import kernel_function
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.google.google_ai import GoogleAIChatCompletion
from semantic_kernel.connectors.memory.redis import RedisMemoryStore
from typing import Annotated, Optional, Dict, Any
import logging
import asyncio

class ReasoningPluginBase:
    """Base class for all reasoning plugins with agent integration"""
    
    def __init__(
        self, 
        agent: Optional[ChatCompletionAgent] = None,
        memory_store: Optional[RedisMemoryStore] = None,
        sandbox_client: Optional[Any] = None
    ):
        self.agent = agent
        self.memory = memory_store
        self.sandbox = sandbox_client
        self.logger = logging.getLogger(self.__class__.__name__)
        self._initialize()
    
    def _initialize(self):
        """Override for plugin-specific initialization"""
        pass
    
    @kernel_function(
        name="get_capabilities",
        description="Get plugin capabilities and supported reasoning types"
    )
    async def get_capabilities(self) -> str:
        """Return plugin capabilities"""
        return f"Agent-integrated plugin: {self.__class__.__name__}"
```

### Memory-Enhanced Functions

Use SK memory integration for context-aware reasoning:

```python
@kernel_function(
    name="memory_enhanced_reasoning",
    description="Perform reasoning with memory context retrieval"
)
async def memory_enhanced_reasoning(
    self,
    input_text: Annotated[str, "The input to analyze"],
    reasoning_type: Annotated[str, "Type of reasoning to apply"] = "abstract",
    use_memory: Annotated[bool, "Whether to use memory context"] = True
) -> str:
    """Reasoning with automatic memory integration."""
    
    memory_context = ""
    if use_memory and self.memory:
        # Search for relevant context
        relevant_memories = await self.memory.search(
            collection=f"{reasoning_type}_patterns",
            query=input_text,
            limit=3,
            min_relevance_score=0.75
        )
        
        if relevant_memories:
            memory_context = "\n".join([
                f"Previous pattern: {mem.text}" 
                for mem in relevant_memories
            ])
    
    # Combine input with memory context
    enhanced_prompt = f"""
    Input: {input_text}
    
    {f"Relevant context from memory:{chr(10)}{memory_context}" if memory_context else ""}
    
    Apply {reasoning_type} reasoning to analyze this input.
    """
    
    # Use agent for reasoning if available
    if self.agent:
        response = await self.agent.get_response(enhanced_prompt)
        result = response.content
    else:
        # Fallback to direct processing
        result = await self._direct_reasoning(enhanced_prompt, reasoning_type)
    
    # Store successful patterns for future use
    if self.memory and len(result) > 50:  # Quality threshold
        await self.memory.save_information(
            collection=f"{reasoning_type}_patterns",
            id=f"pattern_{asyncio.get_event_loop().time()}",
            text=f"Input: {input_text}\nReasoning: {result}",
            description=f"{reasoning_type} reasoning pattern"
        )
    
    return result
```

### Sandbox-Enabled Functions

Integrate secure code execution with Daytona sandbox:

```python
@kernel_function(
    name="execute_reasoning_analysis",
    description="Execute analytical code in secure sandbox environment"
)
async def execute_reasoning_analysis(
    self,
    analysis_code: Annotated[str, "Python code for analysis"],
    data_context: Annotated[str, "Data context for the analysis"] = "",
    timeout: Annotated[int, "Execution timeout in seconds"] = 120
) -> str:
    """Execute reasoning analysis code in secure sandbox."""
    
    if not self.sandbox:
        return "Error: Sandbox not available"
    
    # Prepare safe execution environment
    safe_code = f"""
# Analysis context
context = '''{data_context}'''

# User analysis code
{analysis_code}
"""
    
    try:
        # Execute in sandbox with resource limits
        result = await self.sandbox.execute_code(
            code=safe_code,
            environment="python3.12",
            timeout=timeout
        )
        
        if "stdout" in result:
            return result["stdout"]
        else:
            return f"Execution completed: {str(result)}"
            
    except Exception as e:
        self.logger.error(f"Sandbox execution failed: {e}")
        return f"Execution error: {str(e)}"
```

## Plugin Examples

### Abstract Reasoning Plugin

Complete example with latest SK patterns:

```python
from semantic_kernel.functions import kernel_function
from typing import Annotated

class AbstractReasoningPlugin(ReasoningPluginBase):
    """Plugin for abstract pattern recognition and reasoning."""
    
    def _initialize(self):
        """Initialize abstract reasoning capabilities."""
        self.pattern_types = [
            "structural", "functional", "temporal", 
            "causal", "analogical", "hierarchical"
        ]
    
    @kernel_function(
        name="extract_abstract_patterns",
        description="Extract abstract patterns from input using memory-enhanced analysis"
    )
    async def extract_patterns(
        self,
        input_text: Annotated[str, "Text to analyze for patterns"],
        pattern_type: Annotated[str, "Type of pattern to extract"] = "structural",
        depth: Annotated[int, "Analysis depth (1-5)"] = 3
    ) -> str:
        """Extract abstract patterns with memory integration."""
        
        # Validate pattern type
        if pattern_type not in self.pattern_types:
            return f"Error: Unsupported pattern type. Use: {', '.join(self.pattern_types)}"
        
        # Use memory-enhanced reasoning
        result = await self.memory_enhanced_reasoning(
            input_text=input_text,
            reasoning_type=f"abstract_{pattern_type}"
        )
        
        return result
    
    @kernel_function(
        name="analogical_mapping",
        description="Create analogical mappings between concepts"
    )
    async def create_analogical_mapping(
        self,
        source_concept: Annotated[str, "Source concept or domain"],
        target_concept: Annotated[str, "Target concept or domain"],
        mapping_type: Annotated[str, "Type of mapping"] = "structural"
    ) -> str:
        """Create analogical mappings between concepts."""
        
        prompt = f"""
        Create an analogical mapping between:
        Source: {source_concept}
        Target: {target_concept}
        
        Mapping type: {mapping_type}
        
        Identify:
        1. Structural similarities
        2. Functional correspondences  
        3. Relational mappings
        4. Conceptual alignments
        """
        
        if self.agent:
            response = await self.agent.get_response(prompt)
            return response.content
        
        return f"Analogical mapping from {source_concept} to {target_concept}"
    
    @kernel_function(
        name="pattern_analysis_code",
        description="Generate and execute code for pattern analysis"
    )
    async def generate_analysis_code(
        self,
        data_description: Annotated[str, "Description of data to analyze"],
        analysis_goal: Annotated[str, "Goal of the analysis"]
    ) -> str:
        """Generate and execute pattern analysis code."""
        
        # Generate analysis code using agent
        code_prompt = f"""
        Generate Python code to analyze patterns in data.
        
        Data: {data_description}
        Goal: {analysis_goal}
        
        Requirements:
        - Use only safe libraries (numpy, pandas, matplotlib, sklearn)
        - Include error handling
        - Return structured results
        - No file I/O operations
        """
        
        if self.agent:
            code_response = await self.agent.get_response(code_prompt)
            generated_code = code_response.content
            
            # Execute generated code in sandbox
            execution_result = await self.execute_reasoning_analysis(
                analysis_code=generated_code,
                data_context=data_description
            )
            
            return f"Generated Code:\n{generated_code}\n\nExecution Result:\n{execution_result}"
        
        return "Agent not available for code generation"
```

### Multi-Agent Plugin Integration

Example of plugin working with multiple agents:

```python
class MultiAgentReasoningPlugin(ReasoningPluginBase):
    """Plugin that coordinates multiple reasoning agents."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agent_pool = {}
    
    def register_agent(self, agent_type: str, agent: ChatCompletionAgent):
        """Register a specialized agent."""
        self.agent_pool[agent_type] = agent
    
    @kernel_function(
        name="collaborative_reasoning",
        description="Coordinate multiple agents for collaborative reasoning"
    )
    async def collaborative_reasoning(
        self,
        problem: Annotated[str, "Problem to solve collaboratively"],
        agent_types: Annotated[list, "Types of agents to involve"] = None
    ) -> str:
        """Coordinate multiple agents for complex reasoning."""
        
        if not agent_types:
            agent_types = list(self.agent_pool.keys())
        
        results = {}
        
        # Get input from each agent type
        for agent_type in agent_types:
            if agent_type in self.agent_pool:
                agent = self.agent_pool[agent_type]
                
                specialized_prompt = f"""
                As a {agent_type} reasoning specialist, analyze:
                {problem}
                
                Provide your specialized perspective and insights.
                """
                
                response = await agent.get_response(specialized_prompt)
                results[agent_type] = response.content
        
        # Synthesize results
        if self.agent:
            synthesis_prompt = f"""
            Synthesize the following specialized reasoning perspectives:
            
            {chr(10).join([f"{agent_type}: {result}" for agent_type, result in results.items()])}
            
            Provide a unified, comprehensive analysis.
            """
            
            synthesis = await self.agent.get_response(synthesis_prompt)
            return synthesis.content
        
        return str(results)
```

## Testing Strategies

### Unit Testing with SK Patterns

```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from semantic_kernel.agents import ChatCompletionAgent

class TestAbstractReasoningPlugin:
    """Test suite for Abstract Reasoning Plugin."""
    
    @pytest.fixture
    async def plugin(self):
        """Create test plugin instance."""
        mock_agent = AsyncMock(spec=ChatCompletionAgent)
        mock_memory = AsyncMock()
        mock_sandbox = AsyncMock()
        
        plugin = AbstractReasoningPlugin(
            agent=mock_agent,
            memory_store=mock_memory,
            sandbox_client=mock_sandbox
        )
        
        return plugin
    
    @pytest.mark.asyncio
    async def test_extract_patterns(self, plugin):
        """Test pattern extraction functionality."""
        
        # Mock agent response
        mock_response = MagicMock()
        mock_response.content = "Extracted patterns: structural hierarchy"
        plugin.agent.get_response.return_value = mock_response
        
        # Test function
        result = await plugin.extract_patterns(
            input_text="Test input",
            pattern_type="structural"
        )
        
        assert "structural hierarchy" in result
        plugin.agent.get_response.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_sandbox_integration(self, plugin):
        """Test sandbox code execution."""
        
        # Mock sandbox response
        plugin.sandbox.execute_code.return_value = {
            "stdout": "Analysis complete",
            "execution_time": 1.5
        }
        
        result = await plugin.execute_reasoning_analysis(
            analysis_code="print('test')",
            data_context="test data"
        )
        
        assert "Analysis complete" in result
        plugin.sandbox.execute_code.assert_called_once()
```

## Best Practices

### 1. Agent Integration

- Always provide fallback mechanisms when agents are unavailable
- Use appropriate agent types for specific reasoning tasks
- Implement proper error handling for agent communication

### 2. Memory Management

- Use descriptive collection names for memory storage
- Implement relevance scoring for memory retrieval
- Clean up stale memory entries periodically

### 3. Sandbox Security

- Validate all code before sandbox execution
- Implement proper resource limits and timeouts
- Use secure code patterns and avoid dangerous operations

### 4. Performance Optimization

- Cache frequently used memory patterns
- Implement async/await patterns throughout
- Use connection pooling for Redis memory store

### 5. Monitoring and Logging

- Implement structured logging with SK context
- Monitor agent response times and memory usage
- Track sandbox execution metrics

This modern plugin architecture leverages the latest Semantic Kernel capabilities for building sophisticated, secure, and memory-enhanced reasoning systems.
async def function_name(
    self,
    parameter: Annotated[str, "Parameter description"],
    optional_param: Annotated[Optional[int], "Optional parameter"] = None
) -> str:
    """Function implementation"""
    pass

```

## Creating a Reasoning Plugin

### Step 1: Plugin Structure

Create the plugin directory structure:

```

src/plugins/reasoning/my_reasoning/
├── __init__.py
├── plugin.py          # Main plugin class
├── functions.py       # Helper functions
├── models.py          # Data models
└── prompts/           # Semantic function prompts
    ├── analyze.yaml
    └── synthesize.yaml

```

### Step 2: Implement Plugin Class

```python
# filepath: src/plugins/reasoning/my_reasoning/plugin.py
from typing import Annotated, Optional, Dict, Any, List
from semantic_kernel import Kernel
from semantic_kernel.functions import kernel_function
from semantic_kernel.kernel_pydantic import KernelBaseModel
from pydantic import Field
import json

class MyReasoningPlugin(KernelBaseModel):
    """Plugin for my specific reasoning type"""
    
    def __init__(self, kernel: Optional[Kernel] = None):
        super().__init__()
        self.kernel = kernel
        self.cache: Dict[str, Any] = {}
        
    @kernel_function(
        name="analyze_input",
        description="Analyze input data for reasoning patterns"
    )
    async def analyze_input(
        self,
        input_data: Annotated[str, "The input to analyze"],
        analysis_type: Annotated[Optional[str], "Type of analysis"] = "comprehensive"
    ) -> str:
        """Analyze input data using reasoning patterns"""
        
        # Use semantic function for analysis
        semantic_function = self.kernel.create_function_from_prompt(
            prompt_template=self._get_analysis_prompt(),
            function_name="analyze_data",
            plugin_name="my_reasoning"
        )
        
        # Execute semantic function
        result = await self.kernel.invoke(
            semantic_function,
            input_data=input_data,
            analysis_type=analysis_type
        )
        
        # Process and return result
        return self._process_analysis_result(str(result))
    
    @kernel_function(
        name="generate_hypothesis",
        description="Generate hypotheses based on analysis"
    )
    async def generate_hypothesis(
        self,
        analysis_result: Annotated[str, "Previous analysis result"],
        num_hypotheses: Annotated[int, "Number of hypotheses to generate"] = 3
    ) -> str:
        """Generate hypotheses from analysis"""
        
        # Use planner for multi-step hypothesis generation
        planner = self.kernel.create_new_stepwise_planner()
        
        hypothesis_goal = f"""
        Based on the analysis: {analysis_result}
        Generate {num_hypotheses} well-reasoned hypotheses that:
        1. Address the core reasoning challenge
        2. Are testable and verifiable
        3. Cover different perspectives
        """
        
        plan = await planner.create_plan(hypothesis_goal)
        result = await plan.invoke_async(self.kernel)
        
        return self._format_hypotheses(str(result))
    
    @kernel_function(
        name="evaluate_reasoning",
        description="Evaluate reasoning quality and confidence"
    )
    async def evaluate_reasoning(
        self,
        reasoning_chain: Annotated[str, "The reasoning chain to evaluate"]
    ) -> str:
        """Evaluate reasoning quality and provide confidence scores"""
        
        evaluation_prompt = """
        Evaluate the following reasoning chain:
        
        {{$reasoning_chain}}
        
        Provide evaluation on:
        1. Logical consistency (0-1)
        2. Evidence support (0-1)  
        3. Completeness (0-1)
        4. Clarity (0-1)
        5. Overall confidence (0-1)
        
        Return as JSON with scores and explanations.
        """
        
        evaluation_function = self.kernel.create_function_from_prompt(
            prompt_template=evaluation_prompt,
            function_name="evaluate_reasoning",
            plugin_name="my_reasoning"
        )
        
        result = await self.kernel.invoke(
            evaluation_function,
            reasoning_chain=reasoning_chain
        )
        
        return str(result)
    
    def _get_analysis_prompt(self) -> str:
        """Get the analysis prompt template"""
        return """
        Analyze the following input for reasoning patterns:
        
        Input: {{$input_data}}
        Analysis Type: {{$analysis_type}}
        
        Identify:
        1. Key entities and relationships
        2. Causal connections
        3. Temporal sequences
        4. Constraints and assumptions
        5. Uncertainty sources
        
        Format as structured JSON.
        """
    
    def _process_analysis_result(self, result: str) -> str:
        """Process and validate analysis result"""
        try:
            # Validate JSON structure
            data = json.loads(result)
            
            # Add metadata
            data["plugin"] = "my_reasoning"
            data["timestamp"] = "2025-08-14T12:00:00Z"
            
            return json.dumps(data, indent=2)
        except json.JSONDecodeError:
            # Fallback to raw result
            return result
    
    def _format_hypotheses(self, result: str) -> str:
        """Format hypotheses result"""
        # Implementation for formatting hypotheses
        return result
```

### Step 3: Add Data Models

```python
# filepath: src/plugins/reasoning/my_reasoning/models.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class ReasoningType(Enum):
    INDUCTIVE = "inductive"
    DEDUCTIVE = "deductive"
    ABDUCTIVE = "abductive"

class ReasoningInput(BaseModel):
    """Input model for reasoning operations"""
    content: str = Field(..., description="Content to reason about")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    reasoning_type: ReasoningType = Field(ReasoningType.INDUCTIVE, description="Type of reasoning")
    confidence_threshold: float = Field(0.7, description="Minimum confidence threshold")

class ReasoningResult(BaseModel):
    """Result model for reasoning operations"""
    conclusion: str = Field(..., description="Reasoning conclusion")
    confidence: float = Field(..., description="Confidence score (0-1)")
    evidence: List[str] = Field(default_factory=list, description="Supporting evidence")
    assumptions: List[str] = Field(default_factory=list, description="Key assumptions")
    reasoning_chain: List[str] = Field(default_factory=list, description="Step-by-step reasoning")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class Hypothesis(BaseModel):
    """Model for generated hypotheses"""
    statement: str = Field(..., description="Hypothesis statement")
    confidence: float = Field(..., description="Confidence in hypothesis")
    testability: float = Field(..., description="How testable the hypothesis is")
    supporting_factors: List[str] = Field(default_factory=list, description="Supporting factors")
    contradicting_factors: List[str] = Field(default_factory=list, description="Contradicting factors")
```

### Step 4: Semantic Function Prompts

Create YAML prompt files for complex reasoning:

```yaml
# filepath: src/plugins/reasoning/my_reasoning/prompts/analyze.yaml
name: analyze_reasoning_pattern
description: Analyze input for specific reasoning patterns
template: |
  You are an expert reasoning analyst. Analyze the following input for patterns and structures.
  
  Input: {{$input}}
  Focus Area: {{$focus_area}}
  
  Please identify:
  
  1. **Entities**: Key objects, concepts, or actors
  2. **Relationships**: How entities connect and interact
  3. **Patterns**: Recurring structures or sequences
  4. **Causal Links**: Cause-and-effect relationships
  5. **Temporal Aspects**: Time-based sequences or dependencies
  6. **Constraints**: Limitations or boundary conditions
  7. **Uncertainties**: Areas of ambiguity or missing information
  
  Format your response as JSON with clear categorization.
  
  Example format:
  ```json
  {
    "entities": ["entity1", "entity2"],
    "relationships": [{"from": "entity1", "to": "entity2", "type": "causes"}],
    "patterns": ["pattern_type": "description"],
    "causal_links": [{"cause": "event1", "effect": "event2", "strength": 0.8}],
    "temporal_aspects": ["sequence1", "sequence2"],
    "constraints": ["constraint1", "constraint2"],
    "uncertainties": ["area1", "area2"]
  }
  ```

parameters:

- name: input
    description: The input text to analyze
    required: true
- name: focus_area
    description: Specific area to focus analysis on
    required: false
    default: "general"

```

## Plugin Registration

### Step 5: Register with Kernel

```python
# filepath: src/kernel/builder.py (addition)
def with_my_reasoning_plugin(self) -> "KernelBuilder":
    """Add custom reasoning plugin"""
    from plugins.reasoning.my_reasoning import MyReasoningPlugin
    
    plugin = MyReasoningPlugin(self.kernel)
    self.kernel.add_plugin(plugin, "my_reasoning")
    self.logger.info("Added MyReasoning plugin")
    return self
```

### Step 6: Plugin Testing

```python
# filepath: tests/test_my_reasoning_plugin.py
import pytest
from semantic_kernel import Kernel
from src.plugins.reasoning.my_reasoning import MyReasoningPlugin
from src.kernel.builder import KernelBuilder

class TestMyReasoningPlugin:
    
    @pytest.fixture
    async def kernel_with_plugin(self):
        """Create kernel with plugin for testing"""
        kernel = (
            KernelBuilder()
            .with_test_ai_service()  # Mock AI service for testing
            .with_my_reasoning_plugin()
            .build()
        )
        return kernel
    
    @pytest.mark.asyncio
    async def test_analyze_input(self, kernel_with_plugin):
        """Test input analysis function"""
        plugin = kernel_with_plugin.plugins["my_reasoning"]
        
        result = await plugin.analyze_input(
            input_data="A machine breaks down causing production delays",
            analysis_type="causal"
        )
        
        assert result is not None
        assert "entities" in result
        assert "causal_links" in result
    
    @pytest.mark.asyncio
    async def test_generate_hypothesis(self, kernel_with_plugin):
        """Test hypothesis generation"""
        plugin = kernel_with_plugin.plugins["my_reasoning"]
        
        analysis_result = '{"entities": ["machine", "production"], "causal_links": []}'
        
        result = await plugin.generate_hypothesis(
            analysis_result=analysis_result,
            num_hypotheses=2
        )
        
        assert result is not None
        # Add more specific assertions based on expected output
    
    @pytest.mark.asyncio
    async def test_evaluate_reasoning(self, kernel_with_plugin):
        """Test reasoning evaluation"""
        plugin = kernel_with_plugin.plugins["my_reasoning"]
        
        reasoning_chain = "Machine failure -> Production stop -> Revenue loss"
        
        result = await plugin.evaluate_reasoning(reasoning_chain)
        
        assert result is not None
        # Verify evaluation metrics are present
```

## Best Practices

### 1. Function Design

- __Single Responsibility__: Each function should do one thing well
- __Clear Interfaces__: Use type hints and descriptive parameters
- __Error Handling__: Graceful handling of edge cases
- __Documentation__: Comprehensive docstrings and examples

### 2. Semantic Functions

- __Prompt Engineering__: Clear, specific prompts for consistent results
- __Parameter Validation__: Validate inputs before processing
- __Output Formatting__: Consistent JSON output structures
- __Prompt Versioning__: Track prompt changes for reproducibility

### 3. Integration Patterns

- __Memory Integration__: Use SK memory for context and caching
- __Planner Usage__: Leverage planners for complex multi-step operations
- __Service Abstraction__: Use kernel services rather than direct API calls
- __Plugin Composition__: Design for composition with other plugins

### 4. Performance Considerations

- __Caching__: Cache expensive operations appropriately
- __Async/Await__: Use async patterns for I/O operations
- __Batch Processing__: Process multiple items efficiently
- __Resource Management__: Clean up resources properly

### 5. Testing Strategy

- __Unit Tests__: Test individual functions in isolation
- __Integration Tests__: Test plugin interactions with kernel
- __Mock Services__: Use mock AI services for consistent testing
- __Performance Tests__: Measure and validate performance characteristics

## Plugin Distribution

### Package Structure

```
my_reasoning_plugin/
├── setup.py
├── requirements.txt
├── README.md
├── my_reasoning/
│   ├── __init__.py
│   ├── plugin.py
│   ├── models.py
│   └── prompts/
└── tests/
    └── test_plugin.py
```

### Installation

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="my-reasoning-plugin",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "semantic-kernel>=1.0.0",
        "pydantic>=2.0.0",
    ],
    entry_points={
        "reasoning_kernel.plugins": [
            "my_reasoning = my_reasoning.plugin:MyReasoningPlugin"
        ]
    }
)
```

This guide provides a comprehensive foundation for developing robust, testable, and maintainable plugins for the Reasoning Kernel using Semantic Kernel best practices.
