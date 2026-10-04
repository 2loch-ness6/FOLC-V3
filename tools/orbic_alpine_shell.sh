#!/bin/bash
# FOLC-V3 Remote Entrance Script

DEVICE="e830926d"
PORT=2222
USER="root"
PASS="root"

# Ensure ADB forward
adb -s "$DEVICE" forward tcp:$PORT tcp:$PORT 2>/dev/null

echo "Connecting to Orbic Speed High-Privilege Shell..."
ssh -p $PORT -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $USER@127.0.0.1
