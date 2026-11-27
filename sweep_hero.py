#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hero fit sweep across viewports for two builds (A=before, B=after)."""
import sys, json
from playwright.sync_api import sync_playwright

A = 'file:///workspace/bellarich-site/shots/_live_before.html'
B = 'file:///workspace/bellarich-site/index.html'

VPS = [(1920, 1080), (1600, 1000), (1440, 900), (1440, 800), (1366, 768), (1366, 900),
       (1280, 800), (1150, 800), (1024, 768), (1024, 900), (1280, 720), (412, 915), (390, 844), (360, 800)]

JS = """() => {
  const R = el => { const r = el.getBoundingClientRect(); return [Math.round(r.top), Math.round(r.height)]; };
  const eb = document.querySelector('.hero__eyebrow');
  const tn = [...eb.childNodes].find(n => n.nodeType === 3);
  const rg = document.createRange(); rg.selectNodeContents(tn);
  const lines = [...rg.getClientRects()];
  const hero = document.querySelector('.hero');
  const cred = document.querySelector('.hero__cred');
  return {vh: window.innerHeight, heroH: Math.round(hero.getBoundingClientRect().height),
          logoTop: R(document.querySelector('.hero__brand .br-logo'))[0],
          navH: Math.round(document.querySelector('.nav').getBoundingClientRect().height),
          ebTop: R(eb)[0], ebLines: lines.length,
          ebRight: Math.round(Math.max(...lines.map(r => r.right))),
          h1Top: R(document.querySelector('.hero h1'))[0],
          credBottom: Math.round(cred.getBoundingClientRect().bottom),
          scrollW: document.documentElement.scrollWidth, vw: document.documentElement.clientWidth};
}"""

with sync_playwright() as p:
    b = p.chromium.launch()
    print(f'{"viewport":>12} | {"A hero/h":>10} {"A logo":>6} | {"B hero/h":>10} {"B logo":>6} {"B ebLines":>9} {"B h1":>5} {"B credBot":>9} | B over?')
    for w, h in VPS:
        row = {}
        for key, url in (('A', A), ('B', B)):
            ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=1)
            pg = ctx.new_page()
            pg.goto(url, wait_until='load')
            pg.wait_for_timeout(500)
            row[key] = pg.evaluate(JS)
            ctx.close()
        a, bb = row['A'], row['B']
        over = 'text over' if bb['credBottom'] > bb['vh'] else ('ok' if bb['heroH'] <= bb['vh'] else f"hero +{bb['heroH']-bb['vh']}")
        print(f'{w}x{h:>5} | {a["heroH"]:>4}/{a["vh"]:<5} {a["logoTop"]:>6} | {bb["heroH"]:>4}/{bb["vh"]:<5} {bb["logoTop"]:>6} {bb["ebLines"]:>9} {bb["h1Top"]:>5} {bb["credBottom"]:>9} | {over}  sw={bb["scrollW"]}')
    b.close()
