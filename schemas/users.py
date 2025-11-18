"""
User Schemas

This module defines the Pydantic models for user-related data structures.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, HttpUrl


class UserCreate(BaseModel):
    """
    Model for creating a new user.

    Attributes:
        username (str): The user's username.
        email (EmailStr): The user's email address.
        password (str): The user's password.
    """
    username: str
    email: EmailStr
    password: str


class UserOut(BaseModel):
    """
    Model for representing a user in responses.

    Attributes:
        id (int): The unique identifier of the user.
        username (str): The user's username.
        email (EmailStr): The user's email address.
        created_at (datetime): The datetime when the user was created.
        email_confirmed (bool): Whether the user's email has been confirmed.
        avatar_url (Optional[HttpUrl]): The URL to the user's avatar, if available.
    """
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
    """
    Model for representing a user in the database.

    Inherits all attributes from UserCreate.

    Attributes:
        hashed_password (str): The hashed password of the user.
    """
    hashed_password: str
