# api/v1/snmp.py
"""
SNMP query endpoints.
"""

from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from api.deps import get_db
from models.device import Device
from services.snmp_client import SNMPClient, SNMPService, SNMP_REAL_IMPL
from config import settings
from core.exceptions import raise_not_found

router = APIRouter()


def _ensure_snmp_available() -> None:
    """
    Ensure SNMP implementation is available.
    If running with the stub (Python 3.12 + pysnmp removed), raise 501.
    """
    if not SNMP_REAL_IMPL:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="SNMP support is temporarily disabled on this environment",
        )


@router.get("/device/{device_id}/info")
async def get_device_snmp_info(
    device_id: str,
    community: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    """
    Get SNMP system information from a device.
    """
    _ensure_snmp_available()

    result = await db.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()

    if not device:
        raise_not_found(Device, device_id)  # type: ignore[arg-type]

    if not device.ip:  # type: ignore[truthy-function]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Device has no IP address",
        )

    if not device.snmp_enabled:  # type: ignore[attr-defined]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SNMP is not enabled for this device",
        )

    snmp_community = (
        community or device.snmp_community or settings.SNMP_COMMUNITY  # type: ignore[attr-defined]
    )
    client = SNMPClient(device.ip, snmp_community)  # type: ignore[arg-type]
    info = await client.get_system_info()
    return info


@router.get("/device/{device_id}/interfaces")
async def get_device_snmp_interfaces(
    device_id: str,
    community: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    """
    Get SNMP interface information from a device.
    """
    _ensure_snmp_available()

    result = await db.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()

    if not device:
        raise_not_found(Device, device_id)  # type: ignore[arg-type]

    if not device.ip:  # type: ignore[truthy-function]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Device has no IP address",
        )

    snmp_community = (
        community or device.snmp_community or settings.SNMP_COMMUNITY  # type: ignore[attr-defined]
    )
    client = SNMPClient(device.ip, snmp_community)  # type: ignore[arg-type]
    interfaces = await client.get_interfaces()

    return {
        "device_id": device_id,
        "device_ip": device.ip,  # type: ignore[union-attr]
        "interface_count": len(interfaces),
        "interfaces": interfaces,
    }


@router.post("/query-oid")
async def query_oid(
    ip: str,
    oid: str,
    community: str = Query(default=settings.SNMP_COMMUNITY),
):
    """
    Query a specific OID from a device.
    """
    _ensure_snmp_available()

    client = SNMPClient(ip, community)
    value = await client.get_oid(oid) # type: ignore
    return {
        "ip": ip,
        "oid": oid,
        "value": value,
    }


@router.post("/walk-oid")
async def walk_oid(
    ip: str,
    base_oid: str,
    community: str = Query(default=settings.SNMP_COMMUNITY),
    max_rows: int = Query(default=100, ge=1, le=1000),
):
    """
    Walk an OID tree from a device.
    """
    _ensure_snmp_available()

    client = SNMPClient(ip, community)
    results = await client.walk(base_oid, max_rows=max_rows)

    return {
        "ip": ip,
        "base_oid": base_oid,
        "result_count": len(results),
        "results": [{"oid": oid, "value": value} for oid, value in results],
    }


@router.post("/discover-devices")
async def discover_devices_snmp(
    ips: List[str],
    community: str = Query(default=settings.SNMP_COMMUNITY),
):
    """
    Discover multiple devices via SNMP.
    """
    _ensure_snmp_available()

    service = SNMPService(community)
    for ip in ips:
        service.add_device(ip)

    results = await service.discover_all()
    return {
        "total_devices": len(ips),
        "results": results,
    }
