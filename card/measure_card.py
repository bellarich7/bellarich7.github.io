import json
import sys
from playwright.sync_api import sync_playwright

URL = sys.argv[1]
print_url = URL

JS = """() => {
  const de = document.documentElement;
  const q = s => { const e = document.querySelector(s); if(!e) return null; const r = e.getBoundingClientRect();
    return {top:+(r.top+window.scrollY).toFixed(1), h:+r.height.toFixed(1), bottom:+(r.bottom+window.scrollY).toFixed(1)}; };
  return {
    docH: de.scrollHeight, innerH: window.innerHeight,
    overflowX: de.scrollWidth - de.clientWidth,
    card: q('.card'), hero: q('.hero'), idbox: q('.idbox'), info: q('.info'),
    slogan: q('.slogan'), links: q('.links'), sns: q('.sns'), acts: q('.acts'), foot: q('.foot'),
    rows: [...document.querySelectorAll('.info__row')].map(r => Math.round(r.getBoundingClientRect().height)),
    lkCount: document.querySelectorAll('.lk').length,
    tags: document.querySelectorAll('.idbox__tags li').length,
    photo: (()=>{const i=document.querySelector('.hero__photo img'); const r=i.getBoundingClientRect();
      return {w:+r.width.toFixed(1), h:+r.height.toFixed(1), top:+r.top.toFixed(1), bottom:+r.bottom.toFixed(1), nw:i.naturalWidth, complete:i.complete};})()
  };
}"""

with sync_playwright() as p:
    b = p.chromium.launch()
    out = {'url': print_url}
    for name, w, h in [('m390', 390, 844), ('m320', 320, 640), ('m414', 414, 896), ('pc1440', 1440, 900)]:
        ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2,
                            is_mobile=w < 700, has_touch=w < 700)
        pg = ctx.new_page()
        errs = []
        pg.on('console', lambda m: errs.append(m.type + ':' + m.text) if m.type == 'error' else None)
        pg.on('pageerror', lambda e: errs.append('pageerror:' + str(e)))
        pg.goto(URL, wait_until='load')
        pg.wait_for_timeout(1400)
        pg.evaluate("() => document.fonts && document.fonts.ready")
        pg.wait_for_timeout(400)
        out[name] = pg.evaluate(JS)
        out[name]['errors'] = errs
        ctx.close()
    b.close()
print(json.dumps(out, ensure_ascii=False, indent=1))
