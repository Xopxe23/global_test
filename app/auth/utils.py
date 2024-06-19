import datetime

from fastapi import Depends, Header
from jose import JWTError, jwt

from app.auth.models import User
from app.auth.repositories import AuthRepository, get_auth_repository
from app.config import settings


def parse_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.SECRET, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        expired: datetime.datetime = payload.get("exp")
        if user_id is None:
            return None
    except JWTError:
        return None
    return {
        "sub": user_id,
        "exp": expired,
    }


async def get_current_user(
        authorization: str = Header(None),
        auth_db: AuthRepository = Depends(get_auth_repository)
) -> User | None:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ")[1]
    token_data = parse_token(token)
    if not token_data:
        return None
    user_id = token_data.get("sub")
    if not user_id:
        return None
    expires_at = token_data.get("exp")
    if expires_at < datetime.datetime.now().timestamp():
        return None
    user = await auth_db.get_user_by_id(user_id)
    return user


async def get_current_superuser(
        user: User = Depends(get_current_user)
) -> User | None:
    if not user or not user.is_superuser:
        return None
    return user
