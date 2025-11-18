import os

from fastapi import APIRouter, Depends, HTTPException, UploadFile, Request
from fastapi.params import File
from jose import jwt
from slowapi import Limiter
from slowapi.util import get_remote_address

from api.instances import auth_service, user_service
from schemas.users import UserOut

SECRET_KEY = os.environ.get("AUTH_SECRET_KEY")
ALGORITHM = os.environ.get("AUTH_JWT_ALGORITHM")
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")


def custom_key_func(request: Request):
    try:
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub", "anonymous")
        return f"user-{user_id}"
    except Exception:
        return f"ip-{get_remote_address(request)}"


limiter = Limiter(key_func=custom_key_func, storage_uri=REDIS_URL)

router = APIRouter(prefix="/users", tags=["users"])


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
