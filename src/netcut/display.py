#!/usr/bin/env python3
"""
display.py — Framebuffer status display for Orbic netcut appliance
Renders live stats to the 128x128 RGB565 display at /dev/fb0.
Runs as a background daemon, reads system stats + netcut live data.
"""

import struct
import time
import json
import os
import subprocess

FB_DEV = "/dev/fb0"
WIDTH = 128
HEIGHT = 128
LIVE_STATS = "/tmp/netcut_live.json"
STATE_FILE = "/tmp/netctl_state.json"
REFRESH_HZ = 2

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("[-] Pillow not available")
    exit(1)

try:
    FONT = ImageFont.truetype("/usr/share/fonts/ttf-dejavu/DejaVuSansMono.ttf", 9)
    FONT_SM = ImageFont.truetype("/usr/share/fonts/ttf-dejavu/DejaVuSansMono.ttf", 8)
    FONT_LG = ImageFont.truetype("/usr/share/fonts/ttf-dejavu/DejaVuSansMono-Bold.ttf", 11)
except (IOError, OSError):
    FONT = ImageFont.load_default()
    FONT_SM = FONT
    FONT_LG = FONT

COL_BG = (0, 0, 0)
COL_HEADER = (0, 255, 100)
COL_TEXT = (200, 200, 200)
COL_VAL = (255, 255, 255)
COL_ATTACK = (255, 40, 40)
COL_IDLE = (80, 80, 80)
COL_SCAN = (255, 200, 0)
COL_BAR = (0, 180, 255)


def rgb888_to_rgb565(img):
    pixels = img.tobytes()
    out = bytearray(WIDTH * HEIGHT * 2)
    for i in range(0, len(pixels), 3):
        r, g, b = pixels[i], pixels[i+1], pixels[i+2]
        rgb565 = ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)
        idx = (i // 3) * 2
        out[idx] = rgb565 & 0xFF
        out[idx+1] = (rgb565 >> 8) & 0xFF
    return bytes(out)


def write_fb(data):
    try:
        with open(FB_DEV, 'wb') as fb:
            fb.write(data)
    except (IOError, OSError):
        pass


def get_cpu():
    try:
        with open('/proc/stat') as f:
            parts = f.readline().split()
        total = sum(int(x) for x in parts[1:])
        idle = int(parts[4])
        return total, idle
    except (IOError, ValueError):
        return 0, 0


def get_mem():
    try:
        with open('/proc/meminfo') as f:
            total = int(f.readline().split()[1])
            free = int(f.readline().split()[1])
        return int((1 - free / total) * 100) if total > 0 else 0
    except (IOError, ValueError):
        return 0


def get_temp():
    try:
        with open('/sys/class/thermal/thermal_zone0/temp') as f:
            return f.read().strip() + "C"
    except (IOError, OSError):
        return "?"


def get_battery():
    try:
        with open('/sys/devices/qpnp-vadc-8/vbat_sns') as f:
            line = f.read()
        uv = int(line.split('Result:')[1].split()[0])
        volts = uv / 1_000_000
        # Li-ion curve: 4.2V=100%, 3.0V=0%
        pct = int((volts - 3.0) / (4.2 - 3.0) * 100)
        pct = max(0, min(100, pct))
        return pct, f"{volts:.2f}V"
    except (IOError, OSError, ValueError, IndexError):
        return -1, "?"


def get_signal():
    try:
        r = subprocess.run(
            ['iw', 'dev', 'wlan0', 'link'],
            capture_output=True, text=True, timeout=3
        )
        for line in r.stdout.split('\n'):
            if 'signal:' in line:
                return line.split('signal:')[1].strip()
        return "N/A"
    except (subprocess.TimeoutExpired, OSError):
        return "?"


def get_uptime():
    try:
        with open('/proc/uptime') as f:
            secs = int(float(f.read().split()[0]))
        m, s = divmod(secs, 60)
        h, m = divmod(m, 60)
        if h > 0:
            return f"{h}h{m:02d}m"
        return f"{m}m{s:02d}s"
    except (IOError, ValueError):
        return "?"


def get_live():
    try:
        with open(LIVE_STATS) as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError, OSError):
        return {"status": "IDLE"}


def get_netstate():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError, OSError):
        return {}


def draw_bar(draw, x, y, w, h, pct, color):
    draw.rectangle([x, y, x+w, y+h], outline=(60, 60, 60))
    fill_w = int(w * min(pct, 100) / 100)
    if fill_w > 0:
        draw.rectangle([x+1, y+1, x+fill_w, y+h-1], fill=color)


