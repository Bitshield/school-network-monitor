# 🌐 School Network Monitor - Setup Guide

Complete guide for setting up your network monitoring system for **any organization** (schools, companies, offices, etc.)

---

## 🚀 Quick Start (Recommended)

The **fastest** way to get started:

### Step 1: Start Your Application

```bash
python -m uvicorn main:app --reload
```

Wait for this message:
```
🚀 School Network Monitor is ready!
```

### Step 2: Run Quick Setup

```bash
python quick_setup.py
```

This will:
- ✅ Check if your app is running
- ✅ Ask for your organization name
- ✅ Let you choose network size (small/medium/large)
- ✅ Automatically create devices
- ✅ Start monitoring immediately

**That's it!** Your network is ready in under 1 minute.

---

## 📚 All Setup Options

You have **3 different ways** to populate your network:

### Option 1: Quick Setup (API-Based) ⚡

**Best for:** Beginners, quick testing

```bash
python quick_setup.py
```

**Advantages:**
- ✅ Simplest - just 3 questions
- ✅ Works via API (no database access needed)
- ✅ Automatic network topology
- ✅ Pre-built templates (small/medium/large)

**Sizes:**
- **Small** (6 devices): Home office, small business
- **Medium** (12 devices): School, medium business
- **Large** (24 devices): University, large enterprise

---

### Option 2: Dynamic Wizard (Database-Based) 🧙

**Best for:** Custom configurations, advanced users

```bash
python seed_network.py
```

**Advantages:**
- ✅ Full customization
- ✅ Choose from presets or build custom
- ✅ Automatic link generation
- ✅ Supports any organization type

**Presets:**
1. **Small School** (8 devices)
   - 1 Router, 3 Switches, 1 Server, 1 AP, 1 Printer

2. **Medium School** (21 devices)
   - 2 Routers, 11 Switches, 2 Servers, 4 APs, 2 Printers

3. **Large Enterprise** (25 devices)
   - 3 Routers, 14 Switches, 5 Servers, WiFi Controller, 4 APs

4. **Small Office** (5 devices)
   - 1 Router, 1 Switch, 1 AP, 1 Printer, 1 Server

5. **Custom** (You define everything)

---

### Option 3: Network Discovery (Real Network) 🔍

**Best for:** Existing networks, production environments

#### Via API:

```bash
curl -X POST "http://localhost:8000/api/v1/discovery/scan?network_range=192.168.1.0/24&save_results=true"
```

#### Via API Docs:

1. Go to `http://localhost:8000/api/docs`
2. Find **POST /api/v1/discovery/scan**
3. Enter your network range (e.g., `192.168.1.0/24`)
4. Click "Execute"

**This will:**
- ✅ Scan your actual network
- ✅ Discover all active devices
- ✅ Auto-detect device types
- ✅ Save to database

**Common Network Ranges:**
- Home/Small Office: `192.168.1.0/24` (254 hosts)
- School: `192.168.0.0/16` (65,534 hosts)
- Enterprise: `10.0.0.0/8` (16 million hosts)

---

## 🎯 Which Setup Method Should I Use?

| Your Situation | Recommended Method |
|---------------|-------------------|
| "Just want to test quickly" | **quick_setup.py** |
| "Need specific configuration" | **seed_network.py** |
| "Have an existing network to monitor" | **Network Discovery** |
| "Building for production" | **seed_network.py** + Discovery |
| "Testing API features" | **quick_setup.py** |

---

## 📖 Detailed Instructions

### Using quick_setup.py

```bash
# 1. Make sure app is running
python -m uvicorn main:app --reload

# 2. In another terminal, run quick setup
python quick_setup.py

# 3. Answer questions:
# Organization name: "Lincoln High School"
# Network size: 2 (Medium)
# Base IP: 192.168.1

# Done! Devices created automatically.
```

### Using seed_network.py

