#!/usr/bin/env python3
import subprocess
import sys
import os
import time
import atexit
import hashlib

# Configuration
# We use the HOST ADB binary via nsenter to ensure connection stability
# and avoid conflicts between container/host adb servers.
ADB_BIN = "nsenter -t 1 -m /bin/adb" 
VERBOSE = True 

# Map local files to device paths
# Note: Local paths are relative to repository root
LOCAL_FILES = {
    "src/ui/foac_ui_v6.py": "/data/alpine/root/foac_ui_v6.py",
    "src/core/foac_core.py": "/data/alpine/root/foac_core.py",
    "tools/start_foac_v2.sh": "/data/rayhunter/start_foac_v2.sh"
}

def log(msg, level="INFO"):
    colors = {
        "INFO": "\033[97m", # White
        "WARN": "\033[93m", # Yellow
        "ERR":  "\033[91m", # Red
        "CMD":  "\033[96m", # Cyan
        "DBG":  "\033[90m", # Gray
        "END":  "\033[0m"
    }
    color = colors.get(level, colors["INFO"])
    print(f"{color}[{level}] {msg}{colors['END']}")

def cleanup():
    log("Cleaning up ADB Bridge...", "INFO")
    
    # 1. Kill Container ADB (if any)
    subprocess.run(["pkill", "adb"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # 2. Kill Host ADB Server (The big hammer)
    try:
        # Kill process directly on host
        subprocess.run(["nsenter", "-t", "1", "-m", "pkill", "adb"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # Polite kill
        cmd = ADB_BIN.split() + ["kill-server"]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except: pass
    
    log("ADB Cleanup Complete.", "INFO")

def calculate_local_md5(file_path):
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        log(f"Hashing Error: {e}", "ERR")
        return None

def run_adb(args, check=True, stdin=None, retries=3):
    # Split ADB_BIN correctly
    cmd = ADB_BIN.split() + args
    
    for attempt in range(retries):
        if VERBOSE:
            log(f"EXEC (Attempt {attempt+1}/{retries}): {' '.join(cmd)}", "CMD")
            
        result = subprocess.run(cmd, capture_output=True, text=(stdin is None), input=stdin)
        
        if VERBOSE:
            if result.stdout:
                log(f"STDOUT: {result.stdout.strip()}", "DBG")
            if result.stderr:
                log(f"STDERR: {result.stderr.strip()}", "DBG")
        
        # ADB is flaky. If it returns 0, great.
        if result.returncode == 0:
            return result
        
        # If not, wait and retry
        time.sleep(1)
    
    if check and result.returncode != 0:
        log(f"Command Failed after {retries} attempts: {' '.join(cmd)}", "ERR")
        log(f"Stderr: {result.stderr}", "ERR")
    return result

def revive_backdoor():
    log("Reviving 'Real Root' Backdoor (via SUID)...", "WARN")
    cmd = "nohup /bin/busybox nc -ll -p 9999 -e /bin/sh >/dev/null 2>&1 &"
    safe_cmd = cmd.replace("'", "'\\''")
    adb_args = ["shell", f"echo '{safe_cmd}' | /bin/rootshell"]
    run_adb(adb_args, check=False)
    time.sleep(2)

def run_root_cmd(cmd_str):
    safe_cmd = cmd_str.replace("'", "'\\''")
    
    # Attempt 1: Direct Netcat (Host -> Device Port 9999)
    # We must pipe into nc on the device because we are using nsenter (Host context)
    # Host ADB -> ADB Shell -> echo | nc localhost 9999
    adb_args = ["shell", f"echo '{safe_cmd}' | nc -w 2 127.0.0.1 9999"]
    
    if VERBOSE:
        log(f"ROOT EXEC: {cmd_str}", "CMD")
        
    res = run_adb(adb_args, check=False)
    
    err_out = res.stderr or ""
    if "Connection refused" in err_out or "can't connect" in (res.stdout or ""):
        log("Backdoor unreachable. Attempting revive...", "WARN")
        revive_backdoor()
        return run_adb(adb_args, check=False)
        
    return res

def verify_remote_file(remote_path, expected_md5):
    log(f"  > Verifying integrity of {remote_path}...", "DBG")
    res = run_root_cmd(f"md5sum {remote_path}")
    output = res.stdout.strip() if res.stdout else ""
    
    if not output or len(output.split()) < 1:
        log("    > Verification Failed: No output from md5sum", "ERR")
        return False
        
    remote_hash = output.split()[0]
    if remote_hash == expected_md5:
        log(f"    > Checksum MATCH: {remote_hash}", "DBG")
        return True
    else:
        log(f"    > Checksum MISMATCH!", "ERR")
        return False

def push_file(local_path, remote_path):
    log(f"Deploying {local_path} -> {remote_path}", "INFO")
    
    if not os.path.exists(local_path):
        log(f"Local file not found: {local_path}", "ERR")
        return

    local_md5 = calculate_local_md5(local_path)
    if not local_md5: return

    # 2. Push to temp via STREAM (Host ADB cannot see Container files directly)
    # We read local file in Python (Container), pipe to ADB (Host) -> Shell (Device)
    tmp_path = f"/data/local/tmp/{os.path.basename(local_path)}"
    log(f"  > Streaming to {tmp_path} (Host Bridge)...", "DBG")
    
    try:
        with open(local_path, 'rb') as f:
            content = f.read()
    except:
        return

    # adb shell "cat > remote"
    res = run_adb(["shell", f"cat > {tmp_path}"], stdin=content)
    
    if res.returncode == 0:
        log(f"  > Installing to destination (ROOT)...", "DBG")
        # Copy from tmp to final, chmod, remove tmp
        root_op = f"cat {tmp_path} > {remote_path} && chmod +x {remote_path} && rm {tmp_path}"
        run_root_cmd(root_op)
        
        # Verify
        if verify_remote_file(remote_path, local_md5):
             log(f"SUCCESS: {remote_path} (Verified)", "INFO")
        else:
             log(f"FAILED: Validation failed for {remote_path}", "ERR")
    else:
        log("FAILED during stream push", "ERR")

def wait_for_device():
    log("Waiting for device connection...", "INFO")
    while True:
        # Check connection using Host ADB
        res = run_adb(["devices"], check=False, retries=1)
        output = res.stdout.strip() if res.stdout else ""
        if "\tdevice" in output:
            log(f"Device found.", "INFO")
            return
        time.sleep(3)

def hard_reboot():
    log("Hard Rebooting device (ROOT)...", "WARN")
    
    reboot_cmds = [
        "/sbin/reboot",
        "busybox reboot -f",
        "killall -9 cpe_daemon" # The Panic Button
    ]
    
    for cmd in reboot_cmds:
        log(f"  > Attempting: {cmd}", "DBG")
        run_root_cmd(cmd)
        time.sleep(2)
        res = run_adb(["devices"], check=False)
        if "\tdevice" not in (res.stdout or ""):
            log("  > Device went offline.", "INFO")
            break
    
    log("Waiting for device to go offline...", "INFO")
    time.sleep(5)
    wait_for_device()
    time.sleep(10)

def flash_files():
    log("Starting Flash Process...", "INFO")
    for local, remote in LOCAL_FILES.items():
        push_file(local, remote)

def verify_installation():
    log("Verifying Installation...", "INFO")
    all_good = True
    for local, remote in LOCAL_FILES.items():
        local_md5 = calculate_local_md5(local)
        if verify_remote_file(remote, local_md5):
            log(f"  [✓] {os.path.basename(remote)}: MATCH", "INFO")
        else:
            log(f"  [X] {os.path.basename(remote)}: MISMATCH", "ERR")
            all_good = False
    return all_good

def main():
    cleanup() # Initial aggressive cleanup
    atexit.register(cleanup)
    
    if "--shell" in sys.argv:
        log("::: ORBIC ROOT SHELL (Host Bridge) :::", "WARN")
        wait_for_device()
        run_adb(["forward", "tcp:9999", "tcp:9999"])
        log("Connecting to Backdoor...", "INFO")
        # Use Host NC if possible, or container NC?
        # Container NC -> Host Port 9999 (mapped via adb forward)
        # localhost in container != localhost on host.
        # ADB forward binds to Host Localhost.
        # We need to access Host Localhost.
        # This is tricky. simpler to use interactive shell via ADB
        subprocess.run(ADB_BIN.split() + ["shell", "/bin/rootshell"])
        return

    log("::: ORBIC MANAGER v6.0 (Host Stability) :::", "INFO")
    
    log("--- STEP 1: INITIAL REBOOT ---", "WARN")
    wait_for_device()
    hard_reboot()
    
    log("--- STEP 2: FLASHING UPDATES ---", "WARN")
    flash_files()
    
    log("--- STEP 3: POST-FLASH REBOOT ---", "WARN")
    hard_reboot()
    
    log("--- STEP 4: VERIFICATION ---", "WARN")
    if verify_installation():
        log("✓ UPDATE SUCCESSFUL", "INFO")
    else:
        log("X UPDATE FAILED CHECK", "ERR")
        sys.exit(1)

if __name__ == "__main__":
    main()