import json

from ai_engineer_roadmap.models import Priority
from ai_engineer_roadmap.task_manager import TaskManager

COMPLETE_TASK_TOOL = {
    "type": "function",
    "function": {
        "name": "complete_task",
        "description": "Complete a task by its ID",
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "integer",
                    "description": "The ID of the task to complete",
                },
            },
            "required": ["task_id"],
        },
    },
}


GET_TASKS_TOOL = {
    "type": "function",
    "function": {
        "name": "get_tasks",
        "description": "Get all tasks",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
}

CREATE_TASK_TOOL = {
    "type": "function",
    "function": {
        "name": "create_task",
        "description": "Create a new task",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "The title of the new task",
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "high"],
                    "description": "The priority of the new task",
                },
            },
            "required": ["title", "priority"],
        },
    },
}


def complete_task_tool(task_manager: TaskManager, task_id: int) -> str:
    task_manager.complete_task(task_id)
    return f"Task {task_id} completed successfully."


def get_tasks_tool(task_manager: TaskManager) -> str:
    tasks = task_manager.get_tasks()
    result = []
    for task in tasks:
        result.append(
            {
                "id": task.id,
                "title": task.title,
                "priority": task.priority.value,
                "completed": task.completed,
            }
        )
    return json.dumps(result, ensure_ascii=False)


def create_task_tool(task_manager: TaskManager, title: str, priority: str) -> str:
    task_manager.create_task(title, Priority(priority))
    return f"Task '{title}' created successfully with priority '{priority}'."


def execute_tool_call(task_manager: TaskManager, tool_call) -> str:
    function_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)

    if function_name == "complete_task":
        return complete_task_tool(task_manager, arguments["task_id"])

    if function_name == "get_tasks":
        return get_tasks_tool(task_manager)

    if function_name == "create_task":
        title = arguments["title"]
        priority = arguments["priority"]
        return create_task_tool(task_manager, title, priority)
    return f"Unknown tool function: {function_name}"
