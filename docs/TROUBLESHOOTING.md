# Troubleshooting Guide

Solutions to common issues with FOLC-V3.

---

## 🔍 Diagnostic Process

When something goes wrong, follow this systematic approach:

1. **Identify the symptom** - What exactly isn't working?
2. **Check the basics** - Is device connected? Is it powered on?
3. **Review logs** - Look for error messages
4. **Try simple fixes** - Restart, reconnect, etc.
5. **Escalate if needed** - Factory reset, seek help

---

## 📱 Device Connection Issues

### Problem: `adb devices` shows no devices

**Symptoms:**
- Running `adb devices` returns empty list
- Computer doesn't recognize device

**Solutions:**

1. **Check USB cable:**
   ```bash
   # Try different cable - must be data cable, not charge-only
   # Try different USB port - preferably USB 2.0
   ```

2. **Restart ADB server:**
   ```bash
   adb kill-server
   adb start-server
   adb devices
   ```

3. **Linux: Check udev rules:**
   ```bash
   # Find device vendor ID
   lsusb | grep -i qualcomm
   # Look for something like: Bus 001 Device 005: ID 05c6:90db
   
   # Create udev rule
   echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="05c6", MODE="0666"' | \
       sudo tee /etc/udev/rules.d/51-android.rules
   
   # Reload udev
   sudo udevadm control --reload-rules
   sudo udevadm trigger
   
   # Reconnect device
   ```

4. **Windows: Install drivers:**
   - Download Qualcomm USB drivers
   - Or use Windows Update to find drivers

5. **Check device is in right mode:**
   ```bash
   # Some devices have multiple USB modes
   # May need to cycle through with power+volume buttons
   ```

---

### Problem: ADB shows "unauthorized"

**Symptoms:**
```
List of devices attached
1234567890ABCDEF    unauthorized
```

**Solutions:**

This device doesn't have the standard Android authorization prompt, so:

1. **Wait a moment:**
   - Sometimes takes 10-20 seconds to authorize

2. **Restart ADB:**
   ```bash
   adb kill-server
   adb start-server
   ```

3. **Check if locked:**
   - Some firmware versions may have disabled ADB access
   - Try factory resetting device (will lose data!)

---

## 🚪 Backdoor Access Issues

### Problem: Cannot connect to port 9999

**Symptoms:**
```bash
nc 127.0.0.1 9999
# Connection refused or hangs
```

**Solutions:**

1. **Check port forwarding:**
   ```bash
   # Remove old forward
   adb forward --remove tcp:9999
   
   # Re-establish
   adb forward tcp:9999 tcp:9999
   
   # Verify
   adb forward --list
   # Should show: 1234567890ABCDEF tcp:9999 tcp:9999
   ```

2. **Check if backdoor is running:**
   ```bash
   adb shell "ps | grep nc"
   # Should see: root ... nc -ll -p 9999 -e /bin/sh
   ```

3. **Manually start backdoor:**
   ```bash
   # Use the root exploit
   adb shell "echo 'nohup /bin/busybox nc -ll -p 9999 -e /bin/sh &' | /bin/rootshell"
   
   # Wait 5 seconds
   sleep 5
   
   # Try connecting again
   nc 127.0.0.1 9999
   ```

4. **Check if busybox exists:**
   ```bash
   adb shell "ls -la /bin/busybox"
   # If not found, backdoor won't work
   ```

5. **Alternative: Use ADB shell directly:**
   ```bash
   # Less convenient but works
   adb shell "echo 'COMMAND' | /bin/rootshell"
   ```

---

## 📺 UI Display Issues

### Problem: Screen is blank or shows vendor logo

**Symptoms:**
- Device screen doesn't show FOLC UI
- Still shows carrier/vendor branding

**Solutions:**

1. **Check if UI process is running:**
   ```bash
   adb shell "ps | grep folc_ui"
   ```

2. **Check logs:**
   ```bash
   adb shell "cat /data/rayhunter/folc.log"
   # Look for error messages
   ```

3. **Verify files exist:**
   ```bash
   adb shell "ls -la /data/alpine/root/folc_ui.py"
   adb shell "ls -la /data/alpine/root/folc_core.py"
   ```

4. **Check framebuffer permissions:**
   ```bash
   adb shell "ls -la /dev/fb0"
   # Should be: crw-rw---- 1 root graphics
   ```

