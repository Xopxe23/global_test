import datetime
import enum
import uuid
from typing import Annotated

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

uuid_pk = Annotated[uuid.UUID, mapped_column(primary_key=True, default=uuid.uuid4)]


class User(Base):
    __tablename__ = "auth_user"

    id: Mapped[uuid_pk]
    first_name: Mapped[str]
    middle_name: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(default=False)
    is_superuser: Mapped[bool] = mapped_column(default=False)


class RefreshToken(Base):
    __tablename__ = "refresh_token"

    id: Mapped[uuid_pk]
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("auth_user.id", ondelete="cascade"))
    token: Mapped[str]
    expires_at: Mapped[datetime.datetime]


class Action(enum.Enum):
    register = "register"
    login = "login"


class VerifyCode(Base):
    __tablename__ = "verify_code"

    id: Mapped[uuid_pk]
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("auth_user.id", ondelete="cascade"))
    action: Mapped[Action]
    code: Mapped[str]
    expires_at: Mapped[datetime.datetime]
