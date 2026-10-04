#!/bin/sh
case "$1" in
    bound|renew)
        ip addr flush dev "$interface"
        ip addr add "$ip/${mask:-24}" dev "$interface"
        if [ -n "$router" ]; then
            ip route add default via "$router" dev "$interface"
        fi
        if [ -n "$dns" ]; then
            echo "nameserver $dns" > /data/alpine/etc/resolv.conf
        else
            echo "nameserver 8.8.8.8" > /data/alpine/etc/resolv.conf
        fi
        echo "$ip $mask $router $dns" > /tmp/dhcp_result
        ;;
esac
