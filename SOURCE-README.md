# 벨라리치(주) 홈페이지 — 제작 소스 (source 브랜치)

이 브랜치는 **벨라리치 홈페이지의 제작 소스 전체**를 보관하는 곳입니다.
서비스 중인 사이트 파일은 같은 저장소의 `main` 브랜치에 있고, 이 `source` 브랜치는 사이트 공개에 쓰이지 않습니다(GitHub Pages는 `main`만 서비스).
피클(Pickle) 같은 도구가 없어져도, 이 계정(`bellarich7`)만 있으면 사이트를 그대로 다시 만들고 배포할 수 있도록 남겨 둔 백업입니다.

- 저장소: https://github.com/bellarich7/bellarich7.github.io
- 소스 브랜치: `source` (이 문서가 있는 브랜치)
- 서비스 브랜치: `main`
- 백업일: 2026-11-27

## 사이트 구성

- 도메인: **bellarich.co.kr** — 가비아에서 구입한 도메인을 GitHub Pages에 연결했습니다(`main` 브랜치의 `CNAME` 파일에 `bellarich.co.kr` 기재, 가비아 DNS에서 GitHub Pages 주소를 가리킴).
- 호스팅: **GitHub Pages** (저장소 `bellarich7/bellarich7.github.io`, `main` 브랜치 루트를 그대로 서비스)
- 기본 주소: https://bellarich7.github.io/ , https://bellarich.co.kr
- 페이지 구성:
  - `/index.html` — 메인(한 파일에 이미지·로고가 base64로 들어간 단일 HTML)
  - `/plan/{슬러그}/index.html` — 솔루션 상세 페이지 15개 (tax, in-kind, retirement, office, family-corp, governance, trust, incorporation, startup-succession, family-business, home-for-kids, welfare-fund, ma, asset, credit)
  - `/check/` — 1분 법인 자산 건강검진
  - `/card/` — 전자명함

## 폴더 안내

| 경로 | 설명 |
| --- | --- |
| `_index.src.html` | 메인 페이지 편집용 원본 템플릿 (`__DATA__`, `__LOGO__`, `__BOOK1__` 등 자리표시자 포함) |
| `_plan.src.html` | 솔루션 상세 페이지 공통 틀 |
| `build.py` | 빌드 스크립트. 원본 + `assets/` → `index.html`, 그리고 `/plan/*/index.html` 15개 생성 |
| `build_check.py` | 빌드 결과 점검 |
| `assets/` | 로고·대표 사진·책 표지·영상(`intro.mp4` 로고 소개 영상, `tax-venture.mp4` 절세 플랜 영상) 등 실제 사이트에 쓰는 파일 |
| `plan/` | 빌드로 만들어진 상세 페이지 결과물 |
| `check/`, `card/` | 건강검진·전자명함 페이지(원본과 결과물) |
| `shots/` | 작업 중 화면 검증 스크린샷 |
| `tmp/` | 작업 중 임시 파일(대표 사진 원본·시안 등) |
| `check_*.py`, `chk_*.py`, `measure_*.py`, `shot_*.py`, `verify_*.py`, `make_*.py`, `test_*.py` 등 | 제작 중 레이아웃 실측·캡처·점검에 쓴 보조 스크립트. 사이트 동작에는 필요 없지만, 나중에 직접 고칠 때 참고용으로 전부 넣어 두었습니다. |
| `index.html` | 빌드 결과물(메인). `build.py`를 돌리면 새로 만들어집니다. |

`README.md`에 페이지 구성·문구·색·링크를 바꾸는 방법이 자세히 적혀 있습니다. 수정 전에 먼저 읽어 보세요.

## 다시 빌드하고 배포하는 방법

준비물: Python 3 (외부 패키지 없이 표준 라이브러리만 씁니다), git.

1. 저장소를 두 브랜치 모두 받습니다.

   ```bash
   git clone https://github.com/bellarich7/bellarich7.github.io.git bellarich-deploy
   cd bellarich-deploy && git checkout main
   cd ..
   git clone -b source https://github.com/bellarich7/bellarich7.github.io.git bellarich-site
   ```

   두 폴더가 **나란히** 있어야 합니다(`bellarich-site`와 `bellarich-deploy`가 같은 상위 폴더 안).

2. 소스를 고친 뒤 빌드합니다.

   ```bash
   cd bellarich-site
   python3 build.py
   ```

   `index.html`과 `plan/*/index.html`이 새로 만들어지고, 옆의 `bellarich-deploy/` 폴더로 자동 복사됩니다.

3. 배포합니다.

   ```bash
   cd ../bellarich-deploy
   git add -A
   git commit -m "사이트 수정"
   git push origin main
   ```

   몇 분 안에 https://bellarich.co.kr 에 반영됩니다.

4. (선택) 소스 브랜치도 갱신하려면 `bellarich-site`에서 커밋 후 `git push origin source` 하면 됩니다.

## 되살리는 순서 (사이트가 사라졌을 때)

1. GitHub에서 새 저장소를 만들고(또는 이 저장소 사용) 이 `source` 브랜치를 받습니다.
2. 위 2번처럼 `python3 build.py`를 돌리면 사이트 전체가 다시 만들어집니다(영상·이미지 포함, 외부 서비스 필요 없음).
3. 결과물을 `main` 브랜치 루트에 올리고, 저장소 Settings → Pages에서 `main` 브랜치를 서비스 대상으로 지정합니다.
4. 도메인을 쓰려면 `CNAME` 파일에 `bellarich.co.kr`을 두고, 가비아 DNS에서 GitHub Pages가 안내하는 레코드(A 레코드 4개 + `www` CNAME)를 설정합니다.

## 참고

- 상담 신청은 구글 폼(`docs.google.com/forms/.../viewform`)으로 연결됩니다. 폼 주소를 바꿀 때는 `build.py`의 `FORM` 상수와 `_index.src.html`의 버튼 링크를 함께 바꿔야 합니다(자세한 위치는 `README.md`).
- `build.py`는 편집용 `/edit` 주소가 들어 있으면 빌드를 중단합니다(사이트에는 응답 주소 `/viewform`만 사용).
- 이 브랜치에는 개인정보나 비밀번호 같은 민감 정보가 들어 있지 않습니다. 사이트에 쓰인 연락처(전화·이메일)는 이미 공개된 사이트 내용과 같습니다.
