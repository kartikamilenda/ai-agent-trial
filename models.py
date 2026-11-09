from datetime import date
from typing import Optional, Literal
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


TaskStatus = Literal[
    "pending",
    "in_progress",
    "completed"
]

class ExtractedActionItem(BaseModel):
    title: str = Field(min_length=3)
    assignee: str | None = Field(...)
    deadline: str | None = Field(...)
    source_excerpt: str = Field(...)


class MeetingExtraction(BaseModel):
    action_items: list[ExtractedActionItem]

class ActionItem(BaseModel):
    item_id: str = Field(
        default_factory=lambda: str(uuid4())
    )
    title: str = Field(min_length=3)
    assignee: Optional[str] = None
    deadline: Optional[date] = None
    source_excerpt: str = ""

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value):
        value = value.strip()
        if len(value) < 3:
            raise ValueError("Title must contain at least 3 characters")
        return value

    @field_validator("assignee", mode="before")
    @classmethod
    def normalize_assignee(cls, value):
        if value is None:
            return None

        value = str(value).strip()

        if value.lower() in (
            "", "unknown", "null", "none",
            "-", "tidak diketahui"
        ):
            return None

        return value

    @property
    def missing(self) -> list[str]:
        missing = []

        if not self.assignee:
            missing.append("PIC")

        if self.deadline is None:
            missing.append("deadline")

        return missing


class MeetingAnalysis(BaseModel):
    action_items: list[ActionItem] = Field(
        default_factory=list
    )


class TaskOperation(BaseModel):
    operation: Literal[
        "list_tasks",
        "update_task_status",
        "check_overdue",
        "task_summary"
    ]
    task_id: Optional[int] = Field(
        default=None,
        gt=0
    )
    status: Optional[TaskStatus] = None
