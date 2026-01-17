"""
Link management endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from api.deps import get_db, Pagination
from models.link import Link, LinkStatusEnum
from schemas.link import LinkCreate, LinkUpdate, LinkResponse, LinkDetailResponse
from core.exceptions import raise_not_found

router = APIRouter()


@router.get("/", response_model=List[LinkResponse])
async def get_links(
    db: AsyncSession = Depends(get_db),
    pagination: Pagination = Depends(),
    status: Optional[LinkStatusEnum] = None,
    device_id: Optional[str] = None,
):
    """Get all links with pagination and filtering."""
    query = select(Link)
    
    if status:
        query = query.where(Link.status == status)
    
    if device_id:
        query = query.where(
            or_(
                Link.source_device_id == device_id,
                Link.target_device_id == device_id
            )
        )
    
    query = query.order_by(Link.created_at.desc())
    query = query.offset(pagination.skip).limit(pagination.limit)
    
    result = await db.execute(query)
    links = result.scalars().all()
    
    return links


@router.get("/{link_id}", response_model=LinkDetailResponse)
async def get_link(
    link_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific link by ID."""
    result = await db.execute(
        select(Link).where(Link.id == link_id)
    )
    link = result.scalar_one_or_none()
    
    if not link:
        raise_not_found("Link", link_id)
    
    return link


@router.post("/", response_model=LinkResponse, status_code=status.HTTP_201_CREATED)
async def create_link(
    link_data: LinkCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new link."""
    import uuid
    from datetime import datetime
    from models.device import Device
    
    # Verify devices exist
    result = await db.execute(
        select(Device).where(
            Device.id.in_([link_data.source_device_id, link_data.target_device_id])
        )
    )
    devices = result.scalars().all()
    
    if len(devices) != 2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or both devices not found"
        )
    
    # Check for duplicate link
    result = await db.execute(
        select(Link).where(
            or_(
                (Link.source_device_id == link_data.source_device_id) & 
                (Link.target_device_id == link_data.target_device_id),
                (Link.source_device_id == link_data.target_device_id) & 
                (Link.target_device_id == link_data.source_device_id)
            )
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Link already exists between these devices"
        )
    
    link = Link(
        id=str(uuid.uuid4()),
        **link_data.model_dump(),
        status=LinkStatusEnum.UNKNOWN,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        last_seen=datetime.utcnow()
    )
    
    db.add(link)
    await db.commit()
    await db.refresh(link)
    
    return link


@router.put("/{link_id}", response_model=LinkResponse)
async def update_link(
    link_id: str,
    link_data: LinkUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a link."""
    from datetime import datetime
    
    result = await db.execute(
        select(Link).where(Link.id == link_id)
    )
    link = result.scalar_one_or_none()
    
    if not link:
        raise_not_found("Link", link_id)
    
    update_data = link_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(link, field, value)
    
    link.updated_at = datetime.utcnow() # type: ignore
    
    await db.commit()
    await db.refresh(link)
    
    return link


@router.delete("/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_link(
    link_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a link."""
    result = await db.execute(
        select(Link).where(Link.id == link_id)
    )
    link = result.scalar_one_or_none()
    
    if not link:
        raise_not_found("Link", link_id)
    
    await db.delete(link)
    await db.commit()
    
    return None


@router.post("/{link_id}/test")
async def test_link(
    link_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Test link health."""
    from services.cable_health import CableHealthService
    
    result = await db.execute(
        select(Link).where(Link.id == link_id)
    )
    link = result.scalar_one_or_none()
    
    if not link:
        raise_not_found("Link", link_id)
    
    service = CableHealthService(db)
    test_result = await service.test_link_health(link)
    
    return test_result


@router.get("/{link_id}/health-history")
async def get_link_health_history(
    link_id: str,
    hours: int = 24,
    db: AsyncSession = Depends(get_db)
):
    """Get health history for a link."""
    from services.cable_health import CableHealthService
    
    result = await db.execute(
        select(Link).where(Link.id == link_id)
    )
    link = result.scalar_one_or_none()
    
    if not link:
        raise_not_found("Link", link_id)
    
    service = CableHealthService(db)
    history = await service.get_link_history(link_id, hours=hours)
    
    return history