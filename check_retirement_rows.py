#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CEO 은퇴 플랜 상세: 모바일 390px 캡처 + 콤마 간격/표 정렬 실측"""
import os
from playwright.sync_api import sync_playwright

URL = 'https://bellarich.co.kr/plan/retirement/'
OUT = '/workspace/bellarich-site/shots'
os.makedirs(OUT, exist_ok=True)

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2)
    pg = ctx.new_page()
    pg.goto(URL, wait_until='load')
    pg.wait_for_timeout(1500)

    info = pg.evaluate("""() => {
      const lead = document.querySelector('.m-lead');
      const txt = lead.textContent;
      // 문장 안에서 "X," 뒤 글자까지의 실제 간격(px)을 재는 함수
      function gapAfter(src, needle) {
        const i = txt.indexOf(needle);
        if (i < 0) return null;
        const comma = i + needle.length - 1;      // 콤마 위치
        const r1 = document.createRange();
        r1.setStart(lead.firstChild, comma); r1.setEnd(lead.firstChild, comma + 1);
        const r2 = document.createRange();
        r2.setStart(lead.firstChild, comma + 1); r2.setEnd(lead.firstChild, comma + 2);
        const a = r1.getBoundingClientRect(), c = r2.getBoundingClientRect();
        return {commaRight: +a.right.toFixed(2), nextLeft: +c.left.toFixed(2),
                gap: +(c.left - a.right).toFixed(2), nextChar: txt[comma + 1]};
      }
      const rows = [...document.querySelectorAll('.m-rows .m-row')].map(r => {
        const bEl = r.querySelector('b'), sEl = r.querySelector('span');
        const sb = sEl.getBoundingClientRect();
        // span 안 첫 글자의 시작 x
        const rg = document.createRange(); rg.selectNodeContents(sEl);
        const first = rg.getClientRects()[0];
        return {label: bEl.textContent, labelW: +bEl.getBoundingClientRect().width.toFixed(2),
                spanLeft: +sb.left.toFixed(2), textLeft: +first.left.toFixed(2),
                top: +sb.top.toFixed(2), spanW: +sb.width.toFixed(2),
                text: sEl.textContent.slice(0, 26)};
      });
      const cs = getComputedStyle(document.querySelector('.m-row'));
      return {vw: document.documentElement.clientWidth,
              scrollW: document.documentElement.scrollWidth,
              rowsGrid: cs.gridTemplateColumns,
              leadHTML: lead.innerHTML.slice(0, 140),
              gapAfterProductComma: gapAfter(txt, '상품, 상가'),
              gapAfterJiSikComma: gapAfter(txt, '지식산업센터, 오피스텔'),
              gapAfterBunchang: gapAfter(txt, '은퇴 후'),
              rows};
    }""")
    import json
    print(json.dumps(info, ensure_ascii=False, indent=1))

    pg.screenshot(path=os.path.join(OUT, 'retirement-live-390-top.png'))
    # 표 영역이 화면에 오도록 스크롤
    pg.evaluate("()=>{const s=document.querySelector('.m-lead'); window.scrollTo(0, s.getBoundingClientRect().top+window.scrollY-90);}")
    pg.wait_for_timeout(400)
    pg.screenshot(path=os.path.join(OUT, 'retirement-live-390-rows.png'))
    el = pg.query_selector('.m-rows')
    el.screenshot(path=os.path.join(OUT, 'retirement-live-390-tablerows.png'))
    # 표 + 리드 문단을 함께 담은 요소 캡처
    doc = pg.query_selector('.pdoc') or pg.query_selector('.m-rows')
    pg.screenshot(path=os.path.join(OUT, 'retirement-live-390-full.png'), full_page=True)
    ctx.close()
    b.close()
print('saved')
