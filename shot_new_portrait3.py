from playwright.sync_api import sync_playwright
URL='file:///workspace/bellarich-site/index.html'
OUT='/workspace/bellarich-site/shots/new-portrait/'
CHROME='/workspace/.cache/ms-playwright/chromium-1255/chrome-linux64/chrome'
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=CHROME,args=['--no-sandbox'])
    for tag,w,h in [('1440',1440,900),('1366',1366,768),('1180',1180,800)]:
        ctx=b.new_context(viewport={'width':w,'height':h},device_scale_factor=1)
        pg=ctx.new_page(); pg.goto(URL,wait_until='load'); pg.wait_for_timeout(700)
        info=pg.evaluate("()=>{const q=document.querySelector('.hero').getBoundingClientRect();const m=document.querySelector('.hero__media').getBoundingClientRect();return {hero:[q.height],media:[m.y,m.height]};}")
        print(tag,info)
        pg.locator('.hero').screenshot(path=OUT+'heroel-%s.png'%tag)
        ctx.close()
    b.close()
