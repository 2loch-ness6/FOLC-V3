#!/bin/sh
# Helper to run APK commands via the Rayhunter Hijack (Proxy Enabled)
# Usage: ./apk_install package_name

# Define Proxy (ADB Tunnel)
PROXY="http://127.0.0.1:8888"

CMD="export http_proxy=$PROXY; export https_proxy=$PROXY; apk update && apk add $@"

echo "[-] Queueing command: $CMD"
cat > /data/payload.sh <<EOF
#!/bin/sh
echo "[-] Running: $CMD"
chroot /data/alpine /bin/sh -c "$CMD"
echo "[-] Done."
EOF

echo "[-] Triggering Execution (Restarting Service)..."
/etc/init.d/rayhunter_daemon restart

echo "[-] Waiting for output..."
tail -f /data/rayhunter/hijack.log
