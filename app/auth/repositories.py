from uuid import UUID

from fastapi import Depends
from sqlalchemy import Select, delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import RefreshToken, User, VerifyCode
from app.database import get_async_session


class AuthRepository:
    user_table = User
    refresh_token_table = RefreshToken
    verify_code_table = VerifyCode

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_users(self) -> list[User] | None:
        statement = select(self.user_table).where(self.user_table.is_active)
        result = await self.session.execute(statement)
        return result.scalars()

    async def get_user_by_id(self, id: UUID) -> User | None:
        statement = select(self.user_table).where(self.user_table.id == id)
        return await self._get_user(statement)

    async def get_user_by_email(self, email: str) -> User | None:
        statement = select(self.user_table).where(
            func.lower(self.user_table.email) == func.lower(email)
        )
        return await self._get_user(statement)

    async def create_user(self, user_data: dict) -> User:
        user = self.user_table(**user_data)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def verify_user(self, user: User) -> None:
        user.is_active = True
        await self.session.commit()

    async def update_user(self, user: User, user_data: dict) -> User:
        for key, value in user_data.items():
            if value:
                setattr(user, key, value)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete_user(self, user: User) -> None:
        await self.session.delete(user)
        await self.session.commit()

    async def create_verify_code(self, verify_code_data: dict) -> str:
        verify_code = self.verify_code_table(**verify_code_data)
        self.session.add(verify_code)
        await self.session.commit()
        return verify_code.code

    async def get_verify_code(self, verify_code_data: dict) -> VerifyCode:
        statement = select(self.verify_code_table).filter_by(**verify_code_data)
        results = await self.session.execute(statement)
        return results.unique().scalar_one_or_none()

    async def delete_users_verify_codes(self, user: User) -> None:
        statement = delete(self.verify_code_table).where(
            self.verify_code_table.user_id == user.id
        )
        await self.session.execute(statement)
        await self.session.commit()

    async def create_refresh_token(self, refresh_token_data: dict) -> RefreshToken:
        refresh_token = self.refresh_token_table(**refresh_token_data)
        self.session.add(refresh_token)
        await self.session.commit()
        await self.session.refresh(refresh_token)
        return refresh_token

    async def get_refresh_token(self, token: str) -> RefreshToken | None:
        statement = select(self.refresh_token_table).where(
            self.refresh_token_table.token == token
        )
        results = await self.session.execute(statement)
        return results.unique().scalar_one_or_none()

    async def delete_refresh_token(self, token: RefreshToken) -> None:
        await self.session.delete(token)
        await self.session.commit()

    async def _get_user(self, statement: Select) -> User | None:
        results = await self.session.execute(statement)
        return results.unique().scalar_one_or_none()


async def get_auth_repository(session: AsyncSession = Depends(get_async_session)):
    yield AuthRepository(session)
