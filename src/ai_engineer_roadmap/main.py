from ai_engineer_roadmap.llm import ask_llm_with_tools
from ai_engineer_roadmap.task_manager import TaskManager

if __name__ == "__main__":
    task_manager = TaskManager()

    print("=== Before ===")
    for task in task_manager.get_tasks():
        print(task)

    result = ask_llm_with_tools("创建一个低优先级任务 Buy Milk，然后告诉我现在有哪些任务", task_manager)

    print()
    print("=== AI Response ===")
    print(result)

    print()
    print("=== After ===")
    for task in task_manager.get_tasks():
        print(task)
