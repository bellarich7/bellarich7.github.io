#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Video card: anchor href/target, thumbnail untouched, zero external requests before click."""
import json, sys
from playwright.sync_api import sync_playwright

url = sys.argv[1] if len(sys.argv) > 1 else 'file:///workspace/bellarich-site/index.html'
prefix = sys.argv[2] if len(sys.argv) > 2 else 'vid'

EXT = ('youtube.com', 'ytimg.com', 'googlevideo.com', 'youtu.be', 'google-analytics')

with sync_playwright() as p:
    b = p.chromium.launch()
    out = {}
    for label, vp, dsf in (('pc', {'width': 1440, 'height': 900}, 1),
                           ('m390', {'width': 390, 'height': 844}, 2)):
        ctx = b.new_context(viewport=vp, device_scale_factor=dsf)
        pg = ctx.new_page()
        ext, failed, errs = [], [], []
        pg.on('request', lambda r: ext.append(r.url) if any(h in r.url for h in EXT) else None)
        pg.on('requestfailed', lambda r: failed.append(r.url))
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(url, wait_until='networkidle')
        pg.wait_for_timeout(600)
        card = pg.query_selector('#videoCard')
        card.scroll_into_view_if_needed()
        pg.wait_for_timeout(400)
        box = card.bounding_box()
        pg.screenshot(path=f'/workspace/bellarich-site/shots/{prefix}-{label}-card.png',
                      clip={'x': max(0, box['x'] - 10), 'y': max(0, box['y'] - 10),
                            'width': min(box['width'] + 20, vp['width']), 'height': box['height'] + 20})
        info = pg.evaluate("""() => {
          const a = document.querySelector('.video-card__thumb');
          const cap = document.querySelector('.video-card__yt');
          const cs = getComputedStyle(a);
          const r = a.getBoundingClientRect();
          const bg = cs.backgroundImage.slice(0, 40);
          const bgLen = cs.backgroundImage.length;
          return {
            tag: a.tagName, id: a.id, href: a.getAttribute('href'), target: a.getAttribute('target'),
            rel: a.getAttribute('rel'), aria: a.getAttribute('aria-label'),
            w: Math.round(r.width), h: Math.round(r.height),
            bgPrefix: bg, bgLength: bgLen,
            capHref: cap && cap.getAttribute('href'), capTarget: cap && cap.getAttribute('target'),
            hasIframe: !!document.querySelector('iframe'),
            hasFallback: !!document.getElementById('videoFallback'),
            playBtn: !!document.querySelector('.video-card__play'),
            cursor: cs.cursor
          };
        }""")
        info['external_requests_before_click'] = ext
        info['failed_requests'] = failed
        info['page_errors'] = errs
        out[label] = info
        ctx.close()
    b.close()
print(json.dumps(out, ensure_ascii=False, indent=2))
