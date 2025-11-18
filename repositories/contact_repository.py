"""
Contact Repository Module

This module contains the Contact model and ContactRepository class for managing contacts in the database.
"""

import os
from datetime import datetime, timedelta

from sqlalchemy import Column, Integer, String, Date, or_, and_, extract, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from schemas.contacts import ContactCreate, ContactUpdate
from services.contact_service import IContactRepository

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:qwerty@localhost:5432/hw10")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
Base.metadata.create_all(bind=engine)


class Contact(Base):
    """
    SQLAlchemy model representing a contact.

    Attributes:
        id (int): Primary key of the contact.
        user_id (int): ID of the user who owns this contact.
        first_name (str): First name of the contact.
        last_name (str): Last name of the contact.
        email (str): Email address of the contact.
        phone_number (str): Phone number of the contact.
        birthday (datetime.date): Birthday of the contact.
        additional_data (str): Additional information about the contact.
    """
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String, unique=True, index=True)
    birthday = Column(Date)
    additional_data = Column(String, nullable=True)


class ContactRepository(IContactRepository):
    """
    Repository class for managing contacts.

    Methods:
        get_all_by_user(user_id): Retrieves all contacts for a specific user.
        get_by_id_and_user(contact_id, user_id): Retrieves a specific contact by ID and user ID.
        create_for_user(contact, user_id): Creates a new contact for a specific user.
        update_for_user(contact_id, contact, user_id): Updates an existing contact for a specific user.
        delete_for_user(contact_id, user_id): Deletes a specific contact for a specific user.
        search_by_user(user_id, first_name, last_name, email): Searches contacts for a specific user.
        get_upcoming_birthdays_by_user(user_id): Retrieves upcoming birthdays for contacts of a user.
    """

    def __init__(self):
        """
        Initializes the ContactRepository with a database session.
        """
        self.db = SessionLocal()

    def get_all_by_user(self, user_id: int):
        """
        Retrieves all contacts for a specific user.

        Args:
            user_id (int): The ID of the user.

        Returns:
            list[Contact]: List of contacts for the user.
        """
        return self.db.query(Contact).filter(Contact.user_id == user_id).all()

    def get_by_id_and_user(self, contact_id: int, user_id: int):
        """
        Retrieves a specific contact by its ID and user ID.

        Args:
            contact_id (int): The ID of the contact.
            user_id (int): The ID of the user.

        Returns:
            Contact: The contact object, or None if not found.
        """
        return self.db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == user_id).first()

    def create_for_user(self, contact: ContactCreate, user_id: int):
        """
        Creates a new contact for a specific user.

        Args:
            contact (ContactCreate): The data for the new contact.
            user_id (int): The ID of the user.

        Returns:
            Contact: The created contact.
        """
        db_contact = Contact(**contact.model_dump(), user_id=user_id)
        self.db.add(db_contact)
        self.db.commit()
        self.db.refresh(db_contact)
        return db_contact

    def update_for_user(self, contact_id: int, contact: ContactUpdate, user_id: int):
        """
        Updates an existing contact for a specific user.

        Args:
            contact_id (int): The ID of the contact to update.
            contact (ContactUpdate): The updated data for the contact.
            user_id (int): The ID of the user.

        Returns:
            Contact: The updated contact, or None if not found.
        """
        db_contact = self.get_by_id_and_user(contact_id, user_id)
        if db_contact:
            for key, value in contact.model_dump(exclude_unset=True).items():
                setattr(db_contact, key, value)
            self.db.commit()
            self.db.refresh(db_contact)
        return db_contact

    def delete_for_user(self, contact_id: int, user_id: int):
        """
        Deletes a specific contact for a specific user.

        Args:
            contact_id (int): The ID of the contact to delete.
            user_id (int): The ID of the user.

        Returns:
            Contact: The deleted contact, or None if not found.
        """
        db_contact = self.get_by_id_and_user(contact_id, user_id)
        if db_contact:
            self.db.delete(db_contact)
            self.db.commit()
        return db_contact

    def search_by_user(self, user_id: int, first_name: str = None, last_name: str = None, email: str = None):
        """
        Searches contacts for a specific user based on optional filters.

        Args:
            user_id (int): The ID of the user.
            first_name (str, optional): The first name to search for.
            last_name (str, optional): The last name to search for.
            email (str, optional): The email address to search for.

        Returns:
            list[Contact]: List of contacts matching the search criteria.
        """
        query = self.db.query(Contact).filter(Contact.user_id == user_id)
        if first_name:
            query = query.filter(Contact.first_name.ilike(f"%{first_name}%"))
        if last_name:
            query = query.filter(Contact.last_name.ilike(f"%{last_name}%"))
        if email:
            query = query.filter(Contact.email.ilike(f"%{email}%"))
        return query.all()

    def get_upcoming_birthdays_by_user(self, user_id: int):
        """
        Retrieves upcoming birthdays for contacts of a user within the next 7 days.

        Args:
            user_id (int): The ID of the user.

        Returns:
            list[Contact]: List of contacts with upcoming birthdays.
        """
        today = datetime.today()
        upcoming_days = [(today + timedelta(days=i)).date() for i in range(7)]
        upcoming_month_days = [(d.month, d.day) for d in upcoming_days]

        conditions = [
            and_(
                extract('month', Contact.birthday) == month,
                extract('day', Contact.birthday) == day
            )
            for month, day in upcoming_month_days
        ]

        return self.db.query(Contact).filter(Contact.user_id == user_id, or_(*conditions)).all()
