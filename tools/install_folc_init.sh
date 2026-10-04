#!/bin/sh
########################################################################
# install_folc_init.sh — Install FOLC init persistence via inittab hijack
# Replaces /usr/bin/mbimd with our init script.
# Uses adb push (writes directly to rw rootfs).
########################################################################

set -e
cd "$(dirname "$0")/.."

echo "[*] Checking device..."
adb devices | grep -q "device$" || { echo "[-] No device"; exit 1; }

echo "[*] Backing up original mbimd..."
adb shell "[ -f /usr/bin/mbimd.real ] && echo 'Backup exists' || cp /usr/bin/mbimd /usr/bin/mbimd.real 2>/dev/null && echo 'Backed up'"

echo "[*] Pushing FOLC init..."
chmod 755 exploits/folc_init.sh
adb push exploits/folc_init.sh /usr/bin/mbimd

echo "[*] Pushing support files..."
adb push tools/netctl.sh /data/rayhunter/netctl.sh
adb push tools/udhcpc_apply.sh /data/rayhunter/udhcpc_apply.sh
adb push src/netcut/netcut.py /data/alpine/usr/local/bin/netcut
adb push src/netcut/display.py /data/alpine/usr/local/bin/folc-display
adb push config/netcut.conf /data/rayhunter/netcut.conf
adb push tools/folc /data/alpine/usr/local/bin/folc-ctl

echo "[*] Setting permissions..."
adb shell "chmod 755 /data/rayhunter/netctl.sh /data/rayhunter/udhcpc_apply.sh"
adb shell "chmod 755 /data/alpine/usr/local/bin/netcut /data/alpine/usr/local/bin/folc-display"

echo "[*] Verifying..."
adb shell "head -3 /usr/bin/mbimd; echo '---'; ls -la /usr/bin/mbimd /usr/bin/mbimd.real"

echo ""
echo "[+] FOLC init installed."
echo "    Replaces mbimd in inittab (m2:5:respawn)"
echo "    Full capabilities from init — no rayhunter dependency."
echo ""
echo "    Reboot to activate: adb reboot"
echo "    Revert: adb push /usr/bin/mbimd.real /usr/bin/mbimd && adb reboot"
