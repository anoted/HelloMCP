from __future__ import annotations

import asyncio
import json
import os
import re
import urllib.request
from pathlib import Path
from typing import Any

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


if load_dotenv is not None:
    load_dotenv(Path(__file__).with_name(".env"))


OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "http://127.0.0.1:1234/v1").rstrip("/")
OPENAI_HOST = os.getenv("OPENAI_HOST") or os.getenv("OPENAI_IP")
OPENAI_PORT = os.getenv("OPENAI_PORT")
if OPENAI_HOST and OPENAI_PORT:
    OPENAI_BASE_URL = f"http://{OPENAI_HOST}:{OPENAI_PORT}/v1"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "local-not-needed")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "Qwen/Qwen3.6-35B-A3B")
MCP_URL = os.getenv("HELLO_MCP_URL", "http://127.0.0.1:8765/mcp")


def call_openai(messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> dict[str, Any]:
    body = {
        "model": OPENAI_MODEL,
        "messages": messages,
        "tools": tools,
        "tool_choice": "auto",
        "temperature": 0.2,
    }
    request = urllib.request.Request(
        f"{OPENAI_BASE_URL}/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}",
        },
        method="POST",
    )
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


def safe_tool_name(name: str) -> str:
    safe = re.sub(r"[^a-zA-Z0-9_-]", "_", name)
    return safe[:64]


def to_openai_tools(mcp_tools: list[Any]) -> tuple[list[dict[str, Any]], dict[str, str]]:
    tools = []
    name_map = {}
    for tool in mcp_tools:
        safe_name = safe_tool_name(tool.name)
        name_map[safe_name] = tool.name
        input_schema = getattr(tool, "inputSchema", None) or getattr(tool, "input_schema", {})
        tools.append(
            {
                "type": "function",
                "function": {
                    "name": safe_name,
                    "description": f"MCP tool {tool.name}: {tool.description or ''}",
                    "parameters": input_schema,
                },
            }
        )
    return tools, name_map


def tool_result_text(result: Any) -> str:
    structured = getattr(result, "structuredContent", None) or getattr(
        result, "structured_content", None
    )
    if structured is not None:
        return json.dumps(structured)

    texts = [item.text for item in result.content if getattr(item, "type", None) == "text"]
    return "\n".join(texts) if texts else str(result)


async def chat() -> None:
    async with streamable_http_client(MCP_URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            mcp_tools = (await session.list_tools()).tools
            openai_tools, tool_name_map = to_openai_tools(mcp_tools)

            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant. When arithmetic is requested, "
                        "call the available MCP tools instead of doing it mentally."
                    ),
                }
            ]

            print(f"Model: {OPENAI_MODEL}")
            print(f"OpenAI-compatible endpoint: {OPENAI_BASE_URL}")
            print(f"MCP endpoint: {MCP_URL}")
            print("Type 'exit' to quit.\n")

            while True:
                user_text = input("you> ").strip()
                if user_text.lower() in {"exit", "quit"}:
                    return
                if not user_text:
                    continue

                messages.append({"role": "user", "content": user_text})
                response = call_openai(messages, openai_tools)
                assistant_message = response["choices"][0]["message"]
                messages.append(assistant_message)

                tool_calls = assistant_message.get("tool_calls") or []
                for tool_call in tool_calls:
                    function = tool_call["function"]
                    openai_tool_name = function["name"]
                    mcp_tool_name = tool_name_map[openai_tool_name]
                    arguments = json.loads(function.get("arguments") or "{}")

                    print(f"mcp> {mcp_tool_name}({arguments})")
                    result = await session.call_tool(mcp_tool_name, arguments)
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "content": tool_result_text(result),
                        }
                    )

                if tool_calls:
                    response = call_openai(messages, openai_tools)
                    assistant_message = response["choices"][0]["message"]
                    messages.append(assistant_message)

                print(f"assistant> {assistant_message.get('content') or ''}\n")


if __name__ == "__main__":
    asyncio.run(chat())
