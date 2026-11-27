"""Render card/og-image.jpg (1200x630) for Kakao/social sharing.

Matches the 2026-11-27 card: charcoal suit portrait on the studio grey
backdrop (no cutout, no navy panel). The right panel carries a portrait crop
of the same photo the hero uses, so the shared preview and the card agree.
Run from bellarich-site:

    python3 card/make_card_og.py

Writes assets/card-og-portrait.webp (panel crop), assets/card-og.png (lossless
master) and assets/card-og.jpg (deployed as card/og-image.jpg).
"""
import base64
import pathlib

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path('/workspace/bellarich-site')
SRC = ROOT / 'assets' / '_src_ceo-charcoal.png'
SRC_HTML = ROOT / 'card' / 'og-template.html'
OUT_HTML = ROOT / 'card' / '.og-build.html'
OUT_PORTRAIT = ROOT / 'assets' / 'card-og-portrait.webp'
OUT_PNG = ROOT / 'assets' / 'card-og.png'
OUT_JPG = ROOT / 'assets' / 'card-og.jpg'
W, H, DPR = 1200, 630, 2

# right panel is 396x510 (aspect .7765); crop the photo to that, full width
PANEL_W, PANEL_H, PANEL_Y0 = 396, 510, 25


def panel_crop() -> pathlib.Path:
    im = Image.open(SRC).convert('RGB')
    h = round(im.width * PANEL_H / PANEL_W)
    box = (0, PANEL_Y0, im.width, min(im.height, PANEL_Y0 + h))
    crop = im.crop(box)
    crop.save(OUT_PORTRAIT, 'WEBP', quality=88, method=6)
    print('wrote', OUT_PORTRAIT, crop.size, 'from', box)
    return OUT_PORTRAIT


html = SRC_HTML.read_text(encoding='utf-8')
html = html.replace('__LOGO__', (ROOT / 'assets' / 'logo-symbol.html').read_text(encoding='utf-8').strip())
OUT_HTML.write_text(html, encoding='utf-8')

photo = 'data:image/webp;base64,' + base64.b64encode(panel_crop().read_bytes()).decode()

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width': W, 'height': H}, device_scale_factor=DPR)
    pg = ctx.new_page()
    pg.goto(OUT_HTML.as_uri(), wait_until='load')
    pg.evaluate("(d) => { document.getElementById('ceo').src = d; }", photo)
    pg.evaluate("() => document.fonts.ready")
    pg.wait_for_timeout(1200)
    pg.screenshot(path=str(OUT_PNG))
    b.close()

im = Image.open(OUT_PNG).convert('RGB')
im = im.resize((W, H), Image.LANCZOS)
im.save(OUT_JPG, 'JPEG', quality=92, optimize=True, progressive=True)
print('wrote', OUT_PNG, OUT_JPG, OUT_JPG.stat().st_size, 'bytes')
