import sys
from playwright.sync_api import sync_playwright
URL = sys.argv[1] if len(sys.argv) > 1 else 'file:///workspace/bellarich-site/index.html'
OUT = '/workspace/bellarich-site/shots/new-portrait/'
CHROME = '/workspace/.cache/ms-playwright/chromium-1255/chrome-linux64/chrome'
tag = sys.argv[2] if len(sys.argv) > 2 else 'local'
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME, args=['--no-sandbox'])
    for name, w, h, dpr in [('pc1440', 1440, 900, 1), ('m390', 390, 844, 2)]:
        ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=dpr)
        pg = ctx.new_page(); pg.goto(URL, wait_until='load'); pg.wait_for_timeout(900)
        pg.screenshot(path=OUT + '%s-%s-hero.png' % (tag, name))
        box = pg.evaluate("()=>{const r=document.querySelector('.hero__media').getBoundingClientRect();const q=document.querySelector('.hero').getBoundingClientRect();return {media:[r.x,r.y,r.width,r.height],hero:[q.x,q.y,q.width,q.height]};}")
        print(tag, name, box)
        ctx.close()
    b.close()
