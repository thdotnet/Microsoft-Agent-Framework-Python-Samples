from agent_framework import HandoffBuilder
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential

import asyncio
import os

from agent_framework import (
    AgentRunResponse,
    AgentRunEvent,
    ChatAgent,
    ChatMessage,
    HandoffBuilder,
    RequestInfoEvent,
    WorkflowEvent,
    WorkflowOutputEvent,
    WorkflowRunState,
    WorkflowStatusEvent,
    ai_function,
)
from typing import Annotated
from fabric_data_agent_client import FabricDataAgentClient
from agent_framework.azure import AzureAIAgentClient
from agent_framework import (
    WorkflowBuilder,
    WorkflowOutputEvent,
    AgentRunUpdateEvent,
)

# Ensure required Azure AI configuration is available before client initialization
os.environ.setdefault(
    "AZURE_AI_PROJECT_ENDPOINT",
    "https://<your-foundry-name>.services.ai.azure.com/api/projects/<project-name>",
)
os.environ.setdefault("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4.1")


@ai_function
def get_cities_by_sales(query: Annotated[str, "query to ask Fabric Data Agent"]) -> Annotated[str, "Returns the cities by sales."]:
	"""Simple tool function used by the agent.
	
	test
	"""
	
	client = FabricDataAgentClient(
		tenant_id="", #your tenantid
		data_agent_url="https://api.fabric.microsoft.com/v1/workspaces/{workspaceid}/dataagents/{dataagentid}/aiassistant/openai"
	)

	# Ask a simple question
	response = client.ask(query)
	
	return f"{response}."


@ai_function
def get_customer_by_sales(query: Annotated[str, "query to ask Fabric Data Agent"]) -> Annotated[str, "Returns the customers by sales."]:
	"""Simple tool function used by the agent.
	
	test
	"""
	
	client = FabricDataAgentClient(
		tenant_id="", #your tenantid
		data_agent_url="https://api.fabric.microsoft.com/v1/workspaces/{workspaceid}/dataagents/{dataagentid}/aiassistant/openai"
	)

	# Ask a simple question
	response = client.ask(query)

	return f"{response}."

# Initialize the Azure OpenAI chat client
credential = AzureCliCredential()
chat_client = AzureAIAgentClient(credential=credential)

# Create triage/coordinator agent
triage_agent = chat_client.create_agent(
    instructions=(
        "You are a helpful assistant. Route queries to the appropriate specialist agents "
        "based on the problem described."
    ),
    description="Orchestrator agent that handles general inquiries.",
    name="orchestrator_agent",
)

# Refund specialist: Handles refund requests
customers_agent = chat_client.create_agent(
    instructions="You provide insights from customer sales data.",
    description="Agent interacts with customers sales data.",
    name="customers_agent",
    # In a real application, an agent can have multiple tools; here we keep it simple
    tools=[get_customer_by_sales],
)

# Order/shipping specialist: Resolves delivery issues
cities_agent = chat_client.create_agent(
    instructions="You provide insights from cities  sales data.",
    description="Agent interacts with cities sales data.",
    name="cities_agent",
    # In a real application, an agent can have multiple tools; here we keep it simple
    tools=[get_cities_by_sales],
)

workflow = (
    HandoffBuilder(
        name="customer_support_handoff",
        participants=[triage_agent, customers_agent, cities_agent],
    )
    .set_coordinator(triage_agent) # Triage receives initial user input
    .with_termination_condition(
        # Custom termination: Check if one of the agents has provided a closing message.
        # This looks for the last message containing "welcome", which indicates the
        # conversation has concluded naturally.
        lambda conversation: len(conversation) > 0 and "welcome" in conversation[-1].text.lower()
    )
    # Triage cannot route directly to refund agent
    .add_handoff(triage_agent, [customers_agent, cities_agent])
    # All specialists can handoff back to triage for further routing
    .add_handoff(customers_agent, [triage_agent])
    .add_handoff(cities_agent, [triage_agent])
    .build()
)

async def main():
    try:
        events = await workflow.run("top 3 customers by sales.")
        # Print agent run events and final outputs
        for event in events:
            if isinstance(event, AgentRunEvent):
                print(f"{event.executor_id}: {event.data}")

        print(f"{'=' * 60}\nWorkflow Outputs: {events.get_outputs()}")
        # Summarize the final run state (e.g., COMPLETED)
        print("Final state:", events.get_final_state())
    finally:
        # Ensure Azure AI client resources are properly released
        await chat_client.close()


if __name__ == "__main__":
    asyncio.run(main())
