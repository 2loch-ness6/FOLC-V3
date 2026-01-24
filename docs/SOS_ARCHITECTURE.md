# SOS System Architecture

## Overview

This document provides a detailed technical architecture of the Service Orchestration System (SOS).

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Client Layer                                │
│  (Development Computer / External Applications)                  │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Web Browser  │  │ Python       │  │ CLI Tools    │         │
│  │ (curl/API)   │  │ Scripts      │  │ (sos_client) │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                 │                  │                   │
└─────────┼─────────────────┼──────────────────┼───────────────────┘
          │                 │                  │
          │        ADB Port Forwarding         │
          │        tcp:8888 → tcp:8888         │
          │                 │                  │
┌─────────▼─────────────────▼──────────────────▼───────────────────┐
│                    Transport Layer (ADB)                          │
│                  USB Connection to Device                         │
└───────────────────────────────────────────────────────────────────┘
          │
          │
┌─────────▼─────────────────────────────────────────────────────────┐
│                 Orbic Speed Device (RC400L)                        │
│ ┌───────────────────────────────────────────────────────────────┐ │
│ │              Native Environment (Qualcomm Linux)              │ │
│ │                                                               │ │
│ │  ┌──────────────────────────────────────────────────────┐   │ │
│ │  │          Hardware Control Daemon                      │   │ │
│ │  │          (hw_ctl_daemon.py)                          │   │ │
│ │  │                                                       │   │ │
│ │  │  • WiFi Interface Control (wlan0)                    │   │ │
│ │  │  • Cellular Modem Control (rmnet0)                   │   │ │
│ │  │  • Display/Framebuffer (/dev/fb0)                    │   │ │
│ │  │  • System Resource Monitoring                        │   │ │
│ │  │  • Input Device Management                           │   │ │
│ │  │                                                       │   │ │
│ │  │  Unix Socket: /tmp/hw_ctl.sock                       │   │ │
│ │  │  PID File: /data/rayhunter/hw_ctl_daemon.pid        │   │ │
│ │  │  Log: /data/rayhunter/hw_ctl_daemon.log             │   │ │
│ │  └────────────────────┬──────────────────────────────────┘   │ │
│ │                       │ Unix Socket IPC                       │ │
│ │  ┌────────────────────▼──────────────────────────────────┐   │ │
│ │  │          API Gateway Daemon                           │   │ │
│ │  │          (api_gateway_daemon.py)                     │   │ │
│ │  │                                                       │   │ │
│ │  │  HTTP REST API Server                                │   │ │
│ │  │  • Listens on 127.0.0.1:8888                        │   │ │
│ │  │  • JSON Request/Response                            │   │ │
│ │  │  • CORS Support                                      │   │ │
│ │  │                                                       │   │ │
│ │  │  Endpoints:                                          │   │ │
│ │  │  GET  /api/health                                    │   │ │
│ │  │  GET  /api/wifi/status                               │   │ │
│ │  │  GET  /api/wifi/scan                                 │   │ │
│ │  │  GET  /api/cellular/status                           │   │ │
│ │  │  GET  /api/display/info                              │   │ │
│ │  │  GET  /api/system/info                               │   │ │
│ │  │  POST /api/command                                   │   │ │
│ │  │                                                       │   │ │
│ │  │  PID File: /data/rayhunter/api_gateway_daemon.pid   │   │ │
│ │  │  Log: /data/rayhunter/api_gateway_daemon.log        │   │ │
│ │  └───────────────────────────────────────────────────────┘   │ │
│ │                                                               │ │
│ │  ┌───────────────────────────────────────────────────────┐   │ │
│ │  │          SOS Manager (sos_manager.sh)                │   │ │
│ │  │          Service Lifecycle Management                │   │ │
│ │  │                                                       │   │ │
│ │  │  Commands: start | stop | restart | status          │   │ │
│ │  └───────────────────────────────────────────────────────┘   │ │
│ │                                                               │ │
│ └───────────────────────────────────────────────────────────────┘ │
│                                                                   │
│ ┌───────────────────────────────────────────────────────────────┐ │
│ │         Alpine Linux Chroot (/data/alpine)                   │ │
│ │                                                               │ │
│ │  ┌───────────────────────────────────────────────────────┐   │ │
│ │  │         AI Orchestrator (ai_orchestrator.py)         │   │ │
│ │  │                                                       │   │ │
│ │  │  Natural Language Processing & Task Automation       │   │ │
│ │  │                                                       │   │ │
│ │  │  ┌─────────────────┐    ┌──────────────────────┐    │   │ │
│ │  │  │  Gemini         │    │   Claude             │    │   │ │
│ │  │  │  Provider       │    │   Provider           │    │   │ │
│ │  │  │                 │    │                      │    │   │ │
│ │  │  │  CLI: gemini    │    │   CLI: claude        │    │   │ │
│ │  │  │  API Key: ENV   │    │   API Key: ENV       │    │   │ │
│ │  │  └─────────────────┘    └──────────────────────┘    │   │ │
│ │  │                                                       │   │ │
│ │  │  Features:                                           │   │ │
│ │  │  • Natural language command processing               │   │ │
│ │  │  • Context-aware responses                          │   │ │
│ │  │  • API call orchestration                           │   │ │
│ │  │  • Automatic provider fallback                      │   │ │
│ │  │  • Interactive mode                                 │   │ │
│ │  │  • Safety constraints                               │   │ │
│ │  │                                                       │   │ │
│ │  │  Config: /etc/sos/ai_config.json                    │   │ │
│ │  │  Log: /var/log/ai_orchestrator.log                  │   │ │
│ │  └───────────────────────────────────────────────────────┘   │ │
│ │                                                               │ │
│ │  ┌───────────────────────────────────────────────────────┐   │ │
│ │  │         Security Toolkit                             │   │ │
│ │  │                                                       │   │ │
│ │  │  • aircrack-ng    • nmap        • tcpdump           │   │ │
│ │  │  • scapy          • wireshark   • iw                │   │ │
│ │  │  • python3        • pip         • apk                │   │ │
│ │  └───────────────────────────────────────────────────────┘   │ │
│ └───────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Hardware Control Daemon