```bash
# 1. Run the wizard
python seed_network.py

# 2. Select preset:
# [1] Small School (5-15 devices)
# [2] Medium School (15-30 devices)  
# [3] Large Enterprise/University (30+ devices)
# [4] Small Office (5-10 devices)
# [5] Custom Configuration
# Your choice: 2

# 3. Customize:
# Organization name: "Washington University"
# Base IP: 10.0.0
# Monitor all devices: y

# 4. Confirm and create!
```

### Using Network Discovery

#### Step 1: Find Your Network Range

**On Windows:**
```bash
ipconfig
# Look for "IPv4 Address" like 192.168.1.100
# Your network is likely 192.168.1.0/24
```

**On Linux/Mac:**
```bash
ip addr show
# or
ifconfig
```

#### Step 2: Scan Network

**Method A - Using API Docs (Easiest):**
1. Open `http://localhost:8000/api/docs`
2. Scroll to **Network Discovery**
3. Click **POST /api/v1/discovery/scan**
4. Click "Try it out"
5. Enter:
   - `network_range`: Your network (e.g., `192.168.1.0/24`)
   - `save_results`: `true`
6. Click "Execute"

**Method B - Using curl:**
```bash
curl -X POST "http://localhost:8000/api/v1/discovery/scan?network_range=192.168.1.0/24&save_results=true"
```

**Method C - Using Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/discovery/scan",
    params={
        "network_range": "192.168.1.0/24",
        "save_results": True
    }
)

print(response.json())
```

---

## 🔧 Configuration Options

### Customize Organization Name

All scripts support custom organization names:

```python
# quick_setup.py
Organization name: "Your School Name"

# seed_network.py  
Organization name: "Your Company Name"
```

### Customize IP Ranges

Change the base IP to match your network:

```python
# Examples:
Base IP: 192.168.1    # Home/Small Office
Base IP: 192.168.0    # School
Base IP: 10.0.0       # Enterprise
Base IP: 172.16.0     # Corporate
```

### Enable/Disable Monitoring

Choose which devices to monitor:

```python
# Monitor everything
Monitor all devices: y

# Monitor only critical devices (routers, switches, servers)
Monitor all devices: n
```

---

## 📊 After Setup

### Verify Everything Works

#### 1. Check Monitoring Status

**Via Browser:**
```
http://localhost:8000/api/v1/monitoring/status
```

**Via curl:**
```bash
curl http://localhost:8000/api/v1/monitoring/status
```

**Expected Output:**
```json
{
  "is_running": true,
  "check_interval_seconds": 60,
  "monitored_devices": 12,
  "monitored_links": 10,
  "recent_events_1h": 0
}
```

#### 2. View All Devices

**Via Browser:**
```
http://localhost:8000/api/v1/devices
```

**Via API Docs:**
```
http://localhost:8000/api/docs
→ GET /api/v1/devices
```

#### 3. Check Network Health

```bash
curl http://localhost:8000/api/v1/monitoring/health-summary
```

---

## 🎨 Customize Your Network

### Add More Devices Manually

**Via API Docs** (Easiest):
1. Go to `http://localhost:8000/api/docs`
2. Find **POST /api/v1/devices**
3. Click "Try it out"
4. Enter device details:
```json
{
  "name": "New Device",
  "device_type": "SWITCH",
  "ip": "192.168.1.50",
  "mac": "00:11:22:33:44:55",
  "location": "Room 101",
  "is_monitored": true
}
```
5. Click "Execute"

**Via curl:**
```bash
curl -X POST "http://localhost:8000/api/v1/devices" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Lab Switch",
    "device_type": "SWITCH",
    "ip": "192.168.1.50",
    "location": "Computer Lab",
    "is_monitored": true
  }'
```

### Device Types

Available device types:
- `ROUTER` - Network routers
- `SWITCH` - Network switches
- `SERVER` - Servers
- `PC` - Computers/workstations
- `PRINTER` - Network printers
- `AP` - Wireless access points
- `FIREWALL` - Firewalls

