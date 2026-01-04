#!/system/bin/sh
set -x # ENABLE VERBOSE LOGGING (Echo all commands)

# ORBIC DEPLOYMENT SCRIPT (HOST SIDE - NATIVE)
# Executed via 'nsenter' from Kali.
# Runs as: ROOT (Magisk)

WORKDIR="/sdcard/ORBIC_DEPLOY"
LOGFILE="$WORKDIR/deploy_native.log"

{
    set -x # ENABLE VERBOSE LOGGING
    
    echo "=========================================="
    echo "STARTING NATIVE DEPLOYMENT $(date)"
    echo "ID: $(id)"
    # echo "CONTEXT: $(ls -Z /proc/self/attr/current)" # Some shells fail this if file missing
    echo "=========================================="

    # 1. DEFINE TARGETS
    TARGET_UI="/data/alpine/root/foac_ui_v6.py"
    TARGET_CORE="/data/alpine/root/foac_core.py"
    TARGET_SVC="/data/rayhunter/start_foac_v2.sh"

    # 2. FLUSH/REMOUNT (Just in case)
    mount -o remount,rw /data

    install_file() {
        SRC="$WORKDIR/$1"
        DEST="$2"
        
        echo "[-] Processing $1..."
        
        if [ ! -f "$SRC" ]; then
            echo "ERROR: Source file not found: $SRC"
            return 1
        fi
        
        # Direct Copy
        cp "$SRC" "$DEST"
        if [ $? -ne 0 ]; then
            echo "ERROR: Copy failed!"
            return 1
        fi
        
        # Permissions
        chmod 755 "$DEST"
        chown 0:0 "$DEST" # Root:Root
        
        # Verify
        LOCAL_SUM=$(md5sum "$SRC" | awk '{print $1}')
        REMOTE_SUM=$(md5sum "$DEST" | awk '{print $1}')
        
        if [ "$LOCAL_SUM" == "$REMOTE_SUM" ]; then
            echo "SUCCESS: $1 Verified ($REMOTE_SUM)"
        else
            echo "CRITICAL FAILURE: Checksum Mismatch!"
            echo "  Local:  $LOCAL_SUM"
            echo "  Remote: $REMOTE_SUM"
            exit 1
        fi
    }

    echo "--- STEP 1: FLASHING FILES ---"
    install_file "foac_ui_v6.py" "$TARGET_UI"
    install_file "foac_core.py" "$TARGET_CORE"
    install_file "start_foac_v2.sh" "$TARGET_SVC"

    echo "--- STEP 2: VERIFICATION COMPLETE ---"
    echo "All files match source. System is ready for reboot."

    echo "--- STEP 3: REBOOT SEQUENCE ---"
    echo "Attempting Graceful Reboot..."
    setprop sys.powerctl reboot
    sleep 3

    echo "Attempting System Binary Reboot..."
    /system/bin/reboot
    sleep 3

    echo "Attempting Panic Reboot (Kill Critical Daemons)..."
    killall -9 cpe_daemon
    killall -9 rayhunter-daemon
    killall -9 rayhunter-daemon.bak
    sleep 2

    echo "Attempting Busybox Reboot..."
    busybox reboot -f
    sleep 2

    echo "Attempting Kernel Panic (SysRq)..."
    echo b > /proc/sysrq-trigger

    echo "If you see this, the device is unkillable."

} 2>&1 | tee -a "$LOGFILE"