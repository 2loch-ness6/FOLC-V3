# SOS Installation and Integration Guide

## Overview

This guide walks through installing and integrating the Service Orchestration System (SOS) with your existing FOLC-V3 setup.

## Prerequisites

Before installing SOS, ensure you have:

- ✅ Orbic Speed (RC400L) device with root access
- ✅ ADB working and device connected
- ✅ Alpine Linux chroot installed at `/data/alpine`
- ✅ Basic FOLC-V3 setup complete
- ✅ Python 3 available in both native and Alpine environments

## Installation Methods

### Method 1: Automated Installation (Recommended)

The easiest way to install SOS:

```bash
cd FOLC-V3
./tools/deploy_sos.sh
```

This script will:
1. Check prerequisites (ADB, root access)
2. Deploy native daemons to `/data/rayhunter/`
3. Deploy Alpine services to `/data/alpine/`
4. Set proper permissions
5. Test the installation

### Method 2: Manual Installation

If the automated script fails, follow these steps:

#### Step 1: Deploy Native Environment Files

```bash
# Push hardware control daemon
adb push src/sos/daemons/hw_ctl_daemon.py /data/rayhunter/
adb shell "su -c 'chmod +x /data/rayhunter/hw_ctl_daemon.py'"

# Push API gateway daemon
adb push src/sos/daemons/api_gateway_daemon.py /data/rayhunter/
adb shell "su -c 'chmod +x /data/rayhunter/api_gateway_daemon.py'"

# Push SOS manager
adb push src/sos/sos_manager.sh /data/rayhunter/
adb shell "su -c 'chmod +x /data/rayhunter/sos_manager.sh'"
```

#### Step 2: Deploy Alpine Environment Files

```bash
# Create directories
adb shell "su -c 'mkdir -p /data/alpine/usr/local/bin'"
adb shell "su -c 'mkdir -p /data/alpine/etc/sos'"
adb shell "su -c 'mkdir -p /data/alpine/var/log'"

# Push AI orchestrator
adb push src/sos/ai/ai_orchestrator.py /data/alpine/usr/local/bin/
adb shell "su -c 'chmod +x /data/alpine/usr/local/bin/ai_orchestrator.py'"

# Push configuration
adb push src/sos/config/ai_config.json /data/alpine/etc/sos/"
```

#### Step 3: Install Python Dependencies (Alpine Chroot)

```bash
# Enter Alpine chroot
adb shell "su -c 'chroot /data/alpine /bin/sh'"

# Inside chroot, run:
apk add python3 py3-pip

# Install AI packages (optional, for AI features)
pip3 install google-generativeai anthropic
```

#### Step 4: Configure API Keys (Optional)

For AI features, set up API keys:

```bash
# In Alpine chroot
echo 'export GEMINI_API_KEY="your-gemini-api-key-here"' >> /root/.profile
echo 'export ANTHROPIC_API_KEY="your-anthropic-api-key-here"' >> /root/.profile

# Apply changes
source /root/.profile
```

To get API keys:
- **Gemini:** https://makersuite.google.com/app/apikey
- **Claude:** https://console.anthropic.com/

## Integration with Existing System

### Option A: Automatic Startup (Recommended)

Make SOS start automatically with your device:

1. **Using the enhanced wrapper:**

```bash
# Deploy the SOS-enhanced wrapper
adb push exploits/wrapper_sos.sh /data/rayhunter/
adb shell "su -c 'chmod +x /data/rayhunter/wrapper_sos.sh'"

# Backup current wrapper
adb shell "su -c 'cp /data/rayhunter/wrapper_v4.sh /data/rayhunter/wrapper_v4.sh.bak'"

# Replace with SOS-enhanced version
adb shell "su -c 'cp /data/rayhunter/wrapper_sos.sh /data/rayhunter/wrapper_v4.sh'"

# Reboot to apply
adb reboot
```

2. **Manual integration (if you have custom wrapper):**

