# GEMINI CONTEXT HANDOFF - PROJECT MARRIOT

## OPERATIONAL STATUS: GREEN
**Target:** Orbic Speed (RC400L)
**Environment:** Hybrid (Host + Alpine Chroot)
**Root Level:** FULL CAPABILITIES via Backdoor.

## KEY DISCOVERIES
1. **The Capability Glass Ceiling:**
   - `adbd` drops all capabilities except `SETUID`/`SETGID` from the bounding set.
   - Any process spawned via ADB (even with `LD_PRELOAD` root or SUID `su`) is trapped.
   - You cannot `mount`, `chroot`, or perform `net_admin` tasks via ADB shell.
2. **The Rayhunter Hijack (True Root):**
   - The device's "Root of Trust" for our purposes is the `/etc/init.d/rayhunter_daemon` service.
   - Because `init` launches it, it inherits **Full Capabilities** (`3fffffffff`).
   - Hijacking this service is the only way to get unrestricted access.
3. **Persistence:**
   - Root filesystem `/` is **UBIFS Read-Write**. Modifications to `/bin` persist reboots.
   - `LD_PRELOAD` in `/etc/init.d/adbd` grants immediate UID 0 in ADB, but capabilities remain restricted.

## ACCESS PROTOCOLS
- **GOD MODE (Full Caps):** `adb forward tcp:9999 tcp:9999 && nc localhost 9999`
- **BASIC ROOT (File Ops):** `adb shell` (Lands in `#` due to `nosetuid.so`)

## CURRENT ARCHITECTURE
- `/data/rayhunter/orbital_os_init.sh` is the master init script.
- It mounts Alpine, sets up the symlink bridge, and spawns the backdoor.
- Web C2 runs on port 8000.
- Async UI runs as `foac_ui_v9.py`.

## NEXT STEPS (PHASE 3)
1. Implement WiFi Tracker Detection (Bluetooth is hardware-missing).
2. Develop "Mission Profiles" (Automated attack scripts).
3. Secure the C2 interface.