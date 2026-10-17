#!/usr/bin/env python3
import subprocess
import sys
import os
import time
import atexit
import hashlib
import socket

# Configuration
ADB_BIN = "adb" 
VERBOSE = True 
BACKDOOR_PORT = 9999

# Map local files to device paths
# Note: Local paths are relative to repository root
LOCAL_FILES = {
    "src/ui/folc_ui.py": "/data/alpine/root/folc_ui.py",
    "src/core/folc_core.py": "/data/alpine/root/folc_core.py",
    "tools/start_folc.sh": "/data/rayhunter/start_folc.sh",
    "exploits/wrapper_v4.sh": "/data/rayhunter/wrapper_v4.sh"
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
    # Only kill forward on exit if needed, but we keep it for user convenience usually
    pass

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
    cmd = [ADB_BIN] + args
    
    for attempt in range(retries):
        if VERBOSE:
            log(f"ADB EXEC (Attempt {attempt+1}/{retries}): {' '.join(cmd)}", "CMD")
            
        result = subprocess.run(cmd, capture_output=True, text=(stdin is None), input=stdin)
        
        if VERBOSE:
            if result.stdout:
                log(f"STDOUT: {result.stdout.strip()}", "DBG")
            if result.stderr:
                log(f"STDERR: {result.stderr.strip()}", "DBG")
        
        if result.returncode == 0:
            return result
        
        time.sleep(1)
    
    if check and result.returncode != 0:
        log(f"ADB Command Failed: {' '.join(cmd)}", "ERR")
    return result

def ensure_adb_forward():
    log("Setting up ADB Forwarding...", "INFO")
    run_adb(["forward", f"tcp:{BACKDOOR_PORT}", f"tcp:{BACKDOOR_PORT}"])

def run_root_cmd(cmd_str):
    """
    Executes a command via the device backdoor (port 9999) using a direct socket from Host.
    Uses a one-shot connection: Connect -> Send -> Read All -> Close.
    """
    if VERBOSE:
        log(f"ROOT EXEC (Socket): {cmd_str}", "CMD")

    output = b""
    try:
        with socket.create_connection(("127.0.0.1", BACKDOOR_PORT), timeout=5) as sock:
            # We append "; exit" to ensure the remote shell closes the connection when done.
            # This triggers the socket close on our end, breaking the recv loop naturally.
            sock.sendall(f"{cmd_str}; exit\n".encode())
            
            while True:
                try:
                    chunk = sock.recv(4096)
                    if not chunk: break
                    output += chunk
                except socket.timeout:
                    break
                    
    except ConnectionRefusedError:
        log("Backdoor connection refused! Is the device connected and rooted?", "ERR")
        return None
    except Exception as e:
        log(f"Socket Error: {e}", "ERR")
        return None

    return output.decode(errors='ignore').strip()

def verify_remote_file(remote_path, expected_md5):
    log(f"  > Verifying integrity of {remote_path}...", "DBG")
    out = run_root_cmd(f"md5sum {remote_path}")
    
    if not out:
        log("    > Verification Failed: No output from backdoor", "ERR")
        return False
        
    # Output format: "md5hash  filename"
    remote_hash = out.split()[0]
    
    if remote_hash == expected_md5:
        log(f"    > Checksum MATCH: {remote_hash}", "DBG")
        return True
    else:
        log(f"    > Checksum MISMATCH! Got: {remote_hash}, Expected: {expected_md5}", "ERR")
        return False

def push_file(local_path, remote_path):
    log(f"Deploying {local_path} -> {remote_path}", "INFO")
    
    if not os.path.exists(local_path):
        log(f"Local file not found: {local_path}", "ERR")
        return

    local_md5 = calculate_local_md5(local_path)
    if not local_md5: return
    
    # 1. Check if update is needed (compare MD5)
    # We blindly push if we can't verify, or if hash differs
    if verify_remote_file(remote_path, local_md5):
        log("    > File is up to date. Skipping.", "INFO")
        return

    # 2. Push to temp via ADB PUSH (Fast & Reliable)
    # Note: ADB Push goes to /data/local/tmp/
    filename = os.path.basename(local_path)
    tmp_path = f"/data/local/tmp/{filename}"
    
    log(f"  > Pushing to {tmp_path}...", "DBG")
    res = run_adb(["push", local_path, tmp_path])
    
    if res.returncode == 0:
        log(f"  > Moving to destination (ROOT)...", "DBG")
        # Move and Chmod via Backdoor
        cmd = f"cp {tmp_path} {remote_path} && chmod 755 {remote_path} && rm {tmp_path}"
        run_root_cmd(cmd)
        
        # Verify
        if verify_remote_file(remote_path, local_md5):
             log(f"SUCCESS: {remote_path} (Verified)", "INFO")
        else:
             log(f"FAILED: Validation failed for {remote_path}", "ERR")
    else:
        log("FAILED during adb push", "ERR")

def wait_for_device():
    log("Waiting for device connection...", "INFO")
    while True:
        res = run_adb(["devices"], check=False, retries=1)
        output = res.stdout.strip() if res.stdout else ""
        if "\tdevice" in output:
            log(f"Device found.", "INFO")
            ensure_adb_forward()
            return
        time.sleep(3)

def hard_reboot():
    # Only if requested
    pass

def flash_files():
    log("Starting Sync Process...", "INFO")
    ensure_adb_forward()
    for local, remote in LOCAL_FILES.items():
        push_file(local, remote)

def verify_installation():
    log("Verifying Installation...", "INFO")
    ensure_adb_forward()
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
    if "--shell" in sys.argv:
        log("::: ORBIC ROOT SHELL (Socket) :::", "WARN")
        wait_for_device()
        try:
            while True:
                cmd = input("# ")
                if cmd == "exit": break
                print(run_root_cmd(cmd))
        except KeyboardInterrupt:
            print("\nExiting.")
        return

    log("::: ORBIC MANAGER v7.0 (Socket Edition) :::", "INFO")
    
    wait_for_device()
    
    log("--- STEP 1: SYNC FILES ---", "WARN")
    flash_files()
    
    log("--- STEP 2: FINAL VERIFICATION ---", "WARN")
    if verify_installation():
        log("✓ UPDATE SUCCESSFUL", "INFO")
        log("Rebooting device to apply changes...", "WARN")
        run_root_cmd("/sbin/reboot")
    else:
        log("X UPDATE FAILED CHECK", "ERR")
        sys.exit(1)

if __name__ == "__main__":
    main()
