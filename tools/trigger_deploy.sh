#!/bin/bash

# TRIGGER DEPLOYMENT (KALI SIDE)
# Stages files and triggers the Native Host Script.

DEPLOY_DIR="/sdcard/ORBIC_DEPLOY"
HOST_SCRIPT="orbic_deploy.sh"

echo "[*] Staging files to $DEPLOY_DIR..."

# Ensure dir exists (via host)
nsenter -t 1 -m /system/bin/sh -c "mkdir -p $DEPLOY_DIR"

# Copy files (Kali -> SDCard)
cp folc_ui.py "$DEPLOY_DIR/"
cp folc_core.py "$DEPLOY_DIR/"
cp start_folc_v2.sh "$DEPLOY_DIR/"
cp orbic_deploy.sh "$DEPLOY_DIR/"

echo "[*] Files staged."

echo "[*] Executing Native Deployment on Android Host..."
echo "    NOTE: connection will drop when device reboots."
echo "---------------------------------------------------"

# Execute Host Script via Magisk SU
# We use 'sh' to run it.
# We DO NOT wait for it to finish gracefully if it reboots.
nsenter -t 1 -m /system/bin/su -c "sh $DEPLOY_DIR/$HOST_SCRIPT"

echo "---------------------------------------------------"
echo "[*] Script finished (or connection dropped due to reboot)."
echo "[*] Please verify device status manually."