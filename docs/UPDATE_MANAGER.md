# FOLC-V3 Update Manager (v7.0)

The primary tool for managing the device is `tools/orbic_manager.py`. It has been re-engineered to be robust against ADB flakiness and permission issues by using a **Direct Socket Bridge**.

## How It Works

1.  **ADB Forwarding:** It establishes a TCP tunnel (`adb forward tcp:9999 tcp:9999`) to the device's backdoor.
2.  **Socket Comm:** It talks directly to `127.0.0.1:9999` using Python sockets, bypassing `adb shell`.
3.  **One-Shot Protocol:** It sends commands in the format `command; exit`. This ensures the remote shell executes the command and immediately closes the connection, preventing hangs.
4.  **Verification:** It calculates local MD5 hashes and compares them with remote hashes before pushing files.

## Usage

### 1. Automatic Update (Recommended)
This script wraps the Python manager and handles everything.
```bash
./tools/update_folc.sh
```

### 2. Manual Invocation
```bash
python3 tools/orbic_manager.py
```

### 3. Root Shell
To drop into a raw root shell on the device via the socket:
```bash
python3 tools/orbic_manager.py --shell
```

## Troubleshooting

*   **"Connection Refused":** Ensure the device is connected and the backdoor is running. The script attempts to revive it via `adb shell /bin/rootshell`, but this requires the `rootshell` binary to be working.
*   **"Verification Failed":** If the socket returns no data, check if the device is stuck or if `nc` is crashed. A hard reboot usually fixes this.
