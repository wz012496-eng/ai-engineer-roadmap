import pytest

from ai_engineer_roadmap.vector_repository import VectorRecord, VectorRepository


def test_search_without_data_returns_empty_list(tmp_path):
    repository = VectorRepository(tmp_path / "vectors.json")

    results = repository.search([1.0, 0.0])

    assert results == []


@pytest.mark.parametrize("top_k", [0, -1])
def test_search_rejects_invalid_top_k(tmp_path, top_k):
    repository = VectorRepository(tmp_path / "vectors.json")

    with pytest.raises(ValueError, match="top_k 必须大于等于 1"):
        repository.search([1.0, 0.0], top_k=top_k)


def test_records_survive_repository_recreation(tmp_path):
    path = tmp_path / "vectors.json"
    records = [
        VectorRecord("memory-1", "用户有 Android 开发经验", [0.1, 0.2]),
    ]

    repository = VectorRepository(path)
    repository.save(records)

    new_repository = VectorRepository(path)

    assert new_repository.load() == records


@pytest.mark.parametrize(
    "top_k, expected_ids, expected_scores",
    [
        (1, ["C"], [1.0]),
        (2, ["C", "B"], [1.0, 0.8]),
        (5, ["C", "B", "A"], [1.0, 0.8, 0.0]),
    ],
)
def test_search_returns_highest_scores(tmp_path, top_k, expected_ids, expected_scores):
    path = tmp_path / "vectors.json"
    repository = VectorRepository(path)
    repository.save(
        [
            VectorRecord("A", "垂直方向", [0.0, 1.0]),
            VectorRecord("B", "部分接近", [4.0, 3.0]),
            VectorRecord("C", "相同方向", [1.0, 0.0]),
        ]
    )

    new_repository = VectorRepository(path)
    results = new_repository.search([1.0, 0.0], top_k=top_k)

    assert [result.record.record_id for result in results] == expected_ids
    assert [result.score for result in results] == pytest.approx(expected_scores)


def test_search_with_filters_before_top_k(tmp_path):
    path = tmp_path / "vectors.json"
    repository = VectorRepository(path)
    repository.save(
        [
            VectorRecord(
                "A", "美食", [1.0, 0.0], {"category": "food", "source": "note"}
            ),
            VectorRecord(
                "B",
                "Android 笔记",
                [4.0, 3.0],
                {"category": "Android", "source": "note"},
            ),
            VectorRecord(
                "C",
                "Android 文章",
                [9.0, 1.0],
                {"category": "Android", "source": "article"},
            ),
        ]
    )

    results = VectorRepository(path).search(
        [1.0, 0.0], top_k=1, filters={"category": "Android", "source": "note"}
    )

    assert [result.record.record_id for result in results] == ["B"]
    assert results[0].score == pytest.approx(0.8)


def test_load_old_record_without_metadata(tmp_path):
    path = tmp_path / "vectors.json"
    path.write_text(
        '[{"record_id":"old","content":"旧记录","embedding":[1.0,0.0]}]',
        encoding="utf-8",
    )

    repository = VectorRepository(path)
    assert repository.load()[0].metadata == {}
    assert repository.search([1.0, 0.0], filters={"category": "Android"}) == []
