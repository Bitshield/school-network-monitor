"""
Network discovery service.
"""

import asyncio
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from scapy.all import ARP, Ether, srp, conf # type: ignore
from icmplib import async_ping
import logging

logger = logging.getLogger(__name__)


class NetworkDiscovery:
    """Real network device discovery via ARP and ICMP."""

    def __init__(self, timeout: int = 3, retry_count: int = 2):
        """
        Initialize network discovery.
        
        Args:
            timeout: Timeout in seconds for network operations
            retry_count: Number of retry attempts for ARP
        """
        self.timeout = timeout
        self.retry_count = retry_count
        conf.verb = 0  # Scapy quiet mode

    async def arp_scan(self, network_range: str) -> List[Dict]:
        """
        Scan network using ARP requests.
        
        Args:
            network_range: Network range in CIDR notation (e.g., "192.168.1.0/24")
            
        Returns:
            List of discovered devices with IP, MAC, and response time
        """
        devices = []
        
        try:
            logger.info(f"Starting ARP scan on {network_range}")
            
            # Create ARP request packet
            arp_request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=network_range)
            
            # Send requests and collect responses
            # Run in executor to avoid blocking async loop
            loop = asyncio.get_event_loop()
            answered, _ = await loop.run_in_executor(
                None,
                lambda: srp(
                    arp_request,
                    timeout=self.timeout,
                    verbose=False,
                    retry=self.retry_count
                )
            )
            
            for send, recv in answered:
                device_info = {
                    "ip": recv.psrc,
                    "mac": recv.hwsrc,
                    "method": "ARP",
                    "response_time_ms": float((recv.time - send.sent_time) * 1000), # type: ignore
                    "discovered_at": datetime.utcnow(),
                }
                devices.append(device_info)
                logger.debug(f"ARP discovered: {recv.psrc} ({recv.hwsrc})")
            
            logger.info(f"ARP scan complete: found {len(devices)} devices")
        
        except Exception as e:
            logger.error(f"ARP scan failed: {e}")
        
        return devices

    async def icmp_ping(self, ip: str, count: int = 1) -> Optional[Dict]:
        """
        Ping single IP address using ICMP.
        
        Args:
            ip: IP address to ping
            count: Number of ping packets
            
        Returns:
            Dictionary with ping results or None if failed
        """
        try:
            host = await async_ping(ip, count=count, timeout=self.timeout)
            return {
                "ip": ip,
                "is_alive": host.is_alive,
                "latency_ms": host.avg_rtt if host.is_alive else None,
                "min_rtt": host.min_rtt if host.is_alive else None,
                "max_rtt": host.max_rtt if host.is_alive else None,
                "packet_loss": host.packet_loss if host.is_alive else 1.0,
                "method": "ICMP",
                "checked_at": datetime.utcnow(),
            }
        except Exception as e:
            logger.warning(f"Ping failed for {ip}: {e}")
            return {
                "ip": ip,
                "is_alive": False,
                "method": "ICMP",
                "error": str(e),
                "checked_at": datetime.utcnow(),
            }

    async def batch_ping(self, ips: List[str]) -> List[Dict]:
        """
        Ping multiple IPs concurrently.
        
        Args:
            ips: List of IP addresses
            
        Returns:
            List of ping results
        """
        tasks = [self.icmp_ping(ip) for ip in ips]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_results = []
        for result in results:
            if isinstance(result, dict):
                valid_results.append(result)
            else:
                logger.error(f"Ping task failed: {result}")
        
        return valid_results

    def classify_device_type(self, mac: str, hostname: Optional[str] = None) -> str:
        """
        Attempt to classify device type based on MAC OUI and hostname.
        
        Args:
            mac: MAC address
            hostname: Optional hostname
            
        Returns:
            Device type string (ROUTER, SWITCH, PC, etc.)
        """
        # MAC OUI (Organizationally Unique Identifier) prefixes
        mac_prefixes = {
            "00:0A:95": "ROUTER",       # Cisco
            "00:1A:2F": "SWITCH",       # Cisco
            "00:1B:D4": "SWITCH",       # Cisco
            "00:24:C4": "SWITCH",       # HP
            "00:22:55": "SWITCH",       # 3COM
            "BC:52:B7": "ROUTER",       # Netgear
            "54:E6:FC": "ROUTER",       # ASUS
            "00:21:6A": "ROUTER",       # Tenda
            "00:50:56": "SERVER",       # VMware
            "00:1C:42": "SERVER",       # Parallels
            "08:00:27": "PC",           # VirtualBox
        }
        
        # Check MAC prefix
        mac_upper = mac.upper()
        for prefix, device_type in mac_prefixes.items():
            if mac_upper.startswith(prefix):
                logger.debug(f"Classified {mac} as {device_type} by MAC OUI")
                return device_type
        
        # Check hostname patterns if available
        if hostname:
            hostname_lower = hostname.lower()
            if any(x in hostname_lower for x in ['router', 'rt', 'gw', 'gateway']):
                return "ROUTER"
            elif any(x in hostname_lower for x in ['switch', 'sw']):
                return "SWITCH"
            elif any(x in hostname_lower for x in ['server', 'srv']):
                return "SERVER"
            elif any(x in hostname_lower for x in ['ap', 'access-point', 'wifi']):
                return "AP"
            elif any(x in hostname_lower for x in ['printer', 'print']):
                return "PRINTER"
            elif any(x in hostname_lower for x in ['camera', 'cam', 'ipc']):
                return "CAMERA"
        
        # Default classification
        return "UNKNOWN"

    async def scan_network(
        self,
        network_range: str = "192.168.1.0/24",
        use_ping: bool = True,
    ) -> List[Dict]:
        """
        Full network discovery scan combining ARP and optionally ICMP.
        
        Args:
            network_range: Network range in CIDR notation
            use_ping: Whether to also ping each discovered device
            
        Returns:
            List of discovered devices with comprehensive information
        """
        logger.info(f"Starting network scan: {network_range}")
        
        # Step 1: ARP scan
        devices = await self.arp_scan(network_range)
        
        if not devices:
            logger.warning("No devices found via ARP scan")
            return []
        
        # Step 2: Ping verification (optional)
        if use_ping:
            logger.info(f"Verifying {len(devices)} devices with ICMP ping")
            ips = [d["ip"] for d in devices]
            ping_results = await self.batch_ping(ips)
            
            # Merge ping results with ARP data
            ping_dict = {p["ip"]: p for p in ping_results}
            for device in devices:
                ping_data = ping_dict.get(device["ip"], {})
                device.update({
                    "is_alive": ping_data.get("is_alive", False),
                    "latency_ms": ping_data.get("latency_ms", 0),
                    "packet_loss": ping_data.get("packet_loss", 1.0),
                })
        
        # Step 3: Classify device types
        for device in devices:
            device["device_type"] = self.classify_device_type(
                device["mac"],
                device.get("hostname")
            )
            device["status"] = "UP" if device.get("is_alive", True) else "DOWN"
        
        logger.info(f"Network scan complete: found {len(devices)} devices")
        return devices

    async def scan_single_device(self, ip: str) -> Optional[Dict]:
        """
        Scan single device by IP.
        
        Args:
            ip: IP address to scan
            
        Returns:
            Device information dictionary or None
        """
        ping_result = await self.icmp_ping(ip)
        if not ping_result or not ping_result.get("is_alive"):
            return None
        
        return {
            **ping_result,
            "device_type": "UNKNOWN",
            "status": "UP",
            "mac": None,  # ARP would be needed for MAC
        }


