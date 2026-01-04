import subprocess
import re
import time

class WirelessTool:
    def __init__(self, interface="wlan0"):
        self.interface = interface

    def enable_monitor(self):
        # Try airmon-ng first
        try:
            subprocess.run(["airmon-ng", "start", self.interface], check=True)
            self.interface += "mon" # Usually renames to wlan0mon
            return True
        except:
            # Fallback to manual iw
            try:
                subprocess.run(["ifconfig", self.interface, "down"])
                subprocess.run(["iw", self.interface, "set", "type", "monitor"])
                subprocess.run(["ifconfig", self.interface, "up"])
                return True
            except:
                return False

    def scan_networks(self):
        # Returns list of (SSID, BSSID, Signal)
        networks = []
        try:
            # Use iw scan for quick results
            # Added timeout to prevent infinite hang
            result = subprocess.check_output(["iw", self.interface, "scan"], encoding='utf-8', timeout=10)
            ssid = None
            bssid = None
            signal = None
            
            for line in result.split('\n'):
                if line.startswith("BSS "):
                    # Save previous if complete
                    if ssid and bssid and signal:
                        networks.append((ssid, bssid, signal))
                    # Start new
                    bssid = line.split("BSS ")[1].split("(")[0].strip()
                    ssid = None
                    signal = None
                elif "signal:" in line:
                    signal = line.split("signal:")[1].split(".")[0].strip()
                elif "SSID:" in line:
                    ssid = line.split("SSID:")[1].strip()
            
            # Capture the last one
            if ssid and bssid and signal:
                networks.append((ssid, bssid, signal))
        
        except subprocess.TimeoutExpired:
            print("Scan Timeout")
            return [("Scan Timeout", "00:00:00:00:00:00", "-1")]

        except Exception as e:
            print(f"Scan Error: {e}")
            # Mock data for testing if hardware fails
            return [("No Hardware", "00:00:00:00:00:00", "-99")]
            
        return networks[:5] # Return top 5

    def packet_sniff(self, duration=10, output_file="/data/capture.pcap"):
        # Runs tcpdump in background
        proc = subprocess.Popen(["tcpdump", "-i", self.interface, "-w", output_file], 
                                stdout=subprocess.DEVNULL, 
                                stderr=subprocess.DEVNULL)
        time.sleep(duration)
        proc.terminate()
        return True

    def deauth(self, target_mac, count=10):
        # Sends deauth frames
        subprocess.run(["aireplay-ng", "--deauth", str(count), "-a", target_mac, self.interface])

