"""Live captures + before/after sheet for the card hero swap (2026-11-27)."""
import pathlib

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

URL = 'https://bellarich.co.kr/card/?v=1127e'
OUT = pathlib.Path('/workspace/downloads')

with sync_playwright() as p:
    b = p.chromium.launch()
    for name, w, h, dpr in [('390', 390, 844, 2), ('1440', 1440, 900, 1)]:
        ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=dpr,
                            is_mobile=w < 700, has_touch=w < 700)
        pg = ctx.new_page()
        errs = []
        pg.on('console', lambda m: errs.append(m.type + ':' + m.text) if m.type == 'error' else None)
        pg.on('pageerror', lambda e: errs.append('pageerror:' + str(e)))
        resp = pg.goto(URL, wait_until='load')
        pg.wait_for_timeout(1500)
        pg.evaluate("() => document.fonts && document.fonts.ready")
        pg.wait_for_timeout(400)
        pg.screenshot(path=str(OUT / f'card_final_{name}.png'), full_page=True)
        pg.screenshot(path=str(OUT / f'card_black_after_{name}.png'), full_page=True)
        print(name, resp.status, 'err', errs)
        ctx.close()
    b.close()

# before/after sheet at 390
before = Image.open(OUT / 'card_black_before_390.png').convert('RGB')
after = Image.open(OUT / 'card_black_after_390.png').convert('RGB')
scale = min(1.0, 900 / before.width)
if scale < 1:
    before = before.resize((int(before.width * scale), int(before.height * scale)), Image.LANCZOS)
    after = after.resize((int(after.width * scale), int(after.height * scale)), Image.LANCZOS)
h = max(before.height, after.height)
gap, lab = 24, 46
sheet = Image.new('RGB', (before.width + after.width + gap, h + lab), 'white')
sheet.paste(before, (0, lab))
sheet.paste(after, (before.width + gap, lab))
d = ImageDraw.Draw(sheet)
try:
    f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 26)
except OSError:
    f = ImageFont.load_default()
d.text((10, 10), 'BEFORE  (390)', fill='#444', font=f)
d.text((before.width + gap + 10, 10), 'AFTER  (390)', fill='#0B1933', font=f)
sheet.save(OUT / 'card_black_before_after_390.png')
print('wrote comparison', sheet.size)
