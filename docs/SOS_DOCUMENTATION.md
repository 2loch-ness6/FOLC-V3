# SOS: Service Orchestration System

## Overview

The **Service Orchestration System (SOS)** is a comprehensive, dynamic, automated, AI-powered service management system for the FOLC-V3 project. It provides intelligent hardware control, automated system management, and AI-driven operations for the Orbic Speed device.

## Architecture

### System Design

```
┌─────────────────────────────────────────────────────────┐
│                    Native Environment                    │
│  ┌───────────────────────┐  ┌────────────────────────┐ │
│  │  Hardware Control     │  │   API Gateway          │ │
│  │  Daemon               │  │   Daemon               │ │
│  │  (hw_ctl_daemon.py)   │  │   (api_gateway_daemon) │ │
│  │                       │  │                        │ │
│  │  - WiFi Control       │  │   REST API Server      │ │
│  │  - Cellular Modem     │  │   Port: 8888           │ │
│  │  - Display/FB         │  │                        │ │
│  │  - System Monitoring  │  │   Endpoints:           │ │
│  │                       │  │   - /api/wifi/*        │ │
│  │  Unix Socket:         │  │   - /api/cellular/*    │ │
│  │  /tmp/hw_ctl.sock     │  │   - /api/system/*      │ │
│  └───────────┬───────────┘  └────────┬───────────────┘ │
│              │                       │                  │
└──────────────┼───────────────────────┼──────────────────┘
               │                       │
               │    Communication      │
               │    via Unix Socket    │
               │    & HTTP             │
               │                       │
┌──────────────┼───────────────────────┼──────────────────┐
│              │   Alpine Chroot       │                  │
│              │   (/data/alpine)      │                  │
│              │                       │                  │
│  ┌───────────▼───────────────────────▼───────────────┐ │
│  │          AI Orchestrator                          │ │
│  │          (ai_orchestrator.py)                     │ │
│  │                                                    │ │
│  │  ┌─────────────────┐    ┌──────────────────────┐ │ │
│  │  │  Gemini CLI     │    │   Claude CLI         │ │ │
│  │  │  Integration    │    │   Integration        │ │ │
│  │  └─────────────────┘    └──────────────────────┘ │ │
│  │                                                    │ │
│  │  Features:                                         │ │
│  │  - Natural Language Processing                    │ │
│  │  - Command Interpretation                         │ │
│  │  - Task Automation                                │ │
│  │  - System Orchestration                           │ │
│  │  - API Call Management                            │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  Additional Tools:                                       │
│  - Security toolkit (aircrack-ng, nmap, tcpdump)        │
│  - Python environment                                    │
│  - Package manager (apk)                                 │
└──────────────────────────────────────────────────────────┘
```

## Components

### 1. Hardware Control Daemon (Native Environment)

**Location:** `/data/rayhunter/hw_ctl_daemon.py`

**Purpose:** Provides low-level hardware control and monitoring

**Features:**
- WiFi interface management
- Cellular modem control
- Display/framebuffer access
- System resource monitoring
- Unix socket API for IPC

**API:**
- `wifi_status` - Get WiFi interface status
- `wifi_scan` - Scan for WiFi networks
- `cellular_status` - Get cellular modem status
- `display_info` - Get display information
- `system_info` - Get system information

### 2. API Gateway Daemon (Native Environment)

**Location:** `/data/rayhunter/api_gateway_daemon.py`

**Purpose:** HTTP REST API server for system control

**Features:**
- RESTful API endpoints
- JSON request/response handling
- Integration with hardware daemon
- CORS support for web access
- Request logging and monitoring

**Endpoints:**
```
GET  /api/health          - Health check
GET  /api/wifi/status     - WiFi interface status
GET  /api/wifi/scan       - Scan WiFi networks
GET  /api/cellular/status - Cellular modem status
GET  /api/display/info    - Display information
GET  /api/system/info     - System information
POST /api/command         - Execute custom command
```

### 3. AI Orchestrator (Alpine Chroot)

**Location:** `/data/alpine/usr/local/bin/ai_orchestrator.py`

**Purpose:** AI-powered system orchestration and automation

**Features:**
- Natural language command processing
- Gemini CLI integration
- Claude CLI integration
- Automatic provider fallback
- Context-aware responses
- API call orchestration
- Interactive mode
- Task automation

**AI Providers:**

