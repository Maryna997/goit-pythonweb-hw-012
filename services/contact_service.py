from abc import ABC, abstractmethod
from typing import Optional

from schemas.contacts import ContactCreate, ContactUpdate


class IContactRepository(ABC):
    @abstractmethod
    def get_all_by_user(self, user_id: int):
        pass

    @abstractmethod
    def get_by_id_and_user(self, contact_id: int, user_id: int):
        pass

    @abstractmethod
    def create_for_user(self, contact: ContactCreate, user_id: int):
        pass

    @abstractmethod
    def update_for_user(self, contact_id: int, contact: ContactUpdate, user_id: int):
        pass

    @abstractmethod
    def delete_for_user(self, contact_id: int, user_id: int):
        pass

    @abstractmethod
    def search_by_user(self, user_id: int, first_name: Optional[str] = None, last_name: Optional[str] = None,
                       email: Optional[str] = None):
        pass

    @abstractmethod
    def get_upcoming_birthdays_by_user(self, user_id: int):
        pass


class ContactService:
    def __init__(self, repository: IContactRepository):
        self.contact_repository = repository

    def get_user_contacts(self, user_id: int):
        return self.contact_repository.get_all_by_user(user_id)

    def get_user_contact(self, contact_id: int, user_id: int):
        return self.contact_repository.get_by_id_and_user(contact_id, user_id)

    def create_contact(self, contact: ContactCreate, user_id: int):
        return self.contact_repository.create_for_user(contact, user_id)

    def update_user_contact(self, contact_id: int, contact: ContactUpdate, user_id: int):
        return self.contact_repository.update_for_user(contact_id, contact, user_id)

    def delete_user_contact(self, contact_id: int, user_id: int):
        return self.contact_repository.delete_for_user(contact_id, user_id)

    def search_user_contacts(self, user_id: int, first_name: Optional[str] = None, last_name: Optional[str] = None,
                             email: Optional[str] = None):
        return self.contact_repository.search_by_user(user_id, first_name, last_name, email)

    def get_upcoming_birthdays(self, user_id: int):
        return self.contact_repository.get_upcoming_birthdays_by_user(user_id)
