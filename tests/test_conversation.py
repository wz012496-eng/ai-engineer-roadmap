from ai_engineer_roadmap.conversation import ConversationStore


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
