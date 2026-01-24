#!/usr/bin/env python3
"""
Example: SOS API Integration
Demonstrates how to use SOS APIs from Python
"""

import requests
import json
import time
import sys

# Configuration
API_BASE = "http://127.0.0.1:8888/api"

def print_header(text):
    """Print section header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def check_health():
    """Check if SOS API is available"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy":
                print("✓ SOS API is healthy and responding")
                return True
        print("✗ SOS API health check failed")
        return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Cannot connect to SOS API: {e}")
        print("\nMake sure:")
        print("  1. SOS services are running")
        print("  2. Port forwarding is active: adb forward tcp:8888 tcp:8888")
        return False

def get_system_info():
    """Get and display system information"""
    print_header("System Information")
    try:
        response = requests.get(f"{API_BASE}/system/info", timeout=5)
        if response.status_code == 200:
            data = response.json()
            
            uptime = float(data.get("uptime", 0))
            hours = int(uptime // 3600)
            minutes = int((uptime % 3600) // 60)
            
            print(f"Uptime: {hours}h {minutes}m")
            print(f"Load Average: {data.get('load_avg', 'N/A')}")
            
            memory = data.get("memory", {})
            if memory:
                mem_total = memory.get("MemTotal", "N/A")
                mem_free = memory.get("MemFree", "N/A")
                print(f"Memory Total: {mem_total}")
                print(f"Memory Free: {mem_free}")
            
            return True
    except requests.exceptions.RequestException as e:
        print(f"Error getting system info: {e}")
        return False

def get_wifi_status():
    """Get and display WiFi status"""
    print_header("WiFi Status")
    try:
        response = requests.get(f"{API_BASE}/wifi/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            
            if data.get("status") == "success":
                print(f"Interface: {data.get('interface', 'N/A')}")
                info = data.get("info", "")
                if info:
                    # Parse key information from iw output
                    for line in info.split('\n'):
                        line = line.strip()
                        if 'ssid' in line.lower() or 'type' in line.lower():
                            print(f"  {line}")
                print("\n✓ WiFi interface is operational")
            else:
                print(f"✗ WiFi error: {data.get('message', 'Unknown')}")
            return True
    except requests.exceptions.RequestException as e:
        print(f"Error getting WiFi status: {e}")
        return False

def scan_wifi():
    """Scan and display WiFi networks"""
    print_header("WiFi Network Scan")
    print("Scanning for networks... (this may take a few seconds)")
    
    try:
        response = requests.get(f"{API_BASE}/wifi/scan", timeout=15)
        if response.status_code == 200:
            data = response.json()
            
            if data.get("status") == "success":
                networks = data.get("networks", [])
                
                if networks:
                    print(f"\nFound {len(networks)} networks:\n")
                    
                    # Sort by signal strength if available
                    def get_signal_strength(net):
                        signal = net.get("signal", "")
                        if signal and "dBm" in signal:
                            try:
                                return float(signal.split()[0])
                            except:
                                pass
                        return -100
                    
                    networks.sort(key=get_signal_strength, reverse=True)
                    
                    print(f"{'SSID':<30} {'BSSID':<18} {'Signal':<15} {'Frequency'}")
                    print("-" * 80)
                    
                    for net in networks:
                        ssid = net.get("ssid", "Hidden")[:30]
                        bssid = net.get("bssid", "N/A")[:17]
                        signal = net.get("signal", "N/A")
                        freq = net.get("frequency", "N/A")
                        print(f"{ssid:<30} {bssid:<18} {signal:<15} {freq}")
                else:
                    print("No networks found")
            else:
                print(f"✗ Scan error: {data.get('message', 'Unknown')}")
            return True
    except requests.exceptions.RequestException as e:
        print(f"Error scanning WiFi: {e}")
        return False

def get_cellular_status():
    """Get and display cellular status"""
    print_header("Cellular Modem Status")
    try:
        response = requests.get(f"{API_BASE}/cellular/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            
            if data.get("status") == "success":
                print(f"Interface: {data.get('interface', 'N/A')}")
                info = data.get("info", "")
                if info:
                    print("\nInterface Information:")
                    print(info)
            else:
                print(f"✗ Cellular error: {data.get('message', 'Unknown')}")
            return True
    except requests.exceptions.RequestException as e:
        print(f"Error getting cellular status: {e}")
        return False

def continuous_monitoring(interval=5):
    """Continuously monitor system status"""
    print_header("Continuous Monitoring")
    print(f"Monitoring system every {interval} seconds (Ctrl+C to stop)")
    print()
    
    try:
        while True:
            response = requests.get(f"{API_BASE}/system/info", timeout=5)
            if response.status_code == 200:
                data = response.json()
                uptime = float(data.get("uptime", 0))
                load = data.get("load_avg", "N/A").split()[0]  # Get 1-min avg
                
                print(f"[{time.strftime('%H:%M:%S')}] Uptime: {int(uptime)}s | Load: {load}", end="\r")
            
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped")

def main():
    """Main function"""
    print("\n╔══════════════════════════════════════════════════╗")
    print("║  SOS API Integration Example                    ║")
    print("║  Demonstrating Python API Usage                 ║")
    print("╚══════════════════════════════════════════════════╝")
    
    # Check if API is available
    if not check_health():
        sys.exit(1)
    
    # Run demonstrations
    get_system_info()
    time.sleep(1)
    
    get_wifi_status()
    time.sleep(1)
    
    scan_wifi()
    time.sleep(1)
    
    get_cellular_status()
    time.sleep(1)
    
    # Ask if user wants continuous monitoring
    print_header("Options")
    print("\n1. Exit")
    print("2. Start continuous monitoring")
    
    try:
        choice = input("\nSelect option (1-2): ").strip()
        if choice == "2":
            continuous_monitoring()
    except KeyboardInterrupt:
        print("\n\nExiting...")
    
    print("\n✓ Demo complete!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
