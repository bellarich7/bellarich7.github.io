#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""라이브 /plan/in-kind/ .pkind 블록 글자색 전수 목록 출력."""
import json
import sys
from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else 'https://bellarich.co.kr/plan/in-kind/?v=flow3'

AUDIT = r"""() => {
  function parse(c) {
    const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return null;
    const p = m[1].split(',').map(x => parseFloat(x));
    return {r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1};
  }
  function lum(c) { const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
    return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b); }
  function bgOf(el) { let n = el; while (n && n !== document.documentElement) {
      const c = parse(getComputedStyle(n).backgroundColor); if (c && c.a >= 0.99) return c; n = n.parentElement; }
    return {r: 255, g: 255, b: 255, a: 1}; }
  function contrast(fg, bg) { const L1 = lum(fg), L2 = lum(bg);
    const hi = Math.max(L1, L2), lo = Math.min(L1, L2); return Math.round(((hi + 0.05) / (lo + 0.05)) * 100) / 100; }
  const hex = c => '#' + [c.r, c.g, c.b].map(v => Math.round(v).toString(16).padStart(2, '0')).join('').toUpperCase();
  const root = document.querySelector('.pkind'); if (!root) return {error: 'no .pkind'};
  const out = [];
  const walk = el => { for (const n of el.childNodes) {
      if (n.nodeType === 3) { const t = n.textContent.replace(/\s+/g, ' ').trim(); if (!t) continue;
        const cs = getComputedStyle(el), fg = parse(cs.color), bg = bgOf(el);
        out.push({text: t.slice(0, 46), tag: el.tagName.toLowerCase() + (el.className ? '.' + String(el.className).split(' ')[0] : ''),
                  color: hex(fg), bg: hex(bg), weight: cs.fontWeight, size: cs.fontSize, contrast: contrast(fg, bg)});
      } else if (n.nodeType === 1) { if (n.tagName === 'BR') continue; walk(n); } } };
  walk(root);
  return {panel: getComputedStyle(root).backgroundColor, items: out,
          minContrast: Math.min(...out.map(o => o.contrast)), under45: out.filter(o => o.contrast < 4.5).length,
          under7: out.filter(o => o.contrast < 7).length};
}"""

with sync_playwright() as p:
    b = p.chromium.launch(args=['--no-sandbox'])
    pg = b.new_page(viewport={'width': 1440, 'height': 1000})
    pg.goto(URL, wait_until='load')
    pg.wait_for_timeout(900)
    a = pg.evaluate(AUDIT)
    print('items', len(a['items']), 'min', a['minContrast'], 'under4.5', a['under45'], 'under7', a['under7'], 'panel', a['panel'])
    for it in a['items']:
        print('%-26s %-20s %-8s %-8s w%-4s %-7s %.2f' % (it['text'][:24], it['tag'], it['color'], it['bg'], it['weight'], it['size'], it['contrast']))
    b.close()
