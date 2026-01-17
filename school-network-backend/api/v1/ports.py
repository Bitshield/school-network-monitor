"""
Port management endpoints.
"""

from typing import List, Optional, cast

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from api.deps import get_db, Pagination
from models.port import Port, PortStatusEnum
from schemas.port import PortCreate, PortUpdate, PortResponse, PortDetailResponse
from core.exceptions import raise_not_found


router = APIRouter()


@router.get("/", response_model=List[PortResponse])
async def get_ports(
    db: AsyncSession = Depends(get_db),
    pagination: Pagination = Depends(),
    device_id: Optional[str] = None,
    status: Optional[PortStatusEnum] = None,
):
    """Get all ports with pagination and filtering."""
    query = select(Port)

    if device_id:
        query = query.where(Port.device_id == device_id)

    if status:
        query = query.where(Port.status == status)

    query = query.order_by(Port.device_id, Port.port_number)
    query = query.offset(pagination.skip).limit(pagination.limit)

    result = await db.execute(query)
    ports: List[Port] = result.scalars().all() # type: ignore

    return ports


@router.get("/{port_id}", response_model=PortDetailResponse)
async def get_port(
    port_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific port by ID."""
    result = await db.execute(
        select(Port).where(Port.id == port_id)
    )
    port = result.scalar_one_or_none()

    if port is None:
        raise_not_found("Port", port_id)

    return cast(Port, port)


@router.post("/", response_model=PortResponse, status_code=status.HTTP_201_CREATED)
async def create_port(
    port_data: PortCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new port."""
    import uuid
    from datetime import datetime
    from models.device import Device

    # Verify device exists
    result = await db.execute(
        select(Device).where(Device.id == port_data.device_id)
    )
    device = result.scalar_one_or_none()
    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device {port_data.device_id} not found",
        )

    port = Port(
        id=str(uuid.uuid4()),
        **port_data.model_dump(),
        status=PortStatusEnum.UNKNOWN,
        is_up=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        last_seen=datetime.utcnow(),
        last_check=datetime.utcnow(),
    )

    db.add(port)
    await db.commit()
    await db.refresh(port)

    return port


@router.put("/{port_id}", response_model=PortResponse)
async def update_port(
    port_id: str,
    port_data: PortUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a port."""
    from datetime import datetime

    result = await db.execute(
        select(Port).where(Port.id == port_id)
    )
    port = result.scalar_one_or_none()

    if port is None:
        raise_not_found("Port", port_id)

    port = cast(Port, port)

    update_data = port_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(port, field, value)

    port.updated_at = datetime.utcnow() # type: ignore

    await db.commit()
    await db.refresh(port)

    return port


@router.delete("/{port_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_port(
    port_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a port."""
    result = await db.execute(
        select(Port).where(Port.id == port_id)
    )
    port = result.scalar_one_or_none()

    if port is None:
        raise_not_found("Port", port_id)

    port = cast(Port, port)

    await db.delete(port)
    await db.commit()

    return None


@router.get("/{port_id}/statistics")
async def get_port_statistics(
    port_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get statistics for a port."""
    result = await db.execute(
        select(Port).where(Port.id == port_id)
    )
    port = result.scalar_one_or_none()

    if port is None:
        raise_not_found("Port", port_id)

    port = cast(Port, port)

    return {
        "port_id": port.id,
        "device_id": port.device_id,
        "port_name": port.port_name,
        "status": port.status,
        "statistics": {
            "rx_bytes": port.rx_bytes,
            "tx_bytes": port.tx_bytes,
            "rx_packets": port.rx_packets,
            "tx_packets": port.tx_packets,
            "rx_errors": port.rx_errors,
            "tx_errors": port.tx_errors,
            "rx_dropped": port.rx_dropped,
            "tx_dropped": port.tx_dropped,
            "crc_errors": port.crc_errors,
            "frame_errors": port.frame_errors,
            "collision_count": port.collision_count,
        },
        "last_check": port.last_check,
    }
