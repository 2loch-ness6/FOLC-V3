# Implementation Plan: Field Operator UI & AutoIOT Toolkit

## Phase 1: On-Device MCP Server & Infrastructure [checkpoint: 05f212c]
- [x] Task: Initialize MCP Server for Orbic Control 263d924
    - [x] Create `src/sos/ai/mcp_server.py`
    - [x] Write unit tests for tool execution (shell, network tools)
    - [x] Implement core tool definitions: `execute_command`, `read_ui_state`, `write_ui_state`
- [x] Task: Implement Centralized State Manager 40d02c5
    - [x] Write tests for state persistence (JSON-based state for UI and Scan results)
    - [x] Implement `src/core/state_manager.py` to bridge MCP, UI, and AutoIOT
- [ ] Task: Conductor - User Manual Verification 'On-Device MCP Server & Infrastructure' (Protocol in workflow.md)

## Phase 2: Framebuffer UI & Navigation Filter
- [ ] Task: Develop Debounced Navigation Layer
    - [ ] Write unit tests for the cycle/select logic with simulated double-clicks/power signals
    - [ ] Refactor `src/ui/input_manager.py` to handle the sensitive power button
- [ ] Task: Implement Framebuffer Menu System
    - [ ] Write tests for menu transitions (Root -> AutoIOT)
    - [ ] Implement Root and Sub-menu drawing logic in `src/ui/folc_ui.py`
- [ ] Task: Real-time Graphics Engine
    - [ ] Write tests for sparkline generation and data buffering
    - [ ] Implement packet rate and signal strength graphs (60s history)
- [ ] Task: Conductor - User Manual Verification 'Framebuffer UI & Navigation Filter' (Protocol in workflow.md)

## Phase 3: AutoIOT & Global Scan Engine
- [ ] Task: Implement Monitor Mode Scanner
    - [ ] Write tests for `iw` scan output parsing (SSID, BSSID, Signal, Channel)
    - [ ] Implement 2.4/5GHz Global Scan in `src/core/scanner.py`
- [ ] Task: Auditing & Connection Killing Tools
    - [ ] Write tests for ARP MitM/IPTables configuration logic
    - [ ] Implement deauth/connection killing scripts in `src/core/auditor.py`
- [ ] Task: Conductor - User Manual Verification 'AutoIOT & Global Scan Engine' (Protocol in workflow.md)

## Phase 4: AI Orchestration (Nexus Gemini Port)
- [ ] Task: Patch Gemini CLI for Automation
    - [ ] Clone and modify Gemini CLI to pipe I/O to the SOS orchestrator
    - [ ] Create `src/sos/ai/nexus_orchestrator.py`
- [ ] Task: Implement Turn-to-Turn Orchestration Loop
    - [ ] Write tests for state-machine transitions (Idle -> Scanning -> Analyzing -> Exploiting)
    - [ ] Integrate orchestration script with MCP server and state manager
- [ ] Task: Conductor - User Manual Verification 'AI Orchestration (Nexus Gemini Port)' (Protocol in workflow.md)

## Phase 5: Web UI & Integration
- [ ] Task: Flask Dashboard Development
    - [ ] Create Web UI templates (Recon Dashboard, SOS Config)
    - [ ] Implement API endpoints for real-time scan data
- [ ] Task: Final System Integration
    - [ ] Wire Web UI to State Manager
    - [ ] Verify full loop: Scan -> AI Analysis -> UI Display -> Web Dashboard
- [ ] Task: Conductor - User Manual Verification 'Web UI & Integration' (Protocol in workflow.md)
