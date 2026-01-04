import evdev
import struct
import time
import subprocess
import threading
import sys
import os
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
        self.results = []
        self.status_msg = "READY"

    def draw(self):
        img = Image.new("RGB", (WIDTH, HEIGHT), BLACK)
        draw = ImageDraw.Draw(img)
        
        # Header
        draw.rectangle((0, 0, WIDTH, 18), fill=RED)
        draw.text((5, 4), "ORBITAL CANNON v2", fill=BLACK)
        draw.text((5, 22), f"STA: {self.status_msg}", fill=GREEN if "READY" in self.status_msg else ORANGE)

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
            
        elif self.state == "RESULT":
            draw.text((5, 38), f"FOUND: {len(self.results)}", fill=CYAN)
            y = 52
            if not self.results:
                draw.text((10, y), "NONE DETECTED", fill=RED)
            else:
                for ssid, sig in self.results[:4]:
                    draw.text((10, y), f"{sig} {ssid[:10]}", fill=WHITE)
                    y += 14
            draw.text((5, HEIGHT-22), "BTN1: BACK", fill=ORANGE)

        draw_fb(img)

    def next(self):
        self.current_idx = (self.current_idx + 1) % len(self.menu_items)
        self.draw()

    def select(self):
        item = self.menu_items[self.current_idx]
        if item == "SCAN FREQUENCIES":
            self.state = "SCANNING"
            self.status_msg = "SCANNING"
            self.draw()
            if WIFI:
                self.results = WIFI.scan_networks()
            self.state = "RESULT"
            self.status_msg = "DONE"
        elif item == "PACKET HARVEST":
            self.status_msg = "SNIFFING"
            self.draw()
            if WIFI:
                WIFI.packet_sniff(duration=5)
            self.status_msg = "READY"
        elif item == "REBOOT":
            subprocess.run(["reboot"])
        self.draw()

    def back(self):
        self.state = "MENU"
        self.status_msg = "READY"
        self.draw()

def main():
    ui = UI()
    ui.draw()
    
    # Auto-detect all input devices
    devices = []
    try:
        for path in os.listdir("/dev/input"):
            if path.startswith("event"):
                try:
                    dev = evdev.InputDevice(os.path.join("/dev/input", path))
                    devices.append(dev)
                    print(f"Added input: {dev.name} ({path})")
                except: pass
    except: pass

    if not devices:
        print("No input devices found!")
        return

    # Input Loop
    devices_map = {dev.fd: dev for dev in devices}
    
    while True:
        r, w, x = select(devices_map.values(), [], [])
        for dev in r:
            for event in dev.read():
                if event.type == evdev.ecodes.EV_KEY:
                    # Filter for Key Release (value=0) to prevent double trigger
                    if event.value == 0: 
                        continue
                    if event.value == 1: # Key Down
                        print(f"Key detected: {event.code} on {dev.name}")
                        
                        # LOGIC MAP
                        # POWER BUTTON (KEY_POWER=116) -> SELECT
                        if event.code == 116:
                            if ui.state == "MENU":
                                ui.select()
                            elif ui.state == "RESULT":
                                ui.back() # Power also backs out of results
                        
                        # MENU/WPS BUTTON (Likely KEY_8=9, KEY_9=10, or others) -> SCROLL
                        # We treat ANY key other than Power as SCROLL
                        elif event.code != 116:
                            if ui.state == "MENU":
                                ui.next()
                            elif ui.state == "RESULT":
                                ui.back()

if __name__ == "__main__":
    main()
