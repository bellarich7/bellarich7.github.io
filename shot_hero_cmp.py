import sys
from playwright.sync_api import sync_playwright

PAIRS = [('before', 'file:///workspace/bellarich-site/_before_index.html'),
         ('after',  'file:///workspace/bellarich-site/index.html')]
OUT = '/workspace/bellarich-site/shots/hero-quality/'

with sync_playwright() as p:
    b = p.chromium.launch()
    for tag, url in PAIRS:
        # 1440x900 at DPR 1 — the same frame as shots/pc-home/pc-1440-top.png
        ctx = b.new_context(viewport={'width': 1440, 'height': 900}, device_scale_factor=1)
        pg = ctx.new_page(); pg.goto(url, wait_until='load'); pg.wait_for_timeout(700)
        pg.screenshot(path=OUT + '%s-pc1440-top.png' % tag)
        pg.locator('.hero__media').screenshot(path=OUT + '%s-pc1440-heromedia.png' % tag)
        ctx.close()

        # 1440x900 at DPR 2 — what a retina laptop actually asks for
        ctx = b.new_context(viewport={'width': 1440, 'height': 900}, device_scale_factor=2)
        pg = ctx.new_page(); pg.goto(url, wait_until='load'); pg.wait_for_timeout(700)
        pg.screenshot(path=OUT + '%s-pc1440-dpr2-top.png' % tag)
        box = pg.evaluate("""() => { const r = document.querySelector('.hero__media').getBoundingClientRect();
            return {x:r.left, y:r.top, w:r.width, h:r.height}; }""")
        # face region, 1:1 device pixels
        x = box['x'] + box['w'] * 0.30; y = box['y'] + box['h'] * 0.10
        pg.screenshot(path=OUT + '%s-face-dpr2.png' % tag,
                      clip={'x': x, 'y': y, 'width': 300, 'height': 260})
        ctx.close()
    b.close()
print('done')
