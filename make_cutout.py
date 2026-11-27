#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the hero portrait cut-out (grey studio background -> RGBA) from
assets/_gen_beige.png and write assets/ceo-hero.webp.

Pipeline
 1. fit a smooth background model (2D quadratic per channel) on the border band
 2. silhouette = colour distance from that model, largest blob, holes filled
 3. alpha solved by linear unmixing inside a narrow band around the silhouette
 4. edge colour pulled in from the solid core so no studio grey is left to halo
 5. soft bottom fade so the cut-out melts into the navy hero

The source photo is 1022x1538, so the cut-out is built at that full resolution
(previously it was thrown away down to 765x1150, which is what made the portrait
soft on high-DPI PC screens).  Every pixel-radius / area threshold in the matte
below is expressed in "765-wide" units and multiplied by S, so the result is the
same matte as before — only with the detail the downscale used to destroy.

    python3 make_cutout.py
"""
import os
import sys
import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'assets', '_gen_beige.png')
OUT_PNG = os.path.join(HERE, 'assets', '_src_ceo-cutout-beige.png')
OUT_WEBP = os.path.join(HERE, 'assets', 'ceo-hero.webp')

# full resolution of the source portrait (2:3), no downscale
TARGET = (1022, 1538)
BASE_W = 765.0                # the width every tuned constant below was written for
S = TARGET[0] / BASE_W        # ~1.336
WEBP_QUALITY = int(os.environ.get('WEBP_Q', '95'))

NAVY = np.array([0x0B, 0x19, 0x33], np.float32)


def px(n):
    """A length written for the 765-wide matte, at the current resolution."""
    return max(1, int(round(n * S)))


def area(n):
    """An area written for the 765-wide matte, at the current resolution."""
    return int(round(n * S * S))


def load_square():
    im = cv2.imread(SRC, cv2.IMREAD_COLOR)          # BGR
    im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB).astype(np.float32)
    h, w, _ = im.shape
    want_h = int(round(w * TARGET[1] / TARGET[0]))
    if want_h <= h:
        top = max(0, (h - want_h) // 2)
        im = im[top:top + want_h]
    else:
        want_w = int(round(h * TARGET[0] / TARGET[1]))
        left = (w - want_w) // 2
        im = im[:, left:left + want_w]
    if im.shape[:2] != (TARGET[1], TARGET[0]):
        im = cv2.resize(im, TARGET, interpolation=cv2.INTER_AREA)
    return im


def background_model(im):
    """Smooth backdrop estimate by normalised convolution over background-like
    pixels (the studio backdrop has a soft vignette a polynomial misses)."""
    g = im.mean(2)
    chroma = im.max(2) - im.min(2)
    prior = ((chroma < 8) & (g > 95) & (g < 220)).astype(np.float32)
    m = prior.copy()
    sigma = 40 * S
    for _ in range(5):
        wsum = cv2.GaussianBlur(m, (0, 0), sigma)
        bg = cv2.GaussianBlur(im * m[..., None], (0, 0), sigma) / np.maximum(wsum, 1e-6)[..., None]
        d = np.linalg.norm(im - bg, axis=2)
        m = (prior > 0).astype(np.float32) * (d < 9)
    return bg.astype(np.float32)


def edge_colour(im, core, band=12):
    """Grow the solid core's colour outward (weighted blur inpaint)."""
    known = core.astype(np.float32)
    rgb = im.copy()
    for _ in range(px(band)):
        wsum = cv2.blur(known, (5, 5))
        mean = cv2.blur(rgb * known[..., None], (5, 5)) / np.maximum(wsum, 1e-6)[..., None]
        grow = (wsum > 0.02) & (known < 0.5)
        rgb[grow] = mean[grow]
        known = np.maximum(known, grow.astype(np.float32))
    return np.clip(rgb, 0, 255)


