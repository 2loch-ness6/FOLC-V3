#!/usr/bin/env python3
"""
FOLC WiFi Scan Test
Tests the WiFi scanning functionality of folc_core module
"""
import sys
sys.path.insert(0, "/root")

try:
    import folc_core
    wifi = folc_core.WirelessTool("wlan0")
    results = wifi.scan_networks()
    print(f"SCAN_OK:{len(results)}")
    sys.exit(0)
except Exception as e:
    print(f"SCAN_ERROR:{e}")
    sys.exit(1)
