#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""1분 진단 동의 화면 — 휴대폰 번호·카카오톡 전환 검증.

사용:
  python3 test_phone_consent.py <url> <태그>

- 모바일 390 / 데스크톱 1440 에서 카테고리 선택 → 6문항 → 동의 화면까지 진행
- 동의 화면 문구·버튼·입력창(tel) 확인, 가로 넘침 측정
- 빈 번호 / 잘못된 번호 / 정상 번호(동의 미체크) 검증 메시지 확인
- 전송(fetch)이 실제로 나가는지 감시 → 아무 것도 나가면 실패로 기록
- 모바일 동의 화면 스크린샷 저장
"""
import sys
from playwright.sync_api import sync_playwright

URL = sys.argv[1]
TAG = sys.argv[2] if len(sys.argv) > 2 else "local"
SHOT = f"/workspace/downloads/check_consent_phone_390_{TAG}.png"

sent = []


def run(p, width, height, shot=None):
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": width, "height": height}, device_scale_factor=2)
    pg = ctx.new_page()
    errors = []
    pg.on("console", lambda m: errors.append(f"{m.type}: {m.text}") if m.type == "error" else None)
    pg.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))
    pg.on("request", lambda r: sent.append(f"{r.method} {r.url}") if "script.google.com" in r.url else None)

    pg.goto(URL, wait_until="load")
    pg.wait_for_timeout(800)

    # 시작 → 카테고리
    pg.click("#btn-start-test")
    pg.wait_for_timeout(400)
    pg.click(".category-card >> nth=0")
    pg.wait_for_timeout(400)

    # 6문항: 첫 선택지 + 다음
    for i in range(6):
        pg.click("#q-options .option >> nth=0")
        pg.wait_for_timeout(120)
        pg.click("#btn-next")
        pg.wait_for_timeout(350)

    info = pg.evaluate("""() => {
      const v = (sel) => { const e = document.querySelector(sel); return e ? e.textContent.trim() : null; };
      const inp = document.getElementById('consent-phone');
      const btn = document.getElementById('btn-consent');
      const card = document.querySelector('.consent-card');
      return {
        active: document.querySelector('.screen.active') ? document.querySelector('.screen.active').id : null,
        title: v('.consent-title'),
        desc: v('.consent-desc'),
        label: v('.consent-label:nth-of-type(1)'),
        labels: [...document.querySelectorAll('.consent-label')].map(e => e.textContent.trim()),
        meta: v('.consent-meta'),
        foot: v('.consent-foot'),
        btn: btn ? btn.textContent.trim() : null,
        inputType: inp ? inp.type : null,
        inputMode: inp ? inp.getAttribute('inputmode') : null,
        placeholder: inp ? inp.placeholder : null,
        autocomplete: inp ? inp.getAttribute('autocomplete') : null,
        oldEmailInput: !!document.getElementById('consent-email'),
        notice: [...document.querySelectorAll('.data-notice-list li')].map(e => e.textContent.trim()),
        noticeFoot: v('.data-notice-foot'),
        overflowX: document.documentElement.scrollWidth - window.innerWidth
      };
    }""")

    # 검증 메시지 순서: 빈 번호 → 잘못된 번호 → 정상+동의미체크
    pg.fill("#consent-name", "테스트")
    pg.click("#btn-consent")
    pg.wait_for_timeout(200)
    err_empty = pg.text_content("#consent-error")

    pg.fill("#consent-phone", "02-123-4567")
    pg.click("#btn-consent")
    pg.wait_for_timeout(200)
    err_bad = pg.text_content("#consent-error")

    pg.fill("#consent-phone", "01012345678")
    pg.click("#btn-consent")
    pg.wait_for_timeout(200)
    err_coll = pg.text_content("#consent-error")
    still_consent = pg.evaluate("() => document.querySelector('.screen.active').id")

    if shot:
        pg.screenshot(path=shot, full_page=True)

    ctx.close()
    b.close()
    return dict(info=info, err_empty=err_empty, err_bad=err_bad, err_coll=err_coll,
                still=still_consent, errors=errors)


with sync_playwright() as p:
    m = run(p, 390, 844, SHOT)
    d = run(p, 1440, 900, None)

print("=== 모바일 390 ===")
for k, v in m["info"].items():
    print(f"  {k}: {v}")
print(f"  err_empty: {m['err_empty']}")
print(f"  err_bad:   {m['err_bad']}")
print(f"  err_coll:  {m['err_coll']}")
print(f"  active after valid: {m['still']}")
print(f"  console errors: {m['errors']}")
print("=== 데스크톱 1440 ===")
for k, v in d["info"].items():
    print(f"  {k}: {v}")
print(f"  console errors: {d['errors']}")
print(f"전송 시도(script.google.com): {sent if sent else '없음'}")
print(f"screenshot: {SHOT}")
