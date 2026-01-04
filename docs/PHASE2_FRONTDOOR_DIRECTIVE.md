# PHASE 2 DIRECTIVE: FRONT DOOR STANDARDIZATION

**Document Version:** 2.0
**Date:** January 2026
**Status:** ACTIVE
**Reference:** Supersedes Phase 1 Backdoor Usage

---

## 1. System Status Change

**PREVIOUS STATE (Phase 1):**
- Root access via **Backdoor** (Netcat on Port 9999).
- Scripts relied on `nc 127.0.0.1 9999` to execute commands.
- `adb shell` was restricted (UID 2000).

**CURRENT STATE (Phase 2):**
- Root access via **Front Door** (`adb shell su`).
- `/bin/su` has been replaced with a SUID-root `busybox` binary.
- Root password has been removed from `/etc/passwd`.
- `adb shell su -c "id"` returns `uid=0(root)`.

---

## 2. Mission Objective

**Deprecate the Backdoor:**
While the Port 9999 backdoor remains active as a failsafe/init service, it should **NO LONGER** be the primary method for interaction. All tools and scripts must be updated to use the standard Android/Linux `adb shell su` paradigm.

**Architect (Copilot) Responsibilities:**
1.  **Audit** all existing scripts (`tools/*.sh`, `*.py`) for `nc ... 9999` usage.
2.  **Refactor** these scripts to use `adb shell su -c "..."`.
3.  **Update** documentation to reflect the standard `su` usage.
4.  **Verify** that `su` context provides all necessary capabilities (it does, full caps).

---

## 3. Technical Implementation Details

**Command Translation Guide:**

| Old Method (Backdoor) | New Method (Front Door) |
|-----------------------|-------------------------|
| `echo "cmd" \| nc localhost 9999` | `adb shell "su -c 'cmd'"` |
| `adb forward tcp:9999 ...` | *Not Required* |
| `nc -w 5 ...` | `adb shell ...` (handles timeout natively) |

**New `su` Binary:**
- Location: `/bin/su`
- Type: Busybox (Static)
- Permissions: `4755` (rwsr-xr-x)
- Owner: `0:0` (root:root)

---

## 4. Immediate Tasks for Architect

1.  **Modify** `tools/deploy_foac.sh` to use `adb shell su`.
2.  **Modify** `tools/orbic_manager.py` (if exists) to use `adb shell su`.
3.  **Create** a helper function/library for "Execute as Root" that abstracts this.

**ACKNOWLEDGE:**
Confirm understanding of the new "Front Door" paradigm and begin refactoring.
