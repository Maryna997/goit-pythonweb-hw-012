from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from clients.fast_api_mail_client import FastApiMailClient
from repositories.contact_repository import ContactRepository
from repositories.user_repository import UserRepository
from schemas.contacts import ContactCreate, ContactUpdate, ContactOut
from services.auth_service import AuthService
from services.contact_service import ContactService

router = APIRouter(prefix="/contacts", tags=["contacts"])

user_repository = UserRepository()
email_sender = FastApiMailClient()
auth_service = AuthService(user_repository=user_repository, email_sender=email_sender)
contact_service = ContactService(ContactRepository())


@router.get("/", response_model=List[ContactOut])
def read_contacts(
        first_name: str = None,
        last_name: str = None,
        email: str = None,
        current_user: dict = Depends(auth_service.get_current_user),
):
    if first_name or last_name or email:
        contacts = contact_service.search_user_contacts(current_user.id, first_name, last_name, email)
    else:
        contacts = contact_service.get_user_contacts(current_user.id)
    return contacts


@router.get("/upcoming_birthdays", response_model=List[ContactOut])
def read_upcoming_birthdays(current_user: dict = Depends(auth_service.get_current_user)):
    return contact_service.get_upcoming_birthdays(current_user.id)


@router.post("/", response_model=ContactOut, status_code=status.HTTP_201_CREATED)
def create_contact(contact: ContactCreate, current_user: dict = Depends(auth_service.get_current_user)):
    return contact_service.create_contact(contact, current_user.id)


@router.get("/{contact_id}", response_model=ContactOut)
def read_contact(contact_id: int, current_user: dict = Depends(auth_service.get_current_user)):
    contact = contact_service.get_user_contact(contact_id, current_user.id)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.put("/{contact_id}", response_model=ContactOut)
def update_contact(contact_id: int, contact: ContactUpdate,
                   current_user: dict = Depends(auth_service.get_current_user)):
    updated_contact = contact_service.update_user_contact(contact_id, contact, current_user.id)
    if updated_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return updated_contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(contact_id: int, current_user: dict = Depends(auth_service.get_current_user)):
    deleted_contact = contact_service.delete_user_contact(contact_id, current_user.id)
    if deleted_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return
