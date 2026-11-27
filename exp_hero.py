#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Experiment: try candidate mobile hero__top CSS and report boxes."""
import sys, json
from playwright.sync_api import sync_playwright

CSS = sys.argv[1] if len(sys.argv) > 1 else ''
URL = 'file:///workspace/bellarich-site/index.html'

with sync_playwright() as p:
    b = p.chromium.launch()
    for w, h in ((390, 844), (430, 932), (360, 800), (1440, 900)):
        ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=1)
        pg = ctx.new_page()
        pg.goto(URL, wait_until='load')
        if CSS:
            pg.add_style_tag(content=CSS)
        pg.wait_for_timeout(400)
        d = pg.evaluate("""() => {
          const de = document.documentElement;
          const bx = s => { const el = document.querySelector(s); if(!el) return null;
            const r = el.getBoundingClientRect();
            return [Math.round(r.left), Math.round(r.top), Math.round(r.width), Math.round(r.height),
                    Math.round(r.bottom)]; };
          const eb = document.querySelector('.hero__eyebrow');
          let lines = 0;
          if (eb) {
            const lh = parseFloat(getComputedStyle(eb).lineHeight) || 0;
            lines = lh ? Math.round(eb.getBoundingClientRect().height / lh) : 0;
          }
          const logo = document.querySelector('.hero__brand .br-logo');
          return {
            vw: de.clientWidth, scrollW: de.scrollWidth, scrollH: de.scrollHeight, vh: innerHeight,
            brand: bx('.hero__brand'), logo: bx('.hero__brand .br-logo'),
            eyebrow: bx('.hero__eyebrow'), h1: bx('.hero h1'),
            top: bx('.hero__top'),
            ebLines: lines,
            heroBottom: Math.round(document.querySelector('.hero').getBoundingClientRect().bottom),
            gapCaptionH1: eb ? Math.round(document.querySelector('.hero h1').getBoundingClientRect().top - eb.getBoundingClientRect().bottom) : null
          };
        }""")
        print(w, h, json.dumps(d, ensure_ascii=False))
        ctx.close()
    b.close()
