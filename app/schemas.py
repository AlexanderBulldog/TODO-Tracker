from datetime import datetime

from pydantic import BaseModel


class TaskBase(BaseModel):
    title: str
    description: str | None = None
    due_date: datetime | None = None


class TaskCreate(TaskBase):
    pass


class Task(TaskBase):
    id: int
    is_done: bool


class Config:
    from_attributes = True


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    is_done: bool | None = None
    due_date: datetime | None = None
