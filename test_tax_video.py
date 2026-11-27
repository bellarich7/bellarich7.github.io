#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""모바일·PC에서 /plan/tax/ 영상 클릭 동작 검증."""
import sys
from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else 'https://bellarich.co.kr/plan/tax/?v=1127x'

with sync_playwright() as p:
    b = p.chromium.launch()
    for label, w, h, mob in [('mobile390', 390, 844, True), ('pc1440', 1440, 900, False)]:
        ctx = b.new_context(viewport={'width': w, 'height': h}, is_mobile=mob,
                            has_touch=mob, device_scale_factor=2 if mob else 1,
                            user_agent=('Mozilla/5.0 (Linux; Android 13; SM-S918N) AppleWebKit/537.36 '
                                        '(KHTML, like Gecko) Chrome/120.0 Mobile Safari/537.36') if mob else None)
        pg = ctx.new_page()
        errs = []
        pg.on('console', lambda m: errs.append(m.type + ': ' + m.text) if m.type == 'error' else None)
        pg.goto(URL, wait_until='load')
        pg.wait_for_timeout(1500)
        btn = pg.query_selector('#videoPlay')
        box = btn.bounding_box() if btn else None
        info = {'label': label, 'btnBox': box}
        if btn:
            if mob:
                btn.tap()
            else:
                btn.click()
            pg.wait_for_timeout(4000)
            ifr = pg.query_selector('#videoFrame iframe')
            info['iframe'] = bool(ifr)
            if ifr:
                info['src'] = ifr.get_attribute('src')
                fr = ifr.content_frame()
                try:
                    txt = fr.inner_text('body', timeout=5000)
                    info['frameText'] = txt[:200].replace('\n', ' | ')
                except Exception as e:
                    info['frameText'] = 'ERR ' + str(e)
            info['isPlayingClass'] = 'is-playing' in (pg.get_attribute('#videoCard', 'class') or '')
            info['thumbVisible'] = pg.is_visible('#videoPlay')
            pg.screenshot(path=f'/workspace/bellarich-site/shots/taxvideo-{label}.png', full_page=False)
        info['errors'] = errs[:5]
        print(info)
        ctx.close()
    b.close()
