import json, sys, os
from playwright.sync_api import sync_playwright

URL = sys.argv[1]
LABEL = sys.argv[2]  # e.g. before / after
OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))
WIDTHS = [390, 360, 1440]

JS = r"""
() => {
  const r = el => { if (!el) return null; const b = el.getBoundingClientRect();
    return {top: +(b.top + window.scrollY).toFixed(1), bottom: +(b.bottom + window.scrollY).toFixed(1),
            left: +b.left.toFixed(1), right: +b.right.toFixed(1), h: +b.height.toFixed(1), w: +b.width.toFixed(1)}; };
  const first = sel => document.querySelector(sel);
  const all = sel => Array.from(document.querySelectorAll(sel));
  const q0opts = all('#q0-options .q0-opt');
  const lastQ0 = q0opts.length ? q0opts[q0opts.length-1] : null;
  const heroInner = first('.hero-inner');
  const heroEyebrow = first('.hero-eyebrow');
  const heroSub2 = all('.hero-sub')[1] || null;
  const positioning = first('#positioning');
  const posEyebrow = first('#positioning .section-eyebrow');
  const venn = first('.venn-img');
  const intro = first('.intro');
  const expEyebrow = first('.intro .section-eyebrow');
  const services = all('.service');
  const lastService = services.length ? services[services.length-1] : null;
  const footer = first('.footer');
  const footerStrong = first('.footer strong');
  const cfpLabel = all('.hero-stat-label')[2] || null;
  const cfpNum = all('.hero-stat-num')[2] || null;
  let cfpLines = null, cfpLH = null;
  if (cfpLabel) {
    const cs = getComputedStyle(cfpLabel);
    cfpLH = cs.lineHeight;
    const lh = parseFloat(cs.lineHeight) || parseFloat(cs.fontSize)*1.2;
    cfpLines = Math.round(cfpLabel.getBoundingClientRect().height / lh);
  }
  const sub2cs = heroSub2 ? getComputedStyle(heroSub2) : null;
  return {
    docH: document.documentElement.scrollHeight,
    scrollW: document.documentElement.scrollWidth,
    innerW: window.innerWidth,
    q0last: r(lastQ0), heroInner: r(heroInner), heroEyebrow: r(heroEyebrow),
    heroSub2: r(heroSub2), positioning: r(positioning), posEyebrow: r(posEyebrow),
    venn: r(venn), intro: r(intro), expEyebrow: r(expEyebrow),
    lastService: r(lastService), footer: r(footer), footerStrong: r(footerStrong),
    cfpLabel: r(cfpLabel), cfpNum: r(cfpNum), cfpLines: cfpLines, cfpLineHeight: cfpLH,
    heroSub2Style: sub2cs ? {fontSize: sub2cs.fontSize, fontWeight: sub2cs.fontWeight,
      color: sub2cs.color, lineHeight: sub2cs.lineHeight, margin: sub2cs.margin,
      whiteSpace: sub2cs.whiteSpace} : null,
    cfpLabelStyle: cfpLabel ? (s => ({fontSize:s.fontSize, fontWeight:s.fontWeight,
      whiteSpace:s.whiteSpace, letterSpacing:s.letterSpacing, lineHeight:s.lineHeight}))(getComputedStyle(cfpLabel)) : null,
    heroStatBoxes: all('.hero-stat').map(el => r(el)),
  };
}
"""

def gaps(m):
    def g(a, b):
        if a is None or b is None: return None
        return round(b['top'] - a['bottom'], 1)
    return {
        'q0_to_heroEyebrow': g(m['q0last'], m['heroEyebrow']),
        'q0_to_heroInnerTop': g(m['q0last'], m['heroInner']),
        'heroSub2_to_posEyebrow': g(m['heroSub2'], m['posEyebrow']),
        'heroSub2_to_positioningTop': g(m['heroSub2'], m['positioning']),
        'venn_to_expEyebrow': g(m['venn'], m['expEyebrow']),
        'venn_to_introTop': g(m['venn'], m['intro']),
        'lastService_to_footerStrong': g(m['lastService'], m['footerStrong']),
        'lastService_to_footer': g(m['lastService'], m['footer']),
        'lastService_to_docEnd': round(m['docH'] - m['lastService']['bottom'], 1) if m['lastService'] else None,
    }

results = {}
with sync_playwright() as p:
    b = p.chromium.launch()
    for w in WIDTHS:
        ctx = b.new_context(viewport={'width': w, 'height': 900}, device_scale_factor=2 if w < 500 else 1)
        pg = ctx.new_page()
        pg.goto(URL, wait_until='networkidle')
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(700)
        m = pg.evaluate(JS)
        results[w] = {'metrics': m, 'gaps': gaps(m)}
        pg.screenshot(path=os.path.join(OUTDIR, f'{LABEL}_{w}_full.png'), full_page=True)
        # close-ups
        shots = {
            'hero': '.hero',
            'stats': '.hero-stats',
            'positioning': '#positioning',
            'venn_intro': '.venn-img',
            'services_footer': '.intro',
        }
        for name, sel in shots.items():
            try:
                pg.locator(sel).first.scroll_into_view_if_needed()
                pg.wait_for_timeout(150)
                pg.locator(sel).first.screenshot(path=os.path.join(OUTDIR, f'{LABEL}_{w}_{name}.png'))
            except Exception as e:
                print('shot fail', name, e)
        ctx.close()
    b.close()

with open(os.path.join(OUTDIR, f'{LABEL}_metrics.json'), 'w') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
for w, v in results.items():
    print(f"== {w}px == docH={v['metrics']['docH']} scrollW={v['metrics']['scrollW']} (innerW={v['metrics']['innerW']})")
    print('  gaps:', json.dumps(v['gaps'], ensure_ascii=False))
    print('  cfpLines:', v['metrics']['cfpLines'], 'labelH:', v['metrics']['cfpLabel']['h'] if v['metrics']['cfpLabel'] else None)
    print('  heroSub2:', json.dumps(v['metrics']['heroSub2Style'], ensure_ascii=False))
