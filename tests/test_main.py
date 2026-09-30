from importlib import import_module

main_module = import_module("ai_engineer_roadmap.main")
from ai_engineer_roadmap.conversation import ConversationState
from ai_engineer_roadmap.main import trim_messages_by_budget


def test_trim_messages_by_budget_keeps_latest_turn_if_it_exceeds_budget():
    messages = [
        {"role": "user", "content": "旧问题"},
        {"role": "assistant", "content": "旧回答"},
        {"role": "user", "content": "这是一个很长的新问题"},
        {"role": "assistant", "content": "这是一个很长的新回答"},
    ]

    result = trim_messages_by_budget(messages, max_chars=5)

    assert result == messages[2:]


def test_trim_messages_by_budget_keeps_latest_complete_turns():
    messages = [
        {"role": "user", "content": "Q1"},
        {"role": "assistant", "content": "A1"},
        {"role": "user", "content": "Q2"},
        {"role": "assistant", "content": "A2"},
        {"role": "user", "content": "Q3"},
        {"role": "assistant", "content": "A3"},
    ]

    result = trim_messages_by_budget(messages, max_chars=8)

    assert result == messages[2:]
    assert len(messages) == 6


def test_build_context_messages_summarizes_omitted_prefix(monkeypatch):
    messages = [
        {"role": "user", "content": "旧问题"},
        {"role": "assistant", "content": "旧答案"},
        {"role": "user", "content": "新问题"},
        {"role": "assistant", "content": "新答案"},
    ]
    calls = []

    def fake_summarize(messages_to_summarize, existing_summary):
        calls.append((messages_to_summarize, existing_summary))
        return "早期对话摘要"

    monkeypatch.setattr(
        main_module, "summarize_messages", fake_summarize, raising=False
    )
    conversation = ConversationState(conversation_id=1, messages=messages)

    result = main_module.build_context_messages(conversation, max_chars=5)

    assert calls == [(messages[:2], "")]
    assert result[0]["role"] == "assistant"
    assert "早期对话摘要" in result[0]["content"]
    assert result[1:] == messages[2:]
    assert conversation.messages == messages
    assert conversation.summary == "早期对话摘要"
    assert conversation.summarized_message_count == 2
