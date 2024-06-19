from uuid import UUID

from fastapi import Depends
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.devices.models import Terminal, Device


class DeviceRepository:
    device_table = Device
    terminal_table = Terminal

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_devices(self) -> list[Device] | None:
        statement = select(self.device_table)
        result = await self.session.execute(statement)
        return result.scalars()

    async def create_device(self, device_data: dict) -> Device:
        device = self.device_table(**device_data)
        self.session.add(device)
        await self.session.commit()
        await self.session.refresh(device)
        return device

    async def get_terminals(self) -> list[Terminal] | None:
        statement = select(self.terminal_table)
        result = await self.session.execute(statement)
        return result.scalars()

    async def create_terminal(self, terminal_data: dict) -> Terminal:
        terminal = self.terminal_table(**terminal_data)
        self.session.add(terminal)
        await self.session.commit()
        await self.session.refresh(terminal)
        return terminal

    async def delete_terminal(self, terminal_id: UUID) -> None:
        statement = delete(self.terminal_table).where(self.terminal_table.id == terminal_id)
        await self.session.execute(statement)
        await self.session.commit()


async def get_device_repository(session: AsyncSession = Depends(get_async_session)):
    yield DeviceRepository(session)
