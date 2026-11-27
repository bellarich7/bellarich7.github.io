#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""6차 확인용 캡처: 히어로/경력/탭/카드 3탭/짧은 화면."""
import os
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
URL = 'file://' + os.path.join(ROOT, 'index.html')
OUT = os.path.join(ROOT, 'shots')


def top(page, sel, extra=0):
    page.evaluate("""(arg) => {
        const el = document.querySelector(arg.sel);
        if(!el) return;
        window.scrollTo(0, el.getBoundingClientRect().top + window.scrollY - 62 + arg.extra);
    }""", {'sel': sel, 'extra': extra})
    page.wait_for_timeout(600)


with sync_playwright() as p:
    b = p.chromium.launch()
    c = b.new_context(viewport={'width': 1440, 'height': 900})
    pg = c.new_page()
    pg.goto(URL, wait_until='load')
    pg.wait_for_timeout(2200)
    pg.evaluate("document.querySelectorAll('.rv').forEach(e=>e.classList.add('in'))")
    pg.wait_for_timeout(500)
    pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(500)
    pg.screenshot(path=f'{OUT}/desktop-01-hero.png')
    top(pg, '.career'); pg.screenshot(path=f'{OUT}/desktop-04-career.png')
    top(pg, '#solutions', -40); pg.screenshot(path=f'{OUT}/desktop-06-tabs.png')
    el = pg.query_selector('.tabs')
    el.screenshot(path=f'{OUT}/desktop-06-tabs-crop.png')
    top(pg, '#solutions'); pg.screenshot(path=f'{OUT}/desktop-07-solutions-life.png')
    top(pg, '#panel-life', 250); pg.screenshot(path=f'{OUT}/desktop-08-life-cards.png')
    # life bottom (07 + 08 CTA)
    pg.evaluate("""() => { const el = document.querySelector('#panel-life .card--cta');
        window.scrollTo(0, el.getBoundingClientRect().top + window.scrollY - 300); }""")
    pg.wait_for_timeout(600)
    pg.screenshot(path=f'{OUT}/desktop-08b-life-cta.png')
    # suc tab
    pg.evaluate("document.getElementById('tab-suc').click()"); pg.wait_for_timeout(600)
    top(pg, '#solutions', -40); pg.screenshot(path=f'{OUT}/desktop-06b-tabs-suc.png')
    top(pg, '#solutions'); pg.screenshot(path=f'{OUT}/desktop-09-solutions-suc.png')
    # fin tab
    pg.evaluate("document.getElementById('tab-fin').click()"); pg.wait_for_timeout(600)
    top(pg, '#solutions'); pg.screenshot(path=f'{OUT}/desktop-12-solutions-fin.png')
    pg.evaluate("document.getElementById('tab-life').click()"); pg.wait_for_timeout(400)
    # modal for text weight
    pg.click('[data-plan="inv1"]'); pg.wait_for_timeout(900)
    pg.screenshot(path=f'{OUT}/desktop-17-modal-inv1.png')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(400)
    c.close()

    # short screens
    for w, h, name in [(1366, 768, 'desktop-01b-hero-1366x768.png'), (1280, 800, 'desktop-01c-hero-1280x800.png'),
                       (1024, 768, 'desktop-01d-hero-1024x768.png')]:
        cc = b.new_context(viewport={'width': w, 'height': h})
        pp = cc.new_page(); pp.goto(URL, wait_until='load'); pp.wait_for_timeout(1600)
        pp.screenshot(path=f'{OUT}/{name}')
        cc.close()

    # tablet
    t = b.new_context(viewport={'width': 820, 'height': 1180})
    pt = t.new_page(); pt.goto(URL, wait_until='load'); pt.wait_for_timeout(1600)
    pt.evaluate("document.querySelectorAll('.rv').forEach(e=>e.classList.add('in'))"); pt.wait_for_timeout(400)
    top(pt, '#solutions', -20); pt.screenshot(path=f'{OUT}/tablet-06-tabs.png')
    t.close()

    # mobile
    m = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True)
    pm = m.new_page(); pm.goto(URL, wait_until='load'); pm.wait_for_timeout(2000)
    pm.evaluate("document.querySelectorAll('.rv').forEach(e=>e.classList.add('in'))"); pm.wait_for_timeout(400)
    pm.evaluate("window.scrollTo(0,0)"); pm.wait_for_timeout(400)
    pm.screenshot(path=f'{OUT}/mobile-01-hero.png')
    top(pm, '.career'); pm.screenshot(path=f'{OUT}/mobile-04-career.png')
    top(pm, '#solutions', -20); pm.screenshot(path=f'{OUT}/mobile-06-tabs.png')
    top(pm, '#solutions', 200); pm.screenshot(path=f'{OUT}/mobile-09-cards.png')
    pm.evaluate("document.getElementById('tab-suc').click()"); pm.wait_for_timeout(600)
    top(pm, '#solutions', -20); pm.screenshot(path=f'{OUT}/mobile-10-solutions-suc.png')
    pm.evaluate("document.getElementById('tab-fin').click()"); pm.wait_for_timeout(600)
    top(pm, '#solutions', -20); pm.screenshot(path=f'{OUT}/mobile-13-solutions-fin.png')
    m.close()
    b.close()
print('ok')
