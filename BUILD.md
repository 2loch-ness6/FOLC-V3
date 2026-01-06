# Building FOLC-V3 Native Components

This guide explains how to build the native C components for FOLC-V3: the `ksu` SUID root binary and `nosetuid.so` LD_PRELOAD library.

## Overview

FOLC-V3 includes two native components that enable persistent root access:

1. **ksu** - A minimal SUID root binary that provides `su` functionality
2. **nosetuid.so** - An LD_PRELOAD library that prevents privilege dropping in ADB daemon

These components implement the "frontdoor" root access method, providing a firmware-backed persistent root solution.

---

## Prerequisites

### Option 1: Android NDK (Recommended)

Download and install the Android NDK:

```bash
# Download NDK
wget https://dl.google.com/android/repository/android-ndk-r26b-linux.zip
unzip android-ndk-r26b-linux.zip
export NDK_ROOT=$PWD/android-ndk-r26b
```

### Option 2: ARM Cross-Compiler

On Ubuntu/Debian:

```bash
sudo apt-get install gcc-arm-linux-gnueabi
```

### Additional Requirements

- GNU Make
- ADB (for device installation)

---

## Building

### Build All Components

```bash
# Set NDK path (if using NDK)
export NDK_ROOT=/path/to/android-ndk

# Build everything
make
```

This will create:
- `build/ksu` - SUID root binary
- `build/nosetuid.so` - Full version of privilege-prevention library
- `build/nosetuid_min.so` - Minimal version

### Build Individual Components

```bash
# Build only ksu
make ksu

# Build only nosetuid libraries
make nosetuid
```

### Clean Build Artifacts

```bash
make clean
```

---

## Installation

### Automatic Installation (via ADB)

```bash
# Connect device via USB
adb devices

# Build and push to device
make install
```

This pushes the binaries to `/data/local/tmp/` on the device.

### Manual Installation

#### Installing ksu as su replacement:

```bash
# 1. Push to device
adb push build/ksu /data/local/tmp/ksu

# 2. On device (as root)
adb shell
su  # or use existing root method
cp /data/local/tmp/ksu /bin/ksu
chmod 4755 /bin/ksu
chown 0:0 /bin/ksu

# 3. Create symlink (optional)
ln -sf /bin/ksu /bin/su

# 4. Test
exit
su -c id
# Should output: uid=0(root) gid=0(root)
```

#### Installing nosetuid.so for ADB root persistence:

```bash
# 1. Push to device
adb push build/nosetuid.so /data/local/tmp/nosetuid.so

# 2. On device (as root)
adb shell
su
cp /data/local/tmp/nosetuid.so /data/local/nosetuid.so
chmod 644 /data/local/nosetuid.so

# 3. Configure ADB to preload it
setprop wrap.adbd "LD_PRELOAD=/data/local/nosetuid.so"

# 4. Restart ADB daemon
stop adbd
start adbd

# 5. Test (from host)
adb shell id
# Should output: uid=0(root) ...
```

---

## Component Details

### ksu.c - SUID Root Binary

This is a minimal `su` implementation that:
- Sets UID and GID to 0 (root)
- Executes a shell or specified command with root privileges
- Serves as a persistent root access point

**Usage:**
```bash
# Spawn root shell
ksu

# Execute command as root
ksu -c "command here"

# Execute specific binary
ksu /bin/sh
```

**Security Note:** This binary must have SUID bit set (`chmod 4755`) and be owned by root to function.

### nosetuid.c - Privilege Prevention Library

This LD_PRELOAD library intercepts system calls that drop privileges:
- `setuid()`, `setgid()`, `setgroups()`
- `setresuid()`, `setresgid()`
- `capset()` (capability modification)

All intercepted calls return success (0) without actually changing privileges.

**Purpose:** When preloaded into the ADB daemon (adbd), it prevents the daemon from dropping from root to the `shell` user (UID 2000), maintaining root access for all ADB shell sessions.

**Versions:**
- `nosetuid.so` - Full version with GNU extensions
- `nosetuid_min.so` - Minimal version with basic type definitions only

### nosetuid_min.c - Minimal Version

Minimal implementation without standard library dependencies. Useful for systems with limited libc support.

---

## Persistence Integration

These components integrate with FOLC-V3's persistence mechanisms:

### 1. Frontdoor Access (Primary Method)

With `ksu` installed as `/bin/su`:

```bash
# From host
adb shell su -c "command"

# From deployment scripts
adb shell "su -c 'chroot /data/alpine /bin/sh'"
```

### 2. ADB Root Persistence (Alternative)

With `nosetuid.so` preloaded into adbd:

```bash
# All ADB shells are root by default
adb shell
# uid=0(root) ...
```

### 3. Integration with Init Scripts

