#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Screenshot + layout check for bellarich-site/index.html.

Runs headless Chromium from the workspace-local build:
    PLAYWRIGHT_BROWSERS_PATH=/workspace/.cache/ms-playwright \
    LD_LIBRARY_PATH=/workspace/.libs/root/usr/lib/x86_64-linux-gnu python3 shot.py
"""
import os, json
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
URL = 'file://' + os.path.join(ROOT, 'index.html')
OUT = os.path.join(ROOT, 'shots')
os.makedirs(OUT, exist_ok=True)


def top(page, sel, extra=0):
    page.evaluate("""(arg) => {
        const el = document.querySelector(arg.sel);
        if(!el) return;
        window.scrollTo(0, el.getBoundingClientRect().top + window.scrollY - 62 + arg.extra);
    }""", {'sel': sel, 'extra': extra})
    page.wait_for_timeout(650)


def report(page, label):
    d = page.evaluate("""() => {
      const de = document.documentElement, over = [];
      document.querySelectorAll('body *').forEach(el => {
        const r = el.getBoundingClientRect();
        if (r.width > 0 && (r.right > de.clientWidth + 2 || r.left < -2)) {
          const c = (el.className || '').toString();
          if (!/band__track|modal__|br-sprite/.test(c)) over.push(el.tagName + '.' + c.slice(0, 40));
        }
      });
      const links = [...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href'));
      return {
        vw: de.clientWidth, scrollW: de.scrollWidth, h: de.scrollHeight,
        over: over.slice(0, 8),
        kakao: links.filter(h => h.includes('kakao')).length,
        forms: links.filter(h => h.includes('google.com/forms')).length,
        health: links.filter(h => h.includes('BellaRich')).length,
        sections: [...document.querySelectorAll('main section')].map(s => s.id || s.className),
        cards: [...document.querySelectorAll('.panel:not([hidden]) .card')].length,
        nav: [...document.querySelectorAll('.nav__menu .nav__link, .nav__cta')]
              .map(a => a.textContent.trim().replace(/\\s+/g,' ').slice(0, 16))
      };
    }""")
    print(label, json.dumps(d, ensure_ascii=False))
    return d


with sync_playwright() as p:
    b = p.chromium.launch()
    errs = []
    d = b.new_context(viewport={'width': 1440, 'height': 900})
    pg = d.new_page()
    pg.on('pageerror', lambda e: errs.append('pageerror: ' + str(e)))
    pg.on('console', lambda m: errs.append('console: ' + m.text) if m.type == 'error' else None)
    pg.goto(URL, wait_until='load')
    pg.wait_for_timeout(2500)
    print('FONTS', pg.evaluate("document.fonts.status"))
    report(pg, 'DESKTOP')

    pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(600)
    pg.screenshot(path=f'{OUT}/desktop-01-hero.png')
    top(pg, '#about');        pg.screenshot(path=f'{OUT}/desktop-02-about.png')
    top(pg, '.career');       pg.screenshot(path=f'{OUT}/desktop-03-career.png')
    top(pg, '.books');        pg.screenshot(path=f'{OUT}/desktop-04-books.png')
    top(pg, '#philosophy');   pg.screenshot(path=f'{OUT}/desktop-06-philosophy.png')
    top(pg, '#solutions');    pg.screenshot(path=f'{OUT}/desktop-07-solutions-life.png')
    pg.query_selector('.tabs').screenshot(path=f'{OUT}/desktop-06-tabs-crop.png')
    top(pg, '#panel-life', 300); pg.screenshot(path=f'{OUT}/desktop-08-life-cards.png')
    # tab 2 — 가업승계 플랜 (카드 03 + CTA 04). 부동산승계 블록은 2026-11-25 주석 보관
    pg.evaluate("document.getElementById('tab-suc').click()"); pg.wait_for_timeout(500)
    top(pg, '#solutions', 330); pg.screenshot(path=f'{OUT}/desktop-09-solutions-suc.png')
    pg.evaluate("""() => { const el = document.querySelector('#panel-suc .card--cta');
        window.scrollTo(0, el.getBoundingClientRect().top + window.scrollY - 420); }""")
    pg.wait_for_timeout(600)
    pg.screenshot(path=f'{OUT}/desktop-10-suc-cta.png')
    # tab 3 — 법인 재무·경영지원 플랜
    pg.evaluate("document.getElementById('tab-fin').click()"); pg.wait_for_timeout(500)
    top(pg, '#solutions', 330); pg.screenshot(path=f'{OUT}/desktop-12-solutions-fin.png')
    pg.evaluate("document.getElementById('tab-life').click()"); pg.wait_for_timeout(400)
    top(pg, '#contact');      pg.screenshot(path=f'{OUT}/desktop-13-contact.png')
    pg.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)"); pg.wait_for_timeout(700)
    pg.screenshot(path=f'{OUT}/desktop-14-footer.png')

    # sticky nav over ivory
    top(pg, '#philosophy'); pg.wait_for_timeout(500)
    pg.screenshot(path=f'{OUT}/desktop-15-nav-stuck.png')

    # modal
    top(pg, '#solutions', 330)
    pg.evaluate("document.getElementById('tab-suc').click()"); pg.wait_for_timeout(300)
    pg.click('[data-plan="suc3"]'); pg.wait_for_timeout(900)
    pg.screenshot(path=f'{OUT}/desktop-17-modal-suc3.png')
    print('MODAL_CTA', json.dumps(pg.evaluate("""() => {
        const a = document.querySelector('#modalBody .m-cta a');
        return a ? {href: a.getAttribute('href'), text: a.textContent.trim()} : null;
    }"""), ensure_ascii=False))
    pg.keyboard.press('Escape'); pg.wait_for_timeout(400)

    # full page
    pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(500)
    pg.evaluate("document.querySelectorAll('.rv').forEach(e=>e.classList.add('in'))")
    pg.wait_for_timeout(800)
    pg.screenshot(path=f'{OUT}/desktop-00-fullpage.png', full_page=True)
    d.close()

    # tablet
    t = b.new_context(viewport={'width': 820, 'height': 1180})
    pt = t.new_page(); pt.on('pageerror', lambda e: errs.append('tablet: ' + str(e)))
    pt.goto(URL, wait_until='load'); pt.wait_for_timeout(1800)
    report(pt, 'TABLET')
    pt.screenshot(path=f'{OUT}/tablet-01-hero.png')
    top(pt, '#about'); pt.screenshot(path=f'{OUT}/tablet-02-about.png')
    top(pt, '#solutions', 330); pt.screenshot(path=f'{OUT}/tablet-03-solutions.png')
    t.close()

    # mobile
    m = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2,
                      is_mobile=True, has_touch=True)
    pm = m.new_page(); pm.on('pageerror', lambda e: errs.append('mobile: ' + str(e)))
    pm.goto(URL, wait_until='load'); pm.wait_for_timeout(2200)
    report(pm, 'MOBILE')
    pm.evaluate("window.scrollTo(0,0)"); pm.wait_for_timeout(500)
    pm.screenshot(path=f'{OUT}/mobile-01-hero.png')
    pm.evaluate("window.scrollTo(0,520)"); pm.wait_for_timeout(500)
    pm.screenshot(path=f'{OUT}/mobile-02-hero-portrait.png')
    top(pm, '#about');      pm.screenshot(path=f'{OUT}/mobile-03-about.png')
    top(pm, '.career');     pm.screenshot(path=f'{OUT}/mobile-04-career.png')
    top(pm, '.books');      pm.screenshot(path=f'{OUT}/mobile-05-books.png')
    top(pm, '#philosophy'); pm.screenshot(path=f'{OUT}/mobile-07-philosophy.png')
    top(pm, '#solutions');  pm.screenshot(path=f'{OUT}/mobile-08-solutions.png')
    top(pm, '#panel-life', 240); pm.screenshot(path=f'{OUT}/mobile-09-cards.png')
    pm.evaluate("document.getElementById('tab-suc').click()"); pm.wait_for_timeout(500)
    top(pm, '#solutions', 240); pm.screenshot(path=f'{OUT}/mobile-10-solutions-suc.png')
    pm.evaluate("""() => { const el = document.querySelector('#panel-suc .card--cta');
        window.scrollTo(0, el.getBoundingClientRect().top + window.scrollY - 300); }""")
    pm.wait_for_timeout(600)
    pm.screenshot(path=f'{OUT}/mobile-11-suc-cta.png')
    pm.evaluate("document.getElementById('tab-fin').click()"); pm.wait_for_timeout(500)
    top(pm, '#solutions', 240); pm.screenshot(path=f'{OUT}/mobile-13-solutions-fin.png')
    top(pm, '#contact');    pm.screenshot(path=f'{OUT}/mobile-14-contact.png')
    pm.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)"); pm.wait_for_timeout(600)
    pm.screenshot(path=f'{OUT}/mobile-15-footer.png')
    pm.evaluate("window.scrollTo(0,0)"); pm.wait_for_timeout(500)
    pm.click('.nav__burger'); pm.wait_for_timeout(700)
    pm.screenshot(path=f'{OUT}/mobile-16-menu.png')
    pm.click('#mobileMenu [data-tab="fin"]'); pm.wait_for_timeout(1100)
    pm.screenshot(path=f'{OUT}/mobile-17-tab-fin.png')
    pm.click('[data-plan="fin2"]'); pm.wait_for_timeout(900)
    pm.screenshot(path=f'{OUT}/mobile-18-modal.png')
    m.close()
    b.close()
    print('ERRORS', errs)
