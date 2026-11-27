import asyncio, sys
from playwright.async_api import async_playwright

URL = 'https://bellarich.co.kr/plan/tax/?v=1127a'
D = '/workspace/downloads'

async def run():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for label, w, h in (('1440', 1440, 900), ('390', 390, 844)):
            ctx = await b.new_context(viewport={'width': w, 'height': h})
            page = await ctx.new_page()
            errs = []
            page.on('console', lambda m: errs.append(f'{m.type}: {m.text}') if m.type == 'error' else None)
            page.on('pageerror', lambda e: errs.append(f'pageerror: {e}'))
            await page.goto(URL, wait_until='load')
            await page.evaluate("document.querySelector('#video').scrollIntoView({block:'start'})")
            await page.wait_for_timeout(1000)
            await page.screenshot(path=f'{D}/절세플랜_영상표지_{label}.png')
            await page.click('#videoPlay')
            await page.wait_for_selector('#videoFrame iframe', timeout=8000)
            await page.wait_for_timeout(2500)
            await page.screenshot(path=f'{D}/절세플랜_영상표지_{label}_재생후.png')
            print(label, 'errors:', errs)
            await ctx.close()
        await b.close()

asyncio.run(run())