def silhouette(im, bg):
    h, w, _ = im.shape
    diff = np.linalg.norm(im - bg, axis=2)
    raw = (diff > 11).astype(np.uint8)
    raw = cv2.morphologyEx(raw, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    raw = cv2.morphologyEx(raw, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(raw, connectivity=8)
    if n > 1:
        big = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
        raw = (lab == big).astype(np.uint8)
    ff = raw.copy()
    ff[0, :] = ff[-1, :] = 0
    ff[:, 0] = ff[:, -1] = 0
    holes = np.zeros((h + 2, w + 2), np.uint8)
    cv2.floodFill(ff, holes, (0, 0), 1)
    hole = (1 - ff).astype(np.uint8)
    # only fill interior holes worth filling: thin background gaps between hair
    # strands must stay transparent or they show up as grey specks on the hero
    n2, lab2, st2, _ = cv2.connectedComponentsWithStats(hole, connectivity=4)
    big_hole = np.zeros_like(hole)
    for i in range(1, n2):
        x, y, ww, hh, ar = st2[i]
        if ar >= area(900) and min(ww, hh) >= px(20):
            big_hole[lab2 == i] = 1
    return raw | big_hole


def alpha_matte(im, bg):
    """Alpha by linear unmixing between the local backdrop and the subject colour."""
    solid = silhouette(im, bg)
    core = cv2.erode(solid, np.ones((5, 5), np.uint8), iterations=px(4))
    near = cv2.dilate(solid, np.ones((3, 3), np.uint8), iterations=px(2)).astype(bool)

    F = edge_colour(im, core, band=16)
    d = F - bg
    denom = (d * d).sum(2)
    proj = ((im - bg) * d).sum(2) / np.maximum(denom, 1e-6)

    a = np.where(denom > 120, np.clip(proj, 0, 1), 0.0).astype(np.float32)
    inner = cv2.erode(solid, np.ones((5, 5), np.uint8), iterations=px(3))
    a = np.maximum(a, inner.astype(np.float32))
    a[~near] = 0.0
    a = cv2.GaussianBlur(a, (0, 0), 0.5 * S)

    # drop isolated specks
    m = (a > 0.3).astype(np.uint8)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
    keep = np.zeros_like(m)
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] >= area(600):
            keep[lab == i] = 1
    keep = cv2.dilate(keep, np.ones((3, 3), np.uint8), iterations=px(1)).astype(bool)
    a[~keep] = 0.0
    a[a < 0.06] = 0.0
    return np.clip(a, 0, 1)


def edge_colour_out(im, alpha):
    """Final colour: semi-transparent pixels take the nearest solid colour."""
    solid = (alpha > 0.985).astype(np.float32)
    rgb = im.copy()
    for _ in range(px(14)):
        wsum = cv2.blur(solid, (5, 5))
        mean = cv2.blur(rgb * solid[..., None], (5, 5)) / np.maximum(wsum, 1e-6)[..., None]
        grow = (wsum > 0.02) & (solid < 0.5)
        rgb[grow] = mean[grow]
        solid = np.maximum(solid, grow.astype(np.float32))
    return np.clip(rgb, 0, 255)


def bottom_fade(alpha, frac=0.0):
    h, w = alpha.shape
    start = int(h * (1 - frac))
    t = np.linspace(0, 1, h - start)
    ramp = 1 - (t * t * (3 - 2 * t))          # smoothstep: no visible seam
    alpha[start:, :] *= ramp[:, None]
    return alpha


if __name__ == '__main__':
    im = load_square()
    bg = background_model(im)
    a = alpha_matte(im, bg)
    rgb = edge_colour_out(im, a)
    a = bottom_fade(a)   # frac=0 keeps the crop crisp at the hero's bottom edge

    out = np.dstack([rgb, a * 255]).astype(np.uint8)
    cv2.imwrite(OUT_PNG, cv2.cvtColor(out, cv2.COLOR_RGBA2BGRA))
    cv2.imwrite(OUT_WEBP, cv2.cvtColor(out, cv2.COLOR_RGBA2BGRA),
                [cv2.IMWRITE_WEBP_QUALITY, WEBP_QUALITY])
    print('target %dx%d  scale %.3f' % (TARGET[0], TARGET[1], S))
    print('coverage %.3f' % (a > 0.5).mean())
    print('written', OUT_PNG, OUT_WEBP)

    comp = rgb * a[..., None] + NAVY * (1 - a[..., None])
    cv2.imwrite(os.path.join(HERE, 'assets', '_preview_navy.jpg'),
                cv2.cvtColor(np.clip(comp, 0, 255).astype(np.uint8), cv2.COLOR_RGB2BGR),
                [cv2.IMWRITE_JPEG_QUALITY, 92])
