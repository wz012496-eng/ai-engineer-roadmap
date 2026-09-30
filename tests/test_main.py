from ai_engineer_roadmap.main import trim_messages


def test_trim_messages_keeps_latest_complete_turns():
    messages = [
        {"role": "user", "content": "问题 1"},
        {"role": "assistant", "content": "回答 1"},
        {"role": "user", "content": "问题 2"},
        {"role": "assistant", "content": "回答 2"},
        {"role": "user", "content": "问题 3"},
        {"role": "assistant", "content": "回答 3"},
        {"role": "user", "content": "问题 4"},
        {"role": "assistant", "content": "回答 4"},
    ]

    result = trim_messages(messages, max_length=3)

    assert result == messages[2:]
    assert len(messages) == 8


def test_trim_messages_returns_copy_when_under_limit():
    messages = [
        {"role": "user", "content": "问题 1"},
        {"role": "assistant", "content": "回答 1"},
    ]

    result = trim_messages(messages, max_length=3)

    assert result == messages
    assert result is not messages
