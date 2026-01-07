# PHASE 3 DIRECTIVE: WEAPONIZATION & AUTOMATION

**Document Version:** 1.0
**Date:** January 2026
**Status:** ACTIVE
**Reference:** Follow-up to Phase 2 (Native Integration)

---

## 1. System Status
*   **Root Method:** Native Root Integration via `orbital_os_init.sh`.
*   **Access:**
    *   **Primary:** Backdoor (Netcat:9999) - Full Capabilities.
    *   **Secondary:** Frontdoor (`adb shell su`) - Restricted Caps, File Ops only.
*   **UI:** FOLC UI v10 (Strict State Management, Nmap Integration).
*   **Tools:** Nmap, Aircrack-ng, MacChanger (Alpine Chroot).

## 2. Mission Objective
Phase 3 focuses on expanding the offensive capabilities of the device and automating complex workflows.

**Goals:**
1.  **Toolchain Completion:**
    *   Resolve missing `mdk4` / `bettercap` dependencies (Cross-compile if needed).
    *   Integrate `tshark` or similar for on-device packet analysis.
2.  **Web Dashboard (C2):**
    *   Implement a Flask/FastAPI server in Alpine.
    *   Provide a web-based control panel for initiating scans and downloading `.pcap` files.
    *   Expose via USB Ethernet (RNDIS) if possible.
3.  **Automation:**
    *   "Mission Profiles": Scripted attack sequences (e.g., "Scan -> Deauth -> Capture Handshake").
    *   Auto-exfiltration of logs/captures when a known WiFi is detected.

## 3. Immediate Tasks for Architect
1.  **Web Server Prototype:** Create a basic Flask app (`src/web/app.py`) that can read `folc.log` and list pcap files.
2.  **Cross-Compilation Research:** Determine the exact build flags for `mdk4` on armv7 Alpine.
3.  **UI Refinement:** Add a "WEB SERVER" toggle to the UI.

**ACKNOWLEDGE:**
Confirm receipt of Phase 3 Directive.
