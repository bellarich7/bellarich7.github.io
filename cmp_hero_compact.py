"""Face-crop comparison at 1440 DPR2: same part of the source photo, same output size.

before: photo drawn 538x810 css -> 1077x1621 device px from 1022x1538 source (x1.05, upscaled)
after : photo drawn 479x720 css ->  957x1441 device px from 1022x1538 source (x0.94, downsampled)
"""
from PIL import Image, ImageDraw

OUT = '/workspace/bellarich-site/shots/hero-quality/compact/'
VPS = 'cp /workspace/bellarich-site/shots/hero-quality/compact/{}'

# drawn rects in device px (measured with measure_hero_img.py at 1440x900 dpr2)
RECT = {
    'before': dict(x=1440 - 538.4, y=900 - 810.3, w=538.4, h=810.3, dev=2),
    'after':  dict(x=1440 - 478.6, y=900 - 720.3, w=478.6, h=720.3, dev=2),
}
# same fraction of the source image (the face)
FX0, FY0, FX1, FY1 = 0.26, 0.04, 0.80, 0.42

crops = {}
for tag, r in RECT.items():
    img = Image.open(OUT + '%s-1440-dpr2-top.png' % tag).convert('RGB')
    sx = r['dev']; dx, dy = r['x'] * sx, r['y'] * sx
    dw, dh = r['w'] * sx, r['h'] * sx
    box = (int(dx + dw * FX0), int(dy + dh * FY0), int(dx + dw * FX1), int(dy + dh * FY1))
    crops[tag] = img.crop(box)

W = 520
panels = []
for tag in ('before', 'after'):
    c = crops[tag]
    h = round(c.height * W / c.width)
    panels.append((tag, c.resize((W, h), Image.LANCZOS)))

H = max(p[1].height for p in panels)
sheet = Image.new('RGB', (W * 2 + 24, H + 34), (11, 25, 51))
d = ImageDraw.Draw(sheet)
for i, (tag, p) in enumerate(panels):
    x = i * (W + 24)
    sheet.paste(p, (x, 34))
    label = 'BEFORE  538x810 css  (1.05x upscale)' if tag == 'before' else 'AFTER  479x720 css  (0.94x downsample)'
    d.text((x + 6, 12), label, fill=(197, 164, 126))
sheet.save(OUT + 'cmp-face-dpr2.png')
print('saved', OUT + 'cmp-face-dpr2.png', sheet.size)
