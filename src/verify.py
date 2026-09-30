import re, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "index.html")
h = open(P, encoding="utf-8").read()
css = h[h.find("<style>"):h.find("</style>")]

def block(name):
    out = []
    clean = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    for sel, body in re.findall(r"([^{}]+)\{([^{}]*)\}", clean):
        for part in sel.split(","):
            if part.strip() == name:
                out.append((part.strip(), body))
    return out

checks = []
def chk(name, cond, detail=""):
    checks.append((("PASS" if cond else "FAIL"), name, detail))

# ---------- brand fidelity ----------
chk("brand tokens declared from the live site", all(t in h for t in
    ["--tsg-forest-950:#001f16", "--tsg-forest-700:#006b3d",
     "--tsg-gold:#b68a3a", "--tsg-red:#c62d2d"]))
chk("page base is the site background", "background:var(--tsg-forest-950)" in css)
chk("no legacy cyan survives", not re.search(
    r"#9ad9ec|#3ec8e4|#5ad2f0|#46afc8|#a9aeb5|60,224,255|130,180,255", h))
chk("official lockup inlined", "_logo" in h and h.count("data:image/webp;base64,") == 18)
# the lockup now lives in the nav only; the badge carries no image at all
chk("lockup lives in the nav, badge has no seal", 'id="brandLogo"' in h
    and 'id="brandMark"' not in h and ".badge i" not in css)
chk("badge line is the brand name", h.count("badge: 'TSINGTAO VIETNAM'") == 3)
# The static <head> is what crawlers, bookmarks and the tab title read before
# any script runs, and SALES.subject is what lands in the sales inbox. All
# three once carried the old project name, which no browser test can see.
chk("no legacy project name survives",
    not re.search(r"[Vv]ertex|Streamline the shop virtual", h))

# ---------- pixel contract that must still hold ----------
badge_body = block(".badge")[0][1]
# 198 = 158 of fitted ink + 20 of breathing room each side; the pill is still
# centred on x=587, which is the authored centre line for the hero stack
chk("badge is 198x39 r12 and still centred on 587", "width:198px;height:39px" in badge_body
    and "border-radius:12px" in badge_body and "left:488px" in badge_body)
bb = block(".badge b")[0][1]
# the label IS the badge now, so it centres itself and the fitter scales it
# about the pill's own centre, keeping the wordmark centred in every locale
chk("badge label centres itself", "justify-content:center" in bb
    and "transform-origin:50% 50%" in bb and "left:70px" not in bb)
chk("badge cap height raised to 12", "I.badge*T_, 12*T_" in h)
btn = block(".btn")[0][1]
chk("btn still clips its light bank", "overflow:hidden" in btn)
chk("btn bank is multi-stop", btn.count("#") > 20 and "#f4dfb0 1px" in btn)
chk("btn outer blur still capped at 8px", "0 0 8px rgba(0,140,90,.12)" in btn
    and not re.search(r"(?:9|1\d|[2-9]\d)\.\d+px", btn))
chk("btn ::after still 13px falloff", "rgba(244,223,176,0) 13px" in css)
chk("btn ::after still masked", "mask:linear-gradient(to top,#000 0,#000 6px" in css)
chk("btn top streak only on nav button", ".cta2::before{display:none}" in css.replace(" ", ""))
chk("nav btn geometry", "left:530.7px;top:10.5px;width:125.5px;height:39.5px" in css.replace("\n", "").replace("  ", ""))
chk("hero cta geometry", "left:526px;top:349px;width:121px;height:54.5px" in css.replace("\n", "").replace("  ", ""))
chk("both hero CTAs are anchors with inner span",
    h.count('<a class="btn" href="#" data-lead="nav-cta"><span id="ctaLabel">') == 1
    and h.count('<a class="btn cta2" href="#" data-lead="hero-cta"><span id="vpLabel">') == 1)
