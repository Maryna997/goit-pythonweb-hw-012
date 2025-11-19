import pytest
from unittest.mock import MagicMock
from datetime import datetime

from repositories.user_repository import UserRepository, User
from schemas.users import UserInDB


@pytest.fixture
def mock_db_session(mocker):
    return mocker.MagicMock()


@pytest.fixture
def user_repository(mock_db_session):
    repo = UserRepository()
    repo.db = mock_db_session
    return repo


def test_get_by_username(user_repository, mock_db_session):
    mock_user = MagicMock(
        id=1,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_pass",
        created_at=datetime(2023, 1, 1),
        email_confirmed=False,
        avatar_url=None,
        role="user",
    )
    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        mock_user
    )

    user = user_repository.get_by_username("testuser")
    assert user == mock_user
    mock_db_session.query.assert_called_once_with(User)
    mock_db_session.query.return_value.filter.assert_called_once()


def test_get_by_email(user_repository, mock_db_session):
    mock_user = MagicMock(
        id=2,
        username="anotheruser",
        email="another@example.com",
        hashed_password="hashed_pass2",
        created_at=datetime(2023, 2, 1),
        email_confirmed=False,
        avatar_url=None,
        role="user",
    )
    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        mock_user
    )

    user = user_repository.get_by_email("another@example.com")
    assert user == mock_user
    mock_db_session.query.assert_called_once_with(User)
    mock_db_session.query.return_value.filter.assert_called_once()


def test_create(user_repository, mock_db_session):
    user_data = UserInDB(
        username="newuser",
        email="newuser@example.com",
        password="plaintext_pass",
        hashed_password="hashed_pass",
    )

    mock_db_session.add.return_value = None
    mock_db_session.commit.return_value = None
    mock_db_session.refresh.return_value = None

    new_user = user_repository.create(user_data)

    mock_db_session.add.assert_called_once()
    added_user = mock_db_session.add.call_args[0][0]
    assert added_user.username == "newuser"
    assert added_user.email == "newuser@example.com"
    assert added_user.hashed_password == "hashed_pass"

    mock_db_session.commit.assert_called_once()

    mock_db_session.refresh.assert_called_once_with(added_user)

    assert new_user is added_user
    assert new_user.role == "user"
    assert new_user.email_confirmed is False


def test_mark_email_confirmed(user_repository, mock_db_session):
    mock_user = MagicMock(email_confirmed=False)
    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        mock_user
    )

    user_repository.mark_email_confirmed(123)

    assert mock_user.email_confirmed is True
    mock_db_session.commit.assert_called_once()


def test_get_by_id(user_repository, mock_db_session):
    mock_user = MagicMock(id=10)
    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        mock_user
    )

    user = user_repository.get_by_id(10)
    assert user == mock_user
    mock_db_session.query.assert_called_once_with(User)
    mock_db_session.query.return_value.filter.assert_called_once()


def test_update_avatar(user_repository, mock_db_session):
    mock_user = MagicMock(id=5, avatar_url=None)
    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        mock_user
    )

    updated_user = user_repository.update_avatar(
        user_id=5, avatar_url="https://example.com/avatar.png"
    )

    assert updated_user is mock_user
    assert mock_user.avatar_url == "https://example.com/avatar.png"
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(mock_user)


def test_update_avatar_user_not_found(user_repository, mock_db_session):
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    updated_user = user_repository.update_avatar(
        user_id=999, avatar_url="https://example.com/avatar.png"
    )
    assert updated_user is None
    mock_db_session.commit.assert_not_called()
    mock_db_session.refresh.assert_not_called()


def test_update_password(user_repository, mock_db_session):
    mock_user = MagicMock(id=10, hashed_password="old_hashed_password")
    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        mock_user
    )

    user_repository.update_password(user_id=10, hashed_password="new_hashed_password")

    assert mock_user.hashed_password == "new_hashed_password"
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(mock_user)


def test_update_password_user_not_found(user_repository, mock_db_session):
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc_info:
        user_repository.update_password(
            user_id=999, hashed_password="new_hashed_password"
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User not found"
    mock_db_session.commit.assert_not_called()
    mock_db_session.refresh.assert_not_called()
