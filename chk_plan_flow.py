#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""동선 점검: 메인 카드 → 상세 페이지, 카드 안 상담 신청 → 폼(새 탭), 카드 본문 → 모달.
   python3 chk_plan_flow.py http://127.0.0.1:8765/
"""
import sys, json
from playwright.sync_api import sync_playwright

BASE = (sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8765/').rstrip('/')
FORM = 'https://docs.google.com/forms/d/1pvpYq1jJblmrxjHUQeo-nbmB_C3n87T8OCYVzhN5aZE/viewform'
res = {}

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width': 1440, 'height': 900})
    ctx.route('https://docs.google.com/**', lambda r: r.fulfill(status=200, body='ok'))

    # 1) 절세 플랜 카드 '자세히' → 상세 페이지
    pg = ctx.new_page()
    pg.goto(BASE + '/', wait_until='load'); pg.wait_for_timeout(400)
    pg.evaluate("()=>document.getElementById('solutions').scrollIntoView()")
    pg.click('.card[data-href] a.card__more')
    pg.wait_for_load_state('load'); pg.wait_for_timeout(300)
    res['more_link_url'] = pg.url
    res['more_link_h1'] = pg.inner_text('h1') if pg.query_selector('h1') else None

    # 2) 상세 페이지 → 뒤로
    pg.go_back(); pg.wait_for_load_state('load'); pg.wait_for_timeout(200)
    res['back_url'] = pg.url

    # 3) 절세 카드 본문 클릭 → 상세 페이지
    pg.goto(BASE + '/', wait_until='load'); pg.wait_for_timeout(300)
    box = pg.eval_on_selector('.card[data-href] p', "el=>{const r=el.getBoundingClientRect();return r.top+window.scrollY;}")
    pg.evaluate("(y)=>window.scrollTo(0, y-200)", box); pg.wait_for_timeout(200)
    pg.click('.card[data-href] p')
    pg.wait_for_load_state('load'); pg.wait_for_timeout(300)
    res['card_body_url'] = pg.url

    # 4) 일반 카드 본문 클릭 → 모달
    pg.goto(BASE + '/', wait_until='load'); pg.wait_for_timeout(300)
    pg.click('[data-plan="inv1"] p')
    pg.wait_for_timeout(400)
    res['modal_on_card_body'] = pg.evaluate("()=>document.getElementById('modal').classList.contains('is-open')")
    res['modal_title'] = pg.evaluate("()=>document.getElementById('modalTitle').textContent")
    pg.keyboard.press('Escape'); pg.wait_for_timeout(200)

    # 5) 일반 카드 '자세히' → 모달
    pg.click('[data-plan="inv1"] .card__act button.card__more')
    pg.wait_for_timeout(400)
    res['modal_on_more'] = pg.evaluate("()=>document.getElementById('modal').classList.contains('is-open')")
    pg.keyboard.press('Escape'); pg.wait_for_timeout(200)

    # 6) 카드 안 '상담 신청' → 새 탭으로 폼, 카드/모달은 열리지 않음
    for sel, name in [('[data-plan="inv1"] a.card__apply', 'apply_on_normal_card'),
                      ('.card[data-href] a.card__apply', 'apply_on_tax_card')]:
        with ctx.expect_page() as newp:
            pg.click(sel)
        tab = newp.value
        tab.wait_for_load_state('domcontentloaded')
        res[name] = {'tab_url': tab.url, 'modal_open': pg.evaluate("()=>document.getElementById('modal').classList.contains('is-open')"),
                     'still_on': pg.url}
        tab.close()
        pg.wait_for_timeout(150)

    # 7) 상세 페이지 상단·하단 상담 신청 → 같은 폼(새 탭)
    pg.goto(BASE + '/plan/tax/', wait_until='load'); pg.wait_for_timeout(300)
    out = []
    for sel in ['.phero__acts a[data-contact-link]', '.pcta__acts a[data-contact-link]']:
        with ctx.expect_page() as newp:
            pg.click(sel)
        tab = newp.value; tab.wait_for_load_state('domcontentloaded')
        out.append(tab.url); tab.close(); pg.wait_for_timeout(120)
    res['detail_ctas'] = out

    # 8) 상세 페이지 '홈으로' / 브레드크럼 / 하단 다른 메뉴
    res['detail_links'] = pg.evaluate("""()=>({
        home: document.querySelector('.pnav__home').getAttribute('href'),
        logo: document.querySelector('.plogo').getAttribute('href'),
        crumb_home: document.querySelector('.pcrumb a').getAttribute('href'),
        crumb_sol: document.querySelectorAll('.pcrumb a')[1].getAttribute('href'),
        other: document.querySelector('.pcta__back').getAttribute('href'),
        form: [...document.querySelectorAll('[data-contact-link]')].map(a=>a.getAttribute('href')),
        tel: [...document.querySelectorAll('a[href^="tel:"]')].map(a=>a.getAttribute('href'))
    })""")
    ctx.close(); b.close()

print(json.dumps(res, ensure_ascii=False, indent=1))
print('FORM match:', all(u.split('?')[0] == FORM for u in (res['detail_ctas'] + [res['apply_on_normal_card']['tab_url'], res['apply_on_tax_card']['tab_url']])))
