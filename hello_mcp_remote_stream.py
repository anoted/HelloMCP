import asyncio
import contextlib
import json
import os
import re
import socket
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

try:
    from dotenv import load_dotenv
except ImportError:
    pass
else:
    load_dotenv(Path(__file__).with_name(".env"))


# ============================================================
# LLM SETTINGS
# ============================================================

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://127.0.0.1:1234/v1").rstrip("/")
LLM_API_KEY = os.getenv("LLM_API_KEY", "not-needed")
LLM_MODEL = os.getenv("LLM_MODEL", "local-model")

LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.8"))
LLM_STREAM = os.getenv("LLM_STREAM", "true").lower() not in {
    "0",
    "false",
    "no",
    "none",
    "off",
    "disabled",
}


# ============================================================
# MCP SETTINGS
# ============================================================
#
# MCP is optional.
#
# Multiple MCP servers:
#
#   MCP_SERVERS=calculator=http://127.0.0.1:8765/mcp,notes=http://127.0.0.1:8767/mcp
#
# Disable MCP entirely:
#
#   MCP_ENABLED=false
#
# Show connection errors:
#
#   MCP_SHOW_ERRORS=true
#
# Optional preflight timeout:
#
#   MCP_CONNECT_TIMEOUT=1.5
#
# Notes:
# - MCP_URL is intentionally not used.
# - MCP_SERVERS is the only MCP server configuration.
# - Each MCP server should be written as name=url.
# - Server names are used for logging and tool-name namespacing.
#

MCP_ENABLED = os.getenv("MCP_ENABLED", "true").lower() not in {
    "0",
    "false",
    "no",
    "none",
    "off",
    "disabled",
}

MCP_SHOW_ERRORS = os.getenv("MCP_SHOW_ERRORS", "false").lower() in {
    "1",
    "true",
    "yes",
    "on",
}

MCP_CONNECT_TIMEOUT = float(os.getenv("MCP_CONNECT_TIMEOUT", "1.5"))
MCP_SERVERS = os.getenv("MCP_SERVERS", "").strip()


def parse_mcp_servers():
    """
    Parse MCP_SERVERS from the .env file.

    Format:
        MCP_SERVERS=name=url,name2=url2

    Example:
        MCP_SERVERS=calculator=http://127.0.0.1:8765/mcp,notes=http://127.0.0.1:8767/mcp

    Bare URLs are allowed, but generated names will be used:
        MCP_SERVERS=http://127.0.0.1:8765/mcp,http://127.0.0.1:8767/mcp
    """
    if not MCP_ENABLED:
        return []

    if not MCP_SERVERS:
        return []

    servers = []

    for item in MCP_SERVERS.split(","):
        item = item.strip()

        if not item:
            continue

        if "=" not in item:
            name = f"mcp_{len(servers) + 1}"
            url = item
        else:
            name, url = item.split("=", 1)
            name = name.strip()
            url = url.strip()

        if not url or url.lower() in {
            "0",
            "false",
            "no",
            "none",
            "off",
            "disabled",
        }:
            continue

        safe_name = re.sub(
            r"[^a-zA-Z0-9_-]",
            "_",
            name or f"mcp_{len(servers) + 1}",
        )

        servers.append(
            {
                "name": safe_name,
                "url": url.rstrip("/"),
            }
        )

    return servers


# ============================================================
# OUTPUT HELPERS
# ============================================================

def write(section, text, current):
    if not text:
        return

    if current[0] != section:
        print(f"{section}>> ", end="", flush=True)
        current[0] = section

    print(text, end="", flush=True)


# ============================================================
# MCP TOOL CONVERSION
# ============================================================

def make_safe_tool_name(server_name, tool_name, existing_names):
    """
    Create a safe, namespaced OpenAI-compatible function name.

    Example:
        calculator + add -> calculator__add

    This prevents collisions when multiple MCP servers expose tools
    with the same name.
    """
    raw_name = f"{server_name}__{tool_name}"
    safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", raw_name)[:64]

    base_name = safe_name
    counter = 2

    while safe_name in existing_names:
        suffix = f"_{counter}"
        safe_name = f"{base_name[:64 - len(suffix)]}{suffix}"
        counter += 1

    return safe_name


