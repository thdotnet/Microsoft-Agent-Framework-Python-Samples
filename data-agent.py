from fabric_data_agent_client import FabricDataAgentClient

# Initialize the client (will open browser for authentication)
client = FabricDataAgentClient(
    tenant_id="", #add your tenant ID in here
    data_agent_url="https://api.fabric.microsoft.com/v1/workspaces/{workspaceid}/dataagents/{data-agent-id}/aiassistant/openai"
)

# Ask a simple question
response = client.ask("top 3 customers by sales?")
print(response)
