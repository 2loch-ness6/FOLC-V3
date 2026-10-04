#!/bin/sh
########################################################################
# netctl.sh — Host-side network plumbing for netcut
# Runs on HOST (not in chroot) with full capabilities.
# Handles wpa_supplicant, DHCP, ARP scanning — things that need
# direct netlink/raw socket access.
########################################################################

IFACE="wlan0"
WPA_CONF="/tmp/wpa_netctl.conf"
LOG="/data/rayhunter/netctl.log"

# State file lives in /data/rayhunter — accessible from both host and chroot
STATE="/data/rayhunter/netctl_state.json"
UDHCPC_SCRIPT="/data/rayhunter/udhcpc_apply.sh"

log() { echo "[$(date '+%H:%M:%S')] $1" >> "$LOG"; }

wifi_join() {
    SSID="$1"
    PSK="$2"

    log "JOIN: $SSID"

    # Wait for wlan0 — vendor stack must initialize it first
    TRIES=0
    while [ ! -d "/sys/class/net/$IFACE" ] && [ $TRIES -lt 30 ]; do
        TRIES=$((TRIES + 1))
        sleep 1
    done
    if [ ! -d "/sys/class/net/$IFACE" ]; then
        echo '{"ok":false,"error":"wlan0 not found — vendor WiFi not ready"}'
        log "JOIN FAILED: wlan0 not found"
        return 1
    fi
    log "wlan0 ready (waited ${TRIES}s)"

    killall wpa_supplicant 2>/dev/null
    killall hostapd 2>/dev/null
    # Do NOT kill wland or cpe_daemon
    sleep 1

    # Take wlan0 off vendor bridge, switch to managed mode
    brctl delif bridge0 "$IFACE" 2>/dev/null
    ip addr flush dev bridge0 2>/dev/null
    ip addr flush dev "$IFACE" 2>/dev/null
    ip link set "$IFACE" down 2>/dev/null
    iw dev "$IFACE" set type managed 2>/dev/null
    ip link set "$IFACE" up 2>/dev/null
    sleep 1

    cat > "$WPA_CONF" << EOF
ctrl_interface=/var/run/wpa_supplicant
update_config=1
network={
    ssid="$SSID"
    psk="$PSK"
    key_mgmt=WPA-PSK
    scan_ssid=1
}
EOF

    mkdir -p /var/run/wpa_supplicant
    wpa_supplicant -B -i "$IFACE" -c "$WPA_CONF" -D nl80211
    log "wpa_supplicant started"

    TRIES=0
    while [ $TRIES -lt 20 ]; do
        WPA_STATE=$(wpa_cli -i "$IFACE" status 2>/dev/null | grep "^wpa_state=" | cut -d= -f2)
        if [ "$WPA_STATE" = "COMPLETED" ]; then
            break
        fi
        TRIES=$((TRIES + 1))
        sleep 1
    done

    if [ "$WPA_STATE" != "COMPLETED" ]; then
        echo '{"ok":false,"error":"association failed","wpa_state":"'"$WPA_STATE"'"}'
        log "JOIN FAILED: state=$WPA_STATE"
        return 1
    fi

    log "Associated to $SSID"

    rm -f /tmp/dhcp_result
    udhcpc -i "$IFACE" -q -t 5 -n -s "$UDHCPC_SCRIPT" 2>/dev/null

    if [ ! -f /tmp/dhcp_result ]; then
        log "udhcpc failed, trying manual"
        udhcpc -i "$IFACE" -q -t 5 -n 2>/dev/null
        sleep 1
    fi

    MY_IP=$(ip addr show "$IFACE" 2>/dev/null | grep "inet " | awk '{print $2}' | cut -d/ -f1)
    if [ -z "$MY_IP" ]; then
        echo '{"ok":false,"error":"no IP from DHCP"}'
        log "JOIN FAILED: no DHCP"
        return 1
    fi

    GATEWAY=$(ip route 2>/dev/null | grep "default.*$IFACE" | awk '{print $3}')
    if [ -z "$GATEWAY" ]; then
        SUBNET=$(echo "$MY_IP" | cut -d. -f1-3)
        GATEWAY="${SUBNET}.1"
        ip route add default via "$GATEWAY" dev "$IFACE" 2>/dev/null
    fi

    MY_MAC=$(cat "/sys/class/net/$IFACE/address")

    GW_MAC=""
    arping -c 3 -I "$IFACE" "$GATEWAY" > /tmp/arping_gw 2>&1
    GW_MAC=$(grep -o '\[[0-9a-fA-F:]*\]' /tmp/arping_gw | head -1 | tr -d '[]')

    if [ -z "$GW_MAC" ]; then
        ping -c 1 -W 1 "$GATEWAY" >/dev/null 2>&1
        sleep 1
        GW_MAC=$(awk "/$GATEWAY/"'{print $4}' /proc/net/arp | head -1)
    fi

    SUBNET=$(echo "$MY_IP" | cut -d. -f1-3)

    echo 0 > /proc/sys/net/ipv4/ip_forward

    cat > "$STATE" << STATEOF
{"ok":true,"ip":"$MY_IP","gateway":"$GATEWAY","gateway_mac":"$GW_MAC","my_mac":"$MY_MAC","subnet":"$SUBNET","ssid":"$SSID","iface":"$IFACE"}
STATEOF

    log "JOIN OK: ip=$MY_IP gw=$GATEWAY gw_mac=$GW_MAC"
    cat "$STATE"
}

