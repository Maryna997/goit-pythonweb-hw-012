"""
User Repository Module

This module contains the User model and UserRepository class for managing users in the database.
"""

import os
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import Column, Integer, String, Date, Boolean, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from schemas.users import UserInDB
from services.auth_service import IUserRepository
from services.user_service import IUserUpdateRepository

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:qwerty@localhost:5432/hw10")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
Base.metadata.create_all(bind=engine)


class User(Base):
    """
    SQLAlchemy model representing a user.

    Attributes:
        id (int): Primary key of the user.
        username (str): Username of the user.
        email (str): Email address of the user.
        hashed_password (str): Hashed password of the user.
        created_at (datetime.date): The date the user was created.
        email_confirmed (bool): Whether the user's email is confirmed.
        avatar_url (str): URL of the user's avatar.
        role (str): Role of the user, e.g., 'user' or 'admin'.
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(Date, default=datetime.utcnow)
    email_confirmed = Column(Boolean, default=False)
    avatar_url = Column(String, nullable=True)
    role = Column(String, default="user")


class UserRepository(IUserRepository, IUserUpdateRepository):
    """
    Repository class for managing users.

    Methods:
        get_by_username(username): Retrieves a user by their username.
        get_by_email(email): Retrieves a user by their email.
        create(user_data): Creates a new user in the database.
        mark_email_confirmed(user_id): Marks a user's email as confirmed.
        get_by_id(user_id): Retrieves a user by their ID.
        update_avatar(user_id, avatar_url): Updates the avatar URL for a user.
        update_password(user_id, hashed_password): Updates the password for a user.
    """

    def __init__(self):
        """
        Initializes the UserRepository with a database session.
        """
        self.db = SessionLocal()

    def get_by_username(self, username: str):
        """
        Retrieves a user by their username.

        Args:
            username (str): The username of the user.

        Returns:
            User: The user object, or None if not found.
        """
        return self.db.query(User).filter(User.username == username).first()

    def get_by_email(self, email: str):
        """
        Retrieves a user by their email address.

        Args:
            email (str): The email address of the user.

        Returns:
            User: The user object, or None if not found.
        """
        return self.db.query(User).filter(User.email == email).first()

    def create(self, user_data: UserInDB):
        """
        Creates a new user in the database.

        Args:
            user_data (UserInDB): The data for the new user.

        Returns:
            User: The created user object.
        """
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=user_data.hashed_password,
            created_at=datetime.utcnow(),
            email_confirmed=False,
            role="user"
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

    def mark_email_confirmed(self, user_id: int):
        """
        Marks a user's email as confirmed.

        Args:
            user_id (int): The ID of the user.
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            user.email_confirmed = True
            self.db.commit()

    def get_by_id(self, user_id: int):
        """
        Retrieves a user by their ID.

        Args:
            user_id (int): The ID of the user.

        Returns:
            User: The user object, or None if not found.
        """
        return self.db.query(User).filter(User.id == user_id).first()

    def update_avatar(self, user_id: int, avatar_url: str):
        """
        Updates the avatar URL for a user.

        Args:
            user_id (int): The ID of the user.
            avatar_url (str): The new avatar URL.

        Returns:
            User: The updated user object, or None if not found.
        """
        user = self.get_by_id(user_id)
        if not user:
            return None

        user.avatar_url = avatar_url
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_password(self, user_id: int, hashed_password: str):
        """
        Updates the password for a user.

        Args:
            user_id (int): The ID of the user.
            hashed_password (str): The new hashed password.

        Raises:
            HTTPException: If the user is not found.

        Returns:
            None
        """
        user = self.get_by_id(user_id)
        if not user:
            raise HTTPException(404, detail="User not found")
        user.hashed_password = hashed_password
        self.db.commit()
        self.db.refresh(user)
