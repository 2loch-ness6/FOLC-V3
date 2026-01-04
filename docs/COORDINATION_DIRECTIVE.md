# COORDINATION DIRECTIVE: Native Root Integration

**Document Version:** 1.0  
**Date:** January 2026  
**Status:** ACTIVE

---

## 1. Role Definitions

### ARCHITECT (Copilot Agent)
**Responsibilities:**
- Design system architecture and scripts
- Provide implementation specifications
- Review and validate designs before deployment
- Document technical decisions
- **CANNOT:** Execute code on the device directly

### OPERATOR (Gemini Agent / Human)
**Responsibilities:**
- Deploy scripts to the device via ADB
- Execute commands on the device
- Verify deployment success
- Report system status back to Architect
- **CANNOT:** Modify Architect's designs without consultation

---

## 2. Rules of Engagement

### Communication Protocol
1. **Commands from Architect to Operator:**
   - Prefix: `DEPLOY:` for file deployments
   - Prefix: `EXECUTE:` for commands to run
   - Prefix: `VERIFY:` for validation checks
   - Example: `DEPLOY: /path/to/script.sh to device:/data/rayhunter/script.sh`

2. **Reports from Operator to Architect:**
   - Prefix: `STATUS:` for general status updates
   - Prefix: `OUTPUT:` for command outputs
   - Prefix: `ERROR:` for failures
   - Example: `OUTPUT: Script executed successfully, backdoor active on port 9999`

### Safety Protocols
1. **Always backup before modifications:**
   - `cp /data/rayhunter/rayhunter-daemon /data/rayhunter/rayhunter-daemon.backup.$(date +%s)`
   
2. **Test in isolation first:**
   - Deploy to `/tmp` for initial testing
   - Verify syntax and permissions
   - Only move to production paths after validation

3. **Maintain rollback capability:**
   - Keep original binaries
   - Document all changes
   - Provide revert procedures

4. **Never break vendor functionality:**
   - Original `rayhunter-daemon` must remain executable
   - System stability is paramount
   - If vendor services fail, root access fails

---

## 3. Technical Requirements

### A. "Unanimous Root" System

**Objective:** Transition from service hijack to proper init integration.

**Current State (Hijack Method):**
```
System Init → rayhunter-daemon service
              ↓
              wrapper_v4.sh (impersonates daemon)
              ↓
              Spawns backdoor + UI
              ↓
              Executes real daemon (rayhunter-daemon.bak)
```

**Target State (Native Init):**
```
System Init → /etc/init.d/orbital_os (new service)
              ↓
              Mounts Alpine chroot
              ↓
              Starts backdoor service
              ↓
              Launches FOAC UI
              ↓
              System remains stable
```

**Requirements:**
1. **Init Script Location:** `/etc/init.d/orbital_os`
2. **Service Functions:** `start`, `stop`, `restart`, `status`
3. **Privilege Level:** Must run as root (UID 0) with full capabilities
4. **Persistence:** Must survive reboots
5. **Non-Intrusive:** Should not interfere with vendor services

**Integration Method:**
Since `/etc/init.d/` is on a read-only filesystem, we have two options:

**Option A: Maintain Service Hijack (Recommended)**
- Keep using `/data/rayhunter/rayhunter-daemon` as entry point
- Improve wrapper script to follow init.d standards
- Clean separation of concerns within wrapper

**Option B: Init.rc Modification (Advanced)**
- Modify `/system/etc/init.rc` to add new service
- Requires remounting `/system` as read-write
- Higher risk of bricking device
- Not recommended for Phase 1

**Chosen Approach for Phase 1:** Option A - Enhanced Service Hijack

---

### B. "Symlink Bridge" System

**Objective:** Create seamless integration between Host and Alpine environments.

**Problem:**
- Alpine chroot has its own `/bin`, `/sbin`, `/usr/bin`
- Host system has unique binaries not in Alpine (e.g., Qualcomm-specific tools)
- Some operations require Host binaries, some require Alpine binaries
- Need bidirectional access without breaking either environment

**Solution: Symlink Bridge Script**

**Script Location:** `/data/rayhunter/symlink_bridge.sh`

