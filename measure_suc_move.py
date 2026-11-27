#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""현물출자 카드 승계 탭 이동 점검 — 탭별 카드 번호·배지·문서 높이·가로 넘침·콘솔 에러.

usage: python3 measure_suc_move.py <label> [url]
  label: 캡처 파일 접두어 (before / after)
기본 url 은 로컬 index.html.
"""
import json
import os
import sys
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(ROOT, 'shots', 'suc-move')
os.makedirs(SHOTS, exist_ok=True)

label = sys.argv[1] if len(sys.argv) > 1 else 'state'
url = sys.argv[2] if len(sys.argv) > 2 else 'file://' + os.path.join(ROOT, 'index.html')

READ = """() => {
  const de = document.documentElement;
  const badges = {};
  document.querySelectorAll('.tab').forEach(t => {
    badges[t.id] = t.textContent.replace(/\\s+/g, ' ').trim();
  });
  const panels = {};
  ['life','suc','fin'].forEach(g => {
    const p = document.getElementById('panel-' + g);
    if (!p) return;
    const cards = [...p.querySelectorAll('.cards > .card')].map(c => ({
      no: (c.querySelector('.card__no') || {}).textContent || null,
      title: (c.querySelector('h3') || {}).textContent || null,
      cls: c.className
    }));
    panels[g] = {note: (p.querySelector('.panel__note') || {}).textContent || null,
                 cards, hasBlock: !!p.querySelector('.suc-block')};
  });
  const over = [];
  document.querySelectorAll('body *').forEach(el => {
    const r = el.getBoundingClientRect();
    if (r.width > 0 && (r.right > de.clientWidth + 2 || r.left < -2)) {
      const c = (el.className || '').toString();
      if (!/band__track|modal__|br-sprite/.test(c)) over.push(el.tagName + '.' + c.slice(0, 40));
    }
  });
  return {docH: de.scrollHeight, viewportH: innerHeight, horScroll: de.scrollWidth - de.clientWidth,
          overflow: [...new Set(over)].slice(0, 12), badges, panels};
}"""

with sync_playwright() as p:
    b = p.chromium.launch()
    out = {}
    for w, h, dsf in ((1440, 900, 1), (768, 1024, 1), (390, 844, 2), (320, 780, 2)):
        ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=dsf)
        pg = ctx.new_page()
        errs, bad = [], []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.on('console', lambda m: errs.append('console:' + m.text) if m.type == 'error' else None)
        pg.on('response', lambda r: bad.append('%s %s' % (r.status, r.url)) if r.status >= 400 else None)
        pg.goto(url, wait_until='load')
        pg.wait_for_timeout(500)
        d = pg.evaluate(READ)
        d['errors'] = errs
        d['badResponses'] = bad
        out['%dx%d' % (w, h)] = d
        # 탭별 캡처 (솔루션 섹션)
        for g in ('life', 'suc', 'fin'):
            pg.click('#tab-' + g)
            pg.wait_for_timeout(350)
            el = pg.query_selector('#solutions')
            if el and w in (1440, 390):
                el.screenshot(path=os.path.join(SHOTS, '%s-%s-%d.png' % (label, g, w)))
        ctx.close()
    b.close()

print(json.dumps(out, ensure_ascii=False, indent=1))