card_body = block(".card")[0][1]
chk("card 130x300 r12", "width:130px;height:300px" in card_body and "border-radius:12px" in card_body)
chk("nav pill geometry", "left:247px;top:3px;width:678px;height:64px;border-radius:32px" in css.replace("\n", "").replace("  ", ""))
chk("mock geometry", "left:165px;top:558px;width:842px" in css.replace("\n", "")
    and "border-radius:28px 28px 0 0" in css)
chk("mock still paints over the ring",
    "z-index:100" in block(".browser")[0][1] and "z-index:5" in block(".ring")[0][1])

# ---------- engine ----------
chk("ring constants intact", "const R = 891, PERSP = 891, N = 37, CULL = 42, SPEED = 1.9" in h)
chk("scale law intact", "Math.min(vw / W, vh / 560)" in h)
chk("entrance uses individual properties", "html.intro .badge{opacity:0;translate:0 11px;scale:.985}" in css.replace("\n", ""))
chk("entrance settles", "root.classList.remove('intro')" in h
    and "last.finished.then(settle, settle)" in h)

# ---------- catalogue ----------
ids = re.findall(r"\n\s+id:'([a-z0-9-]+)', slug:", h)
chk("10 product lines", len(ids) == 10, str(ids))
chk("every SKU has 3 locales", h.count("copy:{") == 10
    and all(h.count("vi:{ name:") == 10 for _ in [0]))
chk("numeric specs are typed, not baked into prose",
    len(re.findall(r"abv:\d", h)) == 10 and len(re.findall(r"formats:\[", h)) == 10)
chk("no price published", "price:" not in h and not re.search(r"\$\s*\d", h))
chk("catalogue shows every line, not a hand-picked few",
    "const GOODS = BY_ORDER.map" in h)
chk("tiles are real buttons", "<button type=\"button\" class=\"pgcard\"" in h)

# ---------- detail view ----------
chk("detail view exists", 'id="pgdetail"' in h and "function openDetail" in h)
chk("detail renders spec table", "pdspecs" in h and "specAbv" in h)
chk("detail renders features + pairing", "keyFeatures" in h and "foodPairing" in h)
chk("detail CTA opens the lead form", 'data-lead="product-cta"' in h)

# ---------- lead form ----------
chk("form is a real dialog", 'role="dialog" aria-modal="true"' in h)
chk("form is complete", len(re.findall(r"name:'[a-z]+',\s+type:", h)) == 9)
chk("validates before sending", "RE_MAIL" in h and "RE_PHONE" in h and "aria-invalid" in h)
chk("all three CTAs are wired", all(x in h for x in
    ['data-lead="nav-cta"', 'data-lead="hero-cta"', 'data-lead="nav-contact"']))
chk("one destination constant", "const SALES = {" in h
    and "email:" in h and "endpoint:" in h)
chk("mailto offered as a link, never a hijack",
    "const mailto = 'mailto:'" in h and "mail.href = mailto" in h
    and "location.href = mailto" not in h)
chk("form is trilingual", all(k in h for k in
    ["leadTitle:", "fName:", "rEmail:", "dietKeto:"]))

# ---------- mobile contract ----------
# The phone architecture block (10c) sits late in the sheet, so a rule declared
# next to the component it styles is silently overridden by it. Everything that
# has to hold on a handset therefore lives in ONE block at the very end.
mob = h[h.rindex("@media (max-width:700px){"):]
chk("mobile pass lives at the end of the sheet",
    "16. MOBILE PASS" in h and h.rindex("16. MOBILE PASS") > h.rindex("@media (min-width:701px)"))
# iOS zooms the viewport when a focused field is under 16px and strands the
# visitor mid-form. This is the single most common real-device complaint.
chk("phone form fields are 16px (no iOS zoom)",
    ".leadfield input,.leadfield select,.leadfield textarea{font-size:16px}" in mob)
chk("phone reading sizes are larger than desktop",
    ".pgcard b{font-size:12.5px" in mob and ".sheettitle{font-size:23px" in mob
    and ".toastrow span{font-size:15.5px" in mob)
