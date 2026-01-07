# Frontdoor Root Access Analysis & Strategy

**Document Version:** 3.0 (Post-Rayhunter Analysis)
**Date:** January 7, 2026
**Status:** ACTIVE

---

## 1. Executive Summary

Research into the original `rayhunter` architecture and further testing on the Orbic Speed (RC400L) has yielded significant breakthroughs:

1.  **System Partition is Writable:** The root filesystem (`/`) is `ubifs` and is mounted **Read-Write**. Previous assumptions of immutability were incorrect (likely due to temporary mount states or user error). We have successfully installed persistent binaries to `/bin`.
2.  **Native 'su' Installed:** We have installed `/bin/su` (symlinked to a SUID copy of `busybox`). This provides standard UID 0 access via `adb shell`.
3.  **Capability Restrictions Persist:** While `/bin/su` grants UID 0, the `adb shell` session itself is restricted by a Capability Bounding Set (`CapBnd: ...c0`) inherited from `adbd`. This prevents advanced operations (mount, chroot) even as root.
4.  **Rayhunter Privilege Model:** Analysis of the EFF `rayhunter` source and the device's `/etc/init.d/rayhunter_daemon` confirms that the original tool runs as a service started by `init`, inheriting Full Capabilities. This validates our "Backdoor" strategy (hijacking this service) as the correct "Native" method for full system control.

**Conclusion:**
We now have a "Hybrid" root model:
*   **Frontdoor (`/bin/su`):** Standard, persistent root for file operations and inspection.
*   **Backdoor (Port 9999):** Full-capability root for system initialization, container management, and network stack manipulation.

---

## 2. Access Method Comparison

| Feature | Frontdoor (`adb shell su`) | Backdoor (Port 9999) |
| :--- | :--- | :--- |
| **UID** | 0 (Root) | 0 (Root) |
| **Capabilities** | Restricted (`0xc0`) | Full (`3fffffffff`) |
| **Persistence** | **YES** (Binary in `/bin`) | **YES** (Via `/data` hijack) |
| **Mounting** | ❌ Fails | ✅ Works |
| **Chroot** | ❌ Fails | ✅ Works |
| **File Ops** | ✅ Works | ✅ Works |

## 3. Operational Strategy

### Primary Command Channel: The Backdoor
For all automated tools, deployment scripts, and complex operations, utilize the Backdoor service.

**Connection:**
```bash
adb forward tcp:9999 tcp:9999
nc 127.0.0.1 9999
```

### Secondary/Fallback: The Frontdoor
Use `adb shell su` for quick manual interaction:
```bash
adb shell
$ su
# id
uid=0(root) gid=0(root)
```

## 4. Technical Details

### The /bin/su Installation
To restore `/bin/su` on a fresh device:
```bash
# Using the Backdoor to perform the install
adb shell "echo 'cp /bin/busybox /bin/busybox_suid && chmod 4755 /bin/busybox_suid && ln -sf /bin/busybox_suid /bin/su' | nc localhost 9999"
```

### The Rayhunter Service
The root of trust is located at `/etc/init.d/rayhunter_daemon`.
It executes:
```bash
start-stop-daemon ... --startas /bin/sh -- -c "... exec /data/rayhunter/rayhunter-daemon ..."
```
Our exploit (`orbital_os_init.sh`) replaces the binary at `/data/rayhunter/rayhunter-daemon`, thus inheriting the `init` context.

---

**Verified by:** GEMINI NEXUS
**Date:** Jan 7, 2026