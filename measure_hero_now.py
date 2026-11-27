#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hero geometry: logo top vs nav bottom, caption lines, h1 top, fit in viewport."""
import sys, json
from playwright.sync_api import sync_playwright

url = sys.argv[1] if len(sys.argv) > 1 else 'file:///workspace/bellarich-site/index.html'
prefix = sys.argv[2] if len(sys.argv) > 2 else 'now'

VPS = [('pc1440', 1440, 900), ('pc1366', 1366, 768), ('m390', 390, 844)]

JS = """() => {
  const R = el => { if(!el) return null; const r = el.getBoundingClientRect();
    return {x:Math.round(r.left), y:Math.round(r.top), w:Math.round(r.width), h:Math.round(r.height)}; };
  const eb = document.querySelector('.hero__eyebrow');
  const tn = [...eb.childNodes].find(n => n.nodeType === 3);
  const rg = document.createRange(); rg.selectNodeContents(tn);
  const lines = [...rg.getClientRects()].map(r => [Math.round(r.left), Math.round(r.top), Math.round(r.width)]);
  const cs = getComputedStyle(eb);
  const nav = document.querySelector('.nav');
  const hero = document.querySelector('.hero');
  return {
    navH: nav ? Math.round(nav.getBoundingClientRect().height) : null,
    heroPadTop: getComputedStyle(hero).paddingTop,
    heroTop: R(hero),
    brand: R(document.querySelector('.hero__brand')),
    logo: R(document.querySelector('.hero__brand .br-logo')),
    eb: R(eb), ebFont: cs.fontSize, ebLS: cs.letterSpacing, ebLines: lines.length, lines,
    h1: R(document.querySelector('.hero h1')),
    gapEbH1: Math.round(document.querySelector('.hero h1').getBoundingClientRect().top - eb.getBoundingClientRect().bottom),
    sub: R(document.querySelector('.hero__sub')),
    actions: R(document.querySelector('.hero__actions')),
    cred: R(document.querySelector('.hero__cred')),
    heroBottom: Math.round(hero.getBoundingClientRect().bottom),
    docScrollH: document.documentElement.scrollHeight,
    scrollW: document.documentElement.scrollWidth,
    vw: document.documentElement.clientWidth,
    vh: window.innerHeight
  };
}"""

with sync_playwright() as p:
    b = p.chromium.launch()
    for label, w, h in VPS:
        ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2 if w < 500 else 1)
        pg = ctx.new_page()
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(url, wait_until='load')
        pg.wait_for_timeout(600)
        d = pg.evaluate(JS)
        d['errors'] = errs
        print(label, json.dumps(d, ensure_ascii=False))
        pg.screenshot(path=f'/workspace/bellarich-site/shots/{prefix}-{label}.png')
        pg.screenshot(path=f'/workspace/bellarich-site/shots/{prefix}-{label}-full.png', full_page=True)
        ctx.close()
    b.close()
