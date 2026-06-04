from __future__ import annotations

import math # for math.log and what not!
import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


if load_dotenv is not None:
    load_dotenv(Path(__file__).with_name(".env"))

HOST = os.getenv("HELLO_MCP_HOST", "127.0.0.1")
PORT = int(os.getenv("HELLO_MCP_PORT", "8765"))
MCP_PATH = os.getenv("HELLO_MCP_PATH", "/mcp")


mcp = FastMCP(
    name="HelloMCP",
    instructions="A tiny local MCP calculator server with some calculator tools.",
    host=HOST,
    port=PORT,
    streamable_http_path=MCP_PATH,
    json_response=True,
    stateless_http=True,
)


@mcp.tool(
    name="calculator.add",
    description="Add two numbers and return the sum.",
)
def add(a: float, b: float) -> float:
    return a + b

@mcp.tool(
    name="calculator.subtract",
    description="Subtract second number from first number and return the difference.",
)
def subtract(a: float, b: float) -> float:
    return a - b


@mcp.tool(
    name="calculator.log",
    description="Calculate the natural logarithm of a number.",
)
def log(a: float) -> float:
    return math.log(a)

@mcp.custom_route("/healthz", methods=["GET"], include_in_schema=False)
async def healthz(_: Request) -> JSONResponse:
    return JSONResponse(
        {
            "status": "ok",
            "server": "HelloMCP",
            "mcp_url": f"http://{HOST}:{PORT}{MCP_PATH}",
        }
    )


if __name__ == "__main__":
    print(f"Starting HelloMCP at http://{HOST}:{PORT}{MCP_PATH}")
    print(f"Health check: http://{HOST}:{PORT}/healthz")
    mcp.run(transport="streamable-http")
