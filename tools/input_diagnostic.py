import evdev
import time
import sys
import os
from select import select

def main():
    print("ORBITAL INPUT DIAGNOSTIC")
    print("------------------------")
    print("Scanning for input devices...")
    
    devices = []
    try:
        for path in os.listdir("/dev/input"):
            if path.startswith("event"):
                full_path = os.path.join("/dev/input", path)
                try:
                    dev = evdev.InputDevice(full_path)
                    print(f"FOUND: {full_path} - {dev.name} (Phys: {dev.phys})")
                    print(f"  Capabilities: {dev.capabilities(verbose=True)}")
                    devices.append(dev)
                except Exception as e:
                    print(f"  Error reading {full_path}: {e}")
    except Exception as e:
        print(f"Critical Error scanning /dev/input: {e}")
        return

    if not devices:
        print("No input devices found!")
        return

    print("\nListening for events... (Press CTRL+C to stop)")
    print("Format: [TIMESTAMP] DEV_NAME : TYPE / CODE / VALUE")
    
    devices_map = {dev.fd: dev for dev in devices}
    
    try:
        while True:
            r, w, x = select(devices_map.values(), [], [])
            for dev in r:
                for event in dev.read():
                    # Format timestamp
                    ts = event.timestamp()
                    
                    # Categorize event type
                    ev_type = "UNKNOWN"
                    if event.type == evdev.ecodes.EV_SYN: ev_type = "SYN"
                    elif event.type == evdev.ecodes.EV_KEY: ev_type = "KEY"
                    elif event.type == evdev.ecodes.EV_REL: ev_type = "REL"
                    elif event.type == evdev.ecodes.EV_ABS: ev_type = "ABS"
                    
                    # Only print interesting events (exclude SYN_REPORT for cleanliness unless debugging deep)
                    if event.type != evdev.ecodes.EV_SYN:
                        print(f"[{ts:.6f}] {dev.name:<20} : {ev_type} / Code {event.code} / Val {event.value}")
                        
                        # Highlight specific known keys for the user
                        if event.type == evdev.ecodes.EV_KEY:
                            if event.code == 116: print(f"    -> POWER DETECTED ({event.value})")
                            if event.code == 0x211: print(f"    -> BTN_211 DETECTED ({event.value})") # Common for WPS/Reset

    except KeyboardInterrupt:
        print("\nStopping diagnostic.")

if __name__ == "__main__":
    main()
