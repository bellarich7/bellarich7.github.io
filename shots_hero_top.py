from playwright.sync_api import sync_playwright
url='file:///workspace/bellarich-site/index.html'
with sync_playwright() as p:
    b=p.chromium.launch()
    for label,w,h,dsf in (('1440',1440,900,1),('1366',1366,768,1),('390',390,844,2),('360',360,800,2)):
        ctx=b.new_context(viewport={'width':w,'height':h}, device_scale_factor=dsf)
        pg=ctx.new_page(); pg.goto(url,wait_until='load'); pg.wait_for_timeout(700)
        pg.screenshot(path=f'/workspace/bellarich-site/shots/final-hero-top-{label}.png')
        ctx.close()
    b.close()
