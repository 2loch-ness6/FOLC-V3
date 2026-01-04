# Installation Script for Root Backdoor
echo "[-] Moving UI Files..."
mv /data/local/tmp/foac_ui_v6.py /data/alpine/root/foac_ui_v6.py
mv /data/local/tmp/foac_core.py /data/alpine/root/foac_core.py

echo "[-] Moving Startup Scripts..."
mv /data/local/tmp/start_foac_v2.sh /data/rayhunter/start_foac_v2.sh
chmod +x /data/rayhunter/start_foac_v2.sh

mv /data/local/tmp/wrapper_v4.sh /data/rayhunter/wrapper_v4.sh
chmod +x /data/rayhunter/wrapper_v4.sh

echo "[-] Installing Dependencies..."
chroot /data/alpine apk add py3-pillow
chroot /data/alpine pip install evdev

echo "[-] Updating Persistence..."
cp /data/rayhunter/wrapper_v4.sh /data/rayhunter/rayhunter-daemon

echo "[+] Done. Rebooting..."
reboot
