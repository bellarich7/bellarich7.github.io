from playwright.sync_api import sync_playwright
CHROME='/workspace/.cache/ms-playwright/chromium-1255/chrome-linux64/chrome'
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=CHROME,args=['--no-sandbox'])
    ctx=b.new_context(viewport={'width':1440,'height':900})
    pg=ctx.new_page(); errs=[]; fails=[]
    pg.on('console', lambda m: errs.append(m.text) if m.type=='error' else None)
    pg.on('requestfailed', lambda r: fails.append(r.url))
    pg.goto('https://bellarich.co.kr/?v=1125y',wait_until='networkidle'); pg.wait_for_timeout(1000)
    info=pg.evaluate("""()=>{const m=document.querySelector('.hero__media');const cs=getComputedStyle(m);
      const f=document.querySelector('.footer__info');
      return {hasImg: cs.backgroundImage.startsWith('url("data:image/webp'), footer:f.innerText.split('\\n')[1], h:document.querySelector('.hero').getBoundingClientRect().height};}""")
    print(info); print('console errors',errs); print('failed requests',fails)
    b.close()
