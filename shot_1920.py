from playwright.sync_api import sync_playwright
CHROME='/workspace/.cache/ms-playwright/chromium-1255/chrome-linux64/chrome'
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=CHROME,args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1920,'height':1080})
    pg=ctx.new_page(); pg.goto('https://bellarich.co.kr/?v=1125y',wait_until='networkidle'); pg.wait_for_timeout(900)
    pg.screenshot(path='/workspace/bellarich-site/shots/new-portrait/live-1920-hero.png')
    b.close()
