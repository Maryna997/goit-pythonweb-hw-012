from datetime import date, datetime

import pytest
from fastapi.testclient import TestClient

from api.instances import auth_service, contact_service
from main import app
from schemas.users import UserOut


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture
def test_user():
    return UserOut(
        id=1,
        username="testuser",
        email="testuser@example.com",
        created_at=datetime(2025, 11, 19, 12, 0, 0),
        email_confirmed=True,
        avatar_url=None,
    )


@pytest.fixture
def override_deps(test_user):
    async def mock_get_current_user(token: str = None):
        return test_user

    app.dependency_overrides[auth_service.get_current_user] = mock_get_current_user

    orig_get_user_contacts = contact_service.get_user_contacts
    orig_search_user_contacts = contact_service.search_user_contacts
    orig_get_upcoming_birthdays = contact_service.get_upcoming_birthdays
    orig_create_contact = contact_service.create_contact
    orig_get_user_contact = contact_service.get_user_contact
    orig_update_user_contact = contact_service.update_user_contact
    orig_delete_user_contact = contact_service.delete_user_contact

    mock_contact_data = {
        "id": 10,
        "user_id": 1,
        "first_name": "Alice",
        "last_name": "Smith",
        "email": "alice@example.com",
        "phone_number": "123-456-7890",
        "birthday": date(1990, 1, 5).isoformat(),
        "additional_data": "Friend from school",
    }

    mock_contacts_list = [
        dict(mock_contact_data, id=10, first_name="Alice", last_name="Smith"),
        dict(mock_contact_data, id=11, first_name="Bob", last_name="Johnson"),
    ]

    def mock_get_user_contacts(user_id: int):
        return mock_contacts_list

    def mock_search_user_contacts(user_id, first_name=None, last_name=None, email=None):
        results = []
        for c in mock_contacts_list:
            if first_name and first_name.lower() not in c["first_name"].lower():
                continue
            if last_name and last_name.lower() not in c["last_name"].lower():
                continue
            if email and email.lower() not in c["email"].lower():
                continue
            results.append(c)
        return results

    def mock_get_upcoming_birthdays(user_id: int):
        return mock_contacts_list

    def mock_create_contact(contact, user_id: int):
        return dict(mock_contact_data, id=12, **contact.model_dump(), user_id=user_id)

    def mock_get_user_contact(contact_id: int, user_id: int):
        for c in mock_contacts_list:
            if c["id"] == contact_id and c["user_id"] == user_id:
                return c
        return None

    def mock_update_user_contact(contact_id: int, contact, user_id: int):
        for c in mock_contacts_list:
            if c["id"] == contact_id and c["user_id"] == user_id:
                updated_data = c.copy()
                contact_dict = contact.model_dump(exclude_unset=True)
                for k, v in contact_dict.items():
                    updated_data[k] = v
                return updated_data
        return None

    def mock_delete_user_contact(contact_id: int, user_id: int):
        for i, c in enumerate(mock_contacts_list):
            if c["id"] == contact_id and c["user_id"] == user_id:
                return mock_contacts_list.pop(i)
        return None

    contact_service.get_user_contacts = mock_get_user_contacts
    contact_service.search_user_contacts = mock_search_user_contacts
    contact_service.get_upcoming_birthdays = mock_get_upcoming_birthdays
    contact_service.create_contact = mock_create_contact
    contact_service.get_user_contact = mock_get_user_contact
    contact_service.update_user_contact = mock_update_user_contact
    contact_service.delete_user_contact = mock_delete_user_contact

    yield

    app.dependency_overrides = {}
    contact_service.get_user_contacts = orig_get_user_contacts
    contact_service.search_user_contacts = orig_search_user_contacts
    contact_service.get_upcoming_birthdays = orig_get_upcoming_birthdays
    contact_service.create_contact = orig_create_contact
    contact_service.get_user_contact = orig_get_user_contact
    contact_service.update_user_contact = orig_update_user_contact
    contact_service.delete_user_contact = orig_delete_user_contact


def test_read_contacts_no_filters(client, override_deps):
    response = client.get(
        "/contacts/",
        headers={"Authorization": "Bearer mock_token"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["first_name"] == "Alice"
    assert data[1]["first_name"] == "Bob"


def test_read_contacts_with_filters(client, override_deps):
    response = client.get(
        "/contacts/?first_name=ali",
        headers={"Authorization": "Bearer mock_token"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["first_name"] == "Alice"


def test_read_upcoming_birthdays(client, override_deps):
    response = client.get(
        "/contacts/upcoming_birthdays",
        headers={"Authorization": "Bearer mock_token"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["id"] == 10
    assert data[1]["id"] == 11


def test_create_contact(client, override_deps):
    payload = {
        "first_name": "Carol",
        "last_name": "Danvers",
        "email": "carol@example.com",
        "phone_number": "999-888-7777",
        "birthday": "1995-07-12",
        "additional_data": "New contact",
    }
    response = client.post(
        "/contacts/",
        json=payload,
        headers={"Authorization": "Bearer mock_token"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 12
    assert data["first_name"] == "Carol"


def test_read_contact_found(client, override_deps):
    response = client.get(
        "/contacts/10",
        headers={"Authorization": "Bearer mock_token"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 10
    assert data["first_name"] == "Alice"


def test_read_contact_not_found(client, override_deps):
    response = client.get(
        "/contacts/99",
        headers={"Authorization": "Bearer mock_token"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Contact not found"


def test_update_contact_found(client, override_deps):
    payload = {
        "first_name": "Alicia",
    }
    response = client.put(
        "/contacts/10",
        json=payload,
        headers={"Authorization": "Bearer mock_token"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 10
    assert data["first_name"] == "Alicia"
    assert data["last_name"] == "Smith"


def test_update_contact_not_found(client, override_deps):
    payload = {
        "first_name": "George",
    }
    response = client.put(
        "/contacts/999",
        json=payload,
        headers={"Authorization": "Bearer mock_token"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Contact not found"


def test_delete_contact_found(client, override_deps):
    response = client.delete(
        "/contacts/11",
        headers={"Authorization": "Bearer mock_token"},
    )
    assert response.status_code == 204


def test_delete_contact_not_found(client, override_deps):
    response = client.delete(
        "/contacts/999",
        headers={"Authorization": "Bearer mock_token"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Contact not found"
