#!/usr/bin/env python3
"""Build bellarich-site/card/index.html from _card.src.html.

Inlines the Bella Rich logo SVG sprite and a base64 portrait so the page is one
self-contained file (the deploy repo's assets/ folder does not carry the portrait).
The hero canvas ratio and the studio-grey palette come from assets/card-hero.json,
so regenerating the portrait (make_card_hero.py) never needs a CSS edit.
"""
import base64
import json
import pathlib
import re

ROOT = pathlib.Path('/workspace/bellarich-site')
SRC = ROOT / 'card' / '_card.src.html'
OUT = ROOT / 'card' / 'index.html'
LOGO = ROOT / 'assets' / 'logo-symbol.html'
PHOTO = ROOT / 'assets' / 'card-hero.webp'
META = ROOT / 'assets' / 'card-hero.json'

html = SRC.read_text(encoding='utf-8')

logo = LOGO.read_text(encoding='utf-8').strip()
logo = re.sub(r'^<g id="brLogo">.*</g>$', lambda m: m.group(0), logo, flags=re.S)
assert 'id="brLogo"' in logo, 'logo sprite not found'

meta = json.loads(META.read_text(encoding='utf-8'))
cw, ch = meta['canvas']
b64 = base64.b64encode(PHOTO.read_bytes()).decode('ascii')
photo_uri = 'data:image/webp;base64,' + b64

html = html.replace('__LOGO__', logo)
html = html.replace('__CEOPHOTO__', photo_uri)
html = html.replace('__HERO_AR__', '%d / %d' % (cw, ch))
html = html.replace('__HERO_W__', str(cw))
html = html.replace('__HERO_H__', str(ch))
html = html.replace('__HERO_GREY__', meta['page_mid'])
html = html.replace('__HERO_TOP__', meta['page_top'])
html = html.replace('__HERO_BOT__', meta['page_bot'])

for ph in ('__LOGO__', '__CEOPHOTO__', '__HERO_AR__', '__HERO_W__', '__HERO_H__',
           '__HERO_GREY__', '__HERO_TOP__', '__HERO_BOT__'):
    assert ph not in html, 'placeholder left: ' + ph

OUT.write_text(html, encoding='utf-8')
print('wrote', OUT, len(html.encode('utf-8')), 'bytes; photo b64', len(b64),
      '; aspect', cw, '/', ch, '; grey', meta['page_mid'])
