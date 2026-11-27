#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extracts the BellaRich logo (building-silhouette wordmark) from the corporate
deck PDF as a clean SVG, and writes it into assets/logo.svg (+ a widget snippet).

The PDF draws the logo with plain filled paths, so the result is true vector:
  * group blk  : the skyline block (navy)
  * group let  : "Bella" (white, knocked out of the block)
  * group gold : "Rich" (gold)
Everything else is transparent, so on a navy surface the block disappears and
the mark reads as white + gold, exactly as on the deck's cover.

Usage:  python3 make_logo.py
"""
import os
import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(HERE, '..', 'attachments', '2026-11-23',
                   '3865132156272105472-6cf2e5c3525d4289a66b24d3dc6a4441.pdf')
OUT_SVG = os.path.join(HERE, 'assets', 'logo.svg')
OUT_SYMBOL = os.path.join(HERE, 'assets', 'logo-symbol.html')

PAGE = 7                 # page 8 of the deck (0-based)
REGION = (20, 725, 275, 810)
NAVY = '#0B1933'
WHITE = '#FFFFFF'
GOLD = '#E4B477'


def num(v):
    s = ('%.2f' % v).rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s


def path_d(items):
    """PDF path items -> SVG path data (sub-paths detected by point jumps)."""
    d = []
    cur = None

    def move_if_needed(p):
        nonlocal cur
        if cur is None or abs(p.x - cur.x) > 0.01 or abs(p.y - cur.y) > 0.01:
            d.append('M%s %s' % (num(p.x), num(p.y)))

    for it in items:
        op = it[0]
        pts = it[1:]
        if op == 're':
            r = pts[0]
            d.append('M%s %sH%sV%sH%sZ' % (num(r.x0), num(r.y0), num(r.x1),
                                           num(r.y1), num(r.x0)))
            cur = pymupdf.Point(r.x0, r.y0)
            continue
        if op == 'qu':
            q = pts[0]
            move_if_needed(q.ul)
            d.append('Q%s %s %s %sQ%s %s %s %sZ' % (
                num(q.ul.x), num(q.ul.y), num(q.ur.x), num(q.ur.y),
                num(q.ur.x), num(q.ur.y), num(q.lr.x), num(q.lr.y)))
            cur = q.ul
            continue
        move_if_needed(pts[0])
        if op == 'l':
            d.append('L%s %s' % (num(pts[1].x), num(pts[1].y)))
            cur = pts[1]
        elif op == 'c':
            d.append('C%s %s %s %s %s %s' % tuple(
                num(p) for p in (pts[1].x, pts[1].y, pts[2].x, pts[2].y,
                                 pts[3].x, pts[3].y)))
            cur = pts[3]
    d.append('Z')
    return ''.join(d)


def main():
    doc = pymupdf.open(PDF)
    page = doc[PAGE]
    x0, y0, x1, y1 = REGION

    groups = {'blk': [], 'let': [], 'gold': []}
    for g in page.get_drawings():
        r = g['rect']
        if not (r.x0 >= x0 - 6 and r.y0 >= y0 - 6 and r.x1 <= x1 + 6 and r.y1 <= y1 + 6):
            continue
        f = g['fill']
        if not f:
            continue
        if max(f) < 0.5:
            key = 'blk'
        elif min(f) > 0.9:
            key = 'let'
        else:
            key = 'gold'
        groups[key].append(path_d(g['items']))

    # bounding box of every shape, for the viewBox
    xs, ys = [], []
    for g in page.get_drawings():
        r = g['rect']
        if not (r.x0 >= x0 - 6 and r.y0 >= y0 - 6 and r.x1 <= x1 + 6 and r.y1 <= y1 + 6):
            continue
        xs += [r.x0, r.x1]
        ys += [r.y0, r.y1]
    bx0, by0, bx1, by1 = min(xs), min(ys), max(xs), max(ys)
    w, h = bx1 - bx0, by1 - by0

    parts = []
    parts.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %.2f %.2f" '
                 'role="img" aria-label="벨라리치 BellaRich">' % (w, h))
    for key, color in (('blk', NAVY), ('let', WHITE), ('gold', GOLD)):
        if not groups[key]:
            continue
        parts.append('<g fill="%s">' % color)
        for d in groups[key]:
            parts.append('<path d="%s"/>' % d)
        parts.append('</g>')
    parts.append('</svg>')
    svg = ''.join(parts)
    # shift everything so the drawing starts at 0,0
    svg = svg.replace('>', '><', 1)  # no-op guard
    svg = svg.replace('viewBox="0 0', 'viewBox="0 0', 1)
    body = ''.join(parts[1:-1])
    body = ('<g transform="translate(%s %s)">%s</g>'
            % (num(-bx0), num(-by0), body))
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %.2f %.2f" '
           'width="%.2f" height="%.2f" role="img" aria-label="벨라리치 BellaRich">'
           '%s</svg>' % (w, h, w, h, body))

    os.makedirs(os.path.dirname(OUT_SVG), exist_ok=True)
    with open(OUT_SVG, 'w', encoding='utf-8') as f:
        f.write(svg)

    # inline sprite: the three colour groups become CSS custom properties so a
    # single definition can serve the navy hero, the sticky bar and the footer
    sym = ('<g id="brLogo">%s</g>' % body)\
        .replace('fill="%s"' % NAVY, 'fill="var(--br-blk,%s)"' % NAVY)\
        .replace('fill="%s"' % WHITE, 'fill="var(--br-let,%s)"' % WHITE)\
        .replace('fill="%s"' % GOLD, 'fill="var(--br-gold,%s)"' % GOLD)
    with open(OUT_SYMBOL, 'w', encoding='utf-8') as f:
        f.write(sym)

    print('wrote', OUT_SVG, len(svg), 'bytes', 'viewBox %.2f x %.2f' % (w, h))
    print('wrote', OUT_SYMBOL, len(sym), 'bytes')
    for k, v in groups.items():
        print(' ', k, len(v), 'paths')


if __name__ == '__main__':
    main()
