#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PC hero portrait files sized to the new display width (2026-11-26 resize pass).

The PC hero now draws the portrait at 466 CSS px wide (was 700).  A 2x screen
therefore needs 932 device px - inside the 1086 px master, so nothing has to be
upscaled any more.  Instead of letting the browser shrink one big file we bake
each screen tier at exactly the size it draws, with a high-quality kernel:

    pc-1x  466x 578   (1x screens, and 1.25x screens)
    pc-15x 699x 869   (1.5x screens: Windows 150%)
    pc-2x  932x1157   (2x screens)

Every tier comes from assets/_cutout_ceo-slim.png (1086x1448 RGBA master):
premultiplied Lanczos resize (no fringe from the cut edge) -> alpha-weighted
unsharp (detail only where the subject is, background stays clean) -> same
bottom 3% fade and top 100px headroom trim as the current hero asset.

FACE/CLOTHES PIXELS ARE NEVER REDRAWN. No generative upscale.

    python3 make_hero_pc.py            # writes the three webp files
    WEBP_Q=94 SHARP=0.25 python3 make_hero_pc.py
    TIERS=466 python3 make_hero_pc.py  # one tier only
"""
import os

import cv2
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
MASTER = os.path.join(HERE, 'assets', '_cutout_ceo-slim.png')   # 1086x1448 RGBA
TOP_SRC = 100      # headroom trim in master px (same as make_cutout_portrait.py)
FADE = 0.03        # bottom alpha fade

TIERS = [int(t) for t in os.environ.get('TIERS', '466,699,932').split(',')]
SHARP = float(os.environ.get('SHARP', '0.22'))
WEBP_Q = int(os.environ.get('WEBP_Q', '92'))
MATTE = os.environ.get('MATTE', 'clean')     # clean | orig


def clean_crust(rgba):
    """Drop studio-background colour that survived inside the hair silhouette.

    Same idea as card/make_card_hero.py: the cut-out keeps a thin band of the
    warm-grey studio wall along the hair silhouette; on navy it reads as grey
    frost.  Pixels inside the silhouette whose colour is still the backdrop are
    made transparent (opaque crust) or faded (semi-transparent haze).
    """
    rgb_src = np.array(Image.open(os.path.join(HERE, 'assets', '_src_ceo-slim.png'))
                       .convert('RGB')).astype(np.float32)
    arr = rgba.astype(np.float32)
    alpha = arr[..., 3].copy()
    h, w, _ = rgb_src.shape
    ys, xs = np.mgrid[0:h, 0:w]
    m = alpha < 4
    xn, yn = (xs[m] / w) * 2 - 1, (ys[m] / h) * 2 - 1
    design = np.stack([np.ones_like(xn), xn, yn, xn * yn, xn * xn, yn * yn], axis=1)
    X, Y = (xs / w) * 2 - 1, (ys / h) * 2 - 1
    full = np.stack([np.ones_like(X), X, Y, X * Y, X * X, Y * Y], axis=-1)
    bg = np.zeros((h, w, 3), np.float32)
    for ch in range(3):
        coef, *_ = np.linalg.lstsq(design, rgb_src[:, :, ch][m], rcond=None)
        bg[:, :, ch] = full @ coef
    dist = np.linalg.norm(rgb_src - bg, axis=2)

    factor = np.clip(dist / 46.0, 0.0, 1.0)
    haze = (alpha > 4) & (dist < 46)
    alpha[haze] = alpha[haze] * factor[haze]
    crust = (alpha >= 190) & (dist < 16)
    alpha[crust] = 0.0
    out = arr.copy()
    out[..., 3] = np.clip(alpha, 0, 255)
    return np.clip(out, 0, 255).astype(np.uint8)


def premultiplied_resize(rgba, size):
    a = rgba[..., 3:4].astype(np.float32) / 255.0
    pm = np.concatenate([rgba[..., :3].astype(np.float32) * a, a * 255.0], axis=2)
    chans = [np.asarray(Image.fromarray(pm[..., i], mode='F').resize(size, Image.LANCZOS))
             for i in range(4)]
    pm = np.dstack(chans)
    aa = np.clip(pm[..., 3], 1e-3, 255.0)
    rgb = np.clip(pm[..., :3] * 255.0 / aa[..., None], 0, 255)
    return np.dstack([rgb, np.clip(pm[..., 3], 0, 255)]).astype(np.uint8)


def sharpen(rgb, alpha, radius):
    blur = cv2.GaussianBlur(rgb, (0, 0), radius)
    hi = rgb.astype(np.float32) - blur.astype(np.float32)
    w = (np.clip(alpha.astype(np.float32) / 255.0, 0, 1) ** 0.5)[..., None]
    return np.clip(rgb.astype(np.float32) + hi * SHARP * w, 0, 255).astype(np.uint8)


def build(master, width):
    h, w = master.shape[:2]
    s = width / w
    th = round(h * s)
    big = premultiplied_resize(master, (width, th))
    radius = 0.85 * max(s, 0.6)          # in target pixels
    rgb = sharpen(big[..., :3], big[..., 3], radius)
    a = cv2.GaussianBlur(big[..., 3].astype(np.float32) / 255.0, (0, 0), 0.45)
    start = round(th * (1 - FADE))
    t = np.linspace(0, 1, th - start)
    a[start:, :] *= (1 - (t * t * (3 - 2 * t)))[:, None]
    top = round(TOP_SRC * s)
    rgb, a = rgb[top:], a[top:]
    return np.dstack([rgb, (np.clip(a, 0, 1) * 255).astype(np.uint8)])


def main():
    rgba = cv2.cvtColor(cv2.imread(MASTER, cv2.IMREAD_UNCHANGED), cv2.COLOR_BGRA2RGBA)
    if MATTE == 'clean':
        rgba = clean_crust(rgba)
    for t in TIERS:
        out = build(rgba, t)
        suffix = '2x' if t == 932 else ('15x' if t == 699 else '1x')
        name = 'ceo-hero-pc-%s.webp' % suffix
        path = os.path.join(HERE, 'assets', name)
        Image.fromarray(out, mode='RGBA').save(path, 'WEBP', quality=WEBP_Q,
                                               method=6, exact=True)
        print('%s  %dx%d  %.1f KB  (q%d, sharpen %.2f, matte %s)' %
              (name, out.shape[1], out.shape[0], os.path.getsize(path) / 1024,
               WEBP_Q, SHARP, MATTE))


if __name__ == '__main__':
    main()
