#!/bin/sh
################################################################################
# SYMLINK BRIDGE SCRIPT
#
# Purpose: Create bidirectional symlink bridge between Host (Qualcomm Embedded
#          Linux) and Alpine Linux chroot environment
#
# Location: /data/rayhunter/symlink_bridge.sh
#
# Author: FOLC-V3 Project / Copilot Architect  
# Version: 1.0
# Date: January 2026
#
# Usage:
#   symlink_bridge.sh setup    - Create all symlinks
#   symlink_bridge.sh cleanup  - Remove all symlinks
#   symlink_bridge.sh status   - Check current bridge status
#   symlink_bridge.sh verify   - Verify all symlinks are working
#
################################################################################

# Configuration
ALPINE_ROOT="/data/alpine"
HOST_BIN_DIR="$ALPINE_ROOT/host-bin"
HOST_LIB_DIR="$ALPINE_ROOT/host-lib"
MANIFEST_FILE="$ALPINE_ROOT/.bridge_manifest"
LOG_FILE="/data/rayhunter/symlink_bridge.log"

################################################################################
# Logging Functions
################################################################################

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [+] $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [-] $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [!] $1" | tee -a "$LOG_FILE"
}

################################################################################
# Binary Mapping Configuration
################################################################################

# This function defines which Host binaries should be bridged into Alpine
# Format: "host_path:alpine_link:description"
get_binary_mappings() {
    cat <<EOF
/usr/sbin/iw:$HOST_BIN_DIR/iw:WiFi interface configuration tool
/sbin/ip:$HOST_BIN_DIR/ip:Advanced network configuration
/sbin/ifconfig:$HOST_BIN_DIR/ifconfig:Legacy network interface configuration
/sbin/route:$HOST_BIN_DIR/route:Kernel routing table management
/usr/bin/netstat:$HOST_BIN_DIR/netstat:Network statistics display
/sbin/iwconfig:$HOST_BIN_DIR/iwconfig:Wireless interface configuration
/usr/sbin/iwlist:$HOST_BIN_DIR/iwlist:Wireless scanning tool
/sbin/modprobe:$HOST_BIN_DIR/modprobe:Kernel module loading
/sbin/rmmod:$HOST_BIN_DIR/rmmod:Kernel module removal
/sbin/lsmod:$HOST_BIN_DIR/lsmod:List loaded kernel modules
/bin/dmesg:$HOST_BIN_DIR/dmesg:Kernel ring buffer messages
/usr/bin/lsusb:$HOST_BIN_DIR/lsusb:List USB devices
/sbin/ethtool:$HOST_BIN_DIR/ethtool:Ethernet device settings
EOF
}

# Library mappings (if needed for certain binaries)
# This function is currently empty but reserved for future use
# when Host libraries need to be made available in Alpine
get_library_mappings() {
    # Intentionally empty - no library mappings needed yet
    # Add library mappings here in future if binaries require Host libraries
    # Example format: /lib/libnl.so:$HOST_LIB_DIR/libnl.so:Netlink library
    cat <<EOF
EOF
}

################################################################################
# Directory Management
################################################################################

create_bridge_directories() {
    log "Creating bridge directories..."
    
    # Create host-bin directory in Alpine
    if [ ! -d "$HOST_BIN_DIR" ]; then
        if mkdir -p "$HOST_BIN_DIR" 2>/dev/null; then
            log_success "Created directory: $HOST_BIN_DIR"
        else
            log_error "Failed to create directory: $HOST_BIN_DIR"
            return 1
        fi
    else
        log "Directory already exists: $HOST_BIN_DIR"
    fi
    
    # Create host-lib directory in Alpine (for future use)
    if [ ! -d "$HOST_LIB_DIR" ]; then
        if mkdir -p "$HOST_LIB_DIR" 2>/dev/null; then
            log_success "Created directory: $HOST_LIB_DIR"
        else
            log_error "Failed to create directory: $HOST_LIB_DIR"
            return 1
        fi
    else
        log "Directory already exists: $HOST_LIB_DIR"
    fi
    
    return 0
}

