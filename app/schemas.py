from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, Dict


class CreateUser(BaseModel):
    email: EmailStr
    password: str
    username: str
    profile_picture: Optional[str] = None


class User(BaseModel):
    id: int
    email: str
    username: str
    profile_picture: Optional[str]
    created_at: datetime

    @classmethod
    def from_orm(cls, db_user: Dict):
        return cls(**db_user)

    class Config:
        from_attributes = True


class TokenData(BaseModel):
    id: int
