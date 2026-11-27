from playwright.sync_api import sync_playwright
CHROME='/workspace/.cache/ms-playwright/chromium-1255/chrome-linux64/chrome'
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=CHROME,args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1440,'height':900})
    pg=ctx.new_page(); pg.goto('file:///workspace/bellarich-site/index.html',wait_until='load'); pg.wait_for_timeout(600)
    pg.locator('footer.footer').screenshot(path='/workspace/bellarich-site/shots/new-portrait/local-footer.png')
    print(pg.locator('.footer__info').first.inner_text())
    b.close()
