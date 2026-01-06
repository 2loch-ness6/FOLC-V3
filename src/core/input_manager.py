import evdev
import time
import threading
import os
from select import select

# Event Codes
KEY_POWER = 116
KEY_WPS   = 0x211 # 529
KEY_RESET = 0x198 # 408 - sometimes generic

class InputEvent:
    """Standardized Event Object"""
    def __init__(self, action, source="UNKNOWN"):
        self.action = action # "SELECT", "NEXT", "BACK", "CONTEXT"
        self.source = source
        self.timestamp = time.time()

class InputManager:
    def __init__(self, callback=None):
        self.running = False
        self.thread = None
        self.callback = callback
        self.devices = []
        
        # Config
        self.long_press_threshold = 0.8 # Seconds
        self.debounce_window = 0.05      # Seconds
        
        # State
        self.power_down_time = 0
        self.power_is_down = False
        self.last_action_time = 0
        
    def start(self):
        """Initializes devices and starts the listener thread."""
        self._scan_devices()
        if not self.devices:
            print("[INPUT] No devices found.")
            return

        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        print("[INPUT] Manager started.")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)

    def _scan_devices(self):
        """Finds all event devices."""
        self.devices = []
        try:
            for path in os.listdir("/dev/input"):
                if path.startswith("event"):
                    try:
                        dev = evdev.InputDevice(os.path.join("/dev/input", path))
                        self.devices.append(dev)
                        print(f"[INPUT] Found: {dev.name}")
                    except Exception as e:
                        print(f"[INPUT] Failed to initialize device '/dev/input/{path}': {e}")
        except Exception as e:
            print(f"[INPUT] Error scanning devices: {e}")

    def _emit(self, action, source):
        """Debounced emit to callback."""
        now = time.time()
        if now - self.last_action_time < self.debounce_window:
            return # Ignore bounce
            
        self.last_action_time = now
        print(f"[INPUT] Emitting: {action} from {source}")
        if self.callback:
            self.callback(InputEvent(action, source))

    def _loop(self):
        """Main event loop."""
        devices_map = {dev.fd: dev for dev in self.devices}
        
        while self.running:
            try:
                r, _, _ = select(devices_map.values(), [], [], 0.5)
                
                if not r: continue

                for dev in r:
                    name = dev.name.lower()
                    is_power = "pon" in name or "power" in name
                    is_aux = "wps" in name or "reset" in name

                    for event in dev.read():
                        if event.type == evdev.ecodes.EV_KEY:
                            self._handle_key(event, is_power, is_aux)
            except Exception as e:
                print(f"[INPUT] Loop Error: {e}")
                time.sleep(1)

    def _handle_key(self, event, is_power, is_aux):
        now = time.time()
        
        # LOGIC: POWER BUTTON
        if is_power or event.code == KEY_POWER:
            if event.value == 1: # DOWN
                # Prevent bounce: only record first DOWN while button is not already pressed
                if not self.power_is_down:
                    # First press
                    self.power_down_time = now
                    self.power_is_down = True
            elif event.value == 0: # UP
                if not self.power_is_down: return # Glitch or startup state
                self.power_is_down = False
                
                duration = now - self.power_down_time
                if duration >= self.long_press_threshold:
                    self._emit("CONTEXT", "POWER_LONG")
                else:
                    self._emit("SELECT", "POWER_SHORT")

        # LOGIC: AUX BUTTONS (WPS / RESET)
        # These buttons can be glitchy or cause reboots.
        # We treat them as "NEXT" (Scroll)
        elif is_aux or event.code in [KEY_WPS, KEY_RESET]:
            if event.value == 1: # DOWN
                # We emit on DOWN for navigation to feel snappy
                self._emit("NEXT", "AUX_BTN")
            
            # NOTE: If the Reset button causes a hardware reboot, 
            # we can't stop it here. But if it's software-handled,
            # consuming the event here *might* prevent the OS from seeing it
            # if we had an exclusive grab (grab=True).
            # Currently we use shared access.
