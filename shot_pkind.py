#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""라이브/로컬 /plan/in-kind/ 의 .pkind 블록만 잘라 캡처합니다(스티키 헤더 겹침 없이).
   사용: shot_pkind.py <url> <prefix> [outdir]"""
import os, sys
from playwright.sync_api import sync_playwright

url = sys.argv[1]
prefix = sys.argv[2]
outdir = sys.argv[3] if len(sys.argv) > 3 else os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'shots', 'pkind-bg')
os.makedirs(outdir, exist_ok=True)

BOX = """() => { const el = document.querySelector('.pkind'); const r = el.getBoundingClientRect();
  return {x: r.x + window.scrollX, y: r.y + window.scrollY, w: r.width, h: r.height,
          bg: getComputedStyle(el).backgroundColor}; }"""

with sync_playwright() as p:
    b = p.chromium.launch(args=['--no-sandbox'])
    for width in (390, 1440):
        pg = b.new_page(viewport={'width': width, 'height': 900}, device_scale_factor=2)
        pg.goto(url, wait_until='load')
        pg.wait_for_timeout(700)
        # 페이지 전체를 한 번에 그려 요소 위치를 잡습니다
        pg.evaluate("() => { const el = document.querySelector('.pkind'); el.scrollIntoView(); }")
        pg.wait_for_timeout(300)
        box = pg.evaluate(BOX)
        path = os.path.join(outdir, '%s-%d.png' % (prefix, width))
        pg.screenshot(path=path, full_page=True,
                      clip={'x': box['x'], 'y': box['y'], 'width': box['w'], 'height': box['h']})
        print(width, box, path)
        pg.close()
    b.close()
