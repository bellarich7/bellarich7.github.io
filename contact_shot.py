#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Capture the contact section (buttons incl. kakao) and full-page shots."""
import json
import sys
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch()
    out = {}
    for label, vp, dsf in (('pc', {'width': 1440, 'height': 900}, 1),
                           ('m390', {'width': 390, 'height': 844}, 2)):
        ctx = b.new_context(viewport=vp, device_scale_factor=dsf)
        pg = ctx.new_page()
        pg.goto('file:///workspace/bellarich-site/index.html', wait_until='networkidle')
        pg.wait_for_timeout(600)
        pg.screenshot(path=f'/workspace/bellarich-site/shots/final-{label}-full.png', full_page=True)
        acts = pg.query_selector('.contact__acts')
        acts.scroll_into_view_if_needed()
        pg.wait_for_timeout(500)
        box = acts.bounding_box()
        pg.screenshot(path=f'/workspace/bellarich-site/shots/final-{label}-contact.png',
                      clip={'x': max(0, box['x'] - 12), 'y': max(0, box['y'] - 12),
                            'width': min(box['width'] + 24, vp['width']), 'height': box['height'] + 24})
        out[label] = pg.evaluate("""() => {
          const de = document.documentElement;
          const btns = [...document.querySelectorAll('.contact__acts a')].map(a => {
            const r = a.getBoundingClientRect(); const s = getComputedStyle(a);
            return {text: a.textContent.trim().replace(/\\s+/g,' '), href: a.getAttribute('href'),
                    x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height),
                    visible: r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && parseFloat(s.opacity) > .1,
                    inViewportX: r.x >= -1 && r.right <= de.clientWidth + 1};
          });
          return {vw: de.clientWidth, scrollW: de.scrollWidth, buttons: btns};
        }""")
        ctx.close()
    b.close()
print(json.dumps(out, ensure_ascii=False, indent=2))
