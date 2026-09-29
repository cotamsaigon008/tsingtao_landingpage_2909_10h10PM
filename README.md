# Tsingtao Landing Page

A single self-contained `index.html` for the Tsingtao beer range. No build
framework, no runtime dependencies, no external requests — one file you can
open from a USB stick, email, or any static host.

**Vietnamese · English · 中文** · 10 products · 0 % ABV to 5.2 % ABV.

---

## The one thing to know

`index.html` is **generated. Do not edit it.**

```
src/template.html   ──inject.py──▶   index.html
    188 KB                            1.38 MB
     ▲                                  │
     └── edit here                      └── this is what ships
```

The 17 product photos are inlined as base64 (~1.05 MB of the 1.38 MB). They
live in `src/template.html` behind a single `/*__DATA__*/{}` placeholder that
`inject.py` fills. Hand-editing the output means hand-editing a 60,000-character
line of base64, and the next build overwrites it anyway.

### Build

```bash
python src/inject.py     # regenerate index.html
python src/verify.py     # must print 63/63 passed
```

Both need Pillow (`pip install pillow`) for `inject.py`.

### Serve it

```bash
python -m http.server 8899
# http://127.0.0.1:8899/index.html
```

Opening the file directly with `file://` also works.

---

## Layout

```
index.html              the deliverable — generated, do not edit
src/
  template.html         ← THE FILE YOU EDIT
  catalog_block.js      the 10-product catalogue, as a standalone JS module
  inject.py             assets → base64 → index.html
  verify.py             63 static checks; run this after every edit
  prep_images.py        source photos → background-keyed WebP cut-outs
  fix089.py             manual repair for one cut-out the keyer could not do
  banner.py             composites the storefront banner
  prep_logo.py          the official lockup → WebP
  measure_alpha.py      reports how much of each cut-out is product vs padding
  relocate.py           one-shot: repoints paths after moving the project
assets/
  *.webp                17 inlined assets (15 products + banner + logo)
  logo.png              the official Tsingtao lockup, as pulled
  source-photos/        the original photographs, kept for re-keying
```

---

## Where things live in the source

| What | Where in `template.html` |
|---|---|
| The 10 products, 3 languages | `const CATALOG` — swap `catalog_block.js` in here |
| All other UI strings, 3 languages | `const I18N` |
| "Nguồn gốc" / "Hướng dẫn" panel copy | `const SHEETS` |
| Where enquiries go | `const SALES` |
| Support phone + inbox | `const SUPPORT` |
| Layout scales & breakpoints | `const CW`, `resize()` |
| Type fitter (fits text to a fixed ink width) | `fitBox()`, `const INK` |

### Two constants need real values

```js
const SALES = {
  email:    'sales@tsingtao.com.vn',   // ← where enquiries should land
  endpoint: '',                        // ← a form endpoint, e.g. Formspree
};

const SUPPORT = {
  phone: '1900 2028',                  // ← the real hotline
  email: 'hotline@tsingtao.com.vn',    // ← the real support inbox
  tel:   '19002028'                    // ← digits only, for the tel: link
};
```

With `SALES.endpoint` empty the form falls back to a prefilled `mailto:` link
rather than silently navigating away, so an enquiry is never lost.

---

## The rules that keep it from drifting

`verify.py` encodes 63 of them. The ones that bite hardest:

**A product is a SKU, not a flavour family.** Tsingtao sells the same lager in a
330 bottle, a 640 bottle and a 500 can, and each is a real product with its own
occasion and its own copy. Adding a pack means adding a record, not editing one.

**Specifications are never restated in prose.** ABV, volume, ingredients and
energy are rendered from `specs`, so a copy edit cannot contradict a spec edit.

**Prices are never published.** The tiles carry no price and no contact line;
the tile itself is the control, and the enquiry CTA lives on the detail page it
opens.

**The frame follows the image.** Product shots are tall cut-outs (aspect
0.31–0.63). Dropped into a fixed-ratio frame, `object-fit:contain` fits by height
and the product uses only 35 % of the box. `matchFrame()` therefore sizes the
stage from the image's own `naturalWidth/naturalHeight`, capped at 62 % of the
viewport height so the page stays a sensible length. Tiles keep one uniform
frame on purpose — per-tile ratios make the grid rows ragged.

**Desktop geometry is authored, not computed.** The hero's coordinate table in
the spec is pixel-contract; `verify.py` checks the numbers that were fixed by
hand. Read them before moving anything in the canvas layer.

---

## Verified against

320×568 · 375×667 · 390×844 · 430×932 · 667×375 · 744×1133 · 820×1180 ·
1024×768 · 844×390 · 1440×900 · 1920×1080

No horizontal overflow at any of them. Storefront reachable, product detail
fits, and every product image fills ≥ 85 % of its frame — checked across
3 languages × 10 products on each device.

---

## Known trade-off

The file is 1.38 MB, which is one request but a slow first paint on 3G/4G.
Splitting the images out would fix that and break the "one self-contained file"
requirement. The requirement won. If that changes, `inject.py` is the only
script that needs to know.
