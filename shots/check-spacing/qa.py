import json, os, sys
from playwright.sync_api import sync_playwright

URL = sys.argv[1]
LABEL = sys.argv[2]
OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))

report = {}
with sync_playwright() as p:
    b = p.chromium.launch()
    for w in (390, 360, 1440):
        pg = b.new_page(viewport={'width': w, 'height': 900}, device_scale_factor=2 if w < 500 else 1)
        errs, reqs = [], []
        pg.on('console', lambda m: errs.append(f'{m.type}: {m.text}') if m.type in ('error', 'warning') else None)
        pg.on('pageerror', lambda e: errs.append('pageerror: ' + str(e)))
        pg.on('request', lambda r: reqs.append(r.url))
        pg.goto(URL, wait_until='load')
        pg.wait_for_timeout(1000)
        pg.evaluate("document.fonts.ready")

        ov = pg.evaluate("""() => ({sw: document.documentElement.scrollWidth, iw: window.innerWidth,
                                   bh: document.body.scrollWidth, dh: document.documentElement.scrollHeight})""")
        endpoint = pg.evaluate("() => { try { return eval('SUBMIT_ENDPOINT'); } catch(e) { return 'eval-blocked:'+e.message; } }")

        # flow
        pg.click('#btn-start-test')
        pg.wait_for_selector('#screen-category.active', timeout=5000)
        pg.click('.category-card')
        pg.wait_for_selector('#screen-question.active', timeout=5000)
        qcount = pg.evaluate("() => document.querySelectorAll('#q-options .option').length")
        steps = 0
        for i in range(6):
            pg.click('#q-options .option:nth-child(2)')
            steps += 1
            pg.click('#btn-next')
            pg.wait_for_timeout(120)
        consent_ok = pg.evaluate("() => document.querySelector('#screen-consent').classList.contains('active')")
        pg.fill('#consent-name', '테스트')
        pg.fill('#consent-email', 'test@example.com')
        pg.check('#consent-collection')
        pg.click('#btn-consent')
        pg.wait_for_selector('#screen-result.active', timeout=5000)
        grade = pg.evaluate("() => document.getElementById('grade-circle').textContent")
        gname = pg.evaluate("() => document.getElementById('grade-name').textContent")
        pg.wait_for_timeout(400)
        pg.screenshot(path=os.path.join(OUTDIR, f'qa_{LABEL}_{w}_result.png'), full_page=True)
        result_ov = pg.evaluate("() => ({sw: document.documentElement.scrollWidth, iw: window.innerWidth})")
        external = [u for u in reqs if not u.startswith('file:') and 'bellarich' not in u and 'fonts' not in u]
        report[w] = {'overflow': ov, 'endpoint': endpoint, 'console': errs, 'options_on_q1': qcount,
                     'steps_answered': steps, 'consent_reached': consent_ok, 'grade': grade,
                     'grade_name': gname[:40], 'result_overflow': result_ov, 'external_requests': external}
        pg.close()
    b.close()
print(json.dumps(report, ensure_ascii=False, indent=1))
