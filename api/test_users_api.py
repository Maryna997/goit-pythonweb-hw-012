from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from api.instances import auth_service, user_service
from main import app
from schemas.users import UserOut


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture
def test_user_data():
    return UserOut(
        id=1,
        username="adminUser",
        email="admin@example.com",
        created_at=datetime(2025, 11, 19, 12, 0, 0),
        email_confirmed=True,
        avatar_url=None,
    )


@pytest.fixture
def override_deps(test_user_data):
    async def mock_get_current_user(token: str = None):
        return test_user_data

    def mock_change_avatar(user_id, file):
        test_user_data.avatar_url = "http://example.com/path/to/new-avatar.jpg"
        return test_user_data

    app.dependency_overrides[auth_service.get_current_user] = mock_get_current_user

    original_change_avatar = user_service.change_avatar
    user_service.change_avatar = mock_change_avatar

    yield

    app.dependency_overrides = {}
    user_service.change_avatar = original_change_avatar


def test_get_current_user_info(client, override_deps, test_user_data):
    response = client.get(
        "/users/me",
        headers={"Authorization": "Bearer mock_token"},
    )
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    data = response.json()

    assert data["id"] == test_user_data.id
    assert data["username"] == test_user_data.username
    assert data["email"] == test_user_data.email
    assert data["created_at"] == test_user_data.created_at.isoformat()
    assert data["email_confirmed"] == test_user_data.email_confirmed
    assert data["avatar_url"] == test_user_data.avatar_url


def test_change_avatar(client, override_deps, test_user_data):
    file_content = b"fake-image-bytes"
    files = {
        "file": ("test.png", file_content, "image/png"),
    }

    response = client.post(
        "/users/me/avatar",
        files=files,
        headers={"Authorization": "Bearer mock_token"},
    )
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    data = response.json()
    assert data["id"] == test_user_data.id
    assert data["username"] == test_user_data.username
    assert data["email"] == test_user_data.email
    assert data["created_at"] == test_user_data.created_at.isoformat()
    assert data["email_confirmed"] == test_user_data.email_confirmed
    assert data["avatar_url"] == "http://example.com/path/to/new-avatar.jpg"
