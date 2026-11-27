#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""라이브 /plan/in-kind/ .pkind 배경 변경 검증 — 색·대비·레이아웃·에러."""
import json, sys
from playwright.sync_api import sync_playwright

URL = 'https://bellarich.co.kr/plan/in-kind/?v=bgver1'

AUDIT = r"""() => {
  function parse(c) { const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return null;
    const p = m[1].split(',').map(x => parseFloat(x));
    return {r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1}; }
  function lum(c) { const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
    return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b); }
  function bgOf(el) { let n = el; while (n && n !== document.documentElement) {
      const c = parse(getComputedStyle(n).backgroundColor); if (c && c.a >= 0.99) return c; n = n.parentElement; }
    return {r: 255, g: 255, b: 255, a: 1}; }
  function contrast(fg, bg) { const L1 = lum(fg), L2 = lum(bg);
    const hi = Math.max(L1, L2), lo = Math.min(L1, L2); return Math.round(((hi + 0.05) / (lo + 0.05)) * 100) / 100; }
  const hex = c => '#' + [c.r, c.g, c.b].map(v => Math.round(v).toString(16).padStart(2, '0')).join('').toUpperCase();
  const root = document.querySelector('.pkind');
  const out = [];
  const walk = el => { for (const n of el.childNodes) {
      if (n.nodeType === 3) { const t = n.textContent.replace(/\s+/g, ' ').trim(); if (!t) continue;
        const cs = getComputedStyle(el), fg = parse(cs.color), bg = bgOf(el);
        out.push({text: t.slice(0, 40), tag: el.tagName.toLowerCase() + (el.className ? '.' + String(el.className).split(' ')[0] : ''),
                  color: hex(fg), bg: hex(bg), weight: cs.fontWeight, size: cs.fontSize, contrast: contrast(fg, bg)});
      } else if (n.nodeType === 1) { if (n.tagName === 'BR') continue; walk(n); } } };
  walk(root);
  const cs = getComputedStyle(root);
  const cards = [...root.querySelectorAll('.pkind__pair > div, .pkind__node')]
      .map(e => getComputedStyle(e).backgroundColor);
  return {panel: hex(parse(cs.backgroundColor)), border: cs.borderTopColor,
          items: out, cards: [...new Set(cards)],
          minContrast: Math.min(...out.map(o => o.contrast)),
          minItem: out.reduce((a, b) => a.contrast <= b.contrast ? a : b),
          under45: out.filter(o => o.contrast < 4.5).length,
          under7: out.filter(o => o.contrast < 7).length,
          scrollW: document.documentElement.scrollWidth, clientW: document.documentElement.clientWidth,
          cols: root.querySelectorAll('.pkind__cols > *').length,
          nodes: root.querySelectorAll('.pkind__node').length};
}"""

with sync_playwright() as p:
    b = p.chromium.launch(args=['--no-sandbox'])
    res = {}
    for width in (320, 390, 768, 1440):
        pg = b.new_page(viewport={'width': width, 'height': 900}, device_scale_factor=2)
        errs, bad = [], []
        pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.on('response', lambda r: bad.append((r.status, r.url)) if r.status >= 400 else None)
        pg.goto(URL, wait_until='load')
        pg.wait_for_timeout(900)
        pg.evaluate("() => document.querySelector('.pkind').scrollIntoView()")
        pg.wait_for_timeout(300)
        a = pg.evaluate(AUDIT)
        a['errors'] = errs
        a['bad_responses'] = bad
        res[width] = a
        print('== width', width, 'panel', a['panel'], 'border', a['border'], 'cards', a['cards'],
              'scrollW', a['scrollW'], 'clientW', a['clientW'])
        print('   items', len(a['items']), 'minContrast', a['minContrast'], 'under4.5', a['under45'], 'under7', a['under7'],
              'nodes', a['nodes'], 'cols', a['cols'])
        print('   minItem', a['minItem']['text'], a['minItem']['color'], a['minItem']['bg'], a['minItem']['contrast'])
        print('   errors', errs, 'bad', bad)
        pg.close()
    b.close()
json.dump(res, open('shots/pkind-bg/verify.json', 'w'), ensure_ascii=False, indent=1)
