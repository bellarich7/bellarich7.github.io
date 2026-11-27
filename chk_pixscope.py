#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""메인 페이지 픽셀 비교 — 솔루션 카드 밖 영역이 그대로인지."""
import os
from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright

BEFORE = 'file:///workspace/tmp/plan-base/index-before.html'
AFTER = 'file:///workspace/bellarich-site/index.html'
OUT = '/workspace/tmp/pixdiff'
os.makedirs(OUT, exist_ok=True)
SECTIONS = ['.hero', '#about', '#philosophy', '#contact', 'footer.footer', '.sol__head', '.tabs']

with sync_playwright() as p:
    b = p.chromium.launch()
    for w, h in [(1440, 900), (390, 844)]:
        for name, url in [('before', BEFORE), ('after', AFTER)]:
            ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=1)
            pg = ctx.new_page()
            pg.goto(url, wait_until='load')
            pg.add_style_tag(content='*,*::before,*::after{transition:none!important;animation:none!important}')
            pg.wait_for_timeout(1500)
            # .rv 등장 애니메이션을 모두 끝냄
            pg.evaluate("()=>{document.querySelectorAll('.rv').forEach(e=>e.classList.add('in')); window.scrollTo(0,document.body.scrollHeight);}")
            pg.wait_for_timeout(900)
            pg.evaluate("()=>window.scrollTo(0,0)")
            pg.wait_for_timeout(500)
            for i, sel in enumerate(SECTIONS):
                el = pg.query_selector(sel)
                if not el:
                    print('missing', sel); continue
                el.screenshot(path=os.path.join(OUT, '%s-%d-%d.png' % (['hero', 'about', 'philo', 'contact', 'footer', 'solhead', 'tabs'][i], w, 0 if name == 'before' else 1)))
            ctx.close()
    b.close()

print('%-10s %-6s %s' % ('section', 'width', 'pixel diff'))
for i, sel in enumerate(SECTIONS):
    nm = ['hero', 'about', 'philo', 'contact', 'footer', 'solhead', 'tabs'][i]
    for w in (1440, 390):
        a = os.path.join(OUT, '%s-%d-0.png' % (nm, w)); c = os.path.join(OUT, '%s-%d-1.png' % (nm, w))
        if not (os.path.exists(a) and os.path.exists(c)):
            print('%-10s %-6s n/a' % (nm, w)); continue
        ia, ic = Image.open(a).convert('RGB'), Image.open(c).convert('RGB')
        if ia.size != ic.size:
            print('%-10s %-6s size differs %s vs %s' % (nm, w, ia.size, ic.size)); continue
        d = ImageChops.difference(ia, ic)
        bbox = d.getbbox()
        px = sum(1 for v in d.getdata() if v != (0, 0, 0))
        print('%-10s %-6s %s  (diff bbox %s)' % (nm, w, 'IDENTICAL' if px == 0 else '%d px (%.3f%%)' % (px, 100.0 * px / (ia.size[0] * ia.size[1])), bbox))