Add to `/data/rayhunter/orbital_os_init.sh`:

```bash
# Ensure ksu is installed
if [ ! -f /bin/ksu ]; then
    if [ -f /data/local/tmp/ksu ]; then
        cp /data/local/tmp/ksu /bin/ksu
        chmod 4755 /bin/ksu
        chown 0:0 /bin/ksu
    fi
fi

# Configure ADB root persistence
if [ -f /data/local/nosetuid.so ]; then
    setprop wrap.adbd "LD_PRELOAD=/data/local/nosetuid.so"
    stop adbd
    start adbd
fi
```

---

## Troubleshooting

### Build Errors

**Problem:** `arm-linux-androideabi21-clang: not found`

**Solution:** Ensure NDK_ROOT is set correctly:
```bash
export NDK_ROOT=/path/to/your/ndk
make clean
make
```

**Problem:** `No ARM compiler found`

**Solution:** Install cross-compiler or set up NDK:
```bash
sudo apt-get install gcc-arm-linux-gnueabi
```

### Installation Issues

**Problem:** `ksu` doesn't provide root access

**Solution:** Verify SUID bit and ownership:
```bash
adb shell "ls -l /bin/ksu"
# Should show: -rwsr-xr-x 1 root root ...
```

If not:
```bash
adb shell
su  # use alternate root method
chmod 4755 /bin/ksu
chown 0:0 /bin/ksu
```

**Problem:** `nosetuid.so` doesn't work with ADB

**Solution:** Check if property is set:
```bash
adb shell getprop wrap.adbd
# Should output: LD_PRELOAD=/data/local/nosetuid.so
```

Restart ADB daemon:
```bash
adb shell
su
stop adbd
start adbd
```

### Testing

Test `ksu`:
```bash
adb shell "/bin/ksu -c 'id'"
# Should output: uid=0(root) gid=0(root) ...
```

Test `nosetuid.so` with ADB:
```bash
adb shell id
# Should output: uid=0(root) ...
```

---

## Advanced Usage

### Building for Different Architectures

Edit the Makefile to change the target architecture:

```makefile
# For ARM64
CC := $(NDK_ROOT)/toolchains/llvm/prebuilt/linux-x86_64/bin/aarch64-linux-android21-clang

# For x86
CC := $(NDK_ROOT)/toolchains/llvm/prebuilt/linux-x86_64/bin/i686-linux-android21-clang
```

### Custom Compiler Flags

For debugging builds:
```bash
make CFLAGS="-Wall -g -O0" ksu
```

For size-optimized builds:
```bash
make CFLAGS="-Wall -Os -s" ksu
```

### Verification

Verify binary integrity:
```bash
# Check binary type
file build/ksu
# Output: build/ksu: ELF 32-bit LSB executable, ARM, ...

# Check symbols
nm build/ksu

# Check if statically linked
ldd build/ksu
# Should output: not a dynamic executable (statically linked)
```

---

## Security Considerations

### SUID Root Binary Risks

The `ksu` binary provides unrestricted root access. Consider:

1. **Access Control:** On multi-user systems, ensure only authorized users can execute it
2. **File Permissions:** Keep binary permissions at `4755` (no world-write)
3. **Ownership:** Must be owned by root (UID 0)
4. **Auditing:** Monitor usage in production environments

### LD_PRELOAD Implications

Using `nosetuid.so` with adbd:

1. **System-wide Effect:** Affects all ADB connections
2. **Security Impact:** Disables privilege separation in ADB
3. **Alternative:** Consider using `ksu` for explicit root access instead
4. **Persistence:** Survives ADB daemon restarts but not full reboots (without init script)

---

## Integration with FOLC-V3

### Frontdoor Implementation Status

- ✅ `ksu` compiled and tested
- ✅ `nosetuid.so` compiled and tested  
- ✅ Installation scripts created
- ✅ Integration with `orbital_os_init.sh`
- ✅ Documentation complete

### Recommended Setup

For FOLC-V3, we recommend:

1. **Primary Access:** Use `ksu` as `/bin/su` for explicit root commands
2. **Convenience:** Optionally use `nosetuid.so` for ADB root persistence
3. **Fallback:** Keep netcat backdoor (port 9999) as secondary access method

This provides multiple layers of root access redundancy.

---

## References

- Android Security: https://source.android.com/security
- SUID Binaries: `man 2 setuid`
- LD_PRELOAD: `man 8 ld.so`
- Android NDK: https://developer.android.com/ndk

---

## Contributing

When modifying these components:

1. Test thoroughly on target hardware
2. Verify no security regressions
3. Update this documentation
4. Consider compatibility with different Android versions

See [CONTRIBUTING.md](CONTRIBUTING.md) for general contribution guidelines.

---

**Last Updated:** January 2026
