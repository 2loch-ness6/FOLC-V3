#!/bin/bash
# FOLC Deployment Script
# Pushes the latest UI and Logic to the Orbic Speed
# Updated for new repository structure

set -e

DEVICE="e830926d"

echo "[-] Starting Deployment..."

# Get script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Check ADB connection
if ! adb -s "$DEVICE" devices | grep -q "device$"; then
    echo "[-] No device connected"
    exit 1
fi

# 1. UI Files (To Alpine Chroot)
echo "[-] Pushing UI to Alpine /root/..."
adb -s "$DEVICE" push "$PROJECT_ROOT/src/ui/folc_ui.py" /data/alpine/root/
adb -s "$DEVICE" push "$PROJECT_ROOT/src/core/folc_core.py" /data/alpine/root/
adb -s "$DEVICE" push "$PROJECT_ROOT/src/core/input_manager.py" /data/alpine/root/

# 2. Startup Script (To Rayhunter dir)
echo "[-] Pushing Start Script..."
adb -s "$DEVICE" push "$PROJECT_ROOT/tools/start_folc_v2.sh" /data/rayhunter/
adb -s "$DEVICE" shell "chmod +x /data/rayhunter/start_folc_v2.sh"

# 3. Hijack Wrapper
echo "[-] Pushing Wrapper..."
adb -s "$DEVICE" push "$PROJECT_ROOT/exploits/wrapper_v4.sh" /data/rayhunter/
adb -s "$DEVICE" shell "chmod +x /data/rayhunter/wrapper_v4.sh"

# 4. Dependencies Check (Optional)
# This requires the device to have internet or cached pip
echo "[-] Attempting to install evdev via Chroot..."
# adb -s "$DEVICE" shell "chroot /data/alpine pip install evdev"

echo "[+] Deployment Complete."
echo "---------------------------------------------------"
echo "To ACTIVATE the hijack, run:"
echo "  adb -s $DEVICE shell 'cp /data/rayhunter/wrapper_v4.sh /data/rayhunter/rayhunter-daemon && reboot'"
echo "---------------------------------------------------"
