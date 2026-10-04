#!/bin/sh
########################################################################
# HOST BRIDGE - Deep host integration for Alpine chroot
#
# Bind-mounts the host root filesystem into the Alpine chroot at /host,
# then creates transparent wrapper scripts so host-native binaries
# (QMI tools, diag tools, modem utilities) can be called by name
# from inside the chroot using the host's glibc dynamic linker.
#
# Usage:
#   host_bridge.sh setup   - Mount host and create wrappers
#   host_bridge.sh teardown - Unmount and clean up
#   host_bridge.sh status  - Check bridge status
#
# Designed to run ON-DEVICE with full capabilities (via backdoor/wrapper)
########################################################################

ALPINE="/data/alpine"
HOST_MOUNT="$ALPINE/host"
WRAPPER_DIR="$ALPINE/usr/local/bin"
HOST_LINKER="/host/lib/ld-linux.so.3"
LOG="/data/rayhunter/host_bridge.log"

log() {
    echo "[$(date '+%H:%M:%S')] $1" | tee -a "$LOG"
}

# Host binaries we want transparent access to
MODEM_TOOLS="
qmi_simple_ril_test
qmi_shutdown_modem
qmi_ip_multiclient
qmi_test_service_test
rmnetcli
mbimd
atfwd_daemon
cpe_daemon
cpe_route
dialup
sms
wireless_net
statistics
thermal-engine
diag_mdlog
diag_dci_sample
diag_callback_sample
diag_klog
diag_socket_log
diag_uart_log
diagrebootapp
test_diag
netmgrd
qti
QCMAP_ConnectionManager
logcat
"

SBIN_TOOLS="
iptables
ip6tables
ebtables
ethtool
brctl
bridge
chroot
"

setup_mounts() {
    log "Setting up host bridge mounts..."

    mkdir -p "$HOST_MOUNT"

    if mount | grep -q "$HOST_MOUNT"; then
        log "Host already mounted at $HOST_MOUNT"
    else
        mount -o bind,ro / "$HOST_MOUNT"
        if [ $? -eq 0 ]; then
            log "Mounted host root at $HOST_MOUNT (read-only)"
        else
            log "ERROR: Failed to mount host root"
            return 1
        fi
    fi

    # /data is already bind-mounted by wrapper_v4 but ensure /host sees it too
    mkdir -p "$HOST_MOUNT/data"
    if ! mount | grep -q "$HOST_MOUNT/data"; then
        mount -o bind /data "$HOST_MOUNT/data" 2>/dev/null
    fi

    # Ensure /dev is consistent (already mounted by wrapper_v4)
    if ! mount | grep -q "$ALPINE/dev "; then
        mount -o bind /dev "$ALPINE/dev"
    fi

    log "Host mounts ready"
}

create_wrapper() {
    local bin_name="$1"
    local host_path="$2"
    local wrapper="$WRAPPER_DIR/host-$bin_name"

    if [ ! -f "$ALPINE$host_path" ]; then
        return 1
    fi

    cat > "$wrapper" << WRAPPER_EOF
#!/bin/sh
exec $HOST_LINKER --library-path /host/lib:/host/usr/lib $host_path "\$@"
WRAPPER_EOF
    chmod 755 "$wrapper"

    # Also create a direct-name symlink if it doesn't shadow an Alpine binary
    if [ ! -f "$WRAPPER_DIR/$bin_name" ] && [ ! -f "$ALPINE/usr/bin/$bin_name" ] && [ ! -f "$ALPINE/bin/$bin_name" ]; then
        ln -sf "host-$bin_name" "$WRAPPER_DIR/$bin_name"
    fi

    return 0
}

setup_wrappers() {
    log "Creating host binary wrappers..."
    mkdir -p "$WRAPPER_DIR"

    local count=0

    for tool in $MODEM_TOOLS; do
        if create_wrapper "$tool" "/host/usr/bin/$tool"; then
            count=$((count + 1))
        fi
    done

    for tool in $SBIN_TOOLS; do
        if create_wrapper "$tool" "/host/sbin/$tool"; then
            count=$((count + 1))
        elif create_wrapper "$tool" "/host/usr/sbin/$tool"; then
            count=$((count + 1))
        fi
    done

    # AT command helper — uses single r/w fd on /dev/smd11
    cat > "$WRAPPER_DIR/at" << 'AT_EOF'
#!/bin/sh
CMD="${*:-AT}"
T="${AT_TIMEOUT:-2}"
exec 3<>/dev/smd11
printf '%s\r' "$CMD" >&3
sleep "$T"
timeout 1 cat <&3 2>/dev/null
exec 3>&-
AT_EOF
    chmod 755 "$WRAPPER_DIR/at"

    # Batch AT command tool
    cat > "$WRAPPER_DIR/at-batch" << 'ATBATCH_EOF'
#!/bin/sh
T="${AT_TIMEOUT:-2}"
exec 3<>/dev/smd11
if [ $# -gt 0 ]; then
    for cmd in "$@"; do
        printf '%s\r' "$cmd" >&3
        sleep "$T"
    done
else
    while IFS= read -r cmd; do
        printf '%s\r' "$cmd" >&3
        sleep "$T"
    done
fi
timeout 1 cat <&3 2>/dev/null
exec 3>&-
ATBATCH_EOF
    chmod 755 "$WRAPPER_DIR/at-batch"

    # Create a diag helper
    cat > "$WRAPPER_DIR/modem-diag" << 'DIAG_EOF'
#!/bin/sh
# Quick modem diagnostics
# Usage: modem-diag [info|signal|cell|sim|all]
MODE="${1:-all}"
case "$MODE" in
    info)
        at "ATI"
        ;;
    signal)
        at "AT+CSQ"
        ;;
    cell)
        at-batch "AT+COPS?" "AT+CREG?" "AT+CEREG?"
        ;;
    sim)
        at-batch "AT+CPIN?" "AT+CIMI" "AT+CCID"
        ;;
    all)
        at-batch "ATI" "AT+CFUN?" "AT+CPIN?" "AT+CSQ" "AT+COPS?" "AT+CREG?" "AT+CEREG?" "AT+CGDCONT?"
        ;;
    *)
        echo "Usage: modem-diag [info|signal|cell|sim|all]"
        ;;
