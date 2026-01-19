"""
Quick Start - Add devices via API (No database access needed)
This script uses the REST API to add devices, so it's simpler and more portable.
"""

import requests
import sys
import time

BASE_URL = "http://localhost:8000/api/v1"


def check_api():
    """Check if API is running."""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=3)
        return response.status_code == 200
    except:
        return False


def quick_setup():
    """Quick setup with minimal questions."""
    print("\n" + "=" * 70)
    print(" " * 20 + "⚡ QUICK NETWORK SETUP")
    print("=" * 70)
    
    # Check API
    print("\n🔍 Checking if application is running...")
    if not check_api():
        print("\n❌ ERROR: Application is not running!")
        print("\n📌 Please start the application first:")
        print("   python -m uvicorn main:app --reload")
        print("\nThen run this script again.")
        return False
    
    print("✅ Application is running!\n")
    
    # Get organization name
    org_name = input("Organization name (or press Enter for 'My Network'): ").strip()
    if not org_name:
        org_name = "My Network"
    
    # Select size
    print("\nNetwork size:")
    print("  [1] Small (5-8 devices) - Home, Small Office")
    print("  [2] Medium (10-15 devices) - School, Medium Business")
    print("  [3] Large (20+ devices) - University, Enterprise")
    
    while True:
        choice = input("\nSelect size (1-3) [2]: ").strip()
        if not choice:
            choice = "2"
        if choice in ["1", "2", "3"]:
            break
        print("❌ Invalid choice")
    
    # Get base IP
    base_ip = input("\nBase IP (e.g., 192.168.1 or 10.0.0) [192.168.1]: ").strip()
    if not base_ip:
        base_ip = "192.168.1"
    base_ip = base_ip.rstrip('.')
    
    # Build device list
    if choice == "1":
        devices = build_small_network(org_name, base_ip)
    elif choice == "2":
        devices = build_medium_network(org_name, base_ip)
    else:
        devices = build_large_network(org_name, base_ip)
    
    # Confirm
    print(f"\n📊 Ready to create {len(devices)} devices for '{org_name}'")
    confirm = input("Continue? (y/n) [y]: ").strip().lower()
    
    if confirm and confirm != 'y':
        print("❌ Setup cancelled")
        return False
    
    # Create devices
    print("\n" + "=" * 70)
    print("📦 Creating devices...")
    print("=" * 70 + "\n")
    
    created = 0
    for device in devices:
        try:
            response = requests.post(f"{BASE_URL}/devices", json=device, timeout=5)
            if response.status_code == 201:
                print(f"✅ {device['name']} ({device['ip']})")
                created += 1
            elif response.status_code == 409:
                print(f"⚠️  {device['name']} - Already exists")
            else:
                print(f"❌ {device['name']} - Failed: {response.text[:50]}")
        except Exception as e:
            print(f"❌ {device['name']} - Error: {str(e)[:50]}")
        
        time.sleep(0.1)  # Small delay to avoid overwhelming API
    
    print(f"\n✅ Created {created} devices")
    
    # Wait for monitoring
    print("\n⏳ Waiting for monitoring cycle...")
    time.sleep(5)
    
    # Show status
    print("\n" + "=" * 70)
    print("📊 MONITORING STATUS")
    print("=" * 70)
    
    try:
        response = requests.get(f"{BASE_URL}/monitoring/status")
        if response.status_code == 200:
            status = response.json()
            print(f"\n✅ Monitoring: {'ACTIVE' if status['is_running'] else 'INACTIVE'}")
            print(f"📍 Monitored Devices: {status['monitored_devices']}")
            print(f"🔗 Monitored Links: {status['monitored_links']}")
            print(f"⚠️  Recent Events (1h): {status['recent_events_1h']}")
    except:
        print("\n⚠️  Could not fetch monitoring status")
    
    # Final message
    print("\n" + "=" * 70)
    print("✅ SETUP COMPLETE!")
    print("=" * 70)
    print(f"\n🌐 Your network '{org_name}' is ready!")
    print("\n📚 Next Steps:")
    print("  • API Docs: http://localhost:8000/api/docs")
    print("  • Devices: http://localhost:8000/api/v1/devices")
    print("  • Status: http://localhost:8000/api/v1/monitoring/status")
    print("  • Health: http://localhost:8000/api/v1/monitoring/health-summary")
    print("\n✨ The system will automatically monitor your devices every 60 seconds!")
    print("=" * 70 + "\n")
    
    return True


def build_small_network(org_name, base_ip):
    """Build small network (5-8 devices)."""
    return [
        {
            "name": f"{org_name} - Main Router",
            "device_type": "ROUTER",
            "ip": f"{base_ip}.1",
            "mac": "00:1A:2B:3C:4D:01",
            "location": "Network Room",
            "is_monitored": True,
            "snmp_enabled": True
        },
        {
            "name": f"{org_name} - Main Switch",
            "device_type": "SWITCH",
            "ip": f"{base_ip}.2",
            "mac": "00:1A:2B:3C:4D:02",
            "location": "Network Room",
            "is_monitored": True,
            "snmp_enabled": True
        },
        {
            "name": f"{org_name} - Access Switch",
            "device_type": "SWITCH",
            "ip": f"{base_ip}.10",
            "mac": "00:1A:2B:3C:4D:10",
            "location": "Office Area",
            "is_monitored": True
        },
        {
            "name": f"{org_name} - WiFi AP",
            "device_type": "AP",
            "ip": f"{base_ip}.100",
            "mac": "00:1A:2B:3C:4D:64",
            "location": "Main Area",
            "is_monitored": True
        },
        {
            "name": f"{org_name} - Server",
            "device_type": "SERVER",
            "ip": f"{base_ip}.50",
            "mac": "00:1A:2B:3C:4D:32",
            "location": "Server Room",
            "is_monitored": True
        },
        {
            "name": f"{org_name} - Printer",
            "device_type": "PRINTER",
            "ip": f"{base_ip}.200",
            "mac": "00:1A:2B:3C:4D:C8",
            "location": "Office",
            "is_monitored": False
        }
    ]


