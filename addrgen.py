import random
from PIL import Image

END_MARKER = "<<<END>>>"

def text_to_bits(text):
    return ''.join(format(ord(c), '08b') for c in text)

def bits_to_text(bits):
    chars = []
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        chars.append(chr(int(byte, 2)))
    return ''.join(chars)

def get_valid_pixels(img):
    pixels = []
    width, height = img.size
    px = img.load()

    for y in range(height):
        for x in range(width):
            if len(px[x, y]) == 4:
                if px[x, y][3] > 0:
                    pixels.append((x, y))
            else:  # RGB
                pixels.append((x, y))

    return pixels

def encode(input_image, output_image, message, seed=12345):
    img = Image.open(input_image).convert("RGBA")
    px = img.load()

    message += END_MARKER
    bits = text_to_bits(message)

    valid_pixels = get_valid_pixels(img)

    if len(bits) > len(valid_pixels):
        raise ValueError("Address too large. Please check your address length.")

    random.seed(seed)
    positions = random.sample(valid_pixels, len(bits))

    for bit, (x, y) in zip(bits, positions):
        r, g, b, a = px[x, y]

        r = (r & ~1) | int(bit)

        px[x, y] = (r, g, b, a)

    img.save(output_image)
    print("Address encoded successfully.")


def decode(image_path, seed=12345):
    img = Image.open(image_path).convert("RGBA")
    px = img.load()

    valid_pixels = get_valid_pixels(img)

    random.seed(seed)
    positions = random.sample(valid_pixels, len(valid_pixels))

    bits = ""

    for x, y in positions:
        r, _, _, _ = px[x, y]
        bits += str(r & 1)

        if len(bits) % 8 == 0:
            text = bits_to_text(bits)
            if END_MARKER in text:
                print("Address found:")
                print(text.replace(END_MARKER, ""))
                return

    print("No address found in the image.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["encode", "decode"])
    parser.add_argument("--image", type=str, default="HCC-Coin.png")
    parser.add_argument("--output")
    parser.add_argument("--message")

    args = parser.parse_args()

    if args.mode == "encode":
        encode("HCC-Coin.png", args.output, args.message, 12345)
    else:
        decode(args.image, 12345)