#!/bin/bash
################################################################################
# FOLC-V3 Comprehensive Test Suite
#
# Purpose: Test all functionality of the FOLC-V3 system on Android 14
# Environment: Termux or Kali Linux Chroot on Android 14
# Requirements: ADB binary at /bin/adb (Magisk-provided)
#
# Author: FOLC-V3 Project
# Version: 1.0
# Date: January 2026
################################################################################

# Note: We don't use 'set -e' here because test failures should not abort the suite
# Instead, we track pass/fail for each test explicitly

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
LOG_DIR="/tmp/folc_test_logs"
LOG_FILE="$LOG_DIR/test_$(date +%Y%m%d_%H%M%S).log"
ADB_BIN="/bin/adb"
DEVICE_SERIAL=""
TEST_RESULTS=()

# Counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0

################################################################################
# Logging Functions
################################################################################

setup_logging() {
    mkdir -p "$LOG_DIR"
    echo "FOLC-V3 Test Suite - $(date)" > "$LOG_FILE"
    echo "========================================" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"
}

log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
    
    case "$level" in
        INFO)
            echo -e "${CYAN}[INFO]${NC} $message"
            ;;
        PASS)
            echo -e "${GREEN}[PASS]${NC} $message"
            ;;
        FAIL)
            echo -e "${RED}[FAIL]${NC} $message"
            ;;
        WARN)
            echo -e "${YELLOW}[WARN]${NC} $message"
            ;;
        SKIP)
            echo -e "${YELLOW}[SKIP]${NC} $message"
            ;;
        *)
            echo "[$level] $message"
            ;;
    esac
}

