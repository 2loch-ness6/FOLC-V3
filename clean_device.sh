#!/bin/sh
mount -o remount,rw /
# Ensure clean config
echo "" > /etc/default/adbd
# Kill network blockers
killall QCMAP_ConnectionManager
killall qt_daemon
killall rayhunter-daemon.bak
# Kill adbd to apply clean config (Last step)
killall adbd