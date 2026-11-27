import json
from playwright.sync_api import sync_playwright
PAIRS = [('before', 'file:///workspace/bellarich-site/_before_index.html'),
         ('after',  'file:///workspace/bellarich-site/index.html')]
JS = """() => {
  const out = {};
  const sel = ['.hero', '.hero__in', '.hero h1', '.hero__cred', '.band', '#philosophy', '.philo__grid',
               '.venn', '.philo__text', '.philo__video', '.video-card', '.video-card__cap',
               '#solutions', '.sol__head', '.tabs', '#panel-life', '.suc-block', '#about', '.career',
               '#contact', 'footer', 'body'];
  for (const s of sel) {
    const el = document.querySelector(s);
    if (!el) { out[s] = null; continue; }
    const r = el.getBoundingClientRect();
    out[s] = [Math.round(r.left), Math.round(r.top + window.scrollY), Math.round(r.width), Math.round(r.height)];
  }
  out.__docH = document.documentElement.scrollHeight;
  return out;
}"""
res = {}
with sync_playwright() as p:
    b = p.chromium.launch()
    for tag, url in PAIRS:
        ctx = b.new_context(viewport={'width': 1440, 'height': 900}, device_scale_factor=1)
        pg = ctx.new_page(); pg.goto(url, wait_until='load'); pg.wait_for_timeout(500)
        pg.evaluate("() => document.querySelectorAll('.rv').forEach(e => e.classList.add('is-in','in','rv--in'))")
        pg.wait_for_timeout(400)
        res[tag] = pg.evaluate(JS)
        ctx.close()
    b.close()
for k in res['before']:
    a, c = res['before'][k], res['after'][k]
    flag = '' if a == c else '   <<< CHANGED'
    print('%-20s before %-28s after %-28s%s' % (k, a, c, flag))
