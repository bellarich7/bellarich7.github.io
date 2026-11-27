import os, subprocess
from playwright.sync_api import sync_playwright

S = os.path.abspath(os.path.dirname(__file__))          # shots folder
D = '/workspace/downloads'


def html(body, css=''):
    return ('<!doctype html><meta charset="utf-8">'
            '<style>body{margin:0;background:#0d1626;font-family:"Noto Sans KR",'
            '"Malgun Gothic",sans-serif;color:#e9edf5}'
            '.cap{font-size:15px;letter-spacing:.02em;padding:10px 14px 6px}'
            '.cap b{color:#C5A47E;font-weight:700}'
            'img{display:block}'
            + css + '</style>' + body)


def img(path):
    return 'file://' + os.path.join(S, path)


# 1) before/after full hero, 1920
b1 = html(
    '<div class="cap"><b>수정 전</b> — 사진 폭 700px, 오른쪽 끝에 붙어 있음 (1920×1080 화면)</div>'
    '<img src="%s" width="1280">'
    '<div class="cap" style="padding-top:16px"><b>수정 후</b> — 사진 폭 466px(2/3), 오른쪽에서 320px 들여 가운데 쪽으로 (1920×1080 화면)</div>'
    '<img src="%s" width="1280">' % (img('before-1920-top.png'), img('live-1920-top.png')))

# 2) face 1:1 comparison at 2x screens
def row(label, before, after_live, scale):
    return ('<div style="display:flex;align-items:flex-start;gap:18px">'
            '<div><div class="cap"><b>%s</b> · 수정 전 1:1</div><img src="%s"></div>'
            '<div><div class="cap">수정 후 1:1 (사진이 작아진 만큼 픽셀이 1:1)</div><img src="%s"></div>'
            '<div><div class="cap">수정 후 ×%.1f 확대 — 같은 크기로 키워도 이만큼 선명</div>'
            '<img src="%s" style="width:%.0fpx;image-rendering:pixelated"></div></div>'
            % (label, img(before), img(after_live), scale,
               img(after_live), Image_width(after_live) * scale))

from PIL import Image as PImage
def Image_width(p):
    return PImage.open(os.path.join(S, p)).width

rows = []
for lbl in ('1440', '1920', '2560'):
    a = 'before-%sd2-face.png' % lbl
    c = 'live-%sd2-face.png' % lbl
    w = Image_width(a) / Image_width(c)
    rows.append('<div style="margin-bottom:26px">%s</div>' % row(lbl + ' · 2배 화면', a, c, w))

b2 = html('<div class="cap" style="font-size:17px;padding:14px 0 10px">PC 대표 사진 얼굴 — 2배(레티나) 화면 1:1 픽셀 비교</div>' + ''.join(rows))

open(os.path.join(S, 'report1.html'), 'w', encoding='utf-8').write(b1)
open(os.path.join(S, 'report2.html'), 'w', encoding='utf-8').write(b2)

with sync_playwright() as p:
    b = p.chromium.launch()
    for src, out, w in (('report1.html', D + '/히어로_사진_크기_위치_전후_1920.png', 1310),
                        ('report2.html', D + '/히어로_사진_얼굴_1to1_전후_1440_1920_2560.png', 1180)):
        ctx = b.new_context(viewport={'width': w, 'height': 900}, device_scale_factor=1)
        pg = ctx.new_page(); pg.goto('file://' + os.path.join(S, src), wait_until='load')
        pg.wait_for_timeout(400)
        pg.screenshot(path=out, full_page=True)
        print('wrote', out, PImage.open(out).size)
        ctx.close()
    b.close()
