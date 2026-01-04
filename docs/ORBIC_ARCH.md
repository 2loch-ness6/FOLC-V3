# Orbic Flipper: Architectural Blueprint

## 1. System Overview
**Goal:** Transform the Orbic Speed (RC400L) into a standalone, pocket-sized penetration testing device controlled via:
1.  **Physical UI:** Device Screen + 2 Hardware Buttons (Standalone Mode).
2.  **Web UI:** Responsive Dashboard via WiFi or USB-Ethernet.
3.  **CLI:** SSH/ADB for advanced usage.

## 2. Core Components

### A. The "Brain" (Orbic Controller Service)
A central Python application (`orbic_controller.py`) running as a system service inside the Alpine Chroot.
*   **Responsibilities:**
    *   Manage Hardware Inputs (Buttons).
    *   Drive Hardware Output (Framebuffer/Display).
    *   Host the Web API/Frontend.
    *   Orchestrate Attack Modules (Aircrack, etc.).

### B. Hardware Abstraction Layer (HAL)
*   **Input:** Reads `/dev/input/eventX` (Power/Menu keys) using `evdev` or raw file reading.
    *   *Logic:* Short Press vs. Long Press detection.
*   **Output:** Writes raw RGB565 data to `/dev/fb0`.
    *   *Library:* Python `Pillow` (PIL) for drawing text/menus, converted to bytes.
*   **Network:** Wraps `ip`, `iw`, `wpa_supplicant`, and `hostapd` for mode switching (Client vs. AP vs. Monitor).

## 3. User Interface Design

### Physical UI (The "Flipper" Experience)
Designed for the limited 2-button interface.
*   **Navigation:**
    *   **Button 1 (Menu):** Scroll Down / Next Item.
    *   **Button 2 (Power):** Select / Enter.
    *   **Button 1 (Hold):** Back / Parent Menu.
*   **Menu Structure (Draft):**
    *   **Dashboard:** (IP, CPU, Battery, Mode)
    *   **WiFi Attacks:**
        *   *Scan APs*
        *   *Deauth Attack* (Aircrack)
        *   *Beacon Flood* (MDK4)
        *   *Capture Handshake*
    *   **Network Tools:**
        *   *Nmap Scan*
        *   *Spoof MAC*
        *   *TCP Dump* (Toggle)
    *   **System:**
        *   *SSH Server* (Toggle)
        *   *Web Server* (Toggle)
        *   *Reboot*

### Web UI (The "Command Center")
Hosted on `http://<device-ip>:8000`.
*   **Tech Stack:** Python Flask (Backend) + HTML/JS (Frontend).
*   **Features:**
    *   Real-time terminal output (WebSocket).
    *   File Manager (Download .pcap files).
    *   Complex Configuration (Input target lists, SSID wordlists).

## 4. USB Implementation (USB-Ethernet)
To make the device "Plug and Play" on a laptop/phone without ADB:
1.  **Gadget Config:** Use Android's `configfs` or system properties (`sys.usb.config`) to enable RNDIS.
2.  **Networking:** Assign a static IP (e.g., `172.16.42.1`) to the `rndis0` / `usb0` interface.
3.  **DHCP Server:** Run `dnsmasq` on the USB interface to give the host an IP.
*   **Result:** Plug it in -> Type `172.16.42.1` in browser -> Access Web UI.

## 5. Expanded Toolsuit (Wishlist)
1.  **Bettercap:** For Man-in-the-Middle (MITM) and sniffing (Go binary).
2.  **MDK4:** For advanced WiFi jamming/testing.
3.  **Kismet:** For passive visual mapping (might be too heavy for MDM9207 RAM).
4.  **Horst:** Lightweight WiFi analyzer (Spectrum view).
5.  **Responder:** LLMNR/NBT-NS Poisoner.

## 6. Implementation Plan (Phased)
1.  **Phase 1 (Foundation):** Setup Python `evdev` and `PIL` in Chroot. Create "Hello World" on the screen.
2.  **Phase 2 (Menu System):** Implement the Button->Screen loop.
3.  **Phase 3 (Web Core):** Start the Flask server.
4.  **Phase 4 (Attack Integration):** Link menu items to `subprocess.call("aircrack-ng ...")`.
5.  **Phase 5 (USB Ethernet):** Configure RNDIS for "Plug & Play" Web UI access.
