import asyncio

import pytest
from mcp.shared.exceptions import MCPError
from mcp.types import Tool

from ai_engineer_roadmap.mcp_client import (
    discover_openai_tools,
    mcp_tool_to_openai_tool,
)


def test_mcp_tool_to_openai_tool_converts_tool_definition():
    input_schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
        },
        "required": ["title"],
    }
    tool = Tool(
        name="create_task",
        description="Create a task.",
        input_schema=input_schema,
    )

    converted = mcp_tool_to_openai_tool(tool)

    assert converted == {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "Create a task.",
            "parameters": input_schema,
        },
    }


import json
from types import SimpleNamespace

from ai_engineer_roadmap.mcp_client import call_mcp_tool


class FakeMCPClient:
    def __init__(self, result):
        self.result = result
        self.last_call = None

    async def call_tool(self, name, arguments):
        self.last_call = (name, arguments)
        return self.result


def test_call_mcp_tool_unwraps_success_result():
    client = FakeMCPClient(
        SimpleNamespace(
            is_error=False,
            structured_content={
                "result": {"success": True, "message": "Task created."}
            },
        )
    )

    result = asyncio.run(call_mcp_tool(client, "create_task", {"title": "Review"}))

    assert json.loads(result) == {"success": True, "message": "Task created."}
    assert client.last_call == ("create_task", {"title": "Review"})


def test_call_mcp_tool_wraps_mcp_error():
    client = FakeMCPClient(
        SimpleNamespace(is_error=True, content=["server unavailable"])
    )

    result = asyncio.run(call_mcp_tool(client, "get_tasks", {}))

    assert json.loads(result) == {
        "success": False,
        "message": "['server unavailable']",
        "error_type": "MCP_CALL_FAILED",
    }


def test_call_mcp_tool_wraps_mcp_exception():
    class RaisingMCPClient:
        async def call_tool(self, name, arguments):
            raise MCPError(-32000, "connection lost")

    result = asyncio.run(
        call_mcp_tool(
            RaisingMCPClient(),
            "get_tasks",
            {},
        )
    )

    assert json.loads(result) == {
        "success": False,
        "message": "MCP call failed: connection lost",
        "error_type": "MCP_CALL_FAILED",
    }


def test_discover_openai_tools_propagates_mcp_error():
    class RaisingMCPClient:
        async def list_tools(self):
            raise MCPError(-32000, "tool discovery failed")

    with pytest.raises(MCPError, match="tool discovery failed"):
        asyncio.run(discover_openai_tools(RaisingMCPClient()))
