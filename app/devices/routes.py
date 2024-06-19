from uuid import UUID

from fastapi import APIRouter, Depends

from app.auth.exceptions import PermissionDeniedException
from app.auth.models import User
from app.auth.utils import get_current_user
from app.devices.schemas import DeviceInfoSchema, DeviceCreateSchema, TerminalInfoSchema, TerminalCreateSchema
from app.devices.services import DeviceService, get_device_service

router = APIRouter(
    prefix="/devices"
)


@router.get("/")
async def get_devices(
        user: User | None = Depends(get_current_user),
        device_service: DeviceService = Depends(get_device_service)
) -> list[DeviceInfoSchema]:
    if not user:
        raise PermissionDeniedException
    return await device_service.get_devices()


@router.post("/")
async def create_device(
        device: DeviceCreateSchema,
        user: User | None = Depends(get_current_user),
        device_service: DeviceService = Depends(get_device_service)
) -> DeviceInfoSchema:
    if not user:
        raise PermissionDeniedException
    device_data = device.model_dump()
    return await device_service.create_device(device_data)


@router.get("/terminals")
async def get_terminals(
        user: User | None = Depends(get_current_user),
        device_service: DeviceService = Depends(get_device_service)
) -> list[TerminalInfoSchema]:
    if not user:
        raise PermissionDeniedException
    return await device_service.get_terminals()


@router.post("/terminals")
async def create_terminal(
        terminal: TerminalCreateSchema,
        user: User | None = Depends(get_current_user),
        device_service: DeviceService = Depends(get_device_service)
) -> TerminalInfoSchema:
    if not user:
        raise PermissionDeniedException
    terminal_data = terminal.model_dump()
    return await device_service.create_terminal(terminal_data)


@router.delete("/terminals/{terminal_id}")
async def delete_terminal(
        terminal_id: UUID,
        user: User | None = Depends(get_current_user),
        device_service: DeviceService = Depends(get_device_service)
) -> None:
    if not user:
        raise PermissionDeniedException
    return await device_service.delete_terminal(terminal_id)
