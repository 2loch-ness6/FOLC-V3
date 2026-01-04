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

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)

# --- FRAMEBUFFER OPS ---
def rgb888_to_rgb565(r, g, b):
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

def draw_fb(image):
    pixels = image.load()
    try:
        with open(FB_PATH, "wb") as fb:
            data = bytearray()
            for y in range(HEIGHT):
                for x in range(WIDTH):
                    r, g, b = pixels[x, y]
                    val = rgb888_to_rgb565(r, g, b)
                    data.extend(struct.pack("<H", val))
            fb.write(data)
    except Exception as e:
        print(f"FB Error: {e}")

# --- ANIMATION ---
def startup_animation():
    img = Image.new("RGB", (WIDTH, HEIGHT), BLACK)
    draw = ImageDraw.Draw(img)
    
    # 1. Boot Sequence
    for i in range(1, 11):
        draw.rectangle((0, 0, WIDTH, HEIGHT), fill=BLACK)
        
        # Text
        draw.text((10, 40), "INITIALIZING", fill=CYAN)
        draw.text((10, 55), "ORBITAL CANNON", fill=CYAN)
        
        # Loading Bar
        bar_width = int((WIDTH - 20) * (i / 10))
        draw.rectangle((10, 80, 10 + bar_width, 90), fill=RED)
        draw.rectangle((10, 80, WIDTH - 10, 90), outline=WHITE)
        
        draw_fb(img)
        time.sleep(0.1)

    # 2. Flash
    draw.rectangle((0, 0, WIDTH, HEIGHT), fill=WHITE)
    draw_fb(img)
    time.sleep(0.05)
    
    # 3. Logo (Simple Circle/Target)
    draw.rectangle((0, 0, WIDTH, HEIGHT), fill=BLACK)
    draw.ellipse((34, 34, 94, 94), outline=ORANGE)
    draw.line((64, 20, 64, 108), fill=ORANGE) # V
    draw.line((20, 64, 108, 64), fill=ORANGE) # H
    draw.text((15, 110), "SYSTEM READY", fill=GREEN)
    draw_fb(img)
    time.sleep(1.0)

# --- MENU SYSTEM ---
class Menu:
    def __init__(self):
        self.items = ["Status: IDLE", "Target Scan", "Deauth Attack", "Packet Sniff", "Payloads", "Reboot"]
        self.current_idx = 0

    def next(self):
        self.current_idx = (self.current_idx + 1) % len(self.items)

    def select(self):
        item = self.items[self.current_idx]
        print(f"Selected: {item}")
        
        # Simple Feedback Animation
        img = Image.new("RGB", (WIDTH, HEIGHT), BLACK)
        draw = ImageDraw.Draw(img)
        draw.text((10, 60), f"EXECUTING:\n{item.split()[0]}", fill=RED)
        draw_fb(img)
        time.sleep(1.0)
        
        if "Reboot" in item:
            subprocess.run(["reboot"])
            
    def draw(self):
        img = Image.new("RGB", (WIDTH, HEIGHT), BLACK)
        draw = ImageDraw.Draw(img)
        
        # Header
        draw.rectangle((0, 0, WIDTH, 20), fill=RED)
        draw.text((5, 5), "ASSAULT CANNON", fill=BLACK)

        # Items
        y = 25
        for i, item in enumerate(self.items):
            color = WHITE
            prefix = "  "
            if i == self.current_idx:
                color = ORANGE
                prefix = "> "
                draw.rectangle((0, y, WIDTH, y+12), outline=ORANGE)
            
            # Truncate to fit width roughly
            draw.text((5, y), f"{prefix}{item}", fill=color)
            y += 15

        draw_fb(img)

# --- INPUT LOOP ---
def input_loop(menu):
    try:
        dev = evdev.InputDevice(INPUT_DEV)
    except FileNotFoundError:
        print(f"Input device {INPUT_DEV} not found.")
        return

    print(f"Listening on {dev.name}...")
    
    # Grab exclusive access if possible (prevents system handling?)
    # dev.grab()
    
    press_start = 0
    
    for event in dev.read_loop():
        if event.type == evdev.ecodes.EV_KEY and event.code == evdev.ecodes.KEY_POWER:
            if event.value == 1: # DOWN
                press_start = time.time()
            elif event.value == 0: # UP
                duration = time.time() - press_start
                if duration > 0.5: # Long Press
                    menu.select()
                else: # Short Press
                    menu.next()
                menu.draw()

if __name__ == "__main__":
    startup_animation()
    menu = Menu()
    menu.draw()
    input_loop(menu)
