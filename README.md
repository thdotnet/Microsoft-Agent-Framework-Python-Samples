# Microsoft Fabric Data Agent – Python Client and Samples

This repo contains a standalone Python client for calling Microsoft Fabric Data Agents from outside Fabric, plus sample apps showing how to expose a simple HTTP endpoint and how to integrate the client as tools in Azure AI Agent Framework workflows.

Key capabilities:
- Interactive Azure sign-in with automatic token handling.
- Simple `ask()` interface to query a Fabric Data Agent.
- Optional run introspection to extract SQL and preview results.
- FastAPI samples for HTTP integration.
- Azure AI Agent Framework samples with tool handoffs.

## Repo Structure

- [fabric_data_agent_client.py](fabric_data_agent_client.py): Core client that authenticates via `InteractiveBrowserCredential` and calls the Fabric Data Agent OpenAI-compatible endpoint. Provides `ask()`, `get_run_details()`, and `get_raw_run_response()`.
- [data-agent.py](data-agent.py): Minimal sample calling a Fabric Data Agent.
- [http-tool.py](http-tool.py): FastAPI app exposing `GET /fabric?text=...` to proxy queries to a Fabric Data Agent.
- [handoff.py](handoff.py): Workflow sample using tool functions that call Fabric Data Agents, demonstrating handoffs between agents.
- [maf-dataagent.py](maf-dataagent.py): Async Azure AI Agent Framework sample creating an agent with tool functions bound to Fabric Data Agent queries.
- [requirements.txt](requirements.txt): Python dependencies (beta packages included).

## Prerequisites

- Python 3.12 (recommended) on Windows.
- Microsoft Edge/Chrome for interactive sign-in.
- For Agent Framework samples: Azure CLI installed and signed in (`az login`).

## Setup

```powershell
py -3.12 -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

Optional: create a `.env` file for environment variables (see Configuration).

## Configuration

Fabric client requires your tenant and Data Agent URL. You can hardcode them in scripts or provide environment variables:

- `TENANT_ID`: Your Azure tenant ID.
- `DATA_AGENT_URL`: Published URL of your Fabric Data Agent (OpenAI-compatible endpoint).

Example `.env`:

```ini
TENANT_ID=00000000-0000-0000-0000-000000000000
DATA_AGENT_URL=https://api.fabric.microsoft.com/v1/workspaces/<workspace-id>/dataagents/<data-agent-id>/aiassistant/openai
```

Agent Framework samples also use Azure AI Projects configuration. You may override the defaults used in code:

- `AZURE_AI_PROJECT_ENDPOINT`: e.g., `https://<your-subdomain>.services.ai.azure.com/api/projects/<project-name>`
- `AZURE_AI_MODEL_DEPLOYMENT_NAME`: e.g., `gpt-4.1` (must exist in your project)

## Usage

### 1) Call a Fabric Data Agent from Python

Update configuration in [fabric_data_agent_client.py](fabric_data_agent_client.py) or set environment variables, then run either sample:

```powershell
.venv\Scripts\python.exe data-agent.py.py    # top 3 customers by sales
```

The client opens a browser window for interactive authentication and prints the agent’s response to the console.

### 2) Run the HTTP tool (FastAPI)

Starts an HTTP service that forwards queries to your Data Agent.

```powershell
.venv\Scripts\python.exe -m uvicorn http-tool:app --reload --port 9002
```

Endpoints:
- `GET /fabric?text=Your+question` → queries the Data Agent and returns `{ response: "..." }`
- `GET /` → `{ status: "ok" }`

### 3) Azure AI Agent Framework – Handoff workflow

Demonstrates multiple agents with tool functions that call Fabric Data Agents and handoff between them.

Before running:

```powershell
az login
```

Run:

```powershell
.venv\Scripts\python.exe handoff.py
```

### 5) Azure AI Agent Framework – Async tool agent

Creates an agent with tool functions bound to Fabric Data Agent queries and runs a single turn.

```powershell
az login
.venv\Scripts\python.exe maf-dataagent.py
```

## Notes on Authentication

- [fabric_data_agent_client.py](fabric_data_agent_client.py) uses `InteractiveBrowserCredential` to sign in via browser and retrieves tokens for `https://api.fabric.microsoft.com/.default`.
- Agent Framework samples use `AzureCliCredential`; ensure `az login` succeeds in the same environment.

## Troubleshooting

- Authentication window does not open: ensure your default browser is installed and system pop-ups are allowed.
- `TENANT_ID` / `DATA_AGENT_URL` not set: provide them via environment variables or edit the sample scripts.
- Azure AI Agent errors: verify `AZURE_AI_PROJECT_ENDPOINT` and `AZURE_AI_MODEL_DEPLOYMENT_NAME` point to valid resources in your Azure AI project.
- Uvicorn not found: confirm `uvicorn[standard]` is installed (it’s in `requirements.txt`).
- Permission issues calling Fabric Data Agent: ensure your account has access to the workspace and Data Agent.

## Development Tips

- Inspect raw run details and SQL extraction with `get_run_details()` or `get_raw_run_response()` in [fabric_data_agent_client.py](fabric_data_agent_client.py).
- Replace hardcoded IDs in sample files with your own values, or switch to environment variables and `.env` for portability.

---

Happy building with Fabric Data Agents! If you want, I can help wire up more endpoints or add examples that parse SQL results into structured responses.
