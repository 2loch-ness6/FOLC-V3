#!/bin/sh
# robust_connect.sh
# 1. Clean up previous attempts
killall wpa_supplicant udhcpc 2>/dev/null

# 2. Start WiFi (Background Daemon)
wpa_supplicant -B -i wlan0 -c /data/rayhunter/wifi.conf -D nl80211,wext > /data/rayhunter/wifi.log 2>&1

# 3. Wait 5s for association, then grab IP (Background)
(sleep 5; udhcpc -i wlan0 -b -q) > /data/rayhunter/dhcp.log 2>&1 &

exit 0