**Functionality:**
1. **Host → Alpine Mapping:**
   - Map essential Host binaries into Alpine environment
   - Create `/data/alpine/host-bin/` directory
   - Symlink Host tools into this directory
   - Add to Alpine PATH

2. **Alpine → Host Awareness:**
   - Document which Alpine tools are available to Host
   - Create wrapper scripts if needed
   - Maintain clear separation

3. **Categories of Binaries to Bridge:**

   **Network Tools (High Priority):**
   - `iw` - WiFi interface configuration
   - `ip` - Network interface management
   - `ifconfig` - Interface configuration (legacy)
   - `route` - Routing table management
   
   **System Utilities (Medium Priority):**
   - `mount` / `umount` - Filesystem operations
   - `modprobe` - Kernel module loading
   - `dmesg` - Kernel messages
   - `lsusb` - USB device listing
   
   **Qualcomm-Specific (Device-Specific):**
   - Any vendor binaries needed for hardware access
   - AT command tools for modem
   - Hardware diagnostic tools

**Implementation Requirements:**
1. **Idempotent:** Can be run multiple times safely
2. **Non-Destructive:** Never overwrites existing binaries
3. **Reversible:** Provides cleanup function
4. **Documented:** Each symlink should have a comment explaining why it's needed

**Example Structure:**
```
/data/alpine/
├── host-bin/           # Symlinks to Host binaries
│   ├── iw -> /usr/sbin/iw
│   ├── ip -> /sbin/ip
│   └── ifconfig -> /sbin/ifconfig
├── host-lib/           # Symlinks to Host libraries (if needed)
└── .bridge_manifest    # Record of all created symlinks
```

---

## 4. Implementation Phases

### Phase 1: Enhanced Init Script (Current)
**Status:** In Progress  
**Deliverables:**
1. `docs/COORDINATION_DIRECTIVE.md` (this document)
2. `/exploits/orbital_os_init.sh` (new clean init script)
3. `/tools/symlink_bridge.sh` (symlink bridge implementation)
4. Deployment instructions for Operator

**Success Criteria:**
- [ ] Init script follows standard init.d patterns
- [ ] All mounts handled cleanly with error checking
- [ ] Backdoor service starts reliably
- [ ] FOAC UI optional and non-blocking
- [ ] Symlink bridge creates needed connections
- [ ] System remains stable after deployment
- [ ] Rollback procedure documented and tested

### Phase 2: Advanced Integration (Future)
**Status:** Planned  
**Deliverables:**
1. Web-based control panel
2. USB Ethernet gadget mode
3. Advanced automation framework

---

## 5. Deployment Workflow

### Step-by-Step Process

**Step 1: Architect Prepares Files**
```
- Creates orbital_os_init.sh
- Creates symlink_bridge.sh
- Tests syntax locally
- Commits to repository
```

**Step 2: Operator Receives Instructions**
```
DEPLOY: exploits/orbital_os_init.sh to /data/rayhunter/orbital_os_init.sh
DEPLOY: tools/symlink_bridge.sh to /data/rayhunter/symlink_bridge.sh
```

**Step 3: Operator Deploys to Device**
```bash
# Connect to device
adb forward tcp:9999 tcp:9999
nc 127.0.0.1 9999

# Create backup
cp /data/rayhunter/rayhunter-daemon /data/rayhunter/rayhunter-daemon.backup.$(date +%s)

# Deploy new scripts (via adb push or manual paste)
# Set permissions
chmod +x /data/rayhunter/orbital_os_init.sh
chmod +x /data/rayhunter/symlink_bridge.sh

# Test in isolation
/data/rayhunter/orbital_os_init.sh test

# If successful, deploy to production
cp /data/rayhunter/orbital_os_init.sh /data/rayhunter/rayhunter-daemon
```

**Step 4: Operator Verifies**
```bash
VERIFY: Check backdoor accessibility
VERIFY: Test FOAC UI functionality
VERIFY: Verify Alpine chroot mounts
VERIFY: Test symlink bridge functionality
```

**Step 5: Operator Reports Back**
```
STATUS: Deployment successful
OUTPUT: [paste relevant outputs]
OR
ERROR: [describe what failed]
```

---

## 6. Verification Checklist

After deployment, Operator must verify:

