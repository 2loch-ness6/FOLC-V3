# Orbic Speed (RC400L) Research & Root Status

## Device Identification
- **Model:** Orbic Speed (RC400L)
- **Marketing Name:** Orbic Speed 4G/5G Hotspot
- **Chipset:** Qualcomm MDM9207 (ARMv7)
- **Firmware Version:** ORB400L_V1.3.0_BVZRT_R220518
- **Kernel:** Linux 3.18.48 (Built Nov 2020)
- **OS:** Embedded Linux (based on OpenEmbedded/Yocto, not standard Android)

## Root Status
- **Vulnerability Found:** The device contains a setuid binary `/bin/rootshell`.
- **Exploitation:** Executing `adb shell "echo <command> | /bin/rootshell"` runs commands as `root`.
- **Privileges:**
  - `uid=0 (root)`
  - `gid=0 (root)`
  - **Capabilities:** Restricted. The root shell lacks `CAP_SYS_ADMIN` (cannot mount/unmount) and `CAP_DAC_OVERRIDE` (cannot ignore file permissions).
  
## Filesystem Analysis
- **Root (`/`):** Mounted as `rw` (ubifs).
- **Protected Paths:** `/bin` is owned by UID 1000 (likely `system` or `shell`) with `755` permissions. 
  - *Implication:* The restricted root user cannot modify `/bin` directly due to missing `CAP_DAC_OVERRIDE`.
- **Writable Paths:** `/data` is writable and executable.

## Recommended Action
To "root" the device for practical purposes:
1. **Temporary Root:** Use the `/bin/rootshell` shim to execute privileged commands.
2. **Tools:** Push static binaries (BusyBox, etc.) to `/data/local/tmp/` or `/data/` and execute them via the rootshell.
