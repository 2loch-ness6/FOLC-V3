# Frontdoor Root Access Implementation

This document describes the FOLC-V3 "frontdoor" root access implementation using persistent, firmware-backed binaries.

---

## Overview

FOLC-V3 now implements multiple methods for achieving and maintaining persistent root access:

1. **Frontdoor (Primary)** - SUID `ksu` binary providing `su` functionality
2. **ADB Root Persistence** - `nosetuid.so` library preventing privilege drops in ADB
3. **Backdoor (Fallback)** - Netcat listener on port 9999

The frontdoor methods are considered more stable and reliable than the backdoor, as they integrate with the system's native security mechanisms.

---

## Architecture

### 1. KSU Binary (Kernel SU)

**File:** `ksu.c`  
**Built Binary:** `build/ksu`  
**Installation Path:** `/bin/ksu` (symlinked as `/bin/su`)

#### Purpose
A minimal SUID root binary that provides standard `su` functionality without requiring complex kernel modifications.

#### Implementation
```c
int main(int argc, char *argv[]) {
    if (setgid(0) != 0) { perror("setgid"); return 1; }
    if (setuid(0) != 0) { perror("setuid"); return 1; }
    if (argc > 1) {
        execvp(argv[1], &argv[1]);
    } else {
        char *args[] = {"/bin/sh", NULL};
        execv("/bin/sh", args);
    }
    perror("exec");
    return 1;
}
```

#### Usage
```bash
# Spawn root shell
ksu

# Execute command as root
ksu -c "command"

# Via ADB
adb shell su -c "id"
# Output: uid=0(root) gid=0(root)
```

#### Advantages
- ✅ Native system integration
- ✅ Standard `su` semantics
- ✅ Survives ADB disconnections
- ✅ Works with all root-aware apps
- ✅ Persistent across reboots (if properly installed)

### 2. NoSetUID Library

**File:** `nosetuid.c` / `nosetuid_min.c`  
**Built Binary:** `build/nosetuid.so`  
**Installation Path:** `/data/local/nosetuid.so`

#### Purpose
An LD_PRELOAD library that intercepts and neutralizes privilege-dropping system calls, forcing ADB daemon to maintain root privileges.

#### Implementation
Intercepts the following syscalls:
- `setuid()` / `setgid()`
- `setresuid()` / `setresgid()`
- `setgroups()`
- `capset()` (capability modification)

All intercepted calls return success (0) without actually changing privileges.

#### Usage
```bash
# Install library
adb push build/nosetuid.so /data/local/nosetuid.so

# Configure ADB to preload it
adb shell "su -c 'setprop wrap.adbd \"LD_PRELOAD=/data/local/nosetuid.so\"'"

# Restart ADB daemon
adb shell "su -c 'stop adbd && start adbd'"

# Test - all ADB shells are now root
adb shell id
# Output: uid=0(root) gid=0(root)
```

#### Advantages
- ✅ Transparent root access via ADB
- ✅ No need to type `su` for every command
- ✅ Compatible with deployment scripts
- ✅ Easy to enable/disable

#### Disadvantages
- ⚠️ Only affects ADB connections
- ⚠️ Requires configuration after reboot
- ⚠️ Less secure than explicit `su` usage

### 3. Backdoor (Legacy/Fallback)

**Implementation:** Netcat listener on localhost:9999  
**Status:** Optional, kept for backwards compatibility

```bash
# Access backdoor
adb forward tcp:9999 tcp:9999
nc 127.0.0.1 9999
```

---

## Installation

### Prerequisites

1. Device with existing root access (via `/bin/rootshell` or other method)
2. ADB connected
3. Android NDK or ARM cross-compiler (for building)

### Building Binaries

```bash
# Set up NDK (if using)
export NDK_ROOT=/path/to/android-ndk

# Build all components
make

# Or build individually
make ksu
make nosetuid
```

See [BUILD.md](BUILD.md) for detailed build instructions.

### Installing KSU

```bash
# Method 1: Via deployment script (recommended)
./tools/deploy_folc.sh

# Method 2: Manual installation
adb push build/ksu /data/local/tmp/ksu
adb shell
su  # use existing root method
cp /data/local/tmp/ksu /bin/ksu
chmod 4755 /bin/ksu
chown 0:0 /bin/ksu
ln -sf /bin/ksu /bin/su
exit

# Test
adb shell su -c id
# Should output: uid=0(root) gid=0(root)
```

### Installing NoSetUID Library (Optional)

```bash
# Push library
adb push build/nosetuid.so /data/local/tmp/nosetuid.so

# Install and configure
adb shell "su -c 'cp /data/local/tmp/nosetuid.so /data/local/nosetuid.so'"
adb shell "su -c 'chmod 644 /data/local/nosetuid.so'"
adb shell "su -c 'setprop wrap.adbd \"LD_PRELOAD=/data/local/nosetuid.so\"'"

# Restart ADB
adb shell "su -c 'stop adbd && start adbd'"

# Verify
adb shell id
# Should output: uid=0(root) ...
```

