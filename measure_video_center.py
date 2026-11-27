import sys, json
from playwright.sync_api import sync_playwright
url = sys.argv[1] if len(sys.argv) > 1 else 'file:///workspace/bellarich-site/index.html'
VPS = [('pc1440', 1440, 900, 1), ('pc1366', 1366, 768, 1), ('pc1920', 1920, 1080, 1),
       ('tab900', 900, 1180, 1), ('tab768', 768, 1024, 1), ('m390', 390, 844, 2), ('m360', 360, 740, 2)]
JS = """() => {
  const R = el => el.getBoundingClientRect();
  const card = document.querySelector('.philo__video');
  const inner = document.querySelector('.philo__video .video-card');
  const wrap = card.closest('.wrap');
  const cs = getComputedStyle(wrap);
  const wr = R(wrap);
  const padL = parseFloat(cs.paddingLeft), padR = parseFloat(cs.paddingRight);
  const boxL = wr.left + padL, boxR = wr.right - padR;
  const c = R(inner);
  return {
    viewport: window.innerWidth,
    wrapContent: [+boxL.toFixed(1), +boxR.toFixed(1)],
    wrapContentW: +(boxR - boxL).toFixed(1),
    cardW: +c.width.toFixed(1),
    gapLeft: +(c.left - boxL).toFixed(1),
    gapRight: +(boxR - c.right).toFixed(1),
    // distance from the card centre to the viewport centre
    centreOffsetViewport: +((c.left + c.right) / 2 - window.innerWidth / 2).toFixed(1),
    centreOffsetWrap: +((c.left + c.right) / 2 - (boxL + boxR) / 2).toFixed(1)
  };
}"""
with sync_playwright() as p:
    b = p.chromium.launch()
    for label, w, h, dpr in VPS:
        ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=dpr)
        pg = ctx.new_page(); pg.goto(url, wait_until='load'); pg.wait_for_timeout(400)
        print(label, json.dumps(pg.evaluate(JS), ensure_ascii=False))
        ctx.close()
    b.close()
