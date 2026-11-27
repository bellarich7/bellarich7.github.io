#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""라이브 CEO 은퇴 플랜 상세: 390px 표 영역 — 점 크기·정렬·넘침 실측 + 캡처"""
import os, json, urllib.request
from playwright.sync_api import sync_playwright

URL = 'https://bellarich.co.kr/plan/retirement/?v=dot'
OUT = '/workspace/bellarich-site/shots'
os.makedirs(OUT, exist_ok=True)

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2)
    pg = ctx.new_page()
    resp = pg.goto(URL, wait_until='load')
    print('HTTP', resp.status, 'url', pg.url)
    pg.wait_for_timeout(1200)

    info = pg.evaluate("""() => {
      const rows = [...document.querySelectorAll('.m-rows .m-row')];
      return {
        vw: document.documentElement.clientWidth,
        scrollW: document.documentElement.scrollWidth,
        rows: rows.map(r => {
          const bEl = r.querySelector('b'), sp = r.querySelector('span');
          const dot = sp.querySelector('span');
          const out = {label: bEl.textContent, dotHTML: dot ? dot.outerHTML.slice(0, 120) : null,
                       text: sp.textContent.slice(0, 40)};
          if (dot) {
            const dr = dot.getBoundingClientRect();
            const t = sp.lastChild;
            const rg = document.createRange(); rg.setStart(t, 1); rg.setEnd(t, 2);
            const c = rg.getClientRects()[0];
            out.dotW = +dr.width.toFixed(2);
            out.dotFontPx = getComputedStyle(dot).fontSize;
            out.dotMidY = +((dr.top + dr.bottom) / 2).toFixed(2);
            out.charMidY = +((c.top + c.bottom) / 2).toFixed(2);
            out.deltaMid = +(out.dotMidY - out.charMidY).toFixed(2);
            out.gap = +(c.left - dr.right).toFixed(2);
            out.blockLeft = +sp.getBoundingClientRect().left.toFixed(2);
            out.textLeft = +c.left.toFixed(2);
          }
          out.spanH = +sp.getBoundingClientRect().height.toFixed(2);
          out.lineHeight = getComputedStyle(sp).lineHeight;
          return out;
        })
      };
    }""")
    print(json.dumps(info, ensure_ascii=False, indent=1))

    pg.evaluate("()=>{const s=document.querySelector('.m-lead'); window.scrollTo(0, s.getBoundingClientRect().top+window.scrollY-90);}")
    pg.wait_for_timeout(400)
    pg.screenshot(path=os.path.join(OUT, 'retirement-after-390-rows.png'))
    pg.query_selector('.m-rows').screenshot(path=os.path.join(OUT, 'retirement-after-390-tablerows.png'))
    # 표 + 리드 문단 함께
    pg.evaluate("()=>{const s=document.querySelector('.m-lead'); window.scrollTo(0, s.getBoundingClientRect().top+window.scrollY-40);}")
    pg.wait_for_timeout(300)
    pg.screenshot(path=os.path.join(OUT, 'retirement-after-390-lead-rows.png'))
    ctx.close(); b.close()
print('saved')
