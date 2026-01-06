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

# Detect host OS and architecture
HOST_OS := $(shell uname -s | tr '[:upper:]' '[:lower:]')
HOST_ARCH := $(shell uname -m)

# Map host architecture
ifeq ($(HOST_ARCH),x86_64)
    HOST_ARCH_NAME := x86_64
else ifeq ($(HOST_ARCH),aarch64)
    HOST_ARCH_NAME := aarch64
else ifeq ($(HOST_ARCH),arm64)
    HOST_ARCH_NAME := aarch64
else
    HOST_ARCH_NAME := x86_64
endif

# Target architecture (can be overridden)
TARGET_ARCH ?= armv7
TARGET_API ?= 21

# Compiler settings (NDK-based)
ifeq ($(TARGET_ARCH),armv7)
    NDK_TARGET := armv7a-linux-androideabi$(TARGET_API)
    ALT_COMPILER := arm-linux-gnueabi-gcc
    ALT_AR := arm-linux-gnueabi-ar
    ALT_STRIP := arm-linux-gnueabi-strip
else ifeq ($(TARGET_ARCH),aarch64)
    NDK_TARGET := aarch64-linux-android$(TARGET_API)
    ALT_COMPILER := aarch64-linux-gnu-gcc
    ALT_AR := aarch64-linux-gnu-ar
    ALT_STRIP := aarch64-linux-gnu-strip
else ifeq ($(TARGET_ARCH),x86)
    NDK_TARGET := i686-linux-android$(TARGET_API)
    ALT_COMPILER := i686-linux-android-gcc
    ALT_AR := i686-linux-android-ar
    ALT_STRIP := i686-linux-android-strip
else
    $(error Unsupported TARGET_ARCH: $(TARGET_ARCH). Use armv7, aarch64, or x86)
endif

# Try to use NDK if available, otherwise fall back to system compiler
ifdef NDK_ROOT
    CC := $(NDK_ROOT)/toolchains/llvm/prebuilt/$(HOST_OS)-$(HOST_ARCH_NAME)/bin/$(NDK_TARGET)-clang
    AR := $(NDK_ROOT)/toolchains/llvm/prebuilt/$(HOST_OS)-$(HOST_ARCH_NAME)/bin/llvm-ar
    STRIP := $(NDK_ROOT)/toolchains/llvm/prebuilt/$(HOST_OS)-$(HOST_ARCH_NAME)/bin/llvm-strip
else
    CC := $(ALT_COMPILER)
    AR := $(ALT_AR)
    STRIP := $(ALT_STRIP)
endif

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
	@echo "Host:   $(HOST_OS)-$(HOST_ARCH)"
	@echo "Target: $(TARGET_ARCH) (API $(TARGET_API))"
	@echo ""
	@echo "Binaries:"
	@echo "  ksu:           $(KSU_BIN)"
	@echo "  nosetuid.so:   $(NOSETUID_SO)"
	@echo "  nosetuid_min:  $(NOSETUID_MIN_SO)"
	@echo ""
	@echo "To install on device:"
	@echo "  make install"
	@echo ""
	@echo "To build for different architecture:"
	@echo "  make TARGET_ARCH=aarch64"
	@echo "  make TARGET_ARCH=armv7"
	@echo ""

# Check if compiler exists
check:
	@echo "Checking build environment..."
	@echo "Host: $(HOST_OS)-$(HOST_ARCH)"
	@echo "Target: $(TARGET_ARCH) (API $(TARGET_API))"
	@if [ -z "$(NDK_ROOT)" ]; then \
		echo "WARNING: NDK_ROOT not set. Trying system compiler..."; \
		if ! command -v $(CC) >/dev/null 2>&1; then \
			echo "ERROR: No suitable compiler found!"; \
			echo ""; \
			echo "Please either:"; \
			echo "  1. Set NDK_ROOT to your Android NDK path"; \
			echo "  2. Install ARM cross-compiler: apt-get install gcc-$(TARGET_ARCH)-linux-gnueabi"; \
			echo ""; \
			exit 1; \
		else \
			echo "Using system compiler: $(CC)"; \
		fi; \
	else \
		if [ ! -f "$(CC)" ]; then \
			echo "ERROR: NDK compiler not found at: $(CC)"; \
			echo ""; \
			echo "Please verify:"; \
			echo "  1. NDK_ROOT is set correctly: $(NDK_ROOT)"; \
			echo "  2. NDK is properly installed"; \
			echo "  3. Target matches your NDK version"; \
			echo ""; \
			exit 1; \
		else \
			echo "Using NDK compiler: $(CC)"; \
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
	@echo "  cp /data/local/tmp/nosetuid.so /data/local/nosetuid.so"
	@echo "  setprop wrap.adbd \"LD_PRELOAD=/data/local/nosetuid.so\""
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
	@echo "Configuration:"
	@echo "  TARGET_ARCH   - Target architecture (armv7, aarch64, x86)"
	@echo "  TARGET_API    - Android API level (default: 21)"
	@echo "  NDK_ROOT      - Path to Android NDK"
	@echo ""
	@echo "Examples:"
	@echo "  export NDK_ROOT=/path/to/android-ndk"
	@echo "  make                              # Build for ARMv7"
	@echo "  make TARGET_ARCH=aarch64          # Build for ARM64"
	@echo "  make install                      # Build and install"
	@echo ""
	@echo "Current Configuration:"
	@echo "  Host:   $(HOST_OS)-$(HOST_ARCH)"
	@echo "  Target: $(TARGET_ARCH) (API $(TARGET_API))"
	@echo ""