**File:** `src/sos/daemons/hw_ctl_daemon.py`

**Location:** `/data/rayhunter/hw_ctl_daemon.py` (Native)

**Purpose:** Low-level hardware abstraction layer

**Communication:** Unix domain socket (`/tmp/hw_ctl.sock`)

**Responsibilities:**
- Direct hardware access via kernel interfaces
- WiFi control using `iw` commands
- Cellular modem status via `ip` commands
- Framebuffer management
- System resource monitoring (`/proc` filesystem)

**Key Classes:**
- `HardwareController`: Hardware operations implementation
- `DaemonServer`: Unix socket server for IPC

### 2. API Gateway Daemon

**File:** `src/sos/daemons/api_gateway_daemon.py`

**Location:** `/data/rayhunter/api_gateway_daemon.py` (Native)

**Purpose:** HTTP REST API interface

**Communication:** HTTP on `127.0.0.1:8888`

**Responsibilities:**
- REST API endpoint handling
- Request routing and validation
- JSON serialization/deserialization
- Communication with hardware daemon
- CORS support for web access

**Key Classes:**
- `APIHandler`: HTTP request handler
- `HardwareClient`: Unix socket client
- `APIGatewayServer`: HTTP server wrapper

### 3. AI Orchestrator

**File:** `src/sos/ai/ai_orchestrator.py`

**Location:** `/data/alpine/usr/local/bin/ai_orchestrator.py` (Alpine)

**Purpose:** AI-powered automation and orchestration

**Communication:** HTTP client to API Gateway

**Responsibilities:**
- Natural language processing
- AI provider management (Gemini/Claude)
- System context aggregation
- Command interpretation
- Task automation
- Interactive user interface

**Key Classes:**
- `AIOrchestrator`: Main orchestration logic
- `GeminiProvider`: Gemini AI integration
- `ClaudeProvider`: Claude AI integration
- `APIClient`: HTTP client for API calls
- `AIConfig`: Configuration management

### 4. SOS Manager

**File:** `src/sos/sos_manager.sh`

**Location:** `/data/rayhunter/sos_manager.sh` (Native)

**Purpose:** Service lifecycle management

