from ai_engineer_roadmap.llm import suggest_task
from ai_engineer_roadmap.task_manager import TaskManager

if __name__ == "__main__":
    task_manager = TaskManager()

    task = task_manager.get_task_by_id(3)

    if task is not None:
        suggestion = suggest_task(task)
        print("=== Summary ===")
        print(suggestion.summary)
        print("\n=== Steps ===")
        for step in suggestion.steps:
            print(step)
