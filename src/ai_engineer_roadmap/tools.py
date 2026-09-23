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
                    "description": "The priority of the new task",
                },
            },
            "required": ["title", "priority"],
        },
    },
}


def tool_result(
    success: bool, message: str = "", error_type: str | None = None, data=None
) -> str:
    result = {
        "success": success,
        "message": message,
    }
    if error_type is not None:
        result["error_type"] = error_type
    if data is not None:
        result["data"] = data
    return json.dumps(result, ensure_ascii=False)


def complete_task_tool(task_manager: TaskManager, task_id: int) -> str:
    result = task_manager.complete_task(task_id)
    if result["success"]:
        return tool_result(success=True, message=result["message"])
    else:
        return tool_result(
            success=False,
            message=result["error"],
            error_type="TASK_NOT_FOUND",
        )


def get_tasks_tool(task_manager: TaskManager) -> str:
    tasks = task_manager.get_tasks()
    data = []
    for task in tasks:
        data.append(
            {
                "id": task.id,
                "title": task.title,
                "priority": task.priority.value,
                "completed": task.completed,
            }
        )
    return tool_result(success=True, message=f"Found {len(data)} tasks.", data=data)


def create_task_tool(task_manager: TaskManager, title: str, priority: str) -> str:
    try:
        task_manager.create_task(title, Priority(priority))
        return tool_result(
            success=True,
            message=f"Task '{title}' created successfully with priority '{priority}'.",
        )
    except ValueError:
        return tool_result(
            success=False,
            message=f"Invalid priority '{priority}'. Priority must be 'low' or 'high'.",
            error_type="INVALID_ARGUMENT",
        )


def execute_tool_call(task_manager: TaskManager, tool_call) -> str:
    try:
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
        return tool_result(
            success=False,
            message=f"Unknown tool function: {function_name}",
            error_type="UNKNOWN_FUNCTION",
        )
    except json.JSONDecodeError:
        return tool_result(
            success=False,
            message="Tool arguments are not valid JSON.",
            error_type="INVALID_JSON",
        )

    except KeyError as error:
        return tool_result(
            success=False,
            message=f"Missing required argument: {error}",
            error_type="MISSING_ARGUMENT",
        )

    except (TypeError, ValueError) as error:
        return tool_result(
            success=False,
            message=f"Invalid tool argument: {error}",
            error_type="INVALID_ARGUMENT",
        )
