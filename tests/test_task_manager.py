import json
from copy import deepcopy

from ai_engineer_roadmap.models import Priority, Task
from ai_engineer_roadmap.repository import TaskRepository
from ai_engineer_roadmap.task_manager import TaskManager


class FakeTaskRepository:
    def __init__(self) -> None:
        self.tasks = []

    def load_tasks(self):
        return deepcopy(self.tasks)

    def save_tasks(self, tasks: list[Task]):
        self.tasks = deepcopy(tasks)


def test_complete_task_is_persisted(tmp_path):
    repository = TaskRepository()
    task_manager = TaskManager(repository)

    task_manager.create_task("Build AI agent", Priority.HIGH)

    task_id = task_manager.get_tasks()[0].id
    task_manager.complete_task(task_id)

    new_task_manager = TaskManager(repository)

    task = new_task_manager.get_task_by_id(task_id)

    assert task is not None
    assert task.completed is True


def test_load_tasks_skips_invalid_task(tmp_path):
    data_file = tmp_path / "tasks.json"

    data = [
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

    data_file.write_text(json.dumps(data), encoding="utf-8")
    repository = TaskRepository(data_file)

    task_manager = TaskManager(repository)
    tasks = task_manager.get_tasks()

    titles = [task.title for task in tasks]

    assert len(tasks) == 2
    assert "Learn Python" in titles
    assert "Build AI Agent" in titles
    assert "Bad Task" not in titles


def test_complete_task_with_fake_repository():
    repository = FakeTaskRepository()

    repository.tasks = [
        Task(
            id=1,
            title="Learn Python",
            priority=Priority.HIGH,
            completed=False,
        )
    ]

    task_manager = TaskManager(repository)

    result = task_manager.complete_task(1)

    assert result["success"] is True
    assert repository.tasks[0].completed is True
