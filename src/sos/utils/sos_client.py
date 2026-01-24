#!/usr/bin/env python3
"""
SOS Utility Client
Simple client for interacting with SOS API
"""

import json
import sys
import argparse
import http.client
from typing import Dict, Any


class SOSClient:
    """Client for SOS API Gateway"""
    
    def __init__(self, host='127.0.0.1', port=8888):
        self.host = host
        self.port = port
    
    def _call_api(self, method: str, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """Make API call"""
        try:
            conn = http.client.HTTPConnection(self.host, self.port, timeout=10)
            
            headers = {'Content-Type': 'application/json'}
            body = json.dumps(data) if data else None
            
            conn.request(method, endpoint, body, headers)
            response = conn.getresponse()
            
            result = json.loads(response.read().decode('utf-8'))
            conn.close()
            
            return result
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def health(self) -> Dict[str, Any]:
        """Check API health"""
        return self._call_api('GET', '/api/health')
    
    def wifi_status(self) -> Dict[str, Any]:
        """Get WiFi status"""
        return self._call_api('GET', '/api/wifi/status')
    
    def wifi_scan(self) -> Dict[str, Any]:
        """Scan WiFi networks"""
        return self._call_api('GET', '/api/wifi/scan')
    
    def cellular_status(self) -> Dict[str, Any]:
        """Get cellular status"""
        return self._call_api('GET', '/api/cellular/status')
    
    def display_info(self) -> Dict[str, Any]:
        """Get display info"""
        return self._call_api('GET', '/api/display/info')
    
    def system_info(self) -> Dict[str, Any]:
        """Get system info"""
        return self._call_api('GET', '/api/system/info')
    
    def custom_command(self, command: str, params: Dict = None) -> Dict[str, Any]:
        """Execute custom command"""
        data = {"command": command, "params": params or {}}
        return self._call_api('POST', '/api/command', data)


def print_json(data: Dict):
    """Pretty print JSON"""
    print(json.dumps(data, indent=2))


def main():
    parser = argparse.ArgumentParser(description='SOS API Client')
    parser.add_argument('--host', default='127.0.0.1', help='API host')
    parser.add_argument('--port', type=int, default=8888, help='API port')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    subparsers.add_parser('health', help='Check API health')
    subparsers.add_parser('wifi-status', help='Get WiFi status')
    subparsers.add_parser('wifi-scan', help='Scan WiFi networks')
    subparsers.add_parser('cellular-status', help='Get cellular status')
    subparsers.add_parser('display-info', help='Get display info')
    subparsers.add_parser('system-info', help='Get system info')
    
    cmd_parser = subparsers.add_parser('command', help='Execute custom command')
    cmd_parser.add_argument('cmd', help='Command name')
    cmd_parser.add_argument('--params', help='Parameters as JSON')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    client = SOSClient(args.host, args.port)
    
    if args.command == 'health':
        result = client.health()
    elif args.command == 'wifi-status':
        result = client.wifi_status()
    elif args.command == 'wifi-scan':
        result = client.wifi_scan()
    elif args.command == 'cellular-status':
        result = client.cellular_status()
    elif args.command == 'display-info':
        result = client.display_info()
    elif args.command == 'system-info':
        result = client.system_info()
    elif args.command == 'command':
        params = json.loads(args.params) if args.params else {}
        result = client.custom_command(args.cmd, params)
    else:
        print(f"Unknown command: {args.command}")
        return
    
    print_json(result)


if __name__ == '__main__':
    main()
