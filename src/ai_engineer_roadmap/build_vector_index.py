from pathlib import Path

from sentence_transformers import SentenceTransformer

from ai_engineer_roadmap.vector_repository import VectorRecord, VectorRepository

documents = [
    {
        "record_id": "memory-1",
        "content": "用户有 Android 开发经验",
        "metadata": {"category": "background"},
    },
    {
        "record_id": "memory-2",
        "content": "用户喜欢吃火锅",
        "metadata": {"category": "preference"},
    },
]


if __name__ == "__main__":
    model = SentenceTransformer(
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", device="cpu"
    )

    texts = [document["content"] for document in documents]
    embeddings = model.encode(texts).tolist()

    print("资料向量：", len(documents))
    print("向量数量：", len(embeddings))
    print("第一条向量维度：", len(embeddings[0]))

    records = [
        VectorRecord(
            record_id=document["record_id"],
            content=document["content"],
            embedding=embedding,
            metadata=document["metadata"],
        )
        for document, embedding in zip(documents, embeddings, strict=True)
    ]

    data_file = Path("vectors.json")
    repository = VectorRepository(data_file)
    repository.save(records)

    loaded_records = VectorRepository(data_file).load()
    assert loaded_records == records

    print("保存后重新加载的记录数：", len(loaded_records))
    print("资料 ID：", [record.record_id for record in loaded_records])

    query = "我的开发背景和饮食偏好分别是什么？"
    query_vector = model.encode([query]).tolist()[0]

    results = VectorRepository(data_file).search(
        query_vector,
        top_k=2,
        filters={"category": "background"},
    )

    retrieved_ids = [result.record.record_id for result in results]
    assert retrieved_ids == ["memory-1"]

    print("限定 background 类别的检索结果：", retrieved_ids)
