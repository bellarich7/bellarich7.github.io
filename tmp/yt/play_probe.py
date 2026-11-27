import asyncio
from playwright.async_api import async_playwright

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
      'Chrome/131.0.0.0 Safari/537.36')

async def run():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--disable-blink-features=AutomationControlled'])
        ctx = await b.new_context(viewport={'width': 1440, 'height': 900}, user_agent=UA,
                                  locale='ko-KR', timezone_id='Asia/Seoul')
        page = await ctx.new_page()
        await page.goto('https://bellarich.co.kr/plan/tax/?v=1127a', wait_until='load')
        await page.evaluate("document.querySelector('#video').scrollIntoView({block:'start'})")
        await page.click('#videoPlay')
        await page.wait_for_selector('#videoFrame iframe', timeout=8000)
        await page.wait_for_timeout(9000)
        txt = await page.evaluate("""() => {
          const f = document.querySelector('#videoFrame iframe');
          return {src: f.getAttribute('src'), w: f.clientWidth, h: f.clientHeight};
        }""")
        print(txt)
        await page.screenshot(path='/workspace/downloads/절세플랜_영상표지_1440_재생확인.png')
        await ctx.close()
        await b.close()

asyncio.run(run())
