# -*- coding: utf-8 -*-
"""Build the deliverable: inline every asset as base64 into the template.

    python src/inject.py

Reads  src/template.html   (EDIT THIS, never index.html)
Writes index.html          (generated, 1.38 MB, self-contained)

Paths are resolved relative to the repository root, so the project can be
cloned anywhere and still build.
"""
import base64, io, json, os, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG  = os.path.join(ROOT, "assets")
TPL  = os.path.join(ROOT, "src", "template.html")
DEST = os.path.join(ROOT, "index.html")

# key -> file stem in assets/. Keys are the short handles the catalogue uses
# (media.tile / media.gallery), never filenames, so an asset can be swapped
# without touching a line of copy.
KEY = {
    "052":  "1790417137052", "066":  "1790417137066", "078":  "1790417137078",
    "089":  "1790417137089", "097":  "1790417137097", "105":  "1790417137105",
    "113":  "1790417137113", "121":  "1790417137121", "129":  "1790417137129",
    "136":  "1790417137136", "144":  "1790417137144", "152":  "1790417137152",
    "159":  "1790417137159", "167":  "1790417137167", "9206": "1790417149206",
    "banner": "banner",
    # the official Tsingtao lockup, pulled from the brand's own site
    "_logo": "_logo",
}

MIME = {"webp": "image/webp", "png": "image/png", "jpg": "image/jpeg"}

missing = [k for k, s in KEY.items() if not os.path.exists(os.path.join(IMG, s + ".webp"))]
if missing:
    sys.exit("missing assets for keys: %s" % ", ".join(missing))

out, total = {}, 0
for key, stem in KEY.items():
    p = os.path.join(IMG, stem + ".webp")
    ext = p.rsplit(".", 1)[1]
    with Image.open(p) as im:
        buf = io.BytesIO()
        im.convert("RGBA").save(buf, "WEBP", quality=90, method=6)   # re-encode lossless-ish
        raw = buf.getvalue()
    b64 = base64.b64encode(raw).decode("ascii")
    total += len(raw)
    out[key] = "data:%s;base64,%s" % (MIME[ext], b64)

# utf-8-sig: tolerate a stray BOM. A PowerShell Set-Content -Encoding UTF8 once
# wrote one, and the doctype assertion below is what caught it.
html = open(TPL, encoding="utf-8-sig").read()
assert html.startswith("<!doctype html>"), "document must start with the doctype, not a BOM"
assert "/*__DATA__*/{}" in html, "placeholder missing"
html = html.replace("/*__DATA__*/{}", json.dumps(out, separators=(",", ":")))
open(DEST, "w", encoding="utf-8").write(html)

print("images :", len(out))
print("raw    : %.2f MB" % (total / 1024 / 1024))
print("index  : %.2f MB" % (os.path.getsize(DEST) / 1024 / 1024))
print("written:", DEST)
