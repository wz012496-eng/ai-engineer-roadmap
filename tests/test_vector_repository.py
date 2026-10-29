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
