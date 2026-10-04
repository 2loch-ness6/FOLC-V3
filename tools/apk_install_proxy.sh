#!/bin/bash
# APK INSTALL PROXY BLUEPRINT
# This script automates the internet connection method used to provision the Orbic Speed.
# It uses a local tinyproxy on the host and ADB reverse forwarding.

DEVICE="e830926d"
PROXY_PORT=8888
CONFIG_FILE="./config/tinyproxy.conf"

echo "[*] Ensuring tinyproxy is running..."
if ! pgrep tinyproxy > /dev/null; then
    if [ -f "$CONFIG_FILE" ]; then
        tinyproxy -c "$CONFIG_FILE"
        echo "[+] tinyproxy started with $CONFIG_FILE"
    else
        echo "[-] Error: $CONFIG_FILE not found."
        exit 1
    fi
else
    echo "[+] tinyproxy is already running."
fi

echo "[*] Establishing ADB reverse forward..."
adb -s "$DEVICE" reverse tcp:$PROXY_PORT tcp:$PROXY_PORT
if [ $? -eq 0 ]; then
    echo "[+] Forward established: Orbic:$PROXY_PORT -> Host:$PROXY_PORT"
else
    echo "[-] Error: Failed to establish ADB reverse forward."
    exit 1
fi

echo "[*] Preparing high-privilege shell payload..."
# Construct the arguments string
ARGS="$*"
# The payload exports proxy variables and runs apk within the chroot
CMD="export http_proxy=http://127.0.0.1:$PROXY_PORT; export https_proxy=http://127.0.0.1:$PROXY_PORT; chroot /data/alpine /sbin/apk $ARGS"

echo "[*] Executing on device: apk $ARGS"
adb -s "$DEVICE" forward tcp:9999 tcp:9999
# Add an explicit exit and success marker to the command stream
(echo "$CMD"; echo "echo 'DEVICESIDE_DONE'"; echo "exit") | nc -w 120 127.0.0.1 9999 | while read line; do
    echo "  [REMOTE] $line"
    if [[ "$line" == "DEVICESIDE_DONE" ]]; then
        echo "[+] Remote command completed successfully."
        break
    fi
done

echo "[*] Cleaning up reverse forward..."
adb -s "$DEVICE" reverse --remove tcp:$PROXY_PORT