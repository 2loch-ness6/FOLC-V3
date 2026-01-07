# Frontdoor Root Access Analysis & Strategy

**Document Version:** 2.0 (Post-Deployment Verification)
**Date:** January 2026
**Status:** ACTIVE

---

## 1. Executive Summary

Research and deployment testing on the Orbic Speed (RC400L) has confirmed the following regarding root access methods:

1.  **System Partition is Immutable:** The root filesystem (`/`) is `ubifs` but behaves as read-only for modifications to `/bin`. Changes to `/bin/su` do not persist across reboots.
2.  **ADB Shell is Cap-Bounded:** The `adbd` process runs with a restricted Capability Bounding Set (`CapBnd: ...c0`).
    *   `adb shell su` grants **UID 0** (Root User).
    *   It does **NOT** grant capabilities like `CAP_SYS_ADMIN` (required for `mount`, `chroot`, etc.).
3.  **Backdoor is Critical:** The service hijack method (`rayhunter-daemon` replacement) allows our process to inherit the full capabilities of the original system service (`3fffffffff`).

**Conclusion:**
The "Frontdoor" (`adb shell su`) is useful for basic filesystem operations but **cannot** replace the "Backdoor" (Netcat Service) for system initialization, mounting, or launching the Alpine container.

---

## 2. Access Method Comparison

| Feature | Frontdoor (`adb shell su`) | Backdoor (Port 9999) |
| :--- | :--- | :--- |
| **UID** | 0 (Root) | 0 (Root) |
| **Capabilities** | Restricted (`0xc0`) | Full (`3fffffffff`) |
| **Persistence** | N/A (Binary reverts) | **YES** (Via `/data` hijack) |
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

**One-Liner Execution:**
```bash
adb shell "echo 'command' | nc -w 5 localhost 9999"
```

### Secondary/Fallback: The Frontdoor
Use `adb shell su` only for:
- Simple file transfers to `/data`.
- Checking logs (`cat`, `tail`).
- verifying if the backdoor is running (`netstat`, `ps`).

## 4. Architecture Implications

*   **Init Script (`orbital_os_init.sh`):** Must continue to launch the Backdoor service as a critical component, not optional.
*   **Tools:** Wrappers should default to trying the Backdoor for privileged operations.

---

**Verified by:** GEMINI NEXUS
**Date:** Jan 7, 2026
