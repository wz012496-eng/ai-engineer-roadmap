import json
from types import SimpleNamespace

from ai_engineer_roadmap.repository import TaskRepository
from ai_engineer_roadmap.task_manager import TaskManager
from ai_engineer_roadmap.tools import (
    complete_task_tool,
    create_task_tool,
    execute_tool_call,
)


def test_complete_nonexistent_task():
    repository = TaskRepository()

    task_manager = TaskManager(repository)
    result = complete_task_tool(task_manager, task_id=999)
    data = json.loads(result)

    assert data["success"] is False
    assert data["error_type"] == "TASK_NOT_FOUND"
    assert "999" in data["message"]


def test_create_task_with_invalid_priority():
    repository = TaskRepository()

    task_manager = TaskManager(repository)
    result = create_task_tool(task_manager, title="Test Task", priority="urgent")
    data = json.loads(result)

    assert data["success"] is False
    assert data["error_type"] == "INVALID_ARGUMENT"
    assert "urgent" in data["message"]

    tasks = task_manager.get_tasks()
    titles = [task.title for task in tasks]

    assert "Test Task" not in titles


def test_execute_tool_call_with_missing_argument():
    repository = TaskRepository()

    task_manager = TaskManager(repository)

    tool_call = SimpleNamespace(
        function=SimpleNamespace(name="create_task", arguments='{"title": "Buy Milk"}')
    )

    result = execute_tool_call(task_manager, tool_call)
    data = json.loads(result)

    assert data["success"] is False
    assert data["error_type"] == "MISSING_ARGUMENT"
    assert "priority" in data["message"]


def test_execute_tool_call_with_invalid_json():
    repository = TaskRepository()

    task_manager = TaskManager(repository)

    tool_call = SimpleNamespace(
        function=SimpleNamespace(
            name="create_task",
            arguments='{"title": "Buy Milk", "priority": "high"',
        )
    )

    result = execute_tool_call(task_manager, tool_call)
    data = json.loads(result)

    assert data["success"] is False
    assert data["error_type"] == "INVALID_JSON"
    assert data["message"] == "Tool arguments are not valid JSON."


def test_execute_unknown_tool():
    repository = TaskRepository()

    task_manager = TaskManager(repository)

    tool_call = SimpleNamespace(
        function=SimpleNamespace(
            name="delete_task",
            arguments="{}",
        )
    )

    result = execute_tool_call(task_manager, tool_call)
    data = json.loads(result)

    assert data["success"] is False
    assert data["error_type"] == "UNKNOWN_FUNCTION"
    assert "delete_task" in data["message"]


def test_create_task_success():
    repository = TaskRepository()

    task_manager = TaskManager(repository)

    result = create_task_tool(task_manager, "Buy Milk", "high")
    data = json.loads(result)

    assert data["success"] is True
    assert data["message"] == (
        "Task 'Buy Milk' created successfully with priority 'high'."
    )

    tasks = task_manager.get_tasks()
    titles = [task.title for task in tasks]

    assert "Buy Milk" in titles
