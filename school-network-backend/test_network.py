#!/usr/bin/env python3
"""
Quick test script to add sample devices and verify monitoring.
Run this to populate your network and test the system.
"""

import requests
import time
import json
import sys
import asyncio

# Fix Windows event loop for Python 3.12+
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

BASE_URL = "http://localhost:8000/api/v1"

def add_sample_devices():
    """Add sample devices to the network."""
    print("=" * 60)
    print("Adding Sample Devices to School Network Monitor")
    print("=" * 60)
    
    devices = [
        {
            "name": "Main Router",
            "device_type": "ROUTER",
            "ip": "192.168.1.1",
            "mac": "00:1A:2B:3C:4D:01",
            "location": "Server Room",
            "description": "Main internet gateway router",
            "is_monitored": True,
            "snmp_enabled": True
        },
        {
            "name": "Core Switch",
            "device_type": "SWITCH",
            "ip": "192.168.1.2",
            "mac": "00:1A:2B:3C:4D:02",
            "location": "Server Room",
            "description": "Central distribution switch",
            "is_monitored": True,
            "snmp_enabled": True
        },
        {
            "name": "Computer Lab Switch",
            "device_type": "SWITCH",
            "ip": "192.168.1.10",
            "mac": "00:1A:2B:3C:4D:10",
            "location": "Computer Lab - Room 201",
            "description": "Switch for computer lab",
            "is_monitored": True
        },
        {
            "name": "Library Switch",
            "device_type": "SWITCH",
            "ip": "192.168.1.11",
            "mac": "00:1A:2B:3C:4D:11",
            "location": "Library",
            "description": "Switch for library network",
            "is_monitored": True
        },
        {
            "name": "File Server",
            "device_type": "SERVER",
            "ip": "192.168.1.100",
            "mac": "00:1A:2B:3C:4D:64",
            "location": "Server Room",
            "description": "Main file storage server",
            "is_monitored": True
        },
        {
            "name": "WiFi Access Point - Main Hall",
            "device_type": "AP",
            "ip": "192.168.1.50",
            "mac": "00:1A:2B:3C:4D:32",
            "location": "Main Hall",
            "description": "Wireless access point",
            "is_monitored": True
        }
    ]
    
    added_count = 0
    for device in devices:
        try:
            response = requests.post(f"{BASE_URL}/devices", json=device)
            if response.status_code == 201:
                print(f"✅ Added: {device['name']} ({device['ip']})")
                added_count += 1
            elif response.status_code == 409:
                print(f"⚠️  Already exists: {device['name']} ({device['ip']})")
            else:
                print(f"❌ Failed: {device['name']} - {response.text}")
        except Exception as e:
            print(f"❌ Error adding {device['name']}: {e}")
    
    print(f"\n✅ Successfully added {added_count} new devices")
    return added_count


def check_monitoring_status():
    """Check current monitoring status."""
    print("\n" + "=" * 60)
    print("Checking Monitoring Status")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/monitoring/status")
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Monitoring Status:")
            print(f"   - Running: {status['is_running']}")
            print(f"   - Interval: {status['check_interval_seconds']} seconds")
            print(f"   - Monitored Devices: {status['monitored_devices']}")
            print(f"   - Monitored Links: {status['monitored_links']}")
            print(f"   - Recent Events (1h): {status['recent_events_1h']}")
        else:
            print(f"❌ Failed to get status: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")


def list_devices():
    """List all devices in the network."""
    print("\n" + "=" * 60)
    print("Current Devices in Network")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/devices")
        if response.status_code == 200:
            devices = response.json()
            print(f"Found {len(devices)} devices:\n")
            
            for device in devices:
                status_icon = "🟢" if device['status'] == "UP" else "🔴" if device['status'] == "DOWN" else "⚪"
                print(f"{status_icon} {device['name']}")
                print(f"   Type: {device['device_type']}")
                print(f"   IP: {device['ip']}")
                print(f"   Status: {device['status']}")
                print(f"   Location: {device.get('location', 'N/A')}")
                print(f"   Monitored: {'Yes' if device['is_monitored'] else 'No'}")
                print()
        else:
            print(f"❌ Failed to list devices: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")


def trigger_monitoring_cycle():
    """Manually trigger a monitoring cycle."""
    print("\n" + "=" * 60)
    print("Triggering Monitoring Cycle")
    print("=" * 60)
    
    try:
        response = requests.post(f"{BASE_URL}/monitoring/run-cycle")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Monitoring cycle started in background")
            print(f"   Status: {result['status']}")
            print("\n⏳ Waiting 5 seconds for monitoring to complete...")
            time.sleep(5)
        else:
            print(f"❌ Failed to trigger monitoring: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")


def get_health_summary():
    """Get network health summary."""
    print("\n" + "=" * 60)
    print("Network Health Summary")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/monitoring/health-summary")
        if response.status_code == 200:
            health = response.json()
            
            print(f"\n📊 Devices:")
            print(f"   Total: {health['devices']['total']}")
            print(f"   Up: {health['devices']['up']} 🟢")
            print(f"   Down: {health['devices']['down']} 🔴")
            
            print(f"\n🔗 Links:")
            print(f"   Total: {health['links']['total']}")
            print(f"   Up: {health['links']['up']} 🟢")
            print(f"   Degraded: {health['links']['degraded']} 🟡")
            print(f"   Down: {health['links']['down']} 🔴")
            
            print(f"\n⚠️  Alerts:")
            print(f"   Critical (Unacknowledged): {health['alerts']['critical_unacknowledged']}")
        else:
            print(f"❌ Failed to get health summary: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")


def get_statistics():
    """Get network statistics."""
    print("\n" + "=" * 60)
    print("Network Statistics")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/statistics/overview")
        if response.status_code == 200:
            stats = response.json()
            
            print(f"\n📊 Devices by Type:")
            if 'devices' in stats and 'by_type' in stats['devices']:
                for device_type, count in stats['devices']['by_type'].items():
                    print(f"   {device_type}: {count}")
            
            print(f"\n📈 Events (Last 24h):")
            if 'events' in stats:
                print(f"   Total: {stats['events'].get('last_24h', 0)}")
                print(f"   Critical: {stats['events'].get('critical_24h', 0)}")
        else:
            print(f"❌ Failed to get statistics: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Main test function."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "School Network Monitor - Test Script" + " " * 11 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    try:
        # Step 1: Add sample devices
        added_count = add_sample_devices()
        
        if added_count > 0:
            print("\n⏳ Waiting 3 seconds for devices to be registered...")
            time.sleep(3)
        
        # Step 2: Check monitoring status
        check_monitoring_status()
        
        # Step 3: List all devices
        list_devices()
        
        # Step 4: Trigger monitoring cycle
        if added_count > 0:
            trigger_monitoring_cycle()
            
            # Step 5: Get health summary
            get_health_summary()
            
            # Step 6: Get statistics
            get_statistics()
        
        # Final message
        print("\n" + "=" * 60)
        print("✅ Test Complete!")
        print("=" * 60)
        print("\n📚 Next Steps:")
        print("   1. Open http://localhost:8000/api/docs in your browser")
        print("   2. Try the network discovery API to scan your school network")
        print("   3. Monitor real-time updates every 60 seconds")
        print("\n🔍 API Documentation: http://localhost:8000/api/docs")
        print("📊 Monitoring Status: http://localhost:8000/api/v1/monitoring/status")
        print()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")


if __name__ == "__main__":
    main()