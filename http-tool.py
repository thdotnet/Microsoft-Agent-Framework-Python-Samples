from fastapi import FastAPI, Query

from fabric_data_agent_client import FabricDataAgentClient
from fabric_data_agent_client import FabricDataAgentClient

app = FastAPI()

@app.get("/fabric")
def echo(text: str = Query(..., min_length=1, description="query to ask Fabric Data Agent")):
    client = FabricDataAgentClient(
        tenant_id="",
        data_agent_url="https://api.fabric.microsoft.com/v1/workspaces/{workspaceid}/dataagents/{dataagentid}/aiassistant/openai"
    )

    # Ask a simple question
    response = client.ask(text)
    return {"response": response}

@app.get("/")
def root():
    return {"status": "ok"}
