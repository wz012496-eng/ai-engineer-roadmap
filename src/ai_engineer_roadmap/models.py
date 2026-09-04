from dataclasses import dataclass
from enum import Enum


class Priority(str, Enum):
    LOW = "low"
    HIGH = "high"


@dataclass
class Task:
    id: int
    title: str
    priority: Priority
    completed: bool = False
