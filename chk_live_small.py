import json, sys
from playwright.sync_api import sync_playwright
url=sys.argv[1]
JS="""() => {
  const eb=document.querySelector('.hero__eyebrow');
  const tn=[...eb.childNodes].find(n=>n.nodeType===3);
  const rg=document.createRange(); rg.selectNodeContents(tn);
  const rects=[...rg.getClientRects()].map(r=>Math.round(r.width));
  const R=el=>{const r=el.getBoundingClientRect();return {y:Math.round(r.top),h:Math.round(r.height),bottom:Math.round(r.bottom)};};
  const de=document.documentElement;
  return {vw:de.clientWidth, scrollW:de.scrollWidth, cap:R(eb), lines:rects.length, rects,
    font:getComputedStyle(eb).fontSize, logo:R(document.querySelector('.hero__brand .br-logo')),
    h1:R(document.querySelector('.hero h1')), cred:R(document.querySelector('.hero__cred'))};
}"""
with sync_playwright() as p:
    b=p.chromium.launch()
    for w,h in ((360,800),(390,844)):
        ctx=b.new_context(viewport={'width':w,'height':h}, device_scale_factor=2)
        pg=ctx.new_page(); errs=[]; failed=[]
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.on('console', lambda m: errs.append('console:'+m.text) if m.type=='error' else None)
        pg.on('requestfailed', lambda r: failed.append(r.url[:80]))
        pg.goto(url, wait_until='networkidle'); pg.wait_for_timeout(600)
        d=pg.evaluate(JS); d['errors']=errs; d['failed']=failed
        print(w, json.dumps(d,ensure_ascii=False))
        pg.screenshot(path=f'/workspace/bellarich-site/shots/LIVE2-{w}-top.png')
        ctx.close()
    b.close()
