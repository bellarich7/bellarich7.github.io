import json
from playwright.sync_api import sync_playwright
url='file:///workspace/bellarich-site/index.html'
JS="""() => {
  const eb=document.querySelector('.hero__eyebrow');
  const tn=[...eb.childNodes].find(n=>n.nodeType===3);
  const rg=document.createRange(); rg.selectNodeContents(tn);
  const rects=[...rg.getClientRects()].map(r=>Math.round(r.width));
  const R=el=>{const r=el.getBoundingClientRect();return {x:Math.round(r.left),y:Math.round(r.top),w:Math.round(r.width),h:Math.round(r.height),bottom:Math.round(r.bottom)};};
  const de=document.documentElement; const over=[];
  document.querySelectorAll('.hero *').forEach(el=>{const r=el.getBoundingClientRect();
    if(r.width>0&&(r.right>de.clientWidth+2||r.left<-2)) over.push(el.tagName+'.'+(el.className||'').toString().slice(0,30));});
  const cs=getComputedStyle(eb);
  return {vw:de.clientWidth, scrollW:de.scrollWidth, eb:R(eb), ebLines:rects.length, rects,
    font:cs.fontSize, ls:cs.letterSpacing, h1:R(document.querySelector('.hero h1')),
    brand:R(document.querySelector('.hero__brand')), cred:R(document.querySelector('.hero__cred')),
    heroOverflow:over};
}"""
with sync_playwright() as p:
    b=p.chromium.launch()
    for w,h in ((360,800),(390,844),(412,915),(320,700)):
        ctx=b.new_context(viewport={'width':w,'height':h}, device_scale_factor=2)
        pg=ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.goto(url,wait_until='load'); pg.wait_for_timeout(400)
        d=pg.evaluate(JS); d['errors']=errs
        print(w, json.dumps(d,ensure_ascii=False))
        ctx.close()
    b.close()
