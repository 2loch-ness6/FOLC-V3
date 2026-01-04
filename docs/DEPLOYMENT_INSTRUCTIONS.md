# DEPLOYMENT INSTRUCTIONS FOR OPERATOR

**Document Version:** 1.0  
**Date:** January 2026  
**For:** Gemini Agent (Operator)  
**From:** Copilot Agent (Architect)

---

## Mission Brief

You are about to deploy the **Native Root Integration** system to the Orbic Speed (RC400L) device. This transitions the system from a "service hijack" approach to a clean init-style implementation with proper symlink bridge integration.

**Objectives:**
1. Deploy the new `orbital_os_init.sh` script
2. Deploy the `symlink_bridge.sh` script  
3. Replace the current wrapper with the new init script
4. Verify all systems are operational
5. Report results back to Architect

---

## Pre-Deployment Checklist

Before starting, verify:

- [ ] Device is powered on and accessible via ADB
- [ ] Current backdoor on port 9999 is accessible
- [ ] You have reviewed the COORDINATION_DIRECTIVE.md
- [ ] You understand the rollback procedure
- [ ] You have backed up any critical data from the device

---

## Deployment Procedure

### Phase 1: Establish Access

**Step 1.1:** Connect to the device via ADB
```bash
adb devices
# Should show your device connected
```

**Step 1.2:** Forward the backdoor port
```bash
adb forward tcp:9999 tcp:9999
```

**Step 1.3:** Connect to backdoor shell
```bash
nc 127.0.0.1 9999
```

**Step 1.4:** Verify root access
```bash
id
# Should show: uid=0(root) gid=0(root)

grep CapEff /proc/self/status
# Should show: CapEff: 0000003fffffffff (full capabilities)
```

**✓ Report to Architect:**
```
STATUS: Access established
OUTPUT: [paste output from id and CapEff commands]
```

---

### Phase 2: Create Safety Backups

**Step 2.1:** Backup current rayhunter-daemon
```bash
cd /data/rayhunter

# Create timestamped backup
BACKUP_NAME="rayhunter-daemon.backup.$(date +%Y%m%d_%H%M%S)"
cp rayhunter-daemon "$BACKUP_NAME"

# Verify backup
ls -lah rayhunter-daemon*
```

**Step 2.2:** Backup wrapper_v4.sh (if different from rayhunter-daemon)
```bash
if [ -f /data/rayhunter/wrapper_v4.sh ]; then
    cp wrapper_v4.sh "wrapper_v4.sh.backup.$(date +%Y%m%d_%H%M%S)"
fi
```

**Step 2.3:** Verify backups exist
```bash
ls -lah /data/rayhunter/*.backup.*
```

**✓ Report to Architect:**
```
STATUS: Backups created
OUTPUT: [paste ls output showing backup files]
```

---

### Phase 3: Deploy New Scripts

**Step 3.1:** Deploy orbital_os_init.sh

**Method A: Via ADB Push (Recommended)**
```bash
# On your host machine (not in device shell)
adb push exploits/orbital_os_init.sh /data/rayhunter/orbital_os_init.sh
```

**Method B: Via Manual Copy-Paste**
```bash
# On device shell
cat > /data/rayhunter/orbital_os_init.sh << 'SCRIPT_EOF'
[paste entire contents of orbital_os_init.sh here]
SCRIPT_EOF
```

**Step 3.2:** Deploy symlink_bridge.sh

**Method A: Via ADB Push (Recommended)**
```bash
# On your host machine
adb push tools/symlink_bridge.sh /data/rayhunter/symlink_bridge.sh
```

**Method B: Via Manual Copy-Paste**
```bash
# On device shell
cat > /data/rayhunter/symlink_bridge.sh << 'SCRIPT_EOF'
[paste entire contents of symlink_bridge.sh here]
SCRIPT_EOF
```

**Step 3.3:** Set executable permissions
```bash
chmod +x /data/rayhunter/orbital_os_init.sh
chmod +x /data/rayhunter/symlink_bridge.sh
```

**Step 3.4:** Verify deployments
```bash
ls -lah /data/rayhunter/*.sh
```

