#!/bin/bash
# FOLC-V3 Master Setup Script
# This script coordinates the complete installation process

set -e  # Exit on error

DEVICE="e830926d"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  FOLC-V3 Installation Script          ║${NC}"
echo -e "${BLUE}║  Orbic Speed (RC400L) Security Toolkit║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Warning and disclaimer
echo -e "${RED}⚠️  WARNING ⚠️${NC}"
echo -e "${YELLOW}This will modify your Orbic Speed device!${NC}"
echo ""
echo "Risks:"
echo "  • May void warranty"
echo "  • May violate carrier ToS"
echo "  • Small risk of device malfunction"
echo ""
echo -e "${YELLOW}Legal Notice:${NC}"
echo "  This toolkit is for authorized testing and education only."
echo "  Unauthorized network access is illegal."
echo ""
read -p "Do you understand and accept these risks? (yes/no): " ACCEPT

if [ "$ACCEPT" != "yes" ]; then
    echo -e "${RED}Installation cancelled.${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✓ Terms accepted${NC}"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print step header
print_step() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════${NC}"
}

# Step 1: Check prerequisites
print_step "Step 1: Checking Prerequisites"

echo -n "Checking for ADB... "
if command_exists adb; then
    echo -e "${GREEN}✓ Found${NC}"
    adb version | head -1
else
    echo -e "${RED}✗ Not found${NC}"
    echo ""
    echo "Please install ADB:"
    echo "  Ubuntu/Debian: sudo apt-get install android-tools-adb"
    echo "  macOS: brew install android-platform-tools"
    echo "  Windows: Download from https://developer.android.com/studio/releases/platform-tools"
    exit 1
fi

echo -n "Checking for Python 3... "
if command_exists python3; then
    echo -e "${GREEN}✓ Found${NC}"
    python3 --version
else
    echo -e "${YELLOW}⚠ Not found (optional for deployment scripts)${NC}"
fi

# Step 2: Check device connection
print_step "Step 2: Checking Device Connection"

echo "Waiting for device..."
adb -s "$DEVICE" wait-for-device

DEVICE_COUNT=$(adb -s "$DEVICE" devices | grep -c "device$" || true)
if [ "$DEVICE_COUNT" -eq 0 ]; then
    echo -e "${RED}✗ No device connected${NC}"
    echo "Please connect your Orbic Speed via USB"
    exit 1
fi

echo -e "${GREEN}✓ Device connected${NC}"

# Verify it's the right device
DEVICE_MODEL=$(adb -s "$DEVICE" shell getprop ro.product.model 2>/dev/null | tr -d '\r')
echo "Device Model: $DEVICE_MODEL"

if [[ ! "$DEVICE_MODEL" =~ "RC400L" ]] && [[ ! "$DEVICE_MODEL" =~ "Orbic" ]]; then
    echo -e "${YELLOW}⚠ Warning: Device model does not match expected 'RC400L'${NC}"
    read -p "Continue anyway? (yes/no): " CONTINUE
    if [ "$CONTINUE" != "yes" ]; then
        exit 1
    fi
fi

# Step 3: Verify root exploit
print_step "Step 3: Verifying Root Exploit"

echo "Checking for /bin/rootshell..."
if adb -s "$DEVICE" shell "[ -f /bin/rootshell ]" 2>/dev/null; then
    echo -e "${GREEN}✓ Root exploit found${NC}"
    
    # Test root access
    echo "Testing root access..."
    ROOT_UID=$(adb -s "$DEVICE" shell "echo 'id -u' | /bin/rootshell" 2>/dev/null | tr -d '\r')
    if [ "$ROOT_UID" = "0" ]; then
        echo -e "${GREEN}✓ Root access confirmed (UID 0)${NC}"
    else
        echo -e "${RED}✗ Root exploit not working properly${NC}"
        exit 1
    fi
else
    echo -e "${RED}✗ /bin/rootshell not found${NC}"
    echo "This device may not be vulnerable to the known exploit."
    exit 1
fi

# Step 4: Check disk space
print_step "Step 4: Checking Disk Space"

DATA_AVAIL=$(adb -s "$DEVICE" shell "df /data | tail -1 | awk '{print \$4}'" | tr -d '\r')
echo "Available space on /data: ${DATA_AVAIL}K"

