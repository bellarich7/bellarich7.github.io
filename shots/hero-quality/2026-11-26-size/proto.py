import os, sys, json
from playwright.sync_api import sync_playwright

OUT = os.path.dirname(os.path.abspath(__file__))
URL = 'file:///workspace/bellarich-site/index.html'

CANDS = {
 'A': '.hero__media{right:clamp(0px,4vw,120px)!important;width:min(50%,466px)!important}'
      '.hero__glow{right:calc(clamp(0px,4vw,120px) - 4%)!important;width:min(46%,620px)!important}',
 'B': '.hero__media{right:clamp(0px,6vw,150px)!important;width:min(50%,466px)!important}'
      '.hero__glow{right:calc(clamp(0px,6vw,150px) - 4%)!important;width:min(46%,620px)!important}',
 'C': '.hero__media{right:clamp(0px,5vw,130px)!important;width:min(50%,500px)!important}'
      '.hero__glow{right:calc(clamp(0px,5vw,130px) - 4%)!important;width:min(48%,660px)!important}',
 'D': '.hero__media{right:clamp(0px,5vw,130px)!important;width:min(50%,440px)!important}'
      '.hero__glow{right:calc(clamp(0px,5vw,130px) - 4%)!important;width:min(44%,600px)!important}',
}
VP = [(2560, 1440), (1920, 1080), (1440, 900), (1280, 800), (1081, 800)]

JS = """() => {
 const el=document.querySelector('.hero__media'); const r=el.getBoundingClientRect();
 const cs=getComputedStyle(el); const m=cs.backgroundImage.match(/url\\("?([^")]+)"?\\)/);
 return {box:[r.left,r.top,r.width,r.height], src:m[1].slice(0,40)};
}"""

with sync_playwright() as p:
    b = p.chromium.launch()
    for name, css in CANDS.items():
        for w, h in VP:
            ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=1)
            pg = ctx.new_page(); pg.goto(URL, wait_until='load'); pg.wait_for_timeout(300)
            pg.add_style_tag(content='@media (min-width:1081px){' + css + '}')
            pg.wait_for_timeout(150)
            d = pg.evaluate(JS)
            pg.screenshot(path='%s/proto-%s-%d.png' % (OUT, name, w))
            # drawn size from box + natural aspect 1086x1348
            bw, bh = d['box'][2], d['box'][3]
            s = min(bw / 1086, bh / 1348); dw, dh = 1086 * s, 1348 * s
            print('%s %d: box %s draw %.0fx%.0f rightGap %.0f' % (name, w, [round(v) for v in d['box']], dw, dh, w - (d['box'][0] + bw)))
            ctx.close()
    b.close()
