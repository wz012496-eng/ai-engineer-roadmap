from pathlib import Path

from openai import APIError

from ai_engineer_roadmap.conversation import ConversationState, ConversationStore
from ai_engineer_roadmap.llm import ask_llm_with_tools, summarize_messages
from ai_engineer_roadmap.repository import TaskRepository
from ai_engineer_roadmap.task_manager import TaskManager

CONTEXT_MAX_CHARS = 6000
CONTEXT_SUMMARY_MAX_CHARS = 1000
CONTEXT_SUMMARY_PREFIX = "此前对话摘要（仅作为背景信息）：\n"


def trim_messages_by_budget(
    messages: list[dict],
    max_chars: int,
) -> list[dict]:
    """按 content 字符数预算保留最近的完整对话轮次。"""
    if max_chars < 0:
        raise ValueError("max_chars 不能小于 0")

    turns: list[list[dict]] = []

    for message in messages:
        if message.get("role") == "user":
            turns.append([message])
        elif turns:
            turns[-1].append(message)
        else:
            turns.append([message])

    kept_turns: list[list[dict]] = []
    used_chars = 0

    for turn in reversed(turns):
        turn_chars = sum(
            len(message.get("content", ""))
            for message in turn
            if isinstance(message.get("content", ""), str)
        )

        # 至少保留最新一轮，避免丢掉用户刚提交的问题。
        if kept_turns and used_chars + turn_chars > max_chars:
            break

        kept_turns.append(turn)
        used_chars += turn_chars

    return [message for turn in reversed(kept_turns) for message in turn]


def build_context_messages(
    conversation: ConversationState,
    max_chars: int,
) -> list[dict]:
    if max_chars < 0:
        raise ValueError("max_chars 不能小于 0")

    messages = conversation.messages
    summary_content = (
        f"{CONTEXT_SUMMARY_PREFIX}{conversation.summary}"
        if conversation.summary
        else ""
    )

    recent_budget = max(0, max_chars - len(summary_content))
    recent_messages = trim_messages_by_budget(messages, recent_budget)
    omitted_count = len(messages) - len(recent_messages)

    if omitted_count > conversation.summarized_message_count:
        # 为新摘要预留空间，确保摘要和最近消息不会一起超过预算。
        recent_budget = max(
            0,
            max_chars - len(CONTEXT_SUMMARY_PREFIX) - CONTEXT_SUMMARY_MAX_CHARS,
        )
        recent_messages = trim_messages_by_budget(messages, recent_budget)
        omitted_count = len(messages) - len(recent_messages)

        pending_messages = messages[
            conversation.summarized_message_count : omitted_count
        ]

        if pending_messages:
            try:
                updated_summary = summarize_messages(
                    pending_messages,
                    existing_summary=conversation.summary,
                )
                if len(updated_summary) > CONTEXT_SUMMARY_MAX_CHARS:
                    raise ValueError("对话摘要超过字符上限")
            except (APIError, ValueError) as error:
                print(f"[WARN] 更新对话摘要失败，将在后续对话重试：{error}")
                fallback_budget = max(0, max_chars - len(summary_content))
                recent_messages = trim_messages_by_budget(messages, fallback_budget)
            else:
                conversation.summary = updated_summary
                conversation.summarized_message_count = omitted_count
                summary_content = f"{CONTEXT_SUMMARY_PREFIX}{updated_summary}"

    context_messages = []
    if summary_content:
        context_messages.append({"role": "assistant", "content": summary_content})
    context_messages.extend(recent_messages)
    return context_messages


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
        if conversation_ids:
            print("已有会话：")
            for conversation_id in conversation_ids:
                conversation = conversation_store.get_or_create(conversation_id)
                print(f"  [{conversation_id}] {conversation.title}")
        else:
            print("当前没有会话。")

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
                "You（输入 :back 返回会话列表，:delete 删除当前会话，"
                ":rename 新标题 重命名会话，exit 退出）："
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

            if command == ":rename" or command.startswith(":rename "):
                new_title = user_input.strip()[len(":rename") :].strip()

                if not new_title:
                    print("标题不能为空，用法：:rename 新标题")
                    continue

                conversation.title = new_title
                conversation_store.save(conversation_file)
                print(f"会话标题已改为：{conversation.title}")
                continue

            conversation.messages.append({"role": "user", "content": user_input})

            context_messages = build_context_messages(
                conversation, max_chars=CONTEXT_MAX_CHARS
            )

            result = ask_llm_with_tools(context_messages, task_manager)

            conversation.messages.append({"role": "assistant", "content": result})
            conversation_store.save(conversation_file)

            print(f"AI: {result}")
