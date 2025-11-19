from datetime import date, datetime, timedelta
from unittest.mock import MagicMock

import pytest

from repositories.contact_repository import ContactRepository, Contact
from schemas.contacts import ContactCreate, ContactUpdate


@pytest.fixture
def mock_db_session(mocker):
    return mocker.MagicMock()


@pytest.fixture
def contact_repository(mock_db_session):
    repo = ContactRepository()
    repo.db = mock_db_session
    return repo


def test_get_all_by_user(contact_repository, mock_db_session):
    mock_db_session.query.return_value.filter.return_value.all.return_value = [
        Contact(
            id=1,
            user_id=1,
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone_number="1234567890",
            birthday=date.today(),
            additional_data="Test data"
        ),
        Contact(
            id=2,
            user_id=1,
            first_name="Jane",
            last_name="Doe",
            email="jane.doe@example.com",
            phone_number="9876543210",
            birthday=date.today(),
            additional_data="More data"
        )
    ]
    contact_repository.db = mock_db_session

    contacts = contact_repository.get_all_by_user(1)
    assert len(contacts) == 2
    assert contacts[0].first_name == "John"
    assert contacts[1].email == "jane.doe@example.com"


def test_get_by_id_and_user(contact_repository, mock_db_session):
    mock_db_session.query.return_value.filter.return_value.first.return_value = Contact(
        id=1,
        user_id=1,
        first_name="John",
        last_name="Doe"
    )
    contact_repository.db = mock_db_session

    contact = contact_repository.get_by_id_and_user(1, 1)
    assert contact.first_name == "John"
    assert contact.user_id == 1


def test_get_by_id_and_user_not_found(contact_repository, mock_db_session):
    mock_db_session.query.return_value.filter.return_value.first.return_value = None
    contact_repository.db = mock_db_session

    contact = contact_repository.get_by_id_and_user(999, 1)
    assert contact is None


def test_create_for_user(contact_repository, mock_db_session):
    contact_data = ContactCreate(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone_number="1234567890",
        birthday=date.today(),
        additional_data="Test data"
    )
    mock_db_session.add = MagicMock()
    mock_db_session.commit = MagicMock()
    mock_db_session.refresh = MagicMock()
    contact_repository.db = mock_db_session

    contact = contact_repository.create_for_user(contact_data, 1)
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()

    assert contact.first_name == "John"
    assert contact.user_id == 1


def test_update_for_user(contact_repository, mock_db_session):
    contact_data = ContactUpdate(
        first_name="John Updated",
        additional_data="Updated additional notes"
    )

    mock_contact = MagicMock(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone_number="1234567890",
        birthday=date(1990, 1, 1),
        additional_data="Old notes"
    )
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_contact
    contact_repository.db = mock_db_session

    updated_contact = contact_repository.update_for_user(1, contact_data, 1)

    assert mock_contact.first_name == "John Updated"
    assert mock_contact.additional_data == "Updated additional notes"

    assert mock_contact.last_name == "Doe"
    assert mock_contact.email == "john.doe@example.com"
    assert mock_contact.phone_number == "1234567890"
    assert mock_contact.birthday == date(1990, 1, 1)

    assert updated_contact == mock_contact


def test_update_for_user_not_found(contact_repository, mock_db_session):
    mock_db_session.query.return_value.filter.return_value.first.return_value = None
    contact_repository.db = mock_db_session

    contact_data = ContactUpdate(first_name="Non Existent")
    updated_contact = contact_repository.update_for_user(999, contact_data, 1)
    assert updated_contact is None


def test_delete_for_user(contact_repository, mock_db_session):
    mock_contact = MagicMock()
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_contact
    mock_db_session.delete = MagicMock()
    mock_db_session.commit = MagicMock()
    contact_repository.db = mock_db_session

    deleted_contact = contact_repository.delete_for_user(1, 1)
    mock_db_session.delete.assert_called_once_with(mock_contact)
    mock_db_session.commit.assert_called_once()
    assert deleted_contact == mock_contact


def test_delete_for_user_not_found(contact_repository, mock_db_session):
    mock_db_session.query.return_value.filter.return_value.first.return_value = None
    contact_repository.db = mock_db_session

    deleted_contact = contact_repository.delete_for_user(999, 1)
    assert deleted_contact is None
    mock_db_session.delete.assert_not_called()
    mock_db_session.commit.assert_not_called()


def test_search_by_user(contact_repository, mock_db_session):
    mock_db_session.query.return_value.filter.return_value.filter.return_value.all.return_value = [
        Contact(id=1, user_id=1, first_name="John", last_name="Doe")
    ]
    contact_repository.db = mock_db_session

    results = contact_repository.search_by_user(1, first_name="John")
    assert len(results) == 1
    assert results[0].first_name == "John"


def test_search_by_user_no_filters(contact_repository, mock_db_session):
    mock_db_session.query.return_value.filter.return_value.all.return_value = [
        Contact(id=2, user_id=1, first_name="Jake", last_name="Smith"),
        Contact(id=3, user_id=1, first_name="Alice", last_name="Johnson"),
    ]
    contact_repository.db = mock_db_session

    results = contact_repository.search_by_user(1)
    assert len(results) == 2
    assert results[0].first_name == "Jake"
    assert results[1].last_name == "Johnson"


def test_search_by_user_multiple_filters(contact_repository, mock_db_session):
    mock_query = mock_db_session.query.return_value

    mock_query.filter.side_effect = lambda *args, **kwargs: mock_query
    mock_query.all.return_value = [
        Contact(id=4, user_id=1, first_name="John", last_name="Doe", email="john.doe@example.com")
    ]

    contact_repository.db = mock_db_session

    results = contact_repository.search_by_user(
        1,
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com"
    )
    assert len(results) == 1
    assert results[0].first_name == "John"
    assert results[0].last_name == "Doe"
    assert results[0].email == "john.doe@example.com"


def test_search_by_user_no_matches(contact_repository, mock_db_session):
    mock_db_session.query.return_value.filter.return_value.filter.return_value.filter.return_value.all.return_value = []
    contact_repository.db = mock_db_session

    results = contact_repository.search_by_user(1, first_name="Ghost")
    assert len(results) == 0


def test_get_upcoming_birthdays_by_user(contact_repository, mock_db_session):
    today = datetime.today()
    upcoming_contact = Contact(
        id=1,
        user_id=1,
        first_name="John",
        last_name="Doe",
        birthday=(today + timedelta(days=3)).date(),
    )
    mock_db_session.query.return_value.filter.return_value.all.return_value = [upcoming_contact]
    contact_repository.db = mock_db_session

    results = contact_repository.get_upcoming_birthdays_by_user(1)
    assert len(results) == 1
    assert results[0].birthday == (today + timedelta(days=3)).date()


def test_get_upcoming_birthdays_by_user_no_matches(contact_repository, mock_db_session):
    mock_db_session.query.return_value.filter.return_value.all.return_value = []
    contact_repository.db = mock_db_session

    results = contact_repository.get_upcoming_birthdays_by_user(1)
    assert len(results) == 0
