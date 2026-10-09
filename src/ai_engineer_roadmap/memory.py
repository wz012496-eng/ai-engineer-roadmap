import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class MemoryItem:
    memory_id: int
    content: str
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "memory_id": self.memory_id,
            "content": self.content,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MemoryItem":
        return cls(
            memory_id=data.get("memory_id", 0),
            content=data.get("content", ""),
            tags=data.get("tags", []),
        )


class MemoryStore:
    def __init__(self, items: list[MemoryItem] | None = None):
        self.memory_items: list[MemoryItem] = items if items is not None else []

    def add(self, content: str, tags: list[str] | None = None) -> MemoryItem:
        normalized_content = content.strip()
        normalized_tags = [tag.strip() for tag in (tags or []) if tag.strip()]

        for item in self.memory_items:
            if item.content.strip().casefold() != normalized_content.casefold():
                continue

            existing_tags = {tag.strip().casefold() for tag in item.tags}
            for tag in normalized_tags:
                if tag.casefold() not in existing_tags:
                    item.tags.append(tag)
                    existing_tags.add(tag.casefold())

            return item

        memory_id = max((item.memory_id for item in self.memory_items), default=0) + 1
        memory_item = MemoryItem(
            memory_id=memory_id,
            content=normalized_content,
            tags=normalized_tags,
        )
        self.memory_items.append(memory_item)
        return memory_item

    def to_dict(self) -> list[dict]:
        return [item.to_dict() for item in self.memory_items]

    @classmethod
    def from_dict(cls, data: list[dict]) -> "MemoryStore":
        items = [MemoryItem.from_dict(item) for item in data]
        return cls(items=items)

    def save_to_file(self, file_path: str | Path) -> None:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load_from_file(cls, file_path: str | Path) -> "MemoryStore":
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def find_relevant(self, query: str) -> list[MemoryItem]:
        normalized_query = query.casefold().strip()
        if not normalized_query:
            return []
        return [
            item
            for item in self.memory_items
            if any(
                tag.strip() and tag.strip().casefold() in normalized_query
                for tag in item.tags
            )
        ]
