#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Card portrait: same face/cloth pixels as the studio original, but the dark
grey studio backdrop replaced with one soft warm-grey tone (#CFCBC4~#D8D4CD)
through the alpha matte - no AI regeneration.

Outputs
  assets/card-ceo.webp                  1000x1000, square, circular-crop safe
  /workspace/downloads/studio-slim-beige-softbg.png
                                        1000x1000 circular PNG (transparent
                                        outside the circle) for the client

    python3 make_card_portrait.py
"""
import os

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
MASTER = os.path.join(HERE, 'assets', '_cutout_ceo-slim.png')
OUT_WEBP = os.path.join(HERE, 'assets', 'card-ceo.webp')
OUT_CIRCLE = '/workspace/downloads/studio-slim-beige-softbg.png'

# square crop (x0, y0, size) - head top ~55px inside, chin just below centre
CROP = (83, 110, 920)
TOP = np.array([0xD8, 0xD4, 0xCD], np.float32)
BOTTOM = np.array([0xCF, 0xCB, 0xC4], np.float32)


def soft_bg(h, w):
    """One warm-grey tone with a barely-there studio vignette."""
    t = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    img = TOP * (1 - t) + BOTTOM * t
    img = np.repeat(img, w, axis=1)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cy, cx = h * 0.42, w * 0.5
    r = np.sqrt(((yy - cy) / (h * 0.9)) ** 2 + ((xx - cx) / (w * 0.9)) ** 2)
    img = img * (1 - 0.06 * np.clip(r, 0, 1))[..., None]      # soft corner falloff
    return np.clip(img, 0, 255)


def main():
    cut = cv2.imread(MASTER, cv2.IMREAD_UNCHANGED)   # BGRA
    cut = cv2.cvtColor(cut, cv2.COLOR_BGRA2RGBA).astype(np.float32)
    x0, y0, s = CROP
    crop = cut[y0:y0 + s, x0:x0 + s]
    assert crop.shape[:2] == (s, s), crop.shape

    rgb, a = crop[..., :3], crop[..., 3:4] / 255.0
    bg = soft_bg(s, s)
    comp = np.clip(rgb * a + bg * (1 - a), 0, 255).astype(np.uint8)

    cv2.imwrite(OUT_WEBP, cv2.cvtColor(comp, cv2.COLOR_RGBA2BGRA),
                [cv2.IMWRITE_WEBP_QUALITY, 92])

    # keepsake: same picture, circular alpha
    yy, xx = np.mgrid[0:s, 0:s].astype(np.float32)
    r = np.sqrt((yy - s / 2 + 0.5) ** 2 + (xx - s / 2 + 0.5) ** 2)
    circ = np.clip((s / 2 - 1.0 - r) + 0.5, 0, 1)      # 1px anti-aliased rim
    out = np.dstack([comp, (circ * 255).astype(np.uint8)])
    cv2.imwrite(OUT_CIRCLE, cv2.cvtColor(out, cv2.COLOR_RGBA2BGRA))
    print('written', OUT_WEBP, OUT_CIRCLE)


if __name__ == '__main__':
    main()
