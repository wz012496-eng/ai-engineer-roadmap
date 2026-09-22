from ai_engineer_roadmap.llm import ask_llm_with_tools
from ai_engineer_roadmap.task_manager import TaskManager


def trim_messages(messages: list[dict], max_length: int = 3) -> list[dict]:
    user_indexes = []
    for index, message in enumerate(messages):
        if isinstance(message, dict) and message.get("role") == "user":
            user_indexes.append(index)

    if len(user_indexes) <= max_length:
        return messages
    split_index = user_indexes[-max_length]
    return messages[split_index:]


if __name__ == "__main__":
    task_manager = TaskManager()
    messages = []

    while True:
        user_input = input("You: ")
        if user_input == "exit":
            break
        messages.append({"role": "user", "content": user_input})

        result = ask_llm_with_tools(messages, task_manager)

        messages = trim_messages(messages, max_length=3)

        print(f"AI: {result}")
