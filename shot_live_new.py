from playwright.sync_api import sync_playwright
CHROME='/workspace/.cache/ms-playwright/chromium-1255/chrome-linux64/chrome'
OUT='/workspace/bellarich-site/shots/new-portrait/'
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=CHROME,args=['--no-sandbox'])
    for tag,w,h,dpr,url in [
        ('pc1440-hero',1440,900,1,'https://bellarich.co.kr/?v=1125y'),
        ('m390-hero',390,844,2,'https://bellarich.co.kr/?v=1125y'),
        ('card-m390-top',390,844,2,'https://bellarich.co.kr/card/?v=1125y')]:
        ctx=b.new_context(viewport={'width':w,'height':h},device_scale_factor=dpr)
        pg=ctx.new_page(); pg.goto(url,wait_until='networkidle'); pg.wait_for_timeout(1200)
        pg.screenshot(path=OUT+tag+'.png')
        print(tag,'ok')
        ctx.close()
    b.close()
