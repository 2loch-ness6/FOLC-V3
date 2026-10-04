#!/bin/bash
# SESSION BRIDGE - Persistent command execution on Orbic
# Usage: ./session_bridge.sh "<command>"

DEVICE="e830926d"

CMD="$1"
if [ -z "$CMD" ]; then
    echo "Usage: $0 \"command\""
    exit 1
fi

adb -s "$DEVICE" forward tcp:9999 tcp:9999
echo "[*] Sending command to device..."

# Construct a safe payload that exits properly
PAYLOAD="(
$CMD
    echo '---SESSION_END---'
    exit
)"

# Execute and stream output until success marker
echo "$PAYLOAD" | nc -w 10 127.0.0.1 9999 | while read line; do
    if [[ "$line" == "---SESSION_END---" ]]; then
        break
    fi
    echo "$line"
done

echo "[+] Done."
