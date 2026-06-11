# Assignment 1: Environment Setup, Local Model Connection, OpenCode, and MCP Practice

## Overview

In this assignment, you will set up your course programming environment, connect to the course model endpoint, run or adapt the `HelloMCP` example, create or explain a few simple MCP tools, and demonstrate that a CLI-based AI agent or MCP-capable client can use those tools.

The primary workflow is the Python `HelloMCP` example:

* `HelloMCP/hello_mcp_server.py`
* `HelloMCP/hello_mcp_remote_stream.py`

Students who prefer TypeScript may use the TypeScript alternative described in `typescript_alternative.md`.

## Learning Outcomes

By completing this assignment, you will be able to:

* Set up a clean course programming environment.
* Configure environment variables for an OpenAI-compatible model endpoint.
* Connect to the course model, `Qwen/Qwen3.6-35B-A3B`.
* Send prompts to the model and receive responses.
* Explain the difference between streamed and non-streamed model responses.
* Run, adapt, and explain a simple MCP server.
* Create, adapt, or explain a few simple MCP tools.
* Configure a Python MCP-capable client or OpenCode to use the course model and MCP server.
* Explain your workflow, troubleshooting, and AI-assisted development choices in a short reflection.

## Required Steps

### 1. Verify Your Development Environment

Verify that you have access to:

* Git
* Python 3.10 or higher
* A course environment manager such as Conda, Miniconda, `uv`, `venv`, or another approved option
* A coding environment such as VS Code, Cursor, GitHub Codespaces, or another approved option

### 2. Create a Dedicated Course Environment

Create a dedicated environment for this course. Use an environment name such as:

```text
mcpagents
```

Do not use a global Python installation for the assignment.

### 3. Prepare the Required Python Packages

Prepare the packages needed for the Module 1 examples:

* `mcp[cli]`
* `python-dotenv`
* `openai`
* `ipykernel`, optional for notebook users

The `HelloMCP` example uses FastMCP through the `mcp[cli]` package.

### 4. Create an Assignment Project Folder

Create a project folder for Assignment 1 and keep your assignment files organized inside it.

Suggested contents:

* `.env.example`
* model connection script or notebook
* reflection file
* OpenCode evidence, if used
* MCP server code or reference to the server used
* MCP usage evidence
* screenshots, if used

### 5. Create Environment Configuration Files

Create a `.env.example` file showing the required configuration fields without exposing your real local settings.

Required fields:

```env
LLM_BASE_URL=
LLM_API_KEY=
LLM_MODEL=
LLM_TEMPERATURE=
LLM_STREAM=

MCP_ENABLED=
MCP_SERVERS=
MCP_SHOW_ERRORS=
MCP_CONNECT_TIMEOUT=

HELLO_MCP_HOST=
HELLO_MCP_PORT=
HELLO_MCP_PATH=
```

The `LLM_*` variables configure the OpenAI-compatible model endpoint used by the client.

The `MCP_*` variables configure optional MCP client connections. MCP servers should be listed through `MCP_SERVERS`, not through a single MCP URL variable.

The `HELLO_MCP_*` variables configure the local `HelloMCP` server itself. Do not remove or rename these server configuration fields.

Create a local `.env` file for your own machine using the instructor-provided model server IP address and port.

The model endpoint should follow this format:

```text
http://<MODEL_SERVER_IP>:<PORT>/v1

or

https://integrate.api.nvidia.com/v1

or 

https://generativelanguage.googleapis.com/v1beta/openai


NOTE: NO TRAILING '/'
```

Do not submit your real `.env` file.

Example `.env.example`:

```env
LLM_BASE_URL=
LLM_API_KEY=
LLM_MODEL=Qwen/Qwen3.6-35B-A3B
LLM_TEMPERATURE=0.8
LLM_STREAM=true

MCP_ENABLED=true
MCP_SERVERS=calculator=http://127.0.0.1:8765/mcp
MCP_SHOW_ERRORS=false
MCP_CONNECT_TIMEOUT=1.5

HELLO_MCP_HOST=127.0.0.1
HELLO_MCP_PORT=8765
HELLO_MCP_PATH=/mcp
```

Example local `.env` structure:

