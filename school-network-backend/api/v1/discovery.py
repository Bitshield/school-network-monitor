"""
Network discovery endpoints.
"""

from typing import Optional
from fastapi import APIRouter, Depends, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_db
from services.discovery import NetworkDiscovery, DiscoveryService
from config import settings

router = APIRouter()


@router.post("/scan")
async def scan_network(
    network_range: str = Query(
        default=settings.DEFAULT_NETWORK_RANGE,
        description="Network range in CIDR notation"
    ),
    save_results: bool = Query(
        default=True,
        description="Save discovered devices to database"
    ),
    db: AsyncSession = Depends(get_db)
):
    """
    Scan network for devices.
    
    - **network_range**: Network range to scan (e.g., "192.168.1.0/24")
    - **save_results**: Whether to save discovered devices to database
    """
    discovery = NetworkDiscovery()
    devices = await discovery.scan_network(network_range)
    
    result = {
        "network_range": network_range,
        "devices_found": len(devices),
        "devices": devices
    }
    
    if save_results:
        service = DiscoveryService(db)
        save_result = await service.discover_and_save(network_range)
        result["save_result"] = save_result
    
    return result


@router.post("/scan-background")
async def scan_network_background(
    background_tasks: BackgroundTasks,
    network_range: str = Query(default=settings.DEFAULT_NETWORK_RANGE),
    db: AsyncSession = Depends(get_db)
):
    """Run network scan in background."""
    async def scan_task():
        service = DiscoveryService(db)
        await service.discover_and_save(network_range)
    
    background_tasks.add_task(scan_task)
    
    return {
        "message": "Network scan started in background",
        "network_range": network_range,
        "status": "running"
    }


@router.post("/scan-device/{ip}")
async def scan_single_device(
    ip: str,
    save_result: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """Scan a single device by IP address."""
    discovery = NetworkDiscovery()
    device = await discovery.scan_single_device(ip)
    
    if not device:
        return {
            "ip": ip,
            "found": False,
            "message": "Device not reachable"
        }
    
    result = {
        "ip": ip,
        "found": True,
        "device": device
    }
    
    if save_result:
        service = DiscoveryService(db)
        save_result = await service.discover_and_save(f"{ip}/32") # type: ignore
        result["save_result"] = save_result
    
    return result


@router.get("/arp-scan")
async def arp_scan(
    network_range: str = Query(default=settings.DEFAULT_NETWORK_RANGE)
):
    """Perform ARP scan on network range."""
    discovery = NetworkDiscovery()
    devices = await discovery.arp_scan(network_range)
    
    return {
        "network_range": network_range,
        "method": "ARP",
        "devices_found": len(devices),
        "devices": devices
    }


@router.post("/ping-sweep")
async def ping_sweep(
    ips: list[str]
):
    """Ping multiple IP addresses."""
    discovery = NetworkDiscovery()
    results = await discovery.batch_ping(ips)
    
    alive = [r for r in results if r.get("is_alive")]
    
    return {
        "total_ips": len(ips),
        "alive": len(alive),
        "dead": len(ips) - len(alive),
        "results": results
    }