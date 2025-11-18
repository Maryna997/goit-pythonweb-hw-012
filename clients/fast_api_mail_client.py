import logging
import os
from typing import List

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr

from services.auth_service import IEmailSender

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("email_sender")


class FastApiMailClient(IEmailSender):
    def __init__(self):
        self.config = ConnectionConfig(
            MAIL_USERNAME=os.environ.get("MAIL_USERNAME"),
            MAIL_PASSWORD=os.environ.get("MAIL_PASSWORD"),
            MAIL_FROM=os.environ.get("MAIL_FROM"),
            MAIL_SERVER=os.environ.get("MAIL_SERVER"),
            MAIL_PORT=os.environ.get("MAIL_PORT"),
            USE_CREDENTIALS=True,
            MAIL_STARTTLS=False,
            MAIL_SSL_TLS=True
        )
        self.mailer = FastMail(self.config)

    async def send_email(self, subject: str, recipients: List[EmailStr], body: str):
        message = MessageSchema(
            subject=subject,
            recipients=recipients,
            body=body,
            subtype=MessageType.plain
        )

        logger.info(f"Sending email to {recipients}: {message}")

        try:
            await self.mailer.send_message(message)
            logger.info(f"Email sent successfully to {recipients}")
        except Exception as e:
            logger.error(f"Failed to send email to {recipients}. Error: {e}")
