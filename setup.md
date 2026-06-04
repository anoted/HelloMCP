# Module 1 Setup: Local Model + HelloMCP

## Practical / Hands-On Requirements

* Install and configure a Python environment manager.

  * In-class default: `conda` with Miniconda.
  * Acceptable alternative: a local `venv`.
  * Use a dedicated course environment instead of installing packages globally.

* Install the Python packages needed by the Module 1 examples.

  * `mcp[cli]` for the HelloMCP server and MCP clients.
  * `python-dotenv` for `.env` files.
  * `openai` for the model-only connection check in `base_openai.py`.
  * Optional: `ipykernel` for Jupyter notebooks.

* Configure the OpenAI-compatible model endpoint.

  * Model: `Qwen/Qwen3.6-35B-A3B`
  * Endpoint format: `http://<MODEL_SERVER_IP>:<PORT>/v1`
  * HelloMCP clients use `OPENAI_MODEL`.
  * `base_openai.py` uses `MODEL_NAME`.

* Configure and run HelloMCP.

  * Current server file: `HelloMCP/hello_mcp_server.py`
  * Default MCP endpoint: `http://127.0.0.1:8765/mcp`
  * Default health check: `http://127.0.0.1:8765/healthz`
  * Current MCP tools: `calculator.add`, `calculator.subtract`, `calculator.log`

* Optional: install OpenCode and configure it to use the running HelloMCP server as a remote MCP server.

---

## 1. Create the Python Environment

### Option A: Conda

```bash
conda create -n mcpagents python=3.11 -y
conda activate mcpagents
```

### Option B: Local venv

PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

Check the environment:

```bash
python --version
python -m pip --version
```

---

## 2. Install Required Packages

```bash
python -m pip install --upgrade pip
python -m pip install "mcp[cli]>=1.23.0,<2.0.0" python-dotenv openai ipykernel
```

If you do not plan to use Jupyter, `ipykernel` may be omitted:

```bash
python -m pip install "mcp[cli]>=1.23.0,<2.0.0" python-dotenv openai
```

Optional Jupyter kernel registration:

```bash
python -m ipykernel install --user --name mcp-agents --display-name "Python (mcp-agents)"
```

---

## 3. Configure HelloMCP Environment Variables

Create this file:

```text
HelloMCP/.env
```

Add the model and MCP settings:

```env
OPENAI_HOST=<MODEL_SERVER_IP>
OPENAI_PORT=<PORT>
OPENAI_BASE_URL=http://<MODEL_SERVER_IP>:<PORT>/v1
OPENAI_API_KEY=local-not-needed
OPENAI_MODEL=Qwen/Qwen3.6-35B-A3B
MODEL_NAME=Qwen/Qwen3.6-35B-A3B

HELLO_MCP_HOST=127.0.0.1
HELLO_MCP_PORT=8765
HELLO_MCP_PATH=/mcp
HELLO_MCP_URL=http://127.0.0.1:8765/mcp
```

Example only:

```env
OPENAI_HOST=192.168.1.50
OPENAI_PORT=8000
OPENAI_BASE_URL=http://192.168.1.50:8000/v1
OPENAI_API_KEY=local-not-needed
OPENAI_MODEL=Qwen/Qwen3.6-35B-A3B
MODEL_NAME=Qwen/Qwen3.6-35B-A3B

HELLO_MCP_HOST=127.0.0.1
HELLO_MCP_PORT=8765
HELLO_MCP_PATH=/mcp
HELLO_MCP_URL=http://127.0.0.1:8765/mcp
```

Use a bare host name or IP address for `OPENAI_HOST`; do not include `http://` or `/v1` there.

If you need to match older demo notes that use `http://localhost:8000/mcp`, set:

```env
HELLO_MCP_PORT=8000
HELLO_MCP_URL=http://127.0.0.1:8000/mcp
```

---

## 4. Start the HelloMCP Server

Open terminal 1, activate the environment, and start the server:

PowerShell:

```powershell
conda activate mcpagents
python HelloMCP\hello_mcp_server.py
```

macOS/Linux:

```bash
conda activate mcpagents
python HelloMCP/hello_mcp_server.py
```

Leave this terminal open. The server should print:

```text
Starting HelloMCP at http://127.0.0.1:8765/mcp
Health check: http://127.0.0.1:8765/healthz
```

In a second terminal, check the health endpoint.

PowerShell:

```powershell
Invoke-RestMethod http://127.0.0.1:8765/healthz
```

macOS/Linux:

```bash
curl http://127.0.0.1:8765/healthz
```

Expected response:

```json
{
  "status": "ok",
  "server": "HelloMCP",
  "mcp_url": "http://127.0.0.1:8765/mcp"
}
```

---

## 5. Run the HelloMCP Chat Client

Open terminal 2 and activate the same Python environment.

PowerShell:

```powershell
conda activate mcpagents
python HelloMCP\hello_client.py
```

Streaming client:

```powershell
python HelloMCP\hello_client_stream.py
```

macOS/Linux:

```bash
conda activate mcpagents
python HelloMCP/hello_client.py
```

Streaming client:

```bash
python HelloMCP/hello_client_stream.py
```

Try prompts such as:

```text
Use the calculator tool to add 12.5 and 30.
Use the calculator tool to subtract 4 from 19.
Use the calculator tool to compute the natural log of 10.
```

The practical checkpoint is complete when:

* The HelloMCP health endpoint returns `status: ok`.
* The client prints the model endpoint and MCP endpoint.
* The model calls one of the MCP calculator tools and returns a final answer.

---

## 6. Optional Model-Only Connection Check

`base_openai.py` reads `.env` from the project root, not from `HelloMCP/.env`.

Create this file if you want to run the model-only check:

```text
.env
```

Add:

```env
OPENAI_BASE_URL=http://<MODEL_SERVER_IP>:<PORT>/v1
OPENAI_API_KEY=local-not-needed
MODEL_NAME=Qwen/Qwen3.6-35B-A3B
```

Run:

```bash
python base_openai.py
```

---

## 7. Optional OpenCode Installation

Install OpenCode with one supported method.

Official install script:

```bash
curl -fsSL https://opencode.ai/install | bash
```

Alternative using npm:

```bash
npm install -g opencode-ai
```

Check installation:

```bash
opencode --version
```

---

## 8. Optional OpenCode Configuration

Start `HelloMCP/hello_mcp_server.py` before using OpenCode with the MCP server.

Create or edit:

```text
~/.config/opencode/opencode.json
```

Add or merge this MCP entry:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "HelloMCP": {
      "type": "remote",
      "url": "http://127.0.0.1:8765/mcp",
      "enabled": true
    }
  }
}
```

If OpenCode also needs the local Qwen provider, merge the provider and MCP settings into one JSON file:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "local-qwen": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Local Qwen",
      "options": {
        "baseURL": "http://<MODEL_SERVER_IP>:<PORT>/v1"
      },
      "models": {
        "Qwen/Qwen3.6-35B-A3B": {
          "name": "Qwen 3.6 35B A3B"
        }
      }
    }
  },
  "mcp": {
    "HelloMCP": {
      "type": "remote",
      "url": "http://127.0.0.1:8765/mcp",
      "enabled": true
    }
  }
}
```

Check that OpenCode sees the MCP server:

```bash
opencode mcp list
```

Start OpenCode:

```bash
opencode
```

Inside OpenCode, ask:

```text
Use HelloMCP to calculate 12 + 30.
```

[1]: https://opencode.ai/docs/config/ "OpenCode Config"
[2]: https://opencode.ai/docs/cli/ "OpenCode CLI"
