#!/bin/bash
ADB_CMD="nsenter -t 1 -m /bin/adb"

echo "Waiting for device..."
$ADB_CMD wait-for-device
echo "Device found!"

echo "Pushing UI via stream..."
# Use cat in our namespace | adb in global namespace
cat folc_ui.py | $ADB_CMD shell "cat > /data/local/tmp/folc_ui.py"
cat folc_core.py | $ADB_CMD shell "cat > /data/local/tmp/folc_core.py"

echo "Moving to destination..."
$ADB_CMD shell "mv /data/local/tmp/folc_ui.py /data/alpine/root/folc_ui.py"
$ADB_CMD shell "mv /data/local/tmp/folc_core.py /data/alpine/root/folc_core.py"

echo "Restarting UI..."
# Kill python3 to force the loop (if wrapper loops) or we just reboot to be safe
$ADB_CMD reboot
echo "Update Complete."