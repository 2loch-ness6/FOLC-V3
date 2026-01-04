import evdev
import struct
import time
import subprocess
import threading
from select import select
from PIL import Image, ImageDraw, ImageFont

# --- CONFIG ---
FB_PATH = "/dev/fb0"
INPUT_DEV = "/dev/input/event0" # Power Button
WIDTH = 128
HEIGHT = 128

# Colors (RGB Tuple)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# --- FRAMEBUFFER ---
def rgb888_to_rgb565(r, g, b):
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

def draw_fb(image):
    pixels = image.load()
    try:
        with open(FB_PATH, "wb") as fb:
            # Buffer the write? For now raw write is okay for small 128x128
            # Construct bytearray for speed
            data = bytearray()
            for y in range(HEIGHT):
                for x in range(WIDTH):
                    r, g, b = pixels[x, y]
                    val = rgb888_to_rgb565(r, g, b)
                    data.extend(struct.pack("<H", val))
            fb.write(data)
    except Exception as e:
        print(f"FB Error: {e}")

# --- MENU SYSTEM ---
class Menu:
    def __init__(self):
        self.items = ["Dashboard", "WiFi Scan", "Deauth", "Sniff", "Reboot"]
        self.current_idx = 0
        self.active = True

    def next(self):
        self.current_idx = (self.current_idx + 1) % len(self.items)

    def select(self):
        item = self.items[self.current_idx]
        print(f"Selected: {item}")
        if item == "Reboot":
            subprocess.run(["reboot"])
        # Add more actions here

    def draw(self):
        img = Image.new("RGB", (WIDTH, HEIGHT), BLACK)
        draw = ImageDraw.Draw(img)
        
        # Header
        draw.rectangle((0, 0, WIDTH, 20), fill=CYAN)
        draw.text((10, 5), "GEMINI FLIPPER", fill=BLACK)

        # Items
        y = 25
        for i, item in enumerate(self.items):
            color = WHITE
            prefix = "  "
            if i == self.current_idx:
                color = GREEN
                prefix = "> "
                draw.rectangle((0, y, WIDTH, y+12), outline=GREEN)
            
            draw.text((5, y), f"{prefix}{item}", fill=color)
            y += 15

        draw_fb(img)

# --- INPUT LOOP ---
def input_loop(menu):
    dev = evdev.InputDevice(INPUT_DEV)
    print(f"Listening on {dev.name}...")
    
    # Timing for Long Press
    press_start = 0
    
    for event in dev.read_loop():
        if event.type == evdev.ecodes.EV_KEY and event.code == evdev.ecodes.KEY_POWER:
            if event.value == 1: # DOWN
                press_start = time.time()
            elif event.value == 0: # UP
                duration = time.time() - press_start
                if duration > 1.0: # Long Press (>1s)
                    print("Long Press")
                    menu.select()
                else: # Short Press
                    print("Short Press")
                    menu.next()
                menu.draw()

if __name__ == "__main__":
    menu = Menu()
    menu.draw() # Initial draw
    
    try:
        input_loop(menu)
    except Exception as e:
        print(f"Error: {e}")
