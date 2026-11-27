#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""상세 페이지 스크린샷: 390 / 1440 (전체 + 상단/본문/CTA)"""
import os, sys
from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8765/plan/tax/'
TAG = sys.argv[2] if len(sys.argv) > 2 else 'local'
OUT = '/workspace/bellarich-site/shots'
os.makedirs(OUT, exist_ok=True)

with sync_playwright() as p:
    b = p.chromium.launch()
    for w, h in [(1440, 900), (390, 844)]:
        ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=1)
        pg = ctx.new_page()
        errs, failed = [], []
        pg.on('pageerror', lambda e: errs.append('pageerror: ' + str(e)))
        pg.on('console', lambda m: errs.append('console: ' + m.text) if m.type == 'error' else None)
        pg.on('requestfailed', lambda r: failed.append(r.url + ' ' + str(r.failure)))
        pg.goto(URL, wait_until='load')
        pg.wait_for_timeout(1200)
        info = pg.evaluate("""() => {
          const de = document.documentElement, over = [];
          document.querySelectorAll('body *').forEach(el => {
            const r = el.getBoundingClientRect();
            if (r.width > 0 && (r.right > de.clientWidth + 1 || r.left < -1)) {
              const c = (el.className || '').toString();
              if (!/br-sprite|band__track/.test(c)) over.push(el.tagName + '.' + c.slice(0, 40) + '@' + Math.round(r.right));
            }
          });
          const q = s => { const e = document.querySelector(s); return e ? Math.round(e.getBoundingClientRect().height) : null; };
          return {vw: de.clientWidth, scrollW: de.scrollWidth, docH: de.scrollHeight, over: over.slice(0, 10),
            h1: (document.querySelector('h1')||{}).innerText,
            topH: q('.phero'), bodyH: q('.pdoc'), ctaH: q('.pcta'),
            video: !!document.querySelector('#videoCard'),
            contactBtns: [...document.querySelectorAll('[data-contact-link]')].map(a => a.getAttribute('href')),
            tel: [...document.querySelectorAll('a[href^="tel:"]')].map(a => a.getAttribute('href')),
            home: [...document.querySelectorAll('.pnav a, .pcta a, .plogo')].map(a => a.getAttribute('href')).filter(Boolean),
          };}""")
        print('--- %d ---' % w, info)
        print('errors', errs, '| failed', failed)
        pg.screenshot(path=os.path.join(OUT, 'plan-%s-%d-full.png' % (TAG, w)), full_page=True)
        pg.screenshot(path=os.path.join(OUT, 'plan-%s-%d-top.png' % (TAG, w)))
        pg.evaluate("()=>{const s=document.querySelector('.pdoc'); window.scrollTo(0, s.getBoundingClientRect().top+window.scrollY-70);}")
        pg.wait_for_timeout(400)
        pg.screenshot(path=os.path.join(OUT, 'plan-%s-%d-doc.png' % (TAG, w)))
        pg.evaluate("()=>{const s=document.querySelector('.pcta'); window.scrollTo(0, document.documentElement.scrollHeight);}")
        pg.wait_for_timeout(400)
        pg.screenshot(path=os.path.join(OUT, 'plan-%s-%d-cta.png' % (TAG, w)))
        ctx.close()
    b.close()
