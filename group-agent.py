from agent_framework import GroupChatBuilder
from azure.identity import AzureCliCredential

import asyncio
import os
import sys

from agent_framework import (
    AgentRunEvent,
    Role,
)
from agent_framework.azure import AzureAIAgentClient

# Ensure required Azure AI configuration is available before client initialization
os.environ.setdefault(
    "AZURE_AI_PROJECT_ENDPOINT",
    "https://<YOUR_FOUNDRY>.services.ai.azure.com/api/projects/proj-default",
)
os.environ.setdefault("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4.1")

# Initialize the Azure OpenAI chat client
credential = AzureCliCredential()
chat_client = AzureAIAgentClient(credential=credential)


# Refund specialist: Handles refund requests
researcher  = chat_client.create_agent(
    instructions="Collects relevant background information.",
    description="Gather concise facts that help a teammate answer the question.",
    name="Writer",

)

# Order/shipping specialist: Resolves delivery issues
writer = chat_client.create_agent(
    instructions="Synthesizes a polished answer using the gathered notes.",
    description="Compose clear and structured answers using any notes provided.",
    name="Researcher",
)

def stop_after_writer(conversation):
    return any(
        msg.role == Role.ASSISTANT and msg.author_name == writer.name
        for msg in conversation
    )

workflow = (
    GroupChatBuilder()
    .set_manager(
        chat_client.create_agent(
            name="Orchestrator",
            instructions="You are a helpful assistant. Route queries to the appropriate specialist agents based on the problem described."
        ),
        display_name="Orchestrator",
    )
    .participants([researcher, writer])
    .with_termination_condition(stop_after_writer)
    .with_max_rounds(6)
    .build()
)

async def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)
    task = "Outline the core considerations for planning a community hackathon, and finish with a concise action plan."

    print("\nStarting Group Chat Workflow...\n", flush=True)
    print(f"Input: {task}\n", flush=True)

    try:
        workflow_agent = workflow.as_agent(name="GroupChatWorkflowAgent")
        agent_result = await workflow_agent.run(task)

        if agent_result.messages:
            print("\n===== as_agent() Transcript =====", flush=True)
            for i, msg in enumerate(agent_result.messages, start=1):
                role_value = getattr(msg.role, "value", msg.role)
                speaker = msg.author_name or role_value
                print(f"{'-' * 50}\n{i:02d} [{speaker}]\n{msg.text}", flush=True)

    except Exception as e:
        print(f"Workflow execution failed: {e}", flush=True)
    finally:
        await chat_client.close()


if __name__ == "__main__":
    asyncio.run(main())
