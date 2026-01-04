#!/bin/sh
# Start Friendly Orbital Assault Cannon UI
# Called by wrapper_v4.sh or init

LOG="/data/rayhunter/foac.log"
echo "--- FOAC Boot Start: $(date) ---" >> $LOG

# 1. Ensure mounts exist
mount -t proc proc /data/alpine/proc 2>/dev/null
mount -t sysfs sys /data/alpine/sys 2>/dev/null
mount -o bind /dev /data/alpine/dev 2>/dev/null

# 2. Initialize WiFi (Attempt using specific driver if available)
# Check for specific driver module path
WLAN_DRIVER_PATH="/usr/lib/modules/3.18.48/kernel/drivers/net/wireless/uwe5622_RK/unisocwifi/sprdwl_ng.ko"
if [ -f "$WLAN_DRIVER_PATH" ]; then
    echo "Attempting to load specific WiFi driver..." >> $LOG
    # Attempt to power cycle the chip via GPIOs
    echo 1 > /sys/class/gpio/export 2>/dev/null
    echo out > /sys/class/gpio/gpio38/direction 2>/dev/null
    echo 1 > /sys/class/gpio/gpio38/value 2>/dev/null # Power On
    echo 1 > /sys/class/gpio/gpio59/direction 2>/dev/null
    echo 1 > /sys/class/gpio/gpio59/value 2>/dev/null # Reset High

    insmod $WLAN_DRIVER_PATH >> $LOG 2>&1
    sleep 2
    # Try to bring up interface
    ifconfig wlan0 up >> $LOG 2>&1
    udhcpc -i wlan0 -s /data/simple.script -n >> $LOG 2>&1
fi

# 3. Launch UI (Background)
chroot /data/alpine /usr/bin/python3 /root/foac_ui.py >> $LOG 2>&1 &
echo "FOAC UI Launched PID: $! at $(date)" >> $LOG
echo "--- FOAC Boot End ---" >> $LOG