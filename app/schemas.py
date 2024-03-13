from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class CreateUser(BaseModel):
    email: EmailStr
    password: str
    username: str
    profile_picture: Optional[str] = None


class User(BaseModel):
    id: int
    email: str
    password: str
    username: str
    profile_picture: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
