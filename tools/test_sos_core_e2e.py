#!/usr/bin/env python3
import os
import sys
import json
import threading
import http.server
import time
import subprocess
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from sos.ai.ai_orchestrator import AIOrchestrator

class MockGatewayHandler(http.server.BaseHTTPRequestHandler):
    """Mock API Gateway handler for E2E tests"""
    
    def do_GET(self):
        if self.path == "/api/system/info":
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "success",
                "device": "Orbic Speed Mock",
                "uptime": 1234
            }).encode())
        elif self.path == "/api/wifi/status":
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "success",
                "interface": "wlan0",
                "state": "connected",
                "ssid": "MockWiFi"
            }).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return # Silence logging

def run_mock_gateway(server):
    server.serve_forever()

def test_e2e_flow():
    print("Starting SOS E2E Integration Test...")
    
    # Start mock gateway in background with dynamic port
    server = http.server.HTTPServer(('127.0.0.1', 0), MockGatewayHandler)
    port = server.server_port
    server_thread = threading.Thread(target=run_mock_gateway, args=(server,), daemon=True)
    server_thread.start()
    
    # Wait for server to start
    time.sleep(1)
    
    # Mock config
    config_data = {
        "gemini": {"enabled": True, "cli_path": "mock-gemini"},
        "preferred_provider": "gemini"
    }
    
    # Mock AI response - simulating a JSON plan from AI
    ai_plan = {
        "action": "api_call",
        "api_endpoint": "/api/wifi/status",
        "method": "GET"
    }
    
    config_path = "/tmp/mock_ai_config.json"
    with patch("src.sos.ai.ai_orchestrator.CONFIG_FILE", config_path):
        with open(config_path, 'w') as f:
            json.dump(config_data, f)
            
        with patch("subprocess.run") as mock_run:
            # Mock successful Gemini CLI call returning the AI plan
            mock_run.return_value = MagicMock(
                stdout=json.dumps(ai_plan),
                stderr="",
                returncode=0
            )
            
            # Initialize orchestrator
            orchestrator = AIOrchestrator()
            # Force API client to use our mock server port
            orchestrator.api_client.host = "127.0.0.1"
            orchestrator.api_client.port = port
            
            print("Step 1: Process natural language query...")
            ai_result = orchestrator.process_natural_language("What is the wifi status?")
            
            assert ai_result["status"] == "success"
            ai_response = json.loads(ai_result["response"])
            assert ai_response["action"] == "api_call"
            
            print("Step 2: Execute AI specified action...")
            exec_result = orchestrator.execute_ai_action(ai_response)
            
            assert exec_result["status"] == "success"
            assert exec_result["ssid"] == "MockWiFi"
            
            print("\nE2E Integration Test PASSED successfully!")

if __name__ == "__main__":
    try:
        test_e2e_flow()
    except Exception as e:
        print(f"\nE2E Integration Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)