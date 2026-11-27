#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Live /check/ sanity check WITHOUT letting any request reach the Apps Script backend.

Loads the live page, walks the funnel up to the consent screen (never presses the
submit button), and reports console errors, page errors, 4xx/5xx responses,
request failures, horizontal overflow per screen, and every attempted POST to
script.google.com (aborted by request interception, so nothing is written to the
sheet and no result mail is sent).

Usage:
  PLAYWRIGHT_BROWSERS_PATH=/workspace/.cache/ms-playwright \
  LD_LIBRARY_PATH=/workspace/.libs/root/usr/lib/x86_64-linux-gnu \
  python3 bellarich-site/tmp/verify_check_live_blocked.py <url>
"""
import json
import os
import sys

from playwright.sync_api import sync_playwright

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'live-check')


def overflow(pg):
    return pg.evaluate("""() => {
      const de = document.documentElement;
      const wide = [];
      document.querySelectorAll('body *').forEach(el => {
        const r = el.getBoundingClientRect();
        if (r.width > 0 && (r.right > de.clientWidth + 2 || r.left < -2)) {
          const cs = getComputedStyle(el);
          if (cs.position === 'fixed' || cs.visibility === 'hidden' || cs.display === 'none') return;
          wide.push((el.id ? '#' + el.id : el.tagName) + '.' + String(el.className || '').slice(0, 30)
                    + ' right=' + Math.round(r.right));
        }
      });
      return {vw: de.clientWidth, scrollW: de.scrollWidth,
              docOverflow: de.scrollWidth > de.clientWidth + 1, wide: wide.slice(0, 6)};
    }""")


def run(url):
    os.makedirs(OUT, exist_ok=True)
    rep = {'url': url, 'console_errors': [], 'page_errors': [], 'http_errors': [],
           'failed': [], 'blocked_posts': [], 'screens': {}}
    with sync_playwright() as p:
        b = p.chromium.launch()
        for label, vp in (('pc', {'width': 1440, 'height': 900}),
                          ('mobile', {'width': 390, 'height': 844})):
            ctx = b.new_context(viewport=vp, device_scale_factor=1)
            pg = ctx.new_page()
            pg.on('console', lambda m, l=label: rep['console_errors'].append(f'[{l}] {m.type}: {m.text}')
                  if m.type == 'error' else None)
            pg.on('pageerror', lambda e, l=label: rep['page_errors'].append(f'[{l}] {e}'))
            pg.on('requestfailed', lambda r, l=label: rep['failed'].append(
                f'[{l}] {r.method} {r.url[:90]} :: {r.failure}'))
            pg.on('response', lambda r, l=label: rep['http_errors'].append(
                f'[{l}] {r.status} {r.url[:90]}') if r.status >= 400 else None)

            def guard(route, request):
                if 'script.google.com' in request.url:
                    rep['blocked_posts'].append(
                        f'[{label}] {request.method} {request.url[:80]} '
                        f'type={request.headers.get("content-type")} '
                        f'body={len(request.post_data or "")}B')
                    route.abort()
                else:
                    route.continue_()
            pg.route('**/*', guard)

            pg.goto(url, wait_until='networkidle')
            rep['screens'][f'{label}_landing'] = overflow(pg)
            pg.screenshot(path=os.path.join(OUT, f'{label}-landing.png'))

            pg.click('#btn-start-test')
            pg.wait_for_selector('#screen-category.active', timeout=5000)
            pg.wait_for_timeout(250)
            rep['screens'][f'{label}_category'] = overflow(pg)
            pg.screenshot(path=os.path.join(OUT, f'{label}-category.png'))

            pg.click('#category-grid .category-card:first-child')
            pg.wait_for_selector('#screen-question.active', timeout=5000)
            pg.wait_for_timeout(200)

            for i in range(6):
                pg.wait_for_selector('#q-options .option', timeout=5000)
                pick = pg.query_selector('#q-options .option:nth-child(2)') or \
                    pg.query_selector('#q-options .option')
                pick.click()
                pg.wait_for_timeout(100)
                pg.click('#btn-next')
                pg.wait_for_timeout(220)
                if i == 0:
                    rep['screens'][f'{label}_q1'] = overflow(pg)
                    pg.screenshot(path=os.path.join(OUT, f'{label}-q1.png'))

            pg.wait_for_selector('#screen-consent.active', timeout=5000)
            pg.wait_for_timeout(250)
            rep['screens'][f'{label}_consent'] = overflow(pg)
            pg.screenshot(path=os.path.join(OUT, f'{label}-consent.png'))

            # 절대 제출 버튼(#btn-consent)은 누르지 않는다 — 실제 접수·메일 발송 방지.
            ctx.close()
        b.close()
    return rep


if __name__ == '__main__':
    print(json.dumps(run(sys.argv[1]), ensure_ascii=False, indent=2))
