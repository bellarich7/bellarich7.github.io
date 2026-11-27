from playwright.sync_api import sync_playwright
URL='file:///workspace/bellarich-site/index.html'
OUT='/workspace/bellarich-site/shots/new-portrait/'
CHROME='/workspace/.cache/ms-playwright/chromium-1255/chrome-linux64/chrome'
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=CHROME,args=['--no-sandbox'])
    # mobile: whole hero element
    ctx=b.new_context(viewport={'width':390,'height':844},device_scale_factor=2)
    pg=ctx.new_page(); pg.goto(URL,wait_until='load'); pg.wait_for_timeout(800)
    pg.locator('.hero').screenshot(path=OUT+'local-m390-hero-full.png'); ctx.close()
    for tag,w,h in [('pc1366',1366,768),('pc1180',1180,800)]:
        ctx=b.new_context(viewport={'width':w,'height':h},device_scale_factor=1)
        pg=ctx.new_page(); pg.goto(URL,wait_until='load'); pg.wait_for_timeout(800)
        pg.screenshot(path=OUT+'local-%s-hero.png'%tag); ctx.close()
    b.close()
print('ok')
