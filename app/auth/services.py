import datetime
import random
import secrets
import string
from uuid import UUID

from fastapi import Depends
from jose import jwt

from app.auth.models import Action, RefreshToken, User, VerifyCode
from app.auth.repositories import AuthRepository, get_auth_repository
from app.config import settings
from app.tasks.tasks import sent_verification_email


class AuthService:

    def __init__(self, auth_db: AuthRepository):
        self.auth_db = auth_db

    async def get_users(self) -> list[User] | None:
        return await self.auth_db.get_users()

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        return await self.auth_db.get_user_by_id(user_id)

    async def get_user_by_email(self, user_email: str) -> User | None:
        return await self.auth_db.get_user_by_email(user_email)

    async def register_user(self, user_data: dict) -> User:
        user = await self.auth_db.create_user(user_data)
        return user

    async def verify_user(self, user: User) -> None:
        await self.auth_db.verify_user(user)

    async def update_user(self, user: User, user_data: dict) -> User:
        user = await self.auth_db.update_user(user, user_data)
        return user

    async def delete_user(self, user: User) -> None:
        await self.auth_db.delete_user(user)

    async def create_verify_code(self, user: User, action: Action):
        code = self._generate_unique_code()
        code_data = {
            "code": code,
            "user_id": user.id,
            "action": action,
            "expires_at": datetime.datetime.now() + datetime.timedelta(minutes=5)
        }
        await self.auth_db.create_verify_code(code_data)
        sent_verification_email.delay(user.email, code, action.value)

    async def get_verify_code(self, verify_code_data: dict) -> VerifyCode | None:
        return await self.auth_db.get_verify_code(verify_code_data)

    async def delete_users_verify_codes(self, user: User):
        await self.auth_db.delete_users_verify_codes(user)

    async def generate_tokens(self, user: User) -> dict:
        access_token = self._create_access_token(user)
        refresh_token = self._generate_unique_string()
        refresh_token_data = {
            "user_id": user.id,
            "token": refresh_token,
            "expires_at": datetime.datetime.now() + datetime.timedelta(days=30)
        }
        await self.auth_db.create_refresh_token(refresh_token_data)
        tokens = {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
        return tokens

    async def get_refresh_token(self, refresh_token: str) -> RefreshToken | None:
        return await self.auth_db.get_refresh_token(refresh_token)

    async def delete_refresh_token(self, refresh_token: RefreshToken) -> None:
        return await self.auth_db.delete_refresh_token(refresh_token)

    @staticmethod
    def _create_access_token(user: User) -> str | None:
        data = {"sub": user.id.__str__()}
        to_encode = data.copy()
        expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=5)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @classmethod
    def _generate_unique_string(cls, byte: int = 64) -> str:
        return secrets.token_urlsafe(byte)

    @staticmethod
    def _generate_unique_code():
        letters = string.ascii_uppercase
        return ''.join(random.choice(letters) for _ in range(6))


async def get_auth_service(user_db: AuthRepository = Depends(get_auth_repository)):
    yield AuthService(user_db)
