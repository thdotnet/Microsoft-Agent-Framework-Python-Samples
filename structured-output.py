import os
import json
from agent_framework.azure import AzureAIAgentClient
from azure.identity import DefaultAzureCredential
from pydantic import BaseModel, Field, RootModel, ConfigDict, ValidationError

deployment_name = "gpt-4.1"

class CityPopulation(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    city: str
    population: int
    men: int = Field(alias="estimated_men")
    women: int = Field(alias="estimated_women")


class OutputStruct(RootModel[list[CityPopulation]]):
    """Structured output for multiple cities."""

os.environ.setdefault(
    "AZURE_AI_PROJECT_ENDPOINT",
    "https://<YOUR_FOUNDRY>.services.ai.azure.com/api/projects/proj-default",
)
os.environ.setdefault("AZURE_AI_MODEL_DEPLOYMENT_NAME", deployment_name)
client = AzureAIAgentClient(credential=DefaultAzureCredential())

agent = client.create_agent(
    name="CityAgent",
    instructions=(
        "Return only a JSON array of objects with keys: "
        "city, population, estimated_men, estimated_women. "
        "No extra keys, no markdown, no commentary."
    ),
)

query = "Tell me the top 5 cities in France with the largest population and give me the estimate count of men / women in each city"
print(f"User: {query}")

# Get structured response from the agent using response_format parameter
import asyncio


async def main() -> None:
    try:
        result = await agent.run(query, options={"response_format": OutputStruct})

        structured_data = result.value

        if not structured_data and result.text:
            try:
                structured_data = OutputStruct.model_validate(json.loads(result.text))
            except (json.JSONDecodeError, ValidationError):
                structured_data = None

        if structured_data:
            print("Structured Output Agent:")
            for entry in structured_data.root:
                print(f"City: {entry.city}")
                print(f"Population: {entry.population}")
                print(f"Men: {entry.men}")
                print(f"Women: {entry.women}")
                print("-")
        else:
            print(f"Failed to parse response: {result.text}")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
