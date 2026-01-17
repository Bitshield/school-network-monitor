"""
Device management endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from api.deps import get_db, Pagination, FilterParams
from models.device import Device, DeviceStatusEnum, DeviceTypeEnum
from schemas.device import (
    DeviceCreate,
    DeviceUpdate,
    DeviceResponse,
    DeviceDetailResponse
)
from core.exceptions import raise_not_found

router = APIRouter()


@router.get("/", response_model=List[DeviceResponse])
async def get_devices(
    db: AsyncSession = Depends(get_db),
    pagination: Pagination = Depends(),
    filters: FilterParams = Depends(),
    status: Optional[DeviceStatusEnum] = None,
    device_type: Optional[DeviceTypeEnum] = None,
    is_monitored: Optional[bool] = None,
):
    """
    Get all devices with pagination and filtering.
    
    - **search**: Search by name, IP, MAC, or hostname
    - **status**: Filter by device status
    - **device_type**: Filter by device type
    - **is_monitored**: Filter by monitoring status
    """
    query = select(Device)
    
    # Apply filters
    if filters.search:
        search_term = f"%{filters.search}%"
        query = query.where(
            or_(
                Device.name.ilike(search_term),
                Device.ip.ilike(search_term),
                Device.mac.ilike(search_term),
                Device.hostname.ilike(search_term)
            )
        )
    
    if status:
        query = query.where(Device.status == status)
    
    if device_type:
        query = query.where(Device.device_type == device_type)
    
    if is_monitored is not None:
        query = query.where(Device.is_monitored == is_monitored)
    
    # Apply sorting
    if filters.sort_by:
        order_column = getattr(Device, filters.sort_by, Device.name)
        if filters.sort_order == "desc":
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())
    else:
        query = query.order_by(Device.name.asc())
    
    # Apply pagination
    query = query.offset(pagination.skip).limit(pagination.limit)
    
    result = await db.execute(query)
    devices = result.scalars().all()
    
    return devices


@router.get("/count")
async def get_device_count(
    db: AsyncSession = Depends(get_db),
    status: Optional[DeviceStatusEnum] = None,
    device_type: Optional[DeviceTypeEnum] = None,
):
    """Get total count of devices with optional filters."""
    query = select(func.count(Device.id))
    
    if status:
        query = query.where(Device.status == status)
    
    if device_type:
        query = query.where(Device.device_type == device_type)
    
    result = await db.execute(query)
    count = result.scalar_one()
    
    return {"count": count}


@router.get("/{device_id}", response_model=DeviceDetailResponse)
async def get_device(
    device_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific device by ID with all relationships."""
    result = await db.execute(
        select(Device).where(Device.id == device_id)
    )
    device = result.scalar_one_or_none()
    
    if not device:
        raise_not_found("Device", device_id)
    
    return device


@router.post("/", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
async def create_device(
    device_data: DeviceCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new device."""
    import uuid
    from datetime import datetime
    
    # Check if IP already exists
    if device_data.ip:
        result = await db.execute(
            select(Device).where(Device.ip == device_data.ip)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Device with IP {device_data.ip} already exists"
            )
    
    # Check if MAC already exists
    if device_data.mac:
        result = await db.execute(
            select(Device).where(Device.mac == device_data.mac)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Device with MAC {device_data.mac} already exists"
            )
    
    # Create device
    device = Device(
        id=str(uuid.uuid4()),
        **device_data.model_dump(),
        status=DeviceStatusEnum.UNKNOWN,
        last_seen=datetime.utcnow(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(device)
    await db.commit()
    await db.refresh(device)
    
    return device


@router.put("/{device_id}", response_model=DeviceResponse)
async def update_device(
    device_id: str,
    device_data: DeviceUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a device."""
    from datetime import datetime
    
    result = await db.execute(
        select(Device).where(Device.id == device_id)
    )
    device = result.scalar_one_or_none()
    
    if not device:
        raise_not_found("Device", device_id)
    
    # Update fields
    update_data = device_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(device, field, value)
    
    device.updated_at = datetime.utcnow() # type: ignore
    
    await db.commit()
    await db.refresh(device)
    
    return device


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    device_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a device."""
    result = await db.execute(
        select(Device).where(Device.id == device_id)
    )
    device = result.scalar_one_or_none()
    
    if not device:
        raise_not_found("Device", device_id)
    
    await db.delete(device)
    await db.commit()
    
    return None


@router.post("/{device_id}/ping")
async def ping_device(
    device_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Ping a device to check connectivity."""
    from services.monitoring import DeviceMonitor
    
    result = await db.execute(
        select(Device).where(Device.id == device_id)
    )
    device = result.scalar_one_or_none()
    
    if not device:
        raise_not_found("Device", device_id)
    
    monitor = DeviceMonitor(db)
    ping_result = await monitor.check_device(device)
    
    await db.commit()
    
    return ping_result


@router.get("/{device_id}/ports")
async def get_device_ports(
    device_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get all ports for a device."""
    from models.port import Port
    
    result = await db.execute(
        select(Device).where(Device.id == device_id)
    )
    device = result.scalar_one_or_none()
    
    if not device:
        raise_not_found("Device", device_id)
    
    result = await db.execute(
        select(Port).where(Port.device_id == device_id).order_by(Port.port_number)
    )
    ports = result.scalars().all()
    
    return ports


@router.get("/{device_id}/links")
async def get_device_links(
    device_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get all links connected to a device."""
    from models.link import Link
    
    result = await db.execute(
        select(Device).where(Device.id == device_id)
    )
    device = result.scalar_one_or_none()
    
    if not device:
        raise_not_found("Device", device_id)
    
    result = await db.execute(
        select(Link).where(
            or_(
                Link.source_device_id == device_id,
                Link.target_device_id == device_id
            )
        )
    )
    links = result.scalars().all()
    
    return links


@router.get("/{device_id}/events")
async def get_device_events(
    device_id: str,
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=500)
):
    """Get recent events for a device."""
    from models.event import Event
    
    result = await db.execute(
        select(Device).where(Device.id == device_id)
    )
    device = result.scalar_one_or_none()
    
    if not device:
        raise_not_found("Device", device_id)
    
    result = await db.execute(
        select(Event)
        .where(Event.device_id == device_id)
        .order_by(Event.created_at.desc())
        .limit(limit)
    )
    events = result.scalars().all()
    
    return events