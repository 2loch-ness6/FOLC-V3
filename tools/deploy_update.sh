#!/bin/bash
set -e

echo "[*] Checking ADB connection..."
adb devices
if ! adb devices | grep -q "device$"; then
    echo "[-] No ADB device found. Please connect the Orbic Speed via USB or TCP."
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

# 3. Push start_foac_v2.sh
echo "[*] Pushing start_foac_v2.sh..."
adb push tools/start_foac_v2.sh /data/rayhunter/start_foac_v2.sh
adb shell "chmod +x /data/rayhunter/start_foac_v2.sh"

# 4. Push Python Core & UI
echo "[*] Pushing FOAC Python files..."
adb push src/ui/foac_ui_v6.py /data/alpine/root/foac_ui_v6.py
adb push src/core/foac_core.py /data/alpine/root/foac_core.py

echo "[+] Updates pushed successfully."
echo "[*] To apply changes, you may need to restart the services:"
echo "    adb shell '/data/rayhunter/orbital_os_init.sh stop && /data/rayhunter/orbital_os_init.sh start'"
