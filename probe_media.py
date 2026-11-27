from playwright.sync_api import sync_playwright
CHROME='/workspace/.cache/ms-playwright/chromium-1255/chrome-linux64/chrome'
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=CHROME,args=['--no-sandbox'])
    for w,h in [(1440,900),(1180,800),(1100,800)]:
        ctx=b.new_context(viewport={'width':w,'height':h}); pg=ctx.new_page()
        pg.goto('file:///workspace/bellarich-site/index.html',wait_until='load'); pg.wait_for_timeout(500)
        r=pg.evaluate("""()=>{const m=document.querySelector('.hero__media');const cs=getComputedStyle(m);const b=m.getBoundingClientRect();
        return {box:[b.x,b.y,b.width,b.height],height:cs.height,width:cs.width,size:cs.backgroundSize,pos:cs.backgroundPosition};}""")
        print(w,h,r); ctx.close()
    b.close()
