from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, HttpUrl


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime
    email_confirmed: bool
    avatar_url: Optional[HttpUrl]

    class Config:
        orm_mode = True
        from_attributes = True


class UserInDB(UserCreate):
    hashed_password: str
