#!/bin/sh
# Script to connect Orbic Speed to external WiFi (Client Mode)

SSID="OnePlus12"
PSK="123456789"
IFACE="wlan0"
CONF="/data/local/tmp/wpa_client.conf"

# 1. Kill conflicting services
killall hostapd 2>/dev/null
killall dnsmasq 2>/dev/null
killall wpa_supplicant 2>/dev/null

# 2. Cleanup interface
ip link set $IFACE down
brctl delif bridge0 $IFACE 2>/dev/null
ip addr flush dev $IFACE

# 3. Create config
cat > $CONF <<EOF
ctrl_interface=/var/run/wpa_supplicant
update_config=1

network={
    ssid="$SSID"
    psk="$PSK"
}
EOF

# 4. Start wpa_supplicant
echo "Starting wpa_supplicant..."
wpa_supplicant -B -i $IFACE -c $CONF -D nl80211,wext

# 5. Wait for association
echo "Waiting for connection..."
for i in $(seq 1 10); do
    STATUS=$(wpa_cli -i $IFACE status | grep wpa_state | cut -d= -f2)
    echo "Status: $STATUS"
    if [ "$STATUS" = "COMPLETED" ]; then
        break
    fi
    sleep 1
done

# 6. Get IP
echo "Requesting DHCP..."
udhcpc -i $IFACE -q

# 7. Check connectivity
echo "Testing connectivity..."
ping -c 1 8.8.8.8