print_header() {
    local title="$1"
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║ $title${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    log INFO "=== $title ==="
}

################################################################################
# Test Framework
################################################################################

test_assert() {
    local test_name="$1"
    local condition="$2"
    local error_msg="${3:-Test failed}"
    
    ((TESTS_RUN++))
    
    if eval "$condition"; then
        log PASS "$test_name"
        TEST_RESULTS+=("✓ $test_name")
        ((TESTS_PASSED++))
        return 0
    else
        log FAIL "$test_name: $error_msg"
        TEST_RESULTS+=("✗ $test_name: $error_msg")
        ((TESTS_FAILED++))
        return 1
    fi
}

test_skip() {
    local test_name="$1"
    local reason="$2"
    
    ((TESTS_RUN++))
    ((TESTS_SKIPPED++))
    log SKIP "$test_name: $reason"
    TEST_RESULTS+=("⊘ $test_name: $reason")
}

adb_exec() {
    "$ADB_BIN" "$@" 2>&1 | tee -a "$LOG_FILE"
}

adb_shell() {
    "$ADB_BIN" shell "$@" 2>&1 | tee -a "$LOG_FILE"
}

adb_root_shell() {
    "$ADB_BIN" shell "su -c '$*'" 2>&1 | tee -a "$LOG_FILE"
}

################################################################################
# Pre-flight Checks
################################################################################

check_environment() {
    print_header "Environment Check"
    
    # Check if running in Termux or Chroot
    if [ -n "$TERMUX_VERSION" ]; then
        log INFO "Running in Termux environment"
        log INFO "Termux version: $TERMUX_VERSION"
    elif [ -f /proc/1/root/.kali_chroot ]; then
        log INFO "Running in Kali Linux Chroot"
    else
        log WARN "Unknown environment (expected Termux or Kali Chroot)"
    fi
    
    # Check for ADB binary
    if [ -f "$ADB_BIN" ]; then
        log PASS "ADB binary found at $ADB_BIN"
        local adb_version=$("$ADB_BIN" version 2>&1 | head -1)
        log INFO "ADB version: $adb_version"
    else
        log FAIL "ADB binary not found at $ADB_BIN"
        log INFO "Please ensure Magisk ADB module is installed"
        exit 1
    fi
    
    # Check ADB server status
    "$ADB_BIN" start-server >/dev/null 2>&1 || true
    sleep 1
}

################################################################################
# Device Connectivity Tests
################################################################################

test_device_connectivity() {
    print_header "Device Connectivity Tests"
    
    # Test 1: Check for connected devices
    local devices=$("$ADB_BIN" devices 2>/dev/null | grep -v "List of devices" | grep "device$" | wc -l)
    test_assert "Device connected via ADB" "[ $devices -gt 0 ]" "No devices found"
    
    if [ $devices -eq 0 ]; then
        log FAIL "Cannot proceed without connected device"
        return 1
    fi
    
    # Get device serial
    DEVICE_SERIAL=$("$ADB_BIN" devices | grep "device$" | head -1 | awk '{print $1}')
    log INFO "Device serial: $DEVICE_SERIAL"
    
    # Test 2: Device model
    local model=$(adb_shell "getprop ro.product.model" | tr -d '\r\n')
    log INFO "Device model: $model"
    test_assert "Device is Orbic RC400L" "[[ '$model' =~ 'RC400L' ]] || [[ '$model' =~ 'Orbic' ]]" \
        "Expected RC400L, got $model"
    
    # Test 3: Android version
    local android_version=$(adb_shell "getprop ro.build.version.release" | tr -d '\r\n')
    log INFO "Android version: $android_version"
    
    # Test 4: Device is responsive
    test_assert "Device responds to shell commands" \
        "adb_shell 'echo test' | grep -q 'test'" \
        "Device not responding"
}

################################################################################
# Root Access Tests
################################################################################

test_root_access() {
    print_header "Root Access Tests"
    
    # Test 1: Check for /bin/rootshell (backdoor method)
    if adb_shell "[ -f /bin/rootshell ]" >/dev/null 2>&1; then
        log PASS "Backdoor binary /bin/rootshell exists"
        
        # Test rootshell works
        local root_check=$(adb_shell "echo 'id -u' | /bin/rootshell" 2>/dev/null | tr -d '\r\n' | grep -o '[0-9]*' | head -1)
        test_assert "Backdoor root access (UID 0)" "[ '$root_check' = '0' ]" \
            "Backdoor returned UID $root_check"
    else
        test_skip "Backdoor root test" "/bin/rootshell not found"
    fi
    
    # Test 2: Check for su binary (frontdoor method)
    if adb_shell "[ -f /bin/su ] || [ -f /system/bin/su ] || [ -f /system/xbin/su ]" >/dev/null 2>&1; then
        log PASS "su binary found"
        
        # Test su works
        local su_check=$(adb_shell "su -c 'id -u'" 2>/dev/null | tr -d '\r\n' | grep -o '[0-9]*' | head -1)
        test_assert "Frontdoor root access via su (UID 0)" "[ '$su_check' = '0' ]" \
            "su returned UID $su_check"
        
        # Test capabilities
        local caps=$(adb_shell "su -c 'cat /proc/self/status | grep CapEff'" 2>/dev/null | awk '{print $2}')
        log INFO "Root capabilities: $caps"
        test_assert "Root has full capabilities" "[ -n \"$caps\" ]" \
            "Could not read capabilities"
    else
        test_skip "Frontdoor root test" "su binary not found"
    fi
    
    # Test 3: Verify root context
    local root_context=$(adb_root_shell "id" 2>/dev/null | grep -o "uid=[0-9]*(root)")
    test_assert "Root context verified" "[ -n '$root_context' ]" \
        "Could not verify root context"
}

################################################################################
# Alpine Chroot Tests
################################################################################

test_alpine_chroot() {
    print_header "Alpine Linux Chroot Tests"
    
    # Test 1: Alpine directory exists
    test_assert "Alpine chroot directory exists" \
        "adb_shell '[ -d /data/alpine ]' >/dev/null 2>&1" \
        "/data/alpine not found"
    
    # Test 2: Essential directories mounted
    test_assert "Alpine /proc mounted" \
        "adb_shell 'mount | grep /data/alpine/proc' >/dev/null 2>&1" \
        "/proc not mounted in chroot"
    
    test_assert "Alpine /sys mounted" \
        "adb_shell 'mount | grep /data/alpine/sys' >/dev/null 2>&1" \
        "/sys not mounted in chroot"
    
    test_assert "Alpine /dev mounted" \
        "adb_shell 'mount | grep /data/alpine/dev' >/dev/null 2>&1" \
        "/dev not mounted in chroot"
    
    # Test 3: Chroot is functional
    if adb_root_shell "chroot /data/alpine /bin/sh -c 'echo test'" | grep -q "test" 2>/dev/null; then
        log PASS "Alpine chroot is functional"
        
        # Test Alpine version
        local alpine_version=$(adb_root_shell "chroot /data/alpine cat /etc/alpine-release" 2>/dev/null | tr -d '\r\n')
        log INFO "Alpine Linux version: $alpine_version"
    else
        log FAIL "Alpine chroot is not functional"
    fi
    
    # Test 4: Python environment
    test_assert "Python3 installed in chroot" \
        "adb_root_shell 'chroot /data/alpine which python3' >/dev/null 2>&1" \
        "python3 not found in chroot"
    
    local python_version=$(adb_root_shell "chroot /data/alpine python3 --version" 2>/dev/null | tr -d '\r\n')
    log INFO "Python version: $python_version"
}

################################################################################
# FOLC UI Tests
################################################################################

test_folc_ui() {
    print_header "FOLC UI Tests"
    
    # Test 1: UI files present
    test_assert "folc_ui.py exists in chroot" \
        "adb_shell '[ -f /data/alpine/root/folc_ui.py ]' >/dev/null 2>&1" \
        "folc_ui.py not found"
    
    test_assert "folc_core.py exists in chroot" \
        "adb_shell '[ -f /data/alpine/root/folc_core.py ]' >/dev/null 2>&1" \
        "folc_core.py not found"
    
    test_assert "input_manager.py exists in chroot" \
        "adb_shell '[ -f /data/alpine/root/input_manager.py ]' >/dev/null 2>&1" \
        "input_manager.py not found"
    
    # Test 2: Start scripts present
    test_assert "start_folc_v2.sh exists" \
        "adb_shell '[ -f /data/rayhunter/start_folc_v2.sh ]' >/dev/null 2>&1" \
        "start_folc_v2.sh not found"
    
    # Test 3: Check if UI is running
    local ui_running=$(adb_shell "ps | grep -c 'folc_ui' || true" | tr -d '\r\n')
    if [ "$ui_running" -gt 0 ]; then
        log PASS "FOLC UI process is running (PID count: $ui_running)"
    else
        log WARN "FOLC UI is not currently running"
    fi
    
    # Test 4: Dependencies check
    local evdev_check=$(adb_root_shell "chroot /data/alpine python3 -c 'import evdev; print(\"OK\")' 2>/dev/null" | grep "OK")
    test_assert "Python evdev module available" "[ -n \"$evdev_check\" ]" \
        "evdev module not installed"
    
    local pil_check=$(adb_root_shell "chroot /data/alpine python3 -c 'import PIL; print(\"OK\")' 2>/dev/null" | grep "OK")
    test_assert "Python PIL module available" "[ -n \"$pil_check\" ]" \
        "PIL module not installed"
}

################################################################################
# Persistence Tests
################################################################################

test_persistence() {
    print_header "Persistence Tests"
    
    # Test 1: Wrapper script
    test_assert "wrapper_v4.sh exists" \
        "adb_shell '[ -f /data/rayhunter/wrapper_v4.sh ]' >/dev/null 2>&1" \
        "wrapper_v4.sh not found"
    
    # Test 2: Init script
    test_assert "orbital_os_init.sh exists" \
        "adb_shell '[ -f /data/rayhunter/orbital_os_init.sh ]' >/dev/null 2>&1" \
        "orbital_os_init.sh not found"
    
    # Test 3: Rayhunter daemon hijack
    if adb_shell "[ -f /data/rayhunter/rayhunter-daemon.bak ]" >/dev/null 2>&1; then
        log PASS "Original rayhunter-daemon backed up"
        
        # Check if current daemon is our wrapper
        local daemon_check=$(adb_shell "head -2 /data/rayhunter/rayhunter-daemon 2>/dev/null | grep -c 'HIJACK' || true")
        test_assert "Rayhunter daemon is hijacked" "[ '$daemon_check' -gt 0 ]" \
            "Daemon does not appear to be our wrapper"
    else
        test_skip "Daemon hijack test" "Backup not found (may not be installed yet)"
    fi
}

################################################################################
# Network Tests
################################################################################

test_network_capabilities() {
    print_header "Network Capabilities Tests"
    
    # Test 1: WiFi interface exists
    local wlan_exists=$(adb_shell "ip link show wlan0 2>/dev/null | grep -c wlan0 || true")
    test_assert "WiFi interface wlan0 exists" "[ '$wlan_exists' -gt 0 ]" \
        "wlan0 not found"
    
    # Test 2: Cellular interface
    local cell_exists=$(adb_shell "ip link show rmnet_data0 2>/dev/null | grep -c rmnet || true")
    test_assert "Cellular interface rmnet_data0 exists" "[ '$cell_exists' -gt 0 ]" \
        "rmnet_data0 not found"
    
    # Test 3: Wireless tools in chroot
    test_assert "iw tool available" \
        "adb_root_shell 'chroot /data/alpine which iw' >/dev/null 2>&1" \
        "iw not found in chroot"
    
    local aircrack_available=$(adb_root_shell "chroot /data/alpine which aircrack-ng 2>/dev/null")
    if [ -n "$aircrack_available" ]; then
        log PASS "aircrack-ng suite available"
    else
        log WARN "aircrack-ng suite not installed (optional)"
    fi
    
    # Test 4: tcpdump
    test_assert "tcpdump available" \
        "adb_root_shell 'chroot /data/alpine which tcpdump' >/dev/null 2>&1" \
        "tcpdump not found in chroot"
}

################################################################################
# Backdoor Tests
################################################################################

test_backdoor() {
    print_header "Backdoor Tests"
    
    # Test 1: Port 9999 listener
    local backdoor_port=$(adb_shell "netstat -tlpn 2>/dev/null | grep -c ':9999' || true")
    if [ "$backdoor_port" -gt 0 ]; then
        log PASS "Backdoor listening on port 9999"
        
        # Try to connect (without executing commands to avoid interference)
        "$ADB_BIN" forward tcp:9999 tcp:9999 >/dev/null 2>&1
        sleep 1
        
        # Test connection only (send exit immediately to minimize impact)
        local backdoor_test=$(echo "exit" | timeout 3 nc -w 1 127.0.0.1 9999 2>/dev/null && echo "CONNECTED" || echo "FAILED")
        test_assert "Backdoor connection test" "[[ '$backdoor_test' == 'CONNECTED' ]]" \
            "Could not establish connection to backdoor"
        
        # Cleanup
        "$ADB_BIN" forward --remove tcp:9999 >/dev/null 2>&1 || true
    else
        test_skip "Backdoor test" "Port 9999 not listening (may be disabled)"
    fi
}

################################################################################
# Hardware Tests
################################################################################

test_hardware_access() {
    print_header "Hardware Access Tests"
    
    # Test 1: Framebuffer device
    test_assert "Framebuffer /dev/fb0 exists" \
        "adb_shell '[ -c /dev/fb0 ]' >/dev/null 2>&1" \
        "/dev/fb0 not found"
    
    # Test 2: Input devices
    local input_devices=$(adb_shell "ls /dev/input/event* 2>/dev/null | wc -l")
    test_assert "Input event devices exist" "[ '$input_devices' -gt 0 ]" \
        "No input devices found"
    
    log INFO "Found $input_devices input devices"
    
    # Test 3: GPIO access (if available)
    if adb_shell "[ -d /sys/class/gpio ]" >/dev/null 2>&1; then
        log PASS "GPIO interface accessible"
    else
        log WARN "GPIO interface not found (may not be needed)"
    fi
}

################################################################################
# Filesystem Tests
################################################################################

test_filesystem() {
    print_header "Filesystem Tests"
    
    # Test 1: /data partition writable
    local test_file="/data/folc_test_$$"
    if adb_root_shell "touch $test_file && rm $test_file" >/dev/null 2>&1; then
        log PASS "/data partition is writable"
    else
        log FAIL "/data partition is not writable"
    fi
    
    # Test 2: Disk space
    local data_avail=$(adb_shell "df /data | tail -1 | awk '{print \$4}'" | tr -d '\r\n')
    log INFO "Available space on /data: ${data_avail}K"
    test_assert "Sufficient disk space (>50MB)" "[ '$data_avail' -gt 51200 ]" \
        "Low disk space: ${data_avail}K"
    
    # Test 3: Alpine size
    local alpine_size=$(adb_shell "du -sm /data/alpine 2>/dev/null | awk '{print \$1}'" | tr -d '\r\n')
    log INFO "Alpine chroot size: ${alpine_size}MB"
}

################################################################################
# Security Tests
################################################################################

test_security() {
    print_header "Security Tests"
    
    # Test 1: SELinux status
    local selinux=$(adb_shell "getenforce" 2>/dev/null | tr -d '\r\n')
    log INFO "SELinux mode: $selinux"
    if [ "$selinux" = "Permissive" ] || [ "$selinux" = "Disabled" ]; then
        log PASS "SELinux is not enforcing"
    else
        log WARN "SELinux is enforcing (may cause issues)"
    fi
    
    # Test 2: dm-verity status
    local verity=$(adb_shell "getprop ro.boot.veritymode" 2>/dev/null | tr -d '\r\n')
    log INFO "dm-verity mode: ${verity:-unknown}"
}

################################################################################
# Integration Tests
################################################################################

test_integration() {
    print_header "Integration Tests"
    
    # Test 1: Full stack test - scan WiFi via UI core
    log INFO "Testing WiFi scan functionality..."
    
    # Get script directory
    local script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    local test_script="$script_dir/test_wifi_scan.py"
    
    if [ -f "$test_script" ]; then
        # Push test script to device
        "$ADB_BIN" push "$test_script" /data/local/tmp/test_wifi_scan.py >/dev/null 2>&1
        
        # Run test
        local scan_test=$(adb_root_shell "chroot /data/alpine python3 /data/local/tmp/test_wifi_scan.py" 2>&1)
        
        if echo "$scan_test" | grep -q "SCAN_OK"; then
            local count=$(echo "$scan_test" | grep -o "SCAN_OK:[0-9]*" | cut -d: -f2)
            log PASS "WiFi scan test passed (found $count networks)"
        else
            log WARN "WiFi scan test had issues: $scan_test"
        fi
        
        # Cleanup
        "$ADB_BIN" shell "rm -f /data/local/tmp/test_wifi_scan.py" >/dev/null 2>&1
    else
        test_skip "WiFi scan test" "test_wifi_scan.py not found"
    fi
}

################################################################################
# Report Generation
################################################################################

generate_report() {
    print_header "Test Summary"
    
    echo ""
    echo "Test Results:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    for result in "${TEST_RESULTS[@]}"; do
        echo "$result"
    done
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "Total Tests Run:    ${BLUE}$TESTS_RUN${NC}"
    echo -e "Tests Passed:       ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Tests Failed:       ${RED}$TESTS_FAILED${NC}"
    echo -e "Tests Skipped:      ${YELLOW}$TESTS_SKIPPED${NC}"
    echo ""
    
    local pass_rate=0
    if [ $TESTS_RUN -gt 0 ]; then
        pass_rate=$((TESTS_PASSED * 100 / TESTS_RUN))
    fi
    
    echo -e "Pass Rate:          ${CYAN}${pass_rate}%${NC}"
    echo ""
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}✓ All tests passed!${NC}"
        return 0
    else
        echo -e "${RED}✗ Some tests failed${NC}"
        return 1
    fi
}

################################################################################
# Main Execution
################################################################################

main() {
    clear
    echo -e "${BLUE}"
    cat << "EOF"
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║              FOLC-V3 Comprehensive Test Suite             ║
║                                                            ║
║           Full-Stack Testing for Android 14 Device        ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    
    setup_logging
    log INFO "Test suite started"
    log INFO "Log file: $LOG_FILE"
    
    # Run test suites
    check_environment || exit 1
    test_device_connectivity || exit 1
    test_root_access
    test_alpine_chroot
    test_folc_ui
    test_persistence
    test_network_capabilities
    test_backdoor
    test_hardware_access
    test_filesystem
    test_security
    test_integration
    
    # Generate report
    echo ""
    generate_report
    local exit_code=$?
    
    echo ""
    log INFO "Test suite completed"
    log INFO "Full log available at: $LOG_FILE"
    echo ""
    echo -e "${CYAN}Log file saved to: $LOG_FILE${NC}"
    
    exit $exit_code
}

# Run main if executed directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
