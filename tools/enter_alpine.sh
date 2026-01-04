#!/bin/sh
# Alpine Chroot Launcher

CHROOT_DIR="/data/alpine"

# 1. Setup DNS (Use Google DNS if host is empty)
echo "nameserver 8.8.8.8" > $CHROOT_DIR/etc/resolv.conf

# 2. Mount System Filesystems
# We check if they are already mounted to avoid errors
mount | grep "$CHROOT_DIR/proc" > /dev/null || mount -t proc proc $CHROOT_DIR/proc
mount | grep "$CHROOT_DIR/sys" > /dev/null || mount -t sysfs sys $CHROOT_DIR/sys
mount | grep "$CHROOT_DIR/dev" > /dev/null || mount -o bind /dev $CHROOT_DIR/dev

# 3. Enter Chroot
echo "[-] Entering Alpine Linux..."
# Set path to include standard bin dirs
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
chroot $CHROOT_DIR /bin/sh -l
