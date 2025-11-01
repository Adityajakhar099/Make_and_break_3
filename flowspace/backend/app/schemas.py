from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    sub: Optional[str] = None

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    board_id: Optional[int] = None
    status: Optional[str] = "todo"
    priority: Optional[str] = "medium"

class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    priority: str
    board_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
