# Future Roadmap for FOLC-V3

This document outlines potential future developments, features, and research directions for the FOLC-V3 project.

---

## 🎯 Short-Term Goals (1-3 months)

### Software Improvements

#### 1. Enhanced UI System
- **Status:** Planned
- **Priority:** High
- **Description:** 
  - Add configuration menu for WiFi settings
  - Implement status persistence across reboots
  - Add battery level indicator
  - Create visual feedback for long-running operations
  - Add progress bars for scans and captures

#### 2. Web Dashboard
- **Status:** Planned
- **Priority:** High
- **Description:**
  - Flask-based web interface
  - Real-time status monitoring
  - File manager for captured packets
  - Configuration editor
  - Log viewer
- **Access:** `http://<device-ip>:8080`
- **Tech Stack:** Python Flask, HTML/CSS/JavaScript, WebSockets

#### 3. Tool Integration
- **Status:** In Progress
- **Priority:** Medium
- **Tools to Add:**
  - `bettercap` - Advanced MITM framework
  - `mdk4` - Advanced WiFi testing tool
  - `horst` - Lightweight WiFi analyzer
  - `responder` - LLMNR/NBT-NS poisoner
  - `ettercap` - Network sniffer/interceptor

#### 4. Automated Backup/Restore
- **Status:** Planned
- **Priority:** High
- **Description:**
  - One-command device backup
  - Restore to factory settings
  - Save/restore Alpine chroot state
  - Configuration backup to external storage

---

## 🔬 Medium-Term Goals (3-6 months)

### Hardware Enhancements

#### 1. External Antenna Mod
- **Status:** Research Phase
- **Priority:** Medium
- **Description:**
  - Solder SMA connectors to WiFi module test points
  - Support for high-gain antennas
  - Extended range for testing
- **Resources Needed:**
  - Soldering iron and skills
  - SMA pigtails
  - Device disassembly guide

#### 2. USB Ethernet Gadget Mode
- **Status:** Planned
- **Priority:** High
- **Description:**
  - Enable RNDIS USB networking
  - Plug-and-play web interface access
  - No ADB required for basic access
  - Automatic IP assignment (172.16.42.1)
- **Use Case:** Connect device to laptop, browse to 172.16.42.1

#### 3. GPS Integration
- **Status:** Research Phase
- **Priority:** Low
- **Description:**
  - Interface with cellular modem GPS
  - War-driving/walking capabilities
  - Geo-tagged packet captures
  - Network mapping with coordinates
- **Challenges:** 
  - GPS may require carrier activation
  - AT command research needed

### Software Features

#### 4. Automation Framework
- **Status:** Planned
- **Priority:** Medium
- **Description:**
  - Scriptable "mission profiles"
  - Scheduled tasks (cron-like)
  - Event-triggered actions
  - Example: "Scan for networks every 5 minutes, alert if target SSID found"

#### 5. Data Exfiltration
- **Status:** Planned
- **Priority:** Medium
- **Description:**
  - Automated upload of captures to remote server
  - Secure file transfer (SCP/SFTP)
  - Cloud storage integration (optional)
  - Encryption for sensitive data

---

## 🚀 Long-Term Goals (6-12 months)

### Advanced Cellular Research

#### 1. 5G/LTE Modem Analysis
- **Status:** Research Phase
- **Priority:** Medium
- **Description:**
  - AT command documentation for Snapdragon X12
  - Cell tower information extraction
  - Band locking and frequency analysis
  - Signal strength mapping
  - Potentially: IMSI catcher detection (already has rayhunter)

#### 2. Cell Network Testing
- **Status:** Conceptual
- **Priority:** Low
- **Description:**
  - Carrier network vulnerability assessment
  - SS7/Diameter protocol research
  - SIM toolkit interaction
- **⚠️ Legal Warning:** This area has significant legal risks

### Stealth & Evasion

