#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""라이브(bellarich.co.kr/check/?v=1126phone) 검증.

- 390 / 1440 에서 카테고리 → 6문항 → 동의 화면까지 진행, 문구·레이아웃 확인 후 스크린샷
- 결과 화면 확인은 전송을 브라우저 안에서 막고(window.fetch·sendBeacon 무력화 +
  script.google.com 요청 abort) 진행한다. 실제 전송은 0건이어야 한다.
"""
import sys
from playwright.sync_api import sync_playwright

URL = "https://bellarich.co.kr/check/?v=1126phone"
sent, blocked = [], []


def to_consent(pg):
    pg.click("#btn-start-test")
    pg.wait_for_timeout(400)
    pg.click(".category-card >> nth=0")
    pg.wait_for_timeout(400)
    for _ in range(6):
        pg.click("#q-options .option >> nth=0")
        pg.wait_for_timeout(100)
        pg.click("#btn-next")
        pg.wait_for_timeout(300)


with sync_playwright() as p:
    b = p.chromium.launch()

    for w, h, shot in [(390, 844, "/workspace/downloads/check_consent_phone_390.png"),
                       (1440, 900, "/workspace/downloads/check_consent_phone_1440.png")]:
        ctx = b.new_context(viewport={"width": w, "height": h}, device_scale_factor=2)
        pg = ctx.new_page()
        errs = []
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("request", lambda r: sent.append(r.url) if "script.google.com" in r.url else None)
        pg.goto(URL, wait_until="load")
        pg.wait_for_timeout(700)
        to_consent(pg)
        info = pg.evaluate("""() => ({
          active: document.querySelector('.screen.active').id,
          title: document.querySelector('.consent-title').textContent.trim(),
          btn: document.getElementById('btn-consent').textContent.trim(),
          label2: document.querySelectorAll('.consent-label')[1].textContent.trim(),
          inputType: document.getElementById('consent-phone').type,
          overflowX: document.documentElement.scrollWidth - window.innerWidth,
          cardW: Math.round(document.querySelector('.consent-card').getBoundingClientRect().width)
        })""")
        pg.screenshot(path=shot, full_page=True)
        print(f"[{w}px] {info}  console:{errs}  shot:{shot}")
        ctx.close()

    # 결과 화면 — 전송 차단
    ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2)
    pg = ctx.new_page()
    ctx.route("**://script.google.com/**", lambda route: (blocked.append(route.request.url), route.abort()))
    pg.add_init_script("window.fetch = () => Promise.resolve({}); window.navigator.sendBeacon = () => true;")
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto(URL, wait_until="load")
    pg.wait_for_timeout(600)
    to_consent(pg)
    pg.fill("#consent-name", "확인용")
    pg.fill("#consent-phone", "01012345678")
    pg.check("#consent-collection")
    pg.click("#btn-consent")
    pg.wait_for_timeout(700)
    res = pg.evaluate("""() => ({
      active: document.querySelector('.screen.active').id,
      line: document.querySelector('.result-mail-text strong').textContent.trim(),
      muted: document.getElementById('result-email-display').textContent.trim()
    })""")
    pg.screenshot(path="/workspace/downloads/check_result_phone_390.png", full_page=False)
    print(f"[결과화면] {res}  console:{errs}")
    ctx.close()
    b.close()

print(f"script.google.com 요청(실제 전송): {sent if sent else '없음'}")
print(f"차단된 요청: {len(blocked)}")
