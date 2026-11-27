#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""드로어/헤더 앵커 이동 점검: 클릭 후 대상 섹션의 뷰포트 상단 좌표."""
import os, json
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
URL = 'file://' + os.path.join(ROOT, 'index.html')
ITEMS = [('#home', '홈'), ('#about', '대표소개'), ('#philosophy', '철학'), ('#contact', '상담신청')]

def top_of(pg, sel):
    return pg.evaluate("""(sel) => { const e=document.querySelector(sel); if(!e) return null;
        return Math.round(e.getBoundingClientRect().top); }""", sel)

with sync_playwright() as p:
    b = p.chromium.launch()
    # mobile drawer (390)
    m = b.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
    pm = m.new_page(); pm.goto(URL, wait_until='load'); pm.wait_for_timeout(1200)
    print('--- drawer 390')
    for href, label in ITEMS:
        if not pm.evaluate("document.getElementById('mobileMenu').classList.contains('is-open')"):
            pm.click('.nav__burger'); pm.wait_for_timeout(650)
        pm.click(f'.mobile-menu a[href="{href}"]')
        pm.wait_for_timeout(1400)
        print(' ', label, href, 'target top =', top_of(pm, href if href != '#home' else '#home'),
              '| scrollY', pm.evaluate('Math.round(window.scrollY)'),
              '| hash', pm.evaluate('location.hash'),
              '| locked', pm.evaluate("document.body.classList.contains('is-locked')"),
              '| menu open', pm.evaluate("document.getElementById('mobileMenu').classList.contains('is-open')"))
    m.close()

    # desktop header (1440)
    d = b.new_context(viewport={'width': 1440, 'height': 900})
    pd = d.new_page(); pd.goto(URL, wait_until='load'); pd.wait_for_timeout(1000)
    print('--- nav 1440')
    for href, label in [('#home', '홈'), ('#about', '대표소개'), ('#philosophy', '철학')]:
        pd.click(f'.nav__menu a[href="{href}"]'); pd.wait_for_timeout(1400)
        print(' ', label, href, 'target top =', top_of(pd, href), '| scrollY', pd.evaluate('Math.round(window.scrollY)'))
    pd.click('.nav__cta'); pd.wait_for_timeout(1400)
    print('  상담신청 #contact target top =', top_of(pd, '#contact'), '| scrollY', pd.evaluate('Math.round(window.scrollY)'))
    d.close()

    # reduced motion — drawer should jump immediately
    r = b.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True,
                      reduced_motion='reduce')
    pr = r.new_page(); pr.goto(URL, wait_until='load'); pr.wait_for_timeout(800)
    pr.click('.nav__burger'); pr.wait_for_timeout(500)
    pr.click('.mobile-menu a[href="#about"]')
    pr.wait_for_timeout(250)
    print('--- reduced motion 390: #about top =', top_of(pr, '#about'), 'scrollY', pr.evaluate('Math.round(window.scrollY)'))
    r.close()
    b.close()
