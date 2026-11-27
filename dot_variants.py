#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CEO 은퇴 플랜 표의 점 후보들을 390px에서 렌더해 비교 캡처·실측 (v2)"""
import os, json
from playwright.sync_api import sync_playwright

SRC = 'file:///workspace/bellarich-site/plan/retirement/index.html'
OUT = '/workspace/bellarich-site/shots/dots'
os.makedirs(OUT, exist_ok=True)

V = {
 'A_bullet_075': '<span style="font-size:0.75em;vertical-align:0.1em;margin-right:2px">•</span>',
 'B_bullet_085': '<span style="font-size:0.85em;vertical-align:0.1em;margin-right:2px">•</span>',
 'C_bullet_100': '<span style="font-size:1em;vertical-align:0.1em;margin-right:2px">•</span>',
 'D_css_4px':   '<span aria-hidden="true" style="display:inline-block;width:4px;height:4px;border-radius:50%;background:currentColor;vertical-align:middle;margin-right:6px;position:relative;top:-1px"></span>',
 'E_css_5px':   '<span aria-hidden="true" style="display:inline-block;width:5px;height:5px;border-radius:50%;background:currentColor;vertical-align:middle;margin-right:6px"></span>',
}
BASE = ['◆ 안전한 부동산 채권을 통한 확정 이자 수익',
        '◆ 공유 비즈니스센터 등 개발 및 공간분석을 통한 임대차 확보, 상권분석 리테일']

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2)
    pg = ctx.new_page()
    pg.goto(SRC, wait_until='load')
    pg.wait_for_timeout(500)
    pg.evaluate("()=>{const s=document.querySelector('.m-lead'); window.scrollTo(0, s.getBoundingClientRect().top+window.scrollY-90);}")

    for name, html in V.items():
        res = pg.evaluate("""([html, base]) => {
          const rows = [...document.querySelectorAll('.m-rows .m-row')].slice(1);
          rows.forEach((r, i) => {
            const raw = base[i].slice(2);            // '◆ ' 제거
            r.querySelector('span').innerHTML = html + ' ' + raw;
          });
          return rows.map(r => {
            const sp = r.querySelector('span');
            const dot = sp.querySelector('span');
            const dr = dot.getBoundingClientRect();
            const tn = sp.lastChild;                 // 남은 텍스트 노드(' 안전한...')
            const rg = document.createRange();
            rg.setStart(tn, 1); rg.setEnd(tn, 2);    // 첫 글자 '안'
            const c = rg.getClientRects()[0];
            return {dotW: +dr.width.toFixed(2), dotH: +dr.height.toFixed(2),
                    dotMidY: +((dr.top + dr.bottom) / 2).toFixed(2),
                    charTop: +c.top.toFixed(2), charBottom: +c.bottom.toFixed(2),
                    charMidY: +((c.top + c.bottom) / 2).toFixed(2),
                    gap: +(c.left - dr.right).toFixed(2)};
          });
        }""", [html, BASE])
        print(name, json.dumps(res, ensure_ascii=False))
        pg.wait_for_timeout(150)
        pg.query_selector('.m-rows').screenshot(path=os.path.join(OUT, f'{name}.png'))
    ctx.close(); b.close()
print('saved', OUT)