```env
LLM_BASE_URL=http://<MODEL_SERVER_IP>:<PORT>/v1
LLM_API_KEY=local-not-needed
LLM_MODEL=gemini-2.5-flash
LLM_TEMPERATURE=0.8
LLM_STREAM=true

MCP_ENABLED=true
MCP_SERVERS=calculator=http://127.0.0.1:8765/mcp
MCP_SHOW_ERRORS=false
MCP_CONNECT_TIMEOUT=1.5

HELLO_MCP_HOST=127.0.0.1
HELLO_MCP_PORT=8765
HELLO_MCP_PATH=/mcp
```

### 6. Connect to the Course Model

Create or adapt a Python model connection script that connects to:

```text
Qwen/Qwen3.6-35B-A3B
```

```text
Check in your api provider - which models are available. 
Google AI Studio may not have OpenAI models available.
```

Your script should:

* Load environment variables from `.env`.
* Connect to the OpenAI-compatible endpoint configured by `LLM_BASE_URL`.
* Use the model name configured by `LLM_MODEL`.
* Send a prompt to the model.
* Receive and print a response.
* Provide evidence that the model connection worked.

You may use `base_openai.py` or the provided `HelloMCP` client code as a starting point.

### 7. Compare Streamed and Non-Streamed Responses

Test model responses in at least one response mode:

* Non-streamed response: the full response returns at once.
* Streamed response: the response appears gradually as the model generates it.

Stronger submissions demonstrate both response modes.

The provided examples are:

* `HelloMCP/hello_client_remote_stream.py`

The updated client may use `LLM_STREAM=true` or `LLM_STREAM=false` to control whether responses are streamed.

### 8. Run the HelloMCP Server

Run the `HelloMCP` server and verify that it is available.

The server should expose a local MCP endpoint and a health-check endpoint.

The `HelloMCP` server configuration uses:

```env
HELLO_MCP_HOST=127.0.0.1
HELLO_MCP_PORT=8765
HELLO_MCP_PATH=/mcp
```

The current `HelloMCP` server includes these tools:

* `calculator.add`
* `calculator.subtract`
* `calculator.log`

When run with the default server configuration, the MCP endpoint is:

```text
http://127.0.0.1:8765/mcp
```

The client should list this server through `MCP_SERVERS`:

```env
MCP_SERVERS=calculator=http://127.0.0.1:8765/mcp
```

### 9. Demonstrate MCP Tool Use

Use the `HelloMCP` client, OpenCode, or another approved MCP-capable CLI agent to demonstrate that the model can call an MCP tool.

Your evidence should show:

* The MCP server was running.
* The client or agent connected to the server.
* The startup output showed which MCP servers were available.
* A prompt caused an MCP tool call.
* The tool returned a result.
* The model or agent used the result in a final response.

The updated Python client should still start even if no MCP servers are available. If an MCP server is unavailable, the client should report it cleanly as unavailable and continue running as a normal chat client.

### 10. Create or Adapt a Few Simple MCP Tools

Create or adapt a simple MCP server with a few small tools. The goal is to practice tool creation and model tool use, not to build a complex application.

Your server should include at least three simple tools total. The existing `HelloMCP` tools may count toward this requirement if you can explain and demonstrate them. You are encouraged to add one or two new tools of your own.

Possible tools include:

* Returning the current date or time.
* Adding, subtracting, multiplying, or dividing numbers.
* Calculating a natural logarithm.
* Formatting text.
* Returning a course-related message.
* Looking up a value from a small local dictionary or file.

For each tool you use or create, be prepared to explain:

* What the tool does.
* What inputs the tool expects.
* What result the tool returns.
* How the tool description helps the model decide when to call it.

### 11. Configure OpenCode or Another MCP-Capable Client

Configure OpenCode or another approved CLI-based AI agent to use the course model endpoint.

If you use OpenCode with `HelloMCP`, configure it to see the local MCP server as well.

If you use the provided Python MCP-capable client instead of OpenCode for the MCP demonstration, your client should be configured through:

```env
MCP_ENABLED=true
MCP_SERVERS=calculator=http://127.0.0.1:8765/mcp
```

Then demonstrate that the agent or client can call the MCP server and complete a simple task.

Your evidence should show that you tested more than one tool, or explain why only one tool could be demonstrated in your environment.

Provide evidence that OpenCode or the approved client was configured successfully. Evidence may include:

* A screenshot.
* A configuration snippet with sensitive values removed.
* Short command output.
* Startup output showing model and MCP connection status.
* A brief explanation of what the client or agent was connected to.

### 12. Complete a Setup and Tool-Use Reflection

Write a short reflection explaining your understanding of the work you completed.

Your reflection should include:

* What you built or ran.
* How the model connection worked.
* How streamed and non-streamed responses differ.
* How the MCP server and tools worked.
* Which simple tools you used or created.
* How the CLI agent or client used the MCP tools.
* How the client behaved when MCP servers were available or unavailable.
* How you used AI tools while completing the assignment.
* What AI-generated suggestions you accepted, changed, rejected, or tested.

## Optional TypeScript Alternative

Students who prefer TypeScript may complete the TypeScript/Node.js version described in `typescript_alternative.md`.

The TypeScript alternative should demonstrate the same core outcomes:

* Environment configuration.
* Connection to `Qwen/Qwen3.6-35B-A3B`.
* Prompt and response behavior.
* MCP server use.
* MCP tool calls.
* Reflection on what was built and understood.

This option does not provide extra credit. Students only need to submit one working model connection path.

## Submission Requirements

Submit multiple files if needed. A clear submission should include the following items.

### 1. Reflection

Submit a reflection file containing:

* Brief answers to the reflection questions.
* Evidence that the local model connection worked.
* A short explanation of how you used AI tools while completing the assignment and how you evaluated or modified their suggestions.

### 2. Model Connection Code

Submit the Python script, notebook, or TypeScript code used to connect to the local model.

Your submission should include at least one response example. Stronger submissions include both streamed and non-streamed examples.

### 3. Environment Configuration Example

Submit:

```text
.env.example
```

Do not submit:

```text
.env
```

Your `.env.example` should include the client model settings, MCP client settings, and HelloMCP server settings:

```env
LLM_BASE_URL=
LLM_API_KEY=
LLM_MODEL=
LLM_TEMPERATURE=
LLM_STREAM=

MCP_ENABLED=
MCP_SERVERS=
MCP_SHOW_ERRORS=
MCP_CONNECT_TIMEOUT=

HELLO_MCP_HOST=
HELLO_MCP_PORT=
HELLO_MCP_PATH=
```

### 4. OpenCode or Client Configuration Evidence

Submit evidence that OpenCode or another approved MCP-capable client was configured to use the course model endpoint.

If you connected OpenCode or the Python client to `HelloMCP`, include evidence of that connection as well.

Evidence may include:

* A screenshot.
* A configuration snippet with sensitive values removed.
* Startup output showing the model endpoint.
* Startup output showing MCP servers on or unavailable.
* A brief explanation of the configuration.

### 5. MCP Server and MCP Usage Evidence

Submit MCP server code or a clear reference to the `HelloMCP` server you used.

Also submit evidence showing:

* What the server does.
* Which simple tools you used or created.
* How it was connected to the CLI agent or client.
* What prompts or commands caused the agent or client to call the tools.
* What results were returned.

## Grading Criteria

This assignment will be graded based on completion, correctness, and evidence of understanding.

| Category                                           | Percentage |
| -------------------------------------------------- | ---------: |
| Environment setup completed                        |        20% |
| Python or TypeScript model connection works        |        20% |
| OpenCode or approved client configured             |        20% |
| Setup reflection and explanation of AI interaction |        20% |
| MCP server functionality and tool-use reflection   |        20% |

## Reflection Questions

Answer briefly.

1. What did your connection script do?
2. What is the role of `LLM_BASE_URL`?
3. Why should the real `.env` file not be submitted?
4. What problem did you encounter, if any, and how did you address it?
5. How did you know the model connection worked?
6. What is the difference between streamed and non-streamed output?
7. How did you use AI tools while completing this assignment?
8. What does your MCP server do?
9. What simple MCP tools did you use or create?
10. How did the CLI agent or client call your MCP server?
11. How did tool descriptions or input names affect whether the model used the right tool?
12. What happened when an MCP server was unavailable, and how did the client handle it?

## Completion Standard

A complete submission should show that you can:

* Set up a working programming environment for the course.
* Connect code to the local course model.
* Use environment variables safely.
* Run a basic AI interaction through Python or TypeScript.
* Run or adapt the `HelloMCP` server.
* Configure OpenCode or another approved MCP-capable client with the course model.
* Create, adapt, or explain a simple MCP server with a few small tools.
* Connect the MCP server to a CLI agent or MCP-capable client.
* Explain how MCP servers are configured through `MCP_SERVERS`.
* Explain what happens when MCP servers are available or unavailable.
* Explain the setup process and AI interactions at a basic level.
* Reflect clearly on what you built, what you understood, and how you used AI tools.