def mcp_tool_to_openai_tool(server_name, tool, existing_names):
    """
    Convert one MCP tool into one OpenAI-compatible function tool.
    """
    original_name = tool.name
    safe_name = make_safe_tool_name(server_name, original_name, existing_names)

    schema = (
        getattr(tool, "inputSchema", None)
        or getattr(tool, "input_schema", None)
        or {
            "type": "object",
            "properties": {},
            "additionalProperties": True,
        }
    )

    openai_tool = {
        "type": "function",
        "function": {
            "name": safe_name,
            "description": (
                f"MCP server '{server_name}', tool '{original_name}': "
                f"{tool.description or ''}"
            ),
            "parameters": schema,
        },
    }

    return safe_name, openai_tool


def tool_result_to_text(result):
    """
    Convert an MCP tool result into plain text for the LLM.
    """
    structured = (
        getattr(result, "structuredContent", None)
        or getattr(result, "structured_content", None)
    )

    if structured is not None:
        return json.dumps(structured, ensure_ascii=False)

    parts = []

    for item in getattr(result, "content", []) or []:
        if getattr(item, "type", None) == "text":
            parts.append(item.text)

    return "\n".join(parts) if parts else str(result)


# ============================================================
# LLM REQUEST HANDLING
# ============================================================

def make_request_body(messages, tools):
    """
    Create an OpenAI-compatible chat/completions request body.
    """
    body = {
        "model": LLM_MODEL,
        "messages": messages,
        "temperature": LLM_TEMPERATURE,
        "stream": LLM_STREAM,
    }

    if tools:
        body["tools"] = tools
        body["tool_choice"] = "auto"

    return body


def make_request(body):
    """
    Create the HTTP request for the OpenAI-compatible endpoint.
    """
    headers = {
        "Content-Type": "application/json",
    }

    if LLM_API_KEY:
        headers["Authorization"] = f"Bearer {LLM_API_KEY}"

    return urllib.request.Request(
        f"{LLM_BASE_URL}/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers=headers,
        method="POST",
    )


def call_llm_non_streaming(messages, tools):
    """
    Non-streaming OpenAI-compatible chat completion.
    """
    body = make_request_body(messages, tools)
    body["stream"] = False

    request = make_request(body)

    try:
        with urllib.request.urlopen(request) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"LLM request failed: HTTP {exc.code}\n{error_body}") from exc

    choice = (payload.get("choices") or [{}])[0]
    message = choice.get("message") or {}

    return {
        "role": "assistant",
        "content": message.get("content"),
        "tool_calls": message.get("tool_calls") or [],
    }


def call_llm_streaming(messages, tools):
    """
    Streaming OpenAI-compatible chat completion.

    Accumulates streamed text and streamed tool calls into a final assistant message.
    """
    body = make_request_body(messages, tools)
    body["stream"] = True

    request = make_request(body)

    answer = []
    tool_calls = {}
    current = [None]

    try:
        with urllib.request.urlopen(request) as response:
            print("\n=========================")

            for raw in response:
                line = raw.decode("utf-8").strip()

                if not line.startswith("data:"):
                    continue

                data = line[5:].strip()

                if data == "[DONE]":
                    break

                payload = json.loads(data)
                choice = (payload.get("choices") or [{}])[0]
                delta = choice.get("delta") or {}

                reasoning = (
                    delta.get("reasoning_content")
                    or delta.get("reasoning")
                    or delta.get("thought")
                )

                write("reasoning", reasoning, current)

                content = delta.get("content")
                if content:
                    answer.append(content)
                    write("\nanswer", content, current)

                for chunk in delta.get("tool_calls") or []:
                    index = int(chunk.get("index", len(tool_calls)))

                    call = tool_calls.setdefault(
                        index,
                        {
                            "id": "",
                            "type": "function",
                            "function": {
                                "name": "",
                                "arguments": "",
                            },
                        },
                    )

                    call["id"] = chunk.get("id") or call["id"]
                    call["type"] = chunk.get("type") or call["type"]

                    function = chunk.get("function") or {}
                    call["function"]["name"] += function.get("name") or ""
                    call["function"]["arguments"] += function.get("arguments") or ""

    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"LLM request failed: HTTP {exc.code}\n{error_body}") from exc

    if current[0]:
        print("\n=========================")

    message = {
        "role": "assistant",
        "content": "".join(answer).strip() or None,
    }

    if tool_calls:
        message["tool_calls"] = [tool_calls[i] for i in sorted(tool_calls)]

    return message


