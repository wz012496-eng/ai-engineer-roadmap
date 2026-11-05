import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from ai_engineer_roadmap.similarity import cosine_similarity


@dataclass
class VectorRecord:
    record_id: str
    content: str
    embedding: list[float]
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass
class SearchResult:
    record: VectorRecord
    score: float


class VectorRepository:
    def __init__(self, data_file: Path) -> None:
        self.data_file = data_file

    def save(self, records: list[VectorRecord]) -> None:
        data = [asdict(record) for record in records]

        with self.data_file.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

    def load(self) -> list[VectorRecord]:
        if not self.data_file.exists():
            return []

        with self.data_file.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return [VectorRecord(**item) for item in data]

    def search(
        self,
        query_vector: list[float],
        top_k: int = 3,
        filters: dict[str, str] | None = None,
    ) -> list[SearchResult]:
        if top_k < 1:
            raise ValueError("top_k 必须大于等于 1")

        records = self.load()
        results = []

        for record in records:
            if filters and any(
                record.metadata.get(key) != value for key, value in filters.items()
            ):
                continue
            score = cosine_similarity(query_vector, record.embedding)
            results.append(SearchResult(record, score))

        results.sort(key=lambda result: result.score, reverse=True)

        return results[:top_k]
