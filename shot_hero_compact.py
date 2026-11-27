import os
from playwright.sync_api import sync_playwright

OUT = '/workspace/bellarich-site/shots/hero-quality/compact/'
os.makedirs(OUT, exist_ok=True)

PAIRS = [('before', 'file:///workspace/tmp/deploy-backup-heroq/index.html'),
         ('after',  'file:///workspace/bellarich-site/index.html')]

VPS = [('1440', 1440, 900, 1), ('1920', 1920, 1080, 1), ('1366', 1366, 768, 1),
       ('1180', 1180, 800, 1), ('1080', 1080, 800, 1), ('900', 900, 1180, 1),
       ('768', 768, 1024, 1), ('390', 390, 844, 2)]

with sync_playwright() as p:
    b = p.chromium.launch()
    for tag, url in PAIRS:
        for label, w, h, dpr in VPS:
            ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=dpr)
            pg = ctx.new_page(); pg.goto(url, wait_until='load'); pg.wait_for_timeout(700)
            pg.screenshot(path=OUT + '%s-%s-top.png' % (tag, label))
            ctx.close()
        # 1440 hero area only + media element, and DPR2 face crop
        ctx = b.new_context(viewport={'width': 1440, 'height': 900}, device_scale_factor=1)
        pg = ctx.new_page(); pg.goto(url, wait_until='load'); pg.wait_for_timeout(700)
        pg.locator('.hero__media').screenshot(path=OUT + '%s-1440-media.png' % tag)
        ctx.close()

        ctx = b.new_context(viewport={'width': 1440, 'height': 900}, device_scale_factor=2)
        pg = ctx.new_page(); pg.goto(url, wait_until='load'); pg.wait_for_timeout(700)
        pg.screenshot(path=OUT + '%s-1440-dpr2-top.png' % tag)
        box = pg.evaluate("""() => { const r = document.querySelector('.hero__media').getBoundingClientRect();
            return {x:r.left, y:r.top, w:r.width, h:r.height}; }""")
        x = box['x'] + box['w'] * 0.30; y = box['y'] + box['h'] * 0.10
        pg.screenshot(path=OUT + '%s-1440-dpr2-face.png' % tag,
                      clip={'x': x, 'y': y, 'width': 300, 'height': 260})
        ctx.close()
    b.close()
print('done')
