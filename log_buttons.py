import evdev
import os
import time
from select import select

def main():
    devices = []
    for path in os.listdir("/dev/input"):
        if path.startswith("event"):
            try:
                dev = evdev.InputDevice(os.path.join("/dev/input", path))
                devices.append(dev)
            except: pass
            
    with open("/data/rayhunter/buttons.log", "w") as f:
        f.write("Monitoring buttons...\n")
        f.flush()
        
        devices_map = {dev.fd: dev for dev in devices}
        
        start = time.time()
        while time.time() - start < 15: # Run for 15s
            r, w, x = select(devices_map.values(), [], [], 1.0)
            if not r: continue
            for dev in r:
                for event in dev.read():
                    if event.type == evdev.ecodes.EV_KEY:
                        msg = f"Device: {dev.name} | Code: {event.code} | Value: {event.value}\n"
                        f.write(msg)
                        f.flush()

if __name__ == "__main__":
    main()

