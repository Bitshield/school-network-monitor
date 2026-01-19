"""
Network monitoring service for continuous device and link health checks.
FIXED: SQLAlchemy session concurrency issues
"""

import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from models.device import Device, DeviceStatusEnum
from models.link import Link, LinkStatusEnum
from models.port import Port, PortStatusEnum
from models.event import Event, EventTypeEnum, EventSeverityEnum
from services.cable_health import CableHealthAnalyzer
from icmplib import async_ping
from database import async_session
import logging

logger = logging.getLogger(__name__)


class DeviceMonitor:
    """Monitor device availability and status."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.ping_timeout = 2
        self.ping_count = 3

    async def check_device(self, device: Device) -> Dict:
        """
        Check if device is reachable and update status.
        
        Args:
            device: Device model instance
            
        Returns:
            Check result dictionary
        """
        if not device.ip:
            return {
                "device_id": device.id,
                "status": "UNKNOWN",
                "error": "No IP address configured",
            }

        try:
            # Ping device
            host = await async_ping(
                device.ip,
                count=self.ping_count,
                timeout=self.ping_timeout
            )

            old_status = device.status
            new_status = DeviceStatusEnum.UP if host.is_alive else DeviceStatusEnum.DOWN

            # Update device
            device.status = new_status
            device.last_seen = datetime.utcnow()

            # Create event if status changed
            if old_status != new_status:
                await self._create_status_event(device, old_status, new_status)

            return {
                "device_id": device.id,
                "device_name": device.name,
                "ip": device.ip,
                "is_alive": host.is_alive,
                "status": new_status.value,
                "latency_ms": host.avg_rtt if host.is_alive else None,
                "packet_loss": host.packet_loss if host.is_alive else 1.0,
                "status_changed": old_status != new_status,
                "checked_at": datetime.utcnow(),
            }

        except Exception as e:
            logger.error(f"Failed to check device {device.id} ({device.ip}): {e}")
            device.status = DeviceStatusEnum.UNREACHABLE
            return {
                "device_id": device.id,
                "status": "ERROR",
                "error": str(e),
            }

    async def _create_status_event(
        self,
        device: Device,
        old_status: DeviceStatusEnum,
        new_status: DeviceStatusEnum
    ):
        """Create event when device status changes."""
        event_type = EventTypeEnum.DEVICE_UP if new_status == DeviceStatusEnum.UP else EventTypeEnum.DEVICE_DOWN
        severity = EventSeverityEnum.INFO if new_status == DeviceStatusEnum.UP else EventSeverityEnum.HIGH

        event = Event(
            id=f"evt-{device.id}-{datetime.utcnow().timestamp()}",
            event_type=event_type,
            severity=severity,
            device_id=device.id,
            message=f"Device {device.name} status changed from {old_status.value} to {new_status.value}",
            details={
                "old_status": old_status.value,
                "new_status": new_status.value,
                "ip": device.ip,
            },
            source="monitoring_service",
        )
        self.db.add(event)

    async def check_all_monitored_devices(self) -> Dict:
        """
        Check all devices that have monitoring enabled.
        
        Returns:
            Summary of monitoring results
        """
        # Get all monitored devices
        result = await self.db.execute(
            select(Device).where(Device.is_monitored == True)
        )
        devices = result.scalars().all()

        if not devices:
            logger.warning("No monitored devices found")
            return {
                "total_devices": 0,
                "checked": 0,
                "up": 0,
                "down": 0,
                "errors": 0,
            }

        # Check all devices concurrently
        logger.info(f"Checking {len(devices)} monitored devices")
        tasks = [self.check_device(device) for device in devices]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Commit all changes
        await self.db.commit()

        # Summarize results
        summary = {
            "total_devices": len(devices),
            "checked": 0,
            "up": 0,
            "down": 0,
            "unreachable": 0,
            "errors": 0,
            "timestamp": datetime.utcnow(),
        }

        for result in results:
            if isinstance(result, dict):
                summary["checked"] += 1
                status = result.get("status", "ERROR")
                if status == "UP":
                    summary["up"] += 1
                elif status == "DOWN":
                    summary["down"] += 1
                elif status == "UNREACHABLE":
                    summary["unreachable"] += 1
                else:
                    summary["errors"] += 1
            else:
                summary["errors"] += 1
                logger.error(f"Device check failed: {result}")

        logger.info(
            f"Monitoring complete: {summary['up']} UP, "
            f"{summary['down']} DOWN, {summary['unreachable']} UNREACHABLE, "
            f"{summary['errors']} ERRORS"
        )

        return summary


class LinkMonitor:
    """Monitor network link health and performance."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.analyzer = CableHealthAnalyzer()

    async def check_link(self, link: Link) -> Dict:
        """
        Check link health between two devices.
        
        Args:
            link: Link model instance
            
        Returns:
            Link check result
        """
        try:
            # Get source and target devices
            result = await self.db.execute(
                select(Device).where(
                    or_(
                        Device.id == link.source_device_id,
                        Device.id == link.target_device_id
                    )
                )
            )
            devices = {d.id: d for d in result.scalars().all()}

            source_device = devices.get(link.source_device_id)
            target_device = devices.get(link.target_device_id)

            if not target_device or not target_device.ip:
                return {
                    "link_id": link.id,
                    "status": "ERROR",
                    "error": "Target device IP not available",
                }

            # Test link
            test_result = await self.analyzer.test_link(target_device.ip)

            old_status = link.status
            new_status = self._map_health_to_status(test_result.get("status"))

            # Update link
            link.status = new_status # pyright: ignore[reportAttributeAccessIssue]
            link.latency = test_result.get("latency_avg_ms", 0)
            link.packet_loss = test_result.get("packet_loss_percent", 0)
            link.jitter = test_result.get("jitter_ms", 0)
            link.last_seen = datetime.utcnow() # pyright: ignore[reportAttributeAccessIssue]

            # Create event if status changed significantly
            if old_status != new_status and new_status in [LinkStatusEnum.DOWN, LinkStatusEnum.DEGRADED]: # pyright: ignore[reportGeneralTypeIssues]
                await self._create_link_event(link, old_status, new_status, test_result)

            return {
                "link_id": link.id,
                "source_device_id": link.source_device_id,
                "target_device_id": link.target_device_id,
                "status": new_status.value,
                "health_score": test_result.get("health_score", 0),
                "latency_ms": test_result.get("latency_avg_ms"),
                "packet_loss_percent": test_result.get("packet_loss_percent"),
                "jitter_ms": test_result.get("jitter_ms"),
                "status_changed": old_status != new_status,
                "checked_at": datetime.utcnow(),
            }

        except Exception as e:
            logger.error(f"Failed to check link {link.id}: {e}")
            return {
                "link_id": link.id,
                "status": "ERROR",
                "error": str(e),
            }

    def _map_health_to_status(self, health_status) -> LinkStatusEnum:
        """Map cable health status to link status."""
        from models.cable_health import CableHealthStatusEnum
        
        if health_status in [CableHealthStatusEnum.EXCELLENT, CableHealthStatusEnum.GOOD]:
            return LinkStatusEnum.UP
        elif health_status in [CableHealthStatusEnum.FAIR, CableHealthStatusEnum.POOR]:
            return LinkStatusEnum.DEGRADED
        else:
            return LinkStatusEnum.DOWN

    async def _create_link_event(
        self,
        link: Link,
        old_status: LinkStatusEnum,
        new_status: LinkStatusEnum,
        test_result: Dict
    ):
        """Create event when link status changes."""
        if new_status == LinkStatusEnum.DOWN:
            event_type = EventTypeEnum.LINK_DOWN
            severity = EventSeverityEnum.CRITICAL
        else:
            event_type = EventTypeEnum.LINK_UP if new_status == LinkStatusEnum.UP else EventTypeEnum.HIGH_LATENCY
            severity = EventSeverityEnum.MEDIUM

        event = Event(
            id=f"evt-link-{link.id}-{datetime.utcnow().timestamp()}",
            event_type=event_type,
            severity=severity,
            link_id=link.id,
            message=f"Link status changed from {old_status.value} to {new_status.value}",
            details={
                "old_status": old_status.value,
                "new_status": new_status.value,
                "health_score": test_result.get("health_score"),
                "latency_ms": test_result.get("latency_avg_ms"),
                "packet_loss_percent": test_result.get("packet_loss_percent"),
            },
            source="link_monitor",
        )
        self.db.add(event)

    async def check_all_links(self) -> Dict:
        """
        Check health of all active links.
        
        Returns:
            Summary of link monitoring results
        """
        # Get all links
        result = await self.db.execute(select(Link))
        links = result.scalars().all()

        if not links:
            logger.warning("No links found to monitor")
            return {
                "total_links": 0,
                "checked": 0,
                "up": 0,
                "degraded": 0,
                "down": 0,
                "errors": 0,
            }

        # Check all links concurrently
        logger.info(f"Checking {len(links)} links")
        tasks = [self.check_link(link) for link in links]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Commit all changes
        await self.db.commit()

        # Summarize results
        summary = {
            "total_links": len(links),
            "checked": 0,
            "up": 0,
            "degraded": 0,
            "down": 0,
            "errors": 0,
            "timestamp": datetime.utcnow(),
        }

        for result in results:
            if isinstance(result, dict):
                summary["checked"] += 1
                status = result.get("status", "ERROR")
                if status == "UP":
                    summary["up"] += 1
                elif status == "DEGRADED":
                    summary["degraded"] += 1
                elif status == "DOWN":
                    summary["down"] += 1
                else:
                    summary["errors"] += 1
            else:
                summary["errors"] += 1

        logger.info(
            f"Link monitoring complete: {summary['up']} UP, "
            f"{summary['degraded']} DEGRADED, {summary['down']} DOWN"
        )

        return summary


