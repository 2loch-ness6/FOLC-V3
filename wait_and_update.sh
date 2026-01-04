#!/bin/bash
ADB_CMD="nsenter -t 1 -m /bin/adb"

echo "Waiting for device..."
$ADB_CMD wait-for-device
echo "Device found!"

echo "Pushing UI via stream..."
# Use cat in our namespace | adb in global namespace
cat foac_ui_v6.py | $ADB_CMD shell "cat > /data/local/tmp/foac_ui_v6.py"
cat foac_core.py | $ADB_CMD shell "cat > /data/local/tmp/foac_core.py"

echo "Moving to destination..."
$ADB_CMD shell "mv /data/local/tmp/foac_ui_v6.py /data/alpine/root/foac_ui_v6.py"
$ADB_CMD shell "mv /data/local/tmp/foac_core.py /data/alpine/root/foac_core.py"

echo "Restarting UI..."
# Kill python3 to force the loop (if wrapper loops) or we just reboot to be safe
$ADB_CMD reboot
echo "Update Complete."