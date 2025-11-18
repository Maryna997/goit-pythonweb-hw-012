import os
from datetime import datetime

from sqlalchemy import Column, Integer, String, Date, Boolean, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from schemas.users import UserInDB
from services.auth_service import IUserRepository
from services.user_service import IUserUpdateRepository

DATABASE_URL = os.environ.get("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
Base.metadata.create_all(bind=engine)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(Date, default=datetime.utcnow)
    email_confirmed = Column(Boolean, default=False)
    avatar_url = Column(String, nullable=True)


class UserRepository(IUserRepository, IUserUpdateRepository):
    def __init__(self):
        self.db = SessionLocal()

    def get_by_username(self, username: str):
        return self.db.query(User).filter(User.username == username).first()

    def get_by_email(self, email: str):
        return self.db.query(User).filter(User.email == email).first()

    def create(self, user_data: UserInDB):
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=user_data.hashed_password,
            created_at=datetime.utcnow(),
            email_confirmed=False
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

    def mark_email_confirmed(self, user_id: int):
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            user.email_confirmed = True
            self.db.commit()

    def get_by_id(self, user_id: int):
        return self.db.query(User).filter(User.id == user_id).first()

    def update_avatar(self, user_id: int, avatar_url: str):
        user = self.get_by_id(user_id)
        if not user:
            return None

        user.avatar_url = avatar_url
        self.db.commit()
        self.db.refresh(user)
        return user
