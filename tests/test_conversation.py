import json

from ai_engineer_roadmap.conversation import ConversationState, ConversationStore


def test_get_or_create_reuses_state_for_same_id():
    store = ConversationStore()

    first = store.get_or_create(1)
    second = store.get_or_create(1)
    assert first is second


def test_different_ids_have_separate_messages():
    store = ConversationStore()

    first = store.get_or_create(1)
    second = store.get_or_create(2)
    first.messages.append({"role": "user", "content": "你好"})

    assert first is not second
    assert second.messages == []


def test_conversation_state_to_dict():
    state = ConversationState(
        conversation_id=1, messages=[{"role": "user", "content": "你好"}]
    )
    assert state.to_dict() == {
        "conversation_id": 1,
        "title": "会话 1",
        "messages": [{"role": "user", "content": "你好"}],
        "summary": "",
        "summarized_message_count": 0,
    }


def test_conversation_sore_to_dict():
    store = ConversationStore()
    first = store.get_or_create(1)
    first.messages.append({"role": "user", "content": "你好"})

    store.get_or_create(2)

    assert store.to_dict() == [
        {
            "conversation_id": 1,
            "title": "会话 1",
            "messages": [{"role": "user", "content": "你好"}],
            "summary": "",
            "summarized_message_count": 0,
        },
        {
            "conversation_id": 2,
            "title": "会话 2",
            "messages": [],
            "summary": "",
            "summarized_message_count": 0,
        },
    ]


def test_conversation_store_from_dict():
    data = [
        {
            "conversation_id": 1,
            "title": "会话 1",
            "messages": [{"role": "user", "content": "你好"}],
            "summary": "",
            "summarized_message_count": 0,
        },
        {
            "conversation_id": 2,
            "title": "会话 2",
            "messages": [],
            "summary": "",
            "summarized_message_count": 0,
        },
    ]
    store = ConversationStore.from_dict(data=data)
    assert store.to_dict() == data


def test_conversation_store_save(tmp_path):
    store = ConversationStore()
    store.get_or_create(1).messages.append({"role": "user", "content": "你好"})
    file_path = tmp_path / "conversations.json"

    store.save(file_path)

    restored_store = ConversationStore.load(file_path)
    assert restored_store.to_dict() == store.to_dict()

    saved_data = json.loads(file_path.read_text(encoding="utf-8"))
    assert saved_data == store.to_dict()


def test_conversation_store_saves_and_loads_multiple_conversations(tmp_path):
    file_path = tmp_path / "conversations.json"
    store = ConversationStore()

    first = store.get_or_create(1)
    first.messages.append({"role": "user", "content": "第一段对话"})

    second = store.get_or_create(2)
    second.messages.append({"role": "user", "content": "第二段对话"})

    store.save(file_path)
    loaded_store = ConversationStore.load(file_path)

    assert loaded_store.get_or_create(1).messages == [
        {"role": "user", "content": "第一段对话"}
    ]
    assert loaded_store.get_or_create(2).messages == [
        {"role": "user", "content": "第二段对话"}
    ]


def test_create_new_conversation_uses_next_available_id():
    store = ConversationStore()
    store.get_or_create(1)
    store.get_or_create(3)

    conversation = store.create_new()

    assert conversation.conversation_id == 4
    assert conversation.messages == []
    assert store.get_or_create(4) is conversation


def test_conversation_ids_returns_sorted_ids():
    store = ConversationStore()
    store.get_or_create(3)
    store.get_or_create(1)

    assert store.conversation_ids() == [1, 3]


def test_delete_removes_only_the_selected_conversation():
    store = ConversationStore()
    store.get_or_create(1).messages.append({"role": "user", "content": "会话 1"})
    store.get_or_create(2).messages.append({"role": "user", "content": "会话 2"})

    assert store.delete(1) is True
    assert store.conversation_ids() == [2]
    assert store.get_or_create(2).messages == [{"role": "user", "content": "会话 2"}]
    assert store.delete(999) is False


def test_conversation_store_loads_legacy_data_without_title():
    store = ConversationStore.from_dict([{"conversation_id": 7, "messages": []}])

    assert store.get_or_create(7).title == "会话 7"


def test_custom_title_survives_save_and_load(tmp_path):
    store = ConversationStore()
    store.get_or_create(1).title = "AI 学习"
    file_path = tmp_path / "conversations.json"

    store.save(file_path)
    loaded_store = ConversationStore.load(file_path)

    assert loaded_store.get_or_create(1).title == "AI 学习"


def test_conversation_summary_is_persisted():
    store = ConversationStore.from_dict(
        [
            {
                "conversation_id": 1,
                "messages": [],
                "summary": "用户正在开发任务管理 Agent。",
                "summarized_message_count": 3,
            }
        ]
    )

    assert store.get_or_create(1).summary == "用户正在开发任务管理 Agent。"
    assert store.to_dict()[0]["summary"] == "用户正在开发任务管理 Agent。"

    assert store.get_or_create(1).summarized_message_count == 3
    assert store.to_dict()[0]["summarized_message_count"] == 3


def test_legacy_conversation_defaults_to_empty_summary():
    store = ConversationStore.from_dict([{"conversation_id": 1, "messages": []}])

    assert store.get_or_create(1).summary == ""
    assert store.to_dict()[0]["summary"] == ""
