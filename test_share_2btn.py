#!/usr/bin/env python3
"""1분 진단(/check/) 결과 화면의 공유 영역을 '공유하기 + 링크 복사' 2버튼으로 바꾼 것 검증.

- 로컬 bellarich-site 를 http 로 띄워 /check/ 를 연다.
- script.google.com 요청은 모두 가로채 중단한다(실제 시트 기록 방지) + 가로챈 건수 출력.
- 390px / 1440px 에서 결과 화면까지 진행해 공유 카드 캡처.
- 버튼 2개·문구·토스트·클립보드·navigator.share 분기 확인.
"""
import json
import pathlib
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path('/workspace/bellarich-site')
OUT = pathlib.Path('/workspace/bellarich-site/shots/share2')
OUT.mkdir(parents=True, exist_ok=True)
PORT = 8791
BASE = f'http://127.0.0.1:{PORT}/check/'


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(ROOT), **kw)

    def log_message(self, *a):
        pass


srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

results = {}
blocked = []


def finish_quiz(page):
    """인트로 → 카테고리 → 6문항 → 동의 → 결과 화면 (실제 클릭)."""
    page.click('#btn-start-test')
    page.wait_for_selector('#screen-category.active')
    page.click('.category-card >> nth=0')
    page.wait_for_selector('#screen-question.active')
    for i in range(6):
        page.click('#q-options .option >> nth=0')
        page.click('#btn-next')
        page.wait_for_timeout(120)
    page.wait_for_selector('#screen-consent.active')
    page.fill('#consent-name', '검증')
    page.fill('#consent-phone', '01000000000')
    page.check('#consent-collection')
    page.click('#btn-consent')
    page.wait_for_selector('#screen-result.active')
    page.wait_for_timeout(700)


def open_result(browser, w, h, mobile=False):
    ctx = browser.new_context(
        viewport={'width': w, 'height': h},
        device_scale_factor=2 if mobile else 1,
        is_mobile=mobile,
        has_touch=mobile,
    )
    ctx.grant_permissions(['clipboard-read', 'clipboard-write'], origin=f'http://127.0.0.1:{PORT}')

    def route(r):
        blocked.append(r.request.url)
        r.abort()

    ctx.route('**/script.google.com/**', route)
    page = ctx.new_page()
    errs = []
    page.on('pageerror', lambda e: errs.append(str(e)))
    page.goto(BASE + '?v=1126share2', wait_until='load')
    finish_quiz(page)
    return ctx, page, errs


with sync_playwright() as p:
    browser = p.chromium.launch()

    # ---------- 1) 모바일 390 ----------
    ctx, page, errs = open_result(browser, 390, 844, mobile=True)
    btns = page.query_selector_all('.share-buttons .share-btn')
    results['labels_390'] = [b.inner_text().strip().replace('\n', ' ') for b in btns]
    results['count_390'] = len(btns)
    results['cols_390'] = page.evaluate(
        "getComputedStyle(document.querySelector('.share-buttons')).gridTemplateColumns")
    box = page.evaluate("""() => {
      const c = document.querySelector('.share-card').getBoundingClientRect();
      const bs = [...document.querySelectorAll('.share-btn')].map(b => {
        const r = b.getBoundingClientRect();
        return {w: Math.round(r.width), h: Math.round(r.height), left: Math.round(r.left), right: Math.round(r.right)};
      });
      return {card: {w: Math.round(c.width), left: Math.round(c.left), right: Math.round(c.right)}, btns: bs};
    }""")
    results['box_390'] = box
    results['overflow_390'] = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
    page.locator('.share-card').scroll_into_view_if_needed()
    page.wait_for_timeout(300)
    page.locator('.share-card').screenshot(path=str(OUT / 'card_390_local.png'))
    # 링크 복사 클릭 → 토스트 + 클립보드
    page.click('.share-copy')
    page.wait_for_timeout(350)
    results['toast_copy_mobile'] = page.inner_text('#share-toast')
    results['clip_mobile'] = page.evaluate('navigator.clipboard.readText()')
    page.wait_for_timeout(2500)
    # 공유하기: 모바일 컨텍스트에서 navigator.share 지원 여부
    results['has_share_mobile'] = page.evaluate("typeof navigator.share")
    page.evaluate("""() => {
      window.__shareCalls = [];
      navigator.share = (d) => { window.__shareCalls.push(d); return Promise.resolve(); };
    }""")
    page.click('.share-native')
    page.wait_for_timeout(300)
    results['share_calls_mobile'] = page.evaluate('window.__shareCalls')
    results['errs_390'] = errs
    ctx.close()

    # ---------- 2) 데스크톱 1440 (navigator.share 미지원 → 링크 복사 폴백) ----------
    ctx, page, errs = open_result(browser, 1440, 900)
    results['has_share_desktop'] = page.evaluate("typeof navigator.share")
    results['cols_1440'] = page.evaluate(
        "getComputedStyle(document.querySelector('.share-buttons')).gridTemplateColumns")
    page.locator('.share-card').scroll_into_view_if_needed()
    page.wait_for_timeout(300)
    page.locator('.share-card').screenshot(path=str(OUT / 'card_1440_local.png'))
    page.evaluate("delete navigator.share;")  # 확실히 미지원 상태로
    results['has_share_desktop_after_delete'] = page.evaluate("typeof navigator.share")
    page.click('.share-native')
    page.wait_for_timeout(400)
    results['toast_native_fallback'] = page.inner_text('#share-toast')
    results['clip_desktop'] = page.evaluate('navigator.clipboard.readText()')
    page.wait_for_timeout(2500)
    # share()가 AbortError 로 거절되면 조용히 넘어가야 한다(복사 안 함)
    page.evaluate("""() => {
      window.__abort = 0;
      navigator.share = () => Promise.reject(Object.assign(new Error('abort'), {name: 'AbortError'}));
    }""")
    page.evaluate("document.getElementById('share-toast').className = 'share-toast';")
    page.click('.share-native')
    page.wait_for_timeout(400)
    results['toast_after_abort'] = page.inner_text('#share-toast')
    results['toast_visible_after_abort'] = page.evaluate(
        "document.getElementById('share-toast').classList.contains('show')")
    # share() 가 일반 에러로 실패하면 링크 복사로 이어져야 한다
    page.evaluate("() => { navigator.share = () => Promise.reject(new Error('boom')); }")
    page.wait_for_timeout(2600)
    page.evaluate("document.getElementById('share-toast').className = 'share-toast';")
    page.click('.share-native')
    page.wait_for_timeout(400)
    results['toast_after_error'] = page.inner_text('#share-toast')
    # 콘솔 에러 수집
    results['errs_1440'] = errs
    ctx.close()

    browser.close()

srv.shutdown()

results['blocked_count'] = len(blocked)
results['blocked_sample'] = blocked[:3]
print(json.dumps(results, ensure_ascii=False, indent=2))
