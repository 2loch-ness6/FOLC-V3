#!/bin/sh
# Fix Route (Try to guess gateway or just force device)
# udhcpc usually sets this, but maybe it failed to update the kernel table?
# We add a generic default route.
ip route add default dev wlan0 metric 100

# Set DNS
echo "nameserver 8.8.8.8" > /etc/resolv.conf
echo "nameserver 8.8.8.8" > /data/alpine/etc/resolv.conf

# Install Deps
chroot /data/alpine apk update > /data/rayhunter/apk.log 2>&1
chroot /data/alpine apk add py3-pillow py3-evdev >> /data/rayhunter/apk.log 2>&1

echo "DONE" >> /data/rayhunter/apk.log
