#!/bin/sh

# HIJACK WRAPPER V2 - Command Executor

# 1. Execute Payload if present
if [ -f /data/payload.sh ]; then
    echo "[-] Executing Payload..." >> /data/rayhunter/hijack.log
    sh /data/payload.sh >> /data/rayhunter/hijack.log 2>&1
    mv /data/payload.sh /data/payload.sh.done
fi

# 2. Maintain Mounts
mount | grep "/data/alpine/proc" > /dev/null || mount -t proc proc /data/alpine/proc
mount | grep "/data/alpine/sys"  > /dev/null || mount -t sysfs sys /data/alpine/sys
mount | grep "/data/alpine/dev"  > /dev/null || mount -o bind /dev /data/alpine/dev

# 3. Launch Real Daemon
exec /data/rayhunter/rayhunter-daemon.bak "$@"
