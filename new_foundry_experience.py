# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os

from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
from azure.identity.aio import AzureCliCredential

"""
Azure AI Agent with Existing Agent Example

This sample demonstrates working with pre-existing Azure AI Agents by using provider.get_agent() method,
showing agent reuse patterns for production scenarios.
"""


async def using_provider_get_agent() -> None:
    print("=== Get existing Azure AI agent with provider.get_agent() ===")

    # Create the client
    async with (
        AzureCliCredential() as credential,
        AIProjectClient(endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"], credential=credential) as project_client,
    ):
        # Create remote agent using SDK directly
        azure_ai_agent = await project_client.agents.create_version(
            agent_name="AGENT",
            description="Agent for testing purposes.",
            definition=PromptAgentDefinition(
                model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
                # Setting specific requirements to verify that this agent is used.
                instructions="End each response with [END].",
            ),
        )

        openai_client = project_client.get_openai_client()
        response = await openai_client.responses.create(
            input="What is Microsoft Fabric?",
            extra_body={"agent": {"name": azure_ai_agent.name, "type": "agent_reference"}},
        )

        text = getattr(response, "output_text", None)
        if not text:
            output_items = getattr(response, "output", None) or []
            for item in output_items:
                if getattr(item, "type", None) == "message":
                    for part in getattr(item, "content", []) or []:
                        if getattr(part, "type", None) == "output_text":
                            text = (text or "") + getattr(part, "text", "")

        print(f"Agent: {text or response}\n")
        # Clean up the agent manually
        # await project_client.agents.delete_version(
        #     agent_name=azure_ai_agent.name, agent_version=azure_ai_agent.version
        # )


async def main() -> None:
    await using_provider_get_agent()


if __name__ == "__main__":
    os.environ.setdefault(
        "AZURE_AI_PROJECT_ENDPOINT",
        "https://<YOUR_FOUNDRY>.services.ai.azure.com/api/projects/proj-default",
    )
    os.environ.setdefault("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4.1")
    asyncio.run(main())
