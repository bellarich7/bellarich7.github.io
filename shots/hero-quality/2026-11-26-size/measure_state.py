"""Measure the PC hero portrait: box, drawn image, face, text block; capture.

usage: python3 measure_state.py <url> <tag>

Face box in delivered-image fractions (1086x1348 hero file).
"""
import sys, os, json
from playwright.sync_api import sync_playwright
from PIL import Image

OUT = os.path.dirname(os.path.abspath(__file__))
URL = sys.argv[1] if len(sys.argv) > 1 else 'file:///workspace/bellarich-site/index.html'
TAG = sys.argv[2] if len(sys.argv) > 2 else 'now'

VPS = [('2560', 2560, 1440, 1), ('2560d2', 2560, 1440, 2),
       ('1920', 1920, 1080, 1), ('1920x15', 1920, 1080, 1.5), ('1920d2', 1920, 1080, 2),
       ('1440', 1440, 900, 1), ('1440d2', 1440, 900, 2),
       ('1366', 1366, 768, 1), ('1280', 1280, 800, 1), ('1081', 1081, 800, 1),
       ('m390', 390, 844, 2)]

FX0, FY0, FX1, FY1 = 0.415, 0.135, 0.645, 0.425   # face in delivered image

JS = """async () => {
  const el = document.querySelector('.hero__media');
  const hero = document.querySelector('.hero');
  const r = el.getBoundingClientRect();
  const cs = getComputedStyle(el);
  const m = cs.backgroundImage.match(/url\\("?([^")]+)"?\\)/);
  const nat = await new Promise(res => { const i = new Image();
    i.onload = () => res([i.naturalWidth, i.naturalHeight]); i.onerror = () => res(null); i.src = m[1]; });
  const box = n => { const q = document.querySelector(n); if (!q) return null;
    const b = q.getBoundingClientRect(); return {x: b.left, y: b.top, w: b.width, h: b.height}; };
  return {media: {x: r.left, y: r.top, w: r.width, h: r.height}, nat, src: m[1],
          hero: box('.hero'), wrap: box('.hero__in'), h1: box('.hero h1'),
          cred: box('.hero__cred'), actions: box('.hero__actions'),
          quote: box('.hero__cred-quote'),
          bgPos: cs.backgroundPosition, bgSize: cs.backgroundSize,
          dpr: devicePixelRatio, vw: innerWidth, vh: innerHeight,
          docH: document.documentElement.scrollHeight,
          overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth};
}"""

def main():
    rows = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        for label, w, h, dpr in VPS:
            ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=dpr)
            pg = ctx.new_page()
            logs = []
            pg.on('console', lambda m: logs.append((m.type, m.text)))
            pg.goto(URL, wait_until='load'); pg.wait_for_timeout(500)
            d = pg.evaluate(JS)
            mb, nat = d['media'], d['nat']
            s = min(mb['w'] / nat[0], mb['h'] / nat[1])
            dw, dh = nat[0] * s, nat[1] * s
            dx = mb['x'] + mb['w'] - dw
            dy = mb['y'] + mb['h'] - dh
            face = {'x': dx + dw * FX0, 'y': dy + dh * FY0, 'w': dw * (FX1 - FX0), 'h': dh * (FY1 - FY0)}
            need = (dw * dpr, dh * dpr)
            up = max(need[0] / nat[0], need[1] / nat[1])
            row = dict(label=label, vp=(w, h, dpr), src=os.path.basename(d['src'].split('?')[0]), nat=nat,
                       draw=(round(dw, 1), round(dh, 1)), need=(round(need[0]), round(need[1])),
                       up=round(up, 3), media=(round(mb['x'], 1), round(mb['y'], 1), round(mb['w'], 1), round(mb['h'], 1)),
                       facePx=(round(face['w'], 1), round(face['h'], 1)),
                       facePctVW=round(face['w'] / w * 100, 1), facePctVH=round(face['h'] / h * 100, 1),
                       drawPctVW=round(dw / w * 100, 1), drawPctVH=round(dh / h * 100, 1),
                       rightGap=round(w - (dx + dw), 1),
                       heroH=round(d['hero']['h'], 1) if d['hero'] else None,
                       h1right=round(d['h1']['x'] + d['h1']['w'], 1) if d['h1'] else None,
                       credRight=round(d['cred']['x'] + d['cred']['w'], 1) if d['cred'] else None,
                       quoteTop=round(d['quote']['y'], 1) if d['quote'] else None,
                       quoteBottom=round(d['quote']['y'] + d['quote']['h'], 1) if d['quote'] else None,
                       docH=d['docH'], overflow=d['overflow'],
                       errors=[t for t in logs if t[0] == 'error'])
            rows.append(row)
            print(json.dumps(row, ensure_ascii=False))
            pg.screenshot(path='%s/%s-%s-top.png' % (OUT, TAG, label))
            im = Image.open('%s/%s-%s-top.png' % (OUT, TAG, label))
            # face crop at 1:1 device px
            x0 = int(face['x'] * dpr); x1 = int((face['x'] + face['w']) * dpr)
            y0 = int(face['y'] * dpr); y1 = int((face['y'] + face['h']) * dpr)
            im.crop((max(0, x0), max(0, y0), min(im.width, x1), min(im.height, y1))) \
              .save('%s/%s-%s-face.png' % (OUT, TAG, label))
            ctx.close()
        b.close()
    with open('%s/measure-%s.json' % (OUT, TAG), 'w') as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)

main()
