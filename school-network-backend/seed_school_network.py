"""
Dynamic Network Seeding Tool
Flexible database seeding for ANY organization (schools, companies, etc.)
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
import json

# Fix Windows event loop for Python 3.12+
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from database import async_session
from models.device import Device, DeviceTypeEnum, DeviceStatusEnum
from models.link import Link, LinkStatusEnum, LinkTypeEnum
from sqlalchemy import select
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================================================
# PRESET NETWORK CONFIGURATIONS
# =============================================================================

NETWORK_PRESETS = {
    "small_school": {
        "name": "Small School (5-15 devices)",
        "devices": [
            {"name": "Main Router", "type": "ROUTER", "ip": "192.168.1.1", "location": "Server Room"},
            {"name": "Core Switch", "type": "SWITCH", "ip": "192.168.1.2", "location": "Server Room"},
            {"name": "Floor 1 Switch", "type": "SWITCH", "ip": "192.168.1.10", "location": "First Floor"},
            {"name": "Floor 2 Switch", "type": "SWITCH", "ip": "192.168.1.11", "location": "Second Floor"},
            {"name": "WiFi AP Main", "type": "AP", "ip": "192.168.1.100", "location": "Main Hall"},
            {"name": "Lab Switch", "type": "SWITCH", "ip": "192.168.1.20", "location": "Computer Lab"},
            {"name": "Office Printer", "type": "PRINTER", "ip": "192.168.1.50", "location": "Main Office"},
            {"name": "Application Server", "type": "SERVER", "ip": "192.168.1.200", "location": "Server Room"},
        ]
    },
    "medium_school": {
        "name": "Medium School (15-30 devices)",
        "devices": [
            {"name": "Main Router", "type": "ROUTER", "ip": "192.168.1.1", "location": "Server Room"},
            {"name": "Backup Router", "type": "ROUTER", "ip": "192.168.1.2", "location": "Server Room"},
            {"name": "Core Switch 1", "type": "SWITCH", "ip": "192.168.1.10", "location": "Server Room"},
            {"name": "Core Switch 2", "type": "SWITCH", "ip": "192.168.1.11", "location": "Server Room"},
            {"name": "Building A - Floor 1 Switch", "type": "SWITCH", "ip": "192.168.10.1", "location": "Building A - Floor 1"},
            {"name": "Building A - Floor 2 Switch", "type": "SWITCH", "ip": "192.168.10.2", "location": "Building A - Floor 2"},
            {"name": "Building A - Floor 3 Switch", "type": "SWITCH", "ip": "192.168.10.3", "location": "Building A - Floor 3"},
            {"name": "Building B - Floor 1 Switch", "type": "SWITCH", "ip": "192.168.20.1", "location": "Building B - Floor 1"},
            {"name": "Building B - Floor 2 Switch", "type": "SWITCH", "ip": "192.168.20.2", "location": "Building B - Floor 2"},
            {"name": "Computer Lab 1 Switch", "type": "SWITCH", "ip": "192.168.30.1", "location": "Computer Lab 1"},
            {"name": "Computer Lab 2 Switch", "type": "SWITCH", "ip": "192.168.30.2", "location": "Computer Lab 2"},
            {"name": "Library Switch", "type": "SWITCH", "ip": "192.168.40.1", "location": "Library"},
            {"name": "WiFi AP - Building A Floor 1", "type": "AP", "ip": "192.168.100.1", "location": "Building A - Floor 1"},
            {"name": "WiFi AP - Building A Floor 2", "type": "AP", "ip": "192.168.100.2", "location": "Building A - Floor 2"},
            {"name": "WiFi AP - Building B Floor 1", "type": "AP", "ip": "192.168.100.3", "location": "Building B - Floor 1"},
            {"name": "WiFi AP - Library", "type": "AP", "ip": "192.168.100.4", "location": "Library"},
            {"name": "Main File Server", "type": "SERVER", "ip": "192.168.1.100", "location": "Server Room"},
            {"name": "Backup Server", "type": "SERVER", "ip": "192.168.1.101", "location": "Server Room"},
            {"name": "Office Printer Main", "type": "PRINTER", "ip": "192.168.50.1", "location": "Main Office"},
            {"name": "Office Printer Finance", "type": "PRINTER", "ip": "192.168.50.2", "location": "Finance Office"},
            {"name": "Lab Printer 1", "type": "PRINTER", "ip": "192.168.50.3", "location": "Computer Lab 1"},
        ]
    },
    "large_enterprise": {
        "name": "Large Enterprise/University (30+ devices)",
        "devices": [
            {"name": "Core Router 1", "type": "ROUTER", "ip": "10.0.0.1", "location": "Data Center"},
            {"name": "Core Router 2", "type": "ROUTER", "ip": "10.0.0.2", "location": "Data Center"},
            {"name": "Edge Router 1", "type": "ROUTER", "ip": "10.0.0.10", "location": "Data Center"},
            {"name": "Core Switch 1", "type": "SWITCH", "ip": "10.0.1.1", "location": "Data Center"},
            {"name": "Core Switch 2", "type": "SWITCH", "ip": "10.0.1.2", "location": "Data Center"},
            {"name": "Distribution Switch - East Wing", "type": "SWITCH", "ip": "10.1.0.1", "location": "East Wing MDF"},
            {"name": "Distribution Switch - West Wing", "type": "SWITCH", "ip": "10.2.0.1", "location": "West Wing MDF"},
            {"name": "Distribution Switch - North Wing", "type": "SWITCH", "ip": "10.3.0.1", "location": "North Wing MDF"},
            {"name": "Access Switch - East Floor 1", "type": "SWITCH", "ip": "10.1.1.1", "location": "East Wing - Floor 1"},
            {"name": "Access Switch - East Floor 2", "type": "SWITCH", "ip": "10.1.2.1", "location": "East Wing - Floor 2"},
            {"name": "Access Switch - East Floor 3", "type": "SWITCH", "ip": "10.1.3.1", "location": "East Wing - Floor 3"},
            {"name": "Access Switch - West Floor 1", "type": "SWITCH", "ip": "10.2.1.1", "location": "West Wing - Floor 1"},
            {"name": "Access Switch - West Floor 2", "type": "SWITCH", "ip": "10.2.2.1", "location": "West Wing - Floor 2"},
            {"name": "Access Switch - West Floor 3", "type": "SWITCH", "ip": "10.2.3.1", "location": "West Wing - Floor 3"},
            {"name": "WiFi Controller", "type": "SERVER", "ip": "10.0.10.1", "location": "Data Center"},
            {"name": "AP - East Wing Lobby", "type": "AP", "ip": "10.100.1.1", "location": "East Wing Lobby"},
            {"name": "AP - West Wing Lobby", "type": "AP", "ip": "10.100.2.1", "location": "West Wing Lobby"},
            {"name": "AP - Conference Room A", "type": "AP", "ip": "10.100.3.1", "location": "Conference Room A"},
            {"name": "AP - Conference Room B", "type": "AP", "ip": "10.100.3.2", "location": "Conference Room B"},
            {"name": "Database Server Primary", "type": "SERVER", "ip": "10.0.20.1", "location": "Data Center"},
            {"name": "Database Server Standby", "type": "SERVER", "ip": "10.0.20.2", "location": "Data Center"},
            {"name": "Web Server 1", "type": "SERVER", "ip": "10.0.30.1", "location": "Data Center"},
            {"name": "Web Server 2", "type": "SERVER", "ip": "10.0.30.2", "location": "Data Center"},
            {"name": "Mail Server", "type": "SERVER", "ip": "10.0.40.1", "location": "Data Center"},
            {"name": "Backup Server", "type": "SERVER", "ip": "10.0.50.1", "location": "Data Center"},
        ]
    },
    "small_office": {
        "name": "Small Office (5-10 devices)",
        "devices": [
            {"name": "Office Router", "type": "ROUTER", "ip": "192.168.0.1", "location": "Network Room"},
            {"name": "Main Switch", "type": "SWITCH", "ip": "192.168.0.2", "location": "Network Room"},
            {"name": "WiFi Access Point", "type": "AP", "ip": "192.168.0.100", "location": "Office Center"},
            {"name": "Office Printer", "type": "PRINTER", "ip": "192.168.0.50", "location": "Print Room"},
            {"name": "File Server", "type": "SERVER", "ip": "192.168.0.10", "location": "Server Closet"},
        ]
    },
    "custom": {
        "name": "Custom Configuration",
        "devices": []
    }
}


# =============================================================================
# INTERACTIVE MENU
# =============================================================================

def show_menu():
    """Display interactive menu for network configuration."""
    print("\n" + "=" * 70)
    print(" " * 20 + "🌐 NETWORK CONFIGURATION WIZARD")
    print("=" * 70)
    print("\nSelect your organization type:\n")
    
    for idx, (key, preset) in enumerate(NETWORK_PRESETS.items(), 1):
        device_count = len(preset['devices']) if preset['devices'] else 0
        print(f"  [{idx}] {preset['name']}")
        if device_count > 0:
            print(f"      └─ {device_count} devices included")
    
    print("\n" + "=" * 70)
    
    while True:
        try:
            choice = input("\nEnter your choice (1-5): ").strip()
            choice_idx = int(choice) - 1
            
            if 0 <= choice_idx < len(NETWORK_PRESETS):
                preset_key = list(NETWORK_PRESETS.keys())[choice_idx]
                return preset_key
            else:
                print("❌ Invalid choice. Please select 1-5.")
        except ValueError:
            print("❌ Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\n\n⚠️  Setup cancelled by user")
            sys.exit(0)


def customize_network_details():
    """Get organization-specific details."""
    print("\n" + "=" * 70)
    print(" " * 20 + "📝 ORGANIZATION DETAILS")
    print("=" * 70)
    
    org_name = input("\nOrganization name (e.g., 'Lincoln High School'): ").strip()
    if not org_name:
        org_name = "My Organization"
    
    base_ip = input("Base IP address (e.g., '192.168.1' or '10.0.0'): ").strip()
    if not base_ip:
        base_ip = "192.168.1"
    
    # Ensure base_ip doesn't end with a dot
    base_ip = base_ip.rstrip('.')
    
    monitor_all = input("Monitor all devices? (y/n) [y]: ").strip().lower()
    monitor_all = monitor_all != 'n'
    
    return {
        "org_name": org_name,
        "base_ip": base_ip,
        "monitor_all": monitor_all
    }


def add_custom_device():
    """Interactively add a custom device."""
    print("\n" + "─" * 70)
    print("Add a new device:")
    
    name = input("  Device name: ").strip()
    if not name:
        return None
    
    print("\n  Device types:")
    for idx, dtype in enumerate(DeviceTypeEnum, 1):
        print(f"    [{idx}] {dtype.value}")
    
    while True:
        try:
            type_choice = int(input("  Select type (1-7): ").strip())
            if 1 <= type_choice <= 7:
                device_type = list(DeviceTypeEnum)[type_choice - 1].value
                break
            print("  ❌ Invalid choice")
        except ValueError:
            print("  ❌ Invalid input")
    
    ip = input("  IP address: ").strip()
    location = input("  Location: ").strip()
    
    return {
        "name": name,
        "type": device_type,
        "ip": ip,
        "location": location
    }


# =============================================================================
# SEEDING FUNCTIONS
# =============================================================================

async def seed_network(preset_key: str, org_details: dict):
    """Seed the database with network devices."""
    
    logger.info("=" * 70)
    logger.info(f"Starting Network Setup for: {org_details['org_name']}")
    logger.info("=" * 70)
    
    preset = NETWORK_PRESETS[preset_key]
    devices_config = preset['devices'].copy()
    
    # Handle custom configuration
    if preset_key == "custom":
        print("\n" + "=" * 70)
        print("Let's build your custom network!")
        print("=" * 70)
        
        while True:
            device = add_custom_device()
            if device:
                devices_config.append(device)
                more = input("\nAdd another device? (y/n): ").strip().lower()
                if more != 'y':
                    break
            else:
                break
        
        if not devices_config:
            logger.warning("No devices added. Exiting.")
            return
    
    # Customize IP addresses
    base_ip = org_details['base_ip']
    
    # Track used IPs to avoid duplicates
    used_ips = set()
    ip_counter = 1
    
    for device in devices_config:
        if 'ip' in device:
            # Replace IP prefix with custom base_ip
            old_parts = device['ip'].split('.')
            if len(old_parts) == 4:
                # Try to use the last octet from the template
                desired_ip = f"{base_ip}.{old_parts[3]}"
                
                # If IP already used, assign a new one
                if desired_ip in used_ips:
                    # Find next available IP
                    while f"{base_ip}.{ip_counter}" in used_ips:
                        ip_counter += 1
                    device['ip'] = f"{base_ip}.{ip_counter}"
                    used_ips.add(device['ip'])
                    ip_counter += 1
                else:
                    device['ip'] = desired_ip
                    used_ips.add(desired_ip)
    
    async with async_session() as db:
        try:
            # Check for existing devices
            result = await db.execute(select(Device))
            existing = result.scalars().all()
            
            if existing:
                logger.warning(f"⚠️  Database contains {len(existing)} devices")
                print("\nOptions:")
                print("  [1] Delete all and start fresh")
                print("  [2] Add to existing devices")
                print("  [3] Cancel")
                
                choice = input("\nYour choice (1-3): ").strip()
                
                if choice == '1':
                    logger.info("🗑️  Deleting existing data...")
                    await db.execute("DELETE FROM cable_health_metrics")
                    await db.execute("DELETE FROM events")
                    await db.execute("DELETE FROM links")
                    await db.execute("DELETE FROM ports")
                    await db.execute("DELETE FROM devices")
                    await db.commit()
                    logger.info("✓ Existing data deleted")
                elif choice == '3':
                    logger.info("❌ Setup cancelled")
                    return
                # choice == '2' continues to add devices
            
            logger.info(f"\n📦 Creating {len(devices_config)} devices...")
            
            created_devices = []
            
            for idx, dev_config in enumerate(devices_config, 1):
                device_id = f"dev-{idx:03d}"
                
                # Generate MAC address
                mac = f"00:1A:2B:{idx:02X}:{idx:02X}:{idx:02X}"
                
                # Create device
                device = Device(
                    id=device_id,
                    name=dev_config['name'],
                    device_type=DeviceTypeEnum[dev_config['type']],
                    ip=dev_config['ip'],
                    mac=mac,
                    hostname=f"{dev_config['name'].lower().replace(' ', '-')}.{org_details['org_name'].lower().replace(' ', '')}.local",
                    location=dev_config.get('location', 'Unknown'),
                    description=f"{dev_config['type']} - {dev_config['name']}",
                    status=DeviceStatusEnum.UP,
                    last_seen=datetime.utcnow(),
                    is_monitored=org_details['monitor_all'] or dev_config['type'] in ['ROUTER', 'SWITCH', 'SERVER'],
                    snmp_enabled=dev_config['type'] in ['ROUTER', 'SWITCH'],
                    snmp_community="public" if dev_config['type'] in ['ROUTER', 'SWITCH'] else None,
                    snmp_version="2c" if dev_config['type'] in ['ROUTER', 'SWITCH'] else None,
                    position_x=100.0 + (idx * 50),
                    position_y=100.0 + ((idx % 5) * 80),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                db.add(device)
                created_devices.append(device)
                
                monitor_status = "📊" if device.is_monitored else "  "
                logger.info(f"  {monitor_status} ✓ {device.name} ({device.ip})")
            
            await db.commit()
            
            logger.info(f"\n✅ Created {len(created_devices)} devices")
            
            # Create automatic topology links
            logger.info("\n🔗 Creating network topology...")
            links_created = await create_topology_links(db, created_devices)
            
            await db.commit()
            
            # Summary
            logger.info("\n" + "=" * 70)
            logger.info("✅ Network Setup Complete!")
            logger.info("=" * 70)
            logger.info(f"\n📊 Summary:")
            logger.info(f"  • Organization: {org_details['org_name']}")
            logger.info(f"  • Devices: {len(created_devices)}")
            logger.info(f"  • Links: {links_created}")
            logger.info(f"  • Monitored: {sum(1 for d in created_devices if d.is_monitored)}")
            
            # Device breakdown
            from collections import Counter
            device_types = Counter(d.device_type.value for d in created_devices)
            logger.info(f"\n📦 Device Types:")
            for dtype, count in device_types.items():
                logger.info(f"  • {dtype}: {count}")
            
            logger.info("\n🚀 Next Steps:")
            logger.info("  1. Start your application: python -m uvicorn main:app --reload")
            logger.info("  2. Visit: http://localhost:8000/api/docs")
            logger.info("  3. Check status: GET /api/v1/monitoring/status")
            logger.info("  4. View devices: GET /api/v1/devices")
            logger.info("\n✨ Your network is ready to monitor!")
            logger.info("=" * 70)
            
        except Exception as e:
            logger.error(f"❌ Setup failed: {e}", exc_info=True)
            await db.rollback()
            raise


async def create_topology_links(db, devices: list) -> int:
    """
    Automatically create network links based on device hierarchy.
    
    Topology logic:
    - Routers connect to core switches
    - Core switches connect to distribution switches
    - Distribution switches connect to access switches
    - Access switches connect to end devices (APs, printers, servers)
    """
    
    # Categorize devices
    routers = [d for d in devices if d.device_type == DeviceTypeEnum.ROUTER]
    switches = [d for d in devices if d.device_type == DeviceTypeEnum.SWITCH]
    servers = [d for d in devices if d.device_type == DeviceTypeEnum.SERVER]
    aps = [d for d in devices if d.device_type == DeviceTypeEnum.AP]
    printers = [d for d in devices if d.device_type == DeviceTypeEnum.PRINTER]
    pcs = [d for d in devices if d.device_type == DeviceTypeEnum.PC]
    
    links = []
    link_counter = 1
    
    def create_link(source, target, description=""):
        nonlocal link_counter
        link = Link(
            id=f"link-{link_counter:03d}",
            source_device_id=source.id,
            target_device_id=target.id,
            link_type=LinkTypeEnum.PHYSICAL,
            status=LinkStatusEnum.UP,
            bandwidth=1000,
            speed_mbps=1000.0,
            duplex="Full",
            utilization=20.0 + (link_counter % 30),
            packet_loss=0.01,
            latency=1.0,
            jitter=0.2,
            description=description or f"{source.name} ↔ {target.name}",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            last_seen=datetime.utcnow()
        )
        links.append(link)
        link_counter += 1
        return link
    
    # Connect routers to first switches (core switches)
    if routers and switches:
        core_switches = switches[:min(2, len(switches))]
        for router in routers:
            for core_switch in core_switches:
                create_link(router, core_switch, f"Router → Core Switch")
    
    # Connect switches in hierarchy
    if len(switches) > 2:
        core_switches = switches[:2]
        access_switches = switches[2:]
        
        for access in access_switches:
            # Connect to first core switch
            create_link(core_switches[0], access, f"Core → Access Switch")
    elif len(switches) == 2:
        # Connect switches to each other
        create_link(switches[0], switches[1], "Switch Interconnect")
    
    # Connect servers to first switch
    if switches and servers:
        for server in servers:
            create_link(switches[0], server, f"Switch → Server")
    
    # Connect APs to switches
    if switches and aps:
        switches_for_aps = switches[-min(len(switches), len(aps)):]
        for idx, ap in enumerate(aps):
            switch = switches_for_aps[idx % len(switches_for_aps)]
            create_link(switch, ap, f"Switch → WiFi AP")
    
    # Connect printers to switches
    if switches and printers:
        for idx, printer in enumerate(printers):
            switch = switches[min(idx, len(switches) - 1)]
            create_link(switch, printer, f"Switch → Printer")
    
    # Connect PCs to last switches (access switches)
    if switches and pcs:
        access_switches = switches[-min(2, len(switches)):]
        for idx, pc in enumerate(pcs):
            switch = access_switches[idx % len(access_switches)]
            create_link(switch, pc, f"Switch → PC")
    
    # Add all links to database
    for link in links:
        db.add(link)
    
    logger.info(f"  ✓ Created {len(links)} network links")
    
    return len(links)


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

async def main():
    """Main setup wizard."""
    
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "🌐 DYNAMIC NETWORK SEEDING WIZARD" + " " * 20 + "║")
    print("╚" + "=" * 68 + "╝")
    
    try:
        # Step 1: Select preset
        preset_key = show_menu()
        
        # Step 2: Get organization details
        org_details = customize_network_details()
        
        # Step 3: Confirm
        print("\n" + "=" * 70)
        print("📋 Configuration Summary:")
        print("=" * 70)
        print(f"  Organization: {org_details['org_name']}")
        print(f"  Network Type: {NETWORK_PRESETS[preset_key]['name']}")
        print(f"  Base IP: {org_details['base_ip']}.x")
        print(f"  Auto-monitor: {'Yes' if org_details['monitor_all'] else 'No'}")
        
        if preset_key != 'custom':
            print(f"  Devices: {len(NETWORK_PRESETS[preset_key]['devices'])}")
        
        print("=" * 70)
        
        confirm = input("\nProceed with setup? (y/n): ").strip().lower()
        
        if confirm != 'y':
            logger.info("❌ Setup cancelled")
            return
        
        # Step 4: Seed database
        await seed_network(preset_key, org_details)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n❌ Setup failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    # Fix Windows event loop compatibility
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(main())