#### 3. Stealth Mode
- **Status:** Planned
- **Priority:** Medium
- **Features:**
  - Process name obfuscation
  - LD_PRELOAD process hiding
  - Traffic masquerading (blend with normal HTTPS)
  - MAC address randomization automation
  - Minimize RF fingerprint

#### 4. Anti-Detection
- **Status:** Conceptual
- **Priority:** Low
- **Description:**
  - Detect if device is being monitored
  - Kill switch for sensitive operations
  - Secure wipe functionality
  - Encrypted storage

### Platform Expansion

#### 5. Support for Other Devices
- **Status:** Community Driven
- **Priority:** Low
- **Potential Targets:**
  - Other Qualcomm MDM-based hotspots
  - Netgear Nighthawk M series
  - Franklin Wireless hotspots
  - Generic ARMv7 routers
- **Requirements:**
  - Similar exploit vector
  - Community device donation/access

#### 6. Cross-Platform Management Tool
- **Status:** Conceptual
- **Priority:** Low
- **Description:**
  - Desktop application for device management
  - Multi-device support
  - GUI for all functions
  - Windows/Mac/Linux compatibility
- **Tech Stack:** Electron or Qt

---

## 🎨 UI/UX Improvements

### Physical Interface

#### 1. Advanced Menu System
- **Status:** Planned
- **Priority:** Medium
- **Features:**
  - Nested menus (multiple levels)
  - Scrollable text for long items
  - Icons for visual clarity
  - Color-coded status indicators
  - Animated transitions

#### 2. Button Customization
- **Status:** Planned
- **Priority:** Low
- **Description:**
  - Configurable button mappings
  - Gesture support (double-tap, hold patterns)
  - Accessibility options

### Web Interface

#### 3. Responsive Dashboard
- **Status:** Planned
- **Priority:** High
- **Features:**
  - Mobile-friendly design
  - Dark mode
  - Real-time graphs (network traffic, signal strength)
  - Drag-and-drop file management
  - Terminal emulator in browser

#### 4. API Endpoint
- **Status:** Planned
- **Priority:** Medium
- **Description:**
  - RESTful API for programmatic control
  - JSON responses
  - Authentication (API keys)
  - Documentation (Swagger/OpenAPI)
- **Use Case:** Automate device control from scripts

---

## 🔐 Security Enhancements

### 1. Secure Boot Chain
- **Status:** Research Phase
- **Priority:** Low
- **Description:**
  - Verify integrity of exploit chain
  - Detect tampering with wrapper scripts
  - Trusted execution environment research

### 2. Encrypted Storage
- **Status:** Planned
- **Priority:** Medium
- **Description:**
  - LUKS encryption for `/data/alpine`
  - Passphrase or key-based unlock
  - Automatic encryption for captures

### 3. Authentication System
- **Status:** Planned
- **Priority:** High
- **Description:**
  - Password protection for backdoor
  - Web UI authentication
  - SSH key management
  - Session timeout

---

## 🧪 Research Areas

### 1. Firmware Analysis
- **Goal:** Understand vendor firmware structure
- **Method:** 
  - Extract firmware from device
  - Reverse engineer binaries
  - Document services and daemons
  - Find additional vulnerabilities

### 2. Hardware Capabilities
- **Goal:** Document all device capabilities
- **Areas:**
  - GPIO pins and test points
  - UART serial access
  - JTAG debugging
  - Undocumented sensors

### 3. RF Research
- **Goal:** Maximize wireless capabilities
- **Areas:**
  - WiFi monitor mode optimization
  - Packet injection reliability
  - Frequency hopping attacks
  - Bluetooth integration (if supported)

---

## 🌍 Community Ideas

These are ideas from the community that need evaluation:

### 1. Mesh Networking
- **Concept:** Multiple FOLC devices form a mesh
- **Use Case:** Distributed packet capture
- **Status:** Conceptual

