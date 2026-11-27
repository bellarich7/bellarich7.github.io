from playwright.sync_api import sync_playwright
URL = 'https://bellarich.co.kr/?v=1125u'
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width': 1440, 'height': 900})
    pg = ctx.new_page()
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('console', lambda m: errs.append('console:' + m.text) if m.type == 'error' else None)
    pg.goto(URL, wait_until='load'); pg.wait_for_timeout(1200)
    pg.evaluate("""() => { const el = document.querySelector('.philo__video');
        window.scrollTo(0, el.getBoundingClientRect().top + window.scrollY - 120); }""")
    pg.wait_for_timeout(700)
    pg.click('#videoPlay')
    pg.wait_for_timeout(1800)
    state = pg.evaluate("""() => ({playing: document.querySelector('#videoCard').classList.contains('is-playing'),
        playerVisible: getComputedStyle(document.querySelector('#videoPlayer')).display,
        thumbVisible: getComputedStyle(document.querySelector('#videoPlay')).display,
        paused: document.querySelector('#videoPlayer').paused,
        readyState: document.querySelector('#videoPlayer').readyState,
        src: document.querySelector('#videoPlayer currentSrc') ? '' : document.querySelector('#videoPlayer').currentSrc})""")
    pg.screenshot(path='/workspace/bellarich-site/shots/hero-quality/live-1440-video-playing.png')
    print(state)
    print('errors:', errs[:5])
    ctx.close(); b.close()
