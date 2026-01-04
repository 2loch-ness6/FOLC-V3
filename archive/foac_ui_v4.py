import evdev
import struct
import time
import subprocess
import threading
import sys
from select import select
from PIL import Image, ImageDraw, ImageFont

# Import our functional core
try:
    import foac_core
    WIFI = foac_core.WirelessTool("wlan0")
except ImportError:
    WIFI = None

# --- CONFIG ---
FB_PATH = "/dev/fb0"
INPUT_DEV = "/dev/input/event0"
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
                    val = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                    data.extend(struct.pack("<H", val))
            fb.write(data)
    except: pass

class UI:
    def __init__(self):
        self.menu_items = ["SCAN FREQUENCIES", "PACKET HARVEST", "DEAUTH PULSE", "REBOOT"]
        self.current_idx = 0
        self.state = "MENU" # MENU, SCANNING, RESULT, SNIFFING
        self.results = []
        self.status_msg = "ARMED"

    def draw(self):
        img = Image.new("RGB", (WIDTH, HEIGHT), BLACK)
        draw = ImageDraw.Draw(img)
        
        # Header
        draw.rectangle((0, 0, WIDTH, 18), fill=RED)
        draw.text((5, 4), "FRIENDLY ORBITAL CANNON", fill=BLACK)
        draw.text((5, 22), f"STA: {self.status_msg}", fill=GREEN if "ARMED" in self.status_msg else ORANGE)

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
            draw.text((20, 60), "CALIBRATING...", fill=CYAN)
            draw.rectangle((10, 80, WIDTH-10, 90), outline=WHITE)
            # Animation handled by caller usually
            
        elif self.state == "RESULT":
            draw.text((5, 38), "TARGETS FOUND:", fill=CYAN)
            y = 52
            if not self.results:
                draw.text((10, y), "NONE DETECTED", fill=RED)
            else:
                for ssid, sig in self.results[:4]:
                    draw.text((10, y), f"{sig}dBm {ssid[:12]}", fill=WHITE)
                    y += 14
            draw.text((5, HEIGHT-22), "[PRESS] BACK", fill=ORANGE)

        # Footer
        draw.line((0, HEIGHT-12, WIDTH, HEIGHT-12), fill=WHITE)
        draw.text((5, HEIGHT-10), "GEN. LOCH LUCARO", fill=CYAN)
        draw_fb(img)

    def handle_select(self):
        item = self.menu_items[self.current_idx]
        if item == "SCAN FREQUENCIES":
            self.state = "SCANNING"
            self.draw()
            # Run real scan
            if WIFI:
                self.results = WIFI.scan_networks()
            self.state = "RESULT"
        elif item == "PACKET HARVEST":
            self.status_msg = "SNIFFING"
            self.draw()
            if WIFI:
                WIFI.packet_sniff(duration=5)
            self.status_msg = "ARMED"
        elif item == "REBOOT":
            subprocess.run(["reboot"])
        self.draw()

    def handle_back(self):
        self.state = "MENU"
        self.draw()

def main():
    ui = UI()
    ui.draw()
    
    dev = evdev.InputDevice(INPUT_DEV)
    press_start = 0
    for event in dev.read_loop():
        if event.type == evdev.ecodes.EV_KEY and event.code == evdev.ecodes.KEY_POWER:
            if event.value == 1: 
                press_start = time.time()
            elif event.value == 0: 
                duration = time.time() - press_start
                if duration > 0.8: # Long Press
                    if ui.state == "MENU":
                        ui.handle_select()
                    else:
                        ui.handle_back()
                else: # Short Press
                    if ui.state == "MENU":
                        ui.next()
                ui.draw()

    # Helpers inside class
    def next(self):
        self.current_idx = (self.current_idx + 1) % len(self.menu_items)
UI.next = next # Monkey patch for brevity

if __name__ == "__main__":
    main()
