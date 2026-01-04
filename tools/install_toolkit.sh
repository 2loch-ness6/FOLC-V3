#!/bin/sh
# Tool Installer
LOG=/data/install.log

echo "[-] Starting Install at $(date)" > $LOG

# Proxy Setup (Tunnel to OnePlus 12)
export http_proxy=http://127.0.0.1:8888
export https_proxy=http://127.0.0.1:8888

# DNS
echo "nameserver 8.8.8.8" > /data/alpine/etc/resolv.conf

# Execute Install
echo "[-] Running APK..." >> $LOG
chroot /data/alpine /bin/sh -c "apk update && apk add tcpdump aircrack-ng nmap htop tmux python3 scapy py3-pip iw wireless-tools neofetch py3-pillow" >> $LOG 2>&1

echo "[-] Finished at $(date)" >> $LOG
