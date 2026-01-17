"""
Event management endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from datetime import datetime, timedelta

from api.deps import get_db, Pagination
from models.event import Event, EventTypeEnum, EventSeverityEnum
from schemas.event import (
    EventCreate,
    EventUpdate,
    EventResponse,
    EventDetailResponse,
    EventFilterParams
)
from core.exceptions import raise_not_found

router = APIRouter()


@router.get("/", response_model=List[EventResponse])
async def get_events(
    db: AsyncSession = Depends(get_db),
    pagination: Pagination = Depends(),
    event_type: Optional[EventTypeEnum] = None,
    severity: Optional[EventSeverityEnum] = None,
    device_id: Optional[str] = None,
    acknowledged: Optional[bool] = None,
    resolved: Optional[bool] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
):
    """
    Get all events with pagination and filtering.
    
    - **event_type**: Filter by event type
    - **severity**: Filter by severity level
    - **device_id**: Filter by device
    - **acknowledged**: Filter by acknowledgement status
    - **resolved**: Filter by resolution status
    - **start_date**: Filter events after this date
    - **end_date**: Filter events before this date
    """
    query = select(Event)
    
    # Apply filters
    if event_type:
        query = query.where(Event.event_type == event_type)
    
    if severity:
        query = query.where(Event.severity == severity)
    
    if device_id:
        query = query.where(Event.device_id == device_id)
    
    if acknowledged is not None:
        query = query.where(Event.acknowledged == acknowledged) # type: ignore
    
    if resolved is not None:
        query = query.where(Event.resolved == resolved) # type: ignore
    
    if start_date:
        query = query.where(Event.created_at >= start_date)
    
    if end_date:
        query = query.where(Event.created_at <= end_date)
    
    # Order by most recent first
    query = query.order_by(Event.created_at.desc())
    
    # Apply pagination
    query = query.offset(pagination.skip).limit(pagination.limit)
    
    result = await db.execute(query)
    events = result.scalars().all()
    
    return events


@router.get("/unacknowledged", response_model=List[EventResponse])
async def get_unacknowledged_events(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(100, ge=1, le=500)
):
    """Get all unacknowledged events."""
    result = await db.execute(
        select(Event)
        .where(Event.acknowledged == False) # type: ignore
        .order_by(Event.severity.desc(), Event.created_at.desc())
        .limit(limit)
    )
    events = result.scalars().all()
    
    return events


@router.get("/critical", response_model=List[EventResponse])
async def get_critical_events(
    db: AsyncSession = Depends(get_db),
    hours: int = Query(24, ge=1, le=168)
):
    """Get critical events from the last N hours."""
    since = datetime.utcnow() - timedelta(hours=hours)
    
    result = await db.execute(
        select(Event)
        .where(
            and_(
                Event.severity == EventSeverityEnum.CRITICAL,
                Event.created_at >= since
            )
        )
        .order_by(Event.created_at.desc())
    )
    events = result.scalars().all()
    
    return events


@router.get("/summary")
async def get_events_summary(
    db: AsyncSession = Depends(get_db),
    hours: int = Query(24, ge=1, le=168)
):
    """Get summary statistics of events."""
    since = datetime.utcnow() - timedelta(hours=hours)
    
    # Total events
    total_result = await db.execute(
        select(func.count(Event.id)).where(Event.created_at >= since)
    )
    total = total_result.scalar_one()
    
    # By severity
    severity_result = await db.execute(
        select(Event.severity, func.count(Event.id))
        .where(Event.created_at >= since)
        .group_by(Event.severity)
    )
    by_severity = {sev: count for sev, count in severity_result.all()}
    
    # By type
    type_result = await db.execute(
        select(Event.event_type, func.count(Event.id))
        .where(Event.created_at >= since)
        .group_by(Event.event_type)
        .order_by(func.count(Event.id).desc())
        .limit(10)
    )
    by_type = {etype: count for etype, count in type_result.all()}
    
    # Unacknowledged
    unack_result = await db.execute(
        select(func.count(Event.id))
        .where(and_(Event.acknowledged == False, Event.created_at >= since)) # type: ignore
    )
    unacknowledged = unack_result.scalar_one()
    
    # Unresolved
    unres_result = await db.execute(
        select(func.count(Event.id))
        .where(and_(Event.resolved == False, Event.created_at >= since)) # type: ignore
    )
    unresolved = unres_result.scalar_one()
    
    return {
        "total_events": total,
        "unacknowledged": unacknowledged,
        "unresolved": unresolved,
        "by_severity": by_severity,
        "by_type": by_type,
        "time_range_hours": hours,
    }


@router.get("/{event_id}", response_model=EventDetailResponse)
async def get_event(
    event_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific event by ID."""
    result = await db.execute(
        select(Event).where(Event.id == event_id)
    )
    event = result.scalar_one_or_none()
    
    if not event:
        raise_not_found("Event", event_id)
    
    return event


@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_data: EventCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new event."""
    import uuid
    
    event = Event(
        id=str(uuid.uuid4()),
        **event_data.model_dump(),
        acknowledged=False,
        resolved=False,
        occurrence_count=1,
        first_occurred_at=datetime.utcnow(),
        last_occurred_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(event)
    await db.commit()
    await db.refresh(event)
    
    return event


@router.patch("/{event_id}/acknowledge")
async def acknowledge_event(
    event_id: str,
    acknowledged_by: str,
    notes: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Acknowledge an event."""
    result = await db.execute(
        select(Event).where(Event.id == event_id)
    )
    event = result.scalar_one_or_none()
    
    if not event:
        raise_not_found("Event", event_id)
    
    event.acknowledge(acknowledged_by, notes) # type: ignore
    
    await db.commit()
    await db.refresh(event)
    
    return {
        "message": "Event acknowledged successfully",
        "event_id": event_id,
        "acknowledged_by": acknowledged_by,
        "acknowledged_at": event.acknowledged_at # type: ignore
    }


@router.patch("/{event_id}/resolve")
async def resolve_event(
    event_id: str,
    resolved_by: str,
    resolution_notes: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Resolve an event."""
    result = await db.execute(
        select(Event).where(Event.id == event_id)
    )
    event = result.scalar_one_or_none()
    
    if not event:
        raise_not_found("Event", event_id)
    
    event.resolve(resolved_by, resolution_notes) # type: ignore
    
    await db.commit()
    await db.refresh(event)
    
    return {
        "message": "Event resolved successfully",
        "event_id": event_id,
        "resolved_by": resolved_by,
        "resolved_at": event.resolved_at # type: ignore
    }


@router.post("/bulk-acknowledge")
async def bulk_acknowledge_events(
    event_ids: List[str],
    acknowledged_by: str,
    notes: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Acknowledge multiple events at once."""
    result = await db.execute(
        select(Event).where(Event.id.in_(event_ids))
    )
    events = result.scalars().all()
    
    acknowledged_count = 0
    for event in events:
        if not event.acknowledged: # type: ignore
            event.acknowledge(acknowledged_by, notes) # type: ignore
            acknowledged_count += 1
    
    await db.commit()
    
    return {
        "message": f"Acknowledged {acknowledged_count} events",
        "acknowledged_count": acknowledged_count,
        "total_events": len(event_ids)
    }


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete an event."""
    result = await db.execute(
        select(Event).where(Event.id == event_id)
    )
    event = result.scalar_one_or_none()
    
    if not event:
        raise_not_found("Event", event_id)
    
    await db.delete(event)
    await db.commit()
    
    return None