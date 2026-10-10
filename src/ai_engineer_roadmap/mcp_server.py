from typing import TypedDict

from mcp.server import MCPServer

from ai_engineer_roadmap.repository import TaskRepository
from ai_engineer_roadmap.task_manager import TaskManager


class TaskOutput(TypedDict):
    id: int
    title: str
    priority: str
    completed: bool


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


if __name__ == "__main__":
    mcp.run()
