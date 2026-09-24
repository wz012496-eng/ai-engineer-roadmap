import json

from ai_engineer_roadmap.models import Priority
from ai_engineer_roadmap.task_manager import TaskManager


def test_complete_task_is_persisted(tmp_path):
    data_file = tmp_path / "tasks.json"

    task_manager = TaskManager(data_file)

    task_manager.create_task("Build AI agent", Priority.HIGH)

    task_id = task_manager.get_tasks()[0].id
    task_manager.complete_task(task_id)

    new_task_manager = TaskManager(data_file)

    task = new_task_manager.get_task_by_id(task_id)

    assert task is not None
    assert task.completed is True


def test_load_tasks_skips_invalid_task(tmp_path):
    data_file = tmp_path / "tasks.json"

    data  = [
         {
            "id": 1,
            "title": "Learn Python",
            "priority": "high",
            "completed": False,
        },
        {
            "id": 2,
            "title": "Bad Task",
            "priority": "urgent",
            "completed": False,
        },
        {
            "id": 3,
            "title": "Build AI Agent",
            "priority": "high",
            "completed": True,
        },
    ]

    data_file.write_text(
        json.dumps(data),
        encoding="utf-8"
    )

    task_manager = TaskManager(data_file)
    tasks = task_manager.get_tasks()

    titles = [task.title for task in tasks]

    assert len(tasks) == 2
    assert "Learn Python" in titles
    assert "Build AI Agent" in titles
    assert "Bad Task" not in titles