### 2. Machine Learning Integration
- **Concept:** ML-based network anomaly detection
- **Challenges:** Limited compute power on device
- **Possible Solution:** Cloud-based analysis

### 3. IoT Exploitation Toolkit
- **Concept:** Tools for testing IoT devices
- **Includes:** Zigbee, Z-Wave, BLE analysis
- **Challenges:** Hardware limitations

### 4. Social Engineering Toolkit
- **Concept:** Captive portal for credential harvesting
- **⚠️ Ethical Concern:** High risk of misuse
- **Status:** Under debate

---

## 📊 Performance Goals

### Target Metrics

- **Boot Time:** < 30 seconds to operational UI
- **Scan Time:** < 10 seconds for WiFi scan
- **Battery Life:** 6+ hours of active scanning
- **Capture Speed:** 100+ Mbps packet capture
- **UI Responsiveness:** < 100ms button response

### Optimization Areas

1. **Alpine Chroot Size:** Minimize to < 500MB
2. **Memory Usage:** Keep under 256MB RAM
3. **CPU Efficiency:** Reduce idle CPU to < 10%
4. **Storage:** Efficient log rotation

---

## 🎓 Educational Goals

### Documentation Projects

1. **Video Tutorials:** YouTube series on setup and usage
2. **CTF Challenges:** Create challenges using the device
3. **University Integration:** Partner with security courses
4. **Conference Talks:** Present at DEF CON, Black Hat, etc.

### Training Materials

1. **WiFi Security Course:** Using FOLC as teaching tool
2. **Embedded Linux Handbook:** Device as case study
3. **Red Teaming Guide:** Practical penetration testing

---

## 🤝 Collaboration Opportunities

### Open Source Projects

- **Kismet:** Integration for passive network mapping
- **Aircrack-ng:** Contribute device-specific optimizations
- **Alpine Linux:** ARMv7 package improvements

### Industry Partnerships

- **Security Training:** Offensive Security, SANS
- **Bug Bounty Platforms:** HackerOne, Bugcrowd
- **Hardware Vendors:** Hak5, Great Scott Gadgets

---

## ⚠️ Ethical Considerations

As we develop new features, we must consider:

1. **Dual-Use Dilemma:** Every feature can be misused
2. **Harm Reduction:** How can we prevent malicious use?
3. **Legal Compliance:** What jurisdictions restrict these tools?
4. **Responsible Disclosure:** How to share research safely?

### Our Principles

- ✅ Prioritize features with legitimate security testing uses
- ✅ Require explicit authorization flags for destructive actions
- ✅ Provide clear documentation on legal/ethical use
- ✅ Build in safeguards where possible
- ❌ Don't build features solely for malicious purposes
- ❌ Don't market as "undetectable" or for unauthorized use

---

## 📅 Timeline Summary

### Q1 2026
- [x] Repository organization
- [ ] Web dashboard alpha
- [ ] USB ethernet mode
- [ ] Comprehensive documentation

### Q2 2026
- [ ] Tool integration (bettercap, mdk4)
- [ ] External antenna mod guide
- [ ] Automation framework
- [ ] API endpoint

### Q3 2026
- [ ] GPS integration
- [ ] Cellular modem research
- [ ] Stealth features
- [ ] Cross-platform manager

### Q4 2026
- [ ] Advanced cellular testing
- [ ] Multi-device support
- [ ] ML integration research
- [ ] Community expansion

---

## 🎯 How to Contribute

See [CONTRIBUTING.md](../CONTRIBUTING.md) for details on how to help with any of these initiatives.

Priority areas needing contributors:
1. **Web UI Development:** Frontend developers
2. **Hardware Mods:** Electronics expertise
3. **Documentation:** Technical writers
4. **Testing:** Device owners for beta testing
5. **Security Research:** Cellular/RF expertise

---

**This roadmap is a living document and will be updated as the project evolves.**

*Last Updated: January 2026*
