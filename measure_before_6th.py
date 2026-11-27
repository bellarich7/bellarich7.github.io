#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""5차(수정 전) 상태를 CSS 오버라이드로 재현해 About/경력 높이 비교값을 잽니다."""
import os, json
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
URL = 'file://' + os.path.join(ROOT, 'index.html')

OLD = """
.section{padding:clamp(68px,9vw,132px) 0}
.chips{margin-bottom:clamp(24px,3.4vw,36px)}
.books{margin-top:clamp(46px,6vw,72px);padding-top:clamp(32px,4vw,44px)}
.career{margin-top:clamp(34px,4.4vw,58px);padding-top:clamp(32px,4vw,44px);gap:clamp(24px,4vw,54px)}
.career h4{margin-bottom:18px}
.career li{padding:9px 0 9px 20px;line-height:1.7;border-bottom:1px dotted rgba(11,25,51,.1)}
.career li::before{top:17px}
"""
ADD_LI = """() => {
  const ul = document.querySelector('.career__col--cur ul');
  const li = document.createElement('li');
  li.innerHTML = '<b>현)</b> 중개법인 리맥스 아리지파트너스 이사';
  ul.insertBefore(li, ul.children[4]);
}"""

with sync_playwright() as p:
    b = p.chromium.launch()
    for w, h in [(1440, 900), (390, 844)]:
        c = b.new_context(viewport={'width': w, 'height': h}, is_mobile=w < 500, has_touch=w < 500)
        pg = c.new_page(); pg.goto(URL, wait_until='load'); pg.wait_for_timeout(1200)
        pg.add_style_tag(content=OLD)
        pg.evaluate(ADD_LI)
        pg.wait_for_timeout(400)
        d = pg.evaluate("""() => {
          const r = s => { const e = document.querySelector(s); const b = e.getBoundingClientRect();
            return Math.round(b.height); };
          return {about: r('#about'), career: r('.career'), books: r('.books'), top: r('.about__top'),
                  secPad: getComputedStyle(document.querySelector('#about')).paddingTop};
        }""")
        print(f'BEFORE {w}x{h}', json.dumps(d))
        c.close()
    b.close()
