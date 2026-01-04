import evdev
import struct
import time
import subprocess
import threading
import sys
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
        pass

# --- ANIMATION ---
def startup_animation():
    img = Image.new("RGB", (WIDTH, HEIGHT), BLACK)
    draw = ImageDraw.Draw(img)
    
    for i in range(1, 11):
        draw.rectangle((0, 0, WIDTH, HEIGHT), fill=BLACK)
        draw.text((10, 35), "CALIBRATING", fill=CYAN)
        draw.text((10, 50), "ORBITAL OPTICS", fill=CYAN)
        bar_width = int((WIDTH - 20) * (i / 10))
        draw.rectangle((10, 80, 10 + bar_width, 90), fill=RED)
        draw.rectangle((10, 80, WIDTH - 10, 90), outline=WHITE)
        draw_fb(img)
        time.sleep(0.08)

    # Starfield Effect
    import random
    for _ in range(5):
        draw.rectangle((0, 0, WIDTH, HEIGHT), fill=BLACK)
        for _ in range(20):
            x, y = random.randint(0, WIDTH), random.randint(0, HEIGHT)
            draw.point((x, y), fill=WHITE)
        draw.text((30, 60), "TARGET ACQUIRED", fill=GREEN)
        draw_fb(img)
        time.sleep(0.1)

# --- MENU SYSTEM ---
class Menu:
    def __init__(self):
        self.items = [
            "SCAN FREQUENCIES", 
            "DEAUTH PULSE", 
            "PACKET HARVEST", 
            "BEACON FLOOD", 
            "SYSTEM REBOOT"
        ]
        self.current_idx = 0

    def next(self):
        self.current_idx = (self.current_idx + 1) % len(self.items)

    def select(self):
        item = self.items[self.current_idx]
        
        # Execution Animation
        for i in range(3):
            img = Image.new("RGB", (WIDTH, HEIGHT), BLACK)
            draw = ImageDraw.Draw(img)
            draw.rectangle((0, 0, WIDTH, HEIGHT), fill=RED if i % 2 == 0 else BLACK)
            draw.text((20, 60), f"ENGAGING:\n{item.split()[0]}", fill=WHITE)
            draw_fb(img)
            time.sleep(0.2)
        
        if "REBOOT" in item:
            subprocess.run(["reboot"])
            
def draw(self):
        img = Image.new("RGB", (WIDTH, HEIGHT), BLACK)
        draw = ImageDraw.Draw(img)
        
        # Header (Aesthetic)
        draw.rectangle((0, 0, WIDTH, 18), fill=RED)
        draw.text((5, 4), "FRIENDLY ORBITAL CANNON", fill=BLACK)
        draw.line((0, 19, WIDTH, 19), fill=WHITE)

        # Status Line
        draw.text((5, 22), "STA: ARMED", fill=GREEN)
        draw.text((80, 22), "MOD: 5G", fill=CYAN)

        # Items
        y = 38
        for i, item in enumerate(self.items):
            color = WHITE
            prefix = " "
            if i == self.current_idx:
                color = ORANGE
                prefix = ">"
                # Highlight bar
                draw.rectangle((0, y-1, WIDTH, y+11), fill=(30, 30, 30))
            
            draw.text((10, y), f"{prefix} {item}", fill=color)
            y += 14

        # Footer
        draw.line((0, HEIGHT-12, WIDTH, HEIGHT-12), fill=WHITE)
        draw.text((5, HEIGHT-10), "GEN. LOCH LUCARO", fill=CYAN)

        draw_fb(img)

# --- INPUT LOOP ---
def input_loop(menu):
    try:
        dev = evdev.InputDevice(INPUT_DEV)
    except:
        return

    press_start = 0
    for event in dev.read_loop():
        if event.type == evdev.ecodes.EV_KEY and event.code == evdev.ecodes.KEY_POWER:
            if event.value == 1: # DOWN
                press_start = time.time()
            elif event.value == 0: # UP
                duration = time.time() - press_start
                if duration > 0.6: 
                    menu.select()
                else: 
                    menu.next()
                menu.draw()

if __name__ == "__main__":
    startup_animation()
    menu = Menu()
    menu.draw()
    input_loop(menu)
