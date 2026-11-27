from playwright.sync_api import sync_playwright
OUT = '/workspace/bellarich-site/shots/hero-quality/'
PAIRS = [('before', 'file:///workspace/bellarich-site/_before_index.html'),
         ('after',  'file:///workspace/bellarich-site/index.html')]
for tag, url in PAIRS:
    with sync_playwright() as p:
        b = p.chromium.launch()
        for label, w, h in [('m390', 390, 844), ('m360', 360, 740)]:
            ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2)
            pg = ctx.new_page(); pg.goto(url, wait_until='load'); pg.wait_for_timeout(600)
            pg.screenshot(path=OUT + 'mobile-%s-%s-hero.png' % (tag, label))
            pg.screenshot(path=OUT + 'mobile-%s-%s-full.png' % (tag, label), full_page=False)
            ctx.close()
        b.close()
print('ok')
