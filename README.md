# HelloMCP Overview

This project contains a small local Model Context Protocol (MCP) calculator server and OpenAI-compatible chat clients that can call the MCP tool.

## 1. hello_mcp_server

### Overview

`hello_mcp_server.py` defines the local MCP server. It exposes one calculator tool, `calculator.add`, over MCP streamable HTTP and provides a simple `/healthz` endpoint for checking whether the server is running.

The server reads optional configuration from a local `.env` file:

- `HELLO_MCP_HOST`: server host, default `127.0.0.1`
- `HELLO_MCP_PORT`: server port, default `8765`
- `HELLO_MCP_PATH`: MCP endpoint path, default `/mcp`

When run directly, the server starts at:

```text
http://127.0.0.1:8765/mcp
```

### Function Details

#### `add(a: float, b: float) -> float`

Registers the MCP tool `calculator.add`.

Purpose:

- Accepts two numeric values.
- Returns their sum.
- Allows MCP clients and connected models to perform addition through a tool call instead of calculating directly.

Example behavior:

```python
add(2, 3)
# returns 5
```

#### `healthz(_: Request) -> JSONResponse`

Registers a custom HTTP route at `/healthz`.

Purpose:

- Confirms that the server is available.
- Returns basic server metadata.
- Includes the MCP endpoint URL built from the current host, port, and path settings.

Example response:

```json
{
  "status": "ok",
  "server": "HelloMCP",
  "mcp_url": "http://127.0.0.1:8765/mcp"
}
```

#### `if __name__ == "__main__"`

Starts the MCP server when `hello_mcp_server.py` is executed directly.

Purpose:

- Prints the MCP endpoint.
- Prints the health-check endpoint.
- Runs the server using the `streamable-http` transport.

## 2. hello_client

### Overview

The client code connects to the local MCP server, retrieves available MCP tools, converts those tools into OpenAI-compatible function tool definitions, and sends user chat messages to an OpenAI-compatible chat completions endpoint.

There are two client files:

- `hello_client.py`: basic chat client using normal, non-streaming responses.
- `hello_client_stream.py`: streaming chat client that prints reasoning, answer text, MCP tool calls, and MCP tool results as they arrive.

Both clients read optional configuration from a local `.env` file:

- `OPENAI_BASE_URL`: OpenAI-compatible endpoint, default `http://127.0.0.1:1234/v1`
- `OPENAI_HOST` or `OPENAI_IP`: alternate host override
- `OPENAI_PORT`: alternate port override
- `OPENAI_API_KEY`: API key, default `local-not-needed`
- `OPENAI_MODEL`: model name, default `Qwen/Qwen3.6-35B-A3B`
- `HELLO_MCP_URL`: MCP endpoint, default `http://127.0.0.1:8765/mcp`

### Function Details: `hello_client.py`

#### `call_openai(messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> dict[str, Any]`

Sends a chat completion request to the OpenAI-compatible endpoint.

Purpose:

- Builds the request body with the configured model, messages, tools, automatic tool choice, and temperature.
- Sends the request using `urllib.request`.
- Parses and returns the JSON response.

#### `safe_tool_name(name: str) -> str`

Converts an MCP tool name into a valid OpenAI function name.

Purpose:

- Replaces unsupported characters with underscores.
- Limits the name to 64 characters.
- Makes names such as `calculator.add` safe for OpenAI tool calling as `calculator_add`.

#### `to_openai_tools(mcp_tools: list[Any]) -> tuple[list[dict[str, Any]], dict[str, str]]`

Converts MCP tool definitions into OpenAI-compatible tool definitions.

Purpose:

- Iterates over tools returned by the MCP server.
- Creates OpenAI `function` tool definitions.
- Preserves each tool's input schema.
- Builds a name map from safe OpenAI tool names back to original MCP tool names.

#### `tool_result_text(result: Any) -> str`

Extracts readable text from an MCP tool result.

Purpose:

- Uses structured content first, when available.
- Otherwise joins text content items from the MCP result.
- Falls back to stringifying the result object.

#### `chat() -> None`

Runs the main interactive chat loop.

Purpose:

- Opens a streamable HTTP connection to the MCP server.
- Initializes an MCP client session.
- Lists available MCP tools.
- Converts MCP tools into OpenAI tool definitions.
- Reads user input from the terminal.
- Sends messages to the OpenAI-compatible endpoint.
- Executes requested MCP tool calls.
- Sends tool results back to the model.
- Prints the assistant response.
- Exits when the user types `exit` or `quit`.

#### `if __name__ == "__main__"`

Starts the async chat loop when `hello_client.py` is executed directly.

Purpose:

- Runs `chat()` with `asyncio.run()`.

### Function Details: `hello_client_stream.py`

#### `write(section, text, current)`

Prints streamed output under a labeled section.

Purpose:

- Avoids printing empty text.
- Starts a new section label when the stream changes between reasoning and answer text.
- Flushes output immediately so streamed tokens appear as they arrive.

#### `openai_tools(mcp_tools)`

Converts MCP tools into OpenAI-compatible tool definitions.

Purpose:

- Creates safe OpenAI function names from MCP tool names.
- Copies descriptions and input schemas into OpenAI tool format.
- Returns both the tool definitions and a mapping back to original MCP names.

#### `tool_text(result)`

Extracts text from an MCP tool result.

Purpose:

- Prefers structured content when present.
- Otherwise joins text content items from the result.
- Falls back to stringifying the result.

#### `stream_openai(messages, tools)`

Streams a chat completion response from the OpenAI-compatible endpoint.

Purpose:

- Sends a streaming chat completions request.
- Reads server-sent event lines from the response.
- Prints reasoning and answer chunks as they arrive.
- Reconstructs streamed tool call IDs, names, and arguments.
- Returns an assistant message containing final content and any tool calls.

#### `chat()`

Runs the streaming interactive chat loop.

Purpose:

- Connects to the MCP server using streamable HTTP.
- Initializes the MCP client session.
- Lists MCP tools and converts them into OpenAI tool format.
- Reads user input from the terminal.
- Streams the model response.
- Calls MCP tools whenever the model requests them.
- Prints MCP calls and returns.
- Continues the model/tool loop until no more tool calls are requested.
- Exits when the user types `exit` or `quit`.

#### `if __name__ == "__main__"`

Starts the async streaming chat loop when `hello_client_stream.py` is executed directly.

Purpose:

- Runs `chat()` with `asyncio.run()`.
