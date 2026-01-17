"""
Statistics and analytics endpoints.
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from api.deps import get_db
from models.device import Device, DeviceStatusEnum, DeviceTypeEnum
from models.link import Link, LinkStatusEnum
from models.port import Port, PortStatusEnum
from models.event import Event, EventSeverityEnum, EventTypeEnum

router = APIRouter()


@router.get("/overview")
async def get_statistics_overview(
    db: AsyncSession = Depends(get_db)
):
    """Get overall network statistics."""
    # Device counts
    total_devices = await db.execute(select(func.count(Device.id)))
    devices_up = await db.execute(
        select(func.count(Device.id)).where(Device.status == DeviceStatusEnum.UP)
    )
    devices_down = await db.execute(
        select(func.count(Device.id)).where(Device.status == DeviceStatusEnum.DOWN)
    )
    monitored_devices = await db.execute(
        select(func.count(Device.id)).where(Device.is_monitored == True)
    )
    
    # Device types
    device_types = await db.execute(
        select(Device.device_type, func.count(Device.id))
        .group_by(Device.device_type)
    )
    
    # Link counts
    total_links = await db.execute(select(func.count(Link.id)))
    links_up = await db.execute(
        select(func.count(Link.id)).where(Link.status == LinkStatusEnum.UP)
    )
    links_degraded = await db.execute(
        select(func.count(Link.id)).where(Link.status == LinkStatusEnum.DEGRADED)
    )
    
    # Port counts
    total_ports = await db.execute(select(func.count(Port.id)))
    ports_up = await db.execute(
        select(func.count(Port.id)).where(Port.status == PortStatusEnum.UP)
    )
    
    # Event counts (last 24h)
    since = datetime.utcnow() - timedelta(hours=24)
    events_24h = await db.execute(
        select(func.count(Event.id)).where(Event.created_at >= since)
    )
    critical_events = await db.execute(
        select(func.count(Event.id)).where(
            (Event.severity == EventSeverityEnum.CRITICAL) &
            (Event.created_at >= since)
        )
    )
    
    return {
        "devices": {
            "total": total_devices.scalar_one(),
            "up": devices_up.scalar_one(),
            "down": devices_down.scalar_one(),
            "monitored": monitored_devices.scalar_one(),
            "by_type": {dt: count for dt, count in device_types.all()}
        },
        "links": {
            "total": total_links.scalar_one(),
            "up": links_up.scalar_one(),
            "degraded": links_degraded.scalar_one(),
        },
        "ports": {
            "total": total_ports.scalar_one(),
            "up": ports_up.scalar_one(),
        },
        "events": {
            "last_24h": events_24h.scalar_one(),
            "critical_24h": critical_events.scalar_one(),
        }
    }


@router.get("/devices/by-type")
async def get_devices_by_type(
    db: AsyncSession = Depends(get_db)
):
    """Get device count grouped by type."""
    result = await db.execute(
        select(Device.device_type, func.count(Device.id))
        .group_by(Device.device_type)
        .order_by(func.count(Device.id).desc())
    )
    
    return {
        "by_type": {device_type.value: count for device_type, count in result.all()}
    }


@router.get("/devices/by-status")
async def get_devices_by_status(
    db: AsyncSession = Depends(get_db)
):
    """Get device count grouped by status."""
    result = await db.execute(
        select(Device.status, func.count(Device.id))
        .group_by(Device.status)
    )
    
    return {
        "by_status": {status.value: count for status, count in result.all()}
    }


@router.get("/events/timeline")
async def get_events_timeline(
    hours: int = Query(default=24, ge=1, le=168),
    db: AsyncSession = Depends(get_db)
):
    """Get event timeline for the last N hours."""
    since = datetime.utcnow() - timedelta(hours=hours)
    
    # Events by severity over time
    result = await db.execute(
        select(Event.severity, func.count(Event.id))
        .where(Event.created_at >= since)
        .group_by(Event.severity)
    )
    by_severity = {sev.value: count for sev, count in result.all()}
    
    # Events by type
    result = await db.execute(
        select(Event.event_type, func.count(Event.id))
        .where(Event.created_at >= since)
        .group_by(Event.event_type)
        .order_by(func.count(Event.id).desc())
        .limit(10)
    )
    by_type = {etype.value: count for etype, count in result.all()}
    
    return {
        "time_range_hours": hours,
        "by_severity": by_severity,
        "top_event_types": by_type
    }


@router.get("/network-health-score")
async def get_network_health_score(
    db: AsyncSession = Depends(get_db)
):
    """Calculate overall network health score."""
    # Get device health
    total_devices = await db.execute(select(func.count(Device.id)))
    devices_up = await db.execute(
        select(func.count(Device.id)).where(Device.status == DeviceStatusEnum.UP)
    )
    
    total_dev = total_devices.scalar_one()
    up_dev = devices_up.scalar_one()
    device_health = (up_dev / total_dev * 100) if total_dev > 0 else 0
    
    # Get link health
    total_links = await db.execute(select(func.count(Link.id)))
    links_up = await db.execute(
        select(func.count(Link.id)).where(Link.status == LinkStatusEnum.UP)
    )
    
    total_lnk = total_links.scalar_one()
    up_lnk = links_up.scalar_one()
    link_health = (up_lnk / total_lnk * 100) if total_lnk > 0 else 0
    
    # Get event severity impact
    since = datetime.utcnow() - timedelta(hours=1)
    critical_events = await db.execute(
        select(func.count(Event.id)).where(
            (Event.severity == EventSeverityEnum.CRITICAL) &
            (Event.created_at >= since) &
            (Event.acknowledged == False)
        )
    )
    crit_count = critical_events.scalar_one()
    event_impact = max(0, 100 - (crit_count * 10))  # Each critical event reduces score by 10
    
    # Calculate overall score (weighted average)
    overall_score = (device_health * 0.4 + link_health * 0.4 + event_impact * 0.2)
    
    # Determine health status
    if overall_score >= 90:
        status = "EXCELLENT"
    elif overall_score >= 75:
        status = "GOOD"
    elif overall_score >= 60:
        status = "FAIR"
    elif overall_score >= 40:
        status = "POOR"
    else:
        status = "CRITICAL"
    
    return {
        "overall_score": round(overall_score, 2),
        "status": status,
        "components": {
            "device_health": round(device_health, 2),
            "link_health": round(link_health, 2),
            "event_impact": round(event_impact, 2)
        },
        "metrics": {
            "devices_up": up_dev,
            "total_devices": total_dev,
            "links_up": up_lnk,
            "total_links": total_lnk,
            "critical_events_1h": crit_count
        }
    }


@router.get("/traffic-summary")
async def get_traffic_summary(
    db: AsyncSession = Depends(get_db)
):
    """Get network traffic summary."""
    # Sum all port traffic
    result = await db.execute(
        select(
            func.sum(Port.rx_bytes),
            func.sum(Port.tx_bytes),
            func.sum(Port.rx_packets),
            func.sum(Port.tx_packets),
            func.sum(Port.rx_errors),
            func.sum(Port.tx_errors)
        )
    )
    
    row = result.one()
    rx_bytes, tx_bytes, rx_packets, tx_packets, rx_errors, tx_errors = row
    
    return {
        "total_rx_bytes": rx_bytes or 0,
        "total_tx_bytes": tx_bytes or 0,
        "total_rx_packets": rx_packets or 0,
        "total_tx_packets": tx_packets or 0,
        "total_rx_errors": rx_errors or 0,
        "total_tx_errors": tx_errors or 0,
        "total_traffic_bytes": (rx_bytes or 0) + (tx_bytes or 0)
    }