import evdev
from select import select

# Device Paths (from our recon)
EVENT_MENU = "/dev/input/event1"
EVENT_POWER = "/dev/input/event2"

def main():
    print(f"Listening on {EVENT_MENU} (Menu) and {EVENT_POWER} (Power)...")
    
    devices = [evdev.InputDevice(EVENT_MENU), evdev.InputDevice(EVENT_POWER)]
    
    # Map devices to names
    dev_map = {
        devices[0].fd: "MENU",
        devices[1].fd: "POWER"
    }

    while True:
        r, w, x = select(devices, [], [])
        for fd in r:
            for event in dev_map[fd].read():
                if event.type == evdev.ecodes.EV_KEY:
                    state = "DOWN" if event.value == 1 else "UP" if event.value == 0 else "HOLD"
                    print(f"Button: {dev_map[fd]} | State: {state} | Code: {event.code}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
