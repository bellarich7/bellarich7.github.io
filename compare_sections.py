#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compare section heights between two built pages and report console/network health."""
import json, sys
from playwright.sync_api import sync_playwright

files = sys.argv[1:3]
if len(files) != 2:
    raise SystemExit('usage: compare_sections.py <a.html> <b.html>')

JS = """() => {
  const out = {};
  document.querySelectorAll('main > section, footer').forEach((s, i) => {
    const k = s.id || (s.className || s.tagName).toString().slice(0, 24);
    out[k] = Math.round(s.getBoundingClientRect().height);
  });
  return out;
}"""

res = {}
with sync_playwright() as p:
    b = p.chromium.launch()
    for idx, f in enumerate(files):
        for label, vp in (('pc', {'width': 1440, 'height': 900}), ('m390', {'width': 390, 'height': 844})):
            ctx = b.new_context(viewport=vp)
            pg = ctx.new_page()
            errs, failed = [], []
            pg.on('pageerror', lambda e: errs.append(str(e)))
            pg.on('console', lambda m: errs.append('console.' + m.type + ': ' + m.text) if m.type == 'error' else None)
            pg.on('requestfailed', lambda r: failed.append(r.url + ' :: ' + str(r.failure)))
            pg.goto(f, wait_until='networkidle')
            pg.wait_for_timeout(800)
            res.setdefault(label, {})['A' if idx == 0 else 'B'] = pg.evaluate(JS)
            res[label].setdefault('health', {})['A' if idx == 0 else 'B'] = {
                'errors': errs, 'failed': failed,
                'scrollW': pg.evaluate('document.documentElement.scrollWidth'),
                'docH': pg.evaluate('document.documentElement.scrollHeight')}
            ctx.close()
    b.close()

for label, d in res.items():
    a, bb = d['A'], d['B']
    print('==', label, 'health A', json.dumps(d['health']['A']))
    print('   health B', json.dumps(d['health']['B']))
    for k in a:
        if a[k] != bb.get(k):
            print(f'   {k}: {a[k]} -> {bb.get(k)}  ({bb.get(k)-a[k]:+d})')
    extra = [k for k in bb if k not in a]
    if extra:
        print('   new keys:', extra)