**Commands:**
- `start`: Start all SOS services
- `stop`: Stop all SOS services
- `restart`: Restart all SOS services
- `status`: Display service status

**Managed Services:**
- Hardware Control Daemon
- API Gateway Daemon
- AI Orchestrator (status only)

## Data Flow

### API Request Flow

```
Client → ADB Forward → API Gateway → Hardware Daemon → System
  ↑                                                         ↓
  └─────────────────── JSON Response ←──────────────────────┘
```

1. Client sends HTTP request to `http://127.0.0.1:8888/api/*`
2. ADB forwards port 8888 to device
3. API Gateway receives request
4. API Gateway connects to Hardware Daemon via Unix socket
5. Hardware Daemon executes system command
6. Response flows back through the chain
7. Client receives JSON response

### AI Query Flow

```
User → AI Orchestrator → AI Provider (Gemini/Claude)
  ↑            ↓
  │         Context Aggregation
  │            ↓
  │      API Gateway → Hardware Daemon
  │            ↓
  └──────── Response with Action Plan
```

1. User enters natural language query
2. AI Orchestrator gathers system context
3. Query + context sent to AI provider
4. AI provider returns structured response
5. If action required, orchestrator calls APIs
6. Results aggregated and returned to user

## Inter-Process Communication

### Native Environment (Unix Sockets)

Hardware Daemon ←→ API Gateway:
- Protocol: JSON over Unix domain socket
- Socket: `/tmp/hw_ctl.sock`
- Format: `{"command": "...", "params": {...}}`

### Cross-Environment (HTTP)

Alpine Chroot ←→ Native:
- Protocol: HTTP REST API
- Endpoint: `http://127.0.0.1:8888/api/*`
- Format: JSON request/response

## Security Model

### Access Control

1. **API Gateway:**
   - Binds to localhost only (127.0.0.1)
   - No authentication (localhost trust model)
   - Access via ADB port forwarding

2. **Unix Socket:**
   - Permissions: 0666 (world-writable)
   - Location: /tmp (tmpfs, memory-only)
   - No authentication required

3. **AI Orchestrator:**
   - API keys stored in environment variables
   - Safety checks for dangerous commands
   - Rate limiting on API calls
   - Confirmation required for destructive ops

### Trust Boundaries

```
┌─────────────────────────────────────────┐
│  External World                          │
│  (Untrusted)                            │
└─────────────┬───────────────────────────┘
              │
        ADB Connection
              │
┌─────────────▼───────────────────────────┐
│  Native Environment                      │
│  (Trusted - Root Required)              │
│                                          │
│  API Gateway ←→ Hardware Daemon         │
└─────────────┬───────────────────────────┘
              │
      HTTP/Unix Socket
              │
┌─────────────▼───────────────────────────┐
│  Alpine Chroot                           │
│  (Semi-Trusted - Isolated)              │
│                                          │
│  AI Orchestrator + Tools                │
└──────────────────────────────────────────┘
```

## File System Layout

```
/data/rayhunter/              # Native daemon location
├── hw_ctl_daemon.py          # Hardware control daemon
├── hw_ctl_daemon.pid         # PID file
├── hw_ctl_daemon.log         # Log file
├── api_gateway_daemon.py     # API gateway daemon
├── api_gateway_daemon.pid    # PID file
├── api_gateway_daemon.log    # Log file
├── sos_manager.sh            # Service manager
└── wrapper_sos.sh            # Enhanced wrapper (optional)

/data/alpine/                 # Alpine chroot root
├── usr/
│   └── local/
│       └── bin/
│           └── ai_orchestrator.py  # AI orchestrator
├── etc/
│   └── sos/
│       └── ai_config.json    # AI configuration
└── var/
    └── log/
        └── ai_orchestrator.log     # AI log

/tmp/                         # Temporary files
└── hw_ctl.sock              # Unix socket (runtime)
```

## Configuration

### AI Configuration (`/data/alpine/etc/sos/ai_config.json`)

