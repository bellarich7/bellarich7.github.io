from playwright.sync_api import sync_playwright
CHROME='/workspace/.cache/ms-playwright/chromium-1255/chrome-linux64/chrome'
OUT='/workspace/bellarich-site/shots/new-portrait/'
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=CHROME,args=['--no-sandbox'])
    for tag,w,h in [('768',768,1024),('360',360,740)]:
        ctx=b.new_context(viewport={'width':w,'height':h},device_scale_factor=2 if w<500 else 1)
        pg=ctx.new_page(); pg.goto('file:///workspace/bellarich-site/index.html',wait_until='load'); pg.wait_for_timeout(700)
        pg.screenshot(path=OUT+'local-%s-hero.png'%tag)
        ov=pg.evaluate("()=>document.documentElement.scrollWidth-document.documentElement.clientWidth")
        print(tag,'overflowX',ov)
        pg.locator('.hero').screenshot(path=OUT+'heroel-%s.png'%tag); ctx.close()
    b.close()
