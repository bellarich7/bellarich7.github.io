#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hero first-screen fit check: bottom y of the last hero element (facts/chips row)."""
import os, json, sys
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
URL = 'file://' + os.path.join(ROOT, 'index.html')
SIZES = [(1440, 900), (1366, 768), (1280, 800), (1150, 800), (1024, 768), (1024, 900)]

SEL = sys.argv[1] if len(sys.argv) > 1 else '.hero__chips'

with sync_playwright() as p:
    b = p.chromium.launch()
    for w, h in SIZES:
        ctx = b.new_context(viewport={'width': w, 'height': h})
        pg = ctx.new_page()
        pg.goto(URL, wait_until='load')
        pg.wait_for_timeout(900)
        d = pg.evaluate("""(sel) => {
          const el = document.querySelector(sel);
          const hero = document.querySelector('.hero');
          const r = el ? el.getBoundingClientRect() : null;
          const hr = hero.getBoundingClientRect();
          const chips = [...document.querySelectorAll(sel + ' .chip')].map(c => c.textContent.trim());
          return {
            vh: window.innerHeight,
            rowTop: r ? Math.round(r.top) : null,
            rowBottom: r ? Math.round(r.bottom) : null,
            rowH: r ? Math.round(r.height) : null,
            slack: r ? Math.round(window.innerHeight - r.bottom) : null,
            heroBottom: Math.round(hr.bottom),
            heroH: Math.round(hr.height),
            chips,
            scrollW: document.documentElement.scrollWidth,
            vw: document.documentElement.clientWidth
          };
        }""", SEL)
        print(f'{w}x{h}', json.dumps(d, ensure_ascii=False))
        ctx.close()
    b.close()
