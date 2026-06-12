# HelloMCP Overview

This project contains a small local Model Context Protocol (MCP) calculator server and OpenAI-compatible chat clients that can call MCP tools.

#### 1. hello_mcp_server - mcp server with simple tools

#### 2. hello_mcp_remote_stream - mcp client with simple setup


The client reads optional configuration from a local `.env` file:

* `LLM_BASE_URL`: OpenAI-compatible endpoint, default `http://127.0.0.1:1234/v1`
* `LLM_API_KEY`: API key, default `not-needed`
* `LLM_MODEL`: model name, default `local-model`
* `LLM_TEMPERATURE`: model temperature, default `0.8`
* `LLM_STREAM`: whether to stream responses, default `true`
* `MCP_ENABLED`: whether MCP support is enabled, default `true`
* `MCP_SERVERS`: comma-separated MCP server list in `name=url` format
* `MCP_SHOW_ERRORS`: whether to show MCP connection errors, default `false`
* `MCP_CONNECT_TIMEOUT`: TCP preflight timeout in seconds, default `1.5`

Example `.env` for Google AI Studio through its OpenAI-compatible endpoint:

```env
LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai
LLM_API_KEY=your_api_key_here
LLM_MODEL=gemini-2.5-flash

LLM_TEMPERATURE=0.8
LLM_STREAM=true

MCP_ENABLED=true
MCP_SERVERS=calculator=http://127.0.0.1:8765/mcp
MCP_SHOW_ERRORS=false
MCP_CONNECT_TIMEOUT=1.5
```