def call_llm(messages, tools):
    """
    Dispatch to streaming or non-streaming mode.
    """
    if LLM_STREAM:
        return call_llm_streaming(messages, tools)

    return call_llm_non_streaming(messages, tools)


# ============================================================
# MCP PREFLIGHT AND INITIALIZATION
# ============================================================

def extract_host_port(url):
    """
    Extract host and port from an MCP HTTP URL.
    """
    parsed = urlparse(url)

    if not parsed.hostname:
        return None, None

    if parsed.port:
        return parsed.hostname, parsed.port

    if parsed.scheme == "https":
        return parsed.hostname, 443

    return parsed.hostname, 80


async def tcp_port_open(url, timeout=MCP_CONNECT_TIMEOUT):
    """
    Lightweight reachability check before touching streamable_http_client.

    This prevents broken/unavailable MCP servers from creating noisy AnyIO
    async-generator cleanup errors.
    """
    host, port = extract_host_port(url)

    if not host or not port:
        return False

    def try_connect():
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except OSError:
            return False

    return await asyncio.to_thread(try_connect)


async def safe_close_stack(stack):
    """
    Close an AsyncExitStack while suppressing MCP/AnyIO cleanup noise.
    """
    if stack is None:
        return

    try:
        await stack.aclose()
    except BaseException:
        pass


async def initialize_one_mcp_server(server_config):
    """
    Try to initialize one MCP server.

    Important:
    - first check TCP reachability
    - only enter streamable_http_client if the port is reachable
    - if anything fails, return unavailable instead of crashing chat
    """
    name = server_config["name"]
    url = server_config["url"]

    reachable = await tcp_port_open(url)

    if not reachable:
        return {
            "name": name,
            "url": url,
            "connected": False,
            "session": None,
            "raw_tools": [],
            "stack": None,
            "error": "unreachable",
        }

    stack = contextlib.AsyncExitStack()

    try:
        read, write_stream, _ = await stack.enter_async_context(
            streamable_http_client(url)
        )

        session = await stack.enter_async_context(
            ClientSession(read, write_stream)
        )

        await session.initialize()

        mcp_tools = (await session.list_tools()).tools

        return {
            "name": name,
            "url": url,
            "connected": True,
            "session": session,
            "raw_tools": mcp_tools,
            "stack": stack,
            "error": None,
        }

    except asyncio.CancelledError:
        await safe_close_stack(stack)

        return {
            "name": name,
            "url": url,
            "connected": False,
            "session": None,
            "raw_tools": [],
            "stack": None,
            "error": "cancelled",
        }

    except BaseException:
        await safe_close_stack(stack)

        return {
            "name": name,
            "url": url,
            "connected": False,
            "session": None,
            "raw_tools": [],
            "stack": None,
            "error": "failed",
        }


async def initialize_mcp_servers():
    """
    Initialize all configured MCP servers.

    Failed MCP servers are marked unavailable and do not crash chat.
    Connected MCP servers keep their own cleanup stacks.
    """
    server_configs = parse_mcp_servers()

    state = {
        "enabled": MCP_ENABLED,
        "configured": server_configs,
        "servers": [],
        "tools": [],
        "tool_routes": {},
        "stacks": [],
    }

    if not MCP_ENABLED or not server_configs:
        return state

    for server_config in server_configs:
        server_state = await initialize_one_mcp_server(server_config)
        state["servers"].append(server_state)

        if not server_state["connected"]:
            continue

        state["stacks"].append(server_state["stack"])

        for tool in server_state["raw_tools"]:
            safe_name, openai_tool = mcp_tool_to_openai_tool(
                server_state["name"],
                tool,
                existing_names=state["tool_routes"],
            )

            state["tools"].append(openai_tool)

            state["tool_routes"][safe_name] = {
                "server_name": server_state["name"],
                "server_url": server_state["url"],
                "session": server_state["session"],
                "mcp_tool_name": tool.name,
            }

    return state


async def close_mcp_servers(mcp_state):
    """
    Close only successfully connected MCP stacks.

    Cleanup errors are suppressed so MCP stream shutdown does not crash the app.
    """
    for stack in reversed(mcp_state.get("stacks", [])):
        await safe_close_stack(stack)