class PortMonitor:
    """Monitor network port status (requires SNMP)."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def check_port(self, port: Port) -> Dict:
        """
        Check port status (placeholder - requires SNMP implementation).
        
        Args:
            port: Port model instance
            
        Returns:
            Port check result
        """
        # This would typically use SNMP to query port status
        # For now, return current status
        return {
            "port_id": port.id,
            "device_id": port.device_id,
            "port_name": port.port_name,
            "status": port.status.value,
            "checked_at": datetime.utcnow(),
        }


class MonitoringService:
    """
    Unified monitoring service for devices, links, and ports.
    Designed to run as a background task.
    
    FIXED: Creates new database session for each monitoring cycle to avoid
    concurrent connection issues.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.is_running = False
        self.check_interval = 60  # seconds

    async def run_monitoring_cycle(self) -> Dict:
        """
        Run a complete monitoring cycle for all components.
        Uses separate database session to avoid concurrency issues.
        
        Returns:
            Combined monitoring results
        """
        logger.info("Starting monitoring cycle")
        start_time = datetime.utcnow()

        # Create NEW database session for this cycle
        async with async_session() as db:
            try:
                device_monitor = DeviceMonitor(db)
                link_monitor = LinkMonitor(db)

                # Run all monitors
                device_results = await device_monitor.check_all_monitored_devices()
                link_results = await link_monitor.check_all_links()

                # Commit session
                await db.commit()

            except Exception as e:
                logger.error(f"Link monitoring failed: {e}", exc_info=True)
                await db.rollback()
                link_results = {"error": str(e)}
                device_results = {"error": str(e)}

        duration = (datetime.utcnow() - start_time).total_seconds()

        result = {
            "cycle_start": start_time,
            "cycle_duration_seconds": duration,
            "devices": device_results,
            "links": link_results,
            "timestamp": datetime.utcnow(),
        }

        logger.info(f"Monitoring cycle complete in {duration:.2f}s")
        return result

    async def start_continuous_monitoring(self, interval: Optional[int] = None):
        """
        Start continuous monitoring loop.
        
        Args:
            interval: Check interval in seconds (default: 60)
        """
        if interval:
            self.check_interval = interval

        self.is_running = True
        logger.info(f"Starting continuous monitoring (interval: {self.check_interval}s)")

        while self.is_running:
            try:
                await self.run_monitoring_cycle()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Monitoring cycle error: {e}", exc_info=True)
                await asyncio.sleep(self.check_interval)

    def stop_monitoring(self):
        """Stop continuous monitoring."""
        logger.info("Stopping continuous monitoring")
        self.is_running = False

    async def get_monitoring_status(self) -> Dict:
        """
        Get current monitoring service status.
        
        Returns:
            Status dictionary
        """
        # Create new session for status check
        async with async_session() as db:
            try:
                # Get counts from database
                device_count = await db.execute(
                    select(Device).where(Device.is_monitored == True)
                )
                monitored_devices = len(device_count.scalars().all())

                link_count = await db.execute(select(Link))
                total_links = len(link_count.scalars().all())

                # Get recent events count
                recent_time = datetime.utcnow() - timedelta(hours=1)
                event_count = await db.execute(
                    select(Event).where(Event.created_at >= recent_time)
                )
                recent_events = len(event_count.scalars().all())

            except Exception as e:
                logger.error(f"Failed to get monitoring status: {e}")
                monitored_devices = 0
                total_links = 0
                recent_events = 0

        return {
            "is_running": self.is_running,
            "check_interval_seconds": self.check_interval,
            "monitored_devices": monitored_devices,
            "monitored_links": total_links,
            "recent_events_1h": recent_events,
            "timestamp": datetime.utcnow(),
        }