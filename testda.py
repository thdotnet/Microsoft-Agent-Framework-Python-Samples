from testfabricagent import FabricDataAgentClientNew

# Initialize the client (uses DefaultAzureCredential for authentication)
client = FabricDataAgentClientNew(
    tenant_id="",
    data_agent_url="https://api.fabric.microsoft.com/v1/workspaces/{WORKSPACE_ID}/dataagents/{DATA_AGENT_ID}/aiassistant/openai"
)

# Ask a simple question
response = client.ask("top 3 customers by sales?")
print(response)
