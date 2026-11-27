#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""End-to-end check of the diagnostic page (local copy and/or live URL).

Drives the whole funnel in headless Chromium and records console errors,
failed responses, and every request that leaves for a third party.

Usage:
  PLAYWRIGHT_BROWSERS_PATH=/workspace/.cache/ms-playwright \
  LD_LIBRARY_PATH=/workspace/.libs/root/usr/lib/x86_64-linux-gnu \
  python3 verify_check.py <url> [--shots]

With --shots it also saves PC 1440 and mobile 390 screenshots of the result screen.
"""
import json
import os
import sys

from playwright.sync_api import sync_playwright

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shots')
TRACK_HOSTS = ('script.google.com', 'drtardis123', 'DrTardis123')


def run(url, shots):
    os.makedirs(OUT, exist_ok=True)
    report = {'url': url, 'console_errors': [], 'page_errors': [], 'failed': [],
              'third_party': [], 'requests': []}

    with sync_playwright() as p:
        b = p.chromium.launch()
        for label, viewport in (('pc', {'width': 1440, 'height': 900}),
                                ('mobile', {'width': 390, 'height': 844})):
            ctx = b.new_context(viewport=viewport, device_scale_factor=2 if label == 'mobile' else 1)
            pg = ctx.new_page()
            pg.on('console', lambda m, l=label: report['console_errors'].append(
                f'[{l}] {m.text}') if m.type == 'error' else None)
            pg.on('pageerror', lambda e, l=label: report['page_errors'].append(f'[{l}] {e}'))
            pg.on('requestfailed', lambda r, l=label: report['failed'].append(
                f'[{l}] {r.method} {r.url} :: {r.failure}'))
            pg.on('request', lambda r, l=label: report['third_party'].append(
                f'[{l}] {r.method} {r.url}')
                if any(h.lower() in r.url.lower() for h in TRACK_HOSTS) else None)

            pg.goto(url, wait_until='networkidle')
            pg.screenshot(path=os.path.join(OUT, f'check-{label}-intro.png'), full_page=False)

            # intro -> category
            pg.click('#btn-start-test')
            pg.wait_for_selector('#screen-category.active', timeout=5000)
            pg.wait_for_timeout(300)
            pg.screenshot(path=os.path.join(OUT, f'check-{label}-category.png'))

            # first category card
            pg.click('#category-grid .category-card:first-child')
            pg.wait_for_selector('#screen-question.active', timeout=5000)

            # answer 6 questions, first option each
            for i in range(6):
                pg.wait_for_selector('#q-options .option', timeout=5000)
                if i == 0:
                    pg.screenshot(path=os.path.join(OUT, f'check-{label}-q1.png'))
                pg.click('#q-options .option:first-child')
                pg.wait_for_timeout(120)
                pg.click('#btn-next')
                pg.wait_for_timeout(250)

            # consent
            pg.wait_for_selector('#screen-consent.active', timeout=5000)
            pg.fill('#consent-name', '검증')
            pg.fill('#consent-email', 'verify@example.com')
            pg.check('#consent-collection')
            pg.screenshot(path=os.path.join(OUT, f'check-{label}-consent.png'))
            pg.click('#btn-consent')
            pg.wait_for_selector('#screen-result.active', timeout=5000)
            pg.wait_for_timeout(700)
            pg.screenshot(path=os.path.join(OUT, f'check-{label}-result.png'))

            info = pg.evaluate("""() => {
              const de = document.documentElement;
              const over = [];
              document.querySelectorAll('#screen-result.active *').forEach(el => {
                const r = el.getBoundingClientRect();
                if (r.width > 0 && (r.right > de.clientWidth + 2 || r.left < -2))
                  over.push(el.tagName + '.' + (el.className||'').toString().slice(0,40));
              });
              return {
                grade: (document.getElementById('grade-circle')||{}).textContent,
                score: (document.querySelector('.result-score, #result-score')||{}).textContent || null,
                vw: de.clientWidth, scrollW: de.scrollWidth,
                overflow: over.slice(0, 8)
              };
            }""")
            report[f'result_{label}'] = info

            # leave the page: beforeunload can fire -> exit beacon must not go anywhere
            pg.goto('about:blank')
            pg.wait_for_timeout(400)
            ctx.close()
        b.close()
    return report


if __name__ == '__main__':
    url = sys.argv[1]
    rep = run(url, '--shots' in sys.argv)
    print(json.dumps(rep, ensure_ascii=False, indent=2))
