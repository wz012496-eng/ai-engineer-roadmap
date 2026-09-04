from ai_engineer_roadmap.models import Priority
from ai_engineer_roadmap.task_manager import TaskManager

task_manager = TaskManager()

if __name__ == "__main__":
    task_manager.create_task(4, "Learn AI", Priority.HIGH)

    task = task_manager.get_task_by_id(3)
    print(task)

    print("=== Before Delete ===")

    for task in task_manager.get_tasks():
        print(f"[{task.id}] {task.title}")

    task_manager.delete_task(2)

    print("=== After Delete ===")

    for task in task_manager.get_tasks():
        print(f"[{task.id}] {task.title}")