---

## Persistence Integration

### Automatic Installation via Init Script

Add to `/data/rayhunter/orbital_os_init.sh`:

```bash
# Install ksu if not present
if [ ! -f /bin/ksu ]; then
    if [ -f /data/local/tmp/ksu ]; then
        echo "Installing ksu binary..." >> "$LOG"
        cp /data/local/tmp/ksu /bin/ksu
        chmod 4755 /bin/ksu
        chown 0:0 /bin/ksu
        ln -sf /bin/ksu /bin/su
        echo "ksu installed successfully" >> "$LOG"
    fi
fi

# Optional: Configure ADB root persistence
if [ -f /data/local/nosetuid.so ]; then
    CURRENT_WRAP=$(getprop wrap.adbd)
    if [ "$CURRENT_WRAP" != "LD_PRELOAD=/data/local/nosetuid.so" ]; then
        echo "Configuring ADB root persistence..." >> "$LOG"
        setprop wrap.adbd "LD_PRELOAD=/data/local/nosetuid.so"
        stop adbd
        start adbd
        echo "ADB root persistence enabled" >> "$LOG"
    fi
fi
```

### Persistence Across Reboots

The frontdoor implementation persists across reboots if:

1. ✅ `ksu` is installed in `/bin/` (system partition must be writable)
2. ✅ Init script runs on boot (via rayhunter daemon hijack)
3. ✅ Binary has correct permissions (4755, owned by root)

For `nosetuid.so`:
- ⚠️ Requires re-configuration after reboot (via init script)
- Library file persists, but `wrap.adbd` property needs to be set again

---

## Usage Examples

### Basic Root Shell
```bash
# Spawn interactive root shell
adb shell su

# Or via ksu directly
adb shell /bin/ksu
```

### Running Commands as Root
```bash
# Single command
adb shell "su -c 'mount -o remount,rw /system'"

# Multiple commands
adb shell "su -c 'cd /data && ls -la'"

# With environment variables
adb shell "su -c 'export PATH=/data/alpine/bin:$PATH && which python3'"
```

### Entering Alpine Chroot
```bash
# Via su
adb shell "su -c 'chroot /data/alpine /bin/sh'"

# Via ksu directly
adb shell "/bin/ksu -c 'chroot /data/alpine /bin/bash'"
```

### Deployment Scripts
```bash
# From deployment scripts
adb shell "su -c 'mount -t proc proc /data/alpine/proc'"
adb shell "su -c 'chroot /data/alpine apk update'"
```

---

## Comparison: Frontdoor vs Backdoor

| Feature | Frontdoor (ksu) | Backdoor (netcat) |
|---------|-----------------|-------------------|
| **Stability** | ✅ High | ⚠️ Medium |
| **Persistence** | ✅ Across reboots | ⚠️ Until daemon restart |
| **Performance** | ✅ Native speed | ⚠️ Network overhead |
| **Compatibility** | ✅ Standard tools | ❌ Custom scripts only |
| **Security** | ✅ Standard permissions | ⚠️ Open network port |
| **Ease of Use** | ✅ `adb shell su` | ⚠️ Port forwarding required |
| **Integration** | ✅ Works with all apps | ❌ Limited to manual use |

**Recommendation:** Use frontdoor (`ksu`) as primary method, keep backdoor as fallback.

---

## Security Considerations

### SUID Binary Risks

The `ksu` binary grants unrestricted root access to any process that can execute it:

**Mitigations:**
1. File permissions: `4755` (no world-write)
2. Ownership: `0:0` (root:root only)
3. Location: `/bin/` (system partition, not user-writable)
4. Binary integrity: Use checksums to verify authenticity

**Threat Model:**
- ✅ Protects against: Accidental modification, user errors
- ⚠️ Does NOT protect against: Malicious apps with shell access, determined attackers with ADB access
- ℹ️ Note: If an attacker has ADB access, they already have significant system access

### LD_PRELOAD Implications

Using `nosetuid.so` with ADB daemon:

**Advantages:**
- Convenient for development and testing
- Simplifies deployment scripts
- Maintains compatibility with existing tools

**Disadvantages:**
- Disables privilege separation in ADB (security-by-design removed)
- Affects all ADB connections (including potentially malicious ones)
- Library must be trusted (runs in adbd context)

**Mitigations:**
1. Use minimal version (`nosetuid_min.so`) when possible
2. Store library in root-owned directory
3. Set restrictive permissions (644, root-owned)
4. Verify library checksum regularly
5. Disable when not needed (clear `wrap.adbd` property)

