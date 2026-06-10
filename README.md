# HelloMCP Overview

This project contains a small local Model Context Protocol (MCP) calculator server and OpenAI-compatible chat clients that can call MCP tools.

## 1. hello_mcp_server

### Overview

`hello_mcp_server.py` defines the local MCP server. It exposes one calculator tool, `calculator.add`, over MCP streamable HTTP and provides a simple `/healthz` endpoint for checking whether the server is running.

The server reads optional configuration from a local `.env` file:

* `HELLO_MCP_HOST`: server host, default `127.0.0.1`
* `HELLO_MCP_PORT`: server port, default `8765`
* `HELLO_MCP_PATH`: MCP endpoint path, default `/mcp`

When run directly, the server starts at:

```text
http://127.0.0.1:8765/mcp
```

### Function Details

#### `add(a: float, b: float) -> float`

Registers the MCP tool `calculator.add`.

Purpose:

* Accepts two numeric values.
* Returns their sum.
* Allows MCP clients and connected models to perform addition through a tool call instead of calculating directly.

Example behavior:

```python
add(2, 3)
# returns 5
```

#### `healthz(_: Request) -> JSONResponse`

Registers a custom HTTP route at `/healthz`.

Purpose:

* Confirms that the server is available.
* Returns basic server metadata.
* Includes the MCP endpoint URL built from the current host, port, and path settings.

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

* Prints the MCP endpoint.
* Prints the health-check endpoint.
* Runs the server using the `streamable-http` transport.

## 2. hello_client

### Overview

The client code provides an interactive terminal chat interface for any OpenAI-compatible chat completions endpoint. It can optionally connect to one or more MCP servers, retrieve available MCP tools, convert those tools into OpenAI-compatible function tool definitions, and let the model call those tools during the chat.

The client is designed so that chat is independent from MCP. MCP servers are checked at startup, but unavailable MCP servers do not stop the chat from running. If some MCP servers are available and others are not, the client lists which ones are on and which ones are unavailable. If no MCP servers are available, the client still runs as a normal OpenAI-compatible chat client.

The current client supports:

* Any OpenAI-compatible `/chat/completions` endpoint.
* Streaming or non-streaming responses.
* Multiple MCP servers through `MCP_SERVERS`.
* Clean startup reporting for available and unavailable MCP servers.
* Namespaced tool names to avoid collisions between MCP servers.
* Optional MCP connection error display for debugging.

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

Example `.env` with multiple MCP servers:

```env
LLM_BASE_URL=http://127.0.0.1:1234/v1
LLM_API_KEY=not-needed
LLM_MODEL=local-model

LLM_TEMPERATURE=0.8
LLM_STREAM=true

MCP_ENABLED=true
MCP_SERVERS=calculator=http://127.0.0.1:8765/mcp,notes=http://127.0.0.1:8767/mcp,weather=http://127.0.0.1:8768/mcp
MCP_SHOW_ERRORS=false
MCP_CONNECT_TIMEOUT=1.5
```

Example `.env` with MCP disabled:

```env
LLM_BASE_URL=http://127.0.0.1:1234/v1
LLM_API_KEY=not-needed
LLM_MODEL=local-model

MCP_ENABLED=false
```

### MCP Server Configuration Format

MCP servers are configured only through `MCP_SERVERS`.

Format:

```env
MCP_SERVERS=name=url,name2=url2
```

Example:

```env
MCP_SERVERS=calculator=http://127.0.0.1:8765/mcp,notes=http://127.0.0.1:8767/mcp
```

Each MCP server name is used for logging and for tool namespacing. For example, if the `calculator` MCP server exposes a tool called `calculator.add`, the OpenAI-compatible function name becomes a safe namespaced name such as:

```text
calculator__calculator_add
```

This prevents collisions when multiple MCP servers expose tools with the same name.

Bare URLs are also allowed, but generated names will be used:

```env
MCP_SERVERS=http://127.0.0.1:8765/mcp,http://127.0.0.1:8767/mcp
```

The client does not use `MCP_URL`.

### Startup Behavior

At startup, the client:

