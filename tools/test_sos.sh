#!/bin/bash
################################################################################
# SOS Test Script
#
# Purpose: Test SOS installation and functionality
# Usage: ./test_sos.sh
#
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASSED=0
FAILED=0

log() {
    echo -e "${GREEN}[+]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[!]${NC} $1"
}

error() {
    echo -e "${RED}[-]${NC} $1"
}

info() {
    echo -e "${BLUE}[*]${NC} $1"
}

test_passed() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASSED++))
}

test_failed() {
    echo -e "${RED}✗${NC} $1"
    ((FAILED++))
}

echo "=========================================="
echo "SOS System Test Suite"
echo "=========================================="
echo ""

# Test 1: ADB Connection
info "Test 1: Checking ADB connection..."
if adb devices | grep -q "device$"; then
    test_passed "ADB connection working"
else
    test_failed "No ADB device connected"
    exit 1
fi

# Test 2: Root Access
info "Test 2: Checking root access..."
if adb shell "su -c 'id'" 2>/dev/null | grep -q "uid=0"; then
    test_passed "Root access available"
else
    test_failed "Root access not available"
    exit 1
fi

# Test 3: SOS Manager Script
info "Test 3: Checking SOS manager script..."
if adb shell "su -c 'test -f /data/rayhunter/sos_manager.sh'" 2>/dev/null; then
    test_passed "SOS manager script exists"
else
    test_failed "SOS manager script not found"
fi

# Test 4: Hardware Control Daemon
info "Test 4: Checking hardware control daemon..."
if adb shell "su -c 'test -f /data/rayhunter/hw_ctl_daemon.py'" 2>/dev/null; then
    test_passed "Hardware control daemon exists"
else
    test_failed "Hardware control daemon not found"
fi

# Test 5: API Gateway Daemon
info "Test 5: Checking API gateway daemon..."
if adb shell "su -c 'test -f /data/rayhunter/api_gateway_daemon.py'" 2>/dev/null; then
    test_passed "API gateway daemon exists"
else
    test_failed "API gateway daemon not found"
fi

# Test 6: Alpine Chroot
info "Test 6: Checking Alpine chroot..."
if adb shell "su -c 'test -d /data/alpine'" 2>/dev/null; then
    test_passed "Alpine chroot exists"
    
    # Test 7: AI Orchestrator
    info "Test 7: Checking AI orchestrator..."
    if adb shell "su -c 'test -f /data/alpine/usr/local/bin/ai_orchestrator.py'" 2>/dev/null; then
        test_passed "AI orchestrator exists"
    else
        test_failed "AI orchestrator not found"
    fi
else
    test_failed "Alpine chroot not found"
    warn "Skipping AI orchestrator test"
fi

# Test 8: Start SOS Services
info "Test 8: Starting SOS services..."
if adb shell "su -c '/bin/sh /data/rayhunter/sos_manager.sh start'" 2>/dev/null; then
    test_passed "SOS services started"
    sleep 3
else
    test_failed "Failed to start SOS services"
fi

# Test 9: Check Service Status
info "Test 9: Checking service status..."
STATUS_OUTPUT=$(adb shell "su -c '/bin/sh /data/rayhunter/sos_manager.sh status'" 2>/dev/null)
echo "$STATUS_OUTPUT"

if echo "$STATUS_OUTPUT" | grep -q "RUNNING"; then
    test_passed "At least one service is running"
else
    warn "No services appear to be running"
fi

# Test 10: API Health Check
info "Test 10: Testing API health endpoint..."
adb forward tcp:8888 tcp:8888 2>/dev/null
sleep 2

if command -v curl &> /dev/null; then
    HEALTH_RESPONSE=$(curl -s http://127.0.0.1:8888/api/health 2>/dev/null || echo "")
    if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
        test_passed "API health check successful"
        info "Response: $HEALTH_RESPONSE"
    else
        test_failed "API health check failed"
        warn "Response: $HEALTH_RESPONSE"
    fi
else
    warn "curl not found, skipping API test"
fi

# Test 11: WiFi Status API
if command -v curl &> /dev/null; then
    info "Test 11: Testing WiFi status API..."
    WIFI_RESPONSE=$(curl -s http://127.0.0.1:8888/api/wifi/status 2>/dev/null || echo "")
    if echo "$WIFI_RESPONSE" | grep -q "status"; then
        test_passed "WiFi status API working"
        info "WiFi interface detected"
    else
        warn "WiFi status API returned unexpected response"
    fi
fi

# Test 12: System Info API
if command -v curl &> /dev/null; then
    info "Test 12: Testing system info API..."
    SYS_RESPONSE=$(curl -s http://127.0.0.1:8888/api/system/info 2>/dev/null || echo "")
    if echo "$SYS_RESPONSE" | grep -q "uptime"; then
        test_passed "System info API working"
    else
        warn "System info API returned unexpected response"
    fi
fi

# Test 13: Log Files
info "Test 13: Checking log files..."
if adb shell "su -c 'test -f /data/rayhunter/hw_ctl_daemon.log'" 2>/dev/null; then
    test_passed "Hardware daemon log exists"
    
    # Show last 5 lines
    info "Last 5 lines of hardware daemon log:"
    adb shell "su -c 'tail -5 /data/rayhunter/hw_ctl_daemon.log'" 2>/dev/null | sed 's/^/  /'
fi

if adb shell "su -c 'test -f /data/rayhunter/api_gateway_daemon.log'" 2>/dev/null; then
    test_passed "API gateway log exists"
fi

# Test 14: Configuration Files
info "Test 14: Checking configuration files..."
if adb shell "su -c 'test -f /data/alpine/etc/sos/ai_config.json'" 2>/dev/null; then
    test_passed "AI configuration file exists"
else
    warn "AI configuration not found (optional)"
fi

# Summary
echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    echo ""
    log "SOS is ready to use"
    echo ""
    echo "Next steps:"
    echo "  1. Forward API port: adb forward tcp:8888 tcp:8888"
    echo "  2. Test API: curl http://127.0.0.1:8888/api/health"
    echo "  3. Configure AI keys (if needed)"
    echo "  4. See docs/SOS_QUICKSTART.md for usage"
    exit 0
else
    echo -e "${YELLOW}Some tests failed${NC}"
    echo ""
    warn "Review the output above and check:"
    echo "  1. All files are deployed correctly"
    echo "  2. Services are starting properly"
    echo "  3. Check logs for errors"
    echo ""
    echo "For help, see docs/SOS_DOCUMENTATION.md"
    exit 1
fi
