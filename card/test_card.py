import json
import sys
from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else 'file:///workspace/bellarich-site/card/index.html'
PFX = sys.argv[2] if len(sys.argv) > 2 else 'test'
OUT = '/workspace/bellarich-site/shots/card/'

fails = []


def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ') + msg)
    if not cond:
        fails.append(msg)


with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2,
                        is_mobile=True, has_touch=True, accept_downloads=True,
                        permissions=['clipboard-read', 'clipboard-write'])
    pg = ctx.new_page()
    errors, failed_req, bad_status = [], [], []
    pg.on('console', lambda m: errors.append(m.type + ':' + m.text) if m.type == 'error' else None)
    pg.on('pageerror', lambda e: errors.append('pageerror:' + str(e)))
    pg.on('requestfailed', lambda r: failed_req.append(r.url + ' ' + str(r.failure)))
    pg.on('response', lambda r: bad_status.append((r.status, r.url)) if r.status >= 400 else None)
    pg.goto(URL, wait_until='load')
    pg.wait_for_timeout(1500)
    pg.evaluate("() => document.fonts && document.fonts.ready")
    pg.wait_for_timeout(400)

    links = pg.evaluate("() => [...document.querySelectorAll('a')].map(a => ({t:(a.getAttribute('aria-label')||a.textContent.trim().replace(/\\s+/g,' ')).slice(0,34), href:a.getAttribute('href'), y:Math.round(a.getBoundingClientRect().top)}))")
    print(json.dumps(links, ensure_ascii=False, indent=1))
    hrefs = [l['href'] for l in links]
    expected = {
        'tel:+821050310789': 1,
        'https://bellarich.co.kr/': 1,
        'https://bellarich.co.kr/check/': 1,
        'https://docs.google.com/forms/d/1pvpYq1jJblmrxjHUQeo-nbmB_C3n87T8OCYVzhN5aZE/viewform': 1,
        'https://pf.kakao.com/_xkySDn': 1,
        'https://youtube.com/@bellarich7': 1,
        'https://www.instagram.com/bellarich1004': 1,
        'https://m.blog.naver.com/bellarich1004': 1,
        'mailto:bellarich7@naver.com': 2,
        'https://map.naver.com/p/search/%EC%84%9C%EC%9A%B8%20%EC%84%9C%EB%8C%80%EB%AC%B8%EA%B5%AC%20%EC%9D%B4%ED%99%94%EC%97%AC%EB%8C%801%EA%B8%B8%2038': 1,
    }
    for h, n in expected.items():
        check(hrefs.count(h) == n, 'href %s x%d (got %d)' % (h, n, hrefs.count(h)))
    check(len(hrefs) == 11, 'total links 11 (got %d)' % len(hrefs))

    # order: kakao row above the health check, 한 줄 sns row last
    order = [l['href'] for l in links]
    i_kakao = order.index('https://pf.kakao.com/_xkySDn')
    i_check = order.index('https://bellarich.co.kr/check/')
    check(i_kakao < i_check, 'kakao row sits above the health check')

    # removed content
    body = pg.inner_text('body')
    check('법인 절세·승계' not in body and '수익형 부동산' not in body, 'tag chips removed')
    check('법인을 아는 부동산 전문가' not in body, 'slogan removed')
    check('카카오톡 채널 친구 추가' in body, 'kakao row labelled 친구 추가')
    for t in ['김자영', '법인 자산관리 · 부동산 전문가', 'CFP · 공인중개사', '벨라리치(주) 대표']:
        check(t in body, 'idbox line present: ' + t)
    check('상담문의' not in body, '상담문의 row removed')
    check('010-4825-5383' not in body and '4825' not in body, 'secondary phone 5383 gone from page')
    check('벨라리치 홈페이지' in body, 'homepage link row present')
    check('이메일' in body and 'bellarich7@naver.com' in body, 'email row present')

    # contact rows order and content
    rows = pg.evaluate("""() => [...document.querySelectorAll('.info__row')].map(a => ({
        k: a.querySelector('.info__k').textContent.trim(),
        v: a.querySelector('.info__v').textContent.trim(),
        href: a.getAttribute('href'),
        h: +a.getBoundingClientRect().height.toFixed(1)}))""")
    print('rows', json.dumps(rows, ensure_ascii=False))
    order_k = [r['k'] for r in rows]
    check(order_k == ['휴대전화', '이메일', '주소'], 'row order ' + ' > '.join(order_k))
    check(rows[0]['v'] == '010-5031-0789' and rows[0]['href'] == 'tel:+821050310789', 'primary phone row intact')
    check(rows[1]['v'] == 'bellarich7@naver.com' and rows[1]['href'] == 'mailto:bellarich7@naver.com', 'email row value/link')
    check(all(r['h'] >= 68 for r in rows), 'contact rows >= 68px %s' % [r['h'] for r in rows])

    # 위계 균형: 연락처 블록(.info) 과 링크 4줄(.links) 높이가 반반 (±12px), 값>라벨 유지
    blocks = pg.evaluate("""() => { const f=s=>document.querySelector(s).getBoundingClientRect();
        const i=f('.info'), l=f('.links');
        return {info:+i.height.toFixed(1), links:+l.height.toFixed(1),
                infoTop:+i.top.toFixed(1), linkTop:+l.top.toFixed(1),
                rowH:f('.info__row').height, lkH:f('.lk').height,
                v:parseFloat(getComputedStyle(document.querySelector('.info__v')).fontSize),
                k:parseFloat(getComputedStyle(document.querySelector('.info__k')).fontSize),
                lt:parseFloat(getComputedStyle(document.querySelector('.lk__t')).fontSize)}; }""")
    print('blocks', blocks)
    check(abs(blocks['info'] - blocks['links']) <= 12,
          'info %.0f ≈ links %.0f (±12)' % (blocks['info'], blocks['links']))
    check(52 <= blocks['lkH'] <= 60, 'link row height %.0f in 52~60' % blocks['lkH'])
    check(68 <= blocks['rowH'] <= 74, 'contact row height %.0f in 68~74' % blocks['rowH'])
    check(blocks['v'] > blocks['k'] + 2, 'value font %.1f > label %.1f' % (blocks['v'], blocks['k']))
    check(blocks['lt'] >= 13.5, 'link label font %.1f >= 13.5' % blocks['lt'])

    # 히어로: 사진 캔버스 비율 = 스테이지 비율 → 크롭 없음, 페이지 배경 = 캔버스 가장자리 회색
    hero = pg.evaluate("""() => { const s=document.querySelector('.hero__stage'), i=document.querySelector('.hero__photo img');
        const r=s.getBoundingClientRect(); const cs=getComputedStyle(s);
        return {stageAspect:+(r.width/r.height).toFixed(3), imgAspect:+(i.naturalWidth/i.naturalHeight).toFixed(3),
                bg:cs.backgroundColor, pageBg:getComputedStyle(document.body).backgroundColor,
                light:document.querySelectorAll('.hero__light').length}; }""")
    print('hero', hero)
    check(abs(hero['stageAspect'] - hero['imgAspect']) < 0.01,
          'stage aspect %.3f = canvas %.3f (no crop)' % (hero['stageAspect'], hero['imgAspect']))
    check(hero['light'] == 0, 'no scrim/overlay element over the photo')
    diff = pg.evaluate("""() => { const s=getComputedStyle(document.querySelector('.hero__stage')).backgroundColor.match(/\\d+/g).map(Number);
        const p=getComputedStyle(document.body).backgroundColor.match(/\\d+/g).map(Number);
        return [Math.abs(s[0]-p[0]),Math.abs(s[1]-p[1]),Math.abs(s[2]-p[2])]; }""")
    check(max(diff) <= 2, 'stage bg = page bg %s' % diff)

    # 로고: 'Bella' 글자색과 스카이라인 블록색이 달라야 읽힘 (대비 7:1 이상)
    logo = pg.evaluate("""() => { const el=document.querySelector('.br-logo'); const cs=getComputedStyle(el);
        const blk=cs.getPropertyValue('--br-blk').trim(), letr=cs.getPropertyValue('--br-let').trim();
        const rgb=h=>{h=h.replace('#','');return [0,2,4].map(i=>parseInt(h.substr(i,2),16)/255);};
        const lum=h=>{const c=rgb(h).map(v=>v<=0.03928?v/12.92:Math.pow((v+0.055)/1.055,2.4));return 0.2126*c[0]+0.7152*c[1]+0.0722*c[2];};
        const a=lum(blk),b=lum(letr); const cr=(Math.max(a,b)+0.05)/(Math.min(a,b)+0.05);
        return {blk,let:letr,cr:+cr.toFixed(1)}; }""")
    print('logo', logo)
    check(logo['cr'] >= 7, "logo 'Bella' cream vs block contrast %.1f:1" % logo['cr'])

    # link rows have no description lines
    lkd = pg.evaluate("() => document.querySelectorAll('.lk__d').length")
    check(lkd == 0, 'link sub-descriptions removed (got %d)' % lkd)
    lkh = pg.evaluate("() => [...document.querySelectorAll('.lk')].map(a => Math.round(a.getBoundingClientRect().height))")
    lkfs = pg.evaluate("() => [...document.querySelectorAll('.lk__t')].map(a => parseFloat(getComputedStyle(a).fontSize))")
    print('lk rows height', lkh, 'title px', lkfs)

    # sns row: three items on one line
    sns = pg.evaluate("""() => { const r=[...document.querySelectorAll('.sns__a')].map(a=>a.getBoundingClientRect());
        return {n:r.length, sameLine: Math.max(...r.map(x=>x.top)) - Math.min(...r.map(x=>x.top)) < 2,
                minH: Math.min(...r.map(x=>x.height)), y:r[0].top}; }""")
    check(sns['n'] == 3 and sns['sameLine'], 'three sns links on one row')
    check(sns['minH'] >= 44, 'sns tap height %.0f >= 44' % sns['minH'])

    # external links safe
    ext = pg.evaluate("() => [...document.querySelectorAll('a[href^=\"https://\"]')].every(a => a.target==='_blank' && (a.rel||'').includes('noopener'))")
    check(ext, 'external links target=_blank + rel=noopener')

    # vCard
    with pg.expect_download() as dl_info:
        pg.click('#saveCard')
    dl = dl_info.value
    content = open(dl.path(), encoding='utf-8').read()
    print('--- vcf ---'); print(content); print('filename:', dl.suggested_filename)
    for needle in ['BEGIN:VCARD', 'FN:김자영', 'ORG:벨라리치(주)', 'TITLE:대표', '+82-10-5031-0789',
                   'bellarich7@naver.com', 'https://bellarich.co.kr', '이화여대1길 38, 201-51호', 'END:VCARD']:
        check(needle in content, 'vCard has ' + needle)
    check(content.count('TEL') == 1, 'vCard has exactly one TEL (got %d)' % content.count('TEL'))
    check(content.count('EMAIL') == 1, 'vCard has exactly one EMAIL (got %d)' % content.count('EMAIL'))
    check('4825' not in content, 'vCard has no 5383 number')

    # share
    pg.evaluate("() => { navigator.share = undefined; }")
    pg.click('#shareCard')
    pg.wait_for_timeout(500)
    toast = pg.inner_text('#toast')
    clip = pg.evaluate("() => navigator.clipboard.readText().catch(e => 'ERR:'+e.message)")
    check('복사' in toast or clip == 'https://bellarich.co.kr/card/', 'share copies the card URL (toast=%s clip=%s)' % (toast, clip))

    # image + fonts
    img = pg.evaluate("() => { const i=document.querySelector('.hero__photo img'); return {w:i.naturalWidth,h:i.naturalHeight,complete:i.complete}; }")
    check(img['complete'] and img['w'] >= 300, 'portrait loaded %sx%s' % (img['w'], img['h']))
    check(pg.evaluate("() => document.fonts.check('600 14px \"Pretendard Variable\"')"), 'Pretendard loaded')

    # tap targets
    small = pg.evaluate("""() => [...document.querySelectorAll('a,button')].filter(e => !e.closest('.foot__ct')).filter(e => {
        const r=e.getBoundingClientRect(); return r.width>0 && (r.height < 40 || r.width < 24); })
        .map(e => (e.textContent||'').trim().slice(0,18)+':'+Math.round(e.getBoundingClientRect().height))""")
    check(len(small) == 0, 'tap targets >= 40px %s' % small)

    # first screen: four contact rows fully visible in 390x844
    first = pg.evaluate("""() => { const rows=[...document.querySelectorAll('.info__row')];
        const last=rows[rows.length-1].getBoundingClientRect();
        const box=document.querySelector('.idbox').getBoundingClientRect();
        return {rows:rows.length, lastBottom:+last.bottom.toFixed(1), boxBottom:+box.bottom.toFixed(1), vh:innerHeight}; }""")
    check(first['rows'] == 3, 'three contact rows')
    check(first['lastBottom'] <= first['vh'], 'all three contact rows inside the first screen (%.0f <= %.0f)' % (first['lastBottom'], first['vh']))

    # a11y-ish contrast sample: read computed colours
    col = pg.evaluate("""() => { const g=s=>getComputedStyle(document.querySelector(s)).color;
        return {label:g('.info__k'), value:g('.info__v'), lkt:g('.lk__t'), foot:g('.foot__ad')}; }""")
    print('colours', col)

    check(not errors, 'console errors 0 %s' % errors)
    check(not failed_req, 'failed requests 0 %s' % failed_req)
    check(not bad_status, 'no 4xx/5xx %s' % bad_status)
    pg.screenshot(path=OUT + PFX + '-toast.png')
    ctx.close()
    b.close()

print('FAILURES:', len(fails))
for f in fails:
    print(' -', f)
sys.exit(1 if fails else 0)
