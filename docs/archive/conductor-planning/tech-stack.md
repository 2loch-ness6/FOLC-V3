# Technology Stack: FOLC-V3

## Core Platform
- **Hardware:** Orbic Speed 5G (RC400L) / Qualcomm MDM9207 (ARMv7)
- **Host OS:** Qualcomm Embedded Linux (Kernel 3.18.48)
- **Chroot Environment:** Alpine Linux 3.17 (ARMv7)

## Programming Languages
- **Python 3:** Primary language for core logic, UI (framebuffer), and the Service Orchestration System (SOS).
- **C:** Used for native exploits, privilege escalation helpers (e.g., `ksu`, `nosetuid`), and performance-critical tasks.
- **Shell (Bash/Ash):** Used for deployment scripts, persistence wrappers (`wrapper_v4.sh`), and system-level automation.

## Key Libraries & Frameworks
- **Input & Graphics:** `evdev` (hardware button handling), `Pillow` (framebuffer drawing).
- **AI Orchestration (SOS):** `google-generativeai`, `anthropic` (LLM integration).
- **Web (Optional/Internal):** `Flask` (for potential remote dashboards).

## Security & Networking Toolkit (Alpine Chroot)
- **Analysis:** `tcpdump`, `nmap`, `scapy`, `wireshark-common`.
- **Wireless Auditing:** `aircrack-ng`, `iw`, `wireless-tools`.
- **Utilities:** `tmux`, `htop`, `paramiko` (SSH).

## Persistence & Integration
- **Exploit Method:** Service hijacking via `rayhunter-daemon` replacement.
- **Root Strategy:** LD_PRELOAD (`nosetuid.so`) for ADB and native suid binary exploitation.
- **Communication:** Shell-based command injection and log streaming (session-bridge).
