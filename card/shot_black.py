"""Screenshot /card/ at 390 and 1440 for the black-suit hero swap.

usage: python3 card/shot_black.py <url> <outprefix> [tag]
"""
import sys
from playwright.sync_api import sync_playwright

URL = sys.argv[1]
PFX = sys.argv[2]

with sync_playwright() as p:
    b = p.chromium.launch()
    for name, w, h, dpr in [('390', 390, 844, 2), ('1440', 1440, 900, 1)]:
        ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=dpr,
                            is_mobile=w < 700, has_touch=w < 700)
        pg = ctx.new_page()
        errs = []
        pg.on('console', lambda m: errs.append(m.type + ':' + m.text) if m.type == 'error' else None)
        pg.on('pageerror', lambda e: errs.append('pageerror:' + str(e)))
        pg.goto(URL, wait_until='load')
        pg.wait_for_timeout(1500)
        pg.evaluate("() => document.fonts && document.fonts.ready")
        pg.wait_for_timeout(400)
        # full page + hero-only crops
        pg.screenshot(path=f'/workspace/downloads/card_black_{PFX}_%s.png' % name, full_page=(name == '390'))
        pg.screenshot(path=f'/workspace/downloads/card_black_{PFX}_{name}_top.png')
        vis = pg.evaluate("""() => {
          const i = document.querySelector('.hero__photo img');
          const r = i.getBoundingClientRect();
          return {w:+r.width.toFixed(1), h:+r.height.toFixed(1), nw:i.naturalWidth, nh:i.naturalHeight,
                  err: document.documentElement.scrollWidth - document.documentElement.clientWidth};
        }""")
        print(name, vis, 'err', errs)
        ctx.close()
    b.close()
