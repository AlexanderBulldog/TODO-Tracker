from sqlalchemy import Boolean, Column, DateTime, Integer, String

from .database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    is_done = Column(Boolean, default=False)
    # ИСПРАВЛЕНО: Добавляем timezone=True
    due_date = Column(DateTime(timezone=True), nullable=True)
