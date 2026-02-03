import os
import json
import io

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from agent_framework.azure import AzureAIAgentClient
from azure.identity import DefaultAzureCredential
from pydantic import BaseModel, Field, RootModel, ConfigDict, ValidationError

class CityPopulation(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    city: str
    population: int
    men: int = Field(alias="estimated_men")
    women: int = Field(alias="estimated_women")


class OutputStruct(RootModel[list[CityPopulation]]):
    """Structured output for multiple cities."""
    
app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/chart")
async def render_chart():
    deployment_name = "gpt-4.1"
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

    try:
        result = await agent.run(query, options={"response_format": OutputStruct})

        structured_data = result.value

        if not structured_data and result.text:
            try:
                structured_data = OutputStruct.model_validate(json.loads(result.text))
            except (json.JSONDecodeError, ValidationError):
                structured_data = None

        if not structured_data:
            return {"error": "Failed to parse response", "raw": result.text}

        cities = [entry.city for entry in structured_data.root]
        men = [entry.men for entry in structured_data.root]
        women = [entry.women for entry in structured_data.root]

        fig, ax = plt.subplots(figsize=(8, 4.5))
        x = range(len(cities))
        width = 0.4
        ax.bar([i - width / 2 for i in x], men, width, label="Men")
        ax.bar([i + width / 2 for i in x], women, width, label="Women")

        ax.set_title("Estimated Men/Women Population by City")
        ax.set_xticks(list(x))
        ax.set_xticklabels(cities, rotation=30, ha="right")
        ax.set_ylabel("Estimated population")
        ax.legend()
        fig.tight_layout()

        buffer = io.BytesIO()
        fig.savefig(buffer, format="png", dpi=150)
        plt.close(fig)
        buffer.seek(0)

        return StreamingResponse(buffer, media_type="image/png")
    finally:
        await client.close()
