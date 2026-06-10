import asyncio
import json
import os
import re
import urllib.request
from pathlib import Path

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

try:
    from dotenv import load_dotenv
except ImportError:
    pass
else:
    load_dotenv(Path(__file__).with_name(".env"))

if (host := os.getenv("OPENAI_HOST") or os.getenv("OPENAI_IP")) and (port := os.getenv("OPENAI_PORT")):
    OPENAI_BASE_URL = f"http://{host}:{port}/v1"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "local-not-needed")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "Qwen/Qwen3.6-35B-A3B")
MCP_URL = os.getenv("HELLO_MCP_URL", "http://127.0.0.1:8765/mcp")


def write(section, text, current):
    if not text:
        return
    if current[0] != section:
        # if current[0]:
        #     print()
        print(f"{section}>> ", end="", flush=True)
        current[0] = section
    print(text, end="", flush=True)


def openai_tools(mcp_tools):
    """
    Convert MCP tools to OpenAI tool format, and return a mapping of safe tool names to original tool names.
    Takes a list of MCP tools, which can be either dicts or objects with attributes. 
    Each tool should have at least 'name' and 'description', and optionally 'inputSchema' or 'input_schema' for the parameters.
     Returns a tuple of (tools, name_map) where tools is a list of dicts
    """
    tools, names = [], {}
    for tool in mcp_tools:
        name = re.sub(r"[^a-zA-Z0-9_-]", "_", tool.name)[:64]
        names[name] = tool.name
        schema = getattr(tool, "inputSchema", None) or getattr(tool, "input_schema", {})
        tools.append({"type": "function", "function": {"name": name, "description": f"MCP tool {tool.name}: {tool.description or ''}", "parameters": schema}})
    return tools, names


def tool_text(result):
    """
    Return a string representation of a tool result, 
    preferring structured content if available, otherwise concatenating text content.
    """
    structured = getattr(result, "structuredContent", None) or getattr(result, "structured_content", None)
    if structured is not None:
        return json.dumps(structured)
    return "\n".join(item.text for item in result.content if getattr(item, "type", None) == "text") or str(result)


def stream_openai(messages, tools):
    """
    Stream a response from the OpenAI API for the given messages and tools, 
    yielding reasoning, answer, and tool call chunks as they arrive.
    """
    body = {"model": OPENAI_MODEL, "messages": messages, "tools": tools, "tool_choice": "auto", "temperature": 0.8, "stream": True}
    request = urllib.request.Request(f"{OPENAI_BASE_URL}/chat/completions", json.dumps(body).encode(), {"Content-Type": "application/json", "Authorization": f"Bearer {OPENAI_API_KEY}"}, method="POST")
    answer, tool_calls, current = [], {}, [None]
    with urllib.request.urlopen(request) as response:
        print("\n=========================")
        
        for raw in response:
            line = raw.decode("utf-8").strip()
            if not line.startswith("data:"):
                continue

            data = line[5:].strip()
            if data == "[DONE]":
                break
            delta = (json.loads(data).get("choices") or [{}])[0].get("delta") or {}
            write("reasoning", delta.get("reasoning_content") or delta.get("reasoning"), current)

            if content := delta.get("content"):
                answer.append(content)
                write("\nanswer", content, current)

            for chunk in delta.get("tool_calls") or []:
                call = tool_calls.setdefault(int(chunk.get("index", len(tool_calls))), {"id": "", "type": "function", "function": {"name": "", "arguments": ""}})
                call["id"] = chunk.get("id") or call["id"]
                call["type"] = chunk.get("type") or call["type"]
                function = chunk.get("function") or {}
                call["function"]["name"] += function.get("name") or ""
                call["function"]["arguments"] += function.get("arguments") or ""

    if current[0]:
        print("\n=========================")
    message = {"role": "assistant", "content": "".join(answer).strip() or None}
    if tool_calls:
        message["tool_calls"] = [tool_calls[i] for i in sorted(tool_calls)]
    return message


async def chat():
    """
    Main chat loop that initializes the MCP client session, retrieves available tools, and interacts with the user.
     For each user input, it sends the conversation history to the OpenAI API, streams the response, and handles any tool calls by invoking the corresponding MCP tools and feeding the results back into the conversation.
     The loop continues until the user types 'exit' or 'quit'.
     This function uses the streamable HTTP client to maintain an open connection with the MCP server.
    """
    async with streamable_http_client(MCP_URL) as (read, write_stream, _):
        async with ClientSession(read, write_stream) as session:
            await session.initialize()
            tools, names = openai_tools((await session.list_tools()).tools)
            messages = [{"role": "system", "content": "You are a helpful assistant. When arithmetic is requested, call the available MCP calculator tool instead of doing it mentally."}]
            
            print(f"Model: {OPENAI_MODEL}")
            print(f"OpenAI-compatible endpoint: {OPENAI_BASE_URL}")
            print(f"MCP endpoint: {MCP_URL}")
            print(f"Available MCP tools: {', '.join(names.values())}")
            print("Type 'exit' to quit.\n")


            while True:
                text = input("you>> ").strip()
                if text.lower() in {"exit", "quit"}:
                    return
                if not text:
                    continue
                messages.append({"role": "user", "content": text})

                while True:
                    messages.append(stream_openai(messages, tools))
                    calls = messages[-1].get("tool_calls") or []
                    if not calls:
                        print()
                        break
                    for call in calls:
                        function = call["function"]
                        name = names[function["name"]]
                        args = json.loads(function.get("arguments") or "{}")
                        print(f"mcp call> {name}({args})")
                        result = await session.call_tool(name, args)
                        content = tool_text(result)
                        print(f"mcp return> {content}")
                        messages.append({"role": "tool", "tool_call_id": call["id"], "content": content})


if __name__ == "__main__":
    asyncio.run(chat())
