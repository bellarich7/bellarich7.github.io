#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hero first-screen check: logo visibility, duplication, overflow.

Usage: python3 hero_shot.py <out_prefix> [url]
Defaults to file:///workspace/bellarich-site/index.html
"""
import json
import sys
from playwright.sync_api import sync_playwright

prefix = sys.argv[1]
url = sys.argv[2] if len(sys.argv) > 2 else 'file:///workspace/bellarich-site/index.html'

with sync_playwright() as p:
    b = p.chromium.launch()
    out = {}
    for label, vp, dsf in (('pc', {'width': 1440, 'height': 900}, 1),
                           ('m390', {'width': 390, 'height': 844}, 2)):
        ctx = b.new_context(viewport=vp, device_scale_factor=dsf)
        pg = ctx.new_page()
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(url, wait_until='networkidle')
        pg.wait_for_timeout(700)
        pg.screenshot(path=f'/workspace/bellarich-site/shots/{prefix}-{label}-top.png')
        info = pg.evaluate("""() => {
          const de = document.documentElement;
          const box = el => { if(!el) return null; const r = el.getBoundingClientRect();
            return {x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height),
                    visible: r.width > 0 && r.height > 0 && getComputedStyle(el).visibility !== 'hidden'
                             && getComputedStyle(el).opacity !== '0'}; };
          const over = [];
          document.querySelectorAll('body *').forEach(el => {
            const r = el.getBoundingClientRect();
            if (r.width > 0 && (r.right > de.clientWidth + 2 || r.left < -2)) {
              const c = (el.className || '').toString();
              if (!/band__track|modal__|br-sprite/.test(c)) over.push(el.tagName + '.' + c.slice(0, 40));
            }
          });
          const hero = document.querySelector('.hero');
          const acts = document.querySelector('.hero__actions');
          const quote = document.querySelector('.hero__cred-quote');
          const name = document.querySelector('.hero__cred-name');
          return {
            vw: de.clientWidth, scrollW: de.scrollWidth,
            navLogo: box(document.querySelector('.nav .logo')),
            heroBrand: box(document.querySelector('.hero__brand')),
            heroBrandLogo: box(document.querySelector('.hero__brand .br-logo')),
            name: box(name), quote: box(quote), actions: box(acts),
            heroBottom: box(hero) ? box(hero).y + box(hero).h : null,
            fold: window.innerHeight,
            overflow: over.slice(0, 6)
          };
        }""")
        # scroll a little to see whether the nav logo appears next to the hero brand
        pg.evaluate("window.scrollTo(0, 60)")
        pg.wait_for_timeout(450)
        pg.screenshot(path=f'/workspace/bellarich-site/shots/{prefix}-{label}-scroll60.png')
        both = pg.evaluate("""() => {
          const b = document.querySelector('.hero__brand');
          const l = document.querySelector('.nav .logo');
          const vis = el => { const r = el.getBoundingClientRect(); const s = getComputedStyle(el);
            return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && parseFloat(s.opacity) > .1; };
          return {heroBrandVisible: vis(b), navLogoVisible: vis(l)};
        }""")
        info['at_scroll_60'] = both
        info['page_errors'] = errs
        out[label] = info
        ctx.close()
    b.close()
print(json.dumps(out, ensure_ascii=False, indent=2))
