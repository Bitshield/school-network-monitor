"""
Cable health monitoring endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from api.deps import get_db, Pagination
from models.cable_health import CableHealthMetrics, CableHealthStatusEnum
from models.link import Link
from schemas.cable_health import (
    CableHealthCreate,
    CableHealthUpdate,
    CableHealthResponse,
    CableHealthDetailResponse,
    CableHealthTestRequest,
    CableHealthTestResult
)
from services.cable_health import CableHealthService
from core.exceptions import raise_not_found

router = APIRouter()


@router.get("/", response_model=List[CableHealthResponse])
async def get_cable_health_metrics(
    db: AsyncSession = Depends(get_db),
    pagination: Pagination = Depends(),
    link_id: Optional[str] = None,
    status: Optional[CableHealthStatusEnum] = None,
):
    """Get all cable health metrics with pagination and filtering."""
    query = select(CableHealthMetrics)
    
    if link_id:
        query = query.where(CableHealthMetrics.link_id == link_id)
    
    if status:
        query = query.where(CableHealthMetrics.status == status)
    
    query = query.order_by(CableHealthMetrics.measured_at.desc())
    query = query.offset(pagination.skip).limit(pagination.limit)
    
    result = await db.execute(query)
    metrics = result.scalars().all()
    
    return metrics


@router.get("/unhealthy")
async def get_unhealthy_cables(
    db: AsyncSession = Depends(get_db),
    threshold: float = Query(70.0, ge=0, le=100)
):
    """Get cables with health score below threshold."""
    service = CableHealthService(db)
    unhealthy = await service.get_unhealthy_links(threshold_score=threshold)
    
    return {
        "threshold": threshold,
        "count": len(unhealthy),
        "cables": unhealthy
    }


@router.get("/{metric_id}", response_model=CableHealthDetailResponse)
async def get_cable_health_metric(
    metric_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific cable health metric by ID."""
    result = await db.execute(
        select(CableHealthMetrics).where(CableHealthMetrics.id == metric_id)
    )
    metric = result.scalar_one_or_none()
    
    if not metric:
        raise_not_found("Cable health metric", metric_id)
    
    return metric


@router.post("/test", response_model=CableHealthTestResult)
async def test_cable_health(
    test_request: CableHealthTestRequest,
    db: AsyncSession = Depends(get_db)
):
    """Run a cable health test on a link."""
    # Get the link
    result = await db.execute(
        select(Link).where(Link.id == test_request.link_id)
    )
    link = result.scalar_one_or_none()
    
    if not link:
        raise_not_found("Link", test_request.link_id)
    
    # Run the test
    service = CableHealthService(db)
    test_result = await service.test_link_health(link)
    
    # Save the results
    if test_result.get("test_results"):
        await service.create_health_metric(
            test_request.link_id,
            test_result["test_results"]
        )
        await db.commit()
    
    return {
        "link_id": test_request.link_id,
        "test_passed": test_result.get("test_results", {}).get("is_reachable", False),
        "status": test_result.get("test_results", {}).get("status", CableHealthStatusEnum.UNKNOWN),
        "signal_quality": test_result.get("test_results", {}).get("health_score"),
        "issues_found": [],
        "recommendations": test_result.get("recommendations", []),
        "test_duration": 0.0,
        "tested_at": test_result.get("timestamp")
    }


@router.get("/link/{link_id}/history")
async def get_link_health_history(
    link_id: str,
    hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db)
):
    """Get health history for a specific link."""
    # Verify link exists
    result = await db.execute(
        select(Link).where(Link.id == link_id)
    )
    link = result.scalar_one_or_none()
    
    if not link:
        raise_not_found("Link", link_id)
    
    service = CableHealthService(db)
    history = await service.get_link_history(link_id, hours=hours)
    
    return {
        "link_id": link_id,
        "time_range_hours": hours,
        "count": len(history),
        "metrics": history
    }


@router.get("/link/{link_id}/latest", response_model=CableHealthResponse)
async def get_link_latest_health(
    link_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get the latest health metric for a link."""
    result = await db.execute(
        select(CableHealthMetrics)
        .where(CableHealthMetrics.link_id == link_id)
        .order_by(CableHealthMetrics.measured_at.desc())
        .limit(1)
    )
    metric = result.scalar_one_or_none()
    
    if not metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No health metrics found for link {link_id}"
        )
    
    return metric


@router.post("/", response_model=CableHealthResponse, status_code=status.HTTP_201_CREATED)
async def create_cable_health_metric(
    metric_data: CableHealthCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new cable health metric."""
    import uuid
    from datetime import datetime
    
    # Verify link exists
    result = await db.execute(
        select(Link).where(Link.id == metric_data.link_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Link {metric_data.link_id} not found"
        )
    
    metric = CableHealthMetrics(
        id=str(uuid.uuid4()),
        **metric_data.model_dump(),
        test_date=datetime.utcnow(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        measured_at=datetime.utcnow()
    )
    
    db.add(metric)
    await db.commit()
    await db.refresh(metric)
    
    return metric


@router.delete("/{metric_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cable_health_metric(
    metric_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a cable health metric."""
    result = await db.execute(
        select(CableHealthMetrics).where(CableHealthMetrics.id == metric_id)
    )
    metric = result.scalar_one_or_none()
    
    if not metric:
        raise_not_found("Cable health metric", metric_id)
    
    await db.delete(metric)
    await db.commit()
    
    return None