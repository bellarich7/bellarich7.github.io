# 히어로 대표 사진 화질 개선 · 영상 카드 가운데 정렬 (2026-11-25)

배포 커밋: `e2bb6ed` (bellarich-deploy, index.html 한 파일)
라이브: https://bellarich.co.kr/?v=1125u (HTTP 200)

## 무엇을 바꿨나

1. **대표 사진 해상도** — `make_cutout.py` 의 `TARGET` 을 765×1150 → **1022×1538**(원본 `assets/_gen_beige.png` 전해상도).
   컷아웃 알고리즘의 픽셀 반경·면적 상수는 765 기준값에 배율 S(=1022/765=1.336)를 곱해 그대로 등가가 되도록 했다.
   WebP 품질 88 → **95** (60,302B → 176,698B).
   검증: 새 컷아웃을 765로 되돌려 기존 컷아웃과 비교 → 알파 평균차 0.0010 (p99 0.0235), 0.5 이상 차이나는 픽셀 91개(전체의 0.010%), 불투명 영역 색 평균차 1.14/255. 즉 마스크는 동일, 디테일만 살아남.
2. **영상 카드 가운데 정렬** — `.philo__video{max-width:680px;margin:... auto 0}` (margin-inline:auto). 폭·높이 변화 없음(680×428 유지).
3. 표시 크기는 **바꾸지 않았다**(1440에서 538×810 CSS px). 원본이 커져서 업스케일이 사라졌기 때문.

## 수치

| 화면 | 그리는 크기(CSS) | 필요한 기기 픽셀 | 원본 | 배율(변경 전 → 후) |
|---|---|---|---|---|
| 1440 DPR1 | 538×810 | 538×810 | 1022×1538 | 0.70 → 0.53 |
| 1440 DPR2 | 538×810 | 1077×1621 | 1022×1538 | **1.41 → 1.05** |
| 1920 DPR1.5 | 646×972 | 969×1458 | 1022×1538 | **1.27 → 0.95** |
| 2560 DPR1 | 780×1174 | 780×1174 | 1022×1538 | 1.02 → 0.76 |
| 1366 DPR1 | 459×691 | 459×691 | 1022×1538 | 0.60 → 0.45 |
| 390 DPR2 | 238×359 | 477×718 | 1022×1538 | 0.62 → 0.47 |

영상 카드 좌우 여백(카드 폭 680, `.wrap` 내용 폭 기준):

| 뷰포트 | 좌 | 우 | 화면 중심 오차 |
|---|---|---|---|
| 1440 | 240 | 240 | 0 |
| 1366 | 240 | 240 | 0 |
| 1920 | 240 | 240 | 0 |
| 900 | 74 | 74 | 0 |
| 768 | 13 | 13 | 0 |
| 390 | 0 | 0 | 0 (카드가 폭을 꽉 채움) |

index.html: 639,621B → **794,906B** (+155,285B, 사진 base64 +151KB).

## 파일

- `shots/hero-quality/BEFORE-*` : 변경 전 원본(웹p·컷아웃PNG·index.html·src)
- `cmp-alpha-faces.png` : 765(좌, 업스케일) vs 1022(우) 1:1 비교
- `cutout-on-light.png` / `cutout-on-white.png` : 밝은 배경에서 헤일로 점검
- `before-*` / `after-*` `-pc1440-top.png`, `-face-dpr2.png` : 로컬 변경 전/후
- `live-1440-top.png`, `live-1366-top.png`, `live-390-top.png`, `live-1440-dpr2-top.png`, `live-1440-dpr2-face.png` : 라이브
- `live-1440-video.png`, `live-390-video.png`, `live-1440-video-playing.png` : 라이브 영상 카드
- `videoctx-before-pc1440.png` / `videoctx-after-pc1440.png` : 정렬 전/후 같은 위치
- 스크립트: `make_cutout.py`(수정), `cmp_cutout.py`, `measure_hero_img.py`, `measure_video_center.py`, `measure_layout_cmp.py`, `shot_hero_cmp.py`, `shot_video_cmp.py`, `shot_live_final.py`, `test_live_video_click.py`
