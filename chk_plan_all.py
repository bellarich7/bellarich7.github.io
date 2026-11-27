#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""모든 /plan/<slug>/ 상세 페이지를 실제 브라우저로 검사합니다.

확인: 콘솔/페이지 에러 0 · 390px 가로 넘침 0 · 상단·하단 색 = 플랜 갈래 색 ·
      상담 신청 버튼 두 곳 · 영상 카드(클릭 전 유튜브 요청 0 → 클릭 후 nocookie iframe).
"""
import os, sys, glob
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

ROOT = '/workspace/bellarich-deploy'
PLAN = os.path.join(ROOT, 'plan')

EXPECT = {  # 갈래별 상단 색 (rgba)
    'life': 'rgb(11, 25, 51)',
    'suc':  'rgb(92, 59, 22)',
    'fin':  'rgb(47, 66, 56)',
}
GROUP = {
    'office': 'life', 'family-corp': 'life', 'retirement': 'life', 'home-for-kids': 'life',
    'tax': 'life', 'asset': 'life',
    'in-kind': 'suc',
    'startup-succession': 'suc', 'family-business': 'suc', 'trust': 'suc',
    'credit': 'fin', 'governance': 'fin', 'incorporation': 'fin', 'welfare-fund': 'fin', 'ma': 'fin',
}
YT_HOSTS = ('youtube.com', 'youtu.be', 'ytimg.com', 'googlevideo.com')

slugs = sorted(d for d in os.listdir(PLAN) if os.path.isdir(os.path.join(PLAN, d)))
fails = []

with sync_playwright() as p:
    b = p.chromium.launch()
    for slug in slugs:
        path = os.path.join(PLAN, slug, 'index.html')
        url = 'file://' + path
        for w, h in ((1440, 900), (390, 844)):
            ctx = b.new_context(viewport={'width': w, 'height': h})
            pg = ctx.new_page()
            errs, ytreq = [], []
            pg.on('pageerror', lambda e: errs.append('pageerror: ' + str(e)[:200]))
            pg.on('console', lambda m: errs.append('console: ' + m.text[:200]) if m.type == 'error' else None)
            pg.on('request', lambda r: ytreq.append(r.url) if any(hh in urlparse(r.url).netloc for hh in YT_HOSTS) else None)
            pg.goto(url, wait_until='load')
            pg.wait_for_timeout(400)
            sw = pg.evaluate('document.documentElement.scrollWidth')
            iw = pg.evaluate('window.innerWidth')
            hero = pg.evaluate("getComputedStyle(document.querySelector('.phero')).backgroundColor")
            cta = pg.evaluate("getComputedStyle(document.querySelector('.pcta')).backgroundColor")
            cta_n = pg.evaluate("document.querySelectorAll('.phero__acts [data-contact-link], .pcta__acts [data-contact-link]').length")
            form = pg.evaluate("Array.from(document.querySelectorAll('[data-contact-link]')).every(a=>a.getAttribute('href').indexOf('docs.google.com/forms')>-1)")
            tel = pg.evaluate("document.querySelectorAll('a[href^=\"tel:010-4825-5383\"]').length")
            tag = '[%s %dx%d]' % (slug, w, h)
            if sw > iw + 1:
                fails.append('%s 가로 넘침 scrollWidth=%d innerWidth=%d' % (tag, sw, iw))
            if errs:
                # 폰트 CDN 등 외부 자원 차단은 로컬 file:// 검사에서만 생기므로 따로 표시
                real = [e for e in errs if 'net::ERR' not in e and 'Failed to load resource' not in e]
                if real:
                    fails.append('%s 콘솔/에러 %s' % (tag, real[:3]))
                elif not os.environ.get('KEEP_NET'):
                    print('  (외부 자원 경고 %d건 — file:// 로컬 한정)' % len(errs))
            if hero != EXPECT[GROUP[slug]]:
                fails.append('%s 상단 색 %s (기대 %s)' % (tag, hero, EXPECT[GROUP[slug]]))
            if cta != EXPECT[GROUP[slug]]:
                fails.append('%s 하단 색 %s (기대 %s)' % (tag, cta, EXPECT[GROUP[slug]]))
            if cta_n != 2:
                fails.append('%s 상담 신청 버튼 %d개 (기대 2)' % (tag, cta_n))
            if not form:
                fails.append('%s 상담 폼 링크 아님' % tag)
            if tel < 2:
                fails.append('%s 전화 링크 %d개 (기대 2)' % (tag, tel))
            if slug == 'tax':
                if ytreq:
                    fails.append('%s 클릭 전 유튜브 요청 %d건: %s' % (tag, len(ytreq), ytreq[:2]))
                pg.click('#videoPlay')
                pg.wait_for_timeout(1200)
                info = pg.evaluate("""() => {
                    const f = document.querySelector('#videoFrame iframe');
                    const card = document.getElementById('videoCard');
                    const box = document.querySelector('#videoFrame').getBoundingClientRect();
                    return f ? {src:f.src, cls:card.className, w:Math.round(box.width), h:Math.round(box.height)} : null;
                }""")
                if not info:
                    fails.append('%s 영상 클릭 후 iframe 없음' % tag)
                else:
                    if 'youtube-nocookie.com/embed/D5EWmyd_X8Y' not in info['src']:
                        fails.append('%s iframe 주소 %s' % (tag, info['src']))
                    if 'is-playing' not in info['cls']:
                        fails.append('%s is-playing 클래스 없음' % tag)
                    if abs(info['w'] / max(info['h'], 1) - 16 / 9) > 0.05:
                        fails.append('%s 영상 비율 %dx%d' % (tag, info['w'], info['h']))
                pg.wait_for_timeout(300)
            print('%-34s %4d  넘침 %d  색 %s  버튼 %d' % (slug, w, max(0, sw - iw), hero, cta_n))
            ctx.close()
    b.close()

print('\n지적 %d건' % len(fails))
for f in fails:
    print(' -', f)
sys.exit(1 if fails else 0)
