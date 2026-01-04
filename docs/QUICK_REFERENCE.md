# Quick Reference Guide

Fast reference for common FOLC-V3 operations.

---

## 🔌 Device Connection

```bash
# Check if device is connected
adb devices

# Wait for device
adb wait-for-device

# Restart ADB server if issues
adb kill-server && adb start-server
```

---

## 🚪 Backdoor Access

```bash
# Forward the port
adb forward tcp:9999 tcp:9999

# Connect to backdoor
nc 127.0.0.1 9999

# Once connected, enter chroot
chroot /data/alpine /bin/bash
```

---

## 📱 Physical UI Controls

| Action | Button Combination |
|--------|-------------------|
| Navigate Down | Menu (short press) |
| Select / Confirm | Power (short press) |
| System Info | Power (long press) |
| Back / Cancel | Menu (long press) |

---

## 📡 WiFi Operations

### Scan Networks
```bash
# Using iw
iw wlan0 scan | grep SSID

# Using Python tool
python3 -c "from foac_core import WirelessTool; w=WirelessTool(); print(w.scan_networks())"
```

### Enable Monitor Mode
```bash
# Method 1: airmon-ng
airmon-ng start wlan0

# Method 2: Manual
ifconfig wlan0 down
iw wlan0 set type monitor
ifconfig wlan0 up
```

### Packet Capture
```bash
# Basic capture
tcpdump -i wlan0 -w /data/capture.pcap

# Capture with filters
tcpdump -i wlan0 -w /data/capture.pcap 'port 80 or port 443'

# View capture stats
tcpdump -r /data/capture.pcap | wc -l
```

### Deauth Attack (Authorized Testing Only!)
```bash
# Send 10 deauth packets
aireplay-ng --deauth 10 -a [TARGET_MAC] wlan0mon
```

---

## 🛠️ System Management

### Check Disk Space
```bash
df -h /data
```

### View Logs
```bash
# UI logs
cat /data/rayhunter/foac.log

# System logs
dmesg | tail -50
```

### Restart UI
```bash
# Kill current UI
pkill -f foac_ui_v6

# It will auto-restart via supervisor
```

### Full Reboot
```bash
adb reboot
```

---

## 📦 Package Management (Alpine)

```bash
# Enter chroot first
chroot /data/alpine /bin/bash

# Update package list
apk update

# Search for package
apk search [package_name]

# Install package
apk add [package_name]

# Remove package
apk del [package_name]

# List installed packages
apk list --installed
```

---

## 🔍 Network Analysis Tools

### Nmap Scans
```bash
# Ping scan
nmap -sn 192.168.1.0/24

# Port scan
nmap -p- 192.168.1.1

# Service detection
nmap -sV 192.168.1.1
```

### Tcpdump Examples
```bash
# Capture all traffic
tcpdump -i wlan0 -w capture.pcap

# Capture specific host
tcpdump -i wlan0 host 192.168.1.100 -w capture.pcap

# Capture with packet count limit
tcpdump -i wlan0 -c 1000 -w capture.pcap
```

### Aircrack-ng Suite
```bash
# Monitor mode
airmon-ng start wlan0

# Scan for networks
airodump-ng wlan0mon

# Targeted scan (save to file)
airodump-ng -c 6 --bssid [MAC] -w capture wlan0mon

# Deauth
aireplay-ng --deauth 10 -a [AP_MAC] wlan0mon
```

---

## 🔄 File Transfer

### Device to Computer
```bash
# Pull file
adb pull /data/capture.pcap ./

# Pull directory
adb pull /data/captures/ ./captures/
```

### Computer to Device
```bash
# Push file
adb push local_file.txt /data/

# Push directory
adb push local_dir/ /data/local_dir/
```

### Via Backdoor Shell
```bash
# On device, base64 encode
cat file.txt | base64

# On computer, copy output and decode
echo "[base64_string]" | base64 -d > file.txt
```

---

## 🩹 Troubleshooting

### UI Not Showing
```bash
# Check if process running
adb shell "ps | grep foac_ui"

# Check logs
adb shell "cat /data/rayhunter/foac.log"

# Manually restart
adb shell "pkill -f foac_ui"
```

### Backdoor Not Accessible
```bash
# Check if netcat is running
adb shell "ps | grep nc"

# Manually start backdoor
adb shell "nohup /bin/busybox nc -ll -p 9999 -e /bin/sh &"
```

### WiFi Not Working
```bash
# Check interface status
adb shell "ifconfig wlan0"

# Check if vendor services are blocking
adb shell "ps | grep -E 'hostapd|wpa_supplicant'"

# Kill vendor services
adb shell "killall hostapd wpa_supplicant"
```

### Alpine Chroot Not Working
```bash
# Check if mounted
adb shell "mount | grep alpine"

# Manual mount (if needed)
adb shell "mount -o bind /proc /data/alpine/proc"
adb shell "mount -o bind /sys /data/alpine/sys"
adb shell "mount -o bind /dev /data/alpine/dev"
```

---

## 🔐 Security Best Practices

### Before Testing
- [ ] Written authorization obtained
- [ ] Testing plan documented
- [ ] Legal compliance verified
- [ ] Backup created

### During Testing
- [ ] Monitor impact on target
- [ ] Document all findings
- [ ] Stop if issues arise
- [ ] Protect captured data

### After Testing
- [ ] Delete sensitive captures
- [ ] Report findings
- [ ] Restore device to normal
- [ ] Archive documentation

---

## 📞 Emergency Commands

### Factory Reset (Remove All Modifications)
```bash
# Connect via backdoor
adb forward tcp:9999 tcp:9999
nc 127.0.0.1 9999

# Stop services
pkill -f foac_ui
pkill nc

# Remove Alpine
rm -rf /data/alpine

# Restore original daemon
mv /data/rayhunter/rayhunter-daemon.orig /data/rayhunter/rayhunter-daemon

# Reboot
reboot
```

### Kill Switch (Stop All Testing Activity)
```bash
# Disable WiFi
adb shell "ifconfig wlan0 down"

# Stop packet capture
adb shell "pkill tcpdump"

# Stop all attacks
adb shell "pkill aireplay-ng"
```

---

## 📚 More Information

- **Full Documentation:** See README.md
- **Installation:** See INSTALL.md
- **Security:** See SECURITY.md
- **Contributing:** See CONTRIBUTING.md

---

*Keep this guide handy for quick reference during operations!*