### SELinux Considerations

On devices with SELinux enforcing:
- SUID binaries may be blocked by policy
- LD_PRELOAD may be restricted for system services
- May need to set permissive mode or modify policy

Check SELinux status:
```bash
adb shell getenforce
# Permissive = OK
# Enforcing = May cause issues
```

Temporary solution:
```bash
adb shell "su -c 'setenforce 0'"  # Set permissive
```

Permanent solution: Modify SELinux policy (advanced)

---

## Troubleshooting

### KSU Issues

**Problem:** `ksu: permission denied`

**Solution:** Check SUID bit and ownership:
```bash
adb shell "ls -l /bin/ksu"
# Expected: -rwsr-xr-x 1 root root ...
```

If incorrect:
```bash
adb shell "su -c 'chmod 4755 /bin/ksu && chown 0:0 /bin/ksu'"
```

---

**Problem:** `ksu` exists but `su` doesn't work

**Solution:** Create symlink:
```bash
adb shell "su -c 'ln -sf /bin/ksu /bin/su'"
```

---

**Problem:** `setuid: Operation not permitted`

**Causes:**
1. Filesystem mounted with `nosuid` option
2. SELinux blocking
3. Kernel restrictions

**Check mount options:**
```bash
adb shell "mount | grep ' / '"
```

**Remount if needed:**
```bash
adb shell "su -c 'mount -o remount,suid /'"
```

### NoSetUID Issues

**Problem:** ADB still runs as shell user (UID 2000)

**Solution:** Verify library is loaded:
```bash
adb shell "getprop wrap.adbd"
# Expected: LD_PRELOAD=/data/local/nosetuid.so
```

If not set:
```bash
adb shell "su -c 'setprop wrap.adbd \"LD_PRELOAD=/data/local/nosetuid.so\"'"
adb shell "su -c 'stop adbd && start adbd'"
```

---

**Problem:** Library loads but privilege drop still happens

**Causes:**
1. Wrong architecture (ARM vs x86)
2. SELinux blocking
3. Library not finding symbols

**Check library architecture:**
```bash
file build/nosetuid.so
# Should match device architecture
```

**Check ADB logs:**
```bash
adb shell "logcat -d | grep adbd"
```

---

**Problem:** ADB daemon won't start after setting wrap.adbd

**Solution:** Clear property and restart:
```bash
adb shell "su -c 'setprop wrap.adbd \"\"'"
adb shell "su -c 'start adbd'"
```

### General Troubleshooting

**Test root access:**
```bash
# Via su
adb shell "su -c 'id'"

# Via ksu directly
adb shell "/bin/ksu -c 'id'"

# Via ADB with nosetuid
adb shell "id"
```

**Check logs:**
```bash
# System log
adb shell "logcat -d"

# Init script log
adb shell "cat /data/rayhunter/orbital_os.log"
```

---

## Testing

Use the comprehensive test suite:

```bash
# Run all tests
./tools/test_folc.sh

# Specific tests for frontdoor
adb shell "/bin/ksu -c 'id'"  # Test ksu
adb shell "id"                # Test nosetuid (if enabled)
```

See [tools/test_folc.sh](../tools/test_folc.sh) for complete test suite.

---

## Migration from Backdoor

If you're currently using the backdoor method:

### Step 1: Build and Install Frontdoor
```bash
make
make install
```

### Step 2: Update Scripts
Replace:
```bash
echo "command" | nc localhost 9999
```

With:
```bash
adb shell "su -c 'command'"
```

### Step 3: Update Init Scripts
Modify `/data/rayhunter/orbital_os_init.sh` to prioritize frontdoor.

### Step 4: Test
```bash
./tools/test_folc.sh
```

### Step 5: Optional - Disable Backdoor
If frontdoor works reliably, you can disable the backdoor in `orbital_os_init.sh`:
```bash
# Comment out backdoor launch
# (while true; do /bin/busybox nc -ll -p $BACKDOOR_PORT -e /bin/sh; sleep 1; done) &
```

---

## Future Enhancements

Potential improvements to the frontdoor implementation:

1. **Kernel Module:** Replace SUID binary with kernel-level su support (KernelSU style)
2. **SELinux Policy:** Custom policy allowing frontdoor while maintaining security
3. **Authentication:** Add password or key-based authentication to `ksu`
4. **Logging:** Add audit logging for root access events
5. **Dynamic Enable/Disable:** Remote control of root access methods

---

## References

- **KernelSU Project:** https://github.com/tiann/KernelSU
- **Magisk:** https://github.com/topjohnwu/Magisk
- **Android Security:** https://source.android.com/security
- **LD_PRELOAD:** `man 8 ld.so`
- **SUID Binaries:** `man 2 setuid`

---

**Last Updated:** January 2026
