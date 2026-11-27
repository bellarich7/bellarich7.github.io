#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Experiment: mobile hero__top variants; report alignment, caption lines, widths."""
import sys, json
from playwright.sync_api import sync_playwright

BASE = """@media (max-width:900px){
  .hero__top{flex-direction:row;align-items:flex-start;justify-content:space-between;gap:12px}
  .hero__top .hero__eyebrow{white-space:normal;flex:0 1 auto}
}"""
VARIANTS = {
 'V0 base-row': BASE,
 'V1 kill brand dash': BASE + "@media (max-width:900px){.hero__top .hero__brand::after{display:none}}",
 'V2 kill eyebrow dash': BASE + "@media (max-width:900px){.hero__top .hero__brand::after{flex:0 0 12px}.hero__eyebrow::before{display:none}}",
 'V3 kill both': BASE + "@media (max-width:900px){.hero__top .hero__brand::after{display:none}.hero__eyebrow::before{display:none}}",
 'V4 small logo': BASE + """@media (max-width:900px){.hero__top .hero__brand::after{flex:0 0 20px}
    .br-logo--hero{height:clamp(30px,8.4vw,38px)}}""",
 'V5 logo34+dash': BASE + """@media (max-width:900px){.hero__top .hero__brand::after{flex:0 0 24px}
    .br-logo--hero{height:34px}""",
}
URL = 'file:///workspace/bellarich-site/index.html'

def measure(pg):
    return pg.evaluate("""() => {
      const eb = document.querySelector('.hero__eyebrow');
      const brand = document.querySelector('.hero__brand');
      const logo = document.querySelector('.hero__brand .br-logo');
      const h1 = document.querySelector('.hero h1');
      const tn = [...eb.childNodes].find(n => n.nodeType === 3);
      const rg = document.createRange(); rg.selectNodeContents(tn);
      const rects = [...rg.getClientRects()].map(r => [Math.round(r.left), Math.round(r.top), Math.round(r.width)]);
      const R = el => { const r = el.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.width), Math.round(r.height)]; };
      return {brand: R(brand), logo: R(logo), eyebrow: R(eb), h1: R(h1),
              brandTop: Math.round(brand.getBoundingClientRect().top),
              ebTextTop: rects.length ? rects[0][1] : null,
              lines: rects, scrollW: document.documentElement.scrollWidth};
    }""")

with sync_playwright() as p:
    b = p.chromium.launch()
    for name, css in VARIANTS.items():
        print('###', name)
        for w, h in ((390, 844), (360, 800), (412, 915)):
            ctx = b.new_context(viewport={'width': w, 'height': h})
            pg = ctx.new_page(); pg.goto(URL, wait_until='load'); pg.add_style_tag(content=css); pg.wait_for_timeout(300)
            d = measure(pg)
            print(f'  {w}: brand={d["brand"]} logo={d["logo"]} eb={d["eyebrow"]} lines={len(d["lines"])} '
                  f'lineWidths={[l[2] for l in d["lines"]]} ebTextTop={d["ebTextTop"]} brandTop={d["brandTop"]} h1top={d["h1"][1]}')
            ctx.close()
    b.close()
