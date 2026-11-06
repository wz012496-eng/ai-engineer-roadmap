import pytest

from ai_engineer_roadmap.retrieval_evaluation import recall_at_k


@pytest.mark.parametrize(
    "retrieved_ids, expected_ids, k, expected_score",
    [
        (["A"], ["A"], 1, 1.0),
        (["A"], ["A", "B"], 1, 0.5),
        (["B", "A"], ["A"], 1, 0.0),
        (["A", "A"], ["A", "B"], 2, 0.5),
        ([], ["A"], 1, 0.0),
        (["A"], ["A"], 3, 1.0),
    ],
)
def test_recall_k(
    retrieved_ids,
    expected_ids,
    k,
    expected_score,
):
    result = recall_at_k(retrieved_ids, expected_ids, k)
    assert result == expected_score


def test_recall_at_k_rejects_empty_expected_ids():
    with pytest.raises(ValueError, match="expected_ids 不能为空"):
        recall_at_k(["A"], [], 1)


@pytest.mark.parametrize("k", [0, -1])
def test_recall_at_k_rejects_invalid_k(k):
    with pytest.raises(ValueError, match="k 必须大于等于 1"):
        recall_at_k(["A"], ["A"], k)
