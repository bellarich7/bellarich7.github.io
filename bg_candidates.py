#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""라이브 /plan/in-kind/ 의 .pkind 블록 배경 후보들을 같은 화면에서 비교 캡처합니다.
   --out DIR 로 저장 위치를 정합니다. 기본은 shots/pkind-bg/."""
import os, sys
from playwright.sync_api import sync_playwright

URL = 'https://bellarich.co.kr/plan/in-kind/?v=bgcmp1'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shots', 'pkind-bg')
if '--out' in sys.argv:
    OUT = sys.argv[sys.argv.index('--out') + 1]
os.makedirs(OUT, exist_ok=True)

CANDS = [
    ('now_F7F2E8', None),
    ('c1_F2EBDD', '#F2EBDD'),
    ('c2_F0E7D6', '#F0E7D6'),
    ('c3_ECE2CE', '#ECE2CE'),
]

INFO = """() => {
  const el = document.querySelector('.pkind');
  const cs = getComputedStyle(el);
  const r = el.getBoundingClientRect();
  return {bg: cs.backgroundColor, border: cs.borderTopColor, h: Math.round(r.height), w: Math.round(r.width)};
}"""

with sync_playwright() as p:
    b = p.chromium.launch(args=['--no-sandbox'])
    for width in (390, 1440):
        pg = b.new_page(viewport={'width': width, 'height': 900}, device_scale_factor=2)
        for name, color in CANDS:
            pg.goto(URL, wait_until='load')
            pg.wait_for_timeout(500)
            if color:
                pg.add_style_tag(content='.pkind{background:%s !important}' % color)
                pg.wait_for_timeout(150)
            info = pg.evaluate(INFO)
            el = pg.query_selector('.pkind')
            el.scroll_into_view_if_needed()
            pg.wait_for_timeout(250)
            path = os.path.join(OUT, '%s-%d.png' % (name, width))
            el.screenshot(path=path)
            print(width, name, info, path)
        pg.close()
    b.close()
