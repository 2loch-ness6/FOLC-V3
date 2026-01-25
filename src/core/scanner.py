import subprocess
import re
import logging
import time

logger = logging.getLogger("scanner")

class WifiScanner:
    """
    Optimized 2.4/5GHz scanning engine using 'iw' and monitor mode.
    """
    def __init__(self, interface="wlan0"):
        self.interface = interface
        # Frequency to Channel mapping
        self.freq_map = {
            # 2.4 GHz
            2412: 1, 2417: 2, 2422: 3, 2427: 4, 2432: 5, 2437: 6,
            2442: 7, 2447: 8, 2452: 9, 2457: 10, 2462: 11,
            # 5 GHz (Common channels)
            5180: 36, 5200: 40, 5220: 44, 5240: 48,
            5745: 149, 5765: 153, 5785: 157, 5805: 161, 5825: 165
        }

    def scan(self):
        """Triggers a scan and returns parsed results"""
        try:
            # Trigger scan
            subprocess.run(["iw", "dev", self.interface, "scan", "trigger"], 
                         timeout=5, capture_output=True)
            time.sleep(2)
            
            # Get results
            result = subprocess.run(
                ["iw", "dev", self.interface, "scan", "dump"],
                capture_output=True, text=True, timeout=10
            )
            return self._parse_scan_results(result.stdout)
        except Exception as e:
            logger.error(f"Scan failed: {e}")
            return []

    def _parse_scan_results(self, scan_output):
        """Parse iw scan output into structured data"""
        networks = []
        current_network = {}
        
        for line in scan_output.split('\n'):
            line = line.strip()
            
            # New BSS entry
            if line.startswith('BSS '):
                if current_network:
                    networks.append(current_network)
                # Extract BSSID
                bssid_match = re.search(r'BSS ([0-9a-fA-F:]{17})', line)
                current_network = {"bssid": bssid_match.group(1) if bssid_match else "unknown"}
            
            # SSID
            elif 'SSID:' in line:
                current_network['ssid'] = line.split('SSID:', 1)[1].strip()
            
            # Signal
            elif 'signal:' in line:
                sig_match = re.search(r'signal: (-?\d+)', line)
                if sig_match:
                    current_network['signal'] = int(sig_match.group(1))
            
            # Frequency / Channel
            elif 'freq:' in line:
                freq_match = re.search(r'freq: (\d+)', line)
                if freq_match:
                    freq = int(freq_match.group(1))
                    current_network['freq'] = freq
                    current_network['channel'] = self.freq_map.get(freq, 0)
        
        if current_network:
            networks.append(current_network)
        
        return networks
