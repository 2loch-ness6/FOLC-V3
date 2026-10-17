# Initial Concept
FOLC-V3 is an Orbic Speed RC400L exploitation and security toolkit that transforms the device into a portable Linux security appliance.


# Product Definition: FOLC-V3

## Overview
FOLC-V3 transforms the Orbic Speed 5G Hotspot (Model RC400L) into a portable, embedded Linux security appliance. It bridges the gap between commodity cellular hardware and specialized security tools, providing a versatile platform for network auditing and research.

## Target Users
- **Security Researchers & Pentesters:** Professionals requiring an inconspicuous, battery-powered device for on-site network reconnaissance and auditing.

## Goals
- **On-Device Interaction:** Implement a physical, button-driven UI on the device's built-in screen for efficient, standalone operation.
- **High-Capability Environment:** Maintain a persistent, unrestricted root environment with a full Alpine Linux chroot for standard security tooling.
- **Advanced Network Auditing:** Enable comprehensive WiFi scanning, network mapping, and monitoring capabilities.

## Critical Features
- **SOS (Service Orchestration System):** An AI-powered orchestration layer using LLMs (Gemini/Claude) for automated hardware control and complex task execution.
- **Framebuffer UI:** A dedicated physical interface utilizing the device's framebuffer and hardware buttons for real-time status and control.
- **Integrated Security Toolkit:** Native integration and optimized execution of tools like `nmap`, `scapy`, and `aircrack-ng` within the hybrid environment.

## Constraints & Challenges
- **Hardware Limitations:** Operating within the tight memory and CPU bounds of the Qualcomm MDM9207 chipset.
- **Legacy Software Stack:** Navigating the restrictions of the vendor's 3.18 kernel and proprietary modules.
- **Wireless Driver Constraints:** Managing the lack of monitor mode and packet injection on the current hardware revision.