class DiscoveryService:
    """High-level discovery service with database integration."""

    def __init__(self, db: AsyncSession):
        """
        Initialize discovery service.
        
        Args:
            db: Async database session
        """
        self.db = db
        self.discovery = NetworkDiscovery()

    async def discover_and_save(
        self,
        network_range: str = "192.168.1.0/24"
    ) -> Dict:
        """
        Discover devices and save to database.
        
        Args:
            network_range: Network range to scan
            
        Returns:
            Summary of discovery results
        """
        from models.device import Device, DeviceTypeEnum, DeviceStatusEnum
        from sqlalchemy import select
        
        # Run discovery
        discovered = await self.discovery.scan_network(network_range)
        
        new_devices = 0
        updated_devices = 0
        errors = []
        
        for device_info in discovered:
            try:
                # Check if device exists
                result = await self.db.execute(
                    select(Device).where(Device.ip == device_info["ip"])
                )
                existing_device = result.scalar_one_or_none()
                
                if existing_device:
                    # Update existing device
                    existing_device.status = DeviceStatusEnum[device_info["status"]] # type: ignore
                    existing_device.last_seen = datetime.utcnow() # type: ignore
                    if device_info.get("mac"):
                        existing_device.mac = device_info["mac"]
                    updated_devices += 1
                else:
                    # Create new device
                    new_device = Device(
                        id=f"dev-{device_info['ip'].replace('.', '-')}",
                        name=f"Device {device_info['ip']}",
                        device_type=DeviceTypeEnum[device_info["device_type"]],
                        ip=device_info["ip"],
                        mac=device_info.get("mac"),
                        status=DeviceStatusEnum[device_info["status"]],
                        last_seen=datetime.utcnow(),
                        is_monitored=True,
                    )
                    self.db.add(new_device)
                    new_devices += 1
                
            except Exception as e:
                logger.error(f"Failed to save device {device_info.get('ip')}: {e}")
                errors.append(str(e))
        
        await self.db.commit()
        
        return {
            "network_range": network_range,
            "total_discovered": len(discovered),
            "new_devices": new_devices,
            "updated_devices": updated_devices,
            "errors": errors,
            "timestamp": datetime.utcnow(),
        }