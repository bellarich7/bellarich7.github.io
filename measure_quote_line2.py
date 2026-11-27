#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""인용구 둘째 줄 위치 측정: 첫 줄 '아' 글자 x와 둘째 줄 왼쪽 x."""
import sys
from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else 'file:///workspace/bellarich-site/index.html'

JS = """() => {
  const q = [...document.querySelectorAll('.hero__cred-quote')].find(e => e.getBoundingClientRect().width > 0);
  if(!q) return {err:'no quote'};
  const qr = q.getBoundingClientRect();
  const tn = q.firstChild; // "“법인을 아는 부동산 전문가,"
  const at = tn.textContent.indexOf('아');
  const r = document.createRange();
  r.setStart(tn, at); r.setEnd(tn, at + 1);
  const ar = r.getBoundingClientRect();
  const l2 = q.querySelector('.hero__quote-l2');
  const l2r = l2 ? l2.getBoundingClientRect() : null;
  // 둘째 줄 실제 글자 시작 x (앞 공백 없음)
  const rt = document.createRange();
  if (l2) { rt.selectNodeContents(l2); }
  const tr = l2 ? rt.getBoundingClientRect() : null;
  return {quote: {x:+qr.left.toFixed(1), w:+qr.width.toFixed(1)},
          line1Ah: {x:+ar.left.toFixed(1)},
          line2: tr ? {x:+tr.left.toFixed(1), w:+tr.width.toFixed(1)} : null,
          line2Box: l2r ? {x:+l2r.left.toFixed(1)} : null};
}"""

with sync_playwright() as p:
    b = p.chromium.launch()
    for label, w, h in [('1440x900', 1440, 900), ('1920x1080', 1920, 1080)]:
        ctx = b.new_context(viewport={'width': w, 'height': h})
        pg = ctx.new_page()
        pg.goto(URL, wait_until='load')
        pg.wait_for_timeout(600)
        print(label, pg.evaluate(JS))
        ctx.close()
    b.close()
