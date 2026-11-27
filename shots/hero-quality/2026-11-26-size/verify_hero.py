"""Regression check for the resized / re-centred PC hero portrait.

For every viewport: which hero file is used, drawn size, upscale, person's left
edge vs the h1's real glyph box (Range rects, not the element box), overflow,
console errors, failed requests, quote still inside the first screen.
"""
import os, sys, json
from playwright.sync_api import sync_playwright

OUT = os.path.dirname(os.path.abspath(__file__))
URL = sys.argv[1] if len(sys.argv) > 1 else 'file:///workspace/bellarich-site/index.html'

VPS = [(2560, 1440, 1), (2560, 1440, 2), (1920, 1080, 1), (1920, 1080, 1.25),
       (1920, 1080, 1.5), (1920, 1080, 2), (1536, 864, 1.25), (1440, 900, 1),
       (1440, 900, 2), (1366, 768, 1), (1366, 768, 1.25), (1280, 800, 1),
       (1081, 800, 1), (1081, 800, 2), (1080, 800, 2), (1024, 768, 1),
       (900, 700, 2), (768, 1024, 2), (390, 844, 2), (390, 844, 3), (360, 800, 2)]

JS = """async () => {
  const el = document.querySelector('.hero__media');
  const r = el.getBoundingClientRect(); const cs = getComputedStyle(el);
  const m = cs.backgroundImage.match(/url\\("?([^")]+)"?\\)/);
  const nat = await new Promise(res => { const i = new Image();
    i.onload = () => res([i.naturalWidth, i.naturalHeight]); i.onerror = () => res(null); i.src = m[1]; });
  // real glyph boxes of the h1 lines
  const h1 = document.querySelector('.hero h1');
  const rg = document.createRange(); rg.selectNodeContents(h1);
  const rects = [...rg.getClientRects()].filter(q => q.width > 1 && q.height > 1);
  const glyphRight = Math.max(...rects.map(q => q.right)) || 0;
  const glyphBottom = Math.max(...rects.map(q => q.bottom)) || 0;
  const q = document.querySelector('.hero__cred-quote').getBoundingClientRect();
  const btns = [...document.querySelectorAll('.hero__actions .btn')].map(b => b.getBoundingClientRect().right);
  return {src: m[1], nat, media: [r.left, r.top, r.width, r.height], dpr: devicePixelRatio,
          vw: innerWidth, vh: innerHeight, glyphRight, glyphBottom, quoteBottom: q.bottom,
          btnRight: Math.max(...btns), heroH: document.querySelector('.hero').getBoundingClientRect().height,
          overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
          docH: document.documentElement.scrollHeight};
}"""

CONTENT_LEFT = 0.0866   # person's left edge inside the delivered image (alpha bbox)

rows = []
with sync_playwright() as p:
    b = p.chromium.launch()
    for w, h, dpr in VPS:
        ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=dpr)
        pg = ctx.new_page()
        errs, fails = [], []
        pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
        pg.on('requestfailed', lambda r: fails.append(r.url[:90]))
        pg.on('response', lambda r: fails.append('%d %s' % (r.status, r.url[:80])) if r.status >= 400 else None)
        pg.goto(URL, wait_until='load'); pg.wait_for_timeout(400)
        d = pg.evaluate(JS)
        nat, mb = d['nat'], d['media']
        s = min(mb[2] / nat[0], mb[3] / nat[1])
        dw, dh = nat[0] * s, nat[1] * s
        personLeft = mb[0] + mb[2] - dw + dw * CONTENT_LEFT
        need = max(dw * dpr / nat[0], dh * dpr / nat[1])
        row = dict(vp='%dx%d@%s' % (w, h, dpr), file=os.path.basename(d['src'].split('?')[0])[:34],
                   draw='%.0fx%.0f' % (dw, dh), up=round(need, 2),
                   gap=round(w - (mb[0] + mb[2]), 1), personLeft=round(personLeft, 1),
                   glyphRight=round(d['glyphRight'], 1), textClear=round(personLeft - d['glyphRight'], 1),
                   quoteBottom=round(d['quoteBottom'], 1), vh=d['vh'],
                   quoteInFirst=round(d['quoteBottom'], 1) <= d['vh'],
                   heroH=round(d['heroH'], 1), overflow=d['overflow'],
                   errors=len(errs), fails=fails[:3])
        rows.append(row)
        print(json.dumps(row, ensure_ascii=False))
        ctx.close()
    b.close()

bad = [r for r in rows if r['errors'] or r['fails'] or r['overflow'] or r['textClear'] < -2]
print('\n%s  problems: %d' % ('PASS' if not bad else 'CHECK', len(bad)))
for r in bad:
    print(' ', r)
