import json

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


def complete_task_tool(task_manager: TaskManager, task_id: int) -> str:
    task_manager.complete_task(task_id)
    return f"Task {task_id} completed successfully."


def execute_tool_call(task_manager: TaskManager, tool_call) -> str:
    function_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)

    if function_name == "complete_task":
        return complete_task_tool(task_manager, arguments["task_id"])
    return f"Unknown tool function: {function_name}"
