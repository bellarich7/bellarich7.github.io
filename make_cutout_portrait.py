#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cut the studio portrait (grey-beige backdrop) out to RGBA and write the
hero + card portrait assets.

Source: downloads/studio-slim-beige.png (1086x1448, front-facing, light beige
suit / white blouse, mid-grey studio backdrop).  The client asked for the face
and clothes to stay *exactly* the original pixels, so this script only solves
an alpha matte and rebuilds the colours of anti-aliased edge pixels from the
solid subject core (no generative retouching).

Outputs
  assets/_src_ceo-slim.png           source copy used for reproducibility
  assets/_cutout_ceo-slim.png        RGBA master, no bottom fade (card source)
  assets/ceo-hero.webp               hero cut-out, soft bottom fade, q95
  assets/_preview_navy.jpg           hero cut-out over #0B1933 for eyeballing
  assets/_preview_softgrey.jpg       cut-out over #D2CEC7 for eyeballing

    python3 make_cutout_portrait.py
"""
import os
import shutil

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'assets', '_src_ceo-slim.png')
DOWNLOAD_SRC = '/workspace/downloads/studio-slim-beige.png'

OUT_MASTER = os.path.join(HERE, 'assets', '_cutout_ceo-slim.png')
OUT_WEBP = os.path.join(HERE, 'assets', 'ceo-hero.webp')
WEBP_QUALITY = int(os.environ.get('WEBP_Q', '95'))

NAVY = np.array([0x0B, 0x19, 0x33], np.float32)
SOFT = np.array([0xD2, 0xCE, 0xC7], np.float32)


def background_model(im):
    """Smooth backdrop estimate by normalised convolution over background-like
    pixels.  The studio wall is a vignetted mid grey (~R110 G102 B95)."""
    g = im.mean(2)
    chroma = im.max(2) - im.min(2)
    prior = ((chroma < 24) & (g > 50) & (g < 150)).astype(np.float32)
    m = prior.copy()
    sigma = 20
    for _ in range(8):
        wsum = cv2.GaussianBlur(m, (0, 0), sigma)
        bg = cv2.GaussianBlur(im * m[..., None], (0, 0), sigma) / np.maximum(wsum, 1e-6)[..., None]
        d = np.linalg.norm(im - bg, axis=2)
        m = (prior > 0).astype(np.float32) * (d < 7)
    return bg.astype(np.float32)


def silhouette(im, bg):
    h, w, _ = im.shape
    diff = np.linalg.norm(im - bg, axis=2)
    raw = (diff > 13).astype(np.uint8)
    raw = cv2.morphologyEx(raw, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    raw = cv2.morphologyEx(raw, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(raw, connectivity=8)
    if n > 1:
        big = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
        raw = (lab == big).astype(np.uint8)
    # keep enclosed gaps open: a few pixels of backdrop showing through a gap
    # between hair strands must stay transparent, not turn into a beige patch
    return raw


def edge_colour(im, core, band=16):
    known = core.astype(np.float32)
    rgb = im.copy()
    for _ in range(band):
        wsum = cv2.blur(known, (5, 5))
        mean = cv2.blur(rgb * known[..., None], (5, 5)) / np.maximum(wsum, 1e-6)[..., None]
        grow = (wsum > 0.02) & (known < 0.5)
        rgb[grow] = mean[grow]
        known = np.maximum(known, grow.astype(np.float32))
    return np.clip(rgb, 0, 255)


def alpha_matte(im, bg):
    """Linear-unmixing alpha, applied only in a thin band around the silhouette.

    Unmixing (im = a*F + (1-a)*bg) is what resolves wispy hair: a pixel that is
    30% hair / 70% backdrop gets a=0.3 and no beige patch.  But it is only
    trustworthy close to the edge; deep inside the subject - shadowed cloth that
    is darker than the local core colour - it would read as semi-transparent and
    let the backdrop show through the jacket.  So the core is forced opaque and
    the projection is used outside it.
    """
    solid = silhouette(im, bg)
    dist = cv2.distanceTransform(solid, cv2.DIST_L2, 5)   # px to nearest bg
    core = dist >= 2.6
    near = cv2.dilate(solid, np.ones((5, 5), np.uint8), iterations=2).astype(bool)

    F = edge_colour(im, core, band=18)
    d = F - bg
    denom = (d * d).sum(2)
    proj = ((im - bg) * d).sum(2) / np.maximum(denom, 1e-6)
    pix_d = np.linalg.norm(im - bg, axis=2)
    a = np.where((denom > 120) & (pix_d > 20), np.clip(proj, 0, 1), 0.0).astype(np.float32)
    a[~near] = 0.0
    a[a < 0.12] = 0.0

    # specular highlights on the hair and lit blouse are as bright as the
    # backdrop and read as "transparent" to the projection; every hole the
    # backdrop cannot reach (fully enclosed by subject) is opaque again.
    # The portrait is cut off at the bottom edge, so seal those last rows with
    # the silhouette first - otherwise dark crease shadows that run to the cut
    # stay connected to the outside, are never filled, and show as streaks.
    hh, ww = a.shape
    m0 = (a > 0.4).astype(np.uint8)
    m0[-3:, :] = np.maximum(m0[-3:, :], solid[-3:, :])
    ff = m0.copy()
    ff[0, :] = 0
    ff[:, 0] = ff[:, -1] = 0
    holes = np.zeros((hh + 2, ww + 2), np.uint8)
    cv2.floodFill(ff, holes, (0, 0), 1)
    enclosed = ((1 - ff) & (m0 == 0)).astype(bool)
    a[enclosed] = 1.0
    a = cv2.GaussianBlur(a, (0, 0), 0.6)

    m = (a > 0.3).astype(np.uint8)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
    keep = np.zeros_like(m)
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] >= 600:
            keep[lab == i] = 1
    keep = cv2.dilate(keep, np.ones((3, 3), np.uint8), iterations=1).astype(bool)
    a[~keep] = 0.0
    a[a < 0.06] = 0.0
    return np.clip(a, 0, 1)


def edge_colour_out(im, bg, alpha):
    """Recover the foreground colour of fringe pixels by unmixing the backdrop,
    so a 40% hair pixel becomes dark hair instead of a grey halo.  Fully opaque
    pixels are returned untouched (face and clothes stay original)."""
    a = np.maximum(alpha, 0.45)[..., None]
    rec = np.clip(bg + (im - bg) / a, 0, 255)
    fallback = edge_colour(im, alpha > 0.98, band=18)
    w = np.clip((alpha - 0.30) / 0.45, 0, 1)[..., None]
    rgb = rec * w + fallback * (1 - w)
    solid = alpha >= 0.98
    rgb[solid] = im[solid]
    return np.clip(rgb, 0, 255)


def bottom_fade(alpha, frac=0.0):
    h, w = alpha.shape
    start = int(h * (1 - frac))
    t = np.linspace(0, 1, h - start)
    ramp = 1 - (t * t * (3 - 2 * t))
    alpha[start:, :] *= ramp[:, None]
    return alpha


def main():
    if not os.path.exists(SRC):
        shutil.copyfile(DOWNLOAD_SRC, SRC)
        print('copied source ->', SRC)
    bgr = cv2.imread(SRC, cv2.IMREAD_COLOR)
    im = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB).astype(np.float32)
    h, w, _ = im.shape
    print('source %dx%d' % (w, h))

    bg = background_model(im)
    a = alpha_matte(im, bg)
    rgb = edge_colour_out(im, bg, a)

    ys, xs = np.where(a > 0.5)
    print('subject bbox x %d-%d  y %d-%d  coverage %.3f' %
          (xs.min(), xs.max(), ys.min(), ys.max(), (a > 0.5).mean()))

    master = np.dstack([rgb, a * 255]).astype(np.uint8)
    cv2.imwrite(OUT_MASTER, cv2.cvtColor(master, cv2.COLOR_RGBA2BGRA))

    # hero: trim the empty studio headroom above the head (background only, no
    # subject pixel is touched) and add a soft bottom fade so the cut torso
    # melts into the navy hero
    top = 100
    ah = bottom_fade(a.copy(), frac=0.03)[top:]
    hero = np.dstack([rgb[top:], ah * 255]).astype(np.uint8)
    print('hero crop %dx%d (top -%d)' % (hero.shape[1], hero.shape[0], top))
    cv2.imwrite(OUT_WEBP, cv2.cvtColor(hero, cv2.COLOR_RGBA2BGRA),
                [cv2.IMWRITE_WEBP_QUALITY, WEBP_QUALITY])

    for colr, name in ((NAVY, '_preview_navy.jpg'), (SOFT, '_preview_softgrey.jpg')):
        comp = rgb * a[..., None] + colr * (1 - a[..., None])
        cv2.imwrite(os.path.join(HERE, 'assets', name),
                    cv2.cvtColor(np.clip(comp, 0, 255).astype(np.uint8), cv2.COLOR_RGB2BGR),
                    [cv2.IMWRITE_JPEG_QUALITY, 94])
    print('written', OUT_MASTER, OUT_WEBP)


if __name__ == '__main__':
    main()
