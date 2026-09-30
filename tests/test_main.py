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
