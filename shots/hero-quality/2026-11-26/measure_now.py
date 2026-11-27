"""Measure + capture the hero portrait at PC widths (2026-11-26 quality pass).

usage: python3 measure_now.py <url> <tag>
  writes  <tag>-<label>-top.png      (viewport-top screenshot, full device px)
          <tag>-<label>-face.png     (face crop at 1:1 device px)
"""
import sys, os
from playwright.sync_api import sync_playwright
from PIL import Image

OUT = os.path.dirname(os.path.abspath(__file__))
URL = sys.argv[1] if len(sys.argv) > 1 else 'file:///workspace/bellarich-site/index.html'
TAG = sys.argv[2] if len(sys.argv) > 2 else 'now'

VPS = [('2560', 2560, 1440, 1), ('1920d2', 1920, 1080, 2), ('1920', 1920, 1080, 1),
       ('1920x15', 1920, 1080, 1.5), ('1440d2', 1440, 900, 2), ('1440', 1440, 900, 1),
       ('1366', 1366, 768, 1), ('m390', 390, 844, 2)]

JS = """async () => {
  const el = document.querySelector('.hero__media');
  const r = el.getBoundingClientRect();
  const cs = getComputedStyle(el);
  const src = cs.backgroundImage.match(/url\\("([^"]+)"\\)/);
  const nat = await new Promise(res => { const i = new Image();
    i.onload = () => res([i.naturalWidth, i.naturalHeight]); i.onerror = () => res(null); i.src = src[1]; });
  return {box: {x: r.left, y: r.top, w: r.width, h: r.height}, nat,
          mobile: matchMedia('(max-width:900px)').matches,
          dpr: devicePixelRatio};
}"""

with sync_playwright() as p:
    b = p.chromium.launch()
    for label, w, h, dpr in VPS:
        ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=dpr)
        pg = ctx.new_page()
        pg.goto(URL, wait_until='load'); pg.wait_for_timeout(500)
        pg.add_style_tag(content='.hero__scroll{display:none!important}')
        d = pg.evaluate(JS)
        pg.screenshot(path='%s/%s-%s-top.png' % (OUT, TAG, label))
        box, nat = d['box'], d['nat']
        s = min(box['w'] / nat[0], box['h'] / nat[1])
        dw, dh = nat[0] * s, nat[1] * s
        # drawn image sits at right/bottom (desktop) or centered bottom (mobile)
        dx = box['x'] + (box['w'] - dw) if w > 900 else box['x'] + (box['w'] - dw) / 2
        dy = box['y'] + (box['h'] - dh)
        need = (round(dw * dpr), round(dh * dpr))
        up = max(need[0] / nat[0], need[1] / nat[1])
        print('%-7s dpr%-4s draw %6.1fx%6.1f css -> %dx%d dev  src %dx%d  upscale x%.2f'
              % (label, dpr, dw, dh, need[0], need[1], nat[0], nat[1], up))
        # face crop: same fraction of the source image in both passes
        FX0, FY0, FX1, FY1 = 0.26, 0.02, 0.80, 0.40
        im = Image.open('%s/%s-%s-top.png' % (OUT, TAG, label))
        x0 = int((dx + dw * FX0) * dpr); x1 = int((dx + dw * FX1) * dpr)
        y0 = int((dy + dh * FY0) * dpr); y1 = int((dy + dh * FY1) * dpr)
        im.crop((max(0, x0), max(0, y0), min(im.width, x1), min(im.height, y1))) \
          .save('%s/%s-%s-face.png' % (OUT, TAG, label))
        ctx.close()
    b.close()
