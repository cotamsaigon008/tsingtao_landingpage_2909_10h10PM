"""Prepare the official Tsingtao lockup for the badge tile.

The badge's leading slot is a 29px-tall box. The real logo is a horizontal
lockup (round emblem + wordmark) at 124x63, so it is trimmed to its ink,
re-padded evenly and re-encoded with alpha. 124px of source width covers the
widest case (a 2560px viewport scales the canvas 2.18x, putting the logo at
~124 screen px) so it is never upscaled.
"""
import os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SRC = r"os.path.join(ROOT, "assets", "logo.png")\logo.png"
DST = r"os.path.join(ROOT, "assets")\_logo.webp"

im = Image.open(SRC).convert("RGBA")
bbox = im.getbbox()                       # alpha bbox — drops the dead padding
im = im.crop(bbox)
w, h = im.size
print("trimmed :", im.size, "aspect %.3f" % (w / h))

# even breathing room so the ring is not flush against the tile edge
pad = 2
canvas = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
canvas.alpha_composite(im, (pad, pad))
canvas.save(DST, "WEBP", quality=95, method=6, exact=True)
print("webp    :", canvas.size, os.path.getsize(DST), "bytes")

# at a 29px tile height this lockup is 29 * (w/h) wide
print("tile w at 29px tall: %.1f" % (29 * canvas.width / canvas.height))
