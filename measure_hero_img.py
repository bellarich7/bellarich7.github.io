import sys, json
from playwright.sync_api import sync_playwright
url = 'file:///workspace/bellarich-site/index.html'
VPS = [('pc2560', 2560, 1440, 1), ('pc1920', 1920, 1080, 1), ('pc1920x1.5', 1920, 1080, 1.5),
       ('pc1440', 1440, 900, 1), ('pc1440d2', 1440, 900, 2), ('pc1366', 1366, 768, 1),
       ('pc1536', 1536, 864, 1.25), ('tab900', 900, 1180, 1), ('m390', 390, 844, 2)]
JS = """async () => {
  const R = el => { const r = el.getBoundingClientRect();
    return {x:+r.left.toFixed(1), y:+r.top.toFixed(1), w:+r.width.toFixed(1), h:+r.height.toFixed(1)}; };
  const m = document.querySelector('.hero__media');
  const cs = getComputedStyle(m);
  const url = cs.backgroundImage.slice(5, -2);
  const nat = await new Promise(res => { const i = new Image();
    i.onload = () => res([i.naturalWidth, i.naturalHeight]); i.onerror = () => res(null); i.src = url; });
  const box = R(m);
  let draw = null;
  if (nat && nat[0] > 0) {
    const s = Math.min(box.w / nat[0], box.h / nat[1]);
    draw = {w:+(nat[0]*s).toFixed(1), h:+(nat[1]*s).toFixed(1), ratio:+s.toFixed(3)};
  }
  return {box, nat, draw};
}"""
with sync_playwright() as p:
    b = p.chromium.launch()
    for label, w, h, dpr in VPS:
        ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=dpr)
        pg = ctx.new_page(); pg.goto(url, wait_until='load'); pg.wait_for_timeout(400)
        d = pg.evaluate(JS)
        need = (round(d['draw']['w']*dpr), round(d['draw']['h']*dpr))
        src = tuple(d['nat'])
        over = max(need[0]/src[0], need[1]/src[1])
        print('%-11s dpr%-4s draw %sx%s css -> %dx%d dev  src %dx%d  upscale x%.2f'
              % (label, dpr, d['draw']['w'], d['draw']['h'], need[0], need[1], src[0], src[1], over))
        ctx.close()
    b.close()
