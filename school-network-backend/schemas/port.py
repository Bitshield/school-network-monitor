from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
from enum import Enum as PyEnum


class PortTypeEnum(str, PyEnum):
    ETHERNET = "ETHERNET"
    FIBER = "FIBER"
    SFP = "SFP"
    SFP_PLUS = "SFP+"
    QSFP = "QSFP"
    VIRTUAL = "VIRTUAL"
    UNKNOWN = "UNKNOWN"


class PortStatusEnum(str, PyEnum):
    UP = "UP"
    DOWN = "DOWN"
    DISABLED = "DISABLED"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"


class PortSpeedEnum(str, PyEnum):
    SPEED_10M = "10M"
    SPEED_100M = "100M"
    SPEED_1G = "1G"
    SPEED_10G = "10G"
    SPEED_25G = "25G"
    SPEED_40G = "40G"
    SPEED_100G = "100G"
    UNKNOWN = "UNKNOWN"


class PortCreate(BaseModel):
    """Create port request."""
    device_id: str
    name: str = Field(..., min_length=1, max_length=100)
    port_number: int = Field(..., ge=1)
    port_type: PortTypeEnum = PortTypeEnum.ETHERNET
    speed: Optional[PortSpeedEnum] = PortSpeedEnum.UNKNOWN
    duplex: Optional[str] = Field(None, max_length=50)
    vlan_id: Optional[int] = Field(None, ge=1, le=4094)
    description: Optional[str] = Field(None, max_length=500)
    is_trunk: bool = False
    allowed_vlans: Optional[str] = None
    native_vlan: Optional[int] = None
    
    @field_validator('vlan_id')
    @classmethod
    def validate_vlan(cls, v):
        if v is not None and not (1 <= v <= 4094):
            raise ValueError('VLAN ID must be between 1 and 4094')
        return v


class PortUpdate(BaseModel):
    """Update port request."""
    name: Optional[str] = None
    port_type: Optional[PortTypeEnum] = None
    speed: Optional[PortSpeedEnum] = None
    duplex: Optional[str] = None
    vlan_id: Optional[int] = None
    description: Optional[str] = None
    status: Optional[PortStatusEnum] = None
    is_trunk: Optional[bool] = None
    allowed_vlans: Optional[str] = None
    native_vlan: Optional[int] = None


class PortResponse(BaseModel):
    """Port response."""
    id: str
    device_id: str
    name: str
    port_number: int
    port_type: PortTypeEnum
    status: PortStatusEnum
    speed: Optional[PortSpeedEnum]
    duplex: Optional[str]
    vlan_id: Optional[int]
    description: Optional[str]
    is_trunk: bool
    allowed_vlans: Optional[str]
    native_vlan: Optional[int]
    mac_address: Optional[str]
    rx_bytes: Optional[int]
    tx_bytes: Optional[int]
    rx_packets: Optional[int]
    tx_packets: Optional[int]
    rx_errors: Optional[int]
    tx_errors: Optional[int]
    last_seen: datetime
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class PortDetailResponse(PortResponse):
    """Port with device relationship."""
    device: Optional['DeviceResponse'] = None


# Forward reference
from schemas.device import DeviceResponse

PortDetailResponse.model_rebuild()