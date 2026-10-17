#!/bin/bash
# Emergency Script: Restore Vendor UI
# This modifies the on-device wrapper to execute the original daemon
# instead of suppressing it.

echo "Waiting for device..."
adb wait-for-device

echo "Patching wrapper to enable Vendor UI..."
# We replace the infinite sleep loop with an exec of the backup daemon
adb shell "sed -i 's/while true; do sleep 60; done/exec \/data\/rayhunter\/rayhunter-daemon.bak \"\$@\"/' /data/rayhunter/wrapper_v4.sh"

# Also fix wrapper_v5 if that's what is running
adb shell "sed -i 's/while true; do sleep 60; done/exec \/data\/rayhunter\/rayhunter-daemon.bak \"\$@\"/' /data/rayhunter/wrapper_v5.sh"

echo "Restarting daemon..."
# Killing the wrapper will make init respawn it, running our patched version
adb shell "killall -9 wrapper_v4.sh wrapper_v5.sh rayhunter-daemon"

echo "Done. Vendor UI should appear shortly."
