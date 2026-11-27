from playwright.sync_api import sync_playwright
OUT = '/workspace/bellarich-site/shots/hero-quality/'
PAIRS = [('before', 'file:///workspace/bellarich-site/_before_index.html'),
         ('after',  'file:///workspace/bellarich-site/index.html')]
VPS = [('pc1440', 1440, 900, 1), ('pc1366', 1366, 768, 1), ('tab768', 768, 1024, 1), ('m390', 390, 844, 2)]
with sync_playwright() as p:
    b = p.chromium.launch()
    for tag, url in PAIRS:
        for label, w, h, dpr in VPS:
            ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=dpr)
            pg = ctx.new_page(); pg.goto(url, wait_until='load'); pg.wait_for_timeout(500)
            pg.evaluate("""() => { const el = document.querySelector('#philosophy');
                window.scrollTo(0, el.getBoundingClientRect().top + window.scrollY - 40); }""")
            pg.wait_for_timeout(900)
            # reveal animations
            pg.evaluate("() => document.querySelectorAll('.rv').forEach(e => e.classList.add('is-in','in','rv--in'))")
            pg.wait_for_timeout(500)
            pg.screenshot(path=OUT + 'video-%s-%s.png' % (tag, label))
            pg.locator('.philo__video').screenshot(path=OUT + 'videocard-%s-%s.png' % (tag, label))
            ctx.close()
    b.close()
print('ok')
