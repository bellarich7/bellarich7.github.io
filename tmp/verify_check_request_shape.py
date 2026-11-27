#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verify the exact HTTP request the live /check/ page makes, without touching the backend.

The live HTML is served to the browser with only the endpoint URL swapped for a
throwaway host that is aborted, so whatever the page sends is captured (method,
Content-Type, body) and nothing reaches the Apps Script web app.

- 완료 제출 경로: 동의 → 결과 화면(fetch)
- 이탈 경로: beforeunload 이벤트를 직접 발생시켜 sendBeacon 페이로드 확인

Usage:
  PLAYWRIGHT_BROWSERS_PATH=/workspace/.cache/ms-playwright \
  LD_LIBRARY_PATH=/workspace/.libs/root/usr/lib/x86_64-linux-gnu \
  python3 bellarich-site/tmp/verify_check_request_shape.py <url>
"""
import json
import sys

from playwright.sync_api import sync_playwright

LIVE_HOST = 'script.google.com'
TEST_URL = 'https://bellarich.co.kr/__noop_test_endpoint'
captured = []


def main(url):
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={'width': 1440, 'height': 900})
        pg = ctx.new_page()

        def route(r):
            req = r.request
            if req.resource_type == 'document' and '/check/' in req.url:
                resp = r.fetch()
                body = resp.text()
                n = body.count(LIVE_HOST)
                body = body.replace(
                    'https://script.google.com/macros/s/AKfycbwDYShx9JqX1H86FroITA1yd-b8w-F-OMdFNMuOLF7Os4dSB0M-wPQFmcUTRJUDNkjz/exec',
                    TEST_URL)
                r.fulfill(response=resp, body=body)
                print(f'document served with endpoint swapped ({n} occurrence)')
                return
            if TEST_URL in req.url:
                data = req.post_data or ''
                try:
                    parsed = json.loads(data)
                    keys = sorted(parsed.keys())
                except Exception:
                    parsed, keys = None, []
                captured.append({
                    'method': req.method,
                    'content_type': req.headers.get('content-type'),
                    'origin': req.headers.get('origin'),
                    'body_bytes': len(data.encode()),
                    'json_ok': parsed is not None,
                    'type': parsed.get('type', '(없음)') if parsed else None,
                    'has_email': bool(parsed and parsed.get('email')) if parsed else None,
                    'keys': keys,
                    'head': data[:160],
                })
                r.abort()
                return
            r.continue_()

        pg.route('**/*', route)
        pg.goto(url, wait_until='networkidle')
        pg.click('#btn-start-test')
        pg.wait_for_selector('#screen-category.active')
        pg.click('#category-grid .category-card:first-child')
        pg.wait_for_selector('#screen-question.active')
        for i in range(6):
            pg.wait_for_selector('#q-options .option')
            (pg.query_selector('#q-options .option:nth-child(2)') or pg.query_selector('#q-options .option')).click()
            pg.wait_for_timeout(90)
            pg.click('#btn-next')
            pg.wait_for_timeout(200)
        pg.wait_for_selector('#screen-consent.active')
        pg.fill('#consent-name', '검증용')
        pg.fill('#consent-email', 'verify-shape@example.invalid')
        pg.check('#consent-collection')
        pg.click('#btn-consent')
        pg.wait_for_selector('#screen-result.active', timeout=8000)
        pg.wait_for_timeout(600)
        # 이탈 경로: beforeunload 핸들러가 sendBeacon 으로 보내는지
        pg.evaluate("window.dispatchEvent(new Event('beforeunload'))")
        pg.wait_for_timeout(500)
        ctx.close()
        b.close()

    out = {'captured': captured, 'count': len(captured)}
    print(json.dumps(out, ensure_ascii=False, indent=2))
    print('\n-- type/summary --')
    for c in captured:
        print(c['method'], c['content_type'], c['type'], c['body_bytes'], 'bytes', 'json_ok=', c['json_ok'])
    print('\n-- completed payload keys --')
    if captured:
        print(', '.join(captured[0]['keys']))


if __name__ == '__main__':
    main(sys.argv[1])
