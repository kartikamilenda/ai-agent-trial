from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, field_validator

class ActionItem(BaseModel):
    title: str = Field(min_length=3)
    assignee: Optional[str] = None
    deadline: Optional[date] = None
    source_excerpt: str = ''

    @field_validator('assignee', mode='before')
    @classmethod
    def normalize_assignee(cls, value):
        if not value or str(value).strip().lower() in ('unknown', 'null', 'none', '-', 'tidak diketahui'):
            return None
        return str(value).strip()

    @property
    def missing(self):
        return [key for key, value in [('PIC', self.assignee), ('deadline', self.deadline)] if not value]

class MeetingAnalysis(BaseModel):
    action_items: list[ActionItem] = Field(default_factory=list)

class TaskOperation(BaseModel):
    operation: str
    task_id: Optional[int] = None
    status: Optional[str] = None