1. Reads LLM settings from `.env`.
2. Reads MCP settings from `MCP_SERVERS`.
3. Performs a lightweight TCP preflight check for each MCP server.
4. Connects only to MCP servers that appear reachable.
5. Lists available tools from connected MCP servers.
6. Marks unreachable or failed MCP servers as unavailable.
7. Starts the chat loop regardless of MCP status.

Example startup output:

```text
Model: gemini-2.5-flash
LLM endpoint: https://generativelanguage.googleapis.com/v1beta/openai
Streaming: True
MCP: 1 on, 2 unavailable
MCP servers on:
  - calculator: http://127.0.0.1:8765/mcp
    tools: calculator.add
MCP servers unavailable:
  - notes
  - weather
Type 'exit' or 'quit' to stop.
```

If `MCP_SHOW_ERRORS=true`, unavailable MCP servers also print their connection error. By default, they are listed by name only.

### Function Details

#### `parse_mcp_servers() -> list[dict[str, str]]`

Parses the `MCP_SERVERS` environment variable.

Purpose:

* Reads comma-separated MCP server entries.
* Supports `name=url` entries.
* Supports bare URLs with generated names.
* Sanitizes server names for safe tool namespacing.
* Returns an empty list if MCP is disabled or no servers are configured.

#### `write(section, text, current)`

Prints streamed output under a labeled section.

Purpose:

* Avoids printing empty text.
* Starts a new section label when the stream changes between reasoning and answer text.
* Flushes output immediately so streamed tokens appear as they arrive.

#### `make_safe_tool_name(server_name: str, tool_name: str, existing_names: dict) -> str`

Creates a safe OpenAI-compatible function name for an MCP tool.

Purpose:

* Namespaces the tool with the MCP server name.
* Replaces unsupported characters with underscores.
* Limits the name to 64 characters.
* Avoids collisions when multiple MCP servers expose tools with the same name.

Example:

```text
calculator + calculator.add -> calculator__calculator_add
```

#### `mcp_tool_to_openai_tool(server_name: str, tool: Any, existing_names: dict) -> tuple[str, dict]`

Converts one MCP tool into an OpenAI-compatible function tool definition.

Purpose:

* Creates a safe namespaced function name.
* Copies the MCP tool description.
* Preserves the MCP tool input schema.
* Returns both the safe function name and the OpenAI-compatible tool definition.

#### `tool_result_to_text(result: Any) -> str`

Extracts readable text from an MCP tool result.

Purpose:

* Uses structured content first, when available.
* Otherwise joins text content items from the MCP result.
* Falls back to stringifying the result object.

#### `make_request_body(messages: list[dict], tools: list[dict]) -> dict`

Builds the OpenAI-compatible chat completions request body.

Purpose:

* Adds the configured model.
* Adds the conversation messages.
* Adds temperature and streaming settings.
* Adds tools only if at least one MCP tool is available.
* Uses automatic tool choice when tools are present.

#### `make_request(body: dict) -> urllib.request.Request`

Creates the HTTP request for the OpenAI-compatible endpoint.

Purpose:

* Sends the request to `{LLM_BASE_URL}/chat/completions`.
* Adds the JSON content type header.
* Adds the bearer token authorization header when an API key is configured.

#### `call_llm_non_streaming(messages: list[dict], tools: list[dict]) -> dict`

Sends a non-streaming chat completion request.

Purpose:

* Builds the request body.
* Forces `stream` to `false`.
* Sends the request to the OpenAI-compatible endpoint.
* Parses and returns the assistant message.
* Includes any tool calls requested by the model.

#### `call_llm_streaming(messages: list[dict], tools: list[dict]) -> dict`

Streams a chat completion response.

Purpose:

* Builds the request body.
* Forces `stream` to `true`.
* Reads server-sent event lines from the response.
* Prints reasoning chunks when the endpoint provides them.
* Prints answer chunks as they arrive.
* Reconstructs streamed tool call IDs, names, and arguments.
* Returns a final assistant message containing content and any tool calls.

#### `call_llm(messages: list[dict], tools: list[dict]) -> dict`

Dispatches to streaming or non-streaming mode.

Purpose:

