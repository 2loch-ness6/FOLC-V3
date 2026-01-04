# FOLC-V3: Orbic Speed Exploitation & Security Toolkit

![Status](https://img.shields.io/badge/status-experimental-orange)
![Device](https://img.shields.io/badge/device-Orbic%20RC400L-blue)
![Root](https://img.shields.io/badge/root-achieved-green)

## ⚠️ IMPORTANT DISCLAIMER

**This project is for educational and authorized security research purposes only.**

- Modifying this device may void your warranty
- Unauthorized access to networks is illegal
- Use only on networks you own or have explicit permission to test
- The authors are not responsible for misuse or damage
- This may violate your carrier's terms of service
- Some functionality may be illegal in your jurisdiction

**By using this toolkit, you accept full responsibility for your actions.**

---

## 📋 Project Overview

FOLC-V3 transforms the **Orbic Speed 5G Hotspot (Model RC400L)** into a portable embedded Linux security appliance, similar in concept to devices like the Flipper Zero or WiFi Pineapple, but utilizing commodity cellular hardware.

The device becomes capable of:
- **Network Security Auditing:** WiFi scanning, packet capture, network mapping
- **Wireless Testing:** Monitor mode, packet injection, deauth attacks
- **Penetration Testing:** Portable toolkit with nmap, aircrack-ng, tcpdump, scapy
- **Custom Interface:** Physical button-driven UI on the device's built-in screen
- **Remote Access:** Backdoor shell access via ADB for advanced operations

### What Makes This Interesting?

1. **Cheap & Available:** The RC400L is an inexpensive, mass-produced device
2. **Capable Hardware:** Qualcomm MDM9207, WiFi with monitor mode, 5G modem
3. **Portable:** Battery-powered, pocket-sized, inconspicuous form factor
4. **Rooted:** Full root access with unrestricted capabilities
5. **Dual-Boot Approach:** Maintains vendor firmware while adding custom Alpine Linux environment

---

## 🔧 Device Specifications

| Component | Details |
|-----------|---------|
| **Model** | Orbic Speed (RC400L) |
| **Chipset** | Qualcomm MDM9207 (ARMv7) |
| **Kernel** | Linux 3.18.48 |
| **Firmware** | ORB400L_V1.3.0_BVZRT_R220518 |
| **Modem** | Qualcomm Snapdragon X12 LTE/5G |
| **WiFi** | Atheros/Qualcomm (Monitor Mode Capable) |
| **Display** | 128x128 pixel LCD |
| **Buttons** | 2 physical buttons (Power + Menu) |

---

## 🎯 Current Status

**✅ FULLY ROOTED & OPERATIONAL**

- ✅ Root privileges achieved (UID 0, full capability set `0000003fffffffff`)
- ✅ Persistent backdoor via port 9999
- ✅ Alpine Linux 3.17 chroot environment
- ✅ Security toolkit installed (aircrack-ng, nmap, tcpdump, etc.)
- ✅ Custom framebuffer UI with button controls
- ✅ WiFi monitor mode and packet injection working
- ✅ Hot-reload deployment system

---

## 🏗️ Architecture

### Exploit Chain

1. **Initial Access:** Discovery of SUID binary `/bin/rootshell` (restricted root)
2. **Privilege Escalation:** Identified `rayhunter-daemon` runs with full capabilities
3. **Persistence:** Replace daemon with wrapper script that inherits privileges
4. **Environment:** Mount Alpine Linux chroot at `/data/alpine`
5. **Backdoor:** Spawn netcat listener on localhost:9999

### System Layout

```
Orbic Speed (RC400L)
├── Host OS (Qualcomm Embedded Linux)
│   ├── /bin/rootshell (SUID exploit vector)
│   ├── /data/rayhunter/ (persistence location)
│   └── /dev/fb0, /dev/input/* (hardware access)
│
└── Alpine Linux Chroot (/data/alpine)
    ├── Security Tools (aircrack-ng, nmap, tcpdump)
    ├── Python Environment (UI & automation)
    └── Package Manager (apk)
```

### Access Methods

1. **Physical UI:** 128x128 screen + 2 buttons (standalone operation)
2. **Backdoor Shell:** `adb forward tcp:9999 tcp:9999; nc 127.0.0.1 9999`
3. **ADB:** Standard Android Debug Bridge over USB

---

## 📁 Repository Structure

```
FOLC-V3/
├── src/                 # Source code
│   ├── ui/              # User interface implementations
│   │   └── foac_ui_v6.py   # Current UI (framebuffer-based)
│   └── core/            # Core functionality libraries
│       └── foac_core.py    # Wireless tools wrapper
├── exploits/            # Root exploit and persistence scripts
│   ├── wrapper_v4.sh       # Active persistence exploit
│   └── ...                 # Historical exploit versions
├── tools/               # Utility scripts and helpers
│   ├── setup.sh            # Master installation script
│   ├── deploy_foac.sh      # Deploy UI to device
│   ├── orbic_manager.py    # Deployment manager
│   └── ...                 # Other utilities
├── config/              # Configuration files
│   ├── wifi_setup.conf     # WiFi client configuration
│   └── tinyproxy.conf      # Proxy configuration
├── docs/                # Additional documentation
│   ├── ROADMAP.md          # Future development plans
│   ├── TROUBLESHOOTING.md  # Common issues and solutions
│   ├── QUICK_REFERENCE.md  # Command quick reference
│   ├── PROJECT_SUMMARY.md  # Detailed project analysis
│   └── ...                 # Original research docs
├── archive/             # Deprecated/historical files
│   └── README.md           # Archive explanation
├── README.md            # This file
├── INSTALL.md           # Detailed installation guide
├── SECURITY.md          # Security policy and best practices
├── CONTRIBUTING.md      # Contribution guidelines
├── LICENSE              # MIT License with additional terms
└── requirements.txt     # Python dependencies
```

**Note:** This repository was recently reorganized for clarity. If you have an older checkout, scripts may reference old file locations. Run `git pull` to get the latest structure.

---

## 🚀 Quick Start

### Prerequisites

- Orbic Speed (RC400L) device
- USB cable
- Computer with ADB installed
- Linux/macOS recommended (Windows works with WSL)

### Installation

> **⚠️ Warning:** This will modify your device. Backup any important data first.

1. **Enable ADB on device:**
   ```bash
   # Device should be detected when plugged in
   adb devices
   ```

2. **Clone this repository:**
   ```bash
   git clone https://github.com/2loch-ness6/FOLC-V3.git
   cd FOLC-V3
   ```

3. **Run the deployment script:**
   ```bash
   ./tools/setup.sh
   ```
   
   This will:
   - Verify device connectivity
   - Install the exploit chain
   - Set up Alpine Linux chroot
   - Install security tools
   - Deploy the custom UI

4. **Access the backdoor:**
   ```bash
   adb forward tcp:9999 tcp:9999
   nc 127.0.0.1 9999
   ```

For detailed instructions, see [INSTALL.md](INSTALL.md)

---

## 💡 Usage

### Physical Interface

The device UI is controlled with two buttons:

- **Menu Button (Short Press):** Navigate down / Next item
- **Power Button (Short Press):** Select / Confirm action  
- **Power Button (Long Press):** Context menu / System info
- **Menu Button (Long Press):** Back / Cancel

### Available Functions

1. **SCAN FREQUENCIES:** Discover nearby WiFi networks
2. **PACKET HARVEST:** Capture network traffic to .pcap files
3. **DEAUTH PULSE:** Send deauthentication frames (WiFi testing)
4. **SYSTEM INFO:** View device status and diagnostics
5. **REBOOT:** Restart the device

### Command Line Access

```bash
# Forward the backdoor port
adb forward tcp:9999 tcp:9999

# Connect to root shell
nc 127.0.0.1 9999

# Enter the Alpine chroot
chroot /data/alpine /bin/bash

# Now you have full access to all tools:
tcpdump -i wlan0 -w capture.pcap
nmap -sn 192.168.1.0/24
airmon-ng start wlan0
```

---

## 🔮 Future Possibilities

This project opens up numerous interesting possibilities:

### Software Enhancements
- **Web Dashboard:** Flask-based control panel accessible via browser
- **GPS Integration:** War-walking/driving capabilities with mapping
- **Cellular Analysis:** AT command interface to 5G modem
- **Autonomous Operation:** Script-based "mission profiles"
- **USB Ethernet:** Plug-and-play network bridge mode
- **Stealth Features:** Process hiding, traffic masquerading

### Hardware Modifications
- **External Antenna:** SMA connectors for high-gain antennas
- **Battery Expansion:** Extended runtime for field operations
- **Thermal Management:** Heatsinks for sustained high-load operations
- **GPIO Access:** Utilize exposed test points for additional I/O

### Advanced Applications
- **Cell Tower Analysis:** Research 5G/LTE security
- **IoT Testing:** Scan for vulnerable devices
- **Network Forensics:** Portable packet capture station
- **Red Team Tool:** Covert network assessment device
- **Research Platform:** Embedded Linux experimentation

See [docs/ROADMAP.md](docs/ROADMAP.md) for detailed feature plans.

---

## 📚 Documentation

- **[INSTALL.md](INSTALL.md)** - Detailed installation guide
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Technical deep-dive
- **[docs/EXPLOIT.md](docs/EXPLOIT.md)** - Root methodology explained
- **[docs/HARDWARE.md](docs/HARDWARE.md)** - Device specifications and mods
- **[docs/USAGE.md](docs/USAGE.md)** - Detailed usage examples
- **[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Common issues and fixes
- **[docs/ROADMAP.md](docs/ROADMAP.md)** - Future development plans

---

## ⚖️ Legal & Ethical Considerations

### Responsible Use

This toolkit is designed for:
- **Authorized penetration testing** on your own networks
- **Security research** in controlled environments
- **Educational purposes** to understand embedded Linux security
- **Network administration** of systems you own

### Prohibited Uses

Do NOT use this toolkit for:
- Unauthorized access to networks or devices
- Interfering with cellular or WiFi infrastructure
- Violating your carrier's terms of service
- Any illegal activity in your jurisdiction

### Legal Status

The legality of this toolkit varies by jurisdiction:
- **USA:** May be legal under CFAA for authorized testing; illegal for unauthorized access
- **Europe:** GDPR and computer misuse acts apply
- **Other:** Check your local laws regarding network security tools

**When in doubt, consult a lawyer before using these tools.**

---

## 🤝 Contributing

Contributions are welcome! However, please note:

1. **No Illegal Uses:** Do not submit code for malicious purposes
2. **Responsible Disclosure:** Report security vulnerabilities privately
3. **Documentation:** Well-commented code and updated docs required
4. **Testing:** Verify changes don't brick the device

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 🙏 Acknowledgments

- Qualcomm for making hackable embedded hardware
- The Alpine Linux team for their excellent minimal distribution
- The Aircrack-ng project and wireless security community
- The Flipper Zero team for inspiration

---

## 📄 License

This project is released under the MIT License. See [LICENSE](LICENSE) for details.

**This license applies to the code in this repository only. It does not grant rights to:**
- Modify devices without manufacturer authorization
- Violate terms of service with carriers or vendors
- Use the toolkit for illegal purposes

---

## 🔒 Security

For security concerns or vulnerability reports, please see [SECURITY.md](SECURITY.md).

Do NOT open public issues for security vulnerabilities.

---

## 📞 Contact

- **GitHub Issues:** For bugs, feature requests, and questions
- **Discussions:** For general conversation and community support

---

**Remember: With great power comes great responsibility. Use this toolkit wisely and legally.**

*Last Updated: January 2026*
