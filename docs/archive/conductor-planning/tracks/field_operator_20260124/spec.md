# Specification: Field Operator UI & AutoIOT Toolkit

## 1. Overview
This track implements a dual-interface control system (Framebuffer & Web) and an automated reconnaissance suite (AutoIOT) for the Orbic Speed (RC400L). It integrates a modified Gemini CLI and a custom MCP server to enable autonomous, AI-driven field operations.

## 2. Functional Requirements

### 2.1 Framebuffer UI (On-Device)
- **Menu Structure:** Root (Power, Settings, Tools, AutoIOT) -> AutoIOT Sub-Menu (Analysis, Mapping, Metrics, Vectors, Payloads, CC).
- **Navigation:** Button 1 (Cycle), Button 2 (Select) with a software filter/debounce layer to prevent accidental SIGTERM/SIGKILL power-offs.
- **Visuals:** Real-time sparklines for packet rates (60s history) and signal strength.

### 2.2 Web UI (Tethered Control Panel)
- **Deployment:** Flask-based dashboard served to the tethered phone via USB RNDIS.
- **Features:** Target management, scan configuration, and advanced SOS/AI overrides.

### 2.3 AutoIOT Suite (Security Toolkit)
- **Global Scan:** Optimized 2.4/5GHz scanning in monitor mode.
- **Auditing:** ARP MitM, connection killing (deauth), and tool integration (nmap, scapy, recon-ng).

### 2.4 AI Orchestration (Nexus Gemini Port)
- **Modified Gemini CLI:** A custom build of the Gemini CLI patched to pipe inputs/outputs to an automated orchestration script.
- **On-Device MCP Server:** A hosted Model Context Protocol server providing the AI with tools to:
    - Execute shell commands and security tools.
    - Read/Write to the Framebuffer UI state.
    - Modify network configurations (interfaces, iptables).
- **Automated Turn-to-Turn:** A state-machine script that manages the interaction loop between the device environment and the Gemini model.

## 3. Technical Constraints
- **Hardware:** MDM9207 (ARMv7), limited RAM, 2 buttons (Power button kernel interpretation issues).
- **Environment:** Hybrid Host + Alpine Chroot.
- **Connectivity:** Local loopback for MCP/CLI communication; USB RNDIS for Web UI.

## 4. Acceptance Criteria
- [ ] Navigation filter prevents accidental power-offs.
- [ ] Gemini CLI autonomously executes tools via the MCP server.
- [ ] Real-time graphs update on the framebuffer.
- [ ] Web UI displays accurate scan data from the Alpine environment.
