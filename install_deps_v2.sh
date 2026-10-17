#!/bin/sh
# Force Route
ip route del default 2>/dev/null
ip route add default via 10.227.109.1 dev wlan0

# Set DNS
echo "nameserver 8.8.8.8" > /etc/resolv.conf
echo "nameserver 8.8.8.8" > /data/alpine/etc/resolv.conf

# Retry Install
echo "Retrying Install..." > /data/rayhunter/apk.log
chroot /data/alpine apk update >> /data/rayhunter/apk.log 2>&1
chroot /data/alpine apk add py3-pillow py3-evdev >> /data/rayhunter/apk.log 2>&1
echo "DONE" >> /data/rayhunter/apk.log
