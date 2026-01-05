import struct
import time
import subprocess
import threading
import sys
import os
from PIL import Image, ImageDraw, ImageFont

# Import functional core
try:
    import foac_core
    from input_manager import InputManager
    
    WIFI = foac_core.WirelessTool("wlan0")
    CELL = foac_core.CellularTool("rmnet_data0")
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
        self.menu_items = ["SCAN FREQUENCIES", "PACKET HARVEST", "DEAUTH PULSE", "REBOOT"]
        self.current_idx = 0
        self.state = "MENU" 
        self.results = [] # List of (SSID, BSSID, Signal)
        self.target = None # (SSID, BSSID)
        self.status_msg = "READY"
        self.scan_idx = 0
        self.scanning_thread = None
        self.stop_scan = False
        
        # Init Input Manager
        if INPUT:
            INPUT.callback = self.handle_input
            INPUT.start()

    def handle_input(self, event):
        """Callback for InputManager events"""
        print(f"UI Received: {event.action} from {event.source}")
        
        if event.action == "SELECT":
            if self.state == "SCANNING":
                self.cancel_scan()
            else:
                self.select()
                
        elif event.action == "NEXT":
            if self.state == "SCANNING":
                self.cancel_scan()
            else:
                self.next()
                
        elif event.action == "CONTEXT":
            self.context_menu()
            
        elif event.action == "BACK":
            self.back()
            
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
        draw.text((5, 4), "ORBITAL CANNON v3", fill=BLACK)
        
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
                # Get Cell Info
                cell_ip = "No Net"
                if CELL:
                    info = CELL.get_info()
                    if info["ip"]:
                        cell_ip = info["ip"]
                
                draw.text((5, 40), "SYSTEM INFO:", fill=WHITE)
                draw.text((5, 55), f"Cell IP: {cell_ip}", fill=GRAY)
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
        if not self.stop_scan:
            self.results = results
            self.scan_idx = 0
            self.state = "RESULT"
            self.status_msg = "SELECT TGT"
            self.scanning_thread = None
            self.draw()

    def cancel_scan(self):
        if self.state == "SCANNING":
            self.stop_scan = True
            self.state = "MENU"
            self.status_msg = "ABORTED"
            self.draw()

    def select(self):
        if self.state == "MENU":
            item = self.menu_items[self.current_idx]
            
            if item == "SCAN FREQUENCIES":
                self.state = "SCANNING"
                self.status_msg = "SCANNING"
                self.stop_scan = False
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
    
    # Main thread just waits, InputManager handles events in background
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        if INPUT: INPUT.stop()

if __name__ == "__main__":
    main()
