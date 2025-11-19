from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import HTTPException
from jose import jwt

from schemas.auth import Token
from schemas.users import UserCreate, UserOut
from services.auth_service import AuthService

TEST_SECRET_KEY = "testsecret"
TEST_ALGORITHM = "HS256"
TEST_ACCESS_TOKEN_EXPIRE_MINUTES = 30
TEST_CONFIRMATION_TOKEN_EXPIRE_HOURS = 24
TEST_PASSWORD_RESET_TOKEN_EXPIRE_HOURS = 1
TEST_DOMAIN_NAME = "testdomain.com"


class FakeUser:
    def __init__(
            self,
            id,
            username,
            email,
            created_at,
            email_confirmed,
            avatar_url,
            password,
            hashed_password
    ):
        self.id = id
        self.username = username
        self.email = email
        self.created_at = created_at
        self.email_confirmed = email_confirmed
        self.avatar_url = avatar_url
        self.password = password
        self.hashed_password = hashed_password


@pytest.fixture(autouse=True)
def patch_auth_service_constants():
    with patch("services.auth_service.SECRET_KEY", TEST_SECRET_KEY), \
            patch("services.auth_service.ALGORITHM", TEST_ALGORITHM), \
            patch("services.auth_service.ACCESS_TOKEN_EXPIRE_MINUTES", TEST_ACCESS_TOKEN_EXPIRE_MINUTES), \
            patch("services.auth_service.CONFIRMATION_TOKEN_EXPIRE_HOURS", TEST_CONFIRMATION_TOKEN_EXPIRE_HOURS), \
            patch("services.auth_service.PASSWORD_RESET_TOKEN_EXPIRE_HOURS", TEST_PASSWORD_RESET_TOKEN_EXPIRE_HOURS), \
            patch("services.auth_service.DOMAIN_NAME", TEST_DOMAIN_NAME):
        yield


@pytest.fixture
def mock_user_repository():
    return Mock()


@pytest.fixture
def mock_email_sender():
    return AsyncMock()


@pytest.fixture
def mock_cache():
    return AsyncMock()


@pytest.fixture
def auth_service(mock_user_repository, mock_email_sender, mock_cache):
    return AuthService(mock_user_repository, mock_email_sender, mock_cache)


def test_hash_password(auth_service):
    password = "testpass"
    hashed = auth_service.hash_password(password)
    assert hashed != password
    assert isinstance(hashed, str)


def test_verify_password(auth_service):
    password = "testpass"
    hashed = auth_service.hash_password(password)
    assert auth_service.verify_password(password, hashed) is True
    assert auth_service.verify_password("wrongpass", hashed) is False


def test_authenticate_user(auth_service, mock_user_repository):
    fake_user = FakeUser(
        1,
        "user1",
        "user1@test.com",
        datetime.utcnow(),
        False,
        None,
        "testpass",
        auth_service.hash_password("testpass")
    )
    mock_user_repository.get_by_username.return_value = fake_user
    result = auth_service.authenticate_user("user1", "testpass")
    assert result is not None
    assert result.username == "user1"
    mock_user_repository.get_by_username.assert_called_once_with("user1")


def test_create_access_token(auth_service):
    data = {"sub": "user1"}
    token = auth_service.create_access_token(data)
    decoded = jwt.decode(token, TEST_SECRET_KEY, algorithms=[TEST_ALGORITHM])
    assert decoded["sub"] == "user1"
    assert "exp" in decoded


def test_create_confirmation_token(auth_service):
    email = "user1@test.com"
    token = auth_service.create_confirmation_token(email)
    decoded = jwt.decode(token, TEST_SECRET_KEY, algorithms=[TEST_ALGORITHM])
    assert decoded["sub"] == email
    assert "exp" in decoded


