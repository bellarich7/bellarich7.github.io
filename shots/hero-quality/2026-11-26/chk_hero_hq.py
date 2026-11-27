"""Verify the hero portrait quality pass on a URL (local file:// or live).

usage: python3 chk_hero_hq.py <url> <tag>
  prints, per viewport: which file the hero draws, drawn CSS px, device px
  needed, natural px, scale factor, horizontal overflow, console errors,
  failed requests / 4xx-5xx, and where the hero starts.
  saves <tag>-<label>-top.png + <tag>-<label>-face.png
"""
import sys, os
from playwright.sync_api import sync_playwright
from PIL import Image

OUT = os.path.dirname(os.path.abspath(__file__))
URL = sys.argv[1] if len(sys.argv) > 1 else 'file:///workspace/bellarich-site/index.html'
TAG = sys.argv[2] if len(sys.argv) > 2 else 'chk'

VPS = [('2560', 2560, 1440, 1), ('2560d2', 2560, 1440, 2), ('1920', 1920, 1080, 1),
       ('1920x125', 1920, 1080, 1.25), ('1920x15', 1920, 1080, 1.5), ('1920d2', 1920, 1080, 2),
       ('1536x125', 1536, 864, 1.25), ('1440', 1440, 900, 1), ('1440d2', 1440, 900, 2),
       ('1366', 1366, 768, 1), ('1280', 1280, 800, 1), ('1081', 1081, 800, 2),
       ('1080', 1080, 800, 2), ('900', 900, 1180, 2), ('768', 768, 1024, 2),
       ('390', 390, 844, 2), ('390x3', 390, 844, 3), ('360', 360, 780, 2)]

JS = """async () => {
  const el = document.querySelector('.hero__media');
  const r = el.getBoundingClientRect();
  const cs = getComputedStyle(el);
  const m = cs.backgroundImage.match(/url\\("([^"]+)"\\)/);
  const src = m ? m[1] : '';
  const nat = await new Promise(res => { const i = new Image();
    i.onload = () => res([i.naturalWidth, i.naturalHeight]); i.onerror = () => res(null); i.src = src; });
  return {box: {x: r.left, y: r.top, w: r.width, h: r.height}, nat,
          inline: src.startsWith('data:'),
          docW: document.documentElement.scrollWidth, winW: window.innerWidth,
          dpr: devicePixelRatio,
          h1: document.querySelector('h1').getBoundingClientRect().bottom};
}"""

bad = 0
with sync_playwright() as p:
    b = p.chromium.launch()
    for label, w, h, dpr in VPS:
        ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=dpr)
        pg = ctx.new_page()
        errs, fails = [], []
        pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
        pg.on('requestfailed', lambda r: fails.append(r.url[:90] + ' ' + str(r.failure)))
        pg.on('response', lambda r: fails.append('%d %s' % (r.status, r.url[:90])) if r.status >= 400 else None)
        pg.goto(URL, wait_until='load'); pg.wait_for_timeout(600)
        pg.add_style_tag(content='.hero__scroll{display:none!important}')
        d = pg.evaluate(JS)
        pg.screenshot(path='%s/%s-%s-top.png' % (OUT, TAG, label))
        box, nat = d['box'], d['nat']
        s = min(box['w'] / nat[0], box['h'] / nat[1])
        dw, dh = nat[0] * s, nat[1] * s
        need = (round(dw * dpr), round(dh * dpr))
        up = max(need[0] / nat[0], need[1] / nat[1])
        ov = d['docW'] - d['winW']
        # picture shown: 'inline 1x' | '2x file'
        pick = 'inline' if d['inline'] else '2x'
        flag = ''
        if ov > 0: flag += ' OVERFLOW+%d' % ov
        if errs: flag += ' CONSOLE:%s' % errs[:2]
        if fails: flag += ' REQ:%s' % fails[:2]
        if flag: bad += 1
        print('%-9s dpr%-4s %-6s draw %6.1fx%6.1f css -> %dx%d dev  src %dx%d  scale x%.2f  h1bottom %d%s'
              % (label, dpr, pick, dw, dh, need[0], need[1], nat[0], nat[1], up, round(d['h1']), flag))
        # face crop for the wide cases
        if w >= 1081:
            FX0, FY0, FX1, FY1 = 0.20, 0.02, 0.74, 0.42
            dx = box['x'] + (box['w'] - dw)
            dy = box['y'] + (box['h'] - dh)
            im = Image.open('%s/%s-%s-top.png' % (OUT, TAG, label))
            im.crop((int((dx + dw * FX0) * dpr), int((dy + dh * FY0) * dpr),
                     int((dx + dw * FX1) * dpr), int((dy + dh * FY1) * dpr))) \
              .save('%s/%s-%s-face.png' % (OUT, TAG, label))
        ctx.close()
    b.close()
print('viewports with problems:', bad)
