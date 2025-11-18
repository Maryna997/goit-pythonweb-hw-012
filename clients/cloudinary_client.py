import os
from typing import Dict

import cloudinary
import cloudinary.api
import cloudinary.uploader

from services.user_service import IImageStorage


class CloudinaryClient(IImageStorage):
    def __init__(self):
        cloudinary.config(
            cloud_name=os.environ.get("CLOUDINARY_NAME"),
            api_key=os.environ.get("CLOUDINARY_API_KEY"),
            api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
        )

    def upload_image(self, file_path: str, options: Dict = None) -> Dict:
        options = options or {}
        return cloudinary.uploader.upload(file_path, **options)

    def delete_image(self, public_id: str) -> Dict:
        return cloudinary.uploader.destroy(public_id)
