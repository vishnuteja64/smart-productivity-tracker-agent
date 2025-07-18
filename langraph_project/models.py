from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class Task(BaseModel):
    title: str
    priority: str
    hours: float
    date: date
    status: str = "Not Completed"
    comment: Optional[str] = None
    completion_comment: Optional[str] = None

class TrackerState(BaseModel):
    task_list: List[Task] = Field(default_factory=list)
    suggestions: Optional[str] = None
    summary: Optional[str] = None
    history: Optional[str] = ""
