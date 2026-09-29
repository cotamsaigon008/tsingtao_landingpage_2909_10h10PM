# -*- coding: utf-8 -*-
"""Measure how much of each cut-out is actually product vs dead alpha."""
import os, glob
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

d = r'os.path.join(ROOT, "assets")'
rows = []
for p in sorted(glob.glob(os.path.join(d, '*.webp'))):
    im = Image.open(p).convert('RGBA')
    a = im.getchannel('A')
    bbox = a.getbbox()
    if not bbox:
        rows.append((os.path.basename(p), im.size, None))
        continue
    w, h = im.size
    bw, bh = bbox[2] - bbox[0], bbox[3] - bbox[1]
    rows.append((os.path.basename(p), (w, h), bbox,
                 round(bw / w, 3), round(bh / h, 3), round(bw / bh, 3)))

print('%-22s %-11s %-24s %-6s %-6s %-6s' % ('file', 'canvas', 'alpha bbox', 'fillW', 'fillH', 'ar'))
for r in rows:
    if r[2] is None:
        print('%-22s %-11s EMPTY' % (r[0], r[1]))
    else:
        print('%-22s %-11s %-24s %-6s %-6s %-6s' % (r[0], str(r[1]), str(r[2]), r[3], r[4], r[5]))
