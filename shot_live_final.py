import json
from playwright.sync_api import sync_playwright
OUT = '/workspace/bellarich-site/shots/hero-quality/'
URL = 'https://bellarich.co.kr/?v=1125u'

JS_CARD = """() => {
  const R = el => el.getBoundingClientRect();
  const card = document.querySelector('.philo__video');
  const inner = document.querySelector('.philo__video .video-card');
  const wrap = card.closest('.wrap');
  const cs = getComputedStyle(wrap);
  const wr = R(wrap);
  const boxL = wr.left + parseFloat(cs.paddingLeft), boxR = wr.right - parseFloat(cs.paddingRight);
  const c = R(inner);
  return {vw: window.innerWidth, cardW: +c.width.toFixed(1),
          gapLeft: +(c.left - boxL).toFixed(1), gapRight: +(boxR - c.right).toFixed(1),
          offsetFromViewportCentre: +((c.left + c.right)/2 - window.innerWidth/2).toFixed(1)};
}"""
JS_IMG = """async () => {
  const m = document.querySelector('.hero__media');
  const cs = getComputedStyle(m); const r = m.getBoundingClientRect();
  const url = cs.backgroundImage.slice(5, -2);
  const nat = await new Promise(res => { const i = new Image();
    i.onload = () => res([i.naturalWidth, i.naturalHeight]); i.src = url; });
  const s = Math.min(r.width/nat[0], r.height/nat[1]);
  return {box:[+r.width.toFixed(1), +r.height.toFixed(1)], nat,
          draw:[+(nat[0]*s).toFixed(1), +(nat[1]*s).toFixed(1)], dpr: window.devicePixelRatio};
}"""

with sync_playwright() as p:
    b = p.chromium.launch()
    # 1440 x 900, DPR 1 : same frame as shots/pc-home/pc-1440-top.png
    ctx = b.new_context(viewport={'width': 1440, 'height': 900}, device_scale_factor=1)
    pg = ctx.new_page(); pg.goto(URL, wait_until='load'); pg.wait_for_timeout(1200)
    pg.screenshot(path=OUT + 'live-1440-top.png')
    print('1440 image', json.dumps(pg.evaluate(JS_IMG)))
    print('1440 card ', json.dumps(pg.evaluate(JS_CARD)))
    pg.evaluate("() => document.querySelectorAll('.rv').forEach(e => e.classList.add('is-in','in','rv--in'))")
    pg.evaluate("""() => { const el = document.querySelector('.philo__video');
        window.scrollTo(0, el.getBoundingClientRect().top + window.scrollY - 90); }""")
    pg.wait_for_timeout(900)
    pg.screenshot(path=OUT + 'live-1440-video.png')
    ctx.close()

    # 1440 x 900 at DPR 2 : retina laptop
    ctx = b.new_context(viewport={'width': 1440, 'height': 900}, device_scale_factor=2)
    pg = ctx.new_page(); pg.goto(URL, wait_until='load'); pg.wait_for_timeout(1200)
    pg.screenshot(path=OUT + 'live-1440-dpr2-top.png')
    box = pg.evaluate("""() => { const r = document.querySelector('.hero__media').getBoundingClientRect();
        return {x:r.left, y:r.top, w:r.width, h:r.height}; }""")
    pg.screenshot(path=OUT + 'live-1440-dpr2-face.png',
                  clip={'x': box['x'] + box['w']*0.30, 'y': box['y'] + box['h']*0.10, 'width': 300, 'height': 260})
    print('1440dpr2 image', json.dumps(pg.evaluate(JS_IMG)))
    ctx.close()

    for label, w, h, dpr in [('1366', 1366, 768, 1), ('390', 390, 844, 2)]:
        ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=dpr)
        pg = ctx.new_page(); pg.goto(URL, wait_until='load'); pg.wait_for_timeout(1200)
        pg.screenshot(path=OUT + 'live-%s-top.png' % label)
        print(label, 'image', json.dumps(pg.evaluate(JS_IMG)))
        print(label, 'card ', json.dumps(pg.evaluate(JS_CARD)))
        pg.evaluate("() => document.querySelectorAll('.rv').forEach(e => e.classList.add('is-in','in','rv--in'))")
        pg.evaluate("""() => { const el = document.querySelector('.philo__video');
            window.scrollTo(0, el.getBoundingClientRect().top + window.scrollY - 90); }""")
        pg.wait_for_timeout(900)
        pg.screenshot(path=OUT + 'live-%s-video.png' % label)
        ctx.close()
    b.close()
print('captured')