Edit your existing `/data/rayhunter/wrapper_v4.sh` and add before FOLC UI:

```bash
# Start SOS
if [ -f /data/rayhunter/sos_manager.sh ]; then
    echo "[-] Starting SOS..." >> $LOG
    /bin/sh /data/rayhunter/sos_manager.sh start >> $LOG 2>&1 &
fi
```

### Option B: Manual Startup

Start SOS manually when needed:

```bash
adb shell "su -c '/bin/sh /data/rayhunter/sos_manager.sh start'"
```

## Verification

### Test 1: Check Installation

```bash
./tools/test_sos.sh
```

This runs comprehensive tests to verify installation.

### Test 2: Check Service Status

```bash
adb shell "su -c '/bin/sh /data/rayhunter/sos_manager.sh status'"
```

Expected output should show services as RUNNING.

### Test 3: Test API

```bash
# Forward API port
adb forward tcp:8888 tcp:8888

# Test health endpoint
curl http://127.0.0.1:8888/api/health

# Expected response:
# {"status": "healthy", "service": "api_gateway"}
```

### Test 4: Test WiFi API

```bash
curl http://127.0.0.1:8888/api/wifi/status
```

### Test 5: Test System Info

```bash
curl http://127.0.0.1:8888/api/system/info
```

## Post-Installation Configuration

### Configure Logging

Logs are stored at:
- Hardware daemon: `/data/rayhunter/hw_ctl_daemon.log`
- API gateway: `/data/rayhunter/api_gateway_daemon.log`
- AI orchestrator: `/data/alpine/var/log/ai_orchestrator.log`

To view logs:
```bash
adb shell "su -c 'cat /data/rayhunter/hw_ctl_daemon.log'"
```

### Adjust AI Configuration

Edit `/data/alpine/etc/sos/ai_config.json`:

```json
{
  "preferred_provider": "gemini",  // or "claude"
  "fallback_enabled": true,
  "max_retries": 3,
  "timeout": 30
}
```

## Usage Examples

### Example 1: Query System Status via API

```bash
# Forward port
adb forward tcp:8888 tcp:8888

# Get system info
curl http://127.0.0.1:8888/api/system/info | python3 -m json.tool
```

### Example 2: Scan WiFi Networks

```bash
curl http://127.0.0.1:8888/api/wifi/scan | python3 -m json.tool
```

### Example 3: Use AI Interactive Mode

```bash
# Enter device
adb shell

# Become root
su

# Enter Alpine chroot
chroot /data/alpine /bin/sh

# Start AI orchestrator
/usr/local/bin/ai_orchestrator.py --interactive

# Now you can use natural language:
> scan wifi networks
> show system status
> what is the memory usage?
```

### Example 4: Use from Python Script

Create a script on your computer:

```python
#!/usr/bin/env python3
import requests

# Ensure port is forwarded: adb forward tcp:8888 tcp:8888
API_BASE = "http://127.0.0.1:8888/api"

# Get system info
response = requests.get(f"{API_BASE}/system/info")
info = response.json()
print(f"Uptime: {info['uptime']} seconds")
print(f"Load: {info['load_avg']}")

# Scan WiFi
response = requests.get(f"{API_BASE}/wifi/scan")
networks = response.json().get('networks', [])
print(f"\nFound {len(networks)} WiFi networks:")
for net in networks:
    print(f"  - {net.get('ssid', 'Hidden')}: {net.get('signal', 'N/A')}")
```

## Troubleshooting

### Services Won't Start

**Check if Python 3 is available:**
```bash
adb shell "su -c 'which python3'"
```

**Check permissions:**
```bash
adb shell "su -c 'ls -l /data/rayhunter/*.py'"
```

All scripts should be executable (x flag).

**Check logs:**
```bash
adb shell "su -c 'cat /data/rayhunter/hw_ctl_daemon.log'"
```

### API Not Responding

**Check if daemon is running:**
```bash
adb shell "su -c '/bin/sh /data/rayhunter/sos_manager.sh status'"
```

