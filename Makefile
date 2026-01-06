# Makefile for FOLC-V3 Native Binaries
# Builds ksu (su replacement) and nosetuid.so (LD_PRELOAD library)
#
# Requirements: 
#   - Android NDK or cross-compiler for ARM
#   - Set NDK_ROOT environment variable to your NDK path
#
# Usage:
#   make          - Build all binaries
#   make ksu      - Build ksu binary only
#   make nosetuid - Build nosetuid.so library only
#   make clean    - Remove built binaries

# Compiler settings
CC := $(NDK_ROOT)/toolchains/llvm/prebuilt/linux-x86_64/bin/armv7a-linux-androideabi21-clang
AR := $(NDK_ROOT)/toolchains/llvm/prebuilt/linux-x86_64/bin/llvm-ar
STRIP := $(NDK_ROOT)/toolchains/llvm/prebuilt/linux-x86_64/bin/llvm-strip

# Alternative: use gcc for ARM if NDK not available
# CC := arm-linux-gnueabi-gcc
# AR := arm-linux-gnueabi-ar
# STRIP := arm-linux-gnueabi-strip

# Compiler flags
CFLAGS := -Wall -O2 -static
LDFLAGS := -static

# Shared library flags
SOFLAGS := -shared -fPIC -O2

# Output directory
BUILD_DIR := build

# Targets
KSU_BIN := $(BUILD_DIR)/ksu
NOSETUID_SO := $(BUILD_DIR)/nosetuid.so
NOSETUID_MIN_SO := $(BUILD_DIR)/nosetuid_min.so

# Sources
KSU_SRC := ksu.c
NOSETUID_SRC := nosetuid.c
NOSETUID_MIN_SRC := nosetuid_min.c

.PHONY: all ksu nosetuid nosetuid_min clean install help check

# Default target
all: check $(KSU_BIN) $(NOSETUID_SO) $(NOSETUID_MIN_SO)
	@echo ""
	@echo "════════════════════════════════════════"
	@echo "Build complete!"
	@echo "════════════════════════════════════════"
	@echo "Binaries:"
	@echo "  ksu:           $(KSU_BIN)"
	@echo "  nosetuid.so:   $(NOSETUID_SO)"
	@echo "  nosetuid_min:  $(NOSETUID_MIN_SO)"
	@echo ""
	@echo "To install on device:"
	@echo "  make install"
	@echo ""

# Check if compiler exists
check:
	@echo "Checking build environment..."
	@if [ -z "$(NDK_ROOT)" ]; then \
		echo "WARNING: NDK_ROOT not set. Trying system compiler..."; \
		if ! command -v arm-linux-gnueabi-gcc >/dev/null 2>&1; then \
			echo "ERROR: No ARM compiler found!"; \
			echo ""; \
			echo "Please either:"; \
			echo "  1. Set NDK_ROOT to your Android NDK path"; \
			echo "  2. Install ARM cross-compiler: apt-get install gcc-arm-linux-gnueabi"; \
			echo ""; \
			exit 1; \
		fi; \
	fi
	@mkdir -p $(BUILD_DIR)

# Build ksu (SUID root binary)
ksu: $(KSU_BIN)

$(KSU_BIN): $(KSU_SRC)
	@echo "Building ksu binary..."
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $<
	$(STRIP) $@
	@echo "✓ ksu built successfully"

# Build nosetuid.so (full version)
nosetuid: $(NOSETUID_SO)

$(NOSETUID_SO): $(NOSETUID_SRC)
	@echo "Building nosetuid.so library..."
	$(CC) $(SOFLAGS) -o $@ $<
	$(STRIP) $@
	@echo "✓ nosetuid.so built successfully"

# Build nosetuid_min.so (minimal version)
nosetuid_min: $(NOSETUID_MIN_SO)

$(NOSETUID_MIN_SO): $(NOSETUID_MIN_SRC)
	@echo "Building nosetuid_min.so library..."
	$(CC) $(SOFLAGS) -o $@ $<
	$(STRIP) $@
	@echo "✓ nosetuid_min.so built successfully"

# Install to device via ADB
install: all
	@echo ""
	@echo "Installing binaries to device..."
	@if ! adb devices | grep -q "device$$"; then \
		echo "ERROR: No device connected via ADB"; \
		exit 1; \
	fi
	@echo ""
	@echo "Pushing ksu to /data/local/tmp..."
	adb push $(KSU_BIN) /data/local/tmp/ksu
	@echo ""
	@echo "Pushing nosetuid.so to /data/local/tmp..."
	adb push $(NOSETUID_SO) /data/local/tmp/nosetuid.so
	@echo ""
	@echo "Pushing nosetuid_min.so to /data/local/tmp..."
	adb push $(NOSETUID_MIN_SO) /data/local/tmp/nosetuid_min.so
	@echo ""
	@echo "════════════════════════════════════════"
	@echo "Binaries pushed to /data/local/tmp/"
	@echo ""
	@echo "To install ksu as su replacement:"
	@echo "  adb shell"
	@echo "  su"
	@echo "  cp /data/local/tmp/ksu /bin/ksu"
	@echo "  chmod 4755 /bin/ksu"
	@echo "  ln -sf /bin/ksu /bin/su"
	@echo ""
	@echo "To use nosetuid.so with adbd:"
	@echo "  cp /data/local/tmp/nosetuid.so /data/local/tmp/"
	@echo "  setprop wrap.adbd \"LD_PRELOAD=/data/local/tmp/nosetuid.so\""
	@echo "  stop adbd && start adbd"
	@echo "════════════════════════════════════════"

# Clean build artifacts
clean:
	@echo "Cleaning build directory..."
	rm -rf $(BUILD_DIR)
	@echo "✓ Clean complete"

# Help
help:
	@echo "FOLC-V3 Native Binaries Makefile"
	@echo "================================"
	@echo ""
	@echo "Targets:"
	@echo "  make          - Build all binaries"
	@echo "  make ksu      - Build ksu binary only"
	@echo "  make nosetuid - Build nosetuid.so only"
	@echo "  make clean    - Remove build artifacts"
	@echo "  make install  - Build and push to device via ADB"
	@echo "  make help     - Show this help message"
	@echo ""
	@echo "Prerequisites:"
	@echo "  - Android NDK (set NDK_ROOT environment variable)"
	@echo "  - OR ARM cross-compiler (gcc-arm-linux-gnueabi)"
	@echo "  - ADB for device installation"
	@echo ""
	@echo "Example:"
	@echo "  export NDK_ROOT=/path/to/android-ndk"
	@echo "  make"
	@echo "  make install"
	@echo ""
