from playwright.sync_api import sync_playwright
CHROME='/workspace/.cache/ms-playwright/chromium-1255/chrome-linux64/chrome'
OUT='/workspace/bellarich-site/shots/new-portrait/'
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=CHROME,args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1440,'height':900},device_scale_factor=2)
    pg=ctx.new_page(); pg.goto('https://bellarich.co.kr/?v=1125y',wait_until='networkidle'); pg.wait_for_timeout(1000)
    m=pg.evaluate("()=>{const r=document.querySelector('.hero__media').getBoundingClientRect();return [r.x,r.y,r.width,r.height];}")
    x,y,w,h=m
    pg.screenshot(path=OUT+'pc1440-face-dpr2.png', clip={'x':x+w*0.25,'y':y+h*0.02,'width':w*0.75,'height':h*0.42})
    b.close()
print('ok')
