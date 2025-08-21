"""'Semantic Kernel MCP Coder Agent"""

"""Connect model with mcp tools using Azure AI Agent (Semantic Kernel SDK) in Python
# Please check this link for the list of supported Foundry models for agentic flow:
# https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/model-region-support
# Run this python script
> pip install semantic-kernel[mcp,azure]
> python <this-script-path>.py
"""
import asyncio
from contextlib import AsyncExitStack
from azure.identity.aio import DefaultAzureCredential
from semantic_kernel.agents import AzureAIAgent, AzureAIAgentThread
from semantic_kernel.contents import FunctionCallContent, FunctionResultContent
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.connectors.mcp import MCPStdioPlugin

# Azure AI Agent Configuration
ENDPOINT = "https://qredence-foundry.services.ai.azure.com/api/projects/agentic-fleet"
MODEL_DEPLOYMENT_NAME = "gpt-5-mini"

AGENT_NAME = "mcp-agent"
AGENT_INSTRUCTIONS = 'You are a senior software architect and AI assistant specializing in:\n- Codebase analysis and optimization\n- System architecture improvement planning\n- API design, implementation, and management\n- MCP (Model Context Protocol) tool development and integration\n- Software development best practices\n\n# Instructions\n- You will receive inputs via these variables:\n  • codebase_overview: a description or snapshot of the codebase (languages, frameworks, modules, patterns)  \n  • api_specifications: existing API docs or interfaces (openapi, graphql schema, endpoints list)  \n  • mcp_tools_details: information about current or planned MCP tools  \n- If any variable is missing or insufficient, ask clarifying questions before proceeding.\n- Continue working until you have fully completed the analysis, plan, API strategy, and MCP tool recommendations.\n- Always ground Azure-related advice using the available Azure tools; do not guess.\n\n# Tool Use Guidelines\n- To retrieve official Azure guidance, call the documentation tool with intent="API management best practices" or other relevant intents.  \n- Use the bestpractices tool before suggesting Azure SDK code snippets.  \n- Tools must be used to fetch authoritative content; do not fabricate references.  \n- Plan your reasoning before each tool invocation and reflect on results before proceeding.\n\n# Output Format\nUse the following XML‐like sections in every response:\n\n<analysis>\n[Step-by-step breakdown of your understanding and reasoning]\n</analysis>\n\n<response>\n- Codebase Analysis: [concise findings on structure, dependencies, bottlenecks]\n- Improvement Plan: [prioritized, actionable recommendations]\n- API Strategy: [design or management approach, tooling, standards]\n- MCP Tools: [proposed or existing MCP tool creation and integration steps]\n</response>'

# User inputs for the conversation
USER_INPUTS = [
    "Analyze the provided codebase and deliver a comprehensive improvement strategy.\n\nInput Variables:\n• codebase_overview: \n• api_specifications: \n• mcp_tools_details: \n\n# Steps\n1. Review codebase_overview to understand architecture, languages, frameworks, modules.  \n2. Identify performance bottlenecks, security vulnerabilities, architectural weaknesses.  \n3. Develop a prioritized improvement plan with tasks, risk/benefit analysis, and estimated effort.  \n4. Propose an API strategy: design patterns, versioning, documentation standards, management tooling.  \n5. Recommend MCP tools: creation or enhancement, integration approach, and usage scenarios.  \n6. Provide implementation guidance, code examples, and references to authoritative Azure documentation where applicable.\n\n# Examples\nExample 1:\nCodebase: E-commerce platform  \nAnalysis: Identified database query optimization opportunities  \nImprovement Plan: Implement caching layer and query indexing  \nAPI Management: Designed RESTful API for inventory management  \nMCP Tools: Created tool for automated performance monitoring  \n\nExample 2:\nCodebase: Data processing pipeline  \nAnalysis: Found redundant data transformations causing delays  \nImprovement Plan: Consolidate data processing steps and parallelize operations  \nAPI Management: Implemented GraphQL API for flexible data access  \nMCP Tools: Developed tool for automatic schema validation  \n\n# Output\nFollow the format defined in the system prompt exactly.",
    "Analyze github repository https://github.com/qredence/agenticfleet",
]


