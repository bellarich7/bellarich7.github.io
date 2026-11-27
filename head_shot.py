#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Capture the Philosophy / Solutions headings and report computed text style.

Usage: python3 head_shot.py <prefix> [url]
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
        pg.goto(url, wait_until='networkidle')
        pg.wait_for_timeout(600)
        info = {}
        for name, sel in (('philo', '.philo__text h2'), ('sol', '.sol__head h2')):
            el = pg.query_selector(sel)
            el.scroll_into_view_if_needed()
            pg.wait_for_timeout(500)
            box = el.bounding_box()
            pg.screenshot(path=f'/workspace/bellarich-site/shots/{prefix}-{label}-{name}.png',
                          clip={'x': max(0, box['x'] - 16), 'y': max(0, box['y'] - 16),
                                'width': min(box['width'] + 32, vp['width']), 'height': box['height'] + 32})
            info[name] = pg.evaluate("""(sel) => {
              const el = document.querySelector(sel);
              const em = el.querySelector('em');
              const cs = getComputedStyle(el);
              const ce = em ? getComputedStyle(em) : null;
              return {weight: cs.fontWeight, color: cs.color, family: cs.fontFamily.split(',')[0],
                      size: cs.fontSize, lh: cs.lineHeight, width: Math.round(el.getBoundingClientRect().width),
                      height: Math.round(el.getBoundingClientRect().height),
                      emWeight: ce && ce.fontWeight, emColor: ce && ce.color,
                      text: el.innerText.replace(/\\n/g, ' | ')};
            }""", sel)
        out[label] = info
        ctx.close()
    b.close()
print(json.dumps(out, ensure_ascii=False, indent=2))
