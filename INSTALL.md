# Installation Guide

This guide will walk you through the process of rooting your Orbic Speed (RC400L) and installing the FOLC-V3 security toolkit.

## ⚠️ Before You Begin

### Warnings

1. **This will void your warranty**
2. **This may violate your carrier's terms of service**
3. **There is a small risk of bricking your device**
4. **Backup any important data first**
5. **Understand the legal implications in your jurisdiction**

### What You'll Need

- **Hardware:**
  - Orbic Speed (RC400L) device
  - USB-A to USB-C cable (or appropriate adapter)
  - Computer (Linux/macOS recommended, Windows with WSL)
  
- **Software:**
  - ADB (Android Debug Bridge)
  - Git
  - Python 3 (optional, for deployment scripts)
  - Basic command-line knowledge

- **Time:** 
  - 30-60 minutes for full installation

---

## Step 1: Prepare Your Computer

### Install ADB

#### On Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install android-tools-adb android-tools-fastboot
```

#### On macOS:
```bash
brew install android-platform-tools
```

#### On Windows (WSL):
```bash
# In WSL Ubuntu
sudo apt-get install android-tools-adb

# Or download from Google:
# https://developer.android.com/studio/releases/platform-tools
```

### Verify ADB Installation
```bash
adb version
# Should output: Android Debug Bridge version 1.0.x
```

---

## Step 2: Enable ADB on Device

The Orbic Speed has ADB enabled by default over USB.

1. **Power on the device**
2. **Connect via USB** to your computer
3. **Test the connection:**
   ```bash
   adb devices
   ```
   
   You should see:
   ```
   List of devices attached
   1234567890ABCDEF    device
   ```

**Troubleshooting:**
- If no devices appear, try a different USB cable/port
- On Linux, you may need udev rules for the device
- Restart the ADB server: `adb kill-server && adb start-server`

---

## Step 3: Clone the Repository

```bash
git clone https://github.com/2loch-ness6/FOLC-V3.git
cd FOLC-V3
```

---

## Step 4: Verify Device Status

Run the verification script to check your device:

```bash
./tools/device_check.sh
```

This will check:
- ADB connectivity
- Device model (should be RC400L)
- Firmware version
- Available disk space
- Root exploit presence

**Expected Output:**
```
[✓] ADB Connected
[✓] Device: Orbic Speed (RC400L)
[✓] Firmware: ORB400L_V1.3.0_BVZRT_R220518
[✓] Root Exploit: /bin/rootshell found
[✓] Space Available: 2.5GB on /data
```

---

## Step 5: Initial Root Exploit

The device contains a setuid binary that grants root access:

```bash
# Test root access
adb shell "echo 'id' | /bin/rootshell"
```

Expected output:
```
uid=0(root) gid=0(root)
```

If you see this, **root access is confirmed!** ✅

---

## Step 6: Deploy the Backdoor

This establishes persistent root access via a netcat listener:

```bash
./exploits/deploy_backdoor.sh
```

The script will:
1. Upload the wrapper script to `/data/rayhunter/`
2. Replace the `rayhunter-daemon` binary
3. Make it executable
4. Start the backdoor service

**Verify the backdoor:**
```bash
# Forward the port
adb forward tcp:9999 tcp:9999

# Connect to backdoor
nc 127.0.0.1 9999
```

Type `id` and press Enter. You should see:
```
uid=0(root) gid=0(root) groups=0(root),1004(input),...
```

Type `exit` to close the connection.

---

## Step 7: Install Alpine Linux Chroot

This creates the secure, isolated environment for tools:

```bash
./exploits/install_alpine.sh
```

This process takes 10-15 minutes and will:
1. Download Alpine Linux ARMv7 rootfs (~3MB)
2. Extract to `/data/alpine/`
3. Mount necessary filesystems (`/proc`, `/sys`, `/dev`)
4. Configure networking
5. Set up package manager

**Progress indicators will show:**
```
[1/5] Downloading Alpine Linux...
[2/5] Extracting rootfs...
[3/5] Mounting filesystems...
[4/5] Configuring network...
[5/5] Testing chroot...
✓ Alpine Linux installation complete!
```

---

## Step 8: Install Security Tools

Now install the penetration testing toolkit:

```bash
./tools/install_toolkit.sh
```

This installs:
- `aircrack-ng` - WiFi security auditing suite
- `tcpdump` - Network packet analyzer
- `nmap` - Network scanner
- `wireshark-common` - Packet analysis tools
- `iw` / `wireless-tools` - WiFi management
- `python3` / `py3-pip` - Scripting environment
- `tmux` / `htop` - Terminal utilities
- `scapy` - Packet manipulation library

Installation takes ~20 minutes depending on network speed.

---

## Step 9: Deploy the UI

Install the custom framebuffer interface:

```bash
./tools/deploy_ui.sh
```

This will:
1. Copy `folc_ui.py` and `folc_core.py` to device
2. Install Python dependencies (`evdev`, `Pillow`)
3. Configure the service supervisor
4. Start the UI

**The device screen should now display the FOLC-V3 menu!**

---

## Step 10: Test the Installation

### Test WiFi Scanning

1. Use the **Menu** button to highlight "SCAN FREQUENCIES"
2. Press **Power** to select
3. Wait for scan to complete
4. Results should appear on screen

### Test Command Line Access

```bash
# Forward port
adb forward tcp:9999 tcp:9999

