"""Repair the white-bodied 2025 bottle: its artwork does not form a closed
barrier, so a border flood-fill leaks straight through the glass. Rebuild the
silhouette from the horizontal extent of the artwork on each row instead."""
from PIL import Image, ImageChops, ImageFilter

import glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = glob.glob(r"os.path.join(ROOT, "assets", "source-photos")\1790417137089_*.jpg")[0]
OUT = r"os.path.join(ROOT, "assets")\1790417137089.webp"

im = Image.open(SRC).convert("RGB")
w, h = im.size
r, g, b = im.split()
mn = ImageChops.darker(ImageChops.darker(r, g), b)
# "ink" = anything clearly darker or more saturated than the white glass
px = mn.load()
xs = list(range(w))
ink = []
for y in range(h):
    row = [x for x in xs if px[x, y] < 236]
    ink.append((min(row), max(row)) if row else None)

PAD = 7          # grow each row's span so the glass edge is included
mask = Image.new("L", (w, h), 0)
mp = mask.load()
for y in range(h):
    s = ink[y]
    if not s:
        continue
    a, z = max(0, s[0] - PAD), min(w - 1, s[1] + PAD)
    for x in range(a, z + 1):
        mp[x, y] = 255

# fill the cap/shoulder: any row with no ink inherits the nearest row that had one
last = None
for y in range(h):
    if ink[y] is None:
        if last:
            a, z = last
            for x in range(max(0, a - PAD), min(w - 1, z + PAD) + 1):
                mp[x, y] = 255
    else:
        last = ink[y]

mask = mask.filter(ImageFilter.MinFilter(3))       # hard 1px-eroded edge
bbox = mask.getbbox()
im = im.crop(bbox); mask = mask.crop(bbox)
im.putalpha(mask)
m = 760
s = m / max(im.size)
im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
im.save(OUT, "WEBP", quality=90, method=6)
print("rebuilt", im.size)

# proof sheet
bg = Image.new("RGBA", im.size, (12, 18, 30, 255))
bg.alpha_composite(im)
bg.convert("RGB").save(r"os.path.join(ROOT, ".check")\fix089.jpg", quality=92)
