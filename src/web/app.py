import http.server
import socketserver
import subprocess
import json
import os

PORT = 8000
WEB_ROOT = "/root/src/web/templates"

class FolcHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
            return self.serve_template()
        
        elif self.path == '/api/status':
            self.send_json({
                "uptime": subprocess.getoutput("uptime"),
                "ram": subprocess.getoutput("free -m | grep Mem")
            })
            
        elif self.path == '/api/logs':
            logs = subprocess.getoutput("tail -n 50 /data/rayhunter/folc.log")
            self.send_json({"logs": logs})
            
        else:
            # Serve static files or 404
            super().do_GET()

    def do_POST(self):
        if self.path == '/api/scan':
            # In a real scenario, this would trigger the UI process via IPC
            # For now, we'll just log it
            print("Scan triggered via Web UI")
            self.send_json({"status": "SCAN_INITIATED"})
        else:
            self.send_error(404)

    def serve_template(self):
        try:
            with open(os.path.join(WEB_ROOT, "index.html"), 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, str(e))

    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

# Ensure we map / to our template directory for SimpleHTTPRequestHandler
os.chdir(WEB_ROOT)

with socketserver.TCPServer(("0.0.0.0", PORT), FolcHandler) as httpd:
    print(f"SERVING AT PORT {PORT}")
    httpd.serve_forever()
