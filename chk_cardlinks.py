#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""카드 하단 '자세히 · 상담 신청' 줄 점검 — 390/1440 에서 보임·한 줄·44px 터치·클릭 동작.
   python3 chk_cardlinks.py [url] [tag]
"""
import os, sys, json
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
URL = sys.argv[1] if len(sys.argv) > 1 else 'file://' + os.path.join(ROOT, 'index.html')
TAG = sys.argv[2] if len(sys.argv) > 2 else 'local'
OUT = os.path.join(ROOT, 'shots')
os.makedirs(OUT, exist_ok=True)

PROBE = """() => {
  const rows = [];
  document.querySelectorAll('.panel:not([hidden]) .card[data-plan], .panel:not([hidden]) .card[data-href]').forEach(card => {
    const panel = card.closest('.panel');
    const act = card.querySelector('.card__act');
    const more = act && act.querySelector('.card__more');
    const apply = act && act.querySelector('a.card__apply');
    const h3 = card.querySelector('h3');
    if (!act || !more || !apply) { rows.push({t: h3 ? h3.textContent.trim() : '?', miss: true}); return; }
    const r1 = more.getBoundingClientRect(), r2 = apply.getBoundingClientRect(), ra = act.getBoundingClientRect();
    rows.push({
      t: h3.textContent.trim().replace(/\\s+/g,' '),
      panel: panel.id,
      moreTag: more.tagName.toLowerCase(),
      moreH: +r1.height.toFixed(1),
      applyH: +r2.height.toFixed(1),
      applyW: +r2.width.toFixed(1),
      sameRow: Math.abs((r1.top + r1.height/2) - (r2.top + r2.height/2)) < 3,
      rowH: +ra.height.toFixed(1),
      applyHref: apply.getAttribute('href') || '',
      dataContact: apply.hasAttribute('data-contact-link'),
      moreHref: (more.getAttribute('href') || ''),
      moreDataPlan: !!more.closest('[data-plan]'),
    });
  });
  return rows;
}"""

with sync_playwright() as p:
    b = p.chromium.launch()
    for w, h in [(1440, 900), (390, 844)]:
        ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2 if w == 390 else 1)
        pg = ctx.new_page()
        errs = []
        pg.on('pageerror', lambda e: errs.append('pageerror: ' + str(e)))
        pg.on('console', lambda m: errs.append('console: ' + m.text) if m.type == 'error' else None)
        failed = []
        pg.on('requestfailed', lambda r: failed.append(r.url))
        pg.goto(URL, wait_until='load')
        pg.wait_for_timeout(900)

        allrows = []
        # 세 탭을 차례로 열어 15개 카드를 모두 확인
        for key in ['life', 'suc', 'fin']:
            pg.evaluate("""(k)=>{ const t=document.getElementById('tab-'+k); if(t) t.click(); }""", key)
            pg.wait_for_timeout(250)
            allrows += pg.evaluate(PROBE)

        overflow = pg.evaluate("""()=>{const de=document.documentElement;
            const bad=[]; document.querySelectorAll('.panel .card').forEach(c=>{
              const r=c.getBoundingClientRect(); if(r.right>de.clientWidth+1||r.left<-1) bad.push(c.querySelector('h3').textContent.trim());});
            return {scrollW:de.scrollWidth, vw:de.clientWidth, bad};}""")
        minh = min([r.get('moreH', 0) for r in allrows] + [r.get('applyH', 0) for r in allrows])
        print('--- width %d ---' % w)
        print('cards:', len(allrows), 'missing:', [r for r in allrows if r.get('miss')])
        print('all same row:', all(r.get('sameRow') for r in allrows))
        print('min touch height:', minh)
        print('href set (data-contact-link):', all('docs.google.com/forms' in r.get('applyHref', '') for r in allrows),
              all(r.get('dataContact') for r in allrows))
        print('detail link on tax card:', [ (r['t'], r['moreTag'], r['moreHref']) for r in allrows if '절세' in r['t']])
        print('overflow:', json.dumps(overflow, ensure_ascii=False))
        print('console errors:', errs, '| failed requests:', failed)

        # 스크린샷: 카드 그리드 (플랜 탭별) + 확대
        for key in ['life', 'suc', 'fin']:
            pg.evaluate("""(k)=>{ const t=document.getElementById('tab-'+k); if(t) t.click();
                const s=document.getElementById('solutions'); window.scrollTo(0, s.getBoundingClientRect().top+window.scrollY-60);}""", key)
            pg.wait_for_timeout(500)
            el = pg.query_selector('#panel-' + key)
            path = os.path.join(OUT, 'cards-%s-%s-%d.png' % (TAG, key, w))
            el.screenshot(path=path)
            print('shot', path)
        ctx.close()
    b.close()
