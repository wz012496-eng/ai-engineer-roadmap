import json
from types import SimpleNamespace

from ai_engineer_roadmap.repository import TaskRepository
from ai_engineer_roadmap.task_manager import TaskManager
from ai_engineer_roadmap.tools import (
    complete_task_tool,
    create_task_tool,
    execute_tool_call,
)


def test_complete_nonexistent_task(tmp_path):
    repository = TaskRepository(tmp_path / "tasks.json")

    task_manager = TaskManager(repository)
    result = complete_task_tool(task_manager, task_id=999)
    data = json.loads(result)

    assert data["success"] is False
    assert data["error_type"] == "TASK_NOT_FOUND"
    assert "999" in data["message"]


def test_create_task_with_invalid_priority(tmp_path):
    repository = TaskRepository(tmp_path / "tasks.json")

    task_manager = TaskManager(repository)
    result = create_task_tool(task_manager, title="Test Task", priority="urgent")
    data = json.loads(result)

    assert data["success"] is False
    assert data["error_type"] == "INVALID_ARGUMENT"
    assert "urgent" in data["message"]

    tasks = task_manager.get_tasks()
    titles = [task.title for task in tasks]

    assert "Test Task" not in titles


def test_execute_tool_call_with_missing_argument(tmp_path):
    repository = TaskRepository(tmp_path / "tasks.json")
    task_manager = TaskManager(repository)

    tool_call = SimpleNamespace(
        function=SimpleNamespace(name="create_task", arguments='{"title": "Buy Milk"}')
    )

    result = execute_tool_call(task_manager, tool_call)
    data = json.loads(result)

    assert data["success"] is False
    assert data["error_type"] == "MISSING_ARGUMENT"
    assert "priority" in data["message"]


def test_execute_tool_call_with_invalid_json(tmp_path):
    repository = TaskRepository(tmp_path / "tasks.json")

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


def test_execute_unknown_tool(tmp_path):
    repository = TaskRepository(tmp_path / "tasks.json")

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


def test_create_task_success(tmp_path):
    repository = TaskRepository(tmp_path / "tasks.json")

    task_manager = TaskManager(repository)

    result = create_task_tool(task_manager, "Buy Milk", "high")
    data = json.loads(result)

    assert data["success"] is True
    assert "created successfully" in data["message"]

    tasks = task_manager.get_tasks()
    titles = [task.title for task in tasks]

    assert "Buy Milk" in titles


def test_complete_task_tool_already_completed(tmp_path):
    data_file = tmp_path / "tasks.json"
    data_file.write_text(
        json.dumps(
            [
                {
                    "id": 1,
                    "title": "Task already completed",
                    "priority": "high",
                    "completed": True,
                }
            ]
        ),
        encoding="utf-8",
    )

    repository = TaskRepository(data_file)
    task_manager = TaskManager(repository)

    result = task_manager.complete_task(1)
    assert not result.success
    assert result.error_type == "TASK_ALREADY_COMPLETED"
