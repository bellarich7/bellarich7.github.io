#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""6차 색 대비 보고용: 탭·패널 라벨·카드 본문의 전/후 명암비(WCAG)."""
import json

def lin(c):
    c = c / 255
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

def L(rgb):
    return 0.2126 * lin(rgb[0]) + 0.7152 * lin(rgb[1]) + 0.0722 * lin(rgb[2])

def ratio(a, b):
    hi, lo = sorted([L(a), L(b)], reverse=True)
    return round((hi + 0.05) / (lo + 0.05), 2)

def mix(fg, bg):
    a = fg[3] if len(fg) > 3 else 1.0
    return (a * fg[0] + (1 - a) * bg[0], a * fg[1] + (1 - a) * bg[1], a * fg[2] + (1 - a) * bg[2])

def h(x):
    x = x.lstrip('#')
    return tuple(int(x[i:i + 2], 16) for i in (0, 2, 4))

IVORY, PAPER = h('#FAF8F5'), h('#F4F0E9')
NAVY, AMBER, SAGE = h('#14243F'), h('#7F5423'), h('#455E4D')
DEEP = h('#0B1933')

rows = []
def add(label, fg, bg, before=None):
    after = ratio(fg, bg)
    rows.append({'item': label, 'after': after, 'before': before,
                 'delta': None if before is None else round(after - before, 2)})

# --- solution card text (on each plan tone) ---
old_text, new_text = (245, 241, 233, .96), h('#FBF7EE')
for name, bg in (('남색 카드', NAVY), ('앰버 카드', AMBER), ('세이지 카드', SAGE)):
    add(f'{name} 본문', new_text, bg, ratio(mix(old_text, bg), bg))
    add(f'{name} 제목', h('#FFFFFF'), bg, ratio(h('#FBF8F1'), bg))
old_nums = {'남색 카드': '#E3CDA9', '앰버 카드': '#F0DFC0', '세이지 카드': '#DFE7D6'}
new_nums = {'남색 카드': '#F2E3C8', '앰버 카드': '#FAF0DC', '세이지 카드': '#EDF3E8'}
for name, bg in (('남색 카드', NAVY), ('앰버 카드', AMBER), ('세이지 카드', SAGE)):
    add(f'{name} 번호', h(new_nums[name]), bg, ratio(h(old_nums[name]), bg))
old_more = {'남색 카드': '#D9C1A0', '앰버 카드': '#F0D9B6', '세이지 카드': '#DDE8DC'}
new_more = {'남색 카드': '#EBD6B7', '앰버 카드': '#F7E7CB', '세이지 카드': '#EDF3E8'}
for name, bg in (('남색 카드', NAVY), ('앰버 카드', AMBER), ('세이지 카드', SAGE)):
    add(f'{name} 자세히', h(new_more[name]), bg, ratio(h(old_more[name]), bg))

# --- tabs ---
add('탭 라벨(비활성)', h('#1B2331'), PAPER, ratio(h('#1B2331'), PAPER))   # before was --muted, same hex but 400
add('탭 라벨(활성)', h('#F7F3EA'), DEEP, ratio(h('#0F1B30'), IVORY))
add('탭 배지(비활성)', h('#7A5A31'), PAPER, ratio(h('#9A7B57'), IVORY))
add('탭 배지(활성)', h('#D9C1A0'), DEEP, ratio(h('#9A7B57'), IVORY))

# --- panel note / lead ---
add('panel__note', h('#0F1B30'), IVORY, ratio(h('#3A4351'), IVORY))

# --- CTA card ---
add('CTA 카드 본문', h('#2B3A54'), h('#F2E9DA'))
add('CTA 카드 제목', h('#14243F'), h('#F2E9DA'))
add('CTA 카드 번호·상담신청', h('#7A5A31'), h('#F2E9DA'))

for r in rows:
    print(f"{r['item']:<18} after {r['after']:>6}   before {str(r['before']):>6}   Δ {r['delta']}")
print()
print('min after:', min(r['after'] for r in rows))