```json
{
  "gemini": {
    "enabled": true,
    "model": "gemini-pro",
    "api_key_env": "GEMINI_API_KEY",
    "cli_path": "/usr/local/bin/gemini"
  },
  "claude": {
    "enabled": true,
    "model": "claude-3-sonnet-20240229",
    "api_key_env": "ANTHROPIC_API_KEY",
    "cli_path": "/usr/local/bin/claude"
  },
  "preferred_provider": "gemini",
  "fallback_enabled": true,
  "safety": {
    "require_confirmation": true,
    "max_api_calls_per_minute": 30
  }
}
```

### Environment Variables (Alpine)

```bash
# In /root/.profile or /root/.bashrc
export GEMINI_API_KEY="your-api-key"
export ANTHROPIC_API_KEY="your-api-key"
```

## Performance Characteristics

### Resource Usage

| Component | RAM Usage | CPU Usage | Startup Time |
|-----------|-----------|-----------|--------------|
| HW Daemon | 5-10 MB | <1% | <1 sec |
| API Gateway | 8-15 MB | <1% | <1 sec |
| AI Orchestrator | 20-50 MB | Varies | 2-3 sec |

### Response Times

| Operation | Typical Response | Notes |
|-----------|-----------------|-------|
| API Health Check | <10 ms | Local socket |
| WiFi Status | 50-100 ms | System query |
| WiFi Scan | 2-5 seconds | Hardware scan |
| System Info | 10-50 ms | /proc read |
| AI Query | 2-10 seconds | Network dependent |

## Error Handling

### Hardware Daemon

- Socket connection errors → Log and continue
- Command failures → Return error JSON
- Timeout → 5 second default timeout
- Invalid JSON → Log and skip request

### API Gateway

- Hardware daemon unreachable → HTTP 500 error
- Invalid endpoint → HTTP 404 error
- Malformed request → HTTP 400 error
- Timeout → HTTP 504 error

### AI Orchestrator

- API key missing → Skip provider
- Provider unavailable → Try fallback
- Network error → Retry with exponential backoff
- Invalid response → Return error to user

## Logging

### Log Levels

- INFO: Normal operations
- WARNING: Recoverable errors
- ERROR: Serious errors
- DEBUG: Detailed diagnostics (not used in production)

### Log Rotation

Currently no automatic rotation. Logs grow indefinitely.

**Recommendation:** Implement logrotate or manual cleanup:
```bash
# Truncate logs when too large
if [ $(stat -f%z /data/rayhunter/hw_ctl_daemon.log) -gt 10485760 ]; then
    > /data/rayhunter/hw_ctl_daemon.log
fi
```

## Extension Points

### Adding Hardware Commands

1. Add method to `HardwareController` class
2. Add handler to `DaemonServer.handle_request()`
3. Add API endpoint to `APIHandler`

### Adding AI Providers

1. Create new provider class (inherit pattern)
2. Implement `is_available()` and `query()` methods
3. Register in `AIOrchestrator.__init__()`

### Adding API Endpoints

1. Add handler method to `APIHandler`
2. Route in `do_GET()` or `do_POST()`
3. Document in API reference

## Dependencies

### Native Environment

- Python 3.x
- busybox utilities
- iw (WiFi control)
- ip (network interfaces)
- fbset (optional, framebuffer)

### Alpine Chroot

- Python 3.x
- pip (package manager)
- google-generativeai (Gemini)
- anthropic (Claude)
- curl (HTTP client)

## Deployment

See [SOS_INSTALLATION.md](SOS_INSTALLATION.md) for detailed deployment instructions.

## Maintenance

### Regular Tasks

1. **Log Management:** Clear/rotate logs periodically
2. **API Key Rotation:** Update keys when expired
3. **Version Updates:** Keep AI provider packages updated
4. **Security Patches:** Update Alpine packages

### Monitoring

Check service status:
```bash
/bin/sh /data/rayhunter/sos_manager.sh status
```

View logs:
```bash
tail -f /data/rayhunter/hw_ctl_daemon.log
tail -f /data/rayhunter/api_gateway_daemon.log
tail -f /data/alpine/var/log/ai_orchestrator.log
```

## Future Enhancements

See roadmap in [SOS_DOCUMENTATION.md](SOS_DOCUMENTATION.md#future-enhancements).

---

**Version:** 1.0  
**Last Updated:** January 2026
