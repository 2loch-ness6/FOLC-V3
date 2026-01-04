import evdev
from select import select
import sys

# Device Paths
EVENT_MENU = "/dev/input/event1"
EVENT_POWER = "/dev/input/event2"

def main():
    print(f"Listening on {EVENT_MENU} (Menu) and {EVENT_POWER} (Power)...")
    sys.stdout.flush()
    
    dev_menu = evdev.InputDevice(EVENT_MENU)
    dev_power = evdev.InputDevice(EVENT_POWER)
    
    devices = {dev_menu.fd: dev_menu, dev_power.fd: dev_power}
    names = {dev_menu.fd: "MENU", dev_power.fd: "POWER"}

    while True:
        r, w, x = select(devices.values(), [], [])
        for dev in r:
            for event in dev.read():
                if event.type == evdev.ecodes.EV_KEY:
                    state = "DOWN" if event.value == 1 else "UP" if event.value == 0 else "HOLD"
                    print(f"Button: {names[dev.fd]} | State: {state} | Code: {event.code}")
                    sys.stdout.flush()

if __name__ == "__main__":
    main()
