"""Compose the store mock's hero banner from four cut-out products.

Source is 3:1 on purpose: the desktop slot is ~4.9:1 and the phone slot ~2.8:1, so
a 3:1 source is the compromise that survives `object-fit:cover` at both without
clipping the product cluster. The cluster is kept inside the central band that
the 4.9:1 crop preserves, and sits right-of-centre so the headline copy owns the
empty left third.
"""
import os
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

OUT = r"os.path.join(ROOT, "assets")"
W, H = 1680, 560
BASE = 408                      # common baseline for every product

# (file stem, height scale) — widest first so the tallest sit at the back
LAYOUT = [
    ("1790417137089", 0.95),    # 2025 special edition (white)
    ("1790417137144", 0.84),    # green bottle, gold label
    ("1790417137105", 0.88),    # green bottle, red label
    ("1790417137152", 0.78),    # gold can
]

def gradient_bg():
    base = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(base)
    for x in range(W):
        t = x / W
        d.line([(x, 0), (x, H)], fill=(int(243 - 42*t), int(230 - 44*t), int(219 - 56*t)))
    glow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(glow).ellipse([W*0.44, -H*0.85, W*1.18, H*1.75], fill=150)
    glow = glow.filter(ImageFilter.GaussianBlur(160))
    return Image.composite(Image.new("RGB", (W, H), (255, 226, 172)), base, glow)

canvas = gradient_bg().convert("RGBA")
shadow = Image.new("L", (W, H), 0)
sd = ImageDraw.Draw(shadow)

x = W - 70
for name, sc in LAYOUT:
    p = Image.open(os.path.join(OUT, name + ".webp")).convert("RGBA")
    h = int(BASE * sc)
    p = p.resize((max(1, round(p.width * h / p.height)), h), Image.LANCZOS)
    x -= p.width
    y = BASE - h
    sw = int(p.width * 0.88)
    sd.ellipse([x + (p.width - sw)//2, BASE + 2, x + (p.width + sw)//2, BASE + 24], fill=125)
    canvas.alpha_composite(p, (x, y))
    x -= 30

canvas.paste(Image.new("RGBA", (W, H), (58, 34, 18, 255)), (0, 0),
             shadow.filter(ImageFilter.GaussianBlur(13)))

veil = Image.new("L", (W, H), 0)
ImageDraw.Draw(veil).rectangle([0, 0, int(W*0.44), H], fill=56)
canvas.paste(Image.new("RGBA", (W, H), (44, 26, 16, 255)), (0, 0),
             veil.filter(ImageFilter.GaussianBlur(64)))

canvas.convert("RGB").save(os.path.join(OUT, "banner.webp"), "WEBP", quality=88, method=6)
canvas.resize((840, 280), Image.LANCZOS).convert("RGB").save(
    r"os.path.join(ROOT, ".check")\banner2.jpg", quality=92)
print("banner", os.path.getsize(os.path.join(OUT, "banner.webp")) / 1024, "KB")
