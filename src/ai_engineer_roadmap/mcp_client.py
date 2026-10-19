import asyncio
import json

from mcp import Client
from mcp.client.stdio import StdioServerParameters
from mcp.types import Tool

server_params = StdioServerParameters(
    command="uv", args=["run", "python", "-m", "ai_engineer_roadmap.mcp_server"]
)


async def call_mcp_tool(
    client: Client,
    name: str,
    arguments: dict,
) -> str:
    result = await client.call_tool(name, arguments)
    if result.is_error:
        return json.dumps(
            {
                "success": False,
                "message": str(result.content),
                "error_type": "MCP_CALL_FAILED",
            },
            ensure_ascii=False,
        )
    payload = result.structured_content
    # SDK 会把 Server 返回值放在 "result" 字段里。
    if isinstance(payload, dict) and set(payload) == {"result"}:
        payload = payload["result"]
    return json.dumps(payload, ensure_ascii=False)


def mcp_tool_to_openai_tool(tool: Tool) -> dict:
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or "",
            "parameters": tool.input_schema,
        },
    }


async def discover_openai_tools(client: Client) -> list[dict]:
    tools_result = await client.list_tools()
    return [mcp_tool_to_openai_tool(tool) for tool in tools_result.tools]


async def main() -> None:
    try:
        async with Client(server_params) as client:
            openai_tools = await discover_openai_tools(client)
            print("转换后的工具定义：")
            for tool in openai_tools:
                function = tool["function"]
                print(f"- {function['name']}: {function['parameters']}")

            result = await call_mcp_tool(client, "get_tasks", {})
            task_items = json.loads(result)
            if not isinstance(task_items, list):
                print("读取失败", result)
                return

            print(f"读取成功：共 {len(task_items)} 条任务")
    except OSError as error:
        print(f"无法启动 MCP Server：{error}")


if __name__ == "__main__":
    asyncio.run(main())
