"""
Authentication Schemas

This module defines the Pydantic models for authentication-related data structures.
"""

from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    """
    Model representing an authentication token.

    Attributes:
        access_token (str): The access token string.
        token_type (str): The type of the token (e.g., "Bearer").
    """
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    Model for token-related user data.

    Attributes:
        username (Optional[str]): The username extracted from the token, if available.
    """
    username: Optional[str] = None
