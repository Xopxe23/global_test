from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, field_validator


class UserUpdateSchema(BaseModel):

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None

    @field_validator("first_name", "last_name", "middle_name")
    def check_length(cls, v):
        if len(v) < 2:
            raise ValueError("Field must be at least 2 characters long")
        return v


class UserCreateSchema(UserUpdateSchema):
    email: EmailStr
    first_name: str
    last_name: str
    middle_name: Optional[str] = None

    @field_validator("first_name", "last_name", "middle_name")
    def check_length(cls, v):
        if len(v) < 2:
            raise ValueError("Field must be at least 2 characters long")
        return v


class EmailSchema(BaseModel):
    email: EmailStr


class TokenSchema(BaseModel):
    token: str


class VerifyCodeSchema(EmailSchema):
    code: str

    @field_validator("code")
    def check_code(cls, v):
        if len(v) != 6 or not all(c.isupper() and c.isalpha() for c in v):
            raise ValueError("Code must be 6 uppercase letters")
        return v


class UserInfoSchema(UserCreateSchema):
    id: UUID
    is_active: bool
    is_superuser: bool

    class Config:
        from_attributes = True
