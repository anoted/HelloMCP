# Assignment 1: Environment Setup, Local Model Connection, OpenCode, and MCP Practice

## Overview

In this assignment, you will set up your course programming environment, connect to the course model endpoint, run or adapt the `HelloMCP` example, create a few simple MCP tools, and demonstrate that a CLI-based AI agent or MCP-capable client can use those tools.

The primary workflow is the Python `HelloMCP` example:

- `HelloMCP/hello_mcp_server.py`
- `HelloMCP/hello_client.py`
- `HelloMCP/hello_client_stream.py`

Students who prefer TypeScript may use the TypeScript alternative described in `typescript_alternative.md`.

## Learning Outcomes

By completing this assignment, you will be able to:

- Set up a clean course programming environment.
- Configure environment variables for an OpenAI-compatible model endpoint.
- Connect to the course model, `Qwen/Qwen3.6-35B-A3B`.
- Send prompts to the model and receive responses.
- Explain the difference between streamed and non-streamed model responses.
- Run, adapt, and explain a simple MCP server.
- Create a few simple MCP tools and describe how the model uses them.
- Configure OpenCode or another approved CLI agent to use the course model and MCP server.
- Explain your workflow, troubleshooting, and AI-assisted development choices in a short reflection.

## Required Steps

### 1. Verify Your Development Environment

Verify that you have access to:

- Git
- Python 3.10 or higher
- A course environment manager such as Conda, Miniconda, `uv`, `venv`, or another approved option
- A coding environment such as VS Code, Cursor, GitHub Codespaces, or another approved option

### 2. Create a Dedicated Course Environment

Create a dedicated environment for this course. Use an environment name such as:

```text
mcpagents
```

Do not use a global Python installation for the assignment.

### 3. Prepare the Required Python Packages

Prepare the packages needed for the Module 1 examples:

- `mcp[cli]`
- `python-dotenv`
- `openai`
- `ipykernel`, optional for notebook users

The `HelloMCP` example uses FastMCP through the `mcp[cli]` package.

### 4. Create an Assignment Project Folder

Create a project folder for Assignment 1 and keep your assignment files organized inside it.

Suggested contents:

- `.env.example`
- model connection script or notebook
- reflection file
- OpenCode evidence
- MCP server code or reference to the server used
- MCP usage evidence
- screenshots, if used

### 5. Create Environment Configuration Files

Create a `.env.example` file showing the required configuration fields without exposing your real local settings.

Required fields:

```env
OPENAI_BASE_URL=
OPENAI_API_KEY=
OPENAI_MODEL=
MODEL_NAME=
HELLO_MCP_HOST=
HELLO_MCP_PORT=
HELLO_MCP_PATH=
HELLO_MCP_URL=
```

Create a local `.env` file for your own machine using the instructor-provided model server IP address and port.

The model endpoint should follow this format:

```text
http://<MODEL_SERVER_IP>:<PORT>/v1
```

Do not submit your real `.env` file.

### 6. Connect to the Course Model

Create or adapt a Python model connection script that connects to:

```text
Qwen/Qwen3.6-35B-A3B
```

Your script should:

- Load environment variables from `.env`.
- Connect to the OpenAI-compatible endpoint.
- Send a prompt to the model.
- Receive and print a response.
- Provide evidence that the model connection worked.

You may use `base_openai.py` as a starting point.

### 7. Compare Streamed and Non-Streamed Responses

Test model responses in at least one response mode:

- Non-streamed response: the full response returns at once.
- Streamed response: the response appears gradually as the model generates it.

Stronger submissions demonstrate both response modes.

The provided examples are:

- `HelloMCP/hello_client.py`
- `HelloMCP/hello_client_stream.py`

### 8. Run the HelloMCP Server

Run the `HelloMCP` server and verify that it is available.

The server should expose a local MCP endpoint and a health-check endpoint.

The current `HelloMCP` server includes these tools:

- `calculator.add`
- `calculator.subtract`
- `calculator.log`

### 9. Demonstrate MCP Tool Use

Use the `HelloMCP` client, OpenCode, or another approved MCP-capable CLI agent to demonstrate that the model can call an MCP tool.

Your evidence should show:

- The MCP server was running.
- The client or agent connected to the server.
- A prompt caused an MCP tool call.
- The tool returned a result.
- The model or agent used the result in a final response.

### 10. Create or Adapt a Few Simple MCP Tools

