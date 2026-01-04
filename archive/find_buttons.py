import evdev
import sys
import os
from select import select

def main():
    print("[-] Scanning all /dev/input/event* devices...")
    devices = []
    
    # Auto-discover all input devices
    for f in os.listdir("/dev/input/"):
        if f.startswith("event"):
            path = os.path.join("/dev/input/", f)
            try:
                dev = evdev.InputDevice(path)
                devices.append(dev)
                print(f"[+] Found {path}: {dev.name}")
            except Exception as e:
                print(f"[!] Could not open {path}: {e}")

    if not devices:
        print("[!] No input devices found!")
        return

    print("\n[***] PLEASE PRESS THE TOP BUTTON (MENU) NOW [***]")
    print("[***] Press CTRL+C to stop [***]\n")

    # Mapping fd to device
    fd_to_dev = {dev.fd: dev for dev in devices}

    while True:
        r, w, x = select(devices, [], [])
        for dev in r:
            for event in dev.read():
                if event.type == evdev.ecodes.EV_KEY:
                    # Only show Key Down (1) or Hold (2), ignore Up (0) for clarity
                    if event.value in [1, 2]:
                        state = "DOWN" if event.value == 1 else "HOLD"
                        print(f"!!! DETECTED !!!")
                        print(f"Device: {dev.path} ({dev.name})")
                        print(f"Event:  Code={event.code} ({evdev.ecodes.KEY[event.code] if event.code in evdev.ecodes.KEY else '?'}) State={state}")
                        print("-" * 20)
                        sys.stdout.flush()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting.")
