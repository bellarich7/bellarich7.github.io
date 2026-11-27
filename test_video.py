#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Video card click test: requests before/after click, player state trace, fallback."""
import sys, json, time
from playwright.sync_api import sync_playwright

url = sys.argv[1] if len(sys.argv) > 1 else 'file:///workspace/bellarich-site/index.html'
prefix = sys.argv[2] if len(sys.argv) > 2 else 'vid'

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2)
    pg = ctx.new_page()
    reqs = []
    fails = []
    errs = []
    cons = []
    pg.on('request', lambda r: reqs.append((r.method, r.url[:120], r.resource_type)))
    pg.on('requestfailed', lambda r: fails.append((r.url[:120], str(r.failure))))
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('console', lambda m: cons.append((m.type, m.text[:200])) if m.type in ('error', 'warning') else None)
    pg.goto(url, wait_until='networkidle')
    pg.wait_for_timeout(800)
    ext_before = [r for r in reqs if not r[1].startswith(('file:', 'data:'))]
    print('external requests BEFORE click:', len(ext_before), ext_before[:5])
    pg.evaluate("document.getElementById('videoCard').scrollIntoView({block:'center'})")
    pg.wait_for_timeout(600)
    pg.screenshot(path=f'/workspace/bellarich-site/shots/{prefix}-card-before.png')
    n0 = len(reqs)
    pg.click('#videoPlay')
    trace = []
    for i in range(14):
        pg.wait_for_timeout(500)
        st = pg.evaluate("""() => {
          const ifr = document.querySelector('.video-card__frame iframe');
          let state = null, err = null;
          try {
            const pl = (window.YT && YT.get) ? YT.get('ytPlayer') : null;
            if (pl && pl.getPlayerState) state = pl.getPlayerState();
          } catch(e) { err = String(e).slice(0, 80); }
          return {iframe: !!ifr, src: ifr ? ifr.src.slice(0, 140) : null,
                  frame: !!document.querySelector('.video-card__frame'),
                  fallback: !!document.getElementById('videoFallback'),
                  state: state, err: err};
        }""")
        trace.append((i * 0.5 + 0.5, st))
    print('trace:')
    for t, s in trace:
        print(f'  {t:4.1f}s', json.dumps(s, ensure_ascii=False))
    pg.screenshot(path=f'/workspace/bellarich-site/shots/{prefix}-card-after.png')
    after = [r for r in reqs[n0:] if not r[1].startswith(('file:', 'data:'))]
    print('\nrequests after click:', len(after))
    for r in after[:25]:
        print('   ', r)
    print('\nfailed requests:', fails)
    print('page errors:', errs)
    print('console err/warn:', cons[:10])
    ctx.close()
    b.close()