def build_medium_network(org_name, base_ip):
    """Build medium network (10-15 devices)."""
    devices = [
        {
            "name": f"{org_name} - Main Router",
            "device_type": "ROUTER",
            "ip": f"{base_ip}.1",
            "mac": "00:1A:2B:3C:01:01",
            "location": "Server Room",
            "is_monitored": True,
            "snmp_enabled": True
        },
        {
            "name": f"{org_name} - Core Switch",
            "device_type": "SWITCH",
            "ip": f"{base_ip}.2",
            "mac": "00:1A:2B:3C:02:02",
            "location": "Server Room",
            "is_monitored": True,
            "snmp_enabled": True
        },
    ]
    
    # Add floor switches
    for floor in range(1, 4):
        devices.append({
            "name": f"{org_name} - Floor {floor} Switch",
            "device_type": "SWITCH",
            "ip": f"{base_ip}.{10+floor}",
            "mac": f"00:1A:2B:3C:{10+floor:02X}:{10+floor:02X}",
            "location": f"Floor {floor}",
            "is_monitored": True
        })
    
    # Add APs
    for i in range(1, 3):
        devices.append({
            "name": f"{org_name} - WiFi AP {i}",
            "device_type": "AP",
            "ip": f"{base_ip}.{100+i}",
            "mac": f"00:1A:2B:3C:{100+i:02X}:{100+i:02X}",
            "location": f"Floor {i}",
            "is_monitored": True
        })
    
    # Add servers
    devices.extend([
        {
            "name": f"{org_name} - File Server",
            "device_type": "SERVER",
            "ip": f"{base_ip}.50",
            "mac": "00:1A:2B:3C:50:50",
            "location": "Server Room",
            "is_monitored": True
        },
        {
            "name": f"{org_name} - Backup Server",
            "device_type": "SERVER",
            "ip": f"{base_ip}.51",
            "mac": "00:1A:2B:3C:51:51",
            "location": "Server Room",
            "is_monitored": True
        }
    ])
    
    # Add printers
    for i in range(1, 3):
        devices.append({
            "name": f"{org_name} - Printer {i}",
            "device_type": "PRINTER",
            "ip": f"{base_ip}.{200+i}",
            "mac": f"00:1A:2B:3C:{200+i:02X}:{200+i:02X}",
            "location": f"Floor {i}",
            "is_monitored": False
        })
    
    return devices


def build_large_network(org_name, base_ip):
    """Build large network (20+ devices)."""
    devices = build_medium_network(org_name, base_ip)
    
    # Add more switches
    for floor in range(4, 7):
        devices.append({
            "name": f"{org_name} - Floor {floor} Switch",
            "device_type": "SWITCH",
            "ip": f"{base_ip}.{10+floor}",
            "mac": f"00:1A:2B:3C:{10+floor:02X}:{10+floor:02X}",
            "location": f"Floor {floor}",
            "is_monitored": True
        })
    
    # Add more APs
    for i in range(3, 6):
        devices.append({
            "name": f"{org_name} - WiFi AP {i}",
            "device_type": "AP",
            "ip": f"{base_ip}.{100+i}",
            "mac": f"00:1A:2B:3C:{100+i:02X}:{100+i:02X}",
            "location": f"Floor {i}",
            "is_monitored": True
        })
    
    # Add more servers
    devices.extend([
        {
            "name": f"{org_name} - Web Server",
            "device_type": "SERVER",
            "ip": f"{base_ip}.52",
            "mac": "00:1A:2B:3C:52:52",
            "location": "Server Room",
            "is_monitored": True
        },
        {
            "name": f"{org_name} - Database Server",
            "device_type": "SERVER",
            "ip": f"{base_ip}.53",
            "mac": "00:1A:2B:3C:53:53",
            "location": "Server Room",
            "is_monitored": True
        }
    ])
    
    # Add more printers
    for i in range(3, 6):
        devices.append({
            "name": f"{org_name} - Printer {i}",
            "device_type": "PRINTER",
            "ip": f"{base_ip}.{200+i}",
            "mac": f"00:1A:2B:3C:{200+i:02X}:{200+i:02X}",
            "location": f"Floor {i}",
            "is_monitored": False
        })
    
    return devices


if __name__ == "__main__":
    print("\n╔" + "=" * 68 + "╗")
    print("║" + " " * 20 + "⚡ QUICK NETWORK SETUP" + " " * 23 + "║")
    print("╚" + "=" * 68 + "╝")
    
    try:
        success = quick_setup()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}\n")
        sys.exit(1)