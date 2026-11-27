#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""라이브(bellarich.co.kr) 검증 — 흐름도 삭제 + /plan/in-kind/ 글자 대비. 캡처는 downloads/.
usage: python3 verify_live_flow.py [v]
"""
import json
import os
import sys
from playwright.sync_api import sync_playwright

V = sys.argv[1] if len(sys.argv) > 1 else 'flow1'
HOME = 'https://bellarich.co.kr/?v=%s' % V
INKIND = 'https://bellarich.co.kr/plan/in-kind/?v=%s' % V
OUT = '/workspace/downloads'
SLUGS = ['office', 'family-corp', 'retirement', 'home-for-kids', 'tax', 'asset', 'in-kind',
         'startup-succession', 'family-business', 'trust',
         'credit', 'governance', 'incorporation', 'welfare-fund', 'ma']

READ = """() => {
  const de = document.documentElement, q = s => document.querySelector(s);
  const over = [];
  document.querySelectorAll('body *').forEach(el => {
    const r = el.getBoundingClientRect();
    if (r.width > 0 && (r.right > de.clientWidth + 2 || r.left < -2)) {
      const c = (el.className || '').toString();
      if (!/band__track|modal__|br-sprite|hero__glow/.test(c)) over.push(el.tagName + '.' + c.slice(0, 30));
    }
  });
  const tab = id => { const t = q('#' + id); return t ? t.textContent.replace(/\\s+/g, ' ').trim() : null; };
  const cards = g => [...document.querySelectorAll('#panel-' + g + ' .cards > .card')].map(c => ({
    no: (c.querySelector('.card__no') || {}).textContent,
    title: (c.querySelector('h3') || {}).textContent.replace(/\\s+/g, ' ').trim() }));
  const p = q('#panel-suc');
  return {
    docH: de.scrollHeight, hor: de.scrollWidth - de.clientWidth, over: [...new Set(over)].slice(0, 8),
    tabs: [tab('tab-life'), tab('tab-suc'), tab('tab-fin')],
    life: cards('life'), suc: cards('suc'), fin: cards('fin'),
    flow: !!q('#panel-suc .suc-flow'), sucBlock: !!q('.suc-block'),
    note: q('#panel-suc .panel__note') ? q('#panel-suc .panel__note').textContent.trim() : null,
    panelH: p ? Math.round(p.getBoundingClientRect().height) : null,
  };
}"""

AUDIT = """() => {
  function parse(c) {
    const m = c.match(/rgba?\\(([^)]+)\\)/); if (!m) return null;
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
      if (n.nodeType === 3) { const t = n.textContent.replace(/\\s+/g, ' ').trim(); if (!t) continue;
        const cs = getComputedStyle(el), fg = parse(cs.color), bg = bgOf(el);
        out.push({text: t.slice(0, 40), tag: el.tagName.toLowerCase() + (el.className ? '.' + String(el.className).split(' ')[0] : ''),
                  color: hex(fg), bg: hex(bg), weight: cs.fontWeight, size: cs.fontSize, contrast: contrast(fg, bg)});
      } else if (n.nodeType === 1) { if (n.tagName === 'BR') continue; walk(n); } } };
  walk(root);
  return {panel: getComputedStyle(root).backgroundColor, items: out,
          minContrast: Math.min(...out.map(o => o.contrast)), under45: out.filter(o => o.contrast < 4.5).length,
          nodes: document.querySelectorAll('.pkind__node').length, cols: document.querySelectorAll('.pkind__col').length,
          pairs: document.querySelectorAll('.pkind__pair > div').length};
}"""

report = {}
with sync_playwright() as p:
    b = p.chromium.launch(args=['--no-sandbox'])
    for w, h, dsf in ((1440, 900, 1), (768, 1024, 1), (390, 844, 2), (320, 780, 2)):
        ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=dsf)
        pg = ctx.new_page()
        errs, bad = [], []
        pg.on('pageerror', lambda e: errs.append('pageerror: ' + str(e)[:160]))
        pg.on('console', lambda m: errs.append('console: ' + m.text[:160]) if m.type == 'error' else None)
        pg.on('response', lambda r: bad.append('%s %s' % (r.status, r.url)) if r.status >= 400 else None)
        pg.goto(HOME, wait_until='load'); pg.wait_for_timeout(900)
        d = pg.evaluate(READ)
        pg.click('#tab-suc'); pg.wait_for_timeout(450)
        d['docH_sucOpen'] = pg.evaluate("() => document.documentElement.scrollHeight")
        d['panelH_open'] = pg.evaluate("() => Math.round(document.querySelector('#panel-suc').getBoundingClientRect().height)")
        d['errors'], d['bad'] = errs, bad
        for g in ('life', 'suc', 'fin'):
            pg.click('#tab-' + g); pg.wait_for_timeout(350)
            if w in (1440, 390):
                pg.query_selector('#solutions').screenshot(path=os.path.join(OUT, 'home-%s-%d.png' % (g, w)))
        report['%dx%d' % (w, h)] = d
        ctx.close()

    for w, h, dsf in ((1440, 1000, 1), (390, 844, 2)):
        ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=dsf)
        pg = ctx.new_page()
        errs, bad = [], []
        pg.on('pageerror', lambda e: errs.append('pageerror: ' + str(e)[:160]))
        pg.on('console', lambda m: errs.append('console: ' + m.text[:160]) if m.type == 'error' else None)
        pg.on('response', lambda r: bad.append('%s %s' % (r.status, r.url)) if r.status >= 400 else None)
        pg.goto(INKIND, wait_until='load'); pg.wait_for_timeout(800)
        a = pg.evaluate(AUDIT)
        a['errors'], a['bad'] = errs, bad
        a['hor'] = pg.evaluate("() => document.documentElement.scrollWidth - document.documentElement.clientWidth")
        y = pg.evaluate("() => Math.round(document.querySelector('.pkind').getBoundingClientRect().top + scrollY) - (window.innerWidth < 641 ? 20 : 90)")
        pg.evaluate("y => scrollTo(0, y)", y); pg.wait_for_timeout(400)
        pg.screenshot(path=os.path.join(OUT, 'inkind-structure-%d.png' % w))
        pg.query_selector('.pkind').screenshot(path=os.path.join(OUT, 'inkind-block-%d.png' % w))
        report['inkind-%d' % w] = a
        ctx.close()

    ctx = b.new_context(viewport={'width': 1440, 'height': 900})
    pg = ctx.new_page()
    pages = {}
    for s in SLUGS:
        r = pg.goto('https://bellarich.co.kr/plan/%s/?v=%s' % (s, V), wait_until='load')
        pg.wait_for_timeout(150)
        pages[s] = dict(status=r.status, title=pg.title(),
                        h1=pg.evaluate("() => (document.querySelector('.phero h1')||{}).textContent"),
                        cat=pg.evaluate("() => (document.querySelector('.phero__eyebrow')||{}).textContent"))
    for extra in ('', 'check/', 'card/'):
        r = pg.goto('https://bellarich.co.kr/%s?v=%s' % (extra, V), wait_until='load')
        pages[extra or 'home'] = dict(status=r.status, title=pg.title())
    report['pages'] = pages
    ctx.close()
    b.close()

print(json.dumps(report, ensure_ascii=False, indent=1))
