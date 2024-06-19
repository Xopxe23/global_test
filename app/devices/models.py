import datetime
import uuid
from typing import Annotated

from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

from app.database import Base

uuid_pk = Annotated[uuid.UUID, mapped_column(primary_key=True, default=uuid.uuid4)]


class Device(Base):
    __tablename__ = "device"

    id: Mapped[uuid_pk]
    ip_address: Mapped[str]
    description: Mapped[str] = mapped_column(nullable=True)


class Terminal(Base):
    __tablename__ = "terminal"
    id: Mapped[uuid_pk]
    device_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("device.id", ondelete="cascade"))
    mac_address: Mapped[str]
    model: Mapped[str]
    date_created: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now())
    date_last_pull: Mapped[datetime.datetime] = mapped_column(nullable=True)