**✓ Report to Architect:**
```
STATUS: Scripts deployed
OUTPUT: [paste ls output showing new scripts with +x permissions]
```

---

### Phase 4: Test in Isolation

**Step 4.1:** Run orbital_os_init.sh in test mode
```bash
/data/rayhunter/orbital_os_init.sh test
```

**Step 4.2:** Review test output carefully
Look for:
- ✓ All green [+] success indicators
- ⚠ Any red [-] error indicators
- ⚠ Any yellow [!] warning indicators

**Step 4.3:** Test symlink_bridge.sh
```bash
/data/rayhunter/symlink_bridge.sh status
```

**✓ Report to Architect:**
```
STATUS: Test mode completed
OUTPUT: [paste full output from both test commands]
```

**⚠️ STOP HERE if any critical errors were reported. Report to Architect before proceeding.**

---

### Phase 5: Deploy to Production

**Step 5.1:** Run orbital_os_init.sh once manually
```bash
/data/rayhunter/orbital_os_init.sh start
```

**Step 5.2:** Verify systems started correctly
```bash
# Check if backdoor is running
netstat -tlpn | grep 9999

# Check if Alpine filesystems are mounted
mount | grep /data/alpine

# Check overall status
/data/rayhunter/orbital_os_init.sh status
```

**Step 5.3:** Test Alpine chroot access
```bash
# Enter the Alpine environment
chroot /data/alpine /bin/sh

# Verify host binaries are accessible
ls -la /host-bin/

# Test a host binary (e.g., iw)
/host-bin/iw --version

# Exit chroot
exit
```

**✓ Report to Architect:**
```
STATUS: Manual start successful
OUTPUT: [paste outputs from verification commands]
```

**⚠️ STOP HERE if systems didn't start correctly. Do NOT proceed to Step 5.4.**

---

**Step 5.4:** Replace rayhunter-daemon with new init script

**⚠️ CRITICAL STEP - This makes the change permanent**

```bash
cd /data/rayhunter

# Final verification that backup exists
ls -lah rayhunter-daemon.backup.*

# Replace the daemon
cp orbital_os_init.sh rayhunter-daemon

# Verify replacement
ls -lah rayhunter-daemon
cat rayhunter-daemon | head -20
```

**✓ Report to Architect:**
```
STATUS: Production deployment complete
OUTPUT: [paste verification output]
```

---

### Phase 6: Reboot Test

**Step 6.1:** Reboot the device
```bash
# On device shell
reboot
```

**Step 6.2:** Wait for device to reboot (2-3 minutes)

**Step 6.3:** Re-establish access
```bash
# On host machine
adb forward tcp:9999 tcp:9999
nc 127.0.0.1 9999
```

**Step 6.4:** Verify all systems are operational
```bash
# Check status
/data/rayhunter/orbital_os_init.sh status

# Check logs
tail -50 /data/rayhunter/orbital_os.log

# Test Alpine chroot
chroot /data/alpine /bin/sh
echo $PATH
# Should include /host-bin
exit
```

**✓ Report to Architect:**
```
STATUS: Reboot test complete
OUTPUT: [paste verification results]
```

---

### Phase 7: Final Verification

**Step 7.1:** Run comprehensive status checks
```bash
# System status
/data/rayhunter/orbital_os_init.sh status

# Symlink bridge status
/data/rayhunter/symlink_bridge.sh verify

# List all bridged binaries
/data/rayhunter/symlink_bridge.sh list
```

**Step 7.2:** Test FOAC UI (if applicable)
```bash
# Check if FOAC UI is running
ps | grep python

# Check device screen for UI
# [Physical verification - check the device screen]
```

**Step 7.3:** Test network tools from Alpine
```bash
chroot /data/alpine /bin/sh

# Test iw command (via bridge)
/host-bin/iw dev

# Test ip command (via bridge)
/host-bin/ip addr

# Test Alpine native tools
which tcpdump
tcpdump --version

exit
```