esac
DIAG_EOF
    chmod 755 "$WRAPPER_DIR/modem-diag"

    log "Created $count host binary wrappers + AT/diag helpers"
}

setup_env() {
    log "Setting up environment integration..."

    # Ensure /usr/local/bin is in PATH for all sessions (including non-login SSH)
    if ! grep -q '/usr/local/bin' "$ALPINE/etc/profile" 2>/dev/null; then
        echo 'export PATH="/usr/local/bin:$PATH"' >> "$ALPINE/etc/profile"
    fi

    # Set default ENV for non-login shells (ash reads $ENV on startup)
    cat > "$ALPINE/etc/environment" << 'BASEENV_EOF'
export PATH="/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
BASEENV_EOF

    # Dropbear sets ENV for non-login shells — ensure it sources our env
    if ! grep -q 'ENV=' "$ALPINE/etc/profile" 2>/dev/null; then
        echo 'export ENV="/etc/environment"' >> "$ALPINE/etc/profile"
    fi

    # Create /etc/profile.d script for seamless PATH integration
    mkdir -p "$ALPINE/etc/profile.d"
    cat > "$ALPINE/etc/profile.d/host_bridge.sh" << 'ENV_EOF'
# Host Bridge: transparent access to host-native modem/system tools
export HOST_ROOT="/host"
export HOST_LINKER="/host/lib/ld-linux.so.3"
export PATH="/usr/local/bin:$PATH"

hostexec() {
    local bin="$1"; shift
    $HOST_LINKER --library-path /host/lib:/host/usr/lib "$bin" "$@"
}

alias host-shell='hostexec /host/bin/sh'
alias host-busybox='hostexec /host/bin/busybox'
alias qmi-ril='host-qmi_simple_ril_test'
alias diag-log='host-diag_mdlog'
alias diag-dci='host-diag_dci_sample'
ENV_EOF
    chmod 644 "$ALPINE/etc/profile.d/host_bridge.sh"

    log "Environment integration complete"
}

do_setup() {
    log "=== HOST BRIDGE SETUP ==="
    setup_mounts || return 1
    setup_wrappers
    setup_env
    log "=== HOST BRIDGE READY ==="
    log "Access host tools via: host-<toolname> (e.g., host-qmi_simple_ril_test)"
    log "AT commands via: at 'AT+CSQ' or modem-diag all"
    log "Run any host binary: hostexec /host/usr/bin/<binary>"
}

do_teardown() {
    log "=== HOST BRIDGE TEARDOWN ==="

    # Remove wrappers
    rm -f "$WRAPPER_DIR"/host-* 2>/dev/null
    rm -f "$WRAPPER_DIR/at" "$WRAPPER_DIR/at-batch" "$WRAPPER_DIR/modem-diag" 2>/dev/null
    rm -f "$ALPINE/etc/profile.d/host_bridge.sh" 2>/dev/null

    # Remove symlinks we created (only ones pointing to host-*)
    for f in "$WRAPPER_DIR"/*; do
        if [ -L "$f" ]; then
            target=$(readlink "$f")
            case "$target" in host-*) rm -f "$f" ;; esac
        fi
    done

    # Unmount
    umount "$HOST_MOUNT/data" 2>/dev/null
    umount "$HOST_MOUNT" 2>/dev/null

    log "Host bridge torn down"
}

do_status() {
    echo "========================================"
    echo "Host Bridge Status"
    echo "========================================"
    echo ""
    echo "Host Mount:"
    if mount | grep -q "$HOST_MOUNT"; then
        echo "  MOUNTED at $HOST_MOUNT"
        echo "  Host kernel: $(cat $HOST_MOUNT/proc/version 2>/dev/null | head -c 60)"
    else
        echo "  NOT MOUNTED"
    fi
    echo ""
    echo "Wrappers:"
    wcount=$(ls "$WRAPPER_DIR"/host-* 2>/dev/null | wc -l)
    echo "  $wcount host binary wrappers installed"
    ls "$WRAPPER_DIR"/host-* 2>/dev/null | while read f; do
        echo "    $(basename $f)"
    done
    echo ""
    echo "AT Helper:"
    [ -x "$WRAPPER_DIR/at" ] && echo "  INSTALLED" || echo "  NOT INSTALLED"
    echo ""
    echo "Environment:"
    [ -f "$ALPINE/etc/profile.d/host_bridge.sh" ] && echo "  INSTALLED" || echo "  NOT INSTALLED"
    echo "========================================"
}

case "$1" in
    setup)   do_setup ;;
    teardown) do_teardown ;;
    status)  do_status ;;
    *)
        echo "Usage: $0 {setup|teardown|status}"
        exit 1
        ;;
esac
