import evdev
import struct
import time
import subprocess
import threading
import sys
import os
import signal
from select import select
from PIL import Image, ImageDraw, ImageFont

# Import functional core
try:
    import foac_core
    WIFI = foac_core.WirelessTool("wlan0")
except ImportError:
    WIFI = None

# --- CONFIG ---
FB_PATH = "/dev/fb0"
WIDTH = 128
HEIGHT = 128

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)
GRAY = (50, 50, 50)

# Input Config
CODE_POWER = 116
DEBOUNCE_DELAY = 0.3

def draw_fb(image):
    pixels = image.load()
    try:
        with open(FB_PATH, "wb") as fb:
            data = bytearray()
            for y in range(HEIGHT):
                for x in range(WIDTH):
                    r, g, b = pixels[x, y]
                    # RGB888 -> RGB565
                    val = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                    data.extend(struct.pack("<H", val))
            fb.write(data)
    except: pass

class UI:
    def __init__(self):
        self.menu_items = ["SCAN FREQUENCIES", "PACKET HARVEST", "DEAUTH PULSE", "REBOOT"]
        self.current_idx = 0
        self.state = "MENU" 
        self.results = [] # List of (SSID, BSSID, Signal)
        self.target = None # (SSID, BSSID)
        self.status_msg = "READY"
        self.scan_idx = 0
        self.scanning_thread = None
        self.stop_scan_event = threading.Event()  # Thread-safe flag
        self.state_lock = threading.Lock()  # Protects state transitions

    def cleanup(self):
        """Clean up resources, especially threads"""
        if self.scanning_thread and self.scanning_thread.is_alive():
            self.stop_scan_event.set()
            self.scanning_thread.join(timeout=2.0)
            # Check if thread actually terminated
            if self.scanning_thread.is_alive():
                # Thread didn't terminate - log to stderr
                print("WARNING: Scanning thread did not terminate within timeout", file=sys.stderr)
        self.scanning_thread = None

    def context_menu(self):
        # Triggered by Long Press Power
        if self.state == "RESULT" and self.results:
            self.state = "CONTEXT"
            self.status_msg = "DETAILS"
        elif self.state == "MENU":
            self.state = "CONTEXT"
            self.status_msg = "SYS INFO"
        self.draw()

    def draw(self):
        img = Image.new("RGB", (WIDTH, HEIGHT), BLACK)
        draw = ImageDraw.Draw(img)
        
        # Header
        header_color = RED
        if self.state == "PULSING": header_color = ORANGE
        if self.state == "CONTEXT": header_color = CYAN
        
        draw.rectangle((0, 0, WIDTH, 18), fill=header_color)
        draw.text((5, 4), "ORBITAL CANNON v2", fill=BLACK)
        
        status_color = GREEN
        if "SCAN" in self.status_msg: status_color = CYAN
        if "ERR" in self.status_msg or "NO TGT" in self.status_msg: status_color = RED
        if "ABORTED" in self.status_msg: status_color = ORANGE
        
        draw.text((5, 22), f"STA: {self.status_msg}", fill=status_color)
        
        # Target Info
        tgt_text = "TGT: NONE"
        if self.target:
            tgt_text = f"TGT: {self.target[0][:10]}"
        draw.text((5, HEIGHT-12), tgt_text, fill=ORANGE)

        if self.state == "MENU":
            y = 38
            for i, item in enumerate(self.menu_items):
                color = WHITE
                prefix = " "
                if i == self.current_idx:
                    color = ORANGE
                    prefix = ">"
                    draw.rectangle((0, y-1, WIDTH, y+11), fill=(30, 30, 30))
                draw.text((10, y), f"{prefix} {item}", fill=color)
                y += 18

        elif self.state == "SCANNING":
            draw.text((20, 50), "SCANNING...", fill=CYAN)
            draw.text((20, 65), "PLEASE WAIT", fill=WHITE)
            draw.text((20, 80), "PWR TO ABORT", fill=RED)
            
        elif self.state == "RESULT":
            draw.text((5, 38), f"FOUND: {len(self.results)}", fill=CYAN)
            y = 52
            if not self.results:
                draw.text((10, y), "NONE DETECTED", fill=RED)
            else:
                # Show 4 items, centered around scan_idx
                start_i = 0
                if self.scan_idx > 3:
                    start_i = self.scan_idx - 3
                
                visible_results = self.results[start_i : start_i+4]
                
                for i, (ssid, bssid, sig) in enumerate(visible_results):
                    actual_idx = start_i + i
                    color = WHITE
                    prefix = " "
                    if actual_idx == self.scan_idx:
                        color = ORANGE
                        prefix = ">"
                        draw.rectangle((0, y-1, WIDTH, y+11), fill=(30, 30, 30))
                    
                    draw.text((10, y), f"{prefix}{sig} {ssid[:8]}", fill=color)
                    y += 14

        elif self.state == "CONTEXT":
            # Detail View
            if "SYS" in self.status_msg:
                draw.text((5, 40), "SYSTEM INFO:", fill=WHITE)
                draw.text((5, 55), "Orbic Speed 5G", fill=GRAY)
                draw.text((5, 70), "Rooted: YES", fill=GREEN)
                draw.text((5, 85), "Hold PWR: Back", fill=ORANGE)
            elif "DETAILS" in self.status_msg and self.results:
                # Show full details of selected network
                ssid, bssid, sig = self.results[self.scan_idx]
                draw.text((5, 40), f"SSID: {ssid[:12]}", fill=WHITE)
                draw.text((5, 55), f"MAC: {bssid}", fill=GRAY)
                draw.text((5, 70), f"SIG: {sig}", fill=CYAN)
                draw.text((5, 85), "Hold PWR: Back", fill=ORANGE)

        draw_fb(img)

    def next(self):
        if self.state == "MENU":
            self.current_idx = (self.current_idx + 1) % len(self.menu_items)
        elif self.state == "RESULT":
            if self.results:
                self.scan_idx = (self.scan_idx + 1) % len(self.results)
        self.draw()

    def _scan_task(self):
        results = []
        if WIFI:
            results = WIFI.scan_networks()
        else:
            time.sleep(2) # Mock
            results = [("DEMO_NET", "00:11:22:33:44:55", "-50")]
        
        # Only update if not aborted
        if not self.stop_scan_event.is_set():
            with self.state_lock:
                self.results = results
                self.scan_idx = 0
                self.state = "RESULT"
                self.status_msg = "SELECT TGT"
                self.scanning_thread = None
            self.draw()

    def cancel_scan(self):
        if self.state == "SCANNING":
            # Delegate thread cleanup to the shared cleanup routine
            self.cleanup()
            self.state = "MENU"
            self.status_msg = "ABORTED"
            self.draw()

    def select(self):
        if self.state == "MENU":
            item = self.menu_items[self.current_idx]
            
            if item == "SCAN FREQUENCIES":
                self.state = "SCANNING"
                self.status_msg = "SCANNING"
                self.stop_scan_event.clear()  # Reset event for new scan
                self.draw()
                # Start Thread
                self.scanning_thread = threading.Thread(target=self._scan_task)
                self.scanning_thread.start()
            
            elif item == "PACKET HARVEST":
                self.status_msg = "SNIFFING..."
                self.draw()
                if WIFI:
                    WIFI.packet_sniff(duration=5)
                time.sleep(1)
                self.status_msg = "CAPTURED"
            
            elif item == "DEAUTH PULSE":
                if not self.target:
                    self.status_msg = "NO TARGET!"
                else:
                    self.state = "PULSING"
                    self.status_msg = "FIRE: " + self.target[0][:5]
                    self.draw()
                    if WIFI:
                        WIFI.deauth(self.target[1], count=10)
                    else:
                        time.sleep(2)
                    self.state = "MENU"
                    self.status_msg = "ATTACK SENT"
            
            elif item == "REBOOT":
                self.status_msg = "REBOOTING..."
                self.draw()
                subprocess.run(["reboot"])

        elif self.state == "SCANNING":
            # POWER BUTTON in SCANNING = CANCEL
            self.cancel_scan()

        elif self.state == "RESULT":
            # User selected a network from result list
            if self.results:
                selected = self.results[self.scan_idx]
                self.target = (selected[0], selected[1]) # SSID, BSSID
                self.status_msg = f"TGT: {selected[0][:6]}"
            self.state = "MENU"
        
        elif self.state == "CONTEXT":
            self.state = "MENU"
            if self.results: self.state = "RESULT"
            self.status_msg = "READY"
        
        self.draw()

    def back(self):
        if self.state == "SCANNING":
            self.cancel_scan()
        else:
            self.state = "MENU"
            self.status_msg = "READY"
            self.draw()