5. **Manually restart UI:**
   ```bash
   # Kill current (if running)
   adb shell "pkill -f folc_ui"
   
   # Wait for supervisor to restart (if configured)
   # Or manually start:
   adb forward tcp:9999 tcp:9999
   nc 127.0.0.1 9999
   # In backdoor shell:
   cd /data/alpine/root
   python3 folc_ui.py &
   exit
   ```

6. **Test framebuffer manually:**
   ```bash
   # Simple test - fill screen with color
   adb shell "dd if=/dev/zero of=/dev/fb0 bs=32768 count=1"
   # Screen should turn black
   ```

---

### Problem: UI shows but buttons don't work

**Symptoms:**
- Display works but pressing buttons has no effect

**Solutions:**

1. **Check input devices:**
   ```bash
   adb shell "ls -la /dev/input/event*"
   # Should see multiple eventX devices
   ```

2. **Test button events:**
   ```bash
   # In backdoor or ADB shell
   cat /proc/bus/input/devices
   # Look for keys (Power, Menu)
   ```

3. **Verify button codes:**
   ```bash
   # Run test script
   adb shell "python3 /data/alpine/root/find_buttons.py"
   # Press buttons and check output
   ```

4. **Check permissions:**
   ```bash
   adb shell "ls -la /dev/input/event0"
   # Should be accessible to root
   ```

---

## 📡 WiFi Issues

### Problem: Cannot scan networks

**Symptoms:**
- Scan returns empty or errors
- "No such device" errors

**Solutions:**

1. **Check interface exists:**
   ```bash
   adb shell "ifconfig wlan0"
   # Should show wlan0 with status
   ```

2. **Check if interface is up:**
   ```bash
   adb shell "ifconfig wlan0 up"
   ```

3. **Check for conflicting services:**
   ```bash
   adb shell "ps | grep -E 'hostapd|wpa_supplicant|QCMAP'"
   # If found, these are vendor services
   ```

4. **Kill vendor services:**
   ```bash
   adb shell "killall hostapd wpa_supplicant QCMAP_ConnectionManager qt_daemon"
   ```

5. **Reset WiFi:**
   ```bash
   adb shell "ifconfig wlan0 down"
   sleep 2
   adb shell "ifconfig wlan0 up"
   sleep 2
   adb shell "iw wlan0 scan | grep SSID"
   ```

6. **Check driver:**
   ```bash
   adb shell "dmesg | grep -i wlan"
   # Look for driver load messages or errors
   ```

---

### Problem: Monitor mode not working

**Symptoms:**
- `airmon-ng start wlan0` fails
- Cannot inject packets

**Solutions:**

1. **Check driver support:**
   ```bash
   adb shell "iw list | grep monitor"
   # Should show "monitor" in supported modes
   ```

2. **Manual monitor mode:**
   ```bash
   adb shell "ifconfig wlan0 down"
   adb shell "iw wlan0 set type monitor"
   adb shell "ifconfig wlan0 up"
   adb shell "iw wlan0 info"
   # Should show type: monitor
   ```

3. **Check for errors:**
   ```bash
   adb shell "dmesg | tail -50"
   # Look for WiFi-related errors
   ```

4. **Reboot and retry:**
   ```bash
   adb reboot
   # Wait for boot
   adb wait-for-device
   # Try again
   ```

---

## 🐧 Alpine Chroot Issues

### Problem: Cannot enter chroot

**Symptoms:**
```bash
chroot /data/alpine /bin/bash
# chroot: can't execute '/bin/bash': No such file or directory
```

**Solutions:**

1. **Check if Alpine is installed:**
   ```bash
   adb shell "ls -la /data/alpine/"
   # Should show full Linux filesystem
   ```

2. **Check if bash exists:**
   ```bash
   adb shell "ls -la /data/alpine/bin/bash"
   # Or try /bin/sh if bash not installed
   ```

3. **Check mount points:**
   ```bash
   adb shell "mount | grep alpine"
   # Should show /proc, /sys, /dev mounted
   ```

4. **Manual mount:**
   ```bash
   adb forward tcp:9999 tcp:9999
   nc 127.0.0.1 9999
   # In backdoor:
   mount -o bind /proc /data/alpine/proc
   mount -o bind /sys /data/alpine/sys
   mount -o bind /dev /data/alpine/dev
   chroot /data/alpine /bin/sh
   ```

5. **Reinstall Alpine:**
   ```bash
   # If completely broken, may need to reinstall
   # See INSTALL.md section 7
   ```

---

### Problem: Package installation fails

**Symptoms:**
```bash
apk add package
# ERROR: unable to select packages
```

**Solutions:**

