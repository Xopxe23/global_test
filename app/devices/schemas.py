import re
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, field_validator


class DeviceCreateSchema(BaseModel):
    ip_address: str
    description: Optional[str] = None

    @field_validator('ip_address')
    def check_mac_address(cls, v):
        mac_regex = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
        if not re.match(mac_regex, v):
            raise ValueError('Invalid ip address format')
        return v


class DeviceInfoSchema(DeviceCreateSchema):
    id: UUID

    class Config:
        from_attributes = True


class TerminalCreateSchema(BaseModel):
    device_id: UUID
    mac_address: str
    model: str

    @field_validator('mac_address')
    def check_mac_address(cls, v):
        mac_regex = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
        if not re.match(mac_regex, v):
            raise ValueError('Invalid MAC address format')
        return v


class TerminalInfoSchema(TerminalCreateSchema):
    id: UUID

    class Config:
        from_attributes = True