def main():
    ui = UI()
    ui.draw()
    
    # Signals are handled by default; cleanup is performed by the main loop's
    # normal control flow and any associated finally blocks.
    
    # Auto-detect all input devices
    devices = []
    try:
        for path in os.listdir("/dev/input"):
            if path.startswith("event"):
                try:
                    dev = evdev.InputDevice(os.path.join("/dev/input", path))
                    devices.append(dev)
                except: pass
    except: pass

    if not devices:
        return

    # Input Loop
    devices_map = {dev.fd: dev for dev in devices}
    last_press_time = 0
    power_down_time = 0
    
    try:
        while True:
            r, w, x = select(devices_map.values(), [], [], 0.5) # Timeout 0.5s to refresh
            
            # Check thread health - auto-transition if scan completed
            if ui.state == "SCANNING" and ui.scanning_thread and not ui.scanning_thread.is_alive():
                # Thread finished but state wasn't updated. This can occur if:
                # 1. Hardware scan completes but _scan_task crashes before updating state
                # 2. Thread completes during the select() timeout window
                # Join the thread to ensure all state updates are complete
                ui.scanning_thread.join(timeout=0.5)
                # Use lock to safely check state after thread completion
                with ui.state_lock:
                    # Only transition if _scan_task didn't already update state
                    if ui.state == "SCANNING":
                        ui.scanning_thread = None
                        ui.stop_scan_event.clear()  # Reset event for future scans
                        # Check if results were populated before transitioning state
                        if ui.results:
                            ui.state = "RESULT"
                            ui.status_msg = "SELECT TGT"
                        else:
                            ui.state = "MENU"
                            ui.status_msg = "SCAN DONE"
                        ui.draw()

            if not r: continue

            for dev in r:
                dev_name = dev.name.lower()
                is_power = "pon" in dev_name or "powerkey" in dev_name
                is_bumper = "wps" in dev_name or "reset" in dev_name
                
                for event in dev.read():
                    if event.type == evdev.ecodes.EV_KEY:
                        now = time.time()
                        
                        if is_power:
                            if event.value == 1: # Down
                                power_down_time = now
                            elif event.value == 0: # Up
                                duration = now - power_down_time
                                # Ignore extremely short glitches
                                if duration < 0.05: continue
                                
                                if duration >= 0.8:
                                    # LONG PRESS
                                    ui.context_menu()
                                else:
                                    # SHORT CLICK
                                    if ui.state == "SCANNING":
                                        ui.cancel_scan()
                                    else:
                                        ui.select()
                        elif is_bumper:
                            # Logic for Bumper (Scroll) - Trigger on Press
                            if event.value == 1:
                                if now - last_press_time < DEBOUNCE_DELAY: continue
                                last_press_time = now
                                
                                if ui.state == "SCANNING":
                                    ui.cancel_scan()
                                else:
                                    ui.next()
                        else:
                            # Unknown button, log it or ignore
                            pass
    finally:
        ui.cleanup()

if __name__ == "__main__":
    main()