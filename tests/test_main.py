from importlib import import_module

import pytest

from ai_engineer_roadmap.memory import MemoryItem

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


def test_build_memory_context_raises_for_negative_budget():
    with pytest.raises(ValueError, match="max_chars 不能小于 0"):
        main_module.build_memory_context([], max_chars=-1)


def test_build_memory_context_empty():
    assert main_module.build_memory_context([], max_chars=5) == ""


def test_build_memory_context_trims_to_budget():
    memory_items = [
        MemoryItem(content="记忆1", memory_id=1),
        MemoryItem(content="记忆2", memory_id=2),
        MemoryItem(content="记忆3", memory_id=3),
    ]

    result = main_module.build_memory_context(memory_items, max_chars=5)

    assert "记忆3" in result
    assert "记忆2" not in result
    assert "记忆1" not in result
    assert result == "- 记忆3"


def test_build_memory_context_returns_empty_when_budget_is_zero():
    items = [MemoryItem(content="记忆", memory_id=1)]
    assert main_module.build_memory_context(items, max_chars=0) == ""


def test_build_memory_context_skips_oversized_item_and_keeps_shorter_one():
    items = [
        MemoryItem(content="短", memory_id=1),
        MemoryItem(content="这条记忆很长", memory_id=2),
    ]
    result = main_module.build_memory_context(items, max_chars=len("- 短"))
    assert result == "- 短"


def test_build_memory_context_preserves_order_when_items_fit():
    items = [
        MemoryItem(content="甲", memory_id=1),
        MemoryItem(content="乙", memory_id=2),
    ]
    expected = "- 甲\n- 乙"
    assert main_module.build_memory_context(items, max_chars=len(expected)) == expected