### System Health
- [ ] Device boots successfully
- [ ] Vendor services still functional
- [ ] No kernel panics or crashes
- [ ] Logs show no critical errors

### Root Access
- [ ] Backdoor on port 9999 is accessible
- [ ] Shell has UID 0 (root)
- [ ] Capabilities are `0000003fffffffff` (full)

### Alpine Environment
- [ ] `/data/alpine/proc` is mounted (type: proc)
- [ ] `/data/alpine/sys` is mounted (type: sysfs)
- [ ] `/data/alpine/dev` is mounted (type: bind)
- [ ] Can chroot into `/data/alpine` successfully
- [ ] Alpine package manager (`apk`) works

### Symlink Bridge
- [ ] Host binaries accessible from Alpine
- [ ] Network tools (`iw`, `ip`) functional
- [ ] No broken symlinks
- [ ] PATH includes `/host-bin`

### FOAC UI (Optional)
- [ ] UI launches without errors
- [ ] Display shows correct information
- [ ] Buttons are responsive
- [ ] UI doesn't interfere with other services

---

## 7. Rollback Procedures

### If Deployment Fails

**Immediate Recovery:**
```bash
# Via ADB if still accessible
adb shell
su
cp /data/rayhunter/rayhunter-daemon.bak /data/rayhunter/rayhunter-daemon
reboot
```

**If ADB is Unavailable:**
- Device must be physically accessed
- May require factory reset
- Data loss possible
- **Prevention is critical**

### Best Practices
1. **Always test in `/tmp` first**
2. **Keep multiple backups**
3. **Document every change**
4. **Have emergency access plan**

---

## 8. Security Considerations

### Threat Model

**Threats Mitigated:**
- Unauthorized physical access (device is locked when not in use)
- Network attacks (backdoor only on localhost)
- Accidental exposure (requires ADB forwarding)

**Threats Accepted:**
- Physical access by owner (intended use case)
- ADB access if USB is connected (necessary for management)
- Process visibility (stealth not priority in Phase 1)

### Security Improvements Over Current System
1. **Better error handling:** No silent failures
2. **Cleaner logging:** Audit trail of actions
3. **Proper cleanup:** Resources released on failure
4. **Service isolation:** UI failure doesn't break backdoor

---

## 9. Future Enhancements

### Phase 2 Considerations
- **Authentication:** Add password to backdoor
- **Encryption:** Encrypt Alpine chroot partition
- **Stealth:** Process hiding and traffic masquerading
- **Redundancy:** Multiple access methods
- **Monitoring:** Health checks and alerting

---

## 10. Glossary

| Term | Definition |
|------|------------|
| **Alpine Chroot** | Separate Linux environment at `/data/alpine` |
| **Backdoor** | Netcat listener on port 9999 for shell access |
| **FOAC** | "Flipper-Orbic Attack Console" - the custom UI |
| **Host** | The main Qualcomm Embedded Linux OS |
| **Init Script** | Service management script (start/stop/restart) |
| **Service Hijack** | Replacing vendor binary with wrapper script |
| **Symlink Bridge** | Linking binaries between Host and Alpine |
| **Unanimous Root** | Full root privileges across all environments |
| **Wrapper** | Script that impersonates the original daemon |

---

## 11. Contact & Escalation

**For Technical Questions:**
- Review this directive
- Check existing documentation in `/docs`
- Consult repository README.md

**For Deployment Issues:**
- Document error messages
- Capture system state (`dmesg`, `logcat`)
- Report to Architect with full context

**For Emergencies:**
- Follow rollback procedures immediately
- Preserve logs if possible
- Report incident after recovery

---

**Document Control:**
- **Author:** Copilot (Architect Agent)
- **Approved By:** [Awaiting Operator Acknowledgment]
- **Next Review:** After Phase 1 Deployment
- **Revision History:**
  - v1.0 (2026-01-04): Initial directive created

---

## ACKNOWLEDGMENT

**Operator must acknowledge understanding before proceeding:**

I, [OPERATOR NAME], acknowledge that I have read and understood this directive. I understand:
1. My role as Operator
2. The communication protocols
3. The safety procedures
4. The rollback procedures
5. The verification requirements

I agree to follow these procedures during deployment.

**Signature:** ___________________  
**Date:** ___________________

---

**END OF DIRECTIVE**
