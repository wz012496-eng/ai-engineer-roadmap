import asyncio

from mcp import Client
from mcp.client.stdio import StdioServerParameters

server_params = StdioServerParameters(
    command="uv", args=["run", "python", "-m", "ai_engineer_roadmap.mcp_server"]
)


async def main() -> None:
    try:
        async with Client(server_params) as client:
            tools_result = await client.list_tools()
            print("MCP Server 提供的工具：")
            for tool in tools_result.tools:
                print(f"- {tool.name}: {tool.description}")

            result = await client.call_tool("get_tasks", {})
            if result.is_error:
                print("MCP 工具调用失败：", result.content)
                return

            task_items = result.structured_content["result"]
            print(f"读取成功：共 {len(task_items)} 条任务")
    except OSError as error:
        print(f"无法启动 MCP Server：{error}")


if __name__ == "__main__":
    asyncio.run(main())