1. **Gemini (Google)**
   - Model: gemini-pro
   - CLI integration
   - Fast response time
   - General-purpose tasks

2. **Claude (Anthropic)**
   - Model: claude-3-sonnet
   - CLI integration
   - Complex reasoning
   - Safety-focused

### 4. SOS Manager

**Location:** `/data/rayhunter/sos_manager.sh`

**Purpose:** Service lifecycle management

**Commands:**
```bash
sos_manager.sh start   # Start all services
sos_manager.sh stop    # Stop all services
sos_manager.sh restart # Restart all services
sos_manager.sh status  # Check service status
```

## Installation

### Prerequisites

1. Rooted Orbic Speed (RC400L) device
2. Alpine Linux chroot installed
3. ADB access to device
4. Python 3 installed in both environments

### Deployment

Run the deployment script:

```bash
cd FOLC-V3
./tools/deploy_sos.sh
```

The script will:
1. Verify ADB connection and root access
2. Deploy native environment daemons
3. Deploy Alpine chroot AI services
4. Set up configuration files
5. Test the deployment

### Manual Installation

If automatic deployment fails, follow these steps:

1. **Deploy Native Daemons:**
```bash
adb push src/sos/daemons/hw_ctl_daemon.py /data/rayhunter/
adb push src/sos/daemons/api_gateway_daemon.py /data/rayhunter/
adb push src/sos/sos_manager.sh /data/rayhunter/
adb shell "su -c 'chmod +x /data/rayhunter/*.py /data/rayhunter/*.sh'"
```

2. **Deploy Alpine Services:**
```bash
adb push src/sos/ai/ai_orchestrator.py /data/alpine/usr/local/bin/
adb push src/sos/config/ai_config.json /data/alpine/etc/sos/
adb shell "su -c 'chmod +x /data/alpine/usr/local/bin/ai_orchestrator.py'"
```

3. **Install AI CLI Tools (in Alpine chroot):**
```bash
adb shell "su -c 'chroot /data/alpine /bin/sh'"
# Inside chroot:
apk add python3 py3-pip
pip3 install google-generativeai anthropic
```

4. **Configure API Keys:**
```bash
# Add to /data/alpine/root/.profile
export GEMINI_API_KEY='your-gemini-api-key'
export ANTHROPIC_API_KEY='your-anthropic-api-key'
```

## Usage

### Starting SOS

```bash
# Via ADB
adb shell "su -c '/bin/sh /data/rayhunter/sos_manager.sh start'"

# Or via device shell
su -c '/bin/sh /data/rayhunter/sos_manager.sh start'
```

### Checking Status

```bash
adb shell "su -c '/bin/sh /data/rayhunter/sos_manager.sh status'"
```

### Using the API

Forward the API port and make requests:

```bash
# Forward API port
adb forward tcp:8888 tcp:8888

# Test endpoints
curl http://127.0.0.1:8888/api/health
curl http://127.0.0.1:8888/api/wifi/status
curl http://127.0.0.1:8888/api/wifi/scan
curl http://127.0.0.1:8888/api/system/info
```

### Interactive AI Mode

```bash
# Enter Alpine chroot and start AI orchestrator
adb shell "su -c 'chroot /data/alpine /usr/local/bin/ai_orchestrator.py --interactive'"
```

**Example Session:**
```
AI Orchestrator - Interactive Mode
Type 'exit' to quit, 'help' for commands
--------------------------------------------------

> scan wifi networks

Scanning WiFi networks...
Found 5 networks:
1. MyNetwork (signal: -45 dBm)
2. Neighbor-WiFi (signal: -67 dBm)
...

> what is the system load?

Current system load: 0.15, 0.12, 0.08
Memory usage: 45% (231 MB / 512 MB)
Uptime: 2 days, 5 hours

> help me optimize network performance

Based on current WiFi scan, I recommend:
1. Switch to channel 6 (less congested)
2. Increase transmit power
3. Enable WiFi power management

Would you like me to apply these changes?
```

## Integration with FOLC-V3

### Automatic Startup

To start SOS automatically with system initialization, add to `/data/rayhunter/wrapper_v4.sh`:

```bash
# Start SOS (before FOLC UI)
if [ -f /data/rayhunter/sos_manager.sh ]; then
    echo "[-] Starting SOS..." >> $LOG
    /bin/sh /data/rayhunter/sos_manager.sh start &
fi
```

