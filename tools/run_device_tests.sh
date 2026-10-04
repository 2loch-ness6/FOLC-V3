#!/bin/bash
# RUN DEVICE TESTS
# This script establishes the proxy and executes pytest on the device.

DEVICE="e830926d"
PROXY_PORT=8888

echo "[*] Ensuring proxy bridge..."
adb -s "$DEVICE" reverse tcp:$PROXY_PORT tcp:$PROXY_PORT

# We need to make sure the code and tests are ON the device.
echo "[*] Pushing src and tests to device..."
adb -s "$DEVICE" push src/ /data/alpine/root/src/
adb -s "$DEVICE" push tests/ /data/alpine/root/tests/

echo "[*] Executing tests in chroot..."
CMD="export PYTHONPATH=/data/alpine/root:/data/alpine/root/src; chroot /data/alpine /usr/bin/python3 -m pytest /root/tests/sos/test_mcp_server.py /root/tests/core/test_state_manager.py"

adb -s "$DEVICE" forward tcp:9999 tcp:9999
echo "$CMD" | nc -w 10 127.0.0.1 9999

echo "[*] Cleanup..."
adb -s "$DEVICE" reverse --remove tcp:$PROXY_PORT
