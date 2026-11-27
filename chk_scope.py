#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""메인 페이지 변경 범위 확인 — 이전 배포본(HEAD)과 새 빌드를 영역별로 비교.
   기대: .cards 안의 카드(하단 액션 줄·태그)만 다르고 나머지 영역은 완전히 동일.
"""
import re, json
from playwright.sync_api import sync_playwright

BEFORE = 'file:///workspace/tmp/plan-base/index-before.html'
AFTER = 'file:///workspace/bellarich-site/index.html'

EXTRACT = """() => {
  const norm = s => s.replace(/\\s+/g, ' ').trim();
  const out = {};
  const parts = {
    head: 'head',
    nav: 'header.nav',
    drawer: '#mobileMenu',
    hero: '.hero',
    about: '#about',
    band: '.band',
    philosophy: '#philosophy',
    solhead: '.sol__head',
    solhint: '.sol-hint',
    tabs: '.tabs',
    notes: '.panel .panel__note',
    sucblock: '.suc-block',
    cta_cards: '.cards .card--cta',
    contact: '#contact',
    footer: 'footer.footer',
    modal: '#modal'
  };
  for (const [k, sel] of Object.entries(parts)) {
    const nodes = [...document.querySelectorAll(sel)];
    out[k] = nodes.map(n => norm(n.outerHTML));
  }
  // 카드: 하단 액션 줄을 뺀 나머지가 같아야 함
  out.cards = [...document.querySelectorAll('.cards .card:not(.card--cta)')].map(c => {
    const clone = c.cloneNode(true);
    const act = clone.querySelector('.card__act');
    if (act) act.remove();
    const foot = [...clone.querySelectorAll('.card__more')].map(e => { e.remove(); });
    return {tag: c.tagName, key: c.dataset.plan || c.dataset.href || '',
            body: norm(clone.innerHTML)};
  });
  out.card_acts = [...document.querySelectorAll('.cards .card:not(.card--cta)')].map(c => {
    const a = c.querySelector('.card__act');
    return {key: c.dataset.plan || c.dataset.href || '',
            html: a ? norm(a.innerHTML) : null};
  });
  out.script = [norm(document.querySelector('script:not([src])') ? document.querySelector('script:not([src])').textContent : '')];
  return out;
}"""

with sync_playwright() as p:
    b = p.chromium.launch()
    res = {}
    for name, url in [('before', BEFORE), ('after', AFTER)]:
        ctx = b.new_context(viewport={'width': 1440, 'height': 900})
        pg = ctx.new_page()
        pg.goto(url, wait_until='load')
        pg.wait_for_timeout(500)
        res[name] = pg.evaluate(EXTRACT)
        ctx.close()
    b.close()

same, diff = [], []
for k in res['before']:
    if k in ('cards', 'card_acts'):
        continue
    if res['before'][k] == res['after'][k]:
        same.append(k)
    else:
        diff.append(k)
print('동일 영역:', same)
print('다른 영역:', diff)

# 다른 영역이 있으면 어디가 다른지 요약
for k in diff:
    a, c = res['before'][k], res['after'][k]
    print('---', k, 'nodes', len(a), len(c))
    for i, (x, y) in enumerate(zip(a, c)):
        if x != y:
            # 첫 차이 지점
            n = min(len(x), len(y))
            j = next((t for t in range(n) if x[t] != y[t]), n)
            print('  [%d] before: …%s' % (i, x[max(0, j-60):j+120]))
            print('  [%d] after : …%s' % (i, y[max(0, j-60):j+120]))

print('카드 수 before/after:', len(res['before']['cards']), len(res['after']['cards']))
bad = []
for a, c in zip(res['before']['cards'], res['after']['cards']):
    if a['body'] != c['body'] or a['key'] != c['key']:
        bad.append((a['key'], c['key']))
print('카드 본문/키가 달라진 카드:', bad if bad else '없음')
print('카드 태그 before:', sorted(set(x['tag'] for x in res['before']['cards'])),
      'after:', sorted(set(x['tag'] for x in res['after']['cards'])))
acts = res['after']['card_acts']
print('액션 줄 있는 카드:', sum(1 for x in acts if x['html']),
      '| 상담 신청 포함:', sum(1 for x in acts if x['html'] and '상담 신청' in x['html']),
      '| 자세히:', sum(1 for x in acts if x['html'] and '자세히' in x['html']))
print('액션 줄 예시:', acts[0]['html'][:220] if acts else None)
print('before 액션 줄:', [x['html'] for x in res['before']['card_acts']][:2])
