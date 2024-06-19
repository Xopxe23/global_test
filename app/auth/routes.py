import datetime
from uuid import UUID

from fastapi import APIRouter, Depends

from app.auth.exceptions import (
    AuthenticationRequiredException,
    CodeExpiredException,
    EmailTakenException,
    NoSuchCodeException,
    NoSuchUserException,
    NoTokenException,
    PermissionDeniedException,
    TokenExpiredException,
)
from app.auth.models import Action, User
from app.auth.schemas import EmailSchema, TokenSchema, UserCreateSchema, UserInfoSchema, VerifyCodeSchema, \
    UserUpdateSchema
from app.auth.services import AuthService, get_auth_service
from app.auth.utils import get_current_superuser, get_current_user

router = APIRouter(
    prefix="/auth"
)


@router.post("/register")
async def register(
        user_data: UserCreateSchema,
        auth_service: AuthService = Depends(get_auth_service)
) -> dict:
    existing_user = await auth_service.get_user_by_email(user_data.email)
    if existing_user:
        if existing_user.is_active:
            raise EmailTakenException
        await auth_service.delete_user(existing_user)
    user_data = user_data.model_dump()
    user = await auth_service.register_user(user_data)
    await auth_service.create_verify_code(user, Action.register)
    return {"status": "verify code sent on email"}


@router.post("/verify_register")
async def verify_register(
        code_data: VerifyCodeSchema,
        auth_service: AuthService = Depends(get_auth_service)
) -> dict:
    code_data = code_data.model_dump()
    email = code_data.pop("email")
    user = await auth_service.get_user_by_email(email)
    if not user:
        raise NoSuchUserException
    code_data["user_id"] = user.id
    verify_code = await auth_service.get_verify_code(code_data)
    if not verify_code or verify_code.action != Action.register:
        raise NoSuchCodeException
    if verify_code.expires_at < datetime.datetime.now():
        await auth_service.delete_users_verify_codes(user)
        raise CodeExpiredException
    await auth_service.verify_user(user)
    await auth_service.delete_users_verify_codes(user)
    return {"status": "Registration success"}


@router.post("/login")
async def login(
        email_data: EmailSchema,
        auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.get_user_by_email(email_data.email)
    if not user or not user.is_active:
        raise NoSuchUserException
    await auth_service.delete_users_verify_codes(user)
    await auth_service.create_verify_code(user, Action.login)
    return {"status": "verify code sent on email"}


@router.post("/verify_login")
async def verify_login(
        code_data: VerifyCodeSchema,
        auth_service: AuthService = Depends(get_auth_service),
):
    code_data = code_data.model_dump()
    email = code_data.pop("email")
    user = await auth_service.get_user_by_email(email)
    if not user or not user.is_active:
        raise NoSuchUserException
    code_data["user_id"] = user.id
    verify_code = await auth_service.get_verify_code(code_data)
    if not verify_code or verify_code.action != Action.login:
        raise NoSuchCodeException
    if verify_code.expires_at < datetime.datetime.now():
        await auth_service.delete_users_verify_codes(user)
        raise CodeExpiredException
    await auth_service.delete_users_verify_codes(user)
    tokens = await auth_service.generate_tokens(user)
    return tokens


@router.post("/refresh")
async def refresh_tokens(
        token: TokenSchema,
        auth_service: AuthService = Depends(get_auth_service),
):
    token = await auth_service.get_refresh_token(token.token)
    if not token:
        raise NoTokenException
    if token.expires_at < datetime.datetime.now():
        raise TokenExpiredException
    user = await auth_service.get_user_by_id(token.user_id)
    if not user or not user.is_active:
        raise NoSuchUserException
    await auth_service.delete_refresh_token(token)
    tokens = await auth_service.generate_tokens(user)
    return tokens


@router.get("/me")
async def me(
        user: User | None = Depends(get_current_user)
) -> UserInfoSchema:
    if not user:
        raise AuthenticationRequiredException
    return user


@router.patch("/me")
async def update_info(
        user_data: UserUpdateSchema,
        user: User | None = Depends(get_current_user),
        auth_service: AuthService = Depends(get_auth_service)
) -> UserInfoSchema:
    if not user:
        raise AuthenticationRequiredException
    user_data = user_data.model_dump()
    user = await auth_service.update_user(user, user_data)
    return user


@router.get("/users")
async def get_users(
        user: User | None = Depends(get_current_superuser),
        auth_service: AuthService = Depends(get_auth_service)
) -> list[UserInfoSchema]:
    if not user:
        raise PermissionDeniedException
    return await auth_service.get_users()


@router.delete("/users/{user_id}")
async def delete_user(
        user_id: UUID,
        user: User | None = Depends(get_current_superuser),
        auth_service: AuthService = Depends(get_auth_service)
) -> None:
    if not user:
        raise PermissionDeniedException
    deleted_user = await auth_service.get_user_by_id(user_id)
    if not user:
        return
    await auth_service.delete_user(deleted_user)