net_scan() {
    if [ ! -f "$STATE" ]; then
        echo '{"ok":false,"error":"not connected"}'
        return 1
    fi

    MY_IP=$(grep -o '"ip":"[^"]*"' "$STATE" | cut -d'"' -f4)
    SUBNET=$(grep -o '"subnet":"[^"]*"' "$STATE" | cut -d'"' -f4)

    if [ -z "$SUBNET" ]; then
        echo '{"ok":false,"error":"no subnet"}'
        return 1
    fi

    log "SCAN: ${SUBNET}.0/24"

    # Broadcast ping to populate ARP cache fast
    ping -b -c 3 -W 1 -I "$IFACE" "${SUBNET}.255" >/dev/null 2>&1
    ping -b -c 3 -W 1 -I "$IFACE" "255.255.255.255" >/dev/null 2>&1
    sleep 2

    # Quick targeted ping on common IPs to catch devices that ignore broadcast
    for i in 1 2 10 25 30 33 50 64 68 69 83 87 96 100 144 150 153 158 159 200 254; do
        ping -c 1 -W 1 "${SUBNET}.${i}" >/dev/null 2>&1 &
    done
    wait
    sleep 1

    HOSTS="["
    FIRST=1
    while IFS=' ' read -r ip hwtype flags mac mask dev; do
        if [ "$dev" = "$IFACE" ] && [ "$flags" = "0x2" ] && [ "$ip" != "$MY_IP" ]; then
            if [ $FIRST -eq 0 ]; then
                HOSTS="${HOSTS},"
            fi
            HOSTS="${HOSTS}{\"ip\":\"${ip}\",\"mac\":\"${mac}\"}"
            FIRST=0
        fi
    done < /proc/net/arp

    HOSTS="${HOSTS}]"

    log "SCAN: found $(echo "$HOSTS" | grep -o '"ip"' | wc -l) hosts"
    echo "{\"ok\":true,\"hosts\":${HOSTS}}"
}

net_status() {
    if [ ! -f "$STATE" ]; then
        echo '{"ok":true,"connected":false}'
        return
    fi

    WPA_STATE=$(wpa_cli -i "$IFACE" status 2>/dev/null | grep "^wpa_state=" | cut -d= -f2)
    MY_IP=$(ip addr show "$IFACE" 2>/dev/null | grep "inet " | awk '{print $2}' | cut -d/ -f1)

    if [ "$WPA_STATE" = "COMPLETED" ] && [ -n "$MY_IP" ]; then
        echo '{"ok":true,"connected":true,"ip":"'"$MY_IP"'","wpa_state":"'"$WPA_STATE"'"}'
    else
        echo '{"ok":true,"connected":false,"wpa_state":"'"$WPA_STATE"'"}'
    fi
}

net_disconnect() {
    killall wpa_supplicant 2>/dev/null
    ip addr flush dev "$IFACE" 2>/dev/null
    ip route flush dev "$IFACE" 2>/dev/null
    rm -f "$STATE"
    log "DISCONNECT"
    echo '{"ok":true}'
}

case "$1" in
    join)       wifi_join "$2" "$3" ;;
    scan)       net_scan ;;
    status)     net_status ;;
    disconnect) net_disconnect ;;
    *)
        echo "Usage: $0 {join <ssid> <psk>|scan|status|disconnect}"
        exit 1
        ;;
esac
