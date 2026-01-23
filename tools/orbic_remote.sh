#!/bin/bash
# FOLC-V3 Unified Remote CLI
# Usage: ./tools/orbic_remote.sh [IP_ADDRESS]

TARGET=${1:-"usb"}
PORT=2222
USER="root"
PASS="root"

if [ "$TARGET" == "usb" ] || [ "$TARGET" == "127.0.0.1" ]; then
    echo "[*] Mode: USB Bridge (ADB)"
    # Ensure ADB forward is active
    adb forward tcp:$PORT tcp:$PORT 2>/dev/null
    IP="127.0.0.1"
else
    echo "[*] Mode: Wireless (Wi-Fi)"
    IP=$TARGET
    # Check if host is reachable
    if ! ping -c 1 -W 2 "$IP" > /dev/null 2>&1; then
        echo "[!] Error: Host $IP is unreachable."
        exit 1
    fi
fi

echo "[*] Connecting to $IP:$PORT..."
ssh -p $PORT -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "$USER@$IP"
