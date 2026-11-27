import json
import sys
from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else 'file:///workspace/bellarich-site/card/index.html'
OUT = '/workspace/bellarich-site/shots/card/'
PFX = sys.argv[2] if len(sys.argv) > 2 else 'local'

JS_METRICS = """() => {
  const d = document.documentElement, b = document.body;
  const card = document.querySelector('.card');
  const cr = card.getBoundingClientRect();
  const q = s => { const e = document.querySelector(s); if(!e) return null; const r = e.getBoundingClientRect();
    return {t:+r.top.toFixed(1), b:+r.bottom.toFixed(1), l:+r.left.toFixed(1), r:+r.right.toFixed(1), w:+r.width.toFixed(1), h:+r.height.toFixed(1)}; };
  return {
    vw: window.innerWidth, vh: window.innerHeight,
    scrollW: d.scrollWidth, clientW: d.clientWidth,
    overflowX: d.scrollWidth - d.clientWidth,
    docH: d.scrollHeight,
    card: {w:+cr.width.toFixed(1), l:+cr.left.toFixed(1), r:+cr.right.toFixed(1), h:+cr.height.toFixed(1)},
    hero: q('.hero'), actions: q('.actions'), links: q('.links'), sns: q('.sns'), foot: q('.foot'),
    photo: q('.hero__photo img'), logo: q('.br-logo'), name: q('.hero__name'),
    firstLink: q('.lk--navy')
  };
}"""

with sync_playwright() as p:
    b = p.chromium.launch()

    # mobile
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2,
                        is_mobile=True, has_touch=True,
                        user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1')
    pg = ctx.new_page()
    errors = []
    pg.on('console', lambda m: errors.append('console:' + m.type + ':' + m.text) if m.type == 'error' else None)
    pg.on('pageerror', lambda e: errors.append('pageerror:' + str(e)))
    pg.goto(URL, wait_until='load')
    pg.wait_for_timeout(1500)
    pg.evaluate("() => document.fonts && document.fonts.ready")
    pg.wait_for_timeout(600)
    print('MOBILE', json.dumps(pg.evaluate(JS_METRICS), ensure_ascii=False))
    pg.screenshot(path=OUT + PFX + '-m390-top.png')
    pg.screenshot(path=OUT + PFX + '-m390-full.png', full_page=True)
    # 360 check
    ctx.close()

    ctx = b.new_context(viewport={'width': 360, 'height': 780}, device_scale_factor=2, is_mobile=True, has_touch=True)
    pg = ctx.new_page(); pg.goto(URL, wait_until='load'); pg.wait_for_timeout(1200)
    print('M360', json.dumps({k: v for k, v in pg.evaluate(JS_METRICS).items() if k in ('overflowX', 'scrollW', 'card', 'docH')}, ensure_ascii=False))
    pg.screenshot(path=OUT + PFX + '-m360-top.png')
    ctx.close()

    # desktop
    for label, w, h, dpr in [('1440', 1440, 900, 1), ('1440', 1440, 900, 2)]:
        ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=dpr)
        pg = ctx.new_page()
        pg.on('console', lambda m: errors.append('console:' + m.type + ':' + m.text) if m.type == 'error' else None)
        pg.on('pageerror', lambda e: errors.append('pageerror:' + str(e)))
        pg.goto(URL, wait_until='load'); pg.wait_for_timeout(1500)
        pg.evaluate("() => document.fonts && document.fonts.ready")
        pg.wait_for_timeout(600)
        print('DESK', dpr, json.dumps(pg.evaluate(JS_METRICS), ensure_ascii=False))
        if dpr == 1:
            pg.screenshot(path=OUT + PFX + '-pc1440-top.png')
            pg.screenshot(path=OUT + PFX + '-pc1440-full.png', full_page=True)
        ctx.close()

    print('ERRORS', json.dumps(errors, ensure_ascii=False))
    b.close()
