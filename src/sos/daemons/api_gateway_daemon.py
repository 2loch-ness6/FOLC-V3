#!/usr/bin/env python3
"""
API Gateway Daemon (api_gateway_daemon.py)
Runs in native environment to serve internal REST APIs

This daemon provides HTTP REST API endpoints for system control,
bridging the Alpine chroot environment with native hardware services.
"""

import os
import sys
import json
import logging
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import signal

# Configuration
API_HOST = "127.0.0.1"
API_PORT = 8888
LOG_FILE = "/data/rayhunter/api_gateway_daemon.log"
PID_FILE = "/data/rayhunter/api_gateway_daemon.pid"
HW_CTL_SOCKET = "/tmp/hw_ctl.sock"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("api_gateway")


class HardwareClient:
    """Client to communicate with hardware control daemon"""
    
    def __init__(self, socket_path):
        self.socket_path = socket_path
    
    def send_command(self, command, params=None):
        """Send command to hardware daemon and get response"""
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(self.socket_path)
            
            request = {"command": command, "params": params or {}}
            sock.sendall(json.dumps(request).encode('utf-8'))
            
            response = sock.recv(8192).decode('utf-8')
            sock.close()
            
            return json.loads(response)
        except Exception as e:
            logger.error(f"Failed to communicate with hardware daemon: {e}")
            return {"status": "error", "message": str(e)}


class APIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for API endpoints"""
    
    hw_client = None
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        logger.info(f"GET {path}")
        
        # Route requests
        if path == "/api/health":
            self.send_json_response({"status": "healthy", "service": "api_gateway"})
        elif path == "/api/wifi/status":
            self.handle_wifi_status()
        elif path == "/api/wifi/scan":
            self.handle_wifi_scan()
        elif path == "/api/cellular/status":
            self.handle_cellular_status()
        elif path == "/api/display/info":
            self.handle_display_info()
        elif path == "/api/system/info":
            self.handle_system_info()
        else:
            self.send_error_response(404, "Endpoint not found")
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        logger.info(f"POST {path}")
        
        # Read request body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self.send_error_response(400, "Invalid JSON")
            return
        
        # Route requests
        if path == "/api/command":
            self.handle_custom_command(data)
        else:
            self.send_error_response(404, "Endpoint not found")
    
    def handle_wifi_status(self):
        """Get WiFi interface status"""
        response = self.hw_client.send_command("wifi_status")
        self.send_json_response(response)
    
    def handle_wifi_scan(self):
        """Scan for WiFi networks"""
        response = self.hw_client.send_command("wifi_scan")
        self.send_json_response(response)
    
    def handle_cellular_status(self):
        """Get cellular modem status"""
        response = self.hw_client.send_command("cellular_status")
        self.send_json_response(response)
    
    def handle_display_info(self):
        """Get display information"""
        response = self.hw_client.send_command("display_info")
        self.send_json_response(response)
    
    def handle_system_info(self):
        """Get system information"""
        response = self.hw_client.send_command("system_info")
        self.send_json_response(response)
    
    def handle_custom_command(self, data):
        """Execute custom hardware command"""
        command = data.get("command")
        params = data.get("params", {})
        
        if not command:
            self.send_error_response(400, "Missing command parameter")
            return
        
        response = self.hw_client.send_command(command, params)
        self.send_json_response(response)
    
    def send_json_response(self, data, status=200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def send_error_response(self, status, message):
        """Send error response"""
        self.send_json_response({"status": "error", "message": message}, status)
    
    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info(f"{self.address_string()} - {format % args}")


class APIGatewayServer:
    """API Gateway HTTP server"""
    
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.running = True
        
        # Initialize hardware client
        APIHandler.hw_client = HardwareClient(HW_CTL_SOCKET)
        
        # Create HTTP server
        self.server = HTTPServer((host, port), APIHandler)
        logger.info(f"API Gateway listening on http://{host}:{port}")
    
    def run(self):
        """Start the server"""
        logger.info("API Gateway started")
        
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        logger.info("Shutting down API Gateway")
        self.running = False
        if hasattr(self, 'server'):
            self.server.shutdown()
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
    
    logger.info("Starting API Gateway Daemon")
    server = APIGatewayServer(API_HOST, API_PORT)
    
    try:
        server.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
