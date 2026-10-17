# FOLC-V3: Orbic Speed (RC400L) Development Context

## 1. Project Overview
**FOLC-V3** (Formerly FOAC) is a security research toolkit for the **Orbic Speed 5G Hotspot (RC400L)**. It transforms the device into a portable penetration testing appliance running a hybrid Linux environment.

- **Target Device:** Qualcomm MDM9207 (ARMv7) running Linux 3.18.48.
- **Target Firmware:** `ORB400L_V1.3.0_BVZRT_R220518` (Vulnerable to `/bin/rootshell` SUID exploit).
- **Architecture:** Hybrid system combining a Read-Only vendor Host OS with a Read-Write Alpine Linux 3.17 Guest environment (Chroot).

## 2. Access Mechanisms (The "Three Doors")
The project implements three distinct ways to interact with the device as root:

| Method | Type | Tool/Binary | Command | Persistence |
| :--- | :--- | :--- | :--- | :--- |
| **Initial Exploit** | Vector | `/bin/rootshell` | `echo 'id' \| /bin/rootshell` | Built-in (Vendor) |
| **Front Door** | **Primary** | `/bin/ksu` | `adb shell su` | Persistent (Custom) |
| **ADB Root** | Optional | `nosetuid.so` | `adb shell` (Directly root) | Persistent (Custom) |
| **Backdoor** | Fallback | `busybox nc` | `nc localhost 9999` | Service-based |

- **`ksu` (Front Door):** A minimal SUID binary installed at `/bin/ksu` and symlinked to `/bin/su`. This is the preferred way for scripts and users to gain root.
- **`nosetuid.so`:** An LD_PRELOAD library that intercepts privilege-dropping syscalls in `adbd`, maintaining root across ADB sessions.

## 3. System Architecture & Init Flow
The system is initialized via a hijack of the vendor `rayhunter-daemon` service.

### Execution Chain:
1. **Boot:** System `init` launches `/data/rayhunter/rayhunter-daemon` (which is our `wrapper_v4.sh`).
2. **Wrapper:** `wrapper_v4.sh` calls `/data/rayhunter/orbital_os_init.sh`.
3. **Initialization (`orbital_os_init.sh`):**
   - Mounts Alpine filesystems: `proc`, `sys`, `/dev` (bind-mount).
   - Sets up **Symlink Bridge**: Links host binaries into the Alpine environment.
   - Starts **Backdoor**: Netcat listener on port 9999.
   - Launches **FOLC UI**: Runs `start_folc_v2.sh` to start the framebuffer UI.

### Filesystem Layout:
- **Host Read-Only:** `/`, `/bin`, `/sbin`, `/etc`.
- **Host Read-Write:** `/data` (UBIFS partition).
- **Alpine Guest:** `/data/alpine` (The toolkit's primary runtime).
- **Persistence Dir:** `/data/rayhunter` (Exploit scripts and logs).

## 4. Key Directory & File Map
- **`src/core/folc_core.py`:** Python wrappers for `iw`, `airmon-ng`, `tcpdump`, and `cellular` tools.
- **`src/ui/folc_ui.py`:** Main UI logic using `PIL` for framebuffer rendering and `evdev` for button input.
- **`src/web/app.py`:** Flask-based web dashboard (Port 8080).
- **`tools/setup.sh`:** Master installation script (Dependency checks, model verification, full deployment).
- **`tools/test_folc.sh`:** Comprehensive test suite for Android 14/Termux/Kali environments.
- **`ksu.c` / `nosetuid.c`:** Source for native C components.
- **`Makefile`:** Cross-compilation for ARMv7/ARM64.

## 5. Development & Deployment Workflows

### Deployment
- **Full Provisioning:** Run `./tools/setup.sh` from a host with ADB.
- **Code Updates:** Run `./tools/deploy_folc.sh` to sync Python source and UI files.
- **Building Binaries:** Run `make` (Requires Android NDK or `arm-linux-gnueabi-gcc`).

### Testing & Verification
- **Run System Tests:** `./tools/test_folc.sh`
- **Check Logs:** `adb shell cat /data/rayhunter/orbital_os.log`
- **Verify UI:** Screen should show "FOLC v3" with menu items.

### Interacting with Alpine
To enter the toolkit environment manually:
```bash
adb shell su -c "chroot /data/alpine /bin/bash"
```

## 6. Critical Safety & Operational Rules
1. **Never** attempt to remount `/` as RW unless you have a recovery plan. The device is brittle.
2. **Persistent Root:** Always verify `ksu` permissions (`4755`) after modification. If broken, use the Backdoor (9999) or Initial Exploit (`/bin/rootshell`) to fix.
3. **Resource Management:** The device has limited RAM. Ensure Python threads (scanning/UI) are started with `daemon=True` for clean cleanup.
4. **Button Input:** The UI listens to `/dev/input/event*`. Avoid running multiple UI instances as they will compete for input events.
5. **Framebuffer:** Direct writes to `/dev/fb0` are used. Ensure the vendor UI (if any) is stopped to avoid flickering.