remove_bridge_directories() {
    log "Removing bridge directories..."
    
    if [ -d "$HOST_BIN_DIR" ]; then
        rm -rf "$HOST_BIN_DIR"
        log_success "Removed directory: $HOST_BIN_DIR"
    fi
    
    if [ -d "$HOST_LIB_DIR" ]; then
        rm -rf "$HOST_LIB_DIR"  
        log_success "Removed directory: $HOST_LIB_DIR"
    fi
    
    return 0
}

################################################################################
# Symlink Management
################################################################################

create_symlink() {
    local source="$1"
    local target="$2"
    local description="$3"
    
    # Check if source exists
    if [ ! -e "$source" ]; then
        log_warning "Source not found: $source ($description)"
        return 1
    fi
    
    # Check if source is executable (for binaries)
    if [ ! -x "$source" ] && [ -d "$(dirname "$target")" ] && echo "$target" | grep -q "/host-bin/"; then
        log_warning "Source not executable: $source"
    fi
    
    # Remove existing symlink/file if it exists
    if [ -e "$target" ] || [ -L "$target" ]; then
        rm -f "$target" 2>/dev/null
    fi
    
    # Create the symlink
    if ln -s "$source" "$target" 2>/dev/null; then
        log_success "Created symlink: $target -> $source"
        # Record in manifest
        echo "$source:$target:$description" >> "$MANIFEST_FILE"
        return 0
    else
        log_error "Failed to create symlink: $target -> $source"
        return 1
    fi
}

remove_symlink() {
    local target="$1"
    
    if [ -L "$target" ]; then
        if rm -f "$target" 2>/dev/null; then
            log_success "Removed symlink: $target"
            return 0
        else
            log_error "Failed to remove symlink: $target"
            return 1
        fi
    elif [ -e "$target" ]; then
        log_warning "Not a symlink: $target (skipping)"
        return 1
    else
        log_warning "Target not found: $target (already removed)"
        return 0
    fi
}

################################################################################
# PATH Management
################################################################################

update_alpine_path() {
    log "Updating Alpine PATH to include host binaries..."
    
    local profile_file="$ALPINE_ROOT/etc/profile.d/host-bridge.sh"
    
    # Create profile.d directory if it doesn't exist
    mkdir -p "$ALPINE_ROOT/etc/profile.d" 2>/dev/null
    
    # Create profile script to add host-bin to PATH
    cat > "$profile_file" <<'PROFILE_EOF'
#!/bin/sh
# Symlink Bridge - Add Host binaries to PATH
# Auto-generated by symlink_bridge.sh

# Add host-bin to PATH if not already present
if [ -d /host-bin ] && ! echo "$PATH" | grep -q "/host-bin"; then
    export PATH="/host-bin:$PATH"
fi

# Add host-lib to LD_LIBRARY_PATH if needed
if [ -d /host-lib ] && [ -n "$(ls -A /host-lib 2>/dev/null)" ]; then
    if [ -n "$LD_LIBRARY_PATH" ]; then
        export LD_LIBRARY_PATH="/host-lib:$LD_LIBRARY_PATH"
    else
        export LD_LIBRARY_PATH="/host-lib"
    fi
fi
PROFILE_EOF
    
    if [ -f "$profile_file" ]; then
        chmod +x "$profile_file"
        log_success "Created PATH update script: $profile_file"
        return 0
    else
        log_error "Failed to create PATH update script"
        return 1
    fi
}

remove_alpine_path() {
    log "Removing Alpine PATH modifications..."
    
    local profile_file="$ALPINE_ROOT/etc/profile.d/host-bridge.sh"
    
    if [ -f "$profile_file" ]; then
        rm -f "$profile_file"
        log_success "Removed PATH update script"
    fi
    
    return 0
}

################################################################################
# Main Operations
################################################################################