**✓ Final Report to Architect:**
```
STATUS: Deployment fully successful
VERIFICATION COMPLETE:
  - Root access: [OK/FAIL]
  - Alpine mounts: [OK/FAIL]
  - Backdoor service: [OK/FAIL]
  - Symlink bridge: [OK/FAIL]
  - FOAC UI: [OK/FAIL/SKIPPED]
  - Network tools: [OK/FAIL]
  - Reboot persistence: [OK/FAIL]

OUTPUT: [paste comprehensive verification results]
```

---

## Rollback Procedure

**If anything goes wrong at any step:**

**Rollback Step 1:** Restore from backup
```bash
cd /data/rayhunter

# Find the most recent backup
ls -lah rayhunter-daemon.backup.*

# Restore it
cp rayhunter-daemon.backup.XXXXXX rayhunter-daemon

# Verify restoration
ls -lah rayhunter-daemon
```

**Rollback Step 2:** Reboot device
```bash
reboot
```

**Rollback Step 3:** Verify old system works
```bash
# After reboot, reconnect
adb forward tcp:9999 tcp:9999
nc 127.0.0.1 9999

# Verify access
id
```

**✓ Report rollback to Architect:**
```
ERROR: Deployment failed at [step name]
ERROR: [describe what happened]
STATUS: Rolled back to previous version successfully
```

---

## Troubleshooting

### Problem: Can't connect to backdoor after reboot

**Possible Causes:**
- Script syntax error
- Missing executable permissions
- Original daemon not found

**Solution:**
```bash
# Connect via ADB shell directly
adb shell

# Check if process is running
ps | grep rayhunter

# Check logs
cat /data/rayhunter/orbital_os.log

# Manual restart
/data/rayhunter/orbital_os_init.sh restart
```

### Problem: Alpine chroot not accessible

**Solution:**
```bash
# Check if mounts exist
mount | grep alpine

# Manually remount if needed
/data/rayhunter/orbital_os_init.sh restart
```

### Problem: Symlink bridge not working

**Solution:**
```bash
# Re-run bridge setup
/data/rayhunter/symlink_bridge.sh cleanup
/data/rayhunter/symlink_bridge.sh setup

# Verify
/data/rayhunter/symlink_bridge.sh verify
```

---

## Command Quick Reference

```bash
# Access device
adb forward tcp:9999 tcp:9999 && nc 127.0.0.1 9999

# Check status
/data/rayhunter/orbital_os_init.sh status

# Restart services
/data/rayhunter/orbital_os_init.sh restart

# Check logs
tail -f /data/rayhunter/orbital_os.log

# Symlink bridge operations
/data/rayhunter/symlink_bridge.sh status
/data/rayhunter/symlink_bridge.sh verify
/data/rayhunter/symlink_bridge.sh list

# Enter Alpine
chroot /data/alpine /bin/sh
```

---

## Success Criteria

Deployment is considered successful when ALL of the following are true:

- [x] Device boots and is accessible
- [x] Backdoor on port 9999 is accessible
- [x] Root shell with full capabilities
- [x] Alpine filesystems properly mounted
- [x] Symlink bridge functional
- [x] Host binaries accessible from Alpine
- [x] FOAC UI operational (if applicable)
- [x] System survives reboot
- [x] No critical errors in logs

---

## Next Steps After Successful Deployment

Once deployment is verified successful:

1. **Document the deployment:**
   - Take screenshots of verification outputs
   - Save logs for reference
   - Note any warnings or issues encountered

2. **Test advanced features:**
   - WiFi scanning from Alpine
   - Packet capture functionality
   - FOAC UI features

3. **Report completion to Architect:**
   - Confirm all systems operational
   - Share any observations or recommendations
   - Request next phase instructions (if any)

---

## Contact Architect

**For any issues or questions during deployment:**

Prefix your communication with appropriate tag:
- `ERROR:` for deployment failures
- `QUESTION:` for clarification needed
- `STATUS:` for progress updates
- `OUTPUT:` for command results

**Always include:**
- What step you were on
- What command you ran
- What the output was
- What you expected vs. what happened

---

**Good luck, Operator! Deploy with confidence.**

**END OF DEPLOYMENT INSTRUCTIONS**
