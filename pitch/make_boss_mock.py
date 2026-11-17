# P5 pitch asset: mock boss-fight screen (silhouette style), 1920x1080.
# Fallback art generated in code so the pitch never depends on an external
# image service. If a "real" AI image is wanted later, use the prompt in
# demo-runbook.md and replace boss-fight-mock.png -- nothing else changes.
#
# Run:  python pitch\make_boss_mock.py
# Out:  pitch/boss-fight-mock.png

import math
import os
import random
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "boss-fight-mock.png")

W, H = 1920, 1080
random.seed(831001)  # matches the showcase seed family; deterministic art

SKY_TOP = (10, 10, 18)
SKY_MID = (38, 22, 26)
SKY_LOW = (96, 38, 24)
GLOW = (255, 140, 50)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def sky(img):
    px = img.load()
    for y in range(H):
        t = y / H
        c = lerp(SKY_TOP, SKY_MID, min(1.0, t * 1.6)) if t < 0.62 else lerp(SKY_MID, SKY_LOW, (t - 0.62) / 0.38)
        for x in range(W):
            px[x, y] = c


def molten_glow(img):
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for i in range(5):
        r = 300 + i * 130
        a = int(120 - i * 22)
        gd.ellipse([W * 0.5 - r, H + 120 - r * 0.62, W * 0.5 + r, H + 120 + r * 0.62],
                   fill=(a, int(a * 0.5), 0))
    glow = glow.filter(ImageFilter.GaussianBlur(60))
    base = glow.convert("L").point(lambda v: min(255, v * 2))
    img.paste(Image.composite(glow, img, base), (0, 0))


def gears(dr, cx, cy, r, teeth, color):
    dr.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=6)
    dr.ellipse([cx - r * 0.35, cy - r * 0.35, cx + r * 0.35, cy + r * 0.35], outline=color, width=4)
    for i in range(teeth):
        a = i * 2 * math.pi / teeth
        x1, y1 = cx + math.cos(a) * r, cy + math.sin(a) * r
        x2, y2 = cx + math.cos(a) * (r + 14), cy + math.sin(a) * (r + 14)
        dr.line([x1, y1, x2, y2], fill=color, width=10)


def automaton(img):
    """Colossal rusted clockwork automaton, right side, weeping oil."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    body = (14, 12, 14, 255)
    edge = (66, 40, 30, 255)

    bx, by = 1290, 330          # torso top-left
    d.rounded_rectangle([bx, by, bx + 460, by + 560], 60, fill=body, outline=edge, width=6)
    d.rounded_rectangle([bx + 70, by + 90, bx + 390, by + 330], 40, outline=edge, width=5)
    # head
    d.rounded_rectangle([bx + 130, by - 170, bx + 340, by + 20], 40, fill=body, outline=edge, width=6)
    # eyes -- burning
    d.ellipse([bx + 170, by - 110, bx + 215, by - 65], fill=(255, 176, 60, 255))
    d.ellipse([bx + 265, by - 110, bx + 310, by - 65], fill=(255, 176, 60, 255))
    # raised piston arm (left arm up) -- pieces overlap so the silhouette connects
    d.rounded_rectangle([bx - 250, by - 210, bx - 60, by - 70], 30, fill=body, outline=edge, width=6)   # forearm
    d.rounded_rectangle([bx - 90, by - 110, bx + 60, by + 140], 30, fill=body, outline=edge, width=6)   # upper arm
    d.rounded_rectangle([bx - 330, by - 260, bx - 200, by - 170], 24, fill=body, outline=edge, width=6) # fist
    # legs
    d.rounded_rectangle([bx + 60, by + 540, bx + 190, by + 720], 30, fill=body, outline=edge, width=6)
    d.rounded_rectangle([bx + 280, by + 540, bx + 410, by + 720], 30, fill=body, outline=edge, width=6)
    # exposed gears in the torso
    gears(d, bx + 230, by + 200, 62, 10, edge)
    gears(d, bx + 90, by + 420, 40, 8, edge)
    gears(d, bx + 370, by + 430, 48, 9, edge)
    # oil weeping from eyes and joints
    for ox, oy, ln in [(bx + 192, by - 64, 130), (bx + 287, by - 64, 170),
                       (bx + 66, by + 92, 150), (bx + 384, by + 96, 120)]:
        d.line([ox, oy, ox - 8, oy + ln], fill=(8, 6, 8, 235), width=10)
        d.ellipse([ox - 16, oy + ln - 6, ox, oy + ln + 12], fill=(8, 6, 8, 235))
    lay = lay.filter(ImageFilter.GaussianBlur(1.2))
    img.paste(lay, (0, 0), lay)


def hero(img):
    """Tiny player character, bottom-left third, sword up."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    cx, cy = 470, 880
    c = (12, 10, 12, 255)
    d.ellipse([cx - 22, cy - 150, cx + 22, cy - 106], fill=c)            # head
    d.polygon([(cx - 34, cy - 106), (cx + 34, cy - 106), (cx + 22, cy + 10), (cx - 22, cy + 10)], fill=c)  # torso
    d.line([cx - 20, cy + 10, cx - 34, cy + 96], fill=c, width=16)       # legs
    d.line([cx + 20, cy + 10, cx + 36, cy + 96], fill=c, width=16)
    d.line([cx + 30, cy - 80, cx + 120, cy - 170], fill=c, width=12)     # sword arm
    d.line([cx + 120, cy - 170, cx + 150, cy - 250], fill=(200, 205, 220, 255), width=8)  # blade glint
    lay = lay.filter(ImageFilter.GaussianBlur(0.8))
    img.paste(lay, (0, 0), lay)


def ruins(img):
    """Silhouetted ruined foundry skyline."""
    d = ImageDraw.Draw(img, "RGBA")
    c = (16, 13, 16, 255)
    d.polygon([(0, 980), (0, 760), (140, 780), (160, 640), (240, 660), (260, 980)], fill=c)   # broken wall
    d.rectangle([330, 560, 380, 980], fill=c)                                                 # chimney
    d.rectangle([322, 548, 388, 566], fill=c)
    d.polygon([(1500, 980), (1540, 700), (1660, 720), (1700, 980)], fill=c)
    d.rectangle([0, 960, W, H], fill=c)                                                       # ground


def embers(img):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for _ in range(220):
        x, y = random.uniform(0, W), random.uniform(H * 0.35, H)
        r = random.uniform(1.2, 4.2)
        a = int(90 + 150 * (1 - y / H))
        warm = (255, random.randint(120, 190), random.randint(30, 70), a)
        d.ellipse([x - r, y - r, x + r, y + r], fill=warm)
    lay = lay.filter(ImageFilter.GaussianBlur(0.7))
    img.paste(lay, (0, 0), lay)


def vignette(img):
    mask = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse([-W * 0.25, -H * 0.35, W * 1.25, H * 1.35], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(160))
    black = Image.new("RGB", (W, H), (0, 0, 0))
    img.paste(black, (0, 0), mask.point(lambda v: 255 - v))


def main():
    img = Image.new("RGB", (W, H), SKY_TOP)
    sky(img)
    molten_glow(img)
    ruins(img)
    automaton(img)
    hero(img)
    embers(img)
    vignette(img)
    img.save(OUT)
    print("saved", OUT, img.size)


if __name__ == "__main__":
    main()
