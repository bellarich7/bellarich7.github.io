#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""승계 탭 흐름도 삭제 + /plan/in-kind/ 글자 대비 점검.

usage: python3 measure_flow_remove.py <label> [base]
  label: before / after (캡처·json 접두어)
  base : 기본 file://<repo>/  (라이브는 https://bellarich.co.kr/)
"""
import json
import os
import sys
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(ROOT, 'shots', 'suc-flow-remove')
os.makedirs(SHOTS, exist_ok=True)

label = sys.argv[1] if len(sys.argv) > 1 else 'state'
home_file = os.environ.get('HOME_FILE', 'index.html')
base = sys.argv[2] if len(sys.argv) > 2 else 'file://' + ROOT + '/'
if not base.endswith('/'):
    base += '/'

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
    title: (c.querySelector('h3') || {}).textContent }));
  const flow = q('#panel-suc .suc-flow');
  const note = q('#panel-suc .panel__note');
  const cs = note ? getComputedStyle(note) : null;
  return {
    docH: de.scrollHeight, hor: de.scrollWidth - de.clientWidth, over: [...new Set(over)].slice(0, 8),
    tabs: [tab('tab-life'), tab('tab-suc'), tab('tab-fin')],
    life: cards('life'), suc: cards('suc'), fin: cards('fin'),
    flow: !!flow, flowText: flow ? flow.textContent.replace(/\\s+/g, ' ').trim() : null,
    noteText: note ? note.textContent.trim() : null,
    noteMarginBottom: cs ? cs.marginBottom : null,
    sucPanelH: q('#panel-suc') ? Math.round(q('#panel-suc').getBoundingClientRect().height) : null,
    sucCardsTop: q('#panel-suc .cards') ? Math.round(q('#panel-suc .cards').getBoundingClientRect().top + scrollY) : null,
    sucFlowTop: flow ? Math.round(flow.getBoundingClientRect().top + scrollY) : null,
  };
}"""

AUDIT = """() => {
  function parse(c) {
    const m = c.match(/rgba?\\(([^)]+)\\)/); if (!m) return null;
    const p = m[1].split(',').map(x => parseFloat(x));
    return {r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1};
  }
  function lum(c) {
    const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
    return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b);
  }
  function bgOf(el) {
    let n = el;
    while (n && n !== document.documentElement) {
      const c = parse(getComputedStyle(n).backgroundColor);
      if (c && c.a >= 0.99) return c;
      n = n.parentElement;
    }
    return {r: 255, g: 255, b: 255, a: 1};
  }
  function contrast(fg, bg) {
    const L1 = lum(fg), L2 = lum(bg);
    const hi = Math.max(L1, L2), lo = Math.min(L1, L2);
    return Math.round(((hi + 0.05) / (lo + 0.05)) * 100) / 100;
  }
  const hex = c => '#' + [c.r, c.g, c.b].map(v => Math.round(v).toString(16).padStart(2, '0')).join('').toUpperCase();
  const root = document.querySelector('.pkind');
  if (!root) return {error: 'no .pkind'};
  const out = [];
  const walk = el => {
    for (const n of el.childNodes) {
      if (n.nodeType === 3) {
        const t = n.textContent.replace(/\\s+/g, ' ').trim();
        if (!t) continue;
        const cs = getComputedStyle(el);
        const fg = parse(cs.color), bg = bgOf(el);
        out.push({
          text: t.slice(0, 40),
          tag: el.tagName.toLowerCase() + (el.className ? '.' + String(el.className).split(' ')[0] : ''),
          color: hex(fg), bg: hex(bg), weight: cs.fontWeight, size: cs.fontSize,
          contrast: contrast(fg, bg)
        });
      } else if (n.nodeType === 1) {
        if (n.tagName === 'BR') continue;
        walk(n);
      }
    }
  };
  walk(root);
  const panel = getComputedStyle(root);
  return {
    panel: {bg: panel.backgroundColor, border: panel.borderColor},
    items: out,
    minContrast: Math.min(...out.map(o => o.contrast)),
    under45: out.filter(o => o.contrast < 4.5).length,
    under7: out.filter(o => o.contrast < 7).length
  };
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
        pg.goto((base + home_file) if base.startswith('file:') else base, wait_until='load')
        pg.wait_for_timeout(700)
        d = pg.evaluate(READ)
        pg.click('#tab-suc')
        pg.wait_for_timeout(450)
        d['sucOpen'] = pg.evaluate("""() => {
          const de = document.documentElement, p = document.querySelector('#panel-suc');
          const note = p.querySelector('.panel__note'), cards = p.querySelector('.cards');
          const flow = p.querySelector('.suc-flow');
          return {docH: de.scrollHeight, panelH: Math.round(p.getBoundingClientRect().height),
                  noteBottom: Math.round(note.getBoundingClientRect().bottom),
                  cardsTopPage: Math.round(cards.getBoundingClientRect().top + scrollY),
                  flowH: flow ? Math.round(flow.getBoundingClientRect().height) : null,
                  gapNoteCards: note ? Math.round(cards.getBoundingClientRect().top - note.getBoundingClientRect().bottom) : null};
        }""")
        d['errors'], d['bad'] = errs, bad
        if w in (1440, 390):
            pg.query_selector('#solutions').screenshot(path=os.path.join(SHOTS, '%s-home-suc-%d.png' % (label, w)))
        report['%dx%d' % (w, h)] = dict(d, docH=d['docH'], docH_sucOpen=d['sucOpen']['docH'])
        ctx.close()

    for w, h, dsf in ((1440, 1000, 1), (390, 844, 2)):
        ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=dsf)
        pg = ctx.new_page()
        errs, bad = [], []
        pg.on('pageerror', lambda e: errs.append('pageerror: ' + str(e)[:160]))
        pg.on('console', lambda m: errs.append('console: ' + m.text[:160]) if m.type == 'error' else None)
        pg.on('response', lambda r: bad.append('%s %s' % (r.status, r.url)) if r.status >= 400 else None)
        url = (base + 'plan/in-kind/index.html') if base.startswith('file:') else (base + 'plan/in-kind/')
        pg.goto(url, wait_until='load')
        pg.wait_for_timeout(700)
        a = pg.evaluate(AUDIT)
        a['errors'], a['bad'] = errs, bad
        y = pg.evaluate("() => Math.round(document.querySelector('.pkind').getBoundingClientRect().top + scrollY) - (window.innerWidth < 641 ? 20 : 90)")
        pg.evaluate("y => scrollTo(0, y)", y)
        pg.wait_for_timeout(400)
        pg.screenshot(path=os.path.join(SHOTS, '%s-inkind-%d.png' % (label, w)))
        if w == 390:
            el = pg.query_selector('.pkind')
            el.screenshot(path=os.path.join(SHOTS, '%s-inkind-block-%d.png' % (label, w)))
        report['inkind-%d' % w] = a
        ctx.close()
    b.close()

with open(os.path.join(SHOTS, label + '.json'), 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=1)
print(json.dumps(report, ensure_ascii=False, indent=1))
