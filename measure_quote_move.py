#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""히어로 인용구 이동 전/후 실측: 사진 크기·상단 y, h1 상단, 버튼 하단, 인용구 상단, 캡션.
Usage: python3 measure_quote_move.py <label> [url] [--shot]
"""
import json
import sys
import os
from playwright.sync_api import sync_playwright

label = sys.argv[1]
url = sys.argv[2] if len(sys.argv) > 2 else 'file:///workspace/bellarich-site/index.html'
SHOT = '--shot' in sys.argv
OUT = '/workspace/bellarich-site/shots'

VPS = [('1440x900', 1440, 900), ('1920x1080', 1920, 1080), ('1366x900', 1366, 900),
       ('1280x800', 1280, 800), ('1366x768', 1366, 768)]

JS = """() => {
  const R = el => { if(!el) return null; const r = el.getBoundingClientRect();
    return {x:+(r.left.toFixed(1)), y:+(r.top.toFixed(1)), w:+(r.width.toFixed(1)), h:+(r.height.toFixed(1)),
            bottom:+(r.bottom.toFixed(1)), right:+(r.right.toFixed(1)), visible: r.width>0 && r.height>0}; };
  const vis = sel => [...document.querySelectorAll(sel)].find(e => {
     const r = e.getBoundingClientRect(); return r.width>0 && r.height>0; });
  const hero = document.querySelector('.hero');
  const photo = document.querySelector('.hero__photo');
  const media = vis('.hero__media');
  const quote = vis('.hero__cred-quote');
  const cred = vis('.hero__cred');
  const copy = document.querySelector('.hero__copy');
  const h1 = document.querySelector('.hero h1');
  const acts = document.querySelector('.hero__actions');
  const name = vis('.hero__cred-name');
  const de = document.documentElement;
  // left column bottom = bottom of the lowest visible element inside .hero__copy / left cred
  const inCred = document.querySelector('.hero__in > .hero__cred');
  const leftBottom = Math.max(
     acts ? acts.getBoundingClientRect().bottom : 0,
     (inCred && inCred.getBoundingClientRect().height > 0) ? inCred.getBoundingClientRect().bottom : 0);
  const sideCred = document.querySelector('.hero__cred--side');
  const sideBottom = (sideCred && sideCred.getBoundingClientRect().height>0) ? sideCred.getBoundingClientRect().bottom : 0;
  const contentBottom = Math.max(leftBottom, sideBottom, photo ? photo.getBoundingClientRect().bottom : 0);
  return {
    vw: de.clientWidth, vh: window.innerHeight,
    scrollW: de.scrollWidth, scrollH: de.scrollHeight,
    heroH: +hero.getBoundingClientRect().height.toFixed(1),
    heroBottom: +hero.getBoundingClientRect().bottom.toFixed(1),
    heroOverflow: +(hero.getBoundingClientRect().height - window.innerHeight).toFixed(1),
    contentBottom: +contentBottom.toFixed(1),
    contentOverHero: +(contentBottom - hero.getBoundingClientRect().bottom).toFixed(1),
    photo: R(photo), media: R(media),
    h1: R(h1), actions: R(acts), quote: quote ? R(quote) : null,
    cred: R(cred), name: R(name),
    quoteGapFromActions: (quote && acts) ? +(quote.getBoundingClientRect().top - acts.getBoundingClientRect().bottom).toFixed(1) : null,
    credContainsQuote: (cred && quote) ? cred.contains(quote) : null,
    quoteParent: quote ? quote.parentElement.className : null,
    quoteFont: (() => { const q = vis('.hero__cred-quote'); if(!q) return null; const cs = getComputedStyle(q);
      return {size: cs.fontSize, color: cs.color, family: cs.fontFamily.slice(0,30), align: cs.textAlign, lh: cs.lineHeight}; })(),
    credH: cred ? +cred.getBoundingClientRect().height.toFixed(1) : null,
    errors: window.__errs || []
  };
}"""

rows = []
with sync_playwright() as p:
    b = p.chromium.launch()
    for name_, w, h in VPS:
        ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=1)
        pg = ctx.new_page()
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.on('console', lambda m: errs.append('console:' + m.text) if m.type == 'error' else None)
        pg.evaluate  # no-op
        pg.goto(url, wait_until='load')
        pg.wait_for_timeout(900)
        pg.evaluate("window.__errs = []")
        d = pg.evaluate(JS)
        d['errors'] = errs
        d['label'] = name_
        rows.append(d)
        if SHOT:
            pg.screenshot(path=f'{OUT}/{label}-{name_}.png')
        ctx.close()
    b.close()

for d in rows:
    print(json.dumps(d, ensure_ascii=False))
print()
# compact table
hdr = f"{'res':10} {'photo w×h':12} {'photo y':8} {'h1 y':8} {'btn bottom':11} {'quote top':10} {'quote gap':10} {'cred h':7} {'heroovf':8} {'contovf':8} {'hscroll':8}"
print(hdr)
for d in rows:
    ph = d['photo'] or d['media']
    print(f"{d['label']:10} "
          f"{(str(ph['w'])+'×'+str(ph['h'])) if ph else '-':12} "
          f"{(str(ph['y']) if ph else '-'):8} "
          f"{d['h1']['y']:8} "
          f"{d['actions']['bottom']:11} "
          f"{(str(d['quote']['y']) if d['quote'] else '-'):10} "
          f"{(str(d['quoteGapFromActions']) if d['quoteGapFromActions'] is not None else '-'):10} "
          f"{str(d['credH']):7} "
          f"{d['heroOverflow']:8} "
          f"{d['contentOverHero']:8} "
          f"{(d['scrollW']-d['vw']):8}")
    if d['errors']:
        print('   errors:', d['errors'])
