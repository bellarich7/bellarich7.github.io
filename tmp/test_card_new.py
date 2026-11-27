import json
from playwright.sync_api import sync_playwright

URL = 'file:///workspace/bellarich-site/card/index.html'
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2, is_mobile=True, has_touch=True, accept_downloads=True)
    pg = ctx.new_page()
    errors=[]
    pg.on('console', lambda m: errors.append('console:'+m.type+':'+m.text) if m.type=='error' else None)
    pg.on('pageerror', lambda e: errors.append('pageerror:'+str(e)))
    pg.goto(URL, wait_until='load'); pg.wait_for_timeout(800)

    # hrefs
    links = pg.eval_on_selector_all('a', "els => els.map(e => [e.getAttribute('href'), (e.getAttribute('aria-label')||e.textContent.trim().slice(0,20))])")
    print('LINKS', json.dumps(links, ensure_ascii=False))

    # download vcard
    with pg.expect_download() as dl:
        pg.click('#saveCard')
    d = dl.value
    path = d.path()
    content = open(path, encoding='utf-8').read()
    print('VCARD', d.suggested_filename, '|', content.replace('\r\n',' / '))

    # share fallback -> clipboard message
    pg.evaluate("() => { delete navigator.share; }")
    pg.click('#shareCard'); pg.wait_for_timeout(400)
    print('TOAST', pg.inner_text('#toast'), pg.eval_on_selector('#toast','e=>e.className'))

    # tap targets
    sizes = pg.eval_on_selector_all('a.info__row, .lk, .btn', "els => els.map(e => {const r=e.getBoundingClientRect(); return [e.textContent.trim().slice(0,14), Math.round(r.height)];})")
    print('TAP', json.dumps(sizes, ensure_ascii=False))
    print('ERRORS', errors)
    b.close()
