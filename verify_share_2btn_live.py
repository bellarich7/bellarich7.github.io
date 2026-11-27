#!/usr/bin/env python3
"""라이브(https://bellarich.co.kr/check/)에서 공유 2버튼 확인.

- script.google.com 요청은 playwright route 로 모두 중단 → 실제 시트 기록 없음.
- 390px 모바일 컨텍스트에서 결과 화면까지 진행 후 추천 카드 캡처.
"""
import json
from playwright.sync_api import sync_playwright

URL = 'https://bellarich.co.kr/check/?v=1126share2'
OUT_CARD = '/workspace/downloads/check_share_2btn_390.png'
OUT_FULL = '/workspace/downloads/check_result_390_full.png'
blocked = []
res = {}

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width': 390, 'height': 844},
                        device_scale_factor=3, is_mobile=True, has_touch=True,
                        user_agent=('Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 '
                                    '(KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36'))
    ctx.route('**/script.google.com/**', lambda r: (blocked.append(r.request.url), r.abort()))
    ctx.grant_permissions(['clipboard-read', 'clipboard-write'], origin='https://bellarich.co.kr')

    page = ctx.new_page()
    errs = []
    page.on('pageerror', lambda e: errs.append(str(e)))
    page.on('console', lambda m: errs.append('console:' + m.text) if m.type == 'error' else None)
    page.goto(URL, wait_until='load')
    page.wait_for_timeout(400)

    res['title'] = page.title()
    res['styles'] = page.evaluate(
        "getComputedStyle(document.querySelector('.share-buttons')).gridTemplateColumns")

    page.click('#btn-start-test')
    page.wait_for_selector('#screen-category.active')
    page.click('.category-card >> nth=0')
    page.wait_for_selector('#screen-question.active')
    for i in range(6):
        page.click('#q-options .option >> nth=0')
        page.click('#btn-next')
        page.wait_for_timeout(120)
    page.wait_for_selector('#screen-consent.active')
    page.fill('#consent-name', '레이아웃확인')
    page.fill('#consent-phone', '01000000000')
    page.check('#consent-collection')
    page.click('#btn-consent')
    page.wait_for_selector('#screen-result.active')
    page.wait_for_timeout(900)

    res['on_result'] = page.is_visible('#screen-result .share-card')
    res['labels'] = [t.strip() for t in page.eval_on_selector_all(
        '.share-buttons .share-btn', 'els => els.map(e => e.innerText)')]
    res['overflow'] = page.evaluate('document.documentElement.scrollWidth - window.innerWidth')
    res['box'] = page.evaluate("""() => {
      const c = document.querySelector('.share-card').getBoundingClientRect();
      return {w: Math.round(c.width), left: Math.round(c.left), right: Math.round(c.right)};
    }""")

    page.locator('.share-card').scroll_into_view_if_needed()
    page.wait_for_timeout(400)
    page.locator('.share-card').screenshot(path=OUT_CARD)
    # 카드가 페이지 안에서 어떻게 보이는지 (위아래 맥락 포함)
    page.screenshot(path=OUT_FULL, full_page=True)

    # 라이브 링크 복사 확인
    page.click('.share-copy')
    page.wait_for_timeout(400)
    res['toast'] = page.inner_text('#share-toast')
    res['clip'] = page.evaluate('navigator.clipboard.readText()') if page.evaluate(
        'typeof navigator.clipboard') != 'undefined' else 'no-clipboard-api'

    res['errs'] = errs[:6]
    ctx.close()
    b.close()

res['blocked_count'] = len(blocked)
print(json.dumps(res, ensure_ascii=False, indent=2))
