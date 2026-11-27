from playwright.sync_api import sync_playwright
CHROME='/workspace/.cache/ms-playwright/chromium-1255/chrome-linux64/chrome'
OUT='/workspace/bellarich-site/shots/new-portrait/'
URL='file:///workspace/bellarich-site/card/index.html'
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=CHROME,args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':390,'height':844},device_scale_factor=2)
    pg=ctx.new_page(); pg.goto(URL,wait_until='load'); pg.wait_for_timeout(700)
    pg.screenshot(path=OUT+'local-card-m390-top.png')
    ctx.close()
    ctx=b.new_context(viewport={'width':1440,'height':900},device_scale_factor=1)
    pg=ctx.new_page(); pg.goto(URL,wait_until='load'); pg.wait_for_timeout(700)
    pg.screenshot(path=OUT+'local-card-pc1440.png'); ctx.close()
    b.close()
print('ok')