do_setup() {
    log "=========================================="
    log "SYMLINK BRIDGE - SETUP"
    log "=========================================="
    
    # Verify Alpine root exists
    if [ ! -d "$ALPINE_ROOT" ]; then
        log_error "Alpine root directory not found: $ALPINE_ROOT"
        return 1
    fi
    
    # Create bridge directories
    if ! create_bridge_directories; then
        log_error "Failed to create bridge directories"
        return 1
    fi
    
    # Initialize manifest file
    echo "# Symlink Bridge Manifest" > "$MANIFEST_FILE"
    echo "# Created: $(date)" >> "$MANIFEST_FILE"
    echo "# Format: source:target:description" >> "$MANIFEST_FILE"
    
    # Create binary symlinks
    log "Creating binary symlinks..."
    local success=0
    local failed=0
    
    while IFS=: read -r source target description; do
        if create_symlink "$source" "$target" "$description"; then
            success=$((success + 1))
        else
            failed=$((failed + 1))
        fi
    done <<EOF
$(get_binary_mappings)
EOF
    
    # Create library symlinks (if any)
    log "Creating library symlinks..."
    while IFS=: read -r source target description; do
        if [ -n "$source" ]; then
            if create_symlink "$source" "$target" "$description"; then
                success=$((success + 1))
            else
                failed=$((failed + 1))
            fi
        fi
    done <<EOF
$(get_library_mappings)
EOF
    
    # Update Alpine PATH
    update_alpine_path
    
    # Summary
    log "=========================================="
    log_success "Symlink bridge setup complete"
    log "  Created: $success symlinks"
    if [ $failed -gt 0 ]; then
        log_warning "  Failed: $failed symlinks"
    fi
    log "  Manifest: $MANIFEST_FILE"
    log "=========================================="
    
    return 0
}

do_cleanup() {
    log "=========================================="
    log "SYMLINK BRIDGE - CLEANUP"
    log "=========================================="
    
    # Read manifest and remove all symlinks
    if [ -f "$MANIFEST_FILE" ]; then
        log "Reading manifest file..."
        
        local count=0
        while IFS=: read -r source target description; do
            # Skip comments and empty lines
            if echo "$source" | grep -q "^#" || [ -z "$source" ]; then
                continue
            fi
            
            remove_symlink "$target"
            count=$((count + 1))
        done < "$MANIFEST_FILE"
        
        log "Processed $count entries from manifest"
        
        # Remove manifest
        rm -f "$MANIFEST_FILE"
        log_success "Removed manifest file"
    else
        log_warning "Manifest file not found, cleaning up known locations..."
        
        # Clean up host-bin directory
        if [ -d "$HOST_BIN_DIR" ]; then
            find "$HOST_BIN_DIR" -type l -delete 2>/dev/null
        fi
        
        # Clean up host-lib directory
        if [ -d "$HOST_LIB_DIR" ]; then
            find "$HOST_LIB_DIR" -type l -delete 2>/dev/null
        fi
    fi
    
    # Remove PATH modifications
    remove_alpine_path
    
    # Remove directories
    remove_bridge_directories
    
    log "=========================================="
    log_success "Symlink bridge cleanup complete"
    log "=========================================="
    
    return 0
}

do_status() {
    log "=========================================="
    log "SYMLINK BRIDGE - STATUS"
    log "=========================================="
    
    # Check if directories exist
    if [ -d "$HOST_BIN_DIR" ]; then
        local bin_count=$(find "$HOST_BIN_DIR" -type l 2>/dev/null | wc -l)
        log_success "Host bin directory exists with $bin_count symlinks"
    else
        log_warning "Host bin directory does not exist"
    fi
    
    if [ -d "$HOST_LIB_DIR" ]; then
        local lib_count=$(find "$HOST_LIB_DIR" -type l 2>/dev/null | wc -l)
        log_success "Host lib directory exists with $lib_count symlinks"
    else
        log_warning "Host lib directory does not exist"
    fi
    
    # Check manifest
    if [ -f "$MANIFEST_FILE" ]; then
        local manifest_count=$(grep -v "^#" "$MANIFEST_FILE" | grep -v "^$" | wc -l)
        log_success "Manifest file exists with $manifest_count entries"
    else
        log_warning "Manifest file does not exist"
    fi
    
    # Check PATH configuration
    if [ -f "$ALPINE_ROOT/etc/profile.d/host-bridge.sh" ]; then
        log_success "PATH configuration exists"
    else
        log_warning "PATH configuration does not exist"
    fi
    
    log "=========================================="
    
    return 0
}

