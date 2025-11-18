"""
Cloudinary Client Module

This module provides a client for interacting with the Cloudinary service to manage image uploads and deletions.
"""

import os
from typing import Dict

import cloudinary
import cloudinary.api
import cloudinary.uploader

from services.user_service import IImageStorage


class CloudinaryClient(IImageStorage):
    """
    A client for Cloudinary that implements the IImageStorage interface.

    Methods:
        upload_image(file_path, options): Uploads an image to Cloudinary.
        delete_image(public_id): Deletes an image from Cloudinary.
    """

    def __init__(self):
        """
        Initializes the Cloudinary client with configuration from environment variables.
        """
        cloudinary.config(
            cloud_name=os.environ.get("CLOUDINARY_NAME"),
            api_key=os.environ.get("CLOUDINARY_API_KEY"),
            api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
        )

    def upload_image(self, file_path: str, options: Dict = None) -> Dict:
        """
        Uploads an image to Cloudinary.

        Args:
            file_path (str): The local path to the image file.
            options (Dict, optional): Additional options for the upload.

        Returns:
            Dict: The response from Cloudinary with upload details.
        """
        options = options or {}
        return cloudinary.uploader.upload(file_path, **options)

    def delete_image(self, public_id: str) -> Dict:
        """
        Deletes an image from Cloudinary.

        Args:
            public_id (str): The public ID of the image to delete.

        Returns:
            Dict: The response from Cloudinary with deletion details.
        """
        return cloudinary.uploader.destroy(public_id)
