import json
from dataclasses import asdict
from pathlib import Path
from typing import Protocol

from ai_engineer_roadmap.models import Priority, Task


class TaskRepositoryProtocol(Protocol):
    def load_tasks(self) -> list[Task]: ...
    def save_tasks(self, tasks: list[Task]) -> None: ...


class TaskRepository:
    def __init__(self, data_file: Path | None = None) -> None:
        self.data_file = data_file or Path("tasks.json")

    def load_tasks(self) -> list[Task]:
        if not self.data_file.exists():
            return []

        try:
            with self.data_file.open("r", encoding="utf-8") as file:
                data = json.load(file)

            result = []
            for item in data:
                try:
                    task = Task(
                        id=item["id"],
                        title=item["title"],
                        priority=Priority(item["priority"]),
                        completed=item["completed"],
                    )
                    result.append(task)
                except (ValueError, KeyError, TypeError):
                    continue

            return result
        except json.JSONDecodeError:
            return []

    def save_tasks(self, tasks: list[Task]) -> None:
        data = [asdict(task) for task in tasks]
        with self.data_file.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