Create or adapt a simple MCP server with a few small tools. The goal is to practice tool creation and model tool use, not to build a complex application.

Your server should include at least three simple tools total. The existing `HelloMCP` tools may count toward this requirement if you can explain and demonstrate them. You are encouraged to add one or two new tools of your own.

Possible tools include:

- Returning the current date or time.
- Adding, subtracting, multiplying, or dividing numbers.
- Calculating a natural logarithm.
- Formatting text.
- Returning a course-related message.
- Looking up a value from a small local dictionary or file.

For each tool you use or create, be prepared to explain:

- What the tool does.
- What inputs the tool expects.
- What result the tool returns.
- How the tool description helps the model decide when to call it.

### 11. Configure OpenCode and Connect MCP Server

Configure OpenCode to use the course model endpoint.

If you use OpenCode with `HelloMCP`, configure it to see the local MCP server as well.

Then,

Demonstrate that the agent can call the MCP server and complete a simple task.

Your evidence should show that you tested more than one tool, or explain why only one tool could be demonstrated in your environment.

Provide evidence that OpenCode was configured successfully. Evidence may include:

- A screenshot.
- A configuration snippet with sensitive values removed.
- Short command output.
- A brief explanation of what OpenCode was connected to.

### 12. Complete a Setup and Tool-Use Reflection

Write a short reflection explaining your understanding of the work you completed.

Your reflection should include:

- What you built or ran.
- How the model connection worked.
- How streamed and non-streamed responses differ.
- How the MCP server and tools worked.
- Which simple tools you used or created.
- How the CLI agent or client used the MCP tools.
- How you used AI tools while completing the assignment.
- What AI-generated suggestions you accepted, changed, rejected, or tested.

## Optional TypeScript Alternative

Students who prefer TypeScript may complete the TypeScript/Node.js version described in `typescript_alternative.md`.

The TypeScript alternative should demonstrate the same core outcomes:

- Environment configuration.
- Connection to `Qwen/Qwen3.6-35B-A3B`.
- Prompt and response behavior.
- MCP server use.
- MCP tool calls.
- Reflection on what was built and understood.

This option does not provide extra credit. Students only need to submit one working model connection path.

## Submission Requirements

Submit multiple files if needed. A clear submission should include the following items.

### 1. Reflection

Submit a reflection file containing:

- Brief answers to the reflection questions.
- Evidence that the local model connection worked.
- A short explanation of how you used AI tools while completing the assignment and how you evaluated or modified their suggestions.

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

### 4. OpenCode Configuration Evidence

Submit evidence that OpenCode was configured to use the course model endpoint.

If you connected OpenCode to `HelloMCP`, include evidence of that connection as well.

### 5. MCP Server and MCP Usage Evidence

Submit MCP server code or a clear reference to the `HelloMCP` server you used.

Also submit evidence showing:

- What the server does.
- Which simple tools you used or created.
- How it was connected to the CLI agent or client.
- What prompts or commands caused the agent to call the tools.
- What results were returned.

## Grading Criteria

This assignment will be graded based on completion, correctness, and evidence of understanding.

| Category | Percentage |
| --- | ---: |
| Environment setup completed | 20% |
| Python or TypeScript model connection works | 20% |
| OpenCode configured | 20% |
| Setup reflection and explanation of AI interaction | 20% |
| MCP server functionality and tool-use reflection | 20% |

## Reflection Questions

Answer briefly.

1. What did your connection script do?
2. What is the role of `OPENAI_BASE_URL`?
3. Why should the real `.env` file not be submitted?
4. What problem did you encounter, if any, and how did you address it?
5. How did you know the model connection worked?
6. What is the difference between streamed and non-streamed output?
7. How did you use AI tools while completing this assignment?
8. What does your MCP server do?
9. What simple MCP tools did you use or create?
10. How did the CLI agent or client call your MCP server?
11. How did tool descriptions or input names affect whether the model used the right tool?

## Completion Standard

A complete submission should show that you can:

- Set up a working programming environment for the course.
- Connect code to the local course model.
- Use environment variables safely.
- Run a basic AI interaction through Python or TypeScript.
- Run or adapt the `HelloMCP` server.
- Configure OpenCode with the course model.
- Create, adapt, or explain a simple MCP server with a few small tools.
- Connect the MCP server to a CLI agent or MCP-capable client.
- Explain the setup process and AI interactions at a basic level.
- Reflect clearly on what you built, what you understood, and how you used AI tools.
