import os

from fastapi import APIRouter, Depends, HTTPException, UploadFile, Request
from fastapi.params import File
from jose import jwt
from slowapi import Limiter
from slowapi.util import get_remote_address

from clients.cloudinary_client import CloudinaryClient
from clients.fast_api_mail_client import FastApiMailClient
from repositories.user_repository import UserRepository
from schemas.users import UserOut
from services.auth_service import AuthService
from services.user_service import UserService

SECRET_KEY = os.environ.get("AUTH_SECRET_KEY")
ALGORITHM = os.environ.get("AUTH_JWT_ALGORITHM")


def custom_key_func(request: Request):
    try:
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub", "anonymous")
        return f"user-{user_id}"
    except Exception:
        return f"ip-{get_remote_address(request)}"


limiter = Limiter(key_func=custom_key_func, storage_uri="redis://redis:6379")

router = APIRouter(prefix="/users", tags=["users"])

user_repository = UserRepository()
email_client = FastApiMailClient()
image_client = CloudinaryClient()
auth_service = AuthService(user_repository=user_repository, email_sender=email_client)
user_service = UserService(user_repository=user_repository, image_client=image_client)


@router.get(
    "/me",
    response_model=UserOut,
)
@limiter.limit("5/minute")
async def get_current_user_info(
        request: Request,
        current_user: UserOut = Depends(auth_service.get_current_user),
):
    return current_user


@router.post("/me/avatar", response_model=UserOut)
async def change_avatar(
        file: UploadFile = File(...),
        current_user: UserOut = Depends(auth_service.get_current_user),
):
    updated_user = user_service.change_avatar(current_user.id, file)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user
