#!/bin/sh
# FOAC SERVICE SUPERVISOR
LOG="/data/rayhunter/foac.log"
STOP_FLAG="/data/rayhunter/STOP_FOAC"

# Setup Environment
mount -t proc proc /data/alpine/proc 2>/dev/null
mount -t sysfs sys /data/alpine/sys 2>/dev/null
mount -o bind /dev /data/alpine/dev 2>/dev/null
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

while true; do
    if [ -f "$STOP_FLAG" ]; then
        echo "Stop flag found. Sleeping..." >> $LOG
        sleep 10
        continue
    fi
    
    echo "Starting UI..." >> $LOG
    chroot /data/alpine /usr/bin/python3 /root/foac_ui_v6.py >> $LOG 2>&1
    
    RET=$?
    echo "UI exited with code $RET. Respawning in 2s..." >> $LOG
    sleep 2
done