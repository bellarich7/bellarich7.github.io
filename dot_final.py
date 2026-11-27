#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""최종 후보: 0.9em 점 — 390px / 1440px 렌더"""
import os
from playwright.sync_api import sync_playwright

SRC = 'file:///workspace/bellarich-site/plan/retirement/index.html'
OUT = '/workspace/bellarich-site/shots/dots'
DOT = '<span style="font-size:0.9em;vertical-align:0.1em;margin-right:1px">•</span>'
BASE = ['◆ 안전한 부동산 채권을 통한 확정 이자 수익',
        '◆ 공유 비즈니스센터 등 개발 및 공간분석을 통한 임대차 확보, 상권분석 리테일']

with sync_playwright() as p:
    b = p.chromium.launch()
    for w, h, tag in ((390, 844, '390'), (1440, 900, '1440')):
        ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2)
        pg = ctx.new_page()
        pg.goto(SRC, wait_until='load')
        pg.wait_for_timeout(600)
        pg.evaluate("""([html, base]) => {
          const rows = [...document.querySelectorAll('.m-rows .m-row')].slice(1);
          rows.forEach((r, i) => { r.querySelector('span').innerHTML = html + ' ' + base[i].slice(2); });
          const s = document.querySelector('.m-lead');
          window.scrollTo(0, s.getBoundingClientRect().top + window.scrollY - 90);
        }""", [DOT, BASE])
        pg.wait_for_timeout(300)
        pg.query_selector('.m-rows').screenshot(path=os.path.join(OUT, f'F_final_{tag}.png'))
        info = pg.evaluate("""() => {
          const rows=[...document.querySelectorAll('.m-rows .m-row')].slice(1);
          return rows.map(r=>{const sp=r.querySelector('span'), d=sp.querySelector('span');
            const dr=d.getBoundingClientRect(); const t=sp.lastChild;
            const rg=document.createRange(); rg.setStart(t,1); rg.setEnd(t,2);
            const c=rg.getClientRects()[0];
            return {dot:[+dr.width.toFixed(1),+dr.height.toFixed(1)],
                    dotMid:+((dr.top+dr.bottom)/2).toFixed(1),
                    charMid:+((c.top+c.bottom)/2).toFixed(1),
                    gap:+(c.left-dr.right).toFixed(1),
                    lines:Math.round(sp.getBoundingClientRect().height/(15*1.8))};});
        }""")
        print(tag, info)
        ctx.close()
    b.close()