def render(cpu_pct, mem_pct, temp, signal, uptime, live, netstate, batt_pct, batt_v):
    img = Image.new('RGB', (WIDTH, HEIGHT), COL_BG)
    draw = ImageDraw.Draw(img)

    status = live.get("status", "IDLE")
    status_colors = {
        "ATTACKING": COL_ATTACK,
        "SCANNING": COL_SCAN,
        "IDLE": COL_IDLE,
        "ABORT": (255, 100, 0),
        "RESTORING": (0, 200, 255)
    }
    scol = status_colors.get(status, COL_TEXT)

    # Header
    draw.text((2, 1), "FOLC", fill=COL_HEADER, font=FONT_LG)
    draw.text((50, 2), status, fill=scol, font=FONT)

    # Divider
    draw.line([(0, 14), (127, 14)], fill=(40, 40, 40))

    y = 17

    # Network info
    ssid = netstate.get("ssid", "---")
    ip = netstate.get("ip", "---")
    draw.text((2, y), f"NET {ssid[:14]}", fill=COL_TEXT, font=FONT_SM)
    y += 10
    draw.text((2, y), f"IP  {ip}", fill=COL_VAL, font=FONT_SM)
    y += 10
    draw.text((2, y), f"SIG {signal}", fill=COL_VAL, font=FONT_SM)
    y += 12

    # Divider
    draw.line([(0, y), (127, y)], fill=(40, 40, 40))
    y += 3

    # Attack stats
    if status == "ATTACKING":
        pps = live.get("pps", 0)
        pkts = live.get("packets", 0)
        tgts = live.get("targets", 0)
        elapsed = live.get("elapsed", 0)
        em, es = divmod(elapsed, 60)

        draw.text((2, y), f"TGT {tgts}", fill=COL_VAL, font=FONT)
        draw.text((64, y), f"T {em}:{es:02d}", fill=COL_VAL, font=FONT)
        y += 11

        draw.text((2, y), "PPS", fill=COL_TEXT, font=FONT_SM)
        draw.text((24, y), f"{pps}", fill=COL_ATTACK, font=FONT_LG)
        y += 14

        draw.text((2, y), f"PKT {pkts:,}", fill=COL_TEXT, font=FONT_SM)
        y += 12
    elif status == "SCANNING":
        draw.text((2, y), "Scanning...", fill=COL_SCAN, font=FONT)
        y += 14
    else:
        draw.text((2, y), "Ready", fill=COL_IDLE, font=FONT)
        y += 14

    # Divider
    draw.line([(0, y), (127, y)], fill=(40, 40, 40))
    y += 3

    # System stats
    draw.text((2, y), "CPU", fill=COL_TEXT, font=FONT_SM)
    draw_bar(draw, 24, y, 50, 8, cpu_pct, COL_BAR)
    draw.text((78, y), f"{cpu_pct}%", fill=COL_VAL, font=FONT_SM)
    y += 11

    draw.text((2, y), "MEM", fill=COL_TEXT, font=FONT_SM)
    draw_bar(draw, 24, y, 50, 8, mem_pct, COL_BAR)
    draw.text((78, y), f"{mem_pct}%", fill=COL_VAL, font=FONT_SM)
    y += 11

    batt_col = COL_ATTACK if batt_pct < 15 else COL_SCAN if batt_pct < 30 else COL_BAR
    draw.text((2, y), "BAT", fill=COL_TEXT, font=FONT_SM)
    draw_bar(draw, 24, y, 50, 8, batt_pct, batt_col)
    draw.text((78, y), f"{batt_v}", fill=COL_VAL, font=FONT_SM)
    y += 11

    draw.text((2, y), f"TMP {temp}", fill=COL_TEXT, font=FONT_SM)
    draw.text((64, y), f"UP {uptime}", fill=COL_TEXT, font=FONT_SM)

    return img


def main():
    print("[*] Display daemon starting...")

    prev_total, prev_idle = get_cpu()
    time.sleep(0.1)

    while True:
        # CPU delta
        total, idle = get_cpu()
        dt = total - prev_total
        di = idle - prev_idle
        cpu_pct = int((1 - di / dt) * 100) if dt > 0 else 0
        cpu_pct = max(0, min(100, cpu_pct))
        prev_total, prev_idle = total, idle

        mem_pct = get_mem()
        temp = get_temp()
        signal = get_signal()
        uptime = get_uptime()
        live = get_live()
        netstate = get_netstate()
        batt_pct, batt_v = get_battery()

        img = render(cpu_pct, mem_pct, temp, signal, uptime, live, netstate, batt_pct, batt_v)
        write_fb(rgb888_to_rgb565(img))

        time.sleep(1.0 / REFRESH_HZ)


if __name__ == "__main__":
    main()
