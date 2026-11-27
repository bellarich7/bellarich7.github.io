import sys
from playwright.sync_api import sync_playwright

URL = sys.argv[1]
PFX = sys.argv[2] if len(sys.argv) > 2 else 'chk'
OUT = '/workspace/bellarich-site/shots/card/'
JS = """() => {
  const de = document.documentElement;
  const rows = [...document.querySelectorAll('.info__row')].map(r => Math.round(r.getBoundingClientRect().height));
  const lks = [...document.querySelectorAll('.lk')].map(r => Math.round(r.getBoundingClientRect().height));
  const overflowers = [...document.querySelectorAll('.card *')].filter(e => {
      const r = e.getBoundingClientRect(); return r.right > de.clientWidth + 0.5 || r.left < -0.5;
  }).map(e => (e.className||e.tagName) + ':' + Math.round(e.getBoundingClientRect().right));
  const small = [...document.querySelectorAll('a,button')].filter(e => {
      const r = e.getBoundingClientRect(); return r.width > 0 && (r.height < 40 || r.width < 24); })
      .map(e => (e.textContent || '').trim().slice(0, 14) + ':' + Math.round(e.getBoundingClientRect().height));
  const lkW = [...document.querySelectorAll('.lk__t')].map(t => {
      const r = t.getBoundingClientRect(); return Math.round(r.width); });
  return {docH: de.scrollHeight, overflowX: de.scrollWidth - de.clientWidth,
          rows, lks, lkW, overflowers, small};
}"""
with sync_playwright() as p:
    b = p.chromium.launch()
    for w, h in [(320, 640), (360, 780), (390, 844), (414, 896), (768, 1024), (1440, 900)]:
        ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2 if w < 700 else 1,
                            is_mobile=w < 700, has_touch=w < 700)
        pg = ctx.new_page()
        errs = []
        pg.on('console', lambda m: errs.append(m.type + ':' + m.text) if m.type == 'error' else None)
        pg.on('pageerror', lambda e: errs.append('pageerror:' + str(e)))
        pg.goto(URL, wait_until='load')
        pg.wait_for_timeout(1200)
        pg.evaluate("() => document.fonts && document.fonts.ready")
        pg.wait_for_timeout(300)
        r = pg.evaluate(JS)
        print(w, r, 'err', errs)
        if w in (320, 414):
            pg.screenshot(path=OUT + PFX + '-m%d-top.png' % w)
        ctx.close()
    b.close()
