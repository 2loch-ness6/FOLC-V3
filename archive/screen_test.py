import struct
from PIL import Image, ImageDraw, ImageFont

# Config
FB_PATH = "/dev/fb0"
WIDTH = 128
HEIGHT = 128

def rgb888_to_rgb565(r, g, b):
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

def write_to_fb(image):
    # Convert PIL Image to RGB565 Bytes
    pixels = image.load()
    with open(FB_PATH, "wb") as fb:
        for y in range(HEIGHT):
            for x in range(WIDTH):
                r, g, b = pixels[x, y]
                color = rgb888_to_rgb565(r, g, b)
                # Write 2 bytes (Little Endian or Big Endian? Usually LE for ARM)
                fb.write(struct.pack("<H", color))

def main():
    # Create Black Image
    img = Image.new("RGB", (WIDTH, HEIGHT), "black")
    draw = ImageDraw.Draw(img)

    # Draw Text
    text = "GEMINI"
    draw.text((30, 50), text, fill="cyan")
    draw.rectangle((10, 10, 118, 118), outline="white")
    
    print("Writing to framebuffer...")
    write_to_fb(img)
    print("Done.")

if __name__ == "__main__":
    main()
