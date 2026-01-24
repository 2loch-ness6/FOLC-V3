#!/usr/bin/env python3
"""
Hardware Control Daemon (hw_ctl_daemon.py)
Runs in native environment to hook hardware control services

This daemon provides a bridge between the AI system and hardware control,
managing WiFi, cellular modem, display, and input devices.
"""

import os
import sys
import socket
import json
import subprocess
import logging
from pathlib import Path
import time
import signal

# Configuration
SOCKET_PATH = "/tmp/hw_ctl.sock"
LOG_FILE = "/data/rayhunter/hw_ctl_daemon.log"
PID_FILE = "/data/rayhunter/hw_ctl_daemon.pid"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("hw_ctl_daemon")


class HardwareController:
    """Manages hardware control operations"""
    
    def __init__(self):
        self.wifi_interface = "wlan0"
        self.cellular_interface = "rmnet0"
        self.display_device = "/dev/fb0"
        self.running = True
        
    def get_wifi_status(self):
        """Get WiFi interface status"""
        try:
            result = subprocess.run(
                ["iw", "dev", self.wifi_interface, "info"],
                capture_output=True, text=True, timeout=5
            )
            return {
                "status": "success",
                "interface": self.wifi_interface,
                "info": result.stdout if result.returncode == 0 else None,
                "error": result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            logger.error(f"Failed to get WiFi status: {e}")
            return {"status": "error", "message": str(e)}
    
    def scan_wifi(self):
        """Scan for WiFi networks"""
        try:
            # Trigger scan
            subprocess.run(["iw", "dev", self.wifi_interface, "scan", "trigger"], 
                         timeout=5, capture_output=True)
            time.sleep(2)  # Wait for scan to complete
            
            # Get results
            result = subprocess.run(
                ["iw", "dev", self.wifi_interface, "scan", "dump"],
                capture_output=True, text=True, timeout=10
            )
            return {
                "status": "success",
                "networks": self._parse_scan_results(result.stdout)
            }
        except Exception as e:
            logger.error(f"Failed to scan WiFi: {e}")
            return {"status": "error", "message": str(e)}
    
    def _parse_scan_results(self, scan_output):
        """Parse iw scan output into structured data"""
        networks = []
        current_network = {}
        
        for line in scan_output.split('\n'):
            line = line.strip()
            if line.startswith('BSS '):
                if current_network:
                    networks.append(current_network)
                current_network = {"bssid": line.split()[1].rstrip('()')}
            elif 'SSID:' in line:
                current_network['ssid'] = line.split('SSID:', 1)[1].strip()
            elif 'signal:' in line:
                current_network['signal'] = line.split('signal:', 1)[1].strip()
            elif 'freq:' in line:
                current_network['frequency'] = line.split('freq:', 1)[1].strip()
        
        if current_network:
            networks.append(current_network)
        
        return networks
    
    def get_cellular_status(self):
        """Get cellular modem status"""
        try:
            # Check if interface exists
            result = subprocess.run(
                ["ip", "link", "show", self.cellular_interface],
                capture_output=True, text=True, timeout=5
            )
            return {
                "status": "success",
                "interface": self.cellular_interface,
                "info": result.stdout if result.returncode == 0 else None
            }
        except Exception as e:
            logger.error(f"Failed to get cellular status: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_display_info(self):
        """Get display framebuffer information"""
        try:
            result = subprocess.run(
                ["fbset", "-i"],
                capture_output=True, text=True, timeout=5
            )
            return {
                "status": "success",
                "device": self.display_device,
                "info": result.stdout if result.returncode == 0 else None
            }
        except Exception as e:
            logger.error(f"Failed to get display info: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_system_info(self):
        """Get general system information"""
        try:
            return {
                "status": "success",
                "uptime": Path("/proc/uptime").read_text().split()[0],
                "load_avg": Path("/proc/loadavg").read_text().strip(),
                "memory": self._get_memory_info(),
                "cpu": self._get_cpu_info()
            }
        except Exception as e:
            logger.error(f"Failed to get system info: {e}")
            return {"status": "error", "message": str(e)}
    
    def _get_memory_info(self):
        """Parse /proc/meminfo"""
        meminfo = {}
        try:
            for line in Path("/proc/meminfo").read_text().split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    meminfo[key.strip()] = value.strip()
        except Exception as e:
            logger.error(f"Failed to parse meminfo: {e}")
        return meminfo
    
    def _get_cpu_info(self):
        """Get CPU information"""
        try:
            cpuinfo = Path("/proc/cpuinfo").read_text()
            return {"raw": cpuinfo[:500]}  # Truncate for brevity
        except Exception as e:
            logger.error(f"Failed to get CPU info: {e}")
            return {}


class DaemonServer:
    """Unix socket server for handling hardware control requests"""
    
    def __init__(self, socket_path):
        self.socket_path = socket_path
        self.hw_controller = HardwareController()
        self.running = True
        
        # Remove existing socket if present
        if os.path.exists(socket_path):
            os.remove(socket_path)
        
        # Create Unix socket
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket.bind(socket_path)
        self.socket.listen(5)
        os.chmod(socket_path, 0o666)  # Allow all users to connect
        
        logger.info(f"Hardware control daemon listening on {socket_path}")
    
    def handle_request(self, command, params=None):
        """Process hardware control commands"""
        params = params or {}
        
        handlers = {
            "wifi_status": lambda: self.hw_controller.get_wifi_status(),
            "wifi_scan": lambda: self.hw_controller.scan_wifi(),
            "cellular_status": lambda: self.hw_controller.get_cellular_status(),
            "display_info": lambda: self.hw_controller.get_display_info(),
            "system_info": lambda: self.hw_controller.get_system_info(),
            "ping": lambda: {"status": "success", "message": "pong"}
        }
        
        if command in handlers:
            try:
                return handlers[command]()
            except Exception as e:
                logger.error(f"Error handling {command}: {e}")
                return {"status": "error", "message": str(e)}
        else:
            return {"status": "error", "message": f"Unknown command: {command}"}
    
    def run(self):
        """Main daemon loop"""
        logger.info("Hardware control daemon started")
        
        try:
            while self.running:
                try:
                    conn, _ = self.socket.accept()
                    data = conn.recv(4096).decode('utf-8')
                    
                    if not data:
                        conn.close()
                        continue
                    
                    # Parse JSON request
                    request = json.loads(data)
                    command = request.get("command")
                    params = request.get("params", {})
                    
                    logger.info(f"Received command: {command}")
                    
                    # Process request
                    response = self.handle_request(command, params)
                    
                    # Send response
                    conn.sendall(json.dumps(response).encode('utf-8'))
                    conn.close()
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON request: {e}")
                except Exception as e:
                    logger.error(f"Error in daemon loop: {e}")
        
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        logger.info("Cleaning up daemon resources")
        self.running = False
        if hasattr(self, 'socket'):
            self.socket.close()
        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)


def signal_handler(signum, frame):
    """Handle termination signals"""
    logger.info(f"Received signal {signum}")
    sys.exit(0)


def daemonize():
    """Run as a proper daemon"""
    # Write PID file
    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))
    
    # Setup signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)


def main():
    """Main entry point"""
    daemonize()
    
    logger.info("Starting Hardware Control Daemon")
    server = DaemonServer(SOCKET_PATH)
    
    try:
        server.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
