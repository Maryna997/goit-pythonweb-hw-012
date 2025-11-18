from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from clients.fast_api_mail_client import FastApiMailClient
from repositories.user_repository import UserRepository
from schemas.auth import Token
from schemas.users import UserCreate, UserOut
from services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

user_repository = UserRepository()
email_client = FastApiMailClient()
auth_service = AuthService(user_repository=user_repository, email_sender=email_client)


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