# ============================================================
# STARTUP STATUS
# ============================================================

def print_startup_status(mcp_state):
    """
    Print clean startup status.

    Unavailable MCP servers are listed by name only unless MCP_SHOW_ERRORS=true.
    """
    print(f"Model: {LLM_MODEL}")
    print(f"LLM endpoint: {LLM_BASE_URL}")
    print(f"Streaming: {LLM_STREAM}")

    if not MCP_ENABLED:
        print("MCP: off")
        print("Type 'exit' or 'quit' to stop.\n")
        return

    configured = mcp_state["configured"]

    if not configured:
        print("MCP: no servers configured")
        print("Type 'exit' or 'quit' to stop.\n")
        return

    connected = [server for server in mcp_state["servers"] if server["connected"]]
    unavailable = [server for server in mcp_state["servers"] if not server["connected"]]

    print(f"MCP: {len(connected)} on, {len(unavailable)} unavailable")

    if connected:
        print("MCP servers on:")

        for server in connected:
            tool_names = [
                route["mcp_tool_name"]
                for route in mcp_state["tool_routes"].values()
                if route["server_name"] == server["name"]
            ]

            print(f"  - {server['name']}: {server['url']}")
            print(f"    tools: {', '.join(tool_names) or 'none'}")

    if unavailable:
        print("MCP servers unavailable:")

        for server in unavailable:
            print(f"  - {server['name']}")

            if MCP_SHOW_ERRORS:
                print(f"    error: {server['error']}")

    print("Type 'exit' or 'quit' to stop.\n")


# ============================================================
# TOOL CALL HANDLING
# ============================================================

async def handle_tool_calls(messages, assistant_message, mcp_state):
    """
    Execute tool calls from the model.

    Tool routing uses the namespaced OpenAI function name to find the correct
    MCP server and original MCP tool.
    """
    tool_calls = assistant_message.get("tool_calls") or []

    if not tool_calls:
        return False

    routes = mcp_state["tool_routes"]

    for call in tool_calls:
        function = call.get("function") or {}
        safe_name = function.get("name")

        if safe_name not in routes:
            content = f"Tool is not available: {safe_name}"

            print(f"mcp error> {content}")

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.get("id", ""),
                    "content": content,
                }
            )

            continue

        route = routes[safe_name]
        session = route["session"]
        server_name = route["server_name"]
        mcp_tool_name = route["mcp_tool_name"]

        try:
            args = json.loads(function.get("arguments") or "{}")
        except json.JSONDecodeError:
            args = {}

        print(f"mcp call> [{server_name}] {mcp_tool_name}({args})")

        try:
            result = await session.call_tool(mcp_tool_name, args)
            content = tool_result_to_text(result)
        except Exception as exc:
            content = f"MCP tool call failed on server '{server_name}': {exc}"

        print(f"mcp return> {content}")

        messages.append(
            {
                "role": "tool",
                "tool_call_id": call.get("id", ""),
                "content": content,
            }
        )

    return True


# ============================================================
# MAIN CHAT LOOP
# ============================================================

async def chat():
    """
    Chat starts independently.

    MCP servers are optional:
        - servers are read only from MCP_SERVERS
        - each configured MCP server is checked at startup
        - connected MCP tools are added to the LLM
        - unavailable MCP servers are listed cleanly
        - chat still works if zero MCP servers are available
    """
    mcp_state = await initialize_mcp_servers()
    tools = mcp_state["tools"]

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant. "
                "Use tools only when they are available and useful. "
                "If no tool is available, answer normally."
            ),
        }
    ]

    print_startup_status(mcp_state)

    try:
        while True:
            user_text = input("you>> ").strip()

            if user_text.lower() in {"exit", "quit"}:
                return

            if not user_text:
                continue

            messages.append(
                {
                    "role": "user",
                    "content": user_text,
                }
            )

            while True:
                assistant_message = call_llm(messages, tools)
                messages.append(assistant_message)

                used_tools = await handle_tool_calls(
                    messages,
                    assistant_message,
                    mcp_state,
                )

                if not used_tools:
                    print()
                    break

    finally:
        await close_mcp_servers(mcp_state)


if __name__ == "__main__":
    asyncio.run(chat())