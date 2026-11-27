#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Live verification: hero geometry, contact buttons, video card link, console/network health."""
import json, sys
from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else 'https://bellarich7.github.io/?v=1125e'
PREFIX = sys.argv[2] if len(sys.argv) > 2 else 'LIVE'

HERO = """() => {
  const R = el => { if(!el) return null; const r = el.getBoundingClientRect();
    return {x:Math.round(r.left),y:Math.round(r.top),w:Math.round(r.width),h:Math.round(r.height)}; };
  const eb = document.querySelector('.hero__eyebrow');
  const tn = [...eb.childNodes].find(n => n.nodeType === 3);
  const rg = document.createRange(); rg.selectNodeContents(tn);
  const lines = [...rg.getClientRects()].map(r => [Math.round(r.left), Math.round(r.top), Math.round(r.width)]);
  const hero = document.querySelector('.hero');
  const cred = document.querySelector('.hero__cred');
  const h1 = document.querySelector('.hero h1');
  return {vh: window.innerHeight, vw: document.documentElement.clientWidth,
    navH: Math.round(document.querySelector('.nav').getBoundingClientRect().height),
    logo: R(document.querySelector('.hero__brand .br-logo')),
    eb: R(eb), ebLines: lines.length, lines,
    h1: R(h1), gapEbH1: Math.round(h1.getBoundingClientRect().top - eb.getBoundingClientRect().bottom),
    brandHairline: getComputedStyle(document.querySelector('.hero__brand'), '::after').width,
    ebDash: getComputedStyle(eb, '::before').width,
    credBottom: Math.round(cred.getBoundingClientRect().bottom),
    heroH: Math.round(hero.getBoundingClientRect().height),
    scrollW: document.documentElement.scrollWidth};
}"""

CONTACT = """() => [...document.querySelectorAll('.contact__acts a')].map(a => {
  const r = a.getBoundingClientRect();
  return {text: a.textContent.trim().replace(/\\s+/g,' '), href: a.getAttribute('href'),
          w: Math.round(r.width), h: Math.round(r.height), y: Math.round(r.top),
          style: a.className};
})"""

VIDEO = """() => {
  const a = document.querySelector('.video-card__thumb');
  return {tag: a.tagName, href: a.getAttribute('href'), target: a.getAttribute('target'),
          rel: a.getAttribute('rel'), play: !!document.querySelector('.video-card__play'),
          cap: document.querySelector('.video-card__yt').getAttribute('href'),
          iframe: !!document.querySelector('iframe'), fallback: !!document.getElementById('videoFallback'),
          thumbBytes: getComputedStyle(a).backgroundImage.length};
}"""

with sync_playwright() as p:
    b = p.chromium.launch()
    out = {}
    for label, vp, dsf in (('pc1440', {'width': 1440, 'height': 900}, 1),
                           ('pc1366', {'width': 1366, 'height': 768}, 1),
                           ('m390', {'width': 390, 'height': 844}, 2)):
        ctx = b.new_context(viewport=vp, device_scale_factor=dsf)
        pg = ctx.new_page()
        errs, failed, ext = [], [], []
        pg.on('pageerror', lambda e: errs.append('pageerror: ' + str(e)))
        pg.on('console', lambda m: errs.append('console.error: ' + m.text) if m.type == 'error' else None)
        pg.on('requestfailed', lambda r: failed.append(r.url[:100] + ' :: ' + str(r.failure)))
        pg.on('request', lambda r: ext.append(r.url[:90]) if ('youtu' in r.url or 'ytimg' in r.url) else None)
        pg.goto(URL, wait_until='networkidle', timeout=45000)
        pg.wait_for_timeout(900)
        d = {'hero': pg.evaluate(HERO)}
        pg.screenshot(path=f'/workspace/bellarich-site/shots/{PREFIX}-{label}-hero.png')
        d['contact'] = pg.evaluate(CONTACT)
        pg.evaluate("document.querySelector('#contact').scrollIntoView()")
        pg.wait_for_timeout(600)
        pg.screenshot(path=f'/workspace/bellarich-site/shots/{PREFIX}-{label}-contact.png')
        pg.evaluate("document.querySelector('#videoCard').scrollIntoView({block:'center'})")
        pg.wait_for_timeout(600)
        pg.screenshot(path=f'/workspace/bellarich-site/shots/{PREFIX}-{label}-video.png')
        d['video'] = pg.evaluate(VIDEO)
        d['youtube_requests_before_click'] = ext
        d['page_errors'] = errs
        d['failed_requests'] = failed
        out[label] = d
        ctx.close()
    b.close()
print(json.dumps(out, ensure_ascii=False, indent=1))
