from clients.cloudinary_client import CloudinaryClient
from clients.fast_api_mail_client import FastApiMailClient
from clients.redis_client import RedisCache
from repositories.contact_repository import ContactRepository
from repositories.user_repository import UserRepository
from services.auth_service import AuthService
from services.contact_service import ContactService
from services.user_service import UserService

user_repository = UserRepository()
email_client = FastApiMailClient()
image_client = CloudinaryClient()
cache_client = RedisCache()
auth_service = AuthService(user_repository=user_repository, email_sender=email_client, cache=cache_client)
user_service = UserService(user_repository=user_repository, image_client=image_client)
contact_service = ContactService(ContactRepository())