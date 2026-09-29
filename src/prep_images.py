import os, glob, time
from PIL import Image, ImageChops, ImageFilter, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SRC = r"os.path.join(ROOT, "assets", "source-photos")"
OUT = r"os.path.join(ROOT, "assets")"
os.makedirs(OUT, exist_ok=True)

TOL   = 22      # how close to pure white counts as background
GUARD = 5       # protect this many px of anti-aliased product edge from the fill


def dilate4(m):
    """4-connected binary dilation via pixelwise max of the 4 shifts (all C-level)."""
    up = ImageChops.offset(m, 0, -1)
    dn = ImageChops.offset(m, 0,  1)
    lf = ImageChops.offset(m, -1, 0)
    rt = ImageChops.offset(m,  1, 0)
    return ImageChops.lighter(ImageChops.lighter(up, dn), ImageChops.lighter(lf, rt))


def cutout(im):
    im = im.convert("RGB")
    w, h = im.size
    r, g, b = im.split()
    mn = ImageChops.darker(ImageChops.darker(r, g), b)
    # background candidate = near-white
    bg = mn.point(lambda v: 255 if v >= 255 - TOL else 0)
    # hard "definitely product" seed = clearly not near-white, grown by GUARD px so
    # the anti-aliased silhouette can never be eaten by the fill
    fg = ImageChops.invert(bg)
    for _ in range(GUARD):
        fg = ImageChops.dilate(fg) if hasattr(ImageChops, "dilate") else dilate4(fg)

    # seed the reconstruction from the border ring
    rec = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(rec)
    d.rectangle([0, 0, w - 1, h - 1], outline=255, width=3)
    rec = ImageChops.multiply(rec, bg)

    limit = int((w + h) * 0.75)
    prev = None
    for _ in range(limit):
        rec = ImageChops.multiply(dilate4(rec), bg)
        if prev is not None and ImageChops.difference(rec, prev).getbbox() is None:
            break
        prev = rec.copy()

    # 1 = background (drop it), 0 = product (keep it)
    keep = ImageChops.invert(rec).point(lambda v: 255 if v > 127 else 0)
    # hard edge then eroded 1px: a binary alpha means the browser's downscaling
    # filter can only bleed neighbouring PRODUCT pixels, never a white halo
    keep = keep.filter(ImageFilter.MinFilter(3))
    bbox = keep.getbbox()
    if not bbox:
        return None
    im = im.crop(bbox)
    keep = keep.crop(bbox)
    im.putalpha(keep)
    return im


files = sorted(glob.glob(os.path.join(SRC, "*.jpg")))
total = 0
for f in files:
    t0 = time.time()
    base = os.path.basename(f).split("_")[0]
    orig = Image.open(f).size
    cut = cutout(Image.open(f))
    if cut is None:
        print("!! empty", base); continue
    m = 760
    if max(cut.size) > m:
        s = m / max(cut.size)
        cut = cut.resize((round(cut.width * s), round(cut.height * s)), Image.LANCZOS)
    p = os.path.join(OUT, base + ".webp")
    cut.save(p, "WEBP", quality=90, method=6)
    sz = os.path.getsize(p); total += sz
    print(f"{base} {orig} -> {cut.size} {sz/1024:6.0f} KB  {time.time()-t0:4.1f}s")

print(f"TOTAL {total/1024/1024:.2f} MB webp")
