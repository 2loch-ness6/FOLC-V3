#!/bin/sh

# 1. Log our victory
echo "[-] Rayhunter Hijack Active: $(date)" >> /data/rayhunter/hijack.log

# 2. Launch Alpine Chroot Setup (Background)
# We wait 30s for the system to settle, then mount and launch SSH or just prepare the chroot
(
    sleep 30
    echo "[-] Setting up Alpine Chroot..." >> /data/rayhunter/hijack.log
    
    # Mounts
    mount -t proc proc /data/alpine/proc
    mount -t sysfs sys /data/alpine/sys
    mount -o bind /dev /data/alpine/dev
    
    echo "[+] Mounts complete. Full Root Achieved." >> /data/rayhunter/hijack.log
) &

# 3. Launch the REAL Rayhunter (Foreground)
# We must exec so we take the PID and don't break start-stop-daemon
exec /data/rayhunter/rayhunter-daemon.bak "$@"
