"""메인 솔루션 카드 15개 클릭 동작 검증 (로컬 서버 대상).

사용: python3 chk_card15.py http://127.0.0.1:8765
"""
import sys, json, threading, functools, http.server, socketserver
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8765'
ROOT = '/workspace/bellarich-deploy'

SLUGS = ['office', 'family-corp', 'retirement', 'home-for-kids', 'tax', 'asset', 'in-kind',
         'startup-succession', 'family-business', 'trust', 'credit', 'governance',
         'incorporation', 'welfare-fund', 'ma']
TABS = ['tab-life', 'tab-suc', 'tab-fin']
FORM = 'https://docs.google.com/forms/d/1pvpYq1jJblmrxjHUQeo-nbmB_C3n87T8OCYVzhN5aZE/viewform'
SHORT = '1FAIpQLSeeZEUpDlyWBi7OzRZ74psPsoVOPFQLTok7PFqP'

errors, rows = [], []


def serve():
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


def main():
    global BASE
    if len(sys.argv) > 1:
        srv = None
    else:
        srv = serve()
        BASE = 'http://127.0.0.1:%d' % srv.server_address[1]
    with sync_playwright() as p:
        br = p.chromium.launch()
        # ---------- desktop ----------
        pg = br.new_page(viewport={'width': 1280, 'height': 900})
        pg.on('console', lambda m: errors.append(('desktop', m.type, m.text)) if m.type == 'error' else None)
        pg.on('pageerror', lambda e: errors.append(('desktop', 'pageerror', str(e))))
        pg.goto(BASE + '/', wait_until='networkidle')

        for tab in TABS:
            pg.click('#' + tab)
            pg.wait_for_timeout(150)
            panel = pg.get_attribute('#' + tab, 'aria-controls')
            cards = pg.eval_on_selector_all(
                '#%s .card[data-href]' % panel,
                "els=>els.map(e=>e.getAttribute('data-href'))")
            for href in cards:
                slug = href.split('/')[2]
                sel = '#%s .card[data-href="%s"]' % (panel, href)
                # 1) 카드 본문(제목) 클릭 → 상세 이동
                pg.eval_on_selector(sel, "e=>e.scrollIntoView({block:'center'})")
                pg.wait_for_timeout(60)
                pg.click(sel + ' h3')
                try:
                    pg.wait_for_url('**/plan/%s/' % slug, timeout=4000)
                    url_ok = True
                except Exception:
                    url_ok = False
                try:
                    modal_open = pg.eval_on_selector('#modal', "e=>e.classList.contains('is-open')")
                except Exception:
                    modal_open = False
                rows.append({'panel': panel, 'slug': slug, 'mode': 'body-click',
                             'url': pg.url.replace(BASE, ''), 'ok': url_ok, 'modal': modal_open})
                pg.goto(BASE + '/', wait_until='networkidle')
                pg.click('#' + tab)
                pg.wait_for_timeout(120)

            # 2) '자세히' 링크 · '상담 신청' 링크
            for href in cards:
                slug = href.split('/')[2]
                sel = '#%s .card[data-href="%s"]' % (panel, href)
                pg.click(sel + ' a.card__more:not(.card__apply)')
                try:
                    pg.wait_for_url('**/plan/%s/' % slug, timeout=4000)
                    ok = True
                except Exception:
                    ok = False
                rows.append({'panel': panel, 'slug': slug, 'mode': 'more-link',
                             'url': pg.url.replace(BASE, ''), 'ok': ok})
                pg.goto(BASE + '/', wait_until='networkidle')
                pg.click('#' + tab)
                pg.wait_for_timeout(120)

                with pg.expect_popup() as pop:
                    pg.click(sel + ' a.card__apply')
                popup = pop.value
                popup.wait_for_load_state('domcontentloaded')
                ok2 = (FORM.split('/d/')[1].split('/')[0] in popup.url or SHORT in popup.url) and pg.url.rstrip('/') == BASE.rstrip('/')
                rows.append({'panel': panel, 'slug': slug, 'mode': 'apply-link',
                             'url': popup.url[:60], 'ok': ok2, 'main_stayed': pg.url.rstrip('/') == BASE.rstrip('/')})
                popup.close()
                pg.wait_for_timeout(80)

        # 3) 키보드: 카드 포커스 후 Enter / Space
        for key, tab in [('Enter', 'tab-life'), (' ', 'tab-life')]:
            pg.goto(BASE + '/', wait_until='networkidle')
            pg.click('#' + tab)
            pg.focus('.card[data-href="/plan/office/"]')
            pg.keyboard.press(key)
            try:
                pg.wait_for_url('**/plan/office/', timeout=4000)
                ok = True
            except Exception:
                ok = False
            rows.append({'panel': tab, 'slug': 'office', 'mode': 'keyboard-%s' % key.strip(), 'url': pg.url.replace(BASE, ''), 'ok': ok})

        # 4) 포커스 가능 카드 수
        pg.goto(BASE + '/', wait_until='networkidle')
        tabbable = pg.eval_on_selector_all('.card[tabindex="0"]', 'els=>els.length')
        no_modal_bind = pg.eval_on_selector_all('[data-plan]', 'els=>els.length')

        # ---------- mobile 390 ----------
        m = br.new_page(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
        m.on('console', lambda msg: errors.append(('mobile', msg.type, msg.text)) if msg.type == 'error' else None)
        m.on('pageerror', lambda e: errors.append(('mobile', 'pageerror', str(e))))
        m.goto(BASE + '/', wait_until='networkidle')
        for slug, tab in [('office', 'tab-life'), ('startup-succession', 'tab-suc'), ('ma', 'tab-fin')]:
            m.click('#' + tab)
            m.wait_for_timeout(150)
            sel = '.card[data-href="/plan/%s/"]' % slug
            m.eval_on_selector(sel, "e=>e.scrollIntoView({block:'center'})")
            m.wait_for_timeout(80)
            m.tap(sel + ' h3')
            try:
                m.wait_for_url('**/plan/%s/' % slug, timeout=4000)
                ok = True
            except Exception:
                ok = False
            rows.append({'panel': tab, 'slug': slug, 'mode': 'mobile-tap', 'url': m.url.replace(BASE, ''), 'ok': ok})
            m.goto(BASE + '/', wait_until='networkidle')
        over = m.evaluate("()=>({sw:document.documentElement.scrollWidth, cw:document.documentElement.clientWidth})")

        br.close()
    if srv: srv.shutdown()

    bad = [r for r in rows if not r['ok']]
    print(json.dumps({'rows': rows, 'bad': bad, 'errors': errors,
                      'tabbable_cards': tabbable, 'data_plan_left': no_modal_bind,
                      'mobile_overflow': over}, ensure_ascii=False, indent=1))


main()