# Need at least 100MB for Alpine Linux
if [ "$DATA_AVAIL" -lt 102400 ]; then
    echo -e "${RED}✗ Insufficient disk space${NC}"
    echo "Need at least 100MB free on /data partition"
    exit 1
fi

echo -e "${GREEN}✓ Sufficient disk space${NC}"

# Step 5: Installation menu
print_step "Step 5: Installation Options"

echo "Choose installation type:"
echo "  1) Full Install (Recommended) - Everything"
echo "  2) Minimal Install - Exploit + Basic Tools"
echo "  3) UI Only - Just deploy the interface"
echo "  4) Custom - Select components"
echo ""
read -p "Enter choice (1-4): " INSTALL_TYPE

case $INSTALL_TYPE in
    1)
        DO_BACKDOOR=true
        DO_ALPINE=true
        DO_TOOLS=true
        DO_UI=true
        ;;
    2)
        DO_BACKDOOR=true
        DO_ALPINE=true
        DO_TOOLS=false
        DO_UI=true
        ;;
    3)
        DO_BACKDOOR=false
        DO_ALPINE=false
        DO_TOOLS=false
        DO_UI=true
        ;;
    4)
        read -p "Install backdoor? (y/n): " choice
        [ "$choice" = "y" ] && DO_BACKDOOR=true || DO_BACKDOOR=false
        
        read -p "Install Alpine Linux? (y/n): " choice
        [ "$choice" = "y" ] && DO_ALPINE=true || DO_ALPINE=false
        
        read -p "Install security tools? (y/n): " choice
        [ "$choice" = "y" ] && DO_TOOLS=true || DO_TOOLS=false
        
        read -p "Install UI? (y/n): " choice
        [ "$choice" = "y" ] && DO_UI=true || DO_UI=false
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

# Confirmation
echo ""
echo "Installation plan:"
echo "  Backdoor: $([ "$DO_BACKDOOR" = true ] && echo "Yes" || echo "No")"
echo "  Alpine Linux: $([ "$DO_ALPINE" = true ] && echo "Yes" || echo "No")"
echo "  Security Tools: $([ "$DO_TOOLS" = true ] && echo "Yes" || echo "No")"
echo "  UI: $([ "$DO_UI" = true ] && echo "Yes" || echo "No")"
echo ""
read -p "Proceed with installation? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Installation cancelled"
    exit 0
fi

# Execute installation steps
if [ "$DO_BACKDOOR" = true ]; then
    print_step "Installing Backdoor"
    # TODO: Call backdoor installation script
    echo -e "${YELLOW}⚠ Manual step required - see INSTALL.md section 6${NC}"
fi

if [ "$DO_ALPINE" = true ]; then
    print_step "Installing Alpine Linux"
    # TODO: Call Alpine installation script
    echo -e "${YELLOW}⚠ Manual step required - see INSTALL.md section 7${NC}"
fi

if [ "$DO_TOOLS" = true ]; then
    print_step "Installing Security Tools"
    if [ -f "$SCRIPT_DIR/install_toolkit.sh" ]; then
        bash "$SCRIPT_DIR/install_toolkit.sh"
    else
        echo -e "${YELLOW}⚠ install_toolkit.sh not found${NC}"
    fi
fi

if [ "$DO_UI" = true ]; then
    print_step "Installing UI"
    if [ -f "$SCRIPT_DIR/deploy_folc.sh" ]; then
        bash "$SCRIPT_DIR/deploy_folc.sh"
    else
        echo -e "${YELLOW}⚠ deploy_folc.sh not found${NC}"
    fi
fi

# Final steps
print_step "Installation Complete!"

echo ""
echo -e "${GREEN}✓ FOLC-V3 installation finished${NC}"
echo ""
echo "Next steps:"
echo "  1. Test backdoor access: adb -s $DEVICE forward tcp:9999 tcp:9999; nc 127.0.0.1 9999"
echo "  2. Check device screen for UI"
echo "  3. Read the documentation: README.md and INSTALL.md"
echo ""
echo "For troubleshooting, see: docs/TROUBLESHOOTING.md"
echo ""
echo -e "${BLUE}Happy hacking! (Legally and ethically, of course 😊)${NC}"
