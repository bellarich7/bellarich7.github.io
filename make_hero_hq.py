#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hero portrait 2x (PC retina) asset.  **SUPERSEDED 2026-11-26** — the PC hero
now draws 466 CSS px wide and uses make_hero_pc.py instead (466/699/932 files).
This one targeted the old 700 CSS px display and is kept only for the record.

The studio master is 1086x1448 - the largest original we have.  The hero draws
the cut-out up to 700x869 CSS px, so a 2x screen asks for 1400x1738 device px
and the browser has to stretch 1086 px by 1.29x (that stretch is what looks
soft/mushy on a 1920 retina screen).

This script makes one dedicated PC high-DPI file at exactly 1400x1738 by
resampling the RGBA master once with a high-quality kernel (premultiplied, so
the cut edge does not bleed) plus a mild detail pass, and leaves the existing
1086-wide asset untouched for 1x screens and mobile (no change at all there).

    python3 make_hero_hq.py            # writes assets/ceo-hero-2x.webp (q88, sharpen 0.35)
    WEBP_Q=84 SHARP=0.2 python3 make_hero_hq.py   # 다른 품질/샤픈
"""
import os
import numpy as np
import cv2
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'assets', '_cutout_ceo-slim.png')   # 1086x1448 RGBA master
OUT = os.path.join(HERE, 'assets', 'ceo-hero-2x.webp')

TARGET_W = int(os.environ.get('TARGET_W', '1400'))   # 700 CSS px * 2
TOP_SRC = 100          # same headroom trim as make_cutout_portrait.py (source px)
FADE = 0.03            # same 3% alpha fade at the bottom
SHARP_AMOUNT = float(os.environ.get('SHARP', '0.35'))
SHARP_RADIUS = 1.15    # px at the 2x scale
WEBP_Q = int(os.environ.get('WEBP_Q', '88'))


def premultiplied_resize(rgba, size):
    """Lanczos resize in premultiplied alpha (avoids dark fringes/halo)."""
    a = rgba[..., 3:4].astype(np.float32) / 255.0
    pm = np.concatenate([rgba[..., :3].astype(np.float32) * a, a * 255.0], axis=2)
    chans = [np.asarray(Image.fromarray(pm[..., i], mode='F').resize(size, Image.LANCZOS))
             for i in range(4)]
    pm = np.dstack(chans)
    aa = np.clip(pm[..., 3], 1e-3, 255.0)
    rgb = np.clip(pm[..., :3] * 255.0 / aa[..., None], 0, 255)
    out = np.dstack([rgb, np.clip(pm[..., 3], 0, 255)]).astype(np.uint8)
    return out


def sharpen(rgb, alpha):
    """Unsharp mask on the colour only, weighted by alpha so the empty
    background stays clean (no ringing around the cut edge)."""
    blur = cv2.GaussianBlur(rgb, (0, 0), SHARP_RADIUS)
    hi = rgb.astype(np.float32) - blur.astype(np.float32)
    w = (np.clip(alpha.astype(np.float32) / 255.0, 0, 1) ** 0.5)[..., None]
    out = rgb.astype(np.float32) + hi * SHARP_AMOUNT * w
    return np.clip(out, 0, 255).astype(np.uint8)


def main():
    rgba = cv2.cvtColor(cv2.imread(SRC, cv2.IMREAD_UNCHANGED), cv2.COLOR_BGRA2RGBA)
    h, w = rgba.shape[:2]
    s = TARGET_W / w
    tw, th = TARGET_W, round(h * s)
    big = premultiplied_resize(rgba, (tw, th))
    rgb = sharpen(big[..., :3], big[..., 3])
    a = big[..., 3].astype(np.float32) / 255.0

    # alpha: slight smoothing then the same 3% bottom fade as the 1x asset
    a = cv2.GaussianBlur(a, (0, 0), 0.7)
    start = round(th * (1 - FADE))
    t = np.linspace(0, 1, th - start)
    a[start:, :] *= (1 - (t * t * (3 - 2 * t)))[:, None]

    top = round(TOP_SRC * s)
    rgb, a = rgb[top:], a[top:]
    out = np.dstack([rgb, (a * 255).astype(np.uint8)])
    Image.fromarray(out, mode='RGBA').save(OUT, 'WEBP', quality=WEBP_Q,
                                           method=6, exact=True)
    kb = os.path.getsize(OUT) / 1024
    print('written %s  %dx%d  %.1f KB (q%d, sharpen %.2f)' %
          (OUT, out.shape[1], out.shape[0], kb, WEBP_Q, SHARP_AMOUNT))


if __name__ == '__main__':
    main()
