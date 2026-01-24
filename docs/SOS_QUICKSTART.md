# SOS Quick Start Guide

## Overview

The Service Orchestration System (SOS) adds AI-powered automation and comprehensive service management to FOLC-V3.

## What is SOS?

SOS is a layered system with:
- **Native daemons** running directly on the device hardware
- **AI services** running in the Alpine Linux chroot
- **REST APIs** for programmatic control
- **AI integration** via Gemini and Claude CLI

## Quick Setup (5 minutes)

### 1. Prerequisites

Ensure you have:
- ✅ Rooted Orbic Speed device
- ✅ Alpine Linux chroot installed
- ✅ ADB connection working
- ✅ Basic FOLC-V3 setup complete

### 2. Deploy SOS

```bash
cd FOLC-V3
./tools/deploy_sos.sh
```

This installs everything automatically.

### 3. Get API Keys (Optional for AI features)

To use AI capabilities:

1. **Gemini API Key:**
   - Visit: https://makersuite.google.com/app/apikey
   - Create an API key
   - Copy it for next step

2. **Claude API Key:**
   - Visit: https://console.anthropic.com/
   - Create an API key
   - Copy it for next step

### 4. Configure AI (if using AI features)

```bash
# Connect to device
adb shell

# Enter Alpine chroot as root
su -c 'chroot /data/alpine /bin/sh'

# Set API keys
echo 'export GEMINI_API_KEY="your-key-here"' >> /root/.profile
echo 'export ANTHROPIC_API_KEY="your-key-here"' >> /root/.profile

# Apply changes
source /root/.profile

# Test
echo $GEMINI_API_KEY
```

## Basic Usage

### Start SOS

```bash
adb shell "su -c '/bin/sh /data/rayhunter/sos_manager.sh start'"
```

### Check Status

```bash
adb shell "su -c '/bin/sh /data/rayhunter/sos_manager.sh status'"
```

Expected output:
```
==========================================
SOS (Service Orchestration System) Status
==========================================

Native Environment Daemons:
--------------------------
✓ Hardware Control Daemon: RUNNING (PID: 1234)
✓ API Gateway Daemon: RUNNING (PID: 1235)
  API URL: http://127.0.0.1:8888/api/

Alpine Chroot Environment:
-------------------------
✓ AI Orchestrator: AVAILABLE
  Run: chroot /data/alpine /usr/local/bin/ai_orchestrator.py --interactive
...
```

### Use the API

```bash
# Forward API port to your computer
adb forward tcp:8888 tcp:8888

# Test endpoints
curl http://127.0.0.1:8888/api/health
curl http://127.0.0.1:8888/api/wifi/status
curl http://127.0.0.1:8888/api/wifi/scan
curl http://127.0.0.1:8888/api/system/info
```

### Interactive AI Mode (if configured)

```bash
adb shell "su -c 'chroot /data/alpine /usr/local/bin/ai_orchestrator.py --interactive'"
```

Try commands like:
- `scan wifi networks`
- `show system status`
- `what is the current load?`
- `help me optimize network`

## Common Tasks

### WiFi Scanning

```bash
curl http://127.0.0.1:8888/api/wifi/scan
```

### System Monitoring

```bash
curl http://127.0.0.1:8888/api/system/info
```

### Check Cellular Status

```bash
curl http://127.0.0.1:8888/api/cellular/status
```

## Troubleshooting

### "Connection refused" error

Start SOS:
```bash
adb shell "su -c '/bin/sh /data/rayhunter/sos_manager.sh start'"
```

### Daemons won't start

Check logs:
```bash
adb shell "su -c 'cat /data/rayhunter/hw_ctl_daemon.log'"
adb shell "su -c 'cat /data/rayhunter/api_gateway_daemon.log'"
```

### AI not working

1. Check API keys are set:
```bash
adb shell "su -c 'chroot /data/alpine /bin/sh -c \"env | grep API_KEY\"'"
```

2. Install AI packages:
```bash
adb shell "su -c 'chroot /data/alpine /bin/sh'"
# In chroot:
pip3 install google-generativeai anthropic
```

## Integration with FOLC

### Auto-start on boot

Edit `/data/rayhunter/wrapper_v4.sh` and add:

```bash
# Start SOS
if [ -f /data/rayhunter/sos_manager.sh ]; then
    /bin/sh /data/rayhunter/sos_manager.sh start &
fi
```

### Use in Python scripts

```python
import requests

# Get WiFi networks
response = requests.get('http://127.0.0.1:8888/api/wifi/scan')
networks = response.json()['networks']

for net in networks:
    print(f"{net['ssid']}: {net['signal']}")
```

## Next Steps

1. **Read full documentation:** `docs/SOS_DOCUMENTATION.md`
2. **Explore API endpoints:** Try all available endpoints
3. **Experiment with AI:** Use interactive mode for automation
4. **Integrate with your workflow:** Build custom scripts

## Key Files

- `/data/rayhunter/sos_manager.sh` - Main control script
- `/data/rayhunter/hw_ctl_daemon.py` - Hardware control
- `/data/rayhunter/api_gateway_daemon.py` - API server
- `/data/alpine/usr/local/bin/ai_orchestrator.py` - AI service
- `/data/alpine/etc/sos/ai_config.json` - AI configuration

## Support

For issues or questions:
- Check `docs/SOS_DOCUMENTATION.md`
- Review logs in `/data/rayhunter/*.log`
- Open GitHub issue with logs attached

---

**Tip:** Start small - get the API working first, then add AI capabilities later.
