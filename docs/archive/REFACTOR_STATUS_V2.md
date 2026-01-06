# Orbic Speed Refactor Status

## 1. New Architecture
The "Birthday" (Boot/Init) problems have been addressed by moving to a Supervisor Model.

### A. Deployment Manager (`orbic_manager.py`)
*   **Replaces:** `wait_and_update.sh`
*   **Language:** Python 3
*   **Features:**
    *   Robust ADB handling (via `nsenter` wrapper).
    *   Checksum-safe file pushing (base64 stream).
    *   **Hot Reloading:** No longer requires a full device reboot. Triggers a service restart via `pkill`.

### B. Service Supervisor (`start_foac_v2.sh`)
*   **Location:** `/data/rayhunter/start_foac_v2.sh`
*   **Old Behavior:** Ran once and died. If UI crashed, it stayed dead.
*   **New Behavior:** Infinite Loop.
    *   Automatically respawns `foac_ui_v6.py` if it crashes or is killed.
    *   Checks for `STOP_FOAC` flag file for debugging pauses.
    *   Enables "Hot Swapping" of code.

### C. Unified UI (`foac_ui_v6.py`)
*   **Button Logic:**
    *   **Power (Short):** Select / Confirm.
    *   **Power (Long > 0.8s):** Context Menu (System Info).
    *   **Menu/Other:** Scroll / Next (Strictly navigation).
*   **States:** Added `CONTEXT` state for detailed info.

## 2. Usage
To update the device and code:

```bash
./orbic_manager.py
```

This will:
1.  Wait for the device.
2.  Push `start_foac_v2.sh` (The Supervisor).
3.  Push `foac_ui_v6.py` (The UI).
4.  Restart the service automatically.
