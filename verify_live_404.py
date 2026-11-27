from playwright.sync_api import sync_playwright
CHROME='/workspace/.cache/ms-playwright/chromium-1255/chrome-linux64/chrome'
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=CHROME,args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1440,'height':900})
    pg=ctx.new_page()
    bad=[]
    pg.on('response', lambda r: bad.append((r.status,r.url)) if r.status>=400 else None)
    pg.goto('https://bellarich.co.kr/?v=1125y',wait_until='networkidle'); pg.wait_for_timeout(1200)
    print(bad)
    b.close()
