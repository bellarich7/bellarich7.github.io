#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Structural + typography verification for bellarich-site/index.html."""
import os, json
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
URL = 'file://' + os.path.join(ROOT, 'index.html')
WIDTHS = [(1440, 900), (1280, 800), (1024, 768), (820, 1180), (390, 844)]

PROBES = [
    ('본문 body', 'body'),
    ('섹션 리드 .lead', '.sol__head .lead'),
    ('카드 본문 .card p', '#panel-life .card p'),
    ('카드 제목 .card h3', '#panel-life .card h3'),
    ('경력 목록 .career li', '.career li'),
    ('철학 본문 .philo__text p', '.philo__text p'),
    ('히어로 서브 .hero__sub', '.hero__sub'),
    ('네비 링크 .nav__link', '.nav__link'),
    ('푸터 정보 .footer__info', '.footer__info'),
    ('히어로 자격 .hero__cred-role', '.hero__cred-role'),
]

with sync_playwright() as p:
    b = p.chromium.launch()
    errs = []
    ctx = b.new_context(viewport={'width': 1440, 'height': 900})
    pg = ctx.new_page()
    pg.on('pageerror', lambda e: errs.append('pageerror: ' + str(e)))
    pg.on('console', lambda m: errs.append('console: ' + m.text) if m.type == 'error' else None)
    pg.goto(URL, wait_until='load')
    pg.wait_for_timeout(2000)

    struct = pg.evaluate("""() => {
      const ids = [...document.querySelectorAll('[id]')].map(e => e.id);
      const dup = ids.filter((v, i) => ids.indexOf(v) !== i);
      const empty = [...document.querySelectorAll('a[href]')]
        .map(a => a.getAttribute('href'))
        .filter(h => !h || h === '#' || h === 'javascript:void(0)');
      const noalt = [...document.querySelectorAll('img')].filter(i => !i.hasAttribute('alt')).length;
      const plans = [...document.querySelectorAll('[data-plan]')].map(e => e.dataset.plan);
      return {ids: ids.length, dup: [...new Set(dup)], empty: empty.length,
              noalt, plans: plans.length,
              forms: [...document.querySelectorAll('a[href]')].filter(a => (a.getAttribute('href')||'').includes('docs.google.com')).length};
    }""")
    print('STRUCT', json.dumps(struct, ensure_ascii=False))

    # every plan modal opens with content (3 tabs: activate the tab that owns the card first)
    plans = pg.evaluate("[...document.querySelectorAll('[data-plan]')].map(e=>e.dataset.plan)")
    bad = []
    for pl in plans:
        pg.evaluate("""(pl)=>{
            const el = document.querySelector(`[data-plan="${pl}"]`);
            const panel = el.closest('.panel');
            const tab = panel && document.querySelector(`.tab[aria-controls="${panel.id}"]`);
            if (tab && tab.getAttribute('aria-selected') !== 'true') tab.click();
        }""", pl)
        pg.wait_for_timeout(120)
        pg.click(f'[data-plan="{pl}"]')
        pg.wait_for_timeout(250)
        ok = pg.evaluate("""()=>{const m=document.getElementById('modal');
            const t=document.getElementById('modalTitle');
            return {open:m.classList.contains('is-open'), title:t?t.textContent.trim():'', len:document.getElementById('modalBody').innerText.length};}""")
        if not ok['open'] or ok['len'] < 40 or not ok['title']:
            bad.append((pl, ok))
        pg.keyboard.press('Escape')
        pg.wait_for_timeout(150)
    print('MODALS', len(plans), 'problems', bad)

    # tab structure / aria wiring + arrow-key navigation
    tabinfo = pg.evaluate("""() => {
      const tabs = [...document.querySelectorAll('.tabs .tab')];
      const rows = tabs.map(t => {
        const p = document.getElementById(t.getAttribute('aria-controls'));
        return {id: t.id, label: t.textContent.trim().replace(/\\s+/g,' '), badge: (t.querySelector('b')||{}).textContent,
                panel: p ? p.id : null, hasPanel: !!p,
                panelLabelled: p ? p.getAttribute('aria-labelledby') === t.id : false,
                cards: p ? p.querySelectorAll('.card').length : 0,
                sel: t.getAttribute('aria-selected')};
      });
      const visible = [...document.querySelectorAll('.panel')].filter(p => !p.hidden).map(p => p.id);
      return {tabs: rows.length, rows, visible};
    }""")
    print('TABS', json.dumps(tabinfo, ensure_ascii=False))

    # keyboard: focus first tab, ArrowRight twice -> third tab active, ArrowLeft -> back
    pg.evaluate("document.getElementById('tab-life').focus()")
    pg.keyboard.press('ArrowRight'); pg.wait_for_timeout(120)
    k1 = pg.evaluate("[...document.querySelectorAll('.tabs .tab')].map(t=>t.getAttribute('aria-selected'))")
    pg.keyboard.press('ArrowRight'); pg.wait_for_timeout(120)
    k2 = pg.evaluate("[...document.querySelectorAll('.tabs .tab')].map(t=>t.getAttribute('aria-selected'))")
    pg.keyboard.press('ArrowLeft'); pg.wait_for_timeout(120)
    k3 = pg.evaluate("[...document.querySelectorAll('.tabs .tab')].map(t=>t.getAttribute('aria-selected'))")
    pg.keyboard.press('Home'); pg.wait_for_timeout(120)
    k4 = pg.evaluate("[...document.querySelectorAll('.tabs .tab')].map(t=>t.getAttribute('aria-selected'))")
    print('TABKEYS', json.dumps({'right1': k1, 'right2': k2, 'left': k3, 'home': k4}))

    # anchor navigation: drawer on mobile, header nav on desktop. The target section
    # must land at the top of the viewport (below the fixed header), menu closed,
    # body scroll unlocked, and the hash set.
    anchors = {}
    for w, h, mode in [(1440, 900, 'nav'), (390, 844, 'drawer')]:
        c3 = b.new_context(viewport={'width': w, 'height': h}, is_mobile=w < 500, has_touch=w < 500)
        p3 = c3.new_page()
        p3.on('pageerror', lambda e: errs.append(f'anchor{w}: ' + str(e)))
        p3.goto(URL, wait_until='load')
        p3.wait_for_timeout(1200)
        rows = []
        for href, label in [('#home', '홈'), ('#about', '대표소개'), ('#philosophy', '철학'), ('#contact', '상담신청')]:
            if mode == 'drawer':
                if not p3.evaluate("document.getElementById('mobileMenu').classList.contains('is-open')"):
                    p3.click('.nav__burger')
                    p3.wait_for_timeout(600)
                p3.click(f'.mobile-menu a[href="{href}"]')
            elif href == '#contact':
                p3.click('.nav__cta')
            else:
                p3.click(f'.nav__menu a[href="{href}"]')
            p3.wait_for_timeout(1400)
            st = p3.evaluate("""(href) => {
                const e = document.querySelector(href);
                return {top: e ? Math.round(e.getBoundingClientRect().top) : null,
                        locked: document.body.classList.contains('is-locked'),
                        menu: document.getElementById('mobileMenu').classList.contains('is-open'),
                        hash: location.hash};
            }""", href)
            ok = st['top'] is not None and -2 <= st['top'] <= 120 and not st['locked'] and not st['menu'] and st['hash'] == href
            rows.append({'item': label, 'href': href, 'top': st['top'], 'hash': st['hash'],
                         'locked': st['locked'], 'menuOpen': st['menu'], 'ok': ok})
        anchors[f'{w}x{h}'] = {'rows': rows, 'pass': all(r['ok'] for r in rows)}
        c3.close()
    print('ANCHORS', json.dumps(anchors, ensure_ascii=False))

    typos = pg.evaluate("""(probes) => probes.map(([label, sel]) => {
        const el = document.querySelector(sel);
        if (!el) return [label, sel, null];
        const c = getComputedStyle(el);
        return [label, c.fontSize, c.fontWeight, c.color, c.lineHeight];
    })""", PROBES)
    for row in typos:
        print('TYPO', json.dumps(row, ensure_ascii=False))

    for w, h in WIDTHS:
        c2 = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=1 if w > 500 else 2,
                           is_mobile=w < 500, has_touch=w < 500)
        p2 = c2.new_page()
        p2.on('pageerror', lambda e: errs.append(f'{w}: ' + str(e)))
        p2.goto(URL, wait_until='load')
        p2.wait_for_timeout(1200)
        res = p2.evaluate("""() => {
          const de = document.documentElement;
          const out = [];
          document.querySelectorAll('main *, header *, footer *').forEach(el => {
            const r = el.getBoundingClientRect();
            if (r.width > 0 && (r.right > de.clientWidth + 2 || r.left < -2)) {
              const c = (el.className || '').toString();
              if (!/hero__glow|band__track|br-sprite|modal__/.test(c)) out.push(el.tagName + '.' + c.slice(0, 30));
            }
          });
          return {vw: de.clientWidth, scrollW: de.scrollWidth, over: [...new Set(out)].slice(0, 6)};
        }""")
        print('WIDTH', w, json.dumps(res, ensure_ascii=False))
        c2.close()

    ctx.close()
    b.close()
    print('ERRORS', errs)
