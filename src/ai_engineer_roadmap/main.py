from ai_engineer_roadmap.llm import ask_llm_with_tools
from ai_engineer_roadmap.task_manager import TaskManager

if __name__ == "__main__":
    task_manager = TaskManager()

    print("=== Before ===")
    for task in task_manager.get_tasks():
        print(task)

    result = ask_llm_with_tools("Complete task 3", task_manager)

    print()
    print("=== AI Response ===")
    print(result)

    print()
    print("=== After ===")
    for task in task_manager.get_tasks():
        print(task)
