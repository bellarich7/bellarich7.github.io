#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Career italic variants A/B/C — same block, three screenshots at 1440."""
import os
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
URL = 'file://' + os.path.join(ROOT, 'index.html')
OUT = os.path.join(ROOT, 'shots')

VARIANTS = [
    ('A', ':root{--career-style:italic;--career-past-style:normal}'),
    ('B', ':root{--career-style:normal;--career-past-style:italic}'),
    ('C', ':root{--career-style:normal;--career-past-style:normal}'),
]

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width': 1440, 'height': 900})
    pg = ctx.new_page()
    pg.goto(URL, wait_until='load'); pg.wait_for_timeout(1800)
    # reveal all so the block is not faded
    pg.evaluate("document.querySelectorAll('.rv').forEach(e=>e.classList.add('in'))")
    pg.wait_for_timeout(600)
    for key, css in VARIANTS:
        handle = pg.add_style_tag(content=css)
        pg.wait_for_timeout(300)
        el = pg.query_selector('.career')
        el.scroll_into_view_if_needed(); pg.wait_for_timeout(500)
        el.screenshot(path=f'{OUT}/career-{key}.png')
        print(f'career-{key}.png', pg.evaluate("""() => {
            const li = document.querySelector('.career li');
            const past = document.querySelector('.career__col--past li');
            return {cur: getComputedStyle(li).fontStyle, past: getComputedStyle(past).fontStyle,
                    family: getComputedStyle(li).fontFamily.split(',')[0]};
        }"""))
        pg.evaluate("(h)=>h.remove()", handle)
    b.close()
