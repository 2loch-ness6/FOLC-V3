# Orbic Speed (RC400L) System Analysis & Future Roadmap

## 1. System Architecture

### Filesystem Layout
The device utilizes a hybrid filesystem structure typical of embedded Android/Linux systems:
*   **Root (`/`)**: Read-Only (RO) squashfs/erofs partition. Contains the base OS, init, and vendor binaries.
*   **UserData (`/data`)**: Read-Write (RW) partition. This is the primary persistence vector.
    *   `/data/alpine`: Contains the custom Alpine Linux chroot environment.
    *   `/data/rayhunter`: Stores the persistent exploit scripts (`rayhunter-daemon` wrapper) and logs.
*   **System (`/system`)**: Read-Only partition containing Android framework components and binaries.

### Network Interfaces
*   **`wlan0`**: The primary Wi-Fi interface (Qualcomm/Atheros). It supports Monitor Mode and Packet Injection, critical for the "Orbital Cannon" functionality.
*   **`rmnet0` / `rmnet_data0`**: The cellular modem interface (LTE/5G).
*   **`lo`**: Loopback interface, used for the internal ADB backdoor.

### Process Management
*   **Init System**: Standard Android `init` (PID 1).
*   **Service Hijack**: The exploit targets the `rayhunter-daemon` service. The system `init` attempts to launch the vendor binary, but encounters our `wrapper_v4.sh` script instead.
*   **Chroot Isolation**: The Alpine environment runs within a chroot at `/data/alpine`. It shares the kernel and network namespace with the host but maintains a separate filesystem view and package manager (`apk`).

## 2. Exploit Vectors

### Privilege Escalation
*   **Vulnerability**: The `rayhunter-daemon` service runs with effective UID 0 (root) and full capabilities.
*   **Mechanism**: By replacing the binary with a shell script, we inherit these privileges on boot.

### Persistence
*   **Method**: Filesystem Hijack.
*   **Path**: `/data/rayhunter/rayhunter-daemon`
*   **Execution**: Validated by `init.rc` on boot. The wrapper script launches the original binary (renamed) to prevent system instability, while spawning the backdoor and UI in the background.

### Access Control
*   **Backdoor**: A Netcat listener on `127.0.0.1:9999`.
*   **Access Method**: Requires `adb forward tcp:9999 tcp:9999` to bridge the USB connection to the local listener. This bypasses the need for an SSH server or exposed external port.

## 3. Toolchain Integration

### Installed Packages (Alpine Chroot)
*   **Core**: `busybox`, `alpine-base`, `python3`, `py3-pip`, `py3-pillow` (UI).
*   **Security**: `aircrack-ng` (suite), `tcpdump`, `nmap`, `scapy`.
*   **Utilities**: `htop`, `tmux`, `neofetch`, `iw`, `wireless-tools`, `evdev` (Python bindings).

### Custom Logic
*   **`folc_ui.py`**: The primary interface. Directly addresses the Framebuffer (`/dev/fb0`) for graphics and reads `/dev/input/event*` for button control.
*   **`folc_core.py`**: A Python wrapper for `iw`, `tcpdump`, and `aireplay-ng`, abstracting the shell commands into Python methods.
*   **`wrapper_v4.sh`**: The "Hypervisor" script that manages the environment setup (mounting `/proc`, `/sys`, `/dev` into chroot) and process lifecycle.

## 4. Measurable Outcomes
*   **Root Access**: Confirmed. Shell access via port 9999 yields `uid=0(root)`.
*   **Interface Status**: `wlan0` successfully enters Monitor Mode via `airmon-ng`/`iw`.
*   **UI Functionality**: Framebuffer takeover successful. Buttons (Power/Menu) mapped to Select/Scroll/Context actions.

---

## 5. Future Roadmap

### Phase 1: Hardware Hardening
*   **Antenna Mod**: Solder external SMA connectors to the board's IPEX test points to attach high-gain antennas for increased range on `wlan0`.
*   **Thermal Management**: Add passive heatsinks to the Qualcomm modem to sustain high-load packet injection sessions.

### Phase 2: Software Expansion
*   **Web Dashboard**: Implement a lightweight Flask/FastAPI server in the Alpine chroot.
    *   *Feature*: "War-Walking" map visualization using GPS data (if GPS hardware is accessible via AT commands).
    *   *Feature*: File browser to download `.pcap` captures directly via browser.
*   **Cellular Toolkit**:
    *   Research `AT` command set for the Snapdragon X12 modem.
    *   Implement Cell Tower spoofing or detailed signal analysis (Cell ID, Band locking).

### Phase 3: "Stealth Mode"
*   **Process Hiding**: Use `libprocesshider` or similar LD_PRELOAD techniques to mask the `python3` and `nc` processes from standard `ps` commands on the host system.
*   **Traffic Masquerading**: Ensure all exfiltration traffic mimics standard HTTPS traffic to avoid detection by upstream carrier DPI.

### Phase 4: Autonomous Drone Mode
*   **Scripting Engine**: Allow users to upload "Mission Profiles" (simple scripts) that execute automatically when a specific GPS coordinate or Wi-Fi beacon is detected.
