import os
from playwright.sync_api import sync_playwright

OUT = os.path.dirname(os.path.abspath(__file__))
URL = 'file:///workspace/bellarich-site/index.html'

CANDS = {
 'E': '.hero__media{right:clamp(0px,calc((100vw - 1240px) * .5),320px)!important;width:min(50%,466px)!important}'
      '.hero__glow{right:calc(clamp(0px,calc((100vw - 1240px) * .5),320px) - 4%)!important;width:min(46%,620px)!important}',
 'F': '.hero__media{right:clamp(0px,calc((100vw - 1240px) * .3),230px)!important;width:min(50%,466px)!important}'
      '.hero__glow{right:calc(clamp(0px,calc((100vw - 1240px) * .3),230px) - 4%)!important;width:min(46%,620px)!important}',
}
VP = [(2560, 1440), (1920, 1080), (1440, 900), (1280, 800), (1081, 800)]

with sync_playwright() as p:
    b = p.chromium.launch()
    for name, css in CANDS.items():
        for w, h in VP:
            ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=1)
            pg = ctx.new_page(); pg.goto(URL, wait_until='load'); pg.wait_for_timeout(300)
            pg.add_style_tag(content='@media (min-width:1081px){' + css + '}')
            pg.wait_for_timeout(150)
            d = pg.evaluate("()=>{const r=document.querySelector('.hero__media').getBoundingClientRect();"
                            "const h1=document.querySelector('.hero h1').getBoundingClientRect();"
                            "return [r.left,r.width,Math.round(h1.right)]}")
            pg.screenshot(path='%s/proto-%s-%d.png' % (OUT, name, w))
            print(name, w, 'photoLeft %.0f width %.0f rightGap %.0f h1right %d center%% %.1f' %
                  (d[0], d[1], w - d[0] - d[1], d[2], (d[0] + d[1] / 2) / w * 100))
            ctx.close()
    b.close()
