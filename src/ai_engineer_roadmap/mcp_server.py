import json
from typing import NotRequired, TypedDict

from mcp.server import MCPServer

from ai_engineer_roadmap.repository import TaskRepository
from ai_engineer_roadmap.task_manager import TaskManager
from ai_engineer_roadmap.tools import complete_task_tool as run_complete_task_tool
from ai_engineer_roadmap.tools import create_task_tool as run_create_task_tool


class TaskOutput(TypedDict):
    id: int
    title: str
    priority: str
    completed: bool


class ToolResult(TypedDict):
    success: bool
    message: str
    error_type: NotRequired[str]


mcp = MCPServer("ai-engineer-roadmap")
task_manager = TaskManager(TaskRepository())


@mcp.tool()
def get_tasks() -> list[TaskOutput]:
    """Return all tasks."""
    return [
        {
            "id": task.id,
            "title": task.title,
            "priority": task.priority.value,
            "completed": task.completed,
        }
        for task in task_manager.get_tasks()
    ]


@mcp.tool()
def create_task(title: str, priority: str) -> ToolResult:
    """Create a task with the given title and priority."""
    result = run_create_task_tool(task_manager, title, priority)
    return json.loads(result)


@mcp.tool()
def complete_task(task_id: int) -> ToolResult:
    """Mark a task as completed by its ID."""
    result = run_complete_task_tool(task_manager, task_id)
    return json.loads(result)


if __name__ == "__main__":
    mcp.run()
