# Orbic Speed (RC400L) Exploitation Toolkit

## 1. Project Overview
This directory contains research, exploit scripts, and toolkits for modifying the **Orbic Speed 5G Hotspot (RC400L)**. The project transforms the standard hotspot into a "Bare Bones" embedded Linux security appliance capable of network auditing, packet capture, and penetration testing.

**Current Status:** **FULLY ROOTED & OPERATIONAL**
*   **Root Level:** Unrestricted (UID 0 + Full Capability Set `0000003fffffffff`).
*   **Environment:** Hybrid (Qualcomm Embedded Linux Host + Alpine Linux 3.17 Chroot).
*   **Control:** Remote ADB/Shell via Port 9999 Backdoor + **Native Root (Frontdoor)**.

## 2. Device Hardware & OS
*   **Model:** Orbic Speed (RC400L) / "Orbic Speed 4G/5G"
*   **Chipset:** Unisoc (Spreadtrum) - RC400L Revision
*   **Kernel:** Linux 3.18.48 (Preempt, built Nov 2020)
*   **Firmware:** `ORB400L_V1.3.0_BVZRT_R220518`
*   **Modem:** Unisoc Integrated.
*   **Interfaces:**
    *   `wlan0`: WiFi (Unisoc `sprdwl_ng`) - **NO MONITOR MODE SUPPORT**.
    *   `rmnet0`: Raw Cellular Data Interface.

## 3. Exploit Methodology
The device was rooted using a multi-stage attack:
1.  **Initial Access:** Discovery of a suid binary `/bin/rootshell` which granted `uid=0` but with restricted capabilities (no mounting, no chroot).
2.  **Privilege Escalation:** Identified that the `rayhunter-daemon` (an IMSI-catcher detector installed on the device) runs with **Full Capabilities**.
3.  **Persistence (The Hijack):** The original `rayhunter-daemon` binary in `/data/rayhunter/` was replaced with a shell script wrapper (`wrapper_v4.sh`).
4.  **Native Root (LD_PRELOAD):** Modified `/etc/init.d/adbd` to preload `/data/local/nosetuid.so`, effectively neutralizing privilege dropping in the ADB Daemon.

**Note on Wireless Attacks:** The Unisoc hardware revision of the RC400L does not support Monitor Mode or Packet Injection via standard drivers. Automated deauth attacks are currently unsupported.

**Exploit Exception (Jamming):**
While smart injection is impossible, the device contains a proprietary engineering tool, **\`/usr/bin/iwnpi\`**, capable of raw RF transmission ("Continuous TX").
*   **Capability:** Broad spectrum denial-of-service (Jamming).
*   **Command:** \`iwnpi wlan0 set_channel <CH> <CH>; iwnpi wlan0 tx_start\`
*   **Warning:** This is a "noisy" attack that disrupts all communications on the channel.

## 4. Key Files & Scripts

| File | Purpose |
| :--- | :--- |
| `orbic_research.md` | Initial findings and hardware research notes. |
| `wrapper_v4.sh` | **CRITICAL.** The active persistent exploit. Replaces `rayhunter-daemon`. Mounts filesystems and spawns the backdoor. |
| `nosetuid.c` | Source for the LD_PRELOAD library that prevents `adbd` from dropping root. |
| `enter_alpine.sh` | Script to mount `/proc`, `/sys`, `/dev` and chroot into Alpine manually. |
| `apk_install.sh` | Helper to run `apk` commands via the hijacked service (Deprecated by direct backdoor access). |
| `install_toolkit.sh` | Script that installed the security tools via the backdoor. |
| `flipper.pl` | Perl script to hijack the framebuffer (`/dev/fb0`) and buttons, turning the device screen into a custom UI. |
| `wifi_setup.conf` | `wpa_supplicant` configuration for connecting the device to an external hotspot. |
| `tinyproxy.conf` | Config for the HTTP proxy used to tunnel `apk` traffic over ADB. |

## 5. System Architecture
### Filesystem Layout
*   `/` (Root): Read-Only UBIFS (Flash).
*   `/data`: Read-Write User Data.
    *   `/data/alpine`: The Alpine Linux Root Filesystem.
    *   `/data/rayhunter`: Location of the exploit persistence.

### Network Configuration
*   **Vendor Bloatware:** Disabled (`qt_daemon`, `QCMAP_ConnectionManager`, etc.) to free up `wlan0`.
*   **Connectivity:** The device is configured to connect as a WiFi Client to a hotspot (e.g., "OnePlus12").
*   **Routing:** Custom routing rules added to allow internet access from the Chroot.

### Access Mechanism
1.  **Native Frontdoor:** `adb shell` (Grants UID 0, but restricted capabilities).
2.  **Backdoor:** Netcat Listener on **Port 9999** (Grants Full Capabilities).
    *   **To Connect:** `adb forward tcp:9999 tcp:9999` then `nc 127.0.0.1 9999`.

## 6. Installed Security Toolkit
The Alpine Chroot is equipped with the following tools:
*   **Network Analysis:** `tcpdump`, `nmap`, `scapy`, `wireshark-common`
*   **Wireless Audit:** `aircrack-ng`, `iw`, `wireless-tools`
*   **Utilities:** `tmux`, `htop`, `python3`, `neofetch`, `pip`

## 7. Usage Guide
### Establishing a Session
To drop directly into the high-privilege Alpine environment from the host machine:
```bash
# Ensure ADB is connected
adb forward tcp:9999 tcp:9999
nc 127.0.0.1 9999
# Once connected, you are in a raw shell. To normalize:
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
chroot /data/alpine /bin/bash
```

### Restoring Vendor Functionality
To return the device to its original Hotspot behavior:
```bash
# Re-enable the startup scripts
adb shell "chmod +x /etc/init.d/start_qt_daemon /etc/init.d/start_QCMAP_ConnectionManager_le"
# Reboot
adb reboot
```
*Note: The root hijack will persist even after restoring vendor functionality.*

## 8. Phase 3 Update: Native Root via LD_PRELOAD
**Status:** SUCCESS (UID 0 Integration)
**Method:** 
1. Compiled `nosetuid.so` (intercepts `setuid`, `capset`, `prctl`) for ARMv7 SoftFP.
2. Injected `export LD_PRELOAD=/data/local/nosetuid.so` into `/etc/init.d/adbd`.
**Result:** `adb shell` now grants immediate `uid=0(root)` access.
**Limitations:** Capabilities are still bounded (`0xc0`) likely due to raw syscall usage or complex capability dropping sequences in `adbd`. Full system control (mount/chroot) still requires the Backdoor (Port 9999).
**Persistence:** Persistent modification to `/etc/init.d/adbd`.

## 9. Phase 3 Update: Wireless Attack Capabilities
**Test Date:** Jan 7, 2026
**Objective:** Validate 2.4/5GHz Deauth Attack
**Result:** **FAILED**
**Reason:** The Unisoc `sprdwl_ng` driver does not support standard Monitor Mode interfaces or packet injection via `iw`, `airmon-ng`, or `tcpdump`. 
**Mitigation:** Wireless attacks are not possible on this device without a custom driver.
