#!/bin/sh
# Alpine Install Payload
echo "[-] Starting Alpine Setup"
# Fix DNS
echo "nameserver 8.8.8.8" > /data/alpine/etc/resolv.conf

# Enter Chroot and Install
chroot /data/alpine /bin/sh -c "apk update && apk add tcpdump aircrack-ng iw wireless-tools neofetch"

echo "[-] Alpine Setup Complete"
