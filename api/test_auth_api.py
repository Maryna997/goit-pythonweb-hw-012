from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from api.instances import auth_service
from main import app
from repositories.user_repository import UserRepository


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture(scope="module")
def mock_user_repository():
    mock_repo = MagicMock(spec=UserRepository)
    return mock_repo


@pytest.fixture(autouse=True)
def patch_user_repository(monkeypatch, mock_user_repository):
    monkeypatch.setattr(auth_service, "user_repository", mock_user_repository)


@pytest.fixture(autouse=True)
def mock_auth_service(monkeypatch):
    async def mock_register_user(user_create):
        return {
            "id": 1,
            "username": user_create.username,
            "email": user_create.email,
            "created_at": "2025-11-19T12:00:00",
            "email_confirmed": False,
            "avatar_url": None,
        }

    def mock_login_user(username, password):
        return {"access_token": "mock_token", "token_type": "bearer"}

    def mock_confirm_email(token):
        return {
            "id": 1,
            "username": "testuser",
            "email": "testuser@example.com",
            "created_at": "2025-11-19T12:00:00",
            "email_confirmed": True,
            "avatar_url": None,
        }

    async def mock_create_password_reset_token(email):
        return "valid-reset-token"

    def mock_reset_password(token, new_password):
        return

    async def mock_send_password_reset_email(email, token):
        pass

    monkeypatch.setattr(auth_service, "register_user", mock_register_user)
    monkeypatch.setattr(auth_service, "login_user", mock_login_user)
    monkeypatch.setattr(auth_service, "confirm_email", mock_confirm_email)
    monkeypatch.setattr(
        auth_service, "create_password_reset_token", mock_create_password_reset_token
    )
    monkeypatch.setattr(auth_service, "reset_password", mock_reset_password)
    monkeypatch.setattr(
        auth_service, "send_password_reset_email", mock_send_password_reset_email
    )


def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "strongpassword",
        },
    )
    assert response.status_code == 201

    data = response.json()
    assert data["id"] == 1
    assert data["username"] == "testuser"
    assert data["email"] == "testuser@example.com"
    assert data["created_at"] == "2025-11-19T12:00:00"
    assert data["email_confirmed"] is False
    assert data["avatar_url"] is None


def test_login_user(client):
    response = client.post(
        "/auth/login",
        data={"username": "testuser@example.com", "password": "strongpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["access_token"] == "mock_token"
    assert data["token_type"] == "bearer"


def test_confirm_email(client):
    response = client.get("/auth/confirm/some-valid-token")
    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["username"] == "testuser"
    assert data["email"] == "testuser@example.com"
    assert data["created_at"] == "2025-11-19T12:00:00"
    assert data["email_confirmed"] is True
    assert data["avatar_url"] is None


def test_password_reset_request(client):
    response = client.post(
        "/auth/password-reset/request",
        json={"email": "testuser@example.com"},
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Password reset email sent."}


def test_password_reset_confirm(client):
    response = client.post(
        "/auth/password-reset/confirm",
        params={"token": "valid-reset-token", "new_password": "newpassword"},
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Password has been reset successfully."}
