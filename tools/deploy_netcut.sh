#!/bin/sh
########################################################################
# deploy_netcut.sh — Push netcut system to Orbic device
########################################################################

set -e
cd "$(dirname "$0")/.."

echo "[*] Checking ADB connection..."
adb devices | grep -q "device$" || { echo "[-] No device connected"; exit 1; }

echo "[*] Deploying netcut system..."

adb push exploits/wrapper_netcut.sh   /data/rayhunter/wrapper_netcut.sh
adb push tools/netctl.sh              /data/rayhunter/netctl.sh
adb push tools/udhcpc_apply.sh        /data/rayhunter/udhcpc_apply.sh
adb push config/netcut.conf           /data/rayhunter/netcut.conf
adb push src/netcut/netcut.py          /data/alpine/usr/local/bin/netcut
adb push src/netcut/display.py         /data/alpine/usr/local/bin/folc-display

echo "[*] Setting permissions..."
adb shell "chmod 755 /data/rayhunter/wrapper_netcut.sh"
adb shell "chmod 755 /data/rayhunter/netctl.sh"
adb shell "chmod 755 /data/rayhunter/udhcpc_apply.sh"
adb shell "chmod 755 /data/alpine/usr/local/bin/netcut /data/alpine/usr/local/bin/folc-display"

echo "[+] Files deployed:"
echo "    /data/rayhunter/wrapper_netcut.sh"
echo "    /data/rayhunter/netctl.sh"
echo "    /data/rayhunter/udhcpc_apply.sh"
echo "    /data/rayhunter/netcut.conf"
echo "    /data/alpine/usr/local/bin/netcut"
echo ""
echo "To ACTIVATE (replaces current boot wrapper):"
echo "  adb shell 'cp /data/rayhunter/wrapper_netcut.sh /data/rayhunter/rayhunter-daemon && reboot'"
echo ""
echo "To REVERT to previous wrapper:"
echo "  adb shell 'cp /data/rayhunter/wrapper_v4.sh /data/rayhunter/rayhunter-daemon && reboot'"
echo ""
echo "To test WITHOUT reboot (run manually via backdoor):"
echo "  adb forward tcp:9999 tcp:9999"
echo "  echo 'sh /data/rayhunter/wrapper_netcut.sh' | nc -w 60 127.0.0.1 9999"
