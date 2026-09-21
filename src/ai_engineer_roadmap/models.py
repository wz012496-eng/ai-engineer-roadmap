from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel, Field


class Priority(str, Enum):
    LOW = "low"
    HIGH = "high"


@dataclass
class Task:
    id: int
    title: str
    priority: Priority
    completed: bool = False


class TaskSuggestion(BaseModel):
    summary: str = Field(description="对任务的一句话分析总结")
    steps: list[str] = Field(
        min_length=3, max_length=3, description="三个具体、可执行的任务步骤"
    )
