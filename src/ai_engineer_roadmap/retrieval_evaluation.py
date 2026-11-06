def recall_at_k(retrieved_ids: list[str], expected_ids: list[str], k: int) -> float:
    if k < 1:
        raise ValueError("k 必须大于等于 1")
    if not expected_ids:
        raise ValueError("expected_ids 不能为空")

    retrieved_set = set(retrieved_ids[:k])
    expected_set = set(expected_ids)
    return len(retrieved_set & expected_set) / len(expected_set)


if __name__ == "__main__":
    from pathlib import Path

    from sentence_transformers import SentenceTransformer

    from ai_engineer_roadmap.vector_repository import VectorRepository

    evaluation_cases = [
        {
            "query": "如何利用我的安卓开发背景学习 AI？",
            "expected_ids": ["memory-1"],
        },
        {
            "query": "我有什么饮食偏好？",
            "expected_ids": ["memory-2"],
        },
        {
            "query": "我的开发背景和饮食偏好分别是什么？",
            "expected_ids": ["memory-1", "memory-2"],
        },
    ]

    model = SentenceTransformer(
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", device="cpu"
    )
    repository = VectorRepository(Path("vectors.json"))
    top_k = 1

    queries = [case["query"] for case in evaluation_cases]
    query_vectors = model.encode(queries).tolist()

    recall_scores = []

    for case, query_vector in zip(
        evaluation_cases,
        query_vectors,
        strict=True,
    ):
        results = repository.search(query_vector, top_k=top_k)
        retrieved_ids = [result.record.record_id for result in results]
        score = recall_at_k(retrieved_ids, case["expected_ids"], top_k)
        recall_scores.append(score)

        print(f"问题：{case['query']}")
        print(f"预期：{case['expected_ids']}")
        print(f"实际：{retrieved_ids}")
        print(f"Recall@{top_k}：{score:.2%}")
        print()
    average_recall = sum(recall_scores) / len(recall_scores)
    print(f"平均 Recall@{top_k}：{average_recall:.2%}")
