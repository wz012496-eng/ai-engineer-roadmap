from ai_engineer_roadmap.models import Priority, Task
from ai_engineer_roadmap.repository import TaskRepositoryProtocol


class TaskManager:
    def __init__(self, repository: TaskRepositoryProtocol) -> None:
        self.repository = repository
        self.tasks = self.repository.load_tasks()

    def get_tasks(self) -> list[Task]:
        return self.tasks

    def create_task(self, title: str, priority: Priority) -> dict[str, str | bool]:
        if self.tasks:
            task_id = max(task.id for task in self.tasks) + 1
        else:
            task_id = 1
        task = Task(id=task_id, title=title, priority=priority, completed=False)
        self.tasks.append(task)
        self.repository.save_tasks(self.tasks)
        return {
            "success": True,
            "message": f"Task {task_id} created successfully.",
        }

    def complete_task(self, task_id: int) -> dict[str, str | bool]:
        for task in self.get_tasks():
            if task.id == task_id:
                if task.completed:
                    return {
                        "success": False,
                        "error": f"Task {task_id} is already completed.",
                    }
                task.completed = True
                self.repository.save_tasks(self.tasks)

                return {
                    "success": True,
                    "message": f"Task {task_id} completed successfully.",
                }

        return {
            "success": False,
            "error": f"Task {task_id} does not exist.",
        }

    def get_high_priority_tasks(self) -> list[Task]:
        result = []
        for task in self.get_tasks():
            if task.priority == Priority.HIGH and not task.completed:
                result.append(task)
        return result

    def delete_task(self, task_id: int) -> None:
        for task in self.get_tasks():
            if task.id == task_id:
                self.tasks.remove(task)
                self.repository.save_tasks(self.tasks)
                break

    def get_task_by_id(self, task_id: int) -> Task | None:
        for task in self.get_tasks():
            if task.id == task_id:
                return task
        return None

    def get_task_stats(self) -> dict[str, int]:
        total = len(self.get_tasks())
        completed = sum(1 for task in self.get_tasks() if task.completed)
        pending = total - completed
        high_priority = sum(
            1
            for task in self.get_tasks()
            if task.priority == Priority.HIGH and not task.completed
        )
        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "high_priority": high_priority,
        }
