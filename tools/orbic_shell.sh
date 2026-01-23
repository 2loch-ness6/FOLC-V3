#!/bin/bash
# FOLC-V3 Native Host Shell (Backdoor)

PORT=9999

# Ensure ADB forward
adb forward tcp:$PORT tcp:$PORT 2>/dev/null

echo "Connecting to Orbic Speed Native Host Root (Port $PORT)..."
echo "Note: This is a raw shell. Use 'exit' to disconnect."
nc 127.0.0.1 $PORT
