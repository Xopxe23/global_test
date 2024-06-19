from uuid import UUID

from fastapi import Depends

from app.devices.models import Terminal, Device
from app.devices.repositories import DeviceRepository, get_device_repository


class DeviceService:

    def __init__(self, device_db: DeviceRepository):
        self.device_db = device_db

    async def get_devices(self) -> list[Device]:
        return await self.device_db.get_devices()

    async def get_terminals(self) -> list[Terminal]:
        return await self.device_db.get_terminals()

    async def create_device(self, device_data: dict) -> Device:
        return await self.device_db.create_device(device_data)

    async def create_terminal(self, terminal_data: dict) -> Device:
        return await self.device_db.create_terminal(terminal_data)

    async def delete_terminal(self, terminal_id: UUID) -> None:
        return await self.device_db.delete_terminal(terminal_id)


async def get_device_service(device_db: DeviceRepository = Depends(get_device_repository)):
    yield DeviceService(device_db)
