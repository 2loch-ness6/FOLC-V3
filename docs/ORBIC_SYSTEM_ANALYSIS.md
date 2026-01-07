# Orbic Speed (RC400L) System Analysis
**Date:** Jan 7, 2026
**Analyst:** Gemini Nexus

## 1. Executive Summary
The Orbic Speed (RC400L) is a cost-optimized embedded 4G/5G hotspot. Extensive reverse engineering has revealed significant hardware and software limitations that define its operational envelope as a "Red Team" appliance.

**Verdict:** The device is an excellent **Passive Interceptor (MITM)** but a poor **Active RF Attacker**.

## 2. Hardware Limitations
### 2.1 WiFi Chipset (Unisoc)
*   **Driver:** `sprdwl_ng` (Spreadtrum/Unisoc).
*   **Architecture:** FullMAC (Firmware handles 802.11 management frames).
*   **Constraint:** The driver does not export a standard mac80211 Monitor Mode interface.
*   **Outcome:** Standard tools (`aircrack-ng`, `wireshark`, `tcpdump`) cannot capture raw headers or inject packets.

### 2.2 USB Controller
*   **Kernel Config:** `CONFIG_USB_OTG` is **Disabled**. `CONFIG_USB_EHCI/XHCI` (Host Controllers) are **Disabled**.
*   **Outcome:** The USB port functions *only* in Device/Gadget mode (Charging, ADB, Tethering).
*   **Impact:** External USB WiFi adapters cannot be used to bypass the Unisoc limitations.

## 3. Exploitability Analysis
### 3.1 "Deauth" Attacks (Active)
*   **Standard Method:** 802.11 Management Frames (Type 0xC0) -> **IMPOSSIBLE** (No Injection).
*   **Alternative Method:** "Jamming" via Factory Tools.
    *   **Tool:** `/usr/bin/iwnpi` (Unisoc Engineering Tool).
    *   **Capabilities:** Continuous TX, Carrier Suppression, Raw Power Output.
    *   **Status:** Can disrupt spectrum (DoS) but cannot perform targeted de-authentication. **Not stealthy.**

### 3.2 Man-in-the-Middle (Passive)
*   **Method:** Evil Twin / Rogue AP.
*   **Capabilities:**
    *   DNS Spoofing: **YES** (via `dnsmasq`/`iptables`).
    *   Captive Portal: **YES** (via Flask/Python).
    *   Traffic Inspection: **YES** (via `tcpdump` on bridge interface).
*   **Status:** This is the device's primary operational mode.

## 4. Strategic Recommendation
**Shift Focus to AP-Side Attacks.**
Instead of trying to force the device to be a Kali Linux clone (Packet Injection), leverage its strengths as a persistent, low-power Rogue AP. Focus development on:
1.  **Captive Portals:** High-fidelity cloning of hotel/flight login pages.
2.  **DNS Hijacking:** Redirecting targets to internal exploit servers.
3.  **Tunneling:** Using the LTE/5G backhaul to exfiltrate data from the WiFi clients.