def test_confirm_email(auth_service, mock_user_repository):
    fake_user = FakeUser(
        1,
        "user1",
        "user1@test.com",
        datetime.utcnow(),
        False,
        None,
        "pass",
        "hashed"
    )
    mock_user_repository.get_by_email.return_value = fake_user
    token = auth_service.create_confirmation_token(fake_user.email)
    result = auth_service.confirm_email(token)
    assert result.email == fake_user.email
    mock_user_repository.get_by_email.assert_called_once()
    mock_user_repository.mark_email_confirmed.assert_called_once()


@pytest.mark.asyncio
async def test_send_confirmation_email(auth_service, mock_email_sender):
    fake_user = FakeUser(
        1,
        "user1",
        "user1@test.com",
        datetime.utcnow(),
        False,
        None,
        "pass",
        "hashed"
    )
    token = "testtoken"
    user_out = UserOut.from_orm(fake_user)
    await auth_service.send_confirmation_email(user_out, token)
    mock_email_sender.send_email.assert_awaited_once()


@pytest.mark.asyncio
async def test_register_user(auth_service, mock_user_repository, mock_email_sender):
    mock_user_repository.get_by_email.return_value = None
    user_create = UserCreate(username="user1", email="user1@test.com", password="pass")
    fake_user = FakeUser(
        1,
        user_create.username,
        user_create.email,
        datetime.utcnow(),
        False,
        None,
        user_create.password,
        "hashed"
    )
    mock_user_repository.create.return_value = fake_user
    result = await auth_service.register_user(user_create)
    assert result.email == user_create.email
    mock_user_repository.get_by_email.assert_called_with(user_create.email)
    mock_user_repository.create.assert_called_once()
    mock_email_sender.send_email.assert_awaited_once()


def test_login_user(auth_service, mock_user_repository):
    fake_user = FakeUser(
        1,
        "user1",
        "user1@test.com",
        datetime.utcnow(),
        False,
        None,
        "pass",
        auth_service.hash_password("pass")
    )
    mock_user_repository.get_by_username.return_value = fake_user
    token_data = auth_service.login_user("user1", "pass")
    assert isinstance(token_data, Token)
    with pytest.raises(HTTPException):
        auth_service.login_user("user1", "wrongpass")


@pytest.mark.asyncio
async def test_get_current_user(auth_service, mock_user_repository, mock_cache):
    username = "user1"
    fake_user = FakeUser(
        1,
        username,
        "user1@test.com",
        datetime.utcnow(),
        False,
        None,
        "pass",
        "hashed"
    )
    mock_user_repository.get_by_username.return_value = fake_user
    mock_cache.get.return_value = None
    token = auth_service.create_access_token({"sub": username})
    result = await auth_service.get_current_user(token)
    assert result.username == username
    assert result.email == "user1@test.com"
    mock_cache.set.assert_awaited()


def test_create_password_reset_token(auth_service, mock_user_repository):
    fake_user = FakeUser(
        1,
        "user1",
        "user1@test.com",
        datetime.utcnow(),
        False,
        None,
        "pass",
        "hashed"
    )
    mock_user_repository.get_by_email.return_value = fake_user
    token = auth_service.create_password_reset_token("user1@test.com")
    decoded = jwt.decode(token, TEST_SECRET_KEY, algorithms=[TEST_ALGORITHM])
    assert decoded["sub"] == "user1@test.com"


def test_reset_password(auth_service, mock_user_repository):
    fake_user = FakeUser(
        1,
        "user1",
        "user1@test.com",
        datetime.utcnow(),
        False,
        None,
        "pass",
        "hashed"
    )
    mock_user_repository.get_by_email.return_value = fake_user
    token = auth_service.create_password_reset_token("user1@test.com")
    auth_service.reset_password(token, "newpass")
    mock_user_repository.update_password.assert_called_once()


@pytest.mark.asyncio
async def test_send_password_reset_email(auth_service, mock_email_sender):
    await auth_service.send_password_reset_email("user1@test.com", "resettoken")
    mock_email_sender.send_email.assert_awaited_once()
