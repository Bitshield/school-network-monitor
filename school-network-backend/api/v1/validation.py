"""
Data validation endpoints.
"""

from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from services.validation import ValidationService


router = APIRouter()
validator = ValidationService()


class IPValidationRequest(BaseModel):
    ip: str


class MACValidationRequest(BaseModel):
    mac: str


class IPRangeValidationRequest(BaseModel):
    ip_range: str


class HostnameValidationRequest(BaseModel):
    hostname: str


class DeviceValidationRequest(BaseModel):
    name: str
    ip: Optional[str] = Field(default=None)
    mac: Optional[str] = Field(default=None)
    hostname: Optional[str] = Field(default=None)
    vlan_id: Optional[int] = Field(default=None)
    # On Python 3.10+ you can also write:
    # ip: str | None = None
    # mac: str | None = None
    # hostname: str | None = None
    # vlan_id: int | None = None


@router.post("/ip")
async def validate_ip(request: IPValidationRequest):
    """Validate an IP address."""
    is_valid, error = validator.network.validate_ip(request.ip)

    return {
        "value": request.ip,
        "valid": is_valid,
        "error": error,
    }


@router.post("/mac")
async def validate_mac(request: MACValidationRequest):
    """Validate a MAC address."""
    is_valid, error = validator.network.validate_mac(request.mac)

    normalized = None
    if is_valid:
        normalized = validator.network.normalize_mac(request.mac)

    return {
        "value": request.mac,
        "valid": is_valid,
        "error": error,
        "normalized": normalized,
    }


@router.post("/ip-range")
async def validate_ip_range(request: IPRangeValidationRequest):
    """Validate an IP range in CIDR notation."""
    is_valid, error = validator.network.validate_ip_range(request.ip_range)

    return {
        "value": request.ip_range,
        "valid": is_valid,
        "error": error,
    }


@router.post("/hostname")
async def validate_hostname(request: HostnameValidationRequest):
    """Validate a hostname."""
    is_valid, error = validator.network.validate_hostname(request.hostname)

    return {
        "value": request.hostname,
        "valid": is_valid,
        "error": error,
    }


@router.post("/device")
async def validate_device(request: DeviceValidationRequest):
    """Validate device data."""
    data = request.model_dump()
    errors = validator.validate_device_data(data)

    return {
        "valid": len(errors) == 0,
        "errors": errors if errors else None,
    }


@router.get("/check-ip-in-subnet")
async def check_ip_in_subnet(ip: str, subnet: str):
    """Check if IP address is in subnet."""
    in_subnet = validator.network.ip_in_subnet(ip, subnet)

    return {
        "ip": ip,
        "subnet": subnet,
        "in_subnet": in_subnet,
    }
