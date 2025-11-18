from fastapi import APIRouter, Depends, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr

from api.instances import auth_service
from schemas.auth import Token
from schemas.users import UserCreate, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    return await auth_service.register_user(user)


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    return auth_service.login_user(form_data.username, form_data.password)


@router.get("/confirm/{token}", response_model=UserOut)
def confirm_email(token: str):
    user = auth_service.confirm_email(token)
    return user


@router.post("/password-reset/request", status_code=status.HTTP_200_OK)
async def request_password_reset(email: EmailStr = Body(..., embed=True)):
    reset_token = auth_service.create_password_reset_token(email)
    await auth_service.send_password_reset_email(email, reset_token)
    return {"message": "Password reset email sent."}


@router.post("/password-reset/confirm", status_code=status.HTTP_200_OK)
async def confirm_password_reset(token: str, new_password: str):
    auth_service.reset_password(token, new_password)
    return {"message": "Password has been reset successfully."}
