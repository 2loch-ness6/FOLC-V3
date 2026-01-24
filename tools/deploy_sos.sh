#!/bin/bash
################################################################################
# SOS Deployment Script
#
# Purpose: Deploy the Service Orchestration System to Orbic Speed device
# Usage: ./deploy_sos.sh
#
################################################################################

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SOS_SRC="$PROJECT_ROOT/src/sos"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[+]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[!]${NC} $1"
}

error() {
    echo -e "${RED}[-]${NC} $1"
    exit 1
}

check_adb() {
    if ! command -v adb &> /dev/null; then
        error "ADB not found. Please install Android Debug Bridge."
    fi
    
    if ! adb devices | grep -q "device$"; then
        error "No device connected. Please connect Orbic Speed device."
    fi
    
    log "ADB connected successfully"
}

check_root() {
    log "Checking root access..."
    if ! adb shell "su -c 'id'" 2>/dev/null | grep -q "uid=0"; then
        error "Root access not available. Please root the device first."
    fi
    log "Root access confirmed"
}

deploy_native_daemons() {
    log "Deploying native environment daemons..."
    
    # Create directory structure
    adb shell "su -c 'mkdir -p /data/rayhunter'"
    
    # Push daemon files
    adb push "$SOS_SRC/daemons/hw_ctl_daemon.py" /data/rayhunter/
    adb push "$SOS_SRC/daemons/api_gateway_daemon.py" /data/rayhunter/
    adb push "$SOS_SRC/sos_manager.sh" /data/rayhunter/
    
    # Set permissions
    adb shell "su -c 'chmod +x /data/rayhunter/hw_ctl_daemon.py'"
    adb shell "su -c 'chmod +x /data/rayhunter/api_gateway_daemon.py'"
    adb shell "su -c 'chmod +x /data/rayhunter/sos_manager.sh'"
    
    log "Native daemons deployed successfully"
}

deploy_alpine_services() {
    log "Deploying Alpine chroot AI services..."
    
    # Check if Alpine is installed
    if ! adb shell "su -c 'test -d /data/alpine'" 2>/dev/null; then
        warn "Alpine Linux not found. Skipping Alpine deployment."
        warn "Please install Alpine Linux first using setup.sh"
        return
    fi
    
    # Create Alpine directories
    adb shell "su -c 'mkdir -p /data/alpine/usr/local/bin'"
    adb shell "su -c 'mkdir -p /data/alpine/etc/sos'"
    adb shell "su -c 'mkdir -p /data/alpine/var/log'"
    
    # Push AI orchestrator
    adb push "$SOS_SRC/ai/ai_orchestrator.py" /data/alpine/usr/local/bin/
    adb shell "su -c 'chmod +x /data/alpine/usr/local/bin/ai_orchestrator.py'"
    
    # Push configuration
    adb push "$SOS_SRC/config/ai_config.json" /data/alpine/etc/sos/
    
    log "Alpine services deployed successfully"
}

setup_ai_cli() {
    log "Setting up AI CLI tools..."
    
    warn "AI CLI tools (Gemini/Claude) need to be installed manually."
    warn "Please follow these steps in the Alpine chroot:"
    echo ""
    echo "1. Install Gemini CLI:"
    echo "   pip install google-generativeai"
    echo "   # Or use official Gemini CLI if available"
    echo ""
    echo "2. Install Claude CLI:"
    echo "   pip install anthropic"
    echo "   # Or use official Claude CLI if available"
    echo ""
    echo "3. Set API keys:"
    echo "   export GEMINI_API_KEY='your-api-key'"
    echo "   export ANTHROPIC_API_KEY='your-api-key'"
    echo ""
    echo "4. Add to shell profile (~/.profile or ~/.bashrc):"
    echo "   echo 'export GEMINI_API_KEY=your-key' >> ~/.profile"
    echo ""
}

integrate_with_wrapper() {
    log "Integrating SOS with system initialization..."
    
    # Check if wrapper_v4.sh exists
    if ! adb shell "su -c 'test -f /data/rayhunter/wrapper_v4.sh'" 2>/dev/null; then
        warn "wrapper_v4.sh not found. SOS will need to be started manually."
        return
    fi
    
    warn "To integrate SOS with system startup:"
    echo "1. Edit /data/rayhunter/wrapper_v4.sh"
    echo "2. Add before launching FOLC UI:"
    echo "   # Start SOS"
    echo "   /bin/sh /data/rayhunter/sos_manager.sh start &"
    echo ""
}

test_deployment() {
    log "Testing SOS deployment..."
    
    # Test if files exist
    if ! adb shell "su -c 'test -f /data/rayhunter/sos_manager.sh'" 2>/dev/null; then
        error "Deployment verification failed"
    fi
    
    log "Deployment verified successfully"
    
    # Try to start services
    log "Attempting to start SOS services..."
    adb shell "su -c '/bin/sh /data/rayhunter/sos_manager.sh start'" 2>/dev/null || warn "Failed to start services automatically"
    
    sleep 3
    
    # Check status
    log "Checking SOS status..."
    adb shell "su -c '/bin/sh /data/rayhunter/sos_manager.sh status'"
}

show_usage() {
    echo ""
    log "SOS Deployment Complete!"
    echo ""
    echo "Usage:"
    echo "------"
    echo "Start SOS:   adb shell \"su -c '/bin/sh /data/rayhunter/sos_manager.sh start'\""
    echo "Stop SOS:    adb shell \"su -c '/bin/sh /data/rayhunter/sos_manager.sh stop'\""
    echo "Status:      adb shell \"su -c '/bin/sh /data/rayhunter/sos_manager.sh status'\""
    echo ""
    echo "AI Interactive Mode:"
    echo "-------------------"
    echo "adb shell \"su -c 'chroot /data/alpine /usr/local/bin/ai_orchestrator.py --interactive'\""
    echo ""
    echo "API Endpoints:"
    echo "-------------"
    echo "Health Check: curl http://127.0.0.1:8888/api/health"
    echo "WiFi Status:  curl http://127.0.0.1:8888/api/wifi/status"
    echo "WiFi Scan:    curl http://127.0.0.1:8888/api/wifi/scan"
    echo "System Info:  curl http://127.0.0.1:8888/api/system/info"
    echo ""
}

main() {
    echo "=========================================="
    echo "SOS Deployment Script"
    echo "Service Orchestration System for FOLC-V3"
    echo "=========================================="
    echo ""
    
    check_adb
    check_root
    
    deploy_native_daemons
    deploy_alpine_services
    setup_ai_cli
    integrate_with_wrapper
    
    test_deployment
    
    show_usage
}

main
