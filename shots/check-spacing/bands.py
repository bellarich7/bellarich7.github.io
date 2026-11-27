import json, os, sys
from playwright.sync_api import sync_playwright

URL = sys.argv[1]
LABEL = sys.argv[2]
OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))

JS = r"""
() => {
  const r = el => { const b = el.getBoundingClientRect();
    return {top:+(b.top+scrollY).toFixed(1), bottom:+(b.bottom+scrollY).toFixed(1)}; };
  const all = s => Array.from(document.querySelectorAll(s));
  const q0 = all('#q0-options .q0-opt'); const lastQ0 = q0[q0.length-1];
  const services = all('.service'); const lastSvc = services[services.length-1];
  return {
    q0: r(lastQ0), heroEyebrow: r(document.querySelector('.hero-eyebrow')),
    tagline: r(all('.hero-sub')[1]), posEyebrow: r(document.querySelector('#positioning .section-eyebrow')),
    venn: r(document.querySelector('.venn-img')), expEyebrow: r(document.querySelector('.intro .section-eyebrow')),
    lastSvc: r(lastSvc), footerStrong: r(document.querySelector('.footer strong')),
    docH: document.documentElement.scrollHeight
  };
}
"""

BANDS = [
    ('1_q0_hero', 'q0', 'heroEyebrow'),
    ('2_tagline_why', 'tagline', 'posEyebrow'),
    ('3_venn_expertise', 'venn', 'expEyebrow'),
    ('4_services_footer', 'lastSvc', 'footerStrong'),
]

with sync_playwright() as p:
    b = p.chromium.launch()
    out = {}
    for w in (390, 1440):
        pg = b.new_page(viewport={'width': w, 'height': 900}, device_scale_factor=2 if w < 500 else 1)
        pg.goto(URL, wait_until='load')
        pg.wait_for_timeout(1200)
        pg.evaluate("document.fonts.ready")
        m = pg.evaluate(JS)
        out[w] = m
        for name, a, c in BANDS:
            top = max(0, m[a]['bottom'] - 60)
            bottom = min(m['docH'], m[c]['top'] + 60)
            pg.screenshot(path=os.path.join(OUTDIR, f'{LABEL}_{w}_band_{name}.png'),
                          full_page=True, clip={'x': 0, 'y': top, 'width': w, 'height': bottom - top})
        pg.close()
    b.close()
print(json.dumps(out, ensure_ascii=False, indent=1))