### FOLC UI Integration

The FOLC UI can be extended to use SOS APIs:

```python
import requests

# In folc_ui.py
def get_wifi_networks():
    response = requests.get('http://127.0.0.1:8888/api/wifi/scan')
    return response.json()['networks']
```

## Configuration

### AI Configuration

Edit `/data/alpine/etc/sos/ai_config.json`:

```json
{
  "gemini": {
    "enabled": true,
    "model": "gemini-pro",
    "api_key_env": "GEMINI_API_KEY"
  },
  "claude": {
    "enabled": true,
    "model": "claude-3-sonnet-20240229",
    "api_key_env": "ANTHROPIC_API_KEY"
  },
  "preferred_provider": "gemini",
  "fallback_enabled": true
}
```

### Daemon Configuration

Daemons use hardcoded configuration but can be modified:

**Hardware Daemon:**
- Socket: `/tmp/hw_ctl.sock`
- Log: `/data/rayhunter/hw_ctl_daemon.log`

**API Gateway:**
- Host: `127.0.0.1`
- Port: `8888`
- Log: `/data/rayhunter/api_gateway_daemon.log`

## Security Considerations

### Access Control

1. **API Gateway:** Listens only on localhost (127.0.0.1)
2. **Unix Socket:** Permissions set to 0666 (consider restricting)
3. **AI Commands:** Safety checks for dangerous operations

### API Keys

Store API keys securely:
```bash
# Never commit API keys to git
# Store in environment variables
# Use Alpine chroot's isolated environment
```

### Dangerous Commands

AI orchestrator includes safety constraints:
- Requires confirmation for dangerous operations
- Blocks destructive commands without validation
- Rate limiting on API calls

## Troubleshooting

### Daemons Not Starting

Check logs:
```bash
adb shell "su -c 'cat /data/rayhunter/hw_ctl_daemon.log'"
adb shell "su -c 'cat /data/rayhunter/api_gateway_daemon.log'"
```

### AI Not Responding

1. Check API keys:
```bash
adb shell "su -c 'chroot /data/alpine /bin/sh -c \"echo \$GEMINI_API_KEY\"'"
```

2. Test CLI tools:
```bash
adb shell "su -c 'chroot /data/alpine gemini --version'"
```

### API Not Accessible

1. Check if daemon is running:
```bash
adb shell "su -c '/bin/sh /data/rayhunter/sos_manager.sh status'"
```

2. Test locally on device:
```bash
adb shell "su -c 'wget -O- http://127.0.0.1:8888/api/health'"
```

3. Verify port forwarding:
```bash
adb forward tcp:8888 tcp:8888
curl http://127.0.0.1:8888/api/health
```

## Development

### Adding New API Endpoints

1. **Add handler in hw_ctl_daemon.py:**
```python
def new_operation(self):
    # Implementation
    return {"status": "success", "data": ...}
```

2. **Add command handler:**
```python
handlers = {
    ...
    "new_command": lambda: self.hw_controller.new_operation(),
}
```

3. **Add API endpoint in api_gateway_daemon.py:**
```python
elif path == "/api/new/endpoint":
    self.handle_new_endpoint()
```

### Extending AI Capabilities

Modify `ai_orchestrator.py` to add new AI capabilities:

```python
def process_specialized_task(self, task_type, params):
    # Custom AI processing
    return result
```

## Performance

### Resource Usage

- **Hardware Daemon:** ~5-10 MB RAM, minimal CPU
- **API Gateway:** ~8-15 MB RAM, minimal CPU
- **AI Orchestrator:** ~20-50 MB RAM, varies with AI calls

### Optimization

1. Adjust log levels in production
2. Implement caching for frequent API calls
3. Use connection pooling for HTTP requests
4. Batch AI queries when possible

## Future Enhancements

- [ ] WebSocket support for real-time updates
- [ ] Database integration for state persistence
- [ ] Advanced AI agent capabilities
- [ ] Scheduled task execution
- [ ] Web dashboard for remote management
- [ ] Multi-device orchestration
- [ ] Voice command integration
- [ ] Automated security scanning
- [ ] Machine learning model integration
- [ ] Cloud synchronization

## License

Part of the FOLC-V3 project. See main LICENSE file.

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/2loch-ness6/FOLC-V3/issues
- Documentation: See docs/ directory

---

**Last Updated:** January 2026