* Calls `call_llm_streaming()` when `LLM_STREAM=true`.
* Calls `call_llm_non_streaming()` when `LLM_STREAM=false`.

#### `extract_host_port(url: str) -> tuple[str | None, int | None]`

Extracts the host and port from an MCP HTTP URL.

Purpose:

* Supports MCP TCP preflight checks.
* Uses the explicit URL port when provided.
* Uses port `443` for HTTPS URLs without an explicit port.
* Uses port `80` for HTTP URLs without an explicit port.

#### `tcp_port_open(url: str, timeout: float = MCP_CONNECT_TIMEOUT) -> bool`

Checks whether an MCP server appears reachable before opening a streamable HTTP session.

Purpose:

* Avoids entering `streamable_http_client()` when the server port is closed.
* Prevents noisy async generator and AnyIO cleanup errors from unavailable MCP servers.
* Runs the socket check in a background thread so it does not block the event loop.

#### `safe_close_stack(stack: AsyncExitStack | None) -> None`

Closes an MCP connection stack while suppressing cleanup noise.

Purpose:

* Cleans up successfully opened MCP sessions.
* Suppresses MCP or AnyIO shutdown errors so exit remains clean.
* Handles interrupted or partially closed MCP streams safely.

#### `initialize_one_mcp_server(server_config: dict) -> dict`

Attempts to initialize one MCP server.

Purpose:

* Performs TCP preflight first.
* Skips unavailable servers before opening MCP streamable HTTP.
* Opens a streamable HTTP MCP connection for reachable servers.
* Initializes a `ClientSession`.
* Lists available MCP tools.
* Returns a connected server state when successful.
* Returns an unavailable server state when connection or initialization fails.

#### `initialize_mcp_servers() -> dict`

Initializes all configured MCP servers.

Purpose:

* Reads all configured servers from `MCP_SERVERS`.
* Initializes each server independently.
* Keeps successful MCP sessions alive.
* Converts connected MCP tools into OpenAI-compatible tools.
* Builds the tool routing table.
* Marks failed servers as unavailable.
* Allows chat startup to continue even when no MCP servers connect.

#### `close_mcp_servers(mcp_state: dict) -> None`

Closes connected MCP servers at shutdown.

Purpose:

* Closes only successfully connected MCP stacks.
* Suppresses cleanup errors from MCP stream shutdown.
* Prevents unavailable or interrupted MCP connections from crashing the client on exit.

#### `print_startup_status(mcp_state: dict) -> None`

Prints the client startup summary.

Purpose:

* Shows the selected model.
* Shows the LLM endpoint.
* Shows whether streaming is enabled.
* Shows whether MCP is off, unconfigured, partially available, or fully available.
* Lists connected MCP servers and their tools.
* Lists unavailable MCP servers by name.
* Optionally prints MCP errors when `MCP_SHOW_ERRORS=true`.

#### `handle_tool_calls(messages: list[dict], assistant_message: dict, mcp_state: dict) -> bool`

Executes tool calls requested by the model.

Purpose:

* Reads tool calls from the assistant message.
* Routes each namespaced OpenAI function name back to the correct MCP server and original MCP tool.
* Parses JSON tool arguments.
* Calls the MCP tool through the correct `ClientSession`.
* Converts the MCP result into text.
* Appends the tool result to the message history.
* Returns `True` when tool calls were handled.
* Returns `False` when no tool calls were requested.

#### `chat() -> None`

Runs the main interactive chat loop.

Purpose:

* Initializes MCP servers independently from chat.
* Starts chat even if MCP is disabled, unconfigured, or unavailable.
* Builds the initial system message.
* Prints startup status.
* Reads user input from the terminal.
* Sends messages to the OpenAI-compatible endpoint.
* Streams or prints assistant responses depending on `LLM_STREAM`.
* Executes MCP tool calls when requested.
* Sends tool results back to the model.
* Continues the model/tool loop until no more tool calls are requested.
* Exits when the user types `exit` or `quit`.
* Closes connected MCP sessions cleanly at shutdown.

#### `if __name__ == "__main__"`

Starts the async chat loop when the client file is executed directly.

Purpose:

* Runs `chat()` with `asyncio.run()`.
