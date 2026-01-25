import struct
import time
import subprocess
import threading
import sys
import os
import signal
import evdev
from select import select
from PIL import Image, ImageDraw, ImageFont

# Import functional core
try:
    import folc_core
    from input_manager import InputManager
    
    WIFI = folc_core.WirelessTool("wlan0")
    CELL = folc_core.CellularTool("rmnet_data0")
    INPUT = InputManager()
except ImportError as e:
    print(f"Import Error: {e}")
    WIFI = None
    CELL = None
    INPUT = None

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
        self.root_items = ["POWER", "SETTINGS", "TOOLS", "AutoIOT"]
        self.autoiot_items = ["ANALYSIS", "MAPPING", "METRICS", "VECTORS", "PAYLOADS", "CC"]
        self.menu_items = self.root_items
        self.current_idx = 0
        self.state = "MENU" # MENU, AUTO_IOT, SCANNING, RESULT, CONTEXT
        self.results = [] # List of (SSID, BSSID, Signal)
        self.target = None # (SSID, BSSID)
        self.status_msg = "READY"
        self.scan_idx = 0
        self.scanning_thread = None
        self.stop_scan_event = threading.Event()
        self.state_lock = threading.Lock()

    def cleanup(self):
        """Clean up resources, especially threads"""
        if self.scanning_thread and self.scanning_thread.is_alive():
            self.stop_scan_event.set()
            self.scanning_thread.join(timeout=2.0)
            if self.scanning_thread.is_alive():
                print("WARNING: Scanning thread did not terminate within timeout", file=sys.stderr)
        self.scanning_thread = None

    def context_menu(self):
        # Triggered by Long Press Power
        if self.state == "RESULT" and self.results:
            self.state = "CONTEXT"
            self.status_msg = "DETAILS"
        elif self.state in ["MENU", "AUTO_IOT"]:
            self.state = "CONTEXT"
            self.status_msg = "SYS INFO"
        self.draw()

    def draw(self):
        img = Image.new("RGB", (WIDTH, HEIGHT), BLACK)
        draw = ImageDraw.Draw(img)
        
        # Header
        header_color = RED
        if self.state == "AUTO_IOT": header_color = ORANGE
        if self.state == "CONTEXT": header_color = CYAN
        
        draw.rectangle((0, 0, WIDTH, 18), fill=header_color)
        draw.text((5, 4), "FOLC Field Op", fill=BLACK)
        
        status_color = GREEN
        if "SCAN" in self.status_msg or "ANALYZ" in self.status_msg: status_color = CYAN
        
        draw.text((5, 22), f"STA: {self.status_msg}", fill=status_color)
        
        # Target Info
        tgt_text = "TGT: NONE"
        if self.target:
            tgt_text = f"TGT: {self.target[0][:10]}"
        draw.text((5, HEIGHT-12), tgt_text, fill=ORANGE)

        if self.state in ["MENU", "AUTO_IOT"]:
            y = 38
            for i, item in enumerate(self.menu_items):
                color = WHITE
                prefix = " "
                if i == self.current_idx:
                    color = ORANGE
                    prefix = ">"
                    draw.rectangle((0, y-1, WIDTH, y+11), fill=(30, 30, 30))
                draw.text((10, y), f"{prefix} {item}", fill=color)
                y += 14

        elif self.state == "SCANNING":
            draw.text((20, 50), "SCANNING...", fill=CYAN)
            draw.text((20, 65), "PLEASE WAIT", fill=WHITE)
            
        elif self.state == "RESULT":
            draw.text((5, 38), f"FOUND: {len(self.results)}", fill=CYAN)
            y = 52
            start_i = max(0, self.scan_idx - 3)
            visible_results = self.results[start_i : start_i+4]
            
            for i, (ssid, bssid, sig) in enumerate(visible_results):
                actual_idx = start_i + i
                color = ORANGE if actual_idx == self.scan_idx else WHITE
                draw.text((10, y), f"{sig} {ssid[:8]}", fill=color)
                y += 14

        elif self.state == "CONTEXT":
            # Detail View / Sys Info
            draw.text((5, 40), "SYSTEM STATUS:", fill=WHITE)
            # Placeholder for dynamic metrics from state_manager
            draw.text((5, 55), "CPU: 12%  MEM: 45MB", fill=GRAY)
            draw.text((5, 70), "NET: rmnet0 (UP)", fill=GREEN)
            draw.text((5, 85), "Hold PWR: Back", fill=ORANGE)

        draw_fb(img)

    def select(self):
        if self.state == "MENU":
            item = self.menu_items[self.current_idx]
            if item == "AutoIOT":
                self.state = "AUTO_IOT"
                self.menu_items = self.autoiot_items
                self.current_idx = 0
            elif item == "POWER":
                self.status_msg = "REBOOTING..."
                self.draw()
                subprocess.run(["reboot"])
            
        elif self.state == "AUTO_IOT":
            item = self.menu_items[self.current_idx]
            if item == "ANALYSIS":
                self.state = "SCANNING"
                self.status_msg = "SCANNING"
                self.stop_scan_event.clear()
                self.scanning_thread = threading.Thread(target=self._scan_task, daemon=True)
                self.scanning_thread.start()

        elif self.state == "SCANNING":
            self.cancel_scan()

        elif self.state == "RESULT":
            if self.results:
                selected = self.results[self.scan_idx]
                self.target = (selected[0], selected[1])
                self.status_msg = f"TGT: {selected[0][:6]}"
            self.state = "MENU"
            self.menu_items = self.root_items
        
        elif self.state == "CONTEXT":
            self.back()
        
        self.draw()

    def cancel_scan(self):
        if self.state == "SCANNING":
            self.cleanup()
            self.state = "MENU"
            self.menu_items = self.root_items
            self.status_msg = "ABORTED"
            self.draw()

    def _scan_task(self):
        results = []
        if WIFI:
            results = WIFI.scan_networks()
        else:
            time.sleep(2) # Mock
            results = [("DEMO_NET", "00:11:22:33:44:55", "-50")]
        
        if not self.stop_scan_event.is_set():
            with self.state_lock:
                self.results = results
                self.scan_idx = 0
                self.state = "RESULT"
                self.status_msg = "SELECT TGT"
                self.scanning_thread = None
            self.draw()

    def next(self):
        if self.state in ["MENU", "AUTO_IOT"]:
            self.current_idx = (self.current_idx + 1) % len(self.menu_items)
        elif self.state == "RESULT":
            if self.results:
                self.scan_idx = (self.scan_idx + 1) % len(self.results)
        self.draw()

    def back(self):
        if self.state == "AUTO_IOT":
            self.state = "MENU"
            self.menu_items = self.root_items
            self.current_idx = 3 # Index of AutoIOT in root
        elif self.state == "SCANNING":
            self.cancel_scan()
        elif self.state in ["RESULT", "CONTEXT"]:
            self.state = "MENU"
            self.menu_items = self.root_items
            self.status_msg = "READY"
        self.draw()

def main():
    ui = UI()
    ui.draw()
    
    # Initialize InputManager with UI callback
    input_mgr = InputManager(callback=ui.handle_input)
    input_mgr.start()
    
    try:
        # Keep main thread alive
        while True:
            # Check thread health - auto-transition if scan completed
            if ui.state == "SCANNING" and ui.scanning_thread and not ui.scanning_thread.is_alive():
                ui.scanning_thread.join(timeout=0.1)
                with ui.state_lock:
                    if ui.state == "SCANNING":
                        ui.scanning_thread = None
                        if ui.results:
                            ui.state = "RESULT"
                            ui.status_msg = "SELECT TGT"
                        else:
                            ui.state = "MENU"
                            ui.status_msg = "SCAN DONE"
                        ui.draw()
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        input_mgr.stop()
        ui.cleanup()

if __name__ == "__main__":
    main()
