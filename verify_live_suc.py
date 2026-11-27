#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""라이브(bellarich.co.kr) 최종 검증 — 홈 탭/번호/흐름도, /plan/in-kind/, 15개 상세 페이지, 캡처.

캡처는 downloads/ 에 저장합니다.
usage: python3 verify_live_suc.py [v]
"""
import json
import os
import sys
from playwright.sync_api import sync_playwright

V = sys.argv[1] if len(sys.argv) > 1 else 'suc3'
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
    title: (c.querySelector('h3') || {}).textContent }));
  return {
    hor: de.scrollWidth - de.clientWidth, over: [...new Set(over)].slice(0, 8), docH: de.scrollHeight,
    tabs: [tab('tab-life'), tab('tab-suc'), tab('tab-fin')],
    life: cards('life'), suc: cards('suc'), fin: cards('fin'),
    flow: !!q('#panel-suc .suc-flow'),
    flowText: q('#panel-suc .suc-flow') ? q('#panel-suc .suc-flow').textContent.replace(/\\s+/g, ' ').trim() : null,
    navSuc: [...document.querySelectorAll('.nav__menu .nav__link')].map(a => a.textContent).includes('부동산·가업 승계'),
    blockOnHome: !!q('.suc-block'),
    hrefs: [...document.querySelectorAll('#solutions a[href^="/plan/"]')].map(a => a.getAttribute('href')),
  };
}"""

report = {}
with sync_playwright() as p:
    b = p.chromium.launch(args=['--no-sandbox'])
    # ---------- 홈 ----------
    for w, h, dsf in ((1440, 900, 1), (768, 1024, 1), (390, 844, 2), (320, 780, 2)):
        ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=dsf)
        pg = ctx.new_page()
        errs, bad = [], []
        pg.on('pageerror', lambda e: errs.append('pageerror: ' + str(e)[:160]))
        pg.on('console', lambda m: errs.append('console: ' + m.text[:160]) if m.type == 'error' else None)
        pg.on('response', lambda r: bad.append('%s %s' % (r.status, r.url)) if r.status >= 400 else None)
        pg.goto(HOME, wait_until='load')
        pg.wait_for_timeout(800)
        d = pg.evaluate(READ)
        d['errors'], d['bad'] = errs, bad
        for g in ('life', 'suc', 'fin'):
            pg.click('#tab-' + g)
            pg.wait_for_timeout(350)
            if w in (1440, 390):
                el = pg.query_selector('#solutions')
                el.screenshot(path=os.path.join(OUT, 'home-%s-%d.png' % (g, w)))
        report['%dx%d' % (w, h)] = d
        ctx.close()

    # ---------- /plan/in-kind/ ----------
    for w, h, dsf in ((1440, 1000, 1), (390, 844, 2)):
        ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=dsf)
        pg = ctx.new_page()
        errs, bad = [], []
        pg.on('pageerror', lambda e: errs.append('pageerror: ' + str(e)[:160]))
        pg.on('response', lambda r: bad.append('%s %s' % (r.status, r.url)) if r.status >= 400 else None)
        pg.goto(INKIND, wait_until='load')
        pg.wait_for_timeout(700)
        d = pg.evaluate("""() => {
          const de = document.documentElement, q = s => document.querySelector(s);
          const over = [];
          document.querySelectorAll('body *').forEach(el => { const r = el.getBoundingClientRect();
            if (r.width > 0 && (r.right > de.clientWidth + 2 || r.left < -2)) {
              const c = (el.className || '').toString();
              if (!/br-sprite/.test(c)) over.push(el.tagName + '.' + c.slice(0, 30)); } });
          return {docH: de.scrollHeight, hor: de.scrollWidth - de.clientWidth,
                  over: [...new Set(over)].slice(0, 8), title: document.title,
                  h1: q('.phero h1').textContent, cat: q('.phero__eyebrow').textContent,
                  h3: q('.pkind h3') ? q('.pkind h3').textContent : null,
                  nodes: document.querySelectorAll('.pkind__node').length,
                  cols: document.querySelectorAll('.pkind__col').length,
                  pairs: document.querySelectorAll('.pkind__pair > div').length,
                  order: [...document.querySelectorAll('.pdoc > *')].map(e => e.tagName.toLowerCase() + (e.className ? '.' + String(e.className).split(' ')[0] : ''))};
        }""")
        d['errors'], d['bad'] = errs, bad
        pg.screenshot(path=os.path.join(OUT, 'inkind-top-%d.png' % w))
        y = pg.evaluate("() => Math.round(document.querySelector('.pkind').getBoundingClientRect().top + scrollY) - (window.innerWidth < 641 ? 30 : 100)")
        pg.evaluate("y => scrollTo(0, y)", y)
        pg.wait_for_timeout(400)
        pg.screenshot(path=os.path.join(OUT, 'inkind-structure-%d.png' % w))
        report['inkind-%d' % w] = d
        ctx.close()

    # ---------- 15개 상세 페이지 ----------
    ctx = b.new_context(viewport={'width': 1440, 'height': 900})
    pg = ctx.new_page()
    pages = {}
    for s in SLUGS:
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:120]))
        r = pg.goto('https://bellarich.co.kr/plan/%s/?v=%s' % (s, V), wait_until='load')
        pg.wait_for_timeout(200)
        pages[s] = dict(status=r.status, title=pg.title(),
                        cat=pg.evaluate("() => (document.querySelector('.phero__eyebrow')||{}).textContent"),
                        h1=pg.evaluate("() => (document.querySelector('.phero h1')||{}).textContent"),
                        errs=errs)
    report['planPages'] = pages
    ctx.close()
    b.close()

print(json.dumps(report, ensure_ascii=False, indent=1))
