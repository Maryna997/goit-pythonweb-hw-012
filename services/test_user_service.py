from datetime import datetime
from unittest.mock import Mock, MagicMock

import pytest
from fastapi import HTTPException, UploadFile

from schemas.users import UserOut
from services.user_service import UserService


class FakeUser:
    def __init__(
            self,
            id,
            username,
            email,
            created_at,
            email_confirmed,
            avatar_url,
            role,
            password=None,
            hashed_password=None
    ):
        self.id = id
        self.username = username
        self.email = email
        self.created_at = created_at
        self.email_confirmed = email_confirmed
        self.avatar_url = avatar_url
        self.role = role
        self.password = password
        self.hashed_password = hashed_password


@pytest.fixture
def mock_user_repository():
    return Mock()


@pytest.fixture
def mock_image_storage():
    return Mock()


@pytest.fixture
def user_service(mock_user_repository, mock_image_storage):
    return UserService(mock_user_repository, mock_image_storage)


def test_change_avatar_user_not_found(user_service, mock_user_repository):
    mock_user_repository.get_by_id.return_value = None
    mock_file = MagicMock(spec=UploadFile)
    mock_file.file = MagicMock()
    result = user_service.change_avatar(99, mock_file)
    assert result is None


def test_change_avatar_not_admin(user_service, mock_user_repository):
    fake_user = FakeUser(
        id=1,
        username="testuser",
        email="test@user.com",
        created_at=datetime.utcnow(),
        email_confirmed=True,
        avatar_url=None,
        role="user"
    )
    mock_file = MagicMock(spec=UploadFile)
    mock_file.file = MagicMock()
    mock_user_repository.get_by_id.return_value = fake_user
    with pytest.raises(HTTPException) as exc_info:
        user_service.change_avatar(fake_user.id, mock_file)
    assert exc_info.value.status_code == 403


def test_change_avatar_existing_avatar(user_service, mock_user_repository, mock_image_storage):
    fake_user = FakeUser(
        id=1,
        username="adminuser",
        email="admin@user.com",
        created_at=datetime.utcnow(),
        email_confirmed=True,
        avatar_url="https://example.com/images/folder/oldimage.jpg",
        role="admin"
    )
    mock_file = MagicMock(spec=UploadFile)
    mock_file.file = MagicMock()
    mock_user_repository.get_by_id.return_value = fake_user
    mock_image_storage.upload_image.return_value = {"secure_url": "https://example.com/images/folder/newimage.jpg"}
    updated_user = FakeUser(
        id=1,
        username="adminuser",
        email="admin@user.com",
        created_at=datetime.utcnow(),
        email_confirmed=True,
        avatar_url="https://example.com/images/folder/newimage.jpg",
        role="admin"
    )
    mock_user_repository.update_avatar.return_value = updated_user
    result = user_service.change_avatar(fake_user.id, mock_file)
    mock_image_storage.delete_image.assert_called_once_with("folder/oldimage")
    mock_image_storage.upload_image.assert_called_once_with(mock_file.file, options={"folder": "user_avatars"})
    mock_user_repository.update_avatar.assert_called_once_with(
        fake_user.id, "https://example.com/images/folder/newimage.jpg"
    )
    assert isinstance(result, UserOut)
    assert str(result.avatar_url) == "https://example.com/images/folder/newimage.jpg"


def test_change_avatar_no_existing_avatar(user_service, mock_user_repository, mock_image_storage):
    fake_user = FakeUser(
        id=2,
        username="adminuser2",
        email="admin2@user.com",
        created_at=datetime.utcnow(),
        email_confirmed=True,
        avatar_url=None,
        role="admin"
    )
    mock_file = MagicMock(spec=UploadFile)
    mock_file.file = MagicMock()
    mock_user_repository.get_by_id.return_value = fake_user
    mock_image_storage.upload_image.return_value = {"secure_url": "https://example.com/images/folder/newavatar.jpg"}
    updated_user = FakeUser(
        id=2,
        username="adminuser2",
        email="admin2@user.com",
        created_at=datetime.utcnow(),
        email_confirmed=True,
        avatar_url="https://example.com/images/folder/newavatar.jpg",
        role="admin"
    )
    mock_user_repository.update_avatar.return_value = updated_user
    result = user_service.change_avatar(fake_user.id, mock_file)
    mock_image_storage.delete_image.assert_not_called()
    mock_image_storage.upload_image.assert_called_once_with(mock_file.file, options={"folder": "user_avatars"})
    mock_user_repository.update_avatar.assert_called_once_with(
        fake_user.id, "https://example.com/images/folder/newavatar.jpg"
    )
    assert isinstance(result, UserOut)
    assert str(result.avatar_url) == "https://example.com/images/folder/newavatar.jpg"


def test_extract_public_id(user_service):
    url = "https://example.com/images/user_avatars/old_pic.png"
    public_id = user_service._extract_public_id(url)
    assert public_id == "user_avatars/old_pic"
