import json
from playwright.sync_api import sync_playwright

URL = "https://bellarich.co.kr/check/?v=1125u"
JS = r"""
() => {
  const r = el => { if (!el) return null; const b = el.getBoundingClientRect();
    return {top:+(b.top+scrollY).toFixed(1), bottom:+(b.bottom+scrollY).toFixed(1), h:+b.height.toFixed(1)}; };
  const s = el => { if(!el) return null; const c=getComputedStyle(el);
    return {pt:c.paddingTop,pb:c.paddingBottom,mt:c.marginTop,mb:c.marginBottom,bt:c.borderTopWidth,bb:c.borderBottomWidth,disp:c.display}; };
  const chain = [];
  let el = document.querySelector('#q0-options').lastElementChild;
  while (el && el !== document.body) {
    chain.push({tag: el.tagName + (el.id?('#'+el.id):'') + (el.className && typeof el.className==='string'?('.'+el.className.trim().split(/\s+/).join('.')):''), box:r(el), css:s(el)});
    el = el.parentElement;
  }
  // also hero side
  const heroChain = [];
  let h = document.querySelector('.hero-eyebrow');
  while (h && h !== document.body) {
    heroChain.push({tag: h.tagName + (h.id?('#'+h.id):'') + (h.className && typeof h.className==='string'?('.'+h.className.trim().split(/\s+/).join('.')):''), box:r(h), css:s(h)});
    h = h.parentElement;
  }
  // footer chain
  const footChain = [];
  let f = document.querySelector('.footer strong');
  while (f && f !== document.body) {
    footChain.push({tag: f.tagName + (f.id?('#'+f.id):'') + (f.className && typeof f.className==='string'?('.'+f.className.trim().split(/\s+/).join('.')):''), box:r(f), css:s(f)});
    f = f.parentElement;
  }
  const cfp = document.querySelectorAll('.hero-stat-label')[2];
  return {chain, heroChain, footChain,
    cfp: cfp ? {box:r(cfp), width: cfp.getBoundingClientRect().width, scrollW: cfp.scrollWidth, text: cfp.textContent} : null,
    statNum: document.querySelectorAll('.hero-stat-num')[2] ? r(document.querySelectorAll('.hero-stat-num')[2]) : null,
    cols: getComputedStyle(document.querySelector('.hero-stats')).gridTemplateColumns};
}
"""
for w in (390, 360):
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={'width': w, 'height': 900})
        pg.goto(URL, wait_until='networkidle')
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(500)
        d = pg.evaluate(JS)
        print('=====', w)
        print('q0 chain:')
        for c in d['chain']: print('  ', c['tag'], c['box'], c['css'])
        print('hero chain:')
        for c in d['heroChain']: print('  ', c['tag'], c['box'], c['css'])
        print('footer chain:')
        for c in d['footChain']: print('  ', c['tag'], c['box'], c['css'])
        print('cfp:', json.dumps(d['cfp'], ensure_ascii=False))
        print('statNum:', d['statNum'], 'cols:', d['cols'])
        b.close()