1. **Update package index:**
   ```bash
   # In chroot
   apk update
   apk add package
   ```

2. **Check network connectivity:**
   ```bash
   # In chroot
   ping -c 3 8.8.8.8
   # If fails, networking issue
   ```

3. **Check DNS:**
   ```bash
   # In chroot
   cat /etc/resolv.conf
   # Should have nameserver entries
   
   # If empty, add:
   echo "nameserver 8.8.8.8" > /etc/resolv.conf
   ```

4. **Check repository configuration:**
   ```bash
   # In chroot
   cat /etc/apk/repositories
   # Should have Alpine mirror URLs
   
   # If wrong, fix:
   echo "http://dl-cdn.alpinelinux.org/alpine/v3.17/main" > /etc/apk/repositories
   echo "http://dl-cdn.alpinelinux.org/alpine/v3.17/community" >> /etc/apk/repositories
   ```

5. **Use cache if offline:**
   ```bash
   # If you have cached packages
   apk add --allow-untrusted /path/to/package.apk
   ```

---

## 💾 Storage Issues

### Problem: No space left on device

**Symptoms:**
```
write: No space left on device
```

**Solutions:**

1. **Check disk usage:**
   ```bash
   adb shell "df -h /data"
   ```

2. **Clean packet captures:**
   ```bash
   adb shell "rm /data/*.pcap"
   adb shell "rm /data/captures/*.pcap"
   ```

3. **Clean logs:**
   ```bash
   adb shell "rm /data/*.log"
   adb shell "echo '' > /data/rayhunter/folc.log"
   ```

4. **Clean Alpine cache:**
   ```bash
   # In chroot
   apk cache clean
   rm -rf /var/cache/apk/*
   ```

5. **Check for large files:**
   ```bash
   adb shell "find /data -type f -size +10M"
   ```

6. **Last resort - remove Alpine:**
   ```bash
   # WARNING: Will lose all Alpine data
   adb shell "rm -rf /data/alpine"
   ```

---

## 🔋 Power Issues

### Problem: Device keeps turning off

**Possible causes:**
- Battery drained
- Thermal shutdown
- Power button held too long

**Solutions:**

1. **Charge the device** - Connect to power
2. **Check temperature** - Let it cool down
3. **Review UI code** - May be power button handling issue

---

## 🚨 Emergency Recovery

### Problem: Device is completely unresponsive

**Last resort recovery:**

1. **Hard reset:**
   - Hold Power button for 10+ seconds
   - Device should power off
   - Wait 10 seconds
   - Power back on

2. **Factory reset (if accessible):**
   - May require vendor-specific key combo
   - Usually Power + Volume buttons during boot
   - **WARNING: Loses all data**

3. **Remove battery (if possible):**
   - Some models have removable battery
   - Remove for 30 seconds
   - Reinsert and power on

4. **Flash stock firmware (advanced):**
   - Requires firmware image and flash tool
   - See XDA forums or manufacturer site
   - Should only be done if device is bricked

---

## 📊 Performance Issues

### Problem: UI is slow or laggy

**Solutions:**

1. **Check CPU usage:**
   ```bash
   adb shell "top -n 1"
   # Look for processes using high CPU
   ```

2. **Check memory:**
   ```bash
   adb shell "free -m"
   # Check if memory is full
   ```

3. **Kill unnecessary processes:**
   ```bash
   adb shell "killall tcpdump nmap"
   ```

4. **Optimize UI code:**
   - Reduce refresh rate
   - Simplify graphics
   - See source code comments

---

## 🆘 Getting Help

If none of these solutions work:

1. **Check GitHub Issues:**
   - Search for similar problems
   - Review closed issues

2. **Create New Issue:**
   - Use issue template
   - Include logs and error messages
   - Describe what you've tried

3. **GitHub Discussions:**
   - Ask questions
   - Community may have solutions

4. **Provide Details:**
   ```bash
   # Helpful diagnostic info:
   adb shell "getprop ro.build.display.id"  # Firmware version
   adb shell "uname -a"                      # Kernel info
   adb shell "df -h"                         # Disk space
   adb shell "free -m"                       # Memory
   adb shell "ps | head -20"                 # Running processes
   ```

---

## 🔧 Prevention

To avoid issues:

- ✅ Keep backups before major changes
- ✅ Test one thing at a time
- ✅ Document what you do
- ✅ Monitor disk space
- ✅ Review logs regularly
- ✅ Keep device charged
- ✅ Update documentation when you fix something

---

**Remember: Most issues have simple solutions. Stay calm and debug systematically!**
