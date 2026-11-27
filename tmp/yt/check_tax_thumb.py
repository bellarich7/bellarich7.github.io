import asyncio, sys, os
from playwright.async_api import async_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8931/plan/tax/?v=1127a'
OUT = sys.argv[2] if len(sys.argv) > 2 else '/workspace/bellarich-site/tmp/yt'
TAG = sys.argv[3] if len(sys.argv) > 3 else 'local'

async def run():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for label, w, h in (('1440', 1440, 900), ('390', 390, 844)):
            ctx = await b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=1)
            page = await ctx.new_page()
            errs = []
            page.on('console', lambda m: errs.append(f'{m.type}: {m.text}') if m.type == 'error' else None)
            page.on('pageerror', lambda e: errs.append(f'pageerror: {e}'))
            await page.goto(BASE, wait_until='load')
            await page.wait_for_timeout(600)
            # 영상 섹션까지
            await page.evaluate("document.querySelector('#video').scrollIntoView({block:'center'})")
            await page.wait_for_timeout(900)

            info = await page.evaluate("""() => {
              const c = document.getElementById('videoCard');
              const t = document.getElementById('videoPlay');
              const cs = getComputedStyle(t);
              const r = t.getBoundingClientRect();
              const pr = t.querySelector('.video-card__play').getBoundingClientRect();
              return {
                cls: t.className,
                bgImage: cs.backgroundImage.slice(0, 90),
                bgSize: cs.backgroundSize, bgPos: cs.backgroundPosition,
                thumb: [Math.round(r.width), Math.round(r.height), +(r.width/r.height).toFixed(3)],
                playBtn: [Math.round(pr.width), Math.round(pr.height)],
                playVisible: getComputedStyle(t.querySelector('.video-card__play')).display !== 'none',
                phLeft: t.querySelectorAll('.video-card__ph').length,
                overflowX: document.documentElement.scrollWidth - window.innerWidth,
                loaded: cs.backgroundImage.includes('yt-tax'),
                thumbTopDoc: Math.round(r.top + window.scrollY),
                cardTop: Math.round(c.getBoundingClientRect().top + window.scrollY)
              };
            }""")
            print(label, 'BEFORE', info)

            # 썸네일 crop 영역 확인용 카드 캡처
            card = page.locator('#videoCard')
            await card.screenshot(path=f'{OUT}/{TAG}-{label}-cover.png')

            # 클릭 → iframe
            await page.click('#videoPlay')
            try:
                await page.wait_for_selector('#videoFrame iframe', timeout=6000)
            except Exception as e:
                print(label, 'IFRAME WAIT FAIL', e)
            await page.wait_for_timeout(1200)
            after = await page.evaluate("""() => {
              const f = document.querySelector('#videoFrame iframe');
              const frame = document.getElementById('videoFrame');
              const fr = frame.getBoundingClientRect();
              return {
                hasIframe: !!f,
                src: f ? f.getAttribute('src') : null,
                frameBox: [Math.round(fr.width), Math.round(fr.height), +(fr.width/fr.height).toFixed(3)],
                frameDisplay: getComputedStyle(frame).display,
                thumbDisplay: getComputedStyle(document.getElementById('videoPlay')).display,
                isPlaying: document.getElementById('videoCard').classList.contains('is-playing'),
                overflowX: document.documentElement.scrollWidth - window.innerWidth
              };
            }""")
            print(label, 'AFTER', after)
            await card.screenshot(path=f'{OUT}/{TAG}-{label}-playing.png')
            print(label, 'console errors:', errs)
            await ctx.close()
        await b.close()

asyncio.run(run())
