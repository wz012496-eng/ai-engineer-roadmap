from pathlib import Path

from ai_engineer_roadmap.conversation import ConversationStore
from ai_engineer_roadmap.llm import ask_llm_with_tools
from ai_engineer_roadmap.repository import TaskRepository
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
    task_repository = TaskRepository()
    task_manager = TaskManager(task_repository)

    conversation_file = Path("conversations.json")
    if conversation_file.exists():
        conversation_store = ConversationStore.load(conversation_file)
    else:
        conversation_store = ConversationStore()

    conversation = conversation_store.get_or_create(conversation_id=1)

    while True:
        user_input = input("You: ")
        if user_input == "exit":
            break
        conversation.messages.append({"role": "user", "content": user_input})

        result = ask_llm_with_tools(conversation.messages, task_manager)

        conversation.messages = trim_messages(conversation.messages, max_length=3)
        conversation_store.save(conversation_file)

        print(f"AI: {result}")
