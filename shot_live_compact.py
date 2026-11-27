import os
from playwright.sync_api import sync_playwright

OUT = '/workspace/bellarich-site/shots/hero-quality/'
URL = 'https://bellarich.co.kr/?v=1125w'

JS = """async () => {
  const R = el => { const r = el.getBoundingClientRect();
    return {x:+r.left.toFixed(1), y:+r.top.toFixed(1), w:+r.width.toFixed(1), h:+r.height.toFixed(1)}; };
  const m = document.querySelector('.hero__media');
  const cs = getComputedStyle(m);
  const url = cs.backgroundImage.slice(5, -2);
  const nat = await new Promise(res => { const i = new Image();
    i.onload = () => res([i.naturalWidth, i.naturalHeight]); i.onerror = () => res(null); i.src = url; });
  const box = R(m);
  const s = Math.min(box.w / nat[0], box.h / nat[1]);
  const h1 = R(document.querySelector('.hero h1'));
  return {box, nat, draw: {w:+(nat[0]*s).toFixed(1), h:+(nat[1]*s).toFixed(1)},
          h1_right: h1.x + h1.w, scrollW: document.documentElement.scrollWidth};
}"""

with sync_playwright() as p:
    b = p.chromium.launch()
    # 1440x900 DRP1 — the requested PC shot
    ctx = b.new_context(viewport={'width': 1440, 'height': 900}, device_scale_factor=1)
    pg = ctx.new_page(); pg.goto(URL, wait_until='load'); pg.wait_for_timeout(1200)
    pg.screenshot(path=OUT + 'pc1440-compact-hero.png')
    d = pg.evaluate(JS)
    print('live 1440 dpr1:', d)
    ctx.close()

    for label, w, h, dpr in [('1366', 1366, 768, 1), ('1920', 1920, 1080, 1),
                             ('1440dpr2', 1440, 900, 2), ('390', 390, 844, 2)]:
        ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=dpr)
        pg = ctx.new_page(); pg.goto(URL, wait_until='load'); pg.wait_for_timeout(1200)
        pg.screenshot(path=OUT + 'live-%s-compact-hero.png' % label)
        if label == '1440dpr2':
            box = d['box']
            pg.screenshot(path=OUT + 'live-1440dpr2-compact-face.png',
                          clip={'x': box['x'] + box['w'] * 0.32, 'y': box['y'] + box['h'] * 0.10,
                                'width': 280, 'height': 240})
        ctx.close()
    b.close()
print('done')
