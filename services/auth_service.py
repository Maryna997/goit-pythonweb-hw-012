import os
from abc import abstractmethod, ABC
from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from schemas.auth import Token
from schemas.users import UserCreate, UserOut, UserInDB

SECRET_KEY = os.environ.get("AUTH_SECRET_KEY")
ALGORITHM = os.environ.get("AUTH_JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("AUTH_ACCESS_TOKEN_EXPIRE_MINUTES", 30))
CONFIRMATION_TOKEN_EXPIRE_HOURS = int(os.environ.get("AUTH_CONFIRMATION_TOKEN_EXPIRE_HOURS", 24))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


class IUserRepository(ABC):
    @abstractmethod
    def get_by_username(self, username: str):
        pass

    @abstractmethod
    def get_by_email(self, email: str):
        pass

    @abstractmethod
    def create(self, user_data: dict):
        pass

    @abstractmethod
    def mark_email_confirmed(self, user_id: int):
        pass


class IEmailSender(ABC):
    @abstractmethod
    def send_email(self, subject: str, recipients: List, body: str):
        pass


class AuthService:
    def __init__(self, user_repository: IUserRepository, email_sender: IEmailSender):
        self.user_repository = user_repository
        self.email_client = email_sender

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def authenticate_user(self, username: str, password: str) -> Optional[UserOut]:
        user = self.user_repository.get_by_username(username)
        if user and self.verify_password(password, user.hashed_password):
            return user
        return None

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    def create_confirmation_token(self, email: str) -> str:
        expire = datetime.utcnow() + timedelta(hours=CONFIRMATION_TOKEN_EXPIRE_HOURS)
        to_encode = {"sub": email, "exp": expire}
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    def confirm_email(self, token: str) -> UserOut:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
            user = self.user_repository.get_by_email(email)
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            self.user_repository.mark_email_confirmed(user.id)
            return UserOut.from_orm(user)
        except JWTError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")

    async def send_confirmation_email(self, user: UserOut, token: str):
        subject = "Confirm your email"
        confirmation_url = f"https://your-domain.com/auth/confirm/{token}"
        body = f"""
        Hello {user.username},

        Please confirm your email by clicking the link below:
        {confirmation_url}
        """
        await self.email_client.send_email(subject, [user.email], body)

    async def register_user(self, user: UserCreate) -> UserOut:
        if self.user_repository.get_by_email(user.email):
            raise HTTPException(status_code=409, detail="Email already registered")

        hashed_password = self.hash_password(user.password)
        user_in_db = UserInDB(
            username=user.username,
            email=user.email,
            password=user.password,
            hashed_password=hashed_password
        )

        new_user = self.user_repository.create(user_in_db)

        confirmation_token = self.create_confirmation_token(new_user.email)
        await self.send_confirmation_email(UserOut.from_orm(new_user), confirmation_token)
        return UserOut.from_orm(new_user)

    def login_user(self, username: str, password: str) -> Token:
        user = self.authenticate_user(username, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token = self.create_access_token(data={"sub": user.username})
        return Token(access_token=access_token, token_type="bearer")

    def get_current_user(self, token: str = Depends(oauth2_scheme)):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        user = self.user_repository.get_by_username(username)
        if user is None:
            raise credentials_exception
        return user
