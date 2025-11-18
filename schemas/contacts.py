"""
Contact Schemas

This module defines the Pydantic models for managing contact-related data.
"""

from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr


class ContactBase(BaseModel):
    """
    Base model for contact data.

    Attributes:
        first_name (str): The contact's first name.
        last_name (str): The contact's last name.
        email (EmailStr): The contact's email address.
        phone_number (str): The contact's phone number.
        birthday (date): The contact's birthday.
        additional_data (Optional[str]): Additional notes or details about the contact.
    """
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    birthday: date
    additional_data: Optional[str] = None


class ContactCreate(ContactBase):
    """
    Model for creating a new contact.

    Inherits all attributes from ContactBase.
    """
    pass


class ContactUpdate(BaseModel):
    """
    Model for updating contact data.

    Attributes:
        first_name (Optional[str]): The contact's first name.
        last_name (Optional[str]): The contact's last name.
        email (Optional[EmailStr]): The contact's email address.
        phone_number (Optional[str]): The contact's phone number.
        birthday (Optional[date]): The contact's birthday.
        additional_data (Optional[str]): Additional notes or details about the contact.
    """
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    birthday: Optional[date] = None
    additional_data: Optional[str] = None


class ContactOut(ContactBase):
    """
    Model for representing a contact in responses.

    Attributes:
        id (int): The unique identifier of the contact.

    Inherits all attributes from ContactBase.
    """
    id: int

    class Config:
        from_attributes = True
