#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check books section cover links + caption link row after build."""
import os, json, sys
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
URL = sys.argv[1] if len(sys.argv) > 1 else 'file://' + os.path.join(ROOT, 'index.html')
TAG = sys.argv[2] if len(sys.argv) > 2 else 'local'
OUT = os.path.join(ROOT, 'shots')
os.makedirs(OUT, exist_ok=True)

JS = """() => {
  const books = [...document.querySelectorAll('.book')].map(fig => {
    const c = fig.querySelector('.book__cover');
    const links = [...fig.querySelectorAll('.book__links a')].map(a => ({
      text: a.textContent.trim(), href: a.getAttribute('href'),
      target: a.getAttribute('target'), rel: a.getAttribute('rel')
    }));
    const row = fig.querySelector('.book__links');
    const rr = row ? row.getBoundingClientRect() : null;
    const lh = row ? parseFloat(getComputedStyle(row).fontSize) * 1.5 : 0;
    const spans = row ? [...row.children].map(x => { const b = x.getBoundingClientRect(); return [x.tagName, Math.round(b.left), Math.round(b.right), Math.round(b.top)]; }) : [];
    return {
      coverTag: c ? c.tagName : null,
      coverHref: c ? c.getAttribute('href') : null,
      coverTarget: c ? c.getAttribute('target') : null,
      coverRel: c ? c.getAttribute('rel') : null,
      ariaLabel: c ? c.getAttribute('aria-label') : null,
      imgAlt: fig.querySelector('img') ? fig.querySelector('img').alt : null,
      display: c ? getComputedStyle(c).display : null,
      links,
      rowW: rr ? Math.round(rr.width) : null,
      rowH: rr ? Math.round(rr.height) : null,
      rowOneLine: rr ? rr.height < lh * 1.6 : null,
      linksOverflow: rr ? row.scrollWidth > Math.ceil(rr.width) + 1 : null,
      children: spans
    };
  });
  const de = document.documentElement;
  return {
    vw: de.clientWidth, scrollW: de.scrollWidth,
    books: books,
    coverCount: document.querySelectorAll('a.book__cover').length,
    captionLinkCount: document.querySelectorAll('.book__links a').length,
    spansInsideCovers: document.querySelectorAll('span.book__cover').length
  };
}"""


def snap(pg, name, full_section=True):
    el = pg.query_selector('.books')
    path = os.path.join(OUT, name)
    if full_section and el:
        el.scroll_into_view_if_needed()
        pg.wait_for_timeout(500)
        el.screenshot(path=path)
    else:
        path = os.path.join(OUT, name)
        pg.screenshot(path=path)
    return path


with sync_playwright() as p:
    b = p.chromium.launch()
    for w, h in ((390, 844), (1440, 900)):
        ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2)
        pg = ctx.new_page()
        errs, failed = [], []
        pg.on('pageerror', lambda e: errs.append('pageerror: ' + str(e)))
        pg.on('console', lambda m: errs.append('console: ' + m.text) if m.type == 'error' else None)
        pg.on('requestfailed', lambda r: failed.append(r.url[:120]))
        pg.goto(URL, wait_until='load')
        pg.wait_for_timeout(1200)
        d = pg.evaluate(JS)
        print('==', TAG, w, json.dumps(d, ensure_ascii=False))
        print('   errors', errs, 'failed', failed)
        print('   shot', snap(pg, f'booklinks-{TAG}-{w}.png'))
        ctx.close()
    b.close()
