#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Contrast check (WCAG) for the three solution card tones + capture card crops."""
import os, json
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
URL = 'file://' + os.path.join(ROOT, 'index.html')
OUT = os.path.join(ROOT, 'shots')

def lin(c):
    c = c / 255
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

def lum(rgb_text):
    r, g, b = rgb_text
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)

def ratio(fg, bg):
    a, b = sorted([lum(fg), lum(bg)], reverse=True)
    return round((a + 0.05) / (b + 0.05), 2)

def parse(s):
    # rgb(a) or rgba(...)
    s = s.strip()
    nums = s[s.index('(') + 1:s.index(')')].split(',')
    vals = [float(n) for n in nums]
    return vals

def mix(fg, bg):
    r, g, b = fg[0], fg[1], fg[2]
    a = fg[3] if len(fg) > 3 else 1.0
    return (a * r + (1 - a) * bg[0], a * g + (1 - a) * bg[1], a * b + (1 - a) * bg[2])

TABS = [('tab-life', 'panel-life', 'life'), ('tab-suc', 'panel-suc', 'suc'), ('tab-fin', 'panel-fin', 'fin')]

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width': 1440, 'height': 900})
    pg = ctx.new_page()
    pg.goto(URL, wait_until='load'); pg.wait_for_timeout(1500)
    out = {}
    for tab, panel, key in TABS:
        pg.evaluate("(t)=>document.getElementById(t).click()", tab)
        pg.wait_for_timeout(400)
        d = pg.evaluate("""(panel) => {
          const p = document.getElementById(panel);
          const c = p.querySelector('.card');
          const cs = getComputedStyle(c), h = c.querySelector('h3'), pp = c.querySelector('p'),
                no = c.querySelector('.card__no'), more = c.querySelector('.card__more');
          const g = (e) => { const s = getComputedStyle(e); return {color: s.color, size: s.fontSize, weight: s.fontWeight}; };
          return {bg: cs.backgroundColor, cards: p.querySelectorAll('.card').length,
                  cardBgs: [...p.querySelectorAll('.card')].map(x => getComputedStyle(x).backgroundColor),
                  h3: g(h), p: g(pp), no: g(no), more: g(more)};
        }""", panel)
        bg = parse(d['bg'])[:3]
        rows = []
        for label, key2 in (('제목 h3', 'h3'), ('본문 p', 'p'), ('번호', 'no'), ('더보기', 'more')):
            fg = parse(d[key2]['color'])
            eff = mix(fg, bg)
            rows.append({'el': label, 'color': d[key2]['color'], 'size': d[key2]['size'],
                         'ratio': ratio(eff, bg)})
        out[key] = {'bg': d['bg'], 'cards': d['cards'], 'uniqueCardBgs': sorted(set(d['cardBgs'])), 'text': rows}
        # crop one card (first) and the card grid for the report
        box = pg.evaluate("""(panel)=>{const p=document.getElementById(panel);
            const c=p.querySelector('.card'); const r=c.getBoundingClientRect();
            return {x:r.x,y:r.y,w:r.width,h:r.height};}""", panel)
        pg.evaluate("""(panel)=>{const p=document.getElementById(panel);
            p.scrollIntoView({block:'center'});}""", panel)
        pg.wait_for_timeout(500)
        el = pg.query_selector(f'#{panel} .card')
        el.screenshot(path=f'{OUT}/card-tone-{key}.png')
        grid = pg.query_selector(f'#{panel} .cards')
        grid.screenshot(path=f'{OUT}/card-grid-{key}.png')
    print(json.dumps(out, ensure_ascii=False, indent=1))
    b.close()