**Test locally on device:**
```bash
adb shell "su -c 'wget -O- http://127.0.0.1:8888/api/health'"
```

**Check port forwarding:**
```bash
# Re-forward the port
adb forward tcp:8888 tcp:8888

# Test again
curl http://127.0.0.1:8888/api/health
```

### AI Not Working

**Check API keys:**
```bash
adb shell "su -c 'chroot /data/alpine /bin/sh -c \"env | grep API_KEY\"'"
```

**Install AI packages:**
```bash
adb shell "su -c 'chroot /data/alpine /bin/sh'"
# In chroot:
pip3 install google-generativeai anthropic
```

**Test CLI tools:**
```bash
adb shell "su -c 'chroot /data/alpine gemini --version'"
```

### Permission Denied Errors

Make sure all scripts are executable:
```bash
adb shell "su -c 'chmod +x /data/rayhunter/hw_ctl_daemon.py'"
adb shell "su -c 'chmod +x /data/rayhunter/api_gateway_daemon.py'"
adb shell "su -c 'chmod +x /data/rayhunter/sos_manager.sh'"
adb shell "su -c 'chmod +x /data/alpine/usr/local/bin/ai_orchestrator.py'"
```

## Advanced Configuration

### Customize API Port

Edit `api_gateway_daemon.py` and change:
```python
API_PORT = 8888  # Change to your preferred port
```

### Add Custom Hardware Commands

Edit `hw_ctl_daemon.py` and add to `HardwareController` class:
```python
def my_custom_command(self):
    # Your implementation
    return {"status": "success", "data": ...}
```

Then add to handlers in `DaemonServer.handle_request()`:
```python
handlers = {
    ...
    "my_command": lambda: self.hw_controller.my_custom_command(),
}
```

### Extend API Endpoints

Edit `api_gateway_daemon.py` and add to `APIHandler.do_GET()`:
```python
elif path == "/api/my/endpoint":
    self.handle_my_endpoint()
```

## Security Considerations

1. **API Access:** The API listens only on localhost (127.0.0.1). To expose externally, modify `API_HOST` in the code.

2. **API Keys:** Store API keys securely. Never commit them to git or share publicly.

3. **Socket Permissions:** The Unix socket is created with 0666 permissions. Consider restricting to 0660 and specific group.

4. **AI Safety:** The AI orchestrator includes safety checks for dangerous commands. Review before running AI-suggested commands.

## Uninstallation

To remove SOS:

```bash
# Stop services
adb shell "su -c '/bin/sh /data/rayhunter/sos_manager.sh stop'"

# Remove native files
adb shell "su -c 'rm /data/rayhunter/hw_ctl_daemon.py'"
adb shell "su -c 'rm /data/rayhunter/api_gateway_daemon.py'"
adb shell "su -c 'rm /data/rayhunter/sos_manager.sh'"

# Remove Alpine files
adb shell "su -c 'rm /data/alpine/usr/local/bin/ai_orchestrator.py'"
adb shell "su -c 'rm -rf /data/alpine/etc/sos'"

# Restore original wrapper (if using SOS wrapper)
adb shell "su -c 'cp /data/rayhunter/wrapper_v4.sh.bak /data/rayhunter/wrapper_v4.sh'"
```

## Next Steps

After successful installation:

1. Read [SOS_QUICKSTART.md](SOS_QUICKSTART.md) for usage examples
2. Read [SOS_DOCUMENTATION.md](SOS_DOCUMENTATION.md) for full reference
3. Experiment with API endpoints
4. Try AI interactive mode
5. Build custom integrations

## Support

For issues:
- Check logs in `/data/rayhunter/`
- Run test script: `./tools/test_sos.sh`
- Review [SOS_DOCUMENTATION.md](SOS_DOCUMENTATION.md)
- Open GitHub issue with logs

---

**Installation complete!** SOS is now ready to use. 🚀
