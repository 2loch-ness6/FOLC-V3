#!/bin/bash
# FOAC Deployment Script
# Pushes the latest UI and Logic to the Orbic Speed

echo "[-] Starting Deployment..."

# 1. UI Files (To Alpine Chroot)
echo "[-] Pushing UI to Alpine /root/..."
adb push foac_ui_v6.py /data/alpine/root/
adb push foac_core.py /data/alpine/root/

# 2. Startup Script (To Rayhunter dir)
echo "[-] Pushing Start Script..."
adb push start_foac_v2.sh /data/rayhunter/
adb shell "chmod +x /data/rayhunter/start_foac_v2.sh"

# 3. Hijack Wrapper
echo "[-] Pushing Wrapper..."
adb push wrapper_v4.sh /data/rayhunter/
adb shell "chmod +x /data/rayhunter/wrapper_v4.sh"

# 4. Dependencies Check (Optional)
# This requires the device to have internet or cached pip
echo "[-] Attempting to install evdev via Chroot..."
# adb shell "chroot /data/alpine pip install evdev"

echo "[+] Deployment Complete."
echo "---------------------------------------------------"
echo "To ACTIVATE the hijack, run:"
echo "  adb shell 'cp /data/rayhunter/wrapper_v4.sh /data/rayhunter/rayhunter-daemon && reboot'"
echo "---------------------------------------------------"
