# -*- coding: utf-8 -*-
"""Repoint the build scripts at the repository instead of a temp directory."""
import io, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HDR  = 'ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))'

MAP = {
    r'os.path.join(ROOT, "assets")':   'os.path.join(ROOT, "assets")',
    r'os.path.join(ROOT, ".check")':    'os.path.join(ROOT, ".check")',
    r'os.path.join(ROOT, "assets", "logo.png")': 'os.path.join(ROOT, "assets", "logo.png")',
    r'os.path.join(ROOT, "assets", "source-photos")':                     'os.path.join(ROOT, "assets", "source-photos")',
    r'ROOT': 'ROOT',
}

# the Tailwind/Next project that happened to host the deliverable is not part of
# this repo; index.html now lives at the root next to src/ and assets/
LEGACY = r'ROOT'

changed = []
for fn in sorted(os.listdir(os.path.join(ROOT, "src"))):
    if not fn.endswith(".py") or fn == "inject.py":
        continue
    p = os.path.join(ROOT, "src", fn)
    s = o = open(p, encoding="utf-8").read()
    for old, new in MAP.items():
        s = s.replace(old, new)
    s = s.replace(LEGACY + r'\index.html', 'os.path.join(ROOT, "index.html")')
    if "ROOT" in s and HDR not in s:
        # put the constant after the last top-level import
        lines = s.split("\n")
        last = max(i for i, l in enumerate(lines) if re.match(r'^(import |from )', l))
        lines.insert(last + 1, "\n" + HDR)
        s = "\n".join(lines)
    if s != o:
        open(p, "w", encoding="utf-8", newline="").write(s)
        changed.append(fn)

print("rewritten:", ", ".join(changed) if changed else "(none)")
