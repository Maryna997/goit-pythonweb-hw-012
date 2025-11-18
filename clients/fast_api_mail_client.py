"""
FastAPI Mail Client Module

This module provides a client for sending emails using FastAPI Mail.
"""

import logging
import os
from typing import List

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr

from services.auth_service import IEmailSender

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("email_sender")


class FastApiMailClient(IEmailSender):
    """
    A client for sending emails using FastAPI Mail that implements the IEmailSender interface.

    Methods:
        send_email(subject, recipients, body): Sends an email with the specified subject, recipients, and body.
    """

    def __init__(self):
        """
        Initializes the FastAPI Mail client with configuration from environment variables.
        """
        self.config = ConnectionConfig(
            MAIL_USERNAME=os.environ.get("MAIL_USERNAME", ""),
            MAIL_PASSWORD=os.environ.get("MAIL_PASSWORD", ""),
            MAIL_FROM=os.environ.get("MAIL_FROM", "user@example.com"),
            MAIL_SERVER=os.environ.get("MAIL_SERVER", ""),
            MAIL_PORT=os.environ.get("MAIL_PORT", 587),
            USE_CREDENTIALS=True,
            MAIL_STARTTLS=False,
            MAIL_SSL_TLS=True
        )
        self.mailer = FastMail(self.config)

    async def send_email(self, subject: str, recipients: List[EmailStr], body: str):
        """
        Sends an email with the specified subject, recipients, and body.

        Args:
            subject (str): The subject of the email.
            recipients (List[EmailStr]): A list of recipient email addresses.
            body (str): The body of the email.

        Returns:
            None
        """
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
