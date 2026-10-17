# Specification: Stabilize SOS AI Orchestration Core

## 1. Goal
The primary objective of this track is to transition the Service Orchestration System (SOS) AI Orchestrator from an experimental state to a production-ready core component. This involves standardizing the API interfaces, improving error handling for hardware interactions, and ensuring robust communication between the host and chroot environments.

## 2. Requirements
- **Standardized API Interface:** Define a clear, consistent API for the `AIOrchestrator` to interact with hardware daemons (e.g., `hw_ctl_daemon.py`).
- **Robust Error Handling:** Implement comprehensive try-except blocks and retry logic for LLM calls and hardware commands to handle resource constraints and connectivity issues.
- **Config Management:** Centralize AI configurations in `ai_config.json` and ensure the orchestrator handles missing or corrupt configurations gracefully.
- **Logging & Telemetry:** Implement structured logging to provide clear visibility into AI decision-making and hardware execution.
- **Testing Foundation:** Achieve >80% test coverage for the core orchestrator logic using mocks for LLM and hardware interfaces.

## 3. Architecture
The SOS operates in a hybrid model:
- **AI Orchestrator (Alpine Chroot):** High-level logic and LLM interfacing.
- **API Gateway Daemon (Host/Chroot):** Bridges communication between the AI layer and local services.
- **Hardware Control Daemon (Host):** Direct interaction with `/dev/fb0`, buttons via `evdev`, and cellular/wifi interfaces.

## 4. Constraints
- **Memory Management:** The MDM9207 is memory-constrained. The orchestrator must be lightweight and manage LLM context windows efficiently.
- **Latency:** Hardware commands must be executed with minimal overhead to maintain tactile responsiveness.