# 44px is the touch floor, and pointer type is the real signal — a 1024px iPad
# is a finger on glass too, at a width that gets no phone rules at all
chk("coarse pointers get 44px targets",
    "@media (hover:none) and (pointer:coarse)" in mob
    and "min-height:48px" in mob and ".links a{min-height:44px" in mob)
chk("notch and home-indicator insets are respected",
    "env(safe-area-inset-top)" in h and "env(safe-area-inset-bottom)" in h)
# A landscape rule was tried and measured to make the storefront UNREACHABLE
# (the mock measured 0px tall above 700px, where the tablet architecture is
# already in force). It is not shipped, and this pins that.
chk("landscape keeps the storefront reachable",
    "orientation:landscape" not in h or ".browser{display:none}" not in h)
# the drawer close button moved off the centred locale bar
chk("drawer close clears the phone locale bar",
    ".stage.peek .peekhint{left:auto;right:14px" in mob)

# ---------- image frame contract ----------
# Every product shot is a tall cut-out (aspect 0.31-0.63). Dropped into a
# near-square frame, object-fit:contain fits by HEIGHT and the product used only
# 35-71% of the frame, which reads as a broken, half-missing image. The assets
# are fine (alpha bbox is tight on all 15) — the frame was the bug.
chk("detail stage is sized from the image, not a fixed box",
    "function matchFrame" in h and "function stageMaxH" in h
    and "padding-bottom:112%" not in h and "padding-bottom:78%" not in h)
chk("stage re-frames on thumbnail swap and on resize",
    "stage.src = U(thumb.dataset.img); matchFrame(stage);" in h
    and "if(openProduct) reframe();" in h)
chk("stage height is capped so the page stays a sane length",
    "Math.min(colW / ar, stageMaxH())" in h
    and "Math.min(470, Math.round(window.innerHeight * 0.62))" in h
    and "max-height:78vh" not in h and "max-height:70vh" not in h)
# the store grid must NOT get per-image ratios: ten tiles in a row sharing
# different aspect ratios makes the rows ragged
chk("store grid keeps one uniform frame",
    ".pgcard .ph{position:relative;aspect-ratio:.62" in h
    and "root.querySelectorAll('.pdstage img')" in h)
# banner asset is 1680x560 (3:1); a fixed 158px frame made it 4.9:1 and
# object-fit:cover threw away ~40% of the height
chk("banner frame matches the 3:1 asset, so cover crops nothing",
    ".pghero{position:relative;margin:0 26px;aspect-ratio:3/1" in h
    and "height:158px" not in h and "height:122px" not in h)
chk("thumbs are portrait, not square", ".pdthumb{width:50px;height:68px" in h)

# ---------- i18n ----------
for L in ("vi", "en", "zh"):
    seg = h[h.find("\n  %s: {" % L):]
    seg = seg[:seg.find("\n  },")] if "\n  }," in seg else seg[:4000]
    chk("locale %s complete" % L, all(re.search(r"\b%s\s*:" % k, seg) for k in
        ("h1a", "sub1", "badge", "ask", "leadTitle", "fName", "fProduct", "rConsent")))
chk("english ink targets intact",
    "en: {h1a:563.5, h1b:197.5, sub1:389, sub2:311" in h)

# ---------- drawer ----------
chk("storefront drawer intact", "function setPeek" in h and "mockTopDesign" in h)

# ---------- self containment ----------
ext = re.findall(r'(?:src|href)="(https?://[^"]+)"', h)
chk("only external ref is the font CDN", all("fonts.g" in u for u in ext), str(sorted(set(ext))))
chk("no video anywhere", "<video" not in h.lower())

fails = sum(1 for st, _, _ in checks if st == "FAIL")
for st, name, detail in checks:
    print("%-5s %s%s" % (st, name, ("   [%s]" % detail) if detail and st == "FAIL" else ""))
print("\n%d/%d passed, %d failed" % (len(checks) - fails, len(checks), fails))
print("file: %.2f MB" % (os.path.getsize(P) / 1024 / 1024))
