#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Card hero portrait for the /card/ page — charcoal suit, grey studio backdrop.

2026-11-27 (자영님 지시 4차):
  · 사진은 원본 그대로 — 좌우 크롭 없음, 위 여백만 조금 줄임. 색·톤·스크림·오버레이 없음.
  · 얼굴은 작게, 몸통은 길게: 원본 세로 전체(정수리~골반)를 살리고,
    사진 폭을 캔버스 폭의 PHOTO_W_RATIO 만큼만 차지하게 두어 얼굴을 줄인다.
  · 사진 좌우는 원본 가장자리 배경 픽셀을 그대로 옆으로 이어 붙인다(색 보정 없음).
    → 사진과 바깥이 한 장면으로 이어지고, 페이지 배경색도 이 캔버스 가장자리에서 샘플한다.

'얼굴을 더 줄이거나 키우려면' 아래 PHOTO_W_RATIO 하나만 바꾸면 된다.
  값이 작을수록 사진이 좁아져 얼굴이 작아지고, 스테이지도 그만큼 짧아진다(비율 자동).
  바꾼 뒤 card/build_card.py 가 캔버스 비율·회색을 HTML 에 자동으로 넣는다.

  python3 card/make_card_hero.py                     # 기본
  python3 card/make_card_hero.py --w-ratio 0.62      # 얼굴 더 작게
"""

import argparse
import json
import pathlib

import numpy as np
from PIL import Image

ROOT = pathlib.Path('/workspace/bellarich-site')
SRC = ROOT / 'assets' / '_src_ceo-charcoal.png'
OUT = ROOT / 'assets' / 'card-hero.webp'
META = ROOT / 'assets' / 'card-hero.json'

# --- 프레이밍 (원본 1086x1448 기준) ---
Y0, Y1 = 60, 1448          # 위 여백만 줄인다(머리 위 회색 77px). 좌우 크롭 없음.
PHOTO_W_RATIO = 0.66       # ★ 얼굴 크기 다이얼 — 사진 폭 / 캔버스 폭
QUALITY = 92

# 머리(정수리 137 ~ 턱 599, 좌우 338~778) — 얼굴 크기 보고용 기준
HEAD = (137, 599, 338, 778)


def hexc(v):
    return '#%02x%02x%02x' % tuple(int(round(x)) for x in v)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--y0', type=int, default=Y0)
    ap.add_argument('--y1', type=int, default=Y1)
    ap.add_argument('--w-ratio', type=float, default=PHOTO_W_RATIO)
    ap.add_argument('--out', default=str(OUT))
    ap.add_argument('--preview', type=int, default=390)
    ap.add_argument('--tag', default='')
    ap.add_argument('--no-meta', action='store_true', help='비교용 후보는 메타를 쓰지 않음')
    a = ap.parse_args()

    im = Image.open(SRC).convert('RGB')
    W, H = im.size
    crop = im.crop((0, a.y0, W, a.y1))                 # 좌우 크롭 없음
    cw, ch = crop.size
    ca = np.asarray(crop).astype(np.uint8)

    canvas_w = round(cw / a.w_ratio)
    pad_l = (canvas_w - cw) // 2
    pad_r = canvas_w - cw - pad_l

    left = ca[:, :6].mean(axis=1)                      # 행별 왼쪽 가장자리 색
    right = ca[:, -6:].mean(axis=1)
    out_arr = np.empty((ch, canvas_w, 3), np.uint8)
    out_arr[:, :pad_l] = left[:, None, :].astype(np.uint8)
    out_arr[:, pad_l:pad_l + cw] = ca
    out_arr[:, pad_l + cw:] = right[:, None, :].astype(np.uint8)

    # 사진 가장자리 FEATHER px 는 배경뿐인 구간(인물은 최소 60px 안쪽) — 이어붙임 선을 지운다
    FEATHER = 36
    if FEATHER:
        f = np.linspace(0.0, 1.0, FEATHER) ** 2                       # 0=패드색, 1=사진
        band = out_arr[:, pad_l:pad_l + FEATHER].astype(float)
        out_arr[:, pad_l:pad_l + FEATHER] = (
            band * f[None, :, None] + left[:, None, :] * (1 - f[None, :, None])).astype(np.uint8)
        band = out_arr[:, pad_l + cw - FEATHER:pad_l + cw].astype(float)
        out_arr[:, pad_l + cw - FEATHER:pad_l + cw] = (
            band * f[::-1][None, :, None] + right[:, None, :] * (1 - f[::-1][None, :, None])).astype(np.uint8)

    canvas = Image.fromarray(out_arr)
    out = pathlib.Path(a.out)
    canvas.save(out, 'WEBP', quality=QUALITY, method=6)

    oa = np.asarray(canvas).astype(float)

    def edge_at(frac):
        y = min(ch - 6, max(0, int(round(ch * frac))))
        band = oa[y:y + 4]
        return np.concatenate([band[:, :8], band[:, -8:]]).reshape(-1, 3).mean(axis=0)

    top, mid = edge_at(0.0), edge_at(0.5)
    bot = edge_at(0.92)
    mid_l = oa[ch // 2 - 5:ch // 2 + 5, :10].reshape(-1, 3).mean(axis=0)
    mid_r = oa[ch // 2 - 5:ch // 2 + 5, -10:].reshape(-1, 3).mean(axis=0)

    head_h = HEAD[1] - HEAD[0]
    head_w = HEAD[3] - HEAD[2]
    k = 390 / canvas_w
    meta = {
        'src': str(SRC), 'crop': [0, a.y0, W, a.y1], 'crop_size': [cw, ch],
        'w_ratio': a.w_ratio, 'canvas': [canvas_w, ch], 'pad': [pad_l, pad_r],
        'aspect': round(canvas_w / ch, 6),
        'edge_top': hexc(top), 'edge_mid': hexc(mid), 'edge_bottom': hexc(bot),
        'edge_mid_l': hexc(mid_l), 'edge_mid_r': hexc(mid_r),
        'page_top': hexc(top), 'page_mid': hexc(mid), 'page_bot': hexc(bot),
        'stage_h_at_390': round(390 * ch / canvas_w, 1),
        'photo_w_at_390': round(390 * cw / canvas_w, 1),
        'side_pad_at_390': round(390 * pad_l / canvas_w, 1),
        'face_h_at_390': round(head_h * k, 1),
        'face_w_at_390': round(head_w * k, 1),
        'bytes': out.stat().st_size,
    }
    if not a.no_meta:
        META.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding='utf-8')
    print(json.dumps(meta, ensure_ascii=False))

    if a.preview:
        pw = a.preview
        canvas.resize((pw, round(ch * pw / canvas_w)), Image.LANCZOS).save(
            '/workspace/bellarich-site/shots/card/hero-preview-%s.png' % (a.tag or round(a.w_ratio * 100)))


if __name__ == '__main__':
    main()