---

## ⚠️ Troubleshooting

### "Application is not running"

**Problem:** quick_setup.py shows error

**Solution:**
```bash
# Start the application first
python -m uvicorn main:app --reload

# Wait for "School Network Monitor is ready!"
# Then run quick_setup.py in another terminal
```

### "ProactorEventLoop" Error (Windows)

**Problem:** seed_network.py shows async error

**Solution:** Already fixed! The updated scripts include:
```python
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
```

Make sure you're using the NEW scripts from this update.

### "No monitored devices found"

**Problem:** Application shows warning

**Solution:** This is **normal** when database is empty. Run any setup script:
```bash
python quick_setup.py
```

### Devices Not Showing Up

**Problem:** Created devices but can't see them

**Solution:**
1. Check if app is running:
```bash
curl http://localhost:8000/api/v1/health
```

2. List devices:
```bash
curl http://localhost:8000/api/v1/devices
```

3. If empty, run setup again

---

## 🎓 Examples for Different Organizations

### High School Setup

```bash
python seed_network.py

# Choose: [2] Medium School
# Organization: "Lincoln High School"
# Base IP: 192.168.1
# Monitor all: y
```

**Creates:**
- Main router (internet gateway)
- Core switches (server room)
- Floor switches (3 floors)
- WiFi access points (2)
- Servers (file server, backup)
- Printers (office, labs)

### Small Business

```bash
python quick_setup.py

# Organization: "Smith & Associates Law Firm"
# Size: 1 (Small)
# Base IP: 192.168.0
```

**Creates:**
- Router
- Main switch
- Access switch
- WiFi AP
- Server
- Printer

### University Campus

```bash
python seed_network.py

# Choose: [3] Large Enterprise
# Organization: "State University"
# Base IP: 10.0.0
# Monitor all: y
```

**Creates:**
- Core routers (2)
- Distribution switches (3 wings)
- Access switches (per floor)
- WiFi controller + APs
- Multiple servers
- Enterprise infrastructure

---

## 📝 Summary

### Recommended Workflow

1. **Start application:**
   ```bash
   python -m uvicorn main:app --reload
   ```

2. **Choose your setup method:**
   - Quick test: `python quick_setup.py`
   - Custom config: `python seed_network.py`
   - Real network: Use discovery API

3. **Verify:**
   - Open `http://localhost:8000/api/docs`
   - Check `/api/v1/monitoring/status`
   - View `/api/v1/devices`

4. **Monitor:**
   - System auto-monitors every 60 seconds
   - Check `/api/v1/monitoring/health-summary`
   - View events at `/api/v1/events`

---

## 🆘 Need Help?

### Common Tasks

**Reset database and start over:**
```bash
# Delete database
rm school_network.db

# Restart app (creates new database)
python -m uvicorn main:app --reload

# Run setup again
python quick_setup.py
```

**Add single device:**
- Use API docs: `http://localhost:8000/api/docs`
- Find: POST /api/v1/devices
- Fill form and execute

**Scan your real network:**
- Use API docs: `http://localhost:8000/api/docs`
- Find: POST /api/v1/discovery/scan
- Enter your network range

---

## 🎉 You're All Set!

Your network monitoring system is now ready to:
- ✅ Monitor all devices 24/7
- ✅ Detect when devices go offline
- ✅ Track network health
- ✅ Generate alerts
- ✅ Visualize network topology
- ✅ Analyze performance metrics

**Happy monitoring! 🚀**

---

## 📚 Additional Resources

- **API Documentation:** `http://localhost:8000/api/docs`
- **Health Check:** `http://localhost:8000/api/v1/health`
- **Monitoring Status:** `http://localhost:8000/api/v1/monitoring/status`
- **All Devices:** `http://localhost:8000/api/v1/devices`
- **Network Health:** `http://localhost:8000/api/v1/monitoring/health-summary`