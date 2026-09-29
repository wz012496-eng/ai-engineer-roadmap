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

    while True:
        conversation_ids = conversation_store.conversation_ids()
        print(f"已有会话 ID：{conversation_ids}")

        choice = (
            input(
                "输入会话 ID 选择会话，输入 new 新建，"
                "输入 delete 删除会话，输入 exit 退出："
            )
            .strip()
            .lower()
        )

        if choice == "exit":
            print("已退出。")
            raise SystemExit(0)

        if choice == "delete":
            delete_input = input("输入要删除的会话 ID，输入 cancel 取消：").strip()

            if delete_input.lower() == "cancel":
                continue

            if not delete_input.isdigit() or int(delete_input) not in conversation_ids:
                print("请输入列表中的会话 ID。")
                continue

            conversation_id = int(delete_input)
            conversation_store.delete(conversation_id)
            conversation_store.save(conversation_file)
            print(f"会话 {conversation_id} 已删除。")
            continue

        if choice == "new":
            conversation = conversation_store.create_new()
        elif choice.isdigit() and int(choice) in conversation_ids:
            conversation = conversation_store.get_or_create(int(choice))
        else:
            print("请输入已有的会话 ID，或输入 new、delete、exit。")
            continue

        conversation_store.save(conversation_file)
        print(f"已进入会话 {conversation.conversation_id}。")

        while True:
            user_input = input(
                "You（输入 :back 返回会话列表，:delete 删除当前会话，exit 退出）："
            )
            command = user_input.strip().lower()

            if command == "exit":
                print("已退出。")
                raise SystemExit(0)

            if command == ":back":
                break

            if command == ":delete":
                conversation_id = conversation.conversation_id
                conversation_store.delete(conversation_id)
                conversation_store.save(conversation_file)
                print(f"会话 {conversation_id} 已删除。")
                break

            conversation.messages.append({"role": "user", "content": user_input})
            result = ask_llm_with_tools(conversation.messages, task_manager)

            conversation.messages = trim_messages(
                conversation.messages,
                max_length=3,
            )
            conversation_store.save(conversation_file)

            print(f"AI: {result}")
