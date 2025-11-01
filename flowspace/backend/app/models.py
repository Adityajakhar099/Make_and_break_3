from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
import enum

class Priority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    full_name: Optional[str] = None
    hashed_password: str

class Board(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    status: str = Field(default="todo", index=True)
    priority: Priority = Field(default=Priority.medium)
    board_id: Optional[int] = Field(default=None, foreign_key="board.id")
    assignee_id: Optional[int] = Field(default=None, foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
