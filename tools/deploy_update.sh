#!/bin/bash
set -e

echo "[*] Checking ADB connection..."
adb devices
if ! adb devices | grep -q "device$"; then
    echo "[-] No ADB device found. Please connect a device via USB or ensure ADB over TCP is enabled."
    exit 1
fi

echo "[+] Device found. Pushing updates..."

# 1. Push orbital_os_init.sh
echo "[*] Pushing orbital_os_init.sh..."
adb push exploits/orbital_os_init.sh /data/rayhunter/orbital_os_init.sh
adb shell "chmod +x /data/rayhunter/orbital_os_init.sh"

# 2. Push symlink_bridge.sh
echo "[*] Pushing symlink_bridge.sh..."
adb push tools/symlink_bridge.sh /data/rayhunter/symlink_bridge.sh
adb shell "chmod +x /data/rayhunter/symlink_bridge.sh"

# 3. Push start_folc_v2.sh
echo "[*] Pushing start_folc_v2.sh..."
adb push tools/start_folc_v2.sh /data/rayhunter/start_folc_v2.sh
adb shell "chmod +x /data/rayhunter/start_folc_v2.sh"

# 4. Push Python Core & UI
echo "[*] Pushing FOLC Python files..."
adb push src/ui/folc_ui.py /data/alpine/root/folc_ui.py
adb push src/core/folc_core.py /data/alpine/root/folc_core.py
adb push src/core/input_manager.py /data/alpine/root/input_manager.py

echo "[+] Updates pushed successfully."
echo "[*] To apply changes, you may need to restart the services:"
echo "    adb shell '/data/rayhunter/orbital_os_init.sh stop && /data/rayhunter/orbital_os_init.sh start'"
