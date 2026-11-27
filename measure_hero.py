#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dump hero column boxes at the six target viewports."""
import os, json
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
URL = 'file://' + os.path.join(ROOT, 'index.html')
SIZES = [(1440, 900), (1366, 768), (1280, 800), (1150, 800), (1024, 768), (1024, 900), (820, 1180), (390, 844)]

SELS = ['.hero__brand', '.hero__eyebrow', '.hero h1', '.hero__sub', '.hero__actions',
        '.hero__facts', '.hero__cred', '.hero__cred .cred__eyebrow', '.hero__cred .cred__name',
        '.hero__cred .cred__role', '.hero__cred .cred__quote', '.hero__cred .cred__chips']

with sync_playwright() as p:
    b = p.chromium.launch()
    for w, h in SIZES:
        ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=1)
        pg = ctx.new_page()
        pg.goto(URL, wait_until='load')
        pg.wait_for_timeout(800)
        d = pg.evaluate("""(sels) => {
          const out = {vh: innerHeight, vw: document.documentElement.clientWidth,
                       scrollW: document.documentElement.scrollWidth, items: []};
          for (const s of sels) {
            const el = document.querySelector(s);
            if (!el) { out.items.push([s, null]); continue; }
            const r = el.getBoundingClientRect();
            out.items.push([s, {t: Math.round(r.top), b: Math.round(r.bottom), h: Math.round(r.height),
                                w: Math.round(r.width), l: Math.round(r.left), rt: Math.round(r.right)}]);
          }
          return out;
        }""", SELS)
        print(f'\n=== {w}x{h} vh={d["vh"]} vw={d["vw"]} scrollW={d["scrollW"]}')
        for s, r in d['items']:
            print(' ', s, r)
        ctx.close()
    b.close()
