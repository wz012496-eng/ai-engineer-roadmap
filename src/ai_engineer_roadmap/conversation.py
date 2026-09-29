from dataclasses import dataclass, field


@dataclass
class ConversationState:
    conversation_id: int
    messages: list[dict] = field(default_factory=list)


class ConversationStore:
    def __init__(self):
        self._conversations: dict[int, ConversationState] = {}

    def get_or_create(self, conversation_id: int) -> ConversationState:
        if conversation_id not in self._conversations:
            self._conversations[conversation_id] = ConversationState(
                conversation_id=conversation_id
            )
        return self._conversations[conversation_id]
