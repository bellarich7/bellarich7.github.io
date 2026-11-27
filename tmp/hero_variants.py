import sys
from playwright.sync_api import sync_playwright

URL = 'file:///workspace/bellarich-site/card/index.html'
OUT = '/workspace/bellarich-site/tmp/'
variants = {
    'cur': ('#0B1933', '#1D3152'),
    'a20': ('#16294C', '#2A4270'),
    'b45': ('#1A2F55', '#2E4776'),
    'c57': ('#1B3157', '#35507F'),
    'd2f': ('#1D3259', '#39548A'),
}
with sync_playwright() as p:
    b = p.chromium.launch()
    for name, (base, rad) in variants.items():
        ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2,
                            is_mobile=True, has_touch=True)
        pg = ctx.new_page()
        pg.goto(URL, wait_until='load')
        pg.wait_for_timeout(1200)
        pg.evaluate("() => document.fonts && document.fonts.ready")
        pg.wait_for_timeout(300)
        pg.add_style_tag(content="""
          .hero__stage{background:
            radial-gradient(54%% 48%% at 50%% 62%%,rgba(197,164,126,.22) 0%%,rgba(197,164,126,.06) 52%%,rgba(197,164,126,0) 76%%),
            radial-gradient(125%% 95%% at 50%% 2%%,%s 0%%,rgba(29,49,82,0) 62%%),
            %s !important;}
        """ % (rad, base))
        pg.wait_for_timeout(300)
        pg.screenshot(path=OUT + 'hero-%s.png' % name, clip={'x': 0, 'y': 0, 'width': 390, 'height': 560})
        ctx.close()
    b.close()
print('done')
