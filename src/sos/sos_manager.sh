#!/bin/sh
################################################################################
# SOS Manager - Service Orchestration System Manager
#
# Purpose: Manage all SOS daemons and services
# Location: /data/rayhunter/sos_manager.sh
#
# Usage:
#   sos_manager.sh start   - Start all SOS services
#   sos_manager.sh stop    - Stop all SOS services
#   sos_manager.sh restart - Restart all SOS services
#   sos_manager.sh status  - Check service status
#
################################################################################

LOG_FILE="/data/rayhunter/sos_manager.log"
NATIVE_ENV="/data/rayhunter"
ALPINE_ROOT="/data/alpine"

# Daemon paths (native environment)
HW_CTL_DAEMON="${NATIVE_ENV}/hw_ctl_daemon.py"
API_GATEWAY_DAEMON="${NATIVE_ENV}/api_gateway_daemon.py"

# AI orchestrator (Alpine chroot)
AI_ORCHESTRATOR="${ALPINE_ROOT}/usr/local/bin/ai_orchestrator.py"

# PID files
HW_CTL_PID="/data/rayhunter/hw_ctl_daemon.pid"
API_GATEWAY_PID="/data/rayhunter/api_gateway_daemon.pid"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

check_process() {
    PID_FILE=$1
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            return 0  # Running
        else
            rm -f "$PID_FILE"
            return 1  # Not running
        fi
    fi
    return 1  # No PID file
}

start_hw_ctl() {
    log "Starting Hardware Control Daemon..."
    if check_process "$HW_CTL_PID"; then
        log "Hardware Control Daemon already running"
        return 0
    fi
    
    if [ -f "$HW_CTL_DAEMON" ]; then
        python3 "$HW_CTL_DAEMON" &
        sleep 2
        if check_process "$HW_CTL_PID"; then
            log "Hardware Control Daemon started successfully"
            return 0
        else
            log "ERROR: Failed to start Hardware Control Daemon"
            return 1
        fi
    else
        log "ERROR: Hardware Control Daemon not found at $HW_CTL_DAEMON"
        return 1
    fi
}

start_api_gateway() {
    log "Starting API Gateway Daemon..."
    if check_process "$API_GATEWAY_PID"; then
        log "API Gateway Daemon already running"
        return 0
    fi
    
    if [ -f "$API_GATEWAY_DAEMON" ]; then
        python3 "$API_GATEWAY_DAEMON" &
        sleep 2
        if check_process "$API_GATEWAY_PID"; then
            log "API Gateway Daemon started successfully"
            return 0
        else
            log "ERROR: Failed to start API Gateway Daemon"
            return 1
        fi
    else
        log "ERROR: API Gateway Daemon not found at $API_GATEWAY_DAEMON"
        return 1
    fi
}

start_ai_orchestrator() {
    log "Starting AI Orchestrator (in Alpine chroot)..."
    
    if [ ! -d "$ALPINE_ROOT" ]; then
        log "ERROR: Alpine root not found at $ALPINE_ROOT"
        return 1
    fi
    
    # AI orchestrator runs as a service in Alpine
    # We'll start it via chroot
    if [ -f "$AI_ORCHESTRATOR" ]; then
        log "AI Orchestrator available at $AI_ORCHESTRATOR"
        log "To use AI features, run: chroot $ALPINE_ROOT /usr/local/bin/ai_orchestrator.py --interactive"
        return 0
    else
        log "WARNING: AI Orchestrator not found at $AI_ORCHESTRATOR"
        log "AI features will be limited"
        return 0
    fi
}

stop_daemon() {
    DAEMON_NAME=$1
    PID_FILE=$2
    
    if check_process "$PID_FILE"; then
        PID=$(cat "$PID_FILE")
        log "Stopping $DAEMON_NAME (PID: $PID)..."
        kill "$PID" 2>/dev/null
        sleep 2
        
        # Force kill if still running
        if kill -0 "$PID" 2>/dev/null; then
            log "Force killing $DAEMON_NAME..."
            kill -9 "$PID" 2>/dev/null
        fi
        
        rm -f "$PID_FILE"
        log "$DAEMON_NAME stopped"
    else
        log "$DAEMON_NAME not running"
    fi
}

start_all() {
    log "=========================================="
    log "Starting SOS (Service Orchestration System)"
    log "=========================================="
    
    # Start native daemons
    start_hw_ctl
    start_api_gateway
    
    # Setup AI orchestrator
    start_ai_orchestrator
    
    log "=========================================="
    log "SOS startup complete"
    log "=========================================="
}

stop_all() {
    log "=========================================="
    log "Stopping SOS (Service Orchestration System)"
    log "=========================================="
    
    stop_daemon "API Gateway Daemon" "$API_GATEWAY_PID"
    stop_daemon "Hardware Control Daemon" "$HW_CTL_PID"
    
    log "=========================================="
    log "SOS shutdown complete"
    log "=========================================="
}

status_all() {
    echo "=========================================="
    echo "SOS (Service Orchestration System) Status"
    echo "=========================================="
    
    echo ""
    echo "Native Environment Daemons:"
    echo "--------------------------"
    
    if check_process "$HW_CTL_PID"; then
        PID=$(cat "$HW_CTL_PID")
        echo "✓ Hardware Control Daemon: RUNNING (PID: $PID)"
    else
        echo "✗ Hardware Control Daemon: STOPPED"
    fi
    
    if check_process "$API_GATEWAY_PID"; then
        PID=$(cat "$API_GATEWAY_PID")
        echo "✓ API Gateway Daemon: RUNNING (PID: $PID)"
        echo "  API URL: http://127.0.0.1:8888/api/"
    else
        echo "✗ API Gateway Daemon: STOPPED"
    fi
    
    echo ""
    echo "Alpine Chroot Environment:"
    echo "-------------------------"
    
    if [ -f "$AI_ORCHESTRATOR" ]; then
        echo "✓ AI Orchestrator: AVAILABLE"
        echo "  Run: chroot $ALPINE_ROOT /usr/local/bin/ai_orchestrator.py --interactive"
    else
        echo "✗ AI Orchestrator: NOT INSTALLED"
    fi
    
    echo ""
    echo "API Endpoints:"
    echo "-------------"
    echo "  GET  /api/health          - Health check"
    echo "  GET  /api/wifi/status     - WiFi status"
    echo "  GET  /api/wifi/scan       - WiFi scan"
    echo "  GET  /api/cellular/status - Cellular status"
    echo "  GET  /api/display/info    - Display info"
    echo "  GET  /api/system/info     - System info"
    echo "  POST /api/command         - Custom command"
    echo ""
    echo "=========================================="
}

case "$1" in
    start)
        start_all
        ;;
    stop)
        stop_all
        ;;
    restart)
        stop_all
        sleep 2
        start_all
        ;;
    status)
        status_all
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac

exit 0
