#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""최종 보고용 스크린샷: 카드(누르기 전) / 재생 중(0:05) — 라이브 페이지, 1440·390·360."""
import sys
from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else 'https://bellarich7.github.io/?v=1125k'
OUT = '/workspace/bellarich-site/shots'

with sync_playwright() as p:
    b = p.chromium.launch()
    for label, vp, dsf, mobile in (('1440', {'width': 1440, 'height': 900}, 1, False),
                                   ('390', {'width': 390, 'height': 844}, 2, True),
                                   ('360', {'width': 360, 'height': 740}, 2, True)):
        ctx = b.new_context(viewport=vp, device_scale_factor=dsf, is_mobile=mobile, has_touch=mobile)
        pg = ctx.new_page()
        pg.goto(URL, wait_until='load', timeout=60000)
        pg.wait_for_timeout(1200)
        pg.evaluate("document.getElementById('videoCard').scrollIntoView({block:'center'})")
        pg.wait_for_timeout(1400)   # .rv 등장 애니메이션 끝날 때까지
        box = pg.evaluate("""() => { const c = document.getElementById('videoCard').getBoundingClientRect();
            return {x: Math.round(c.left), y: Math.round(c.top), w: Math.round(c.width), h: Math.round(c.height)}; }""")
        pg.screenshot(path=f'{OUT}/video-final-{label}-1-before.png')
        print(label, 'card box', box)
        if mobile:
            b2 = pg.locator('#videoPlay').bounding_box()
            pg.touchscreen.tap(b2['x'] + b2['width']/2, b2['y'] + b2['height']/2)
        else:
            pg.click('#videoPlay')
        pg.wait_for_timeout(2600)
        pg.evaluate("() => { const v = document.getElementById('videoPlayer'); v.pause(); v.currentTime = 5; }")
        pg.wait_for_timeout(1800)
        pg.evaluate("() => document.getElementById('videoCard').scrollIntoView({block:'center'})")
        pg.wait_for_timeout(500)
        # 마우스를 카드 밖으로 두어 컨트롤이 보이게
        pg.mouse.move(5, 5) if not mobile else None
        pg.wait_for_timeout(300)
        pg.screenshot(path=f'{OUT}/video-final-{label}-2-playing.png')
        st = pg.evaluate("""() => { const v = document.getElementById('videoPlayer');
            return {t: v.currentTime, d: v.duration, paused: v.paused, w: v.videoWidth, h: v.videoHeight,
                    sw: document.documentElement.scrollWidth, vw: document.documentElement.clientWidth}; }""")
        print(label, st)
        ctx.close()
    b.close()