def create_mcp_plugins() -> list:
    return [
        MCPStdioPlugin(
            name="mcp-agent".replace("-", "_"),
            description="MCP server for mcp-agent",
            command="npx",
            args=[
                "-y",
                "@azure/mcp@latest",
                "server",
                "start",
            ],
        ),
        MCPStdioPlugin(
            name="VSCode Tools".replace("-", "_"),
            description="MCP server for VSCode Tools",
            command="INSERT_COMMAND_HERE",
            args=[
                "INSERT_ARGUMENTS_HERE",
            ],
        ),
    ]


async def connect_mcp_plugins(stack: AsyncExitStack) -> list:
    """Connect to MCP servers and return connected plugins"""
    mcp_plugins = create_mcp_plugins()
    print(f"Created {len(mcp_plugins)} MCP plugins")
    print("Connecting to MCP servers...")
    connected_plugins = []
    for i, plugin in enumerate(mcp_plugins):
        print(f"Connecting to {plugin.name}...")
        connected_plugin = await stack.enter_async_context(plugin)
        connected_plugins.append(connected_plugin)
        print(f"{plugin.name} connected successfully.")

    print(f"All {len(connected_plugins)} MCP servers connected!")
    return connected_plugins


async def handle_intermediate_steps(message: ChatMessageContent) -> None:
    if message.items:
        for item in message.items:
            if isinstance(item, FunctionResultContent):
                print(f"Function Result:> {item.result} for function: {item.name}")
            elif isinstance(item, FunctionCallContent):
                print(f"Function Call:> {item.name} with arguments: {item.arguments}")
            else:
                print(f"{item}")


async def create_agent(client, connected_plugins: list) -> AzureAIAgent:
    """Create and configure the Azure AI Agent with MCP plugins"""
    print(f"Creating agent definition for '{AGENT_NAME}'...")

    # Refer to Azure AI Agent docs for adding remote actions (e.g., Code Interpreter, File Search) in Foundry:
    # https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/agent-types/azure-ai-agent?pivots=programming-language-python#advanced-features
    agent_definition = await client.agents.create_agent(
        model=MODEL_DEPLOYMENT_NAME,
        name=AGENT_NAME,
        instructions=AGENT_INSTRUCTIONS,
    )
    print(f"Agent definition created with ID: {agent_definition.id}")

    print("Creating AzureAIAgent instance...")
    agent = AzureAIAgent(
        client=client,
        definition=agent_definition,
        plugins=connected_plugins,
    )
    print("AzureAIAgent instance created.")

    return agent


async def invoke_agent(agent: AzureAIAgent) -> None:
    """Invoke the agent with user inputs"""
    print("Starting conversation with the agent...")

    thread: AzureAIAgentThread = None

    # Process user messages
    for user_input in USER_INPUTS:
        print(f"\n# User: '{user_input}'")
        async for response_chunk in agent.invoke(
            messages=user_input,
            thread=thread,
            on_intermediate_message=handle_intermediate_steps,
        ):
            if response_chunk and response_chunk.content:
                print(f"# [Model Response] {response_chunk.content}")
            if hasattr(response_chunk, "thread") and response_chunk.thread:
                thread = response_chunk.thread

    print("\n--- All tasks completed successfully ---")


# Main Path
async def main() -> None:
    async with AsyncExitStack() as stack:
        # Step 1: Connect to MCP plugins
        connected_plugins = await connect_mcp_plugins(stack)

        async with (
            DefaultAzureCredential() as creds,
            AzureAIAgent.create_client(credential=creds, endpoint=ENDPOINT) as client,
        ):
            # Step 2: Create the agent
            agent = await create_agent(client, connected_plugins)

            # Step 3: Invoke the agent
            await invoke_agent(agent)

    # Give a moment for cleanup to complete
    await asyncio.sleep(0.5)


def run_main():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback

        traceback.print_exc()
    finally:
        print("Program finished.")


if __name__ == "__main__":
    run_main()
