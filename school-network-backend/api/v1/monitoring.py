"""
Network monitoring endpoints.
"""

from typing import Optional
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_db
from services.monitoring import MonitoringService

router = APIRouter()


@router.get("/status")
async def get_monitoring_status(
    db: AsyncSession = Depends(get_db)
):
    """Get current monitoring service status."""
    service = MonitoringService(db)
    status = await service.get_monitoring_status()
    
    return status


@router.post("/run-cycle")
async def run_monitoring_cycle(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Manually trigger a monitoring cycle."""
    service = MonitoringService(db)
    
    # Run in background
    background_tasks.add_task(service.run_monitoring_cycle)
    
    return {
        "message": "Monitoring cycle started in background",
        "status": "running"
    }


@router.post("/devices/check-all")
async def check_all_devices(
    db: AsyncSession = Depends(get_db)
):
    """Check status of all monitored devices."""
    from services.monitoring import DeviceMonitor
    
    monitor = DeviceMonitor(db)
    results = await monitor.check_all_monitored_devices()
    
    return results


@router.post("/links/check-all")
async def check_all_links(
    db: AsyncSession = Depends(get_db)
):
    """Check health of all links."""
    from services.monitoring import LinkMonitor
    
    monitor = LinkMonitor(db)
    results = await monitor.check_all_links()
    
    return results


@router.get("/health-summary")
async def get_health_summary(
    db: AsyncSession = Depends(get_db)
):
    """Get overall network health summary."""
    from models.device import Device, DeviceStatusEnum
    from models.link import Link, LinkStatusEnum
    from models.event import Event, EventSeverityEnum
    from sqlalchemy import select, func
    from datetime import datetime, timedelta
    
    # Device statistics
    device_total = await db.execute(select(func.count(Device.id)))
    device_up = await db.execute(
        select(func.count(Device.id)).where(Device.status == DeviceStatusEnum.UP)
    )
    device_down = await db.execute(
        select(func.count(Device.id)).where(Device.status == DeviceStatusEnum.DOWN)
    )
    
    # Link statistics
    link_total = await db.execute(select(func.count(Link.id)))
    link_up = await db.execute(
        select(func.count(Link.id)).where(Link.status == LinkStatusEnum.UP)
    )
    link_degraded = await db.execute(
        select(func.count(Link.id)).where(Link.status == LinkStatusEnum.DEGRADED)
    )
    link_down = await db.execute(
        select(func.count(Link.id)).where(Link.status == LinkStatusEnum.DOWN)
    )
    
    # Recent critical events (last 24 hours)
    since = datetime.utcnow() - timedelta(hours=24)
    critical_events = await db.execute(
        select(func.count(Event.id)).where(
            (Event.severity == EventSeverityEnum.CRITICAL) &
            (Event.created_at >= since) &
            (Event.acknowledged == False)
        )
    )
    
    return {
        "devices": {
            "total": device_total.scalar_one(),
            "up": device_up.scalar_one(),
            "down": device_down.scalar_one(),
        },
        "links": {
            "total": link_total.scalar_one(),
            "up": link_up.scalar_one(),
            "degraded": link_degraded.scalar_one(),
            "down": link_down.scalar_one(),
        },
        "alerts": {
            "critical_unacknowledged": critical_events.scalar_one(),
        },
        "timestamp": datetime.utcnow()
    }