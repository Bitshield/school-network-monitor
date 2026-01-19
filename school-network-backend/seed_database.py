"""
Database seeding script to add initial test data.
Run this to populate your database with sample devices for testing.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import async_session
from models.device import Device, DeviceTypeEnum, DeviceStatusEnum
from datetime import datetime
import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def seed_database():
    """Seed database with initial test data."""
    
    logger.info("Starting database seeding...")
    
    async with async_session() as db:
        try:
            # Check if devices already exist
            from sqlalchemy import select
            result = await db.execute(select(Device))
            existing = result.scalars().all()
            
            if existing:
                logger.info(f"Database already contains {len(existing)} devices")
                response = input("Do you want to add more test devices? (y/N): ")
                if response.lower() != 'y':
                    logger.info("Seeding cancelled")
                    return
            
            # Sample devices
            devices = [
                {
                    "id": str(uuid.uuid4()),
                    "name": "Core Router 1",
                    "device_type": DeviceTypeEnum.ROUTER,
                    "ip": "192.168.1.1",
                    "mac": "00:1A:2B:3C:4D:01",
                    "hostname": "core-router-01",
                    "location": "Server Room A",
                    "description": "Main core router",
                    "status": DeviceStatusEnum.UP,
                    "last_seen": datetime.utcnow(),
                    "is_monitored": True,
                    "vlan_id": 1,
                    "snmp_enabled": True,
                    "snmp_community": "public",
                    "position_x": 400.0,
                    "position_y": 100.0,
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Core Switch 1",
                    "device_type": DeviceTypeEnum.SWITCH,
                    "ip": "192.168.1.2",
                    "mac": "00:1A:2B:3C:4D:02",
                    "hostname": "core-switch-01",
                    "location": "Server Room A",
                    "description": "Main distribution switch",
                    "status": DeviceStatusEnum.UP,
                    "last_seen": datetime.utcnow(),
                    "is_monitored": True,
                    "vlan_id": 1,
                    "snmp_enabled": True,
                    "position_x": 400.0,
                    "position_y": 250.0,
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Access Switch 1",
                    "device_type": DeviceTypeEnum.SWITCH,
                    "ip": "192.168.1.10",
                    "mac": "00:1A:2B:3C:4D:03",
                    "hostname": "access-switch-01",
                    "location": "Floor 1 - East Wing",
                    "description": "Access layer switch",
                    "status": DeviceStatusEnum.UP,
                    "last_seen": datetime.utcnow(),
                    "is_monitored": True,
                    "vlan_id": 10,
                    "snmp_enabled": True,
                    "position_x": 250.0,
                    "position_y": 400.0,
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Access Switch 2",
                    "device_type": DeviceTypeEnum.SWITCH,
                    "ip": "192.168.1.11",
                    "mac": "00:1A:2B:3C:4D:04",
                    "hostname": "access-switch-02",
                    "location": "Floor 1 - West Wing",
                    "description": "Access layer switch",
                    "status": DeviceStatusEnum.UP,
                    "last_seen": datetime.utcnow(),
                    "is_monitored": True,
                    "vlan_id": 20,
                    "snmp_enabled": True,
                    "position_x": 550.0,
                    "position_y": 400.0,
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Server 1",
                    "device_type": DeviceTypeEnum.SERVER,
                    "ip": "192.168.1.50",
                    "mac": "00:1A:2B:3C:4D:05",
                    "hostname": "srv-01",
                    "location": "Server Room A",
                    "description": "Application server",
                    "status": DeviceStatusEnum.UP,
                    "last_seen": datetime.utcnow(),
                    "is_monitored": True,
                    "vlan_id": 1,
                    "snmp_enabled": False,
                    "position_x": 600.0,
                    "position_y": 250.0,
                },
            ]
            
            # Add devices
            for device_data in devices:
                device = Device(**device_data, created_at=datetime.utcnow(), updated_at=datetime.utcnow())
                db.add(device)
                logger.info(f"Added device: {device_data['name']}")
            
            # Commit
            await db.commit()
            
            logger.info(f"✅ Successfully seeded {len(devices)} devices")
            logger.info("Database seeding complete!")
            
        except Exception as e:
            logger.error(f"❌ Seeding failed: {e}", exc_info=True)
            await db.rollback()
            raise


if __name__ == "__main__":
    print("=" * 60)
    print("Database Seeding Script")
    print("=" * 60)
    print()
    
    asyncio.run(seed_database())