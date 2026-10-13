import json
from pathlib import Path
from typing import Any

from fastmcp import Client

from models import MCPCall


SERVER = Path(__file__).resolve().parents[1] / "mcp_server" / "mcp_server.py"


async def call_mcp(tool_name: str, arguments: dict[str, Any] | None = None) -> Any:
    """Call the project's MCP server; agents never query SQLite directly."""
    request = MCPCall(tool_name=tool_name, arguments=arguments or {})
    async with Client(SERVER) as client:
        result = await client.call_tool(request.tool_name, request.arguments)
        return result.data


def compact(value: Any, limit: int = 1800) -> str:
    text = json.dumps(value, default=str, ensure_ascii=False)
    return text if len(text) <= limit else text[: limit - 3] + "..."