do_verify() {
    log "=========================================="
    log "SYMLINK BRIDGE - VERIFY"
    log "=========================================="
    
    if [ ! -f "$MANIFEST_FILE" ]; then
        log_error "Manifest file not found - bridge not set up"
        return 1
    fi
    
    local total=0
    local valid=0
    local broken=0
    
    log "Verifying symlinks from manifest..."
    
    while IFS=: read -r source target description; do
        # Skip comments and empty lines
        if echo "$source" | grep -q "^#" || [ -z "$source" ]; then
            continue
        fi
        
        total=$((total + 1))
        
        # Check if symlink exists
        if [ ! -L "$target" ]; then
            log_error "Symlink missing: $target"
            broken=$((broken + 1))
            continue
        fi
        
        # Check if symlink points to correct location
        local link_target=$(readlink "$target")
        if [ "$link_target" != "$source" ]; then
            log_error "Symlink incorrect: $target -> $link_target (expected: $source)"
            broken=$((broken + 1))
            continue
        fi
        
        # Check if source still exists
        if [ ! -e "$source" ]; then
            log_warning "Symlink broken (source missing): $target -> $source"
            broken=$((broken + 1))
            continue
        fi
        
        log_success "Valid: $target -> $source"
        valid=$((valid + 1))
        
    done < "$MANIFEST_FILE"
    
    log "=========================================="
    log "Verification complete:"
    log "  Total: $total symlinks"
    log_success "  Valid: $valid symlinks"
    
    if [ $broken -gt 0 ]; then
        log_warning "  Broken: $broken symlinks"
    fi
    
    log "=========================================="
    
    if [ $broken -gt 0 ]; then
        return 1
    else
        return 0
    fi
}

do_list() {
    log "=========================================="
    log "SYMLINK BRIDGE - LIST"
    log "=========================================="
    
    if [ ! -f "$MANIFEST_FILE" ]; then
        log_warning "Manifest file not found"
        return 1
    fi
    
    log "Listing all bridged binaries:"
    echo ""
    
    while IFS=: read -r source target description; do
        # Skip comments and empty lines
        if echo "$source" | grep -q "^#" || [ -z "$source" ]; then
            continue
        fi
        
        printf "  %-40s -> %-40s\n" "$target" "$source"
        printf "    Description: %s\n" "$description"
        
        # Check status
        if [ -L "$target" ] && [ -e "$source" ]; then
            printf "    Status: ✓ OK\n"
        elif [ -L "$target" ]; then
            printf "    Status: ✗ BROKEN (source missing)\n"
        else
            printf "    Status: ✗ MISSING\n"
        fi
        echo ""
        
    done < "$MANIFEST_FILE"
    
    log "=========================================="
    
    return 0
}

################################################################################
# Main Entry Point
################################################################################

main() {
    case "${1:-status}" in
        setup)
            do_setup
            ;;
        cleanup)
            do_cleanup
            ;;
        status)
            do_status
            ;;
        verify)
            do_verify
            ;;
        list)
            do_list
            ;;
        *)
            echo "Usage: $0 {setup|cleanup|status|verify|list}"
            echo ""
            echo "Commands:"
            echo "  setup   - Create symlink bridge"
            echo "  cleanup - Remove symlink bridge"
            echo "  status  - Show bridge status"
            echo "  verify  - Verify all symlinks are working"
            echo "  list    - List all bridged binaries with details"
            exit 1
            ;;
    esac
    
    return $?
}

# Execute main function
main "$@"
exit $?
