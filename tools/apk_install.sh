#!/bin/sh
# Helper to run APK commands via the Rayhunter Hijack
# Usage: ./apk_install package_name

CMD="apk update && apk add $@"

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
