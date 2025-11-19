from datetime import date
from unittest.mock import Mock

import pytest

from schemas.contacts import ContactCreate, ContactUpdate, ContactOut
from services.contact_service import ContactService


@pytest.fixture
def mock_repository():
    return Mock()


@pytest.fixture
def contact_service(mock_repository):
    return ContactService(repository=mock_repository)


def test_get_user_contacts(contact_service, mock_repository):
    user_id = 1
    expected_contacts = [
        ContactOut(
            id=1,
            first_name="John",
            last_name="Doe",
            email="john@doe.com",
            phone_number="123456789",
            birthday=date(1990, 1, 1)
        ),
        ContactOut(
            id=2,
            first_name="Jane",
            last_name="Smith",
            email="jane@smith.com",
            phone_number="987654321",
            birthday=date(1992, 6, 15)
        )
    ]
    mock_repository.get_all_by_user.return_value = expected_contacts
    result = contact_service.get_user_contacts(user_id)
    assert result == expected_contacts
    mock_repository.get_all_by_user.assert_called_once_with(user_id)


def test_get_user_contact(contact_service, mock_repository):
    user_id = 1
    contact_id = 2
    expected_contact = ContactOut(
        id=2,
        first_name="Jane",
        last_name="Smith",
        email="jane@smith.com",
        phone_number="987654321",
        birthday=date(1992, 6, 15)
    )
    mock_repository.get_by_id_and_user.return_value = expected_contact
    result = contact_service.get_user_contact(contact_id, user_id)
    assert result == expected_contact
    mock_repository.get_by_id_and_user.assert_called_once_with(contact_id, user_id)


def test_create_contact(contact_service, mock_repository):
    user_id = 1
    new_contact = ContactCreate(
        first_name="Alice",
        last_name="Wonderland",
        email="alice@wonderland.com",
        phone_number="000000000",
        birthday=date(1995, 3, 20)
    )
    expected_created_contact = ContactOut(
        id=3,
        first_name="Alice",
        last_name="Wonderland",
        email="alice@wonderland.com",
        phone_number="000000000",
        birthday=date(1995, 3, 20)
    )
    mock_repository.create_for_user.return_value = expected_created_contact
    result = contact_service.create_contact(new_contact, user_id)
    assert result == expected_created_contact
    mock_repository.create_for_user.assert_called_once_with(new_contact, user_id)


def test_update_user_contact(contact_service, mock_repository):
    user_id = 1
    contact_id = 2
    update_data = ContactUpdate(last_name="Doe2")
    updated_contact = ContactOut(
        id=2,
        first_name="Jane",
        last_name="Doe2",
        email="jane@smith.com",
        phone_number="987654321",
        birthday=date(1992, 6, 15)
    )
    mock_repository.update_for_user.return_value = updated_contact
    result = contact_service.update_user_contact(contact_id, update_data, user_id)
    assert result == updated_contact
    mock_repository.update_for_user.assert_called_once_with(contact_id, update_data, user_id)


def test_delete_user_contact(contact_service, mock_repository):
    user_id = 1
    contact_id = 2
    mock_repository.delete_for_user.return_value = True
    result = contact_service.delete_user_contact(contact_id, user_id)
    assert result is True
    mock_repository.delete_for_user.assert_called_once_with(contact_id, user_id)


def test_search_user_contacts(contact_service, mock_repository):
    user_id = 1
    first_name = "Jane"
    last_name = None
    email = None
    expected_result = [
        ContactOut(
            id=2,
            first_name="Jane",
            last_name="Smith",
            email="jane@smith.com",
            phone_number="987654321",
            birthday=date(1992, 6, 15)
        )
    ]
    mock_repository.search_by_user.return_value = expected_result
    result = contact_service.search_user_contacts(user_id, first_name=first_name, last_name=last_name, email=email)
    assert result == expected_result
    mock_repository.search_by_user.assert_called_once_with(user_id, first_name, last_name, email)


def test_get_upcoming_birthdays(contact_service, mock_repository):
    user_id = 1
    expected_result = [
        ContactOut(
            id=3,
            first_name="Alice",
            last_name="Wonderland",
            email="alice@wonderland.com",
            phone_number="000000000",
            birthday=date(1995, 3, 20)
        )
    ]
    mock_repository.get_upcoming_birthdays_by_user.return_value = expected_result
    result = contact_service.get_upcoming_birthdays(user_id)
    assert result == expected_result
    mock_repository.get_upcoming_birthdays_by_user.assert_called_once_with(user_id)
