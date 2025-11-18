import os
from datetime import datetime, timedelta

from sqlalchemy import Column, Integer, String, Date, or_, and_, extract, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from schemas.contacts import ContactCreate, ContactUpdate
from services.contact_service import IContactRepository

DATABASE_URL = os.environ.get("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
Base.metadata.create_all(bind=engine)


class Contact(Base):
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
    def __init__(self):
        self.db = SessionLocal()

    def get_all_by_user(self, user_id: int):
        return self.db.query(Contact).filter(Contact.user_id == user_id).all()

    def get_by_id_and_user(self, contact_id: int, user_id: int):
        return self.db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == user_id).first()

    def create_for_user(self, contact: ContactCreate, user_id: int):
        db_contact = Contact(**contact.model_dump(), user_id=user_id)
        self.db.add(db_contact)
        self.db.commit()
        self.db.refresh(db_contact)
        return db_contact

    def update_for_user(self, contact_id: int, contact: ContactUpdate, user_id: int):
        db_contact = self.get_by_id_and_user(contact_id, user_id)
        if db_contact:
            for key, value in contact.model_dump(exclude_unset=True).items():
                setattr(db_contact, key, value)
            self.db.commit()
            self.db.refresh(db_contact)
        return db_contact

    def delete_for_user(self, contact_id: int, user_id: int):
        db_contact = self.get_by_id_and_user(contact_id, user_id)
        if db_contact:
            self.db.delete(db_contact)
            self.db.commit()
        return db_contact

    def search_by_user(self, user_id: int, first_name: str = None, last_name: str = None, email: str = None):
        query = self.db.query(Contact).filter(Contact.user_id == user_id)
        if first_name:
            query = query.filter(Contact.first_name.ilike(f"%{first_name}%"))
        if last_name:
            query = query.filter(Contact.last_name.ilike(f"%{last_name}%"))
        if email:
            query = query.filter(Contact.email.ilike(f"%{email}%"))
        return query.all()

    def get_upcoming_birthdays_by_user(self, user_id: int):
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
