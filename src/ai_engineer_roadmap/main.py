from ai_engineer_roadmap.llm import ask_llm
from ai_engineer_roadmap.task_manager import TaskManager

if __name__ == "__main__":
    task_manager = TaskManager()

    answer = ask_llm("给我一个学习 Python dataclass 的建议")

    print("=== AI Response ===")
    print(answer)
