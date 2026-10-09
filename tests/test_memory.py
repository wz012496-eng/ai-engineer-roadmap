from ai_engineer_roadmap.memory import MemoryStore


def test_memory_store_saves_and_loads_items(tmp_path):
    file_path = tmp_path / "memories.json"
    store = MemoryStore()
    store.add("我喜欢中文分步骤讲解", tags=["偏好", "中文"])

    store.save_to_file(file_path)
    loaded_store = MemoryStore.load_from_file(file_path)
    assert loaded_store.to_dict() == [
        {
            "memory_id": 1,
            "content": "我喜欢中文分步骤讲解",
            "tags": ["偏好", "中文"],
        }
    ]
    next_item = loaded_store.add("我正在开发 AI Agent", tags=["项目"])
    assert next_item.memory_id == 2


def test_find_relevant_matches_tags_in_query():
    store = MemoryStore()
    saved_item = store.add("我喜欢中文分步骤讲解", tags=["偏好", "中文"])
    store.add("我正在开发 AI Agent", tags=["项目"])

    assert store.find_relevant("请用中文回答") == [saved_item]

    assert store.find_relevant("今天天气怎么样") == []

    assert store.find_relevant("") == []


def test_add_deduplicates_same_content_and_merges_tags():
    store = MemoryStore()
    original = store.add("我喜欢中文分步骤讲解", tags=["偏好", "中文"])

    duplicate = store.add(" 我喜欢中文分步骤讲解 ", tags=["中文", "学习"])

    assert duplicate.memory_id == original.memory_id
    assert len(store.memory_items) == 1
    assert original.tags == ["偏好", "中文", "学习"]
