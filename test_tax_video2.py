#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""모바일에서 재생 버튼이 유튜브로 넘기는지 확인."""
import sys
from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else 'https://bellarich.co.kr/plan/tax/?v=1127y'

with sync_playwright() as p:
    b = p.chromium.launch()
    for label, w, h, mob in [('mobile390', 390, 844, True), ('pc1440', 1440, 900, False)]:
        ctx = b.new_context(viewport={'width': w, 'height': h}, is_mobile=mob, has_touch=mob,
                            device_scale_factor=2 if mob else 1,
                            user_agent=('Mozilla/5.0 (Linux; Android 13; SM-S918N) AppleWebKit/537.36 '
                                        '(KHTML, like Gecko) Chrome/120.0 Mobile Safari/537.36') if mob else None)
        pg = ctx.new_page()
        popups = []
        pg.on('popup', lambda pp: popups.append(pp.url))
        pg.goto(URL, wait_until='load')
        pg.wait_for_timeout(1200)
        btn = pg.query_selector('#videoPlay')
        (btn.tap() if mob else btn.click())
        pg.wait_for_timeout(2500)
        print({'label': label, 'popup': popups,
               'iframe': bool(pg.query_selector('#videoFrame iframe')),
               'playing': 'is-playing' in (pg.get_attribute('#videoCard', 'class') or ''),
               'thumb': pg.is_visible('#videoPlay')})
        pg.screenshot(path=f'/workspace/bellarich-site/shots/taxafter-{label}.png')
        ctx.close()
    b.close()