# Connect
nc 127.0.0.1 9999

# Enter Alpine chroot
chroot /data/alpine /bin/bash

# Test aircrack-ng
aircrack-ng --help

# Test tcpdump
tcpdump --version

# Exit
exit
```

---

## Troubleshooting

### ADB Device Not Found

**Problem:** `adb devices` shows no devices

**Solutions:**
1. Try a different USB cable (data cable, not just charging cable)
2. Try a different USB port (preferably USB 2.0)
3. Restart ADB server: `adb kill-server && adb start-server`
4. On Linux, check udev rules:
   ```bash
   lsusb | grep -i qualcomm
   # Add vendor ID to /etc/udev/rules.d/51-android.rules
   ```

### Root Access Denied

**Problem:** `/bin/rootshell` doesn't exist or doesn't work

**Possible Causes:**
- Different firmware version (only tested on ORB400L_V1.3.0_BVZRT_R220518)
- Device has been updated by carrier
- Wrong device model

**Solution:** Check firmware version:
```bash
adb shell "getprop ro.build.display.id"
```

### Alpine Installation Fails

**Problem:** "No space left on device"

**Solution:** Free up space on `/data` partition:
```bash
# Check space
adb shell "df -h /data"

# Remove temporary files if needed
adb shell "rm -rf /data/lost+found/*"
```

### UI Doesn't Appear on Screen

**Problem:** Screen remains black or shows vendor logo

**Solutions:**
1. Check if service is running:
   ```bash
   adb shell "ps | grep folc_ui"
   ```

2. Check logs:
   ```bash
   adb shell "cat /data/rayhunter/folc.log"
   ```

3. Manually restart:
   ```bash
   ./tools/restart_ui.sh
   ```

4. Verify framebuffer access:
   ```bash
   adb shell "ls -la /dev/fb0"
   # Should be: crw-rw---- 1 root graphics /dev/fb0
   ```

### WiFi Monitor Mode Fails

**Problem:** "Monitor mode not supported" or scan fails

**Solutions:**
1. Check if WiFi is in use by vendor services:
   ```bash
   adb shell "ps | grep -E 'hostapd|wpa_supplicant'"
   ```

2. Disable vendor WiFi services (if needed):
   ```bash
   ./tools/disable_vendor_wifi.sh
   ```

3. Manually enable monitor mode:
   ```bash
   # In the backdoor shell
   airmon-ng check kill
   airmon-ng start wlan0
   ```

---

## Uninstallation / Factory Reset

### Restore Vendor Functionality

To return the device to normal hotspot operation:

```bash
./tools/restore_vendor.sh
```

This will:
1. Restore original `rayhunter-daemon` binary
2. Re-enable vendor services
3. Remove backdoor
4. Keep Alpine chroot (optional removal)

### Complete Removal

To completely remove all modifications:

```bash
./tools/factory_reset.sh
```

**⚠️ Warning:** This will delete the Alpine chroot and all data!

### Manual Reset

If scripts fail, manual reset:

```bash
# Connect via backdoor
adb forward tcp:9999 tcp:9999
nc 127.0.0.1 9999

# Remove Alpine chroot
rm -rf /data/alpine

# Restore original daemon
mv /data/rayhunter/rayhunter-daemon.orig /data/rayhunter/rayhunter-daemon

# Remove backdoor
pkill nc

# Reboot
reboot
```

---

## Next Steps

Once installation is complete:

1. **Read the [Usage Guide](docs/USAGE.md)** for detailed examples
2. **Review [Security Considerations](SECURITY.md)** 
3. **Check the [Roadmap](docs/ROADMAP.md)** for upcoming features
4. **Join discussions** on GitHub for community support

---

## Additional Resources

- **ADB Cheat Sheet:** Common ADB commands for device management
- **Alpine Linux Docs:** https://wiki.alpinelinux.org/
- **Aircrack-ng Tutorial:** https://www.aircrack-ng.org/doku.php?id=tutorial
- **WiFi Security:** Understanding 802.11 protocol and vulnerabilities

---

**Installation complete! You now have a portable penetration testing device.**

*Remember to use responsibly and legally.*
