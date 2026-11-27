#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""6차 수정 점검: 히어로 수용 + About the CEO 글씨/사진 + 경력 블록 높이."""
import os, json
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
URL = 'file://' + os.path.join(ROOT, 'index.html')
SIZES = [(1440, 900), (1366, 768), (1280, 800), (1150, 800), (1024, 768), (1024, 900), (820, 1180), (390, 844)]

with sync_playwright() as p:
    b = p.chromium.launch()
    for w, h in SIZES:
        c = b.new_context(viewport={'width': w, 'height': h})
        pg = c.new_page()
        pg.goto(URL, wait_until='load')
        pg.wait_for_timeout(700)
        d = pg.evaluate("""() => {
          const q = s => document.querySelector(s);
          const r = e => { if (!e) return null; const b = e.getBoundingClientRect();
            return {t: Math.round(b.top), b: Math.round(b.bottom), h: Math.round(b.height),
                    w: Math.round(b.width), l: Math.round(b.left), rt: Math.round(b.right)}; };
          const fs = s => { const e = q(s); return e ? getComputedStyle(e).fontSize : null; };
          const quote = q('.hero__cred-quote');
          return {
            vh: innerHeight,
            media: r(q('.hero__media')),
            heroPadTop: getComputedStyle(q('.hero')).paddingTop,
            cred: r(q('.hero__cred')),
            name: r(q('.hero__cred-name')), nameFs: fs('.hero__cred-name'),
            spanFs: fs('.hero__cred-name span'),
            role: r(q('.hero__cred-role')), roleFs: fs('.hero__cred-role'),
            quote: r(quote), quoteFs: fs('.hero__cred-quote'), quoteLh: getComputedStyle(quote).lineHeight,
            eyebrowFs: fs('.hero__cred-eyebrow'),
            quoteLines: quote ? Math.round(quote.getBoundingClientRect().height / parseFloat(getComputedStyle(quote).lineHeight)) : null,
            slack: quote ? Math.round(innerHeight - quote.getBoundingClientRect().bottom) : null,
            career: r(q('.career')), careerLi: r(q('.career li')),
            about: r(q('#about')), aboutTop: r(q('.about__top')), books: r(q('.books')),
            sectionPad: getComputedStyle(q('#about')).paddingTop,
            liPad: getComputedStyle(q('.career li')).padding,
            liLh: getComputedStyle(q('.career li')).lineHeight,
            h4mb: getComputedStyle(q('.career h4')).marginBottom,
            careerGap: getComputedStyle(q('.career')).columnGap,
            careerMt: getComputedStyle(q('.career')).marginTop,
            careerPt: getComputedStyle(q('.career')).paddingTop,
            curCount: document.querySelectorAll('.career__col--cur li').length,
            pastCount: document.querySelectorAll('.career__col--past li').length,
            horScroll: document.documentElement.scrollWidth - document.documentElement.clientWidth
          };
        }""")
        print(f"\n=== {w}x{h}")
        for k in ('media', 'cred', 'name', 'role', 'quote', 'career'):
            v = d.pop(k)
            print(' ', k, v)
        print(' ', json.dumps(d, ensure_ascii=False))
        c.close()
    b.close()
