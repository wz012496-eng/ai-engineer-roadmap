import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ConversationState:
    conversation_id: int
    messages: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {"conversation_id": self.conversation_id, "messages": self.messages}


class ConversationStore:
    def __init__(self):
        self._conversations: dict[int, ConversationState] = {}

    def get_or_create(self, conversation_id: int) -> ConversationState:
        if conversation_id not in self._conversations:
            self._conversations[conversation_id] = ConversationState(
                conversation_id=conversation_id
            )
        return self._conversations[conversation_id]

    def to_dict(self) -> list[dict[str, object]]:
        return [conversation.to_dict() for conversation in self._conversations.values()]

    @classmethod
    def from_dict(cls, data: list[dict]) -> "ConversationStore":
        store = cls()

        for item in data:
            conversation_id = item["conversation_id"]
            messages = item["messages"]
            store._conversations[conversation_id] = ConversationState(
                conversation_id=conversation_id,
                messages=messages,
            )
        return store

    def save(self, file_path: Path) -> None:
        with file_path.open("w", encoding="utf-8") as file:
            json.dump(self.to_dict(), file, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, file_path: Path) -> "ConversationStore":
        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return cls.from_dict(data)
