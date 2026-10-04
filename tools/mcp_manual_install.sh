#!/bin/bash
# Manual install script for mcp to ensure exit and feedback
DEVICE="e830926d"
PROXY_PORT=8888
adb -s "$DEVICE" reverse tcp:$PROXY_PORT tcp:$PROXY_PORT
adb -s "$DEVICE" forward tcp:9999 tcp:9999

echo "[*] Starting mcp installation with explicit timeout logic..."
(
echo "export http_proxy=http://127.0.0.1:$PROXY_PORT"
echo "export https_proxy=http://127.0.0.1:$PROXY_PORT"
echo "chroot /data/alpine /usr/bin/python3 -m pip install mcp --no-deps"
echo "echo 'INSTALL_FINISHED'"
echo "exit"
) | nc -w 120 127.0.0.1 9999

echo "[*] Cleanup..."
adb -s "$DEVICE" reverse --remove tcp:$PROXY_PORT
