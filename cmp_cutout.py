#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compare the old 765-wide cut-out with the new full-resolution one:
alpha agreement (after downscaling the new one back to 765) and 1:1 crops."""
import cv2, numpy as np

OLD = 'shots/hero-quality/BEFORE-cutout-765x1150.png'
NEW = 'assets/_src_ceo-cutout-beige.png'
NAVY = np.array([0x0B, 0x19, 0x33], np.float32)

old = cv2.imread(OLD, cv2.IMREAD_UNCHANGED)
new = cv2.imread(NEW, cv2.IMREAD_UNCHANGED)
print('old', old.shape, 'new', new.shape)

new_small = cv2.resize(new, (old.shape[1], old.shape[0]), interpolation=cv2.INTER_AREA)

ao = old[..., 3].astype(np.float32) / 255.0
an = new_small[..., 3].astype(np.float32) / 255.0
d = np.abs(ao - an)
print('alpha mean|diff| %.4f   p99 %.4f   >0.5 px count %d (%.4f%%)'
      % (d.mean(), np.percentile(d, 99), (d > 0.5).sum(), 100.0 * (d > 0.5).mean()))
print('coverage old %.3f new %.3f' % ((ao > 0.5).mean(), (an > 0.5).mean()))

# colour agreement where both are solid
solid = (ao > 0.99) & (an > 0.99)
dcol = np.abs(old[..., :3].astype(np.float32) - new_small[..., :3].astype(np.float32)).mean(2)
print('solid px %d  colour mean|diff| %.2f  p99 %.2f'
      % (solid.sum(), dcol[solid].mean(), np.percentile(dcol[solid], 99)))


def comp(img, navy=NAVY):
    a = img[..., 3:4].astype(np.float32) / 255.0
    return np.clip(img[..., :3].astype(np.float32) * a + navy * (1 - a), 0, 255).astype(np.uint8)


# 1:1 crops of the same physical region: face, hair edge, shoulder/jacket edge
regions = {
    'face':  (0.30, 0.16, 0.78, 0.42),   # x0,y0,x1,y1 as fractions
    'hairL': (0.18, 0.20, 0.42, 0.44),
    'jacket': (0.02, 0.58, 0.30, 0.86),
}
old_c = comp(old)
new_c = comp(new)
tiles = []
for name, (x0, y0, x1, y1) in regions.items():
    ow, oh = old.shape[1], old.shape[0]
    nw, nh = new.shape[1], new.shape[0]
    o = old_c[int(y0 * oh):int(y1 * oh), int(x0 * ow):int(x1 * ow)]
    n = new_c[int(y0 * nh):int(y1 * nh), int(x0 * nw):int(x1 * nw)]
    # upscale the old one to the new pixel size so both are 1:1 at source detail
    o = cv2.resize(o, (n.shape[1], n.shape[0]), interpolation=cv2.INTER_NEAREST)
    sep = np.full((n.shape[0], 6, 3), (0, 0, 255), np.uint8)
    tiles.append(np.hstack([o, sep, n]))
w = max(t.shape[1] for t in tiles)
tiles = [cv2.copyMakeBorder(t, 0, 0, 0, w - t.shape[1], cv2.BORDER_CONSTANT, value=(255, 255, 255)) for t in tiles]
cv2.imwrite('shots/hero-quality/cmp-alpha-faces.png', np.vstack(tiles))

# alpha diff map
dm = (np.clip(d * 3, 0, 1) * 255).astype(np.uint8)
cv2.imwrite('shots/hero-quality/cmp-alpha-diff.png', dm)
print('wrote shots/hero-quality/cmp-alpha-faces.png (left=old 765 upscaled, right=new)')
