# 벨라리치(주) 홈페이지 시안

`index.html` — 단일 HTML 파일(이미지·로고 SVG 내장, 약 408KB). 더블클릭해 바로 열 수 있습니다.

## 구성
- `index.html` : 완성본 (배포용, 이 파일 하나로 동작)
- `_index.src.html` : 편집용 원본 템플릿 (`__DATA__`, `__LOGO__`, `__BOOK1__`, `__BOOK2__` 자리표시자 포함)
- `build.py` : 원본 + `assets/` + 상품 상세 데이터 → `index.html` 생성
- `make_logo.py` : 회사소개서 PDF(1쪽·8쪽)의 `BellaRich` 로고를 벡터 SVG로 추출
- `assets/logo.svg`, `assets/logo-symbol.html` : 추출한 로고(단독 파일 / 페이지 삽입용 스프라이트)
- `make_cutout.py` : 대표 프로필 원본 → Hero 컷아웃 생성 (아래 참고)
- `assets/ceo-hero.webp` : Hero 우측 대표 프로필 컷아웃 (베이지 재킷 + 아이보리 터틀넥, 알파 포함, 765×1150)
- `assets/book-1.webp` : 《부동산자산관리 마스터 과정 칼럼 모음집》 표지 (알라딘 공식 표지 500×707 → 700×990 WebP)
- `assets/book-2.webp` : 《법인으로 부동산을 움직여라》 표지 (교보문고 eBook 상품 표지, 480N251159780)
- `shots/` : 검증 스크린샷 (desktop-*, tablet-*, mobile-*)
- `shot.py` : 스크린샷·레이아웃 점검 스크립트
- `verify.py` : 중복 id·빈 링크·대체텍스트·모달 17개·가로 넘침·본문 타이포 실측 점검

## 솔루션 상세 페이지 `/plan/{슬러그}/`
- 첫 사례: **개인소득세 절세 플랜** → `https://bellarich7.github.io/plan/tax/`
- `_plan.src.html` : 상세 페이지 틀(템플릿). `build.py`의 `PLAN_PAGES` 목록에 한 줄 추가하면 `/plan/{slug}/index.html`이 생깁니다.
  - 본문은 그 플랜 모달(`build.py`의 `D['키']`)의 문구를 그대로 옮겨 씁니다(문구를 새로 쓰지 않음).
  - 디자인은 `_index.src.html`의 `<style>`을 `__CSS__` 자리에 그대로 넣어 메인 페이지와 같게 유지합니다.
  - 구성: 상단 상담 신청 버튼 → 플랜 설명 → (영상) → 하단 상담 신청 버튼, 상단 바에 `뒤로`·`홈으로`.
- **영상 넣는 법**: `assets/plan-tax.mp4`(썸네일을 쓰려면 `assets/plan-tax.jpg`)를 넣고 `python3 build.py`를 다시 돌리면 설명과 하단 버튼 사이에 영상 카드가 자동으로 생깁니다(파일이 없으면 영상 영역 자체가 페이지에 없음 — 빈 검은 박스 없음). 재생 방식은 로고 소개 영상과 같습니다: 썸네일 클릭 → 같은 자리에서 재생, `preload="none"`, `playsinline`, 소리 켜짐.
- `build.py`는 `bellarich-deploy/` 폴더가 있으면 `index.html`과 `plan/`을 그쪽으로 자동 복사합니다(커밋·푸시는 따로).

## 화면 구성 (순서)
1. Hero — 로고 배지 + 대표 프로필 컷아웃(우측) + `상담 신청`(구글 폼) 버튼
   - 버튼 아래 `.hero__cred` = About the CEO 머리 블록(eyebrow · 김자영 대표 · 역할 라인 · 인용구). 원래 `#about` 머리에 있던 것을 2026-11-24 4차에서 히어로로 올렸습니다. 2026-11-25 6차에서 이름/역할/인용구를 키우고 인용구를 두 줄 가운데 정렬로 바꿨습니다(사진은 90% 높이로 줄임).
2. 대표소개(CEO 김자영) — 자격 칩 4개 + 소개 2단 + 경력(현/전) + 저서(실제 표지 2권)
   - 경력은 2026-11-25 6차에서 `중개법인 리맥스 아리지파트너스 이사`를 빼고 간격을 압축(476→269px)했습니다. 점선 구분선은 없앴습니다.
   - Partners 블록은 2026-11-24 4차에서 이 자리에서 내렸고, 소스에 `<!-- PARTNERS (보류) ... -->` 주석으로 보관 중입니다(렌더링 안 됨). 되살리려면 주석만 풀면 됩니다.
3. 철학 — CFP/부동산/법인 벤다이어그램
4. 솔루션 메뉴 — 3개 플랜 탭(`tab-life` / `tab-suc` / `tab-fin`), 버튼형 탭 박스
   - 카드 하단은 **`— 자세히 · 상담 신청`** 한 줄(2026-11-25 11차). '자세히'를 누르면 모달, 옆의 '상담 신청'은 카드를 열지 않고 바로 구글 폼(새 탭)으로 갑니다. 카드 자체도 누르면 모달이 열립니다(`div.card[data-plan]` + 클릭 핸들러, 카드 안 링크는 예외).
   - `개인소득세 절세 플랜` 카드만 `data-href="/plan/tax/"` — '자세히'와 카드 본문 모두 상세 페이지로 이동합니다.
   - **법인CEO 생애주기별 부동산 플랜** (배지 07): 사옥/공장 · 가족법인 · CEO 은퇴 · 자녀 보금자리 · 개인소득세 절세 · 부동산 자산운용 + 07 상담 CTA
   - **부동산·가업 승계 플랜** (배지 05): 부동산 승계 플랜(01, `/plan/in-kind/`) · 자녀 창업법인 · 가업상속공제·증여특례 · 상속·증여 신탁 + 05 상담 CTA. 카드 위 흐름도는 2026-11-26 15시 통화 지시로 **없앴습니다**(지저분하고 폰에서 깨진다는 지적). 이제 `panel__note` 다음에 바로 카드가 옵니다. 설명 블록(`부동산승계 법인컨설팅`)은 같은 날 `/plan/in-kind/` 본문으로 옮겼습니다(`build.py` `PLAN_EXTRA`, 상세 페이지 클래스 `.pkind`).
   - **법인 재무·경영지원 플랜** (배지 06): 재무·경영지원 5 + 06 상담 CTA
   - 세 탭 모두 맨 끝에 `어떤 메뉴를 골라야 할지 모르겠다면` CTA 카드(폼 직행). life·suc은 카드 줄 전체를 쓰는 가로 띠, fin은 마지막 칸 카드입니다.
5. 상담신청 — `상담 신청` + `1분 법인 자산 건강검진`(drtardis123.github.io/BellaRich) + `카카오채널 친구 추가` 3버튼 + 전화·이메일·SNS(브랜드 로고 아이콘)
6. 푸터 — 회사 정보(서울 서대문구 이화여대길 38, 201-51 포함)

상담 유도는 **구글 폼 상담 신청서**(`https://docs.google.com/forms/d/1pvpYq1jJblmrxjHUQeo-nbmB_C3n87T8OCYVzhN5aZE/viewform`), 전화(`010-4825-5383`), 이메일(`bellarich7@naver.com`)로 연결됩니다. 카카오채널(`https://pf.kakao.com/_xkySDn`) 링크는 Contact 패널의 `카카오채널 친구 추가` 버튼, SNS 카카오 아이콘, 푸터 표기 세 곳에만 남겼습니다(2026-11-25 링크 정리). `build.py`는 편집용 `/edit` 주소가 들어가면 빌드를 중단합니다(사이트에는 응답 주소 `/viewform`만 사용).

### 상담신청 버튼 링크 (한 곳에서 교체)
`.contact__panel`의 1번 버튼(`상담 신청`) 주소는 **스크립트 맨 위 `var CONTACT_LINK`** 한 줄과 해당 `<a href>` 두 곳에 있습니다. 폼을 새로 만들면 `CONTACT_LINK`만 바꾸면 `[data-contact-link]`가 붙은 버튼에 자동 적용됩니다(HTML href는 JS 꺼짐 대비 기본값).
- 모달 하단 CTA(`상담 신청 →`) 17곳은 `build.py` 맨 위 `FORM` 상수 하나를 씁니다.
- 히어로 `상담 신청 ↗`, 세 탭 카드(08/04/08), 모바일 드로어 `FORM 상담 신청`은 각 `<a href>`에 같은 응답 주소가 직접 들어 있습니다. 폼 주소를 바꿀 때는 이 다섯 곳(+`CONTACT_LINK`, `build.py` `FORM`)을 함께 바꿔야 합니다. 현재 빌드에서 응답 주소는 24곳(앵커 23 + `CONTACT_LINK`), 모두 같은 값입니다.
- 내비 CTA `상담신청`과 모바일 드로어 `07 상담신청`은 `#contact` 섹션 이동입니다(폼 직행 아님).

### 카드 바탕색 (플랜별 톤)
`:root`의 세 변수만 바꾸면 탭별 카드 색이 바뀝니다.
```css
--plan-life:#14243F;  /* 탭1 · 남색 */
--plan-suc:#7F5423;   /* 탭2 · 앰버 */
--plan-fin:#455E4D;   /* 탭3 · 세이지그린 */
```
- 글자색은 `--card-on-dark-title` / `--card-on-dark-text` / `--card-on-dark-num`(탭2·3은 `#panel-suc`,`#panel-fin`에서 국소 조정).
- 상담 CTA 카드(`.card--cta`)만 세 탭 공통 **골드/크림 톤**으로 남겨 "상담으로 가는 카드"로 구분됩니다(2026-11-25 6차). 색은 `.panel`의 `--cta-bg` / `--cta-bg-h` / `--cta-bd` / `--cta-ink` / `--cta-ink-2` / `--cta-accent` 여섯 변수로, 탭별로 다른 색을 쓰려면 해당 패널에서 이 변수만 덮으면 됩니다. `.card--dark`(짙은 남색 CTA)는 다른 곳에서 쓰지 않지만 정의는 남겨 두었습니다.
- 대비(WCAG AA, 4.5:1 이상): 남색 12.8~14.6 / 앰버 5.0~6.2 / 세이지 5.6~6.7. 측정은 `python3 check_contrast.py`(→ `shots/card-tone-*.png`, `card-grid-*.png`).

## 저서 카드
- 판매처 링크(2026-11-25 8차): 표지 자체가 교보문고 eBook 페이지로 가고, 캡션 아래 `.book__links` 줄에 교보문고·알라딘 텍스트 링크가 있습니다. URL은 위 8차 항목 참고.
- 왼쪽 = 《부동산자산관리 마스터 과정 칼럼 모음집》 (김준수·김주연·김자영 공저, 도서출판 신기한마케팅, 2025년 1월, 전자책). 표지는 알라딘 저자 페이지의 공식 표지 `image.aladin.co.kr/product/35731/15/cover500/e972635468_1.jpg`(500×707)에서 받아 700×990 WebP로 최적화했습니다.
  - 이전에 왼쪽에 있던 《부동산 상속과 투자의 열쇠는 법인!》은 책이 아니라 회사 브로셔여서 카드에서 뺐습니다. 원본은 `assets/_src_book1-cover.png`, 이전 WebP는 `assets/book-1-brochure.webp`로 보관(사이트에서는 미사용).

## 수정 방법
1. `_index.src.html`(디자인/문구), `build.py` 안의 `DATA`(상품 상세 모달), `assets/logo-symbol.html`(로고) 중 해당 파일 수정
2. `python3 build.py` 실행 → `index.html` 재생성

## Hero 컷아웃 다시 만들기
```bash
python3 make_cutout.py     # assets/_gen_beige.png → assets/ceo-hero.webp (+ _src_ceo-cutout-beige.png)
python3 build.py
```
스튜디오 회색 배경을 지우는 순서:
1. 정규화 컨볼루션으로 배경면을 추정(비네트까지 따라감) → 배경과의 색거리로 실루엣 추출
2. 실루엣 안쪽 코어를 4px 깎고, 그 주변 밴드에서 배경색과 피사체색의 선형 혼합으로 알파를 풀어냄(경계 회색 테두리 방지)
3. 반투명 경계 픽셀의 색을 안쪽 코어 색으로 밀어 넣어(색 전파) 네이비 배경 위 흰 테두리 제거
4. 실루엣 안쪽 구멍은 20px 이상만 메움(머리카락 사이 배경 틈은 비워 둠)
- 하단 페이드는 넣지 않습니다. Hero 이미지는 하단이 히어로 섹션 바닥과 맞닿아 잘리므로, `.hero__media::after`의 짧은 그라데이션(3.4%)만으로 경계를 정리합니다.
- 원본: `assets/_gen_beige.png` (베이지 재킷 + 아이보리 터틀넥, 1022×1538). 이전 검은 터틀넥 컷아웃은 `assets/ceo-hero--navy-black.webp`, `assets/_src_ceo-cutout.png`로 보관.

### PC 히어로 사진 크기·해상도 (2026-11-26 2차)
PC 히어로 사진은 **466 CSS px 폭**으로 그립니다(예전 700의 2/3). 높이는 84% 그대로라 1920×1080에서 466×578 CSS px이고, 오른쪽 끝에서 본문 폭(1240px) 밖 여백 절반만큼(최대 320px) 들여 가운데 쪽에 섭니다. 2배 화면도 932 기기 px면 충분해 원본 1086px 안에 들어오므로, 예전 1400px 2배 파일은 더 쓰지 않습니다(보관: `shots/hero-quality/2026-11-26-size/ARCHIVE-ceo-hero-2x-1400x1738.webp`).

화면 배율마다 그 크기에 딱 맞춰 만든 파일을 물립니다(가로 1081px 이상). 브라우저가 줄이거나 늘리지 않아 가장 또렷합니다.

| 배율 | 파일 | 해상도 | 용량 |
|---|---|---|---|
| 1배 | `assets/ceo-hero-pc-1x.webp` | 466×578 | 40KB |
| 1.5배 | `assets/ceo-hero-pc-15x.webp` | 699×868 | 86KB |
| 2배 | `assets/ceo-hero-pc-2x.webp` | 932×1157 | 142KB |

1배·모바일(가로 1080px 이하)은 인라인 `--ceo-img`(1086×1348) 그대로라 렌더 결과·용량 변화가 없습니다.
```bash
python3 make_hero_pc.py     # assets/_cutout_ceo-slim.png → ceo-hero-pc-{1x,15x,2x}.webp
cp assets/ceo-hero-pc-*.webp ../bellarich-deploy/assets/   # build.py는 자산을 복사하지 않음
```
- 샤픈 `SHARP`(0.22)·품질 `WEBP_Q`(92)·마테 `MATTE`(orig)는 환경변수. 사진 폭을 또 바꾸면 `TIERS`에 새 폭을 넘겨 같은 방식으로 다시 만들면 됩니다.
- 경위·계측·한계: `shots/hero-quality/2026-11-26-size/README.md`

## 경력 목록 시안 (기울임)
`현 · Current` / `전 · Past` 목록의 기울임은 `:root`의 두 변수로만 바꿉니다(기본 C안 = 기울임 없음).
```css
:root{--career-style:normal;--career-past-style:normal}
/* A안 전체 기울임: --career-style:italic */
/* B안 Past만 기울임: --career-past-style:italic */
```
비교 캡처: `shots/career-A.png` / `career-B.png` / `career-C.png` (`python3 career_variants.py`로 재생성).
경력 목록은 본문보다 한 톤 누른 색(#4C5666, 아이보리 위 7.0:1)으로 두고 `현)`/`전)` 표기만 진하게 남겼습니다.

## 타이포그래피 기준 (2026-11-24 3차 수정)
"글씨가 작고 진하지 않다"는 요청으로 본문 계열을 한 단계 키우고 진하게 잡았습니다.
- 색: `--muted` #5C6577 → #2F3948, `--muted-l` #8A8F9B → #55606F, `--gold-d` #A8886A → #9A7B57, 네이비 배경 위 본문 rgba(237,234,227,.6~.76) → rgba(242,239,232,.88~.92)
- 웨이트: body 300 → 400, 카드 제목·라벨 400 → 500, 강조 `<b>` 400 → 600
- 크기: body 16 → 17px, `.lead` 15~16.5 → 16.5~18px, 카드 본문 12.5~13 → 13.5~14px, 카드 제목 16~20 → 17~21px, 경력·승계 본문 13.5 → 14.5~15px, 모달 본문 13.5 → 15px, 푸터 11.5 → 12.5px
- 제목(세리프 h1/h2/h3)은 300 계열을 유지해 위계를 지켰습니다.
- 1024px 구간은 히어로가 한 화면에 들어오도록 h1 clamp·서브카피 폭·facts 간격을 따로 잡았습니다.

## 로고 다시 만들기
```bash
python3 make_logo.py     # PDF → assets/logo.svg + assets/logo-symbol.html
python3 build.py
```
로고는 3개 색 그룹(건물 실루엣·Bella·Rich)으로 되어 있고, 각 그룹 색은 CSS 변수
`--br-blk`, `--br-let`, `--br-gold`로 바꿀 수 있습니다.
- 어두운 배경(Hero·투명 네비·푸터): 실루엣 `#F6F2EA`(아이보리), 글자 `--navy`(실루엣에 뚫린 형태), `Rich` `#C5A47E`
- 아이보리 배경(스크롤 후 고정 네비): 실루엣 `#0B1933`, 글자 흰색, `Rich` `#C5A47E`

## 스크린샷 재촬영
```bash
PLAYWRIGHT_BROWSERS_PATH=/workspace/.cache/ms-playwright \
LD_LIBRARY_PATH=/workspace/.libs/root/usr/lib/x86_64-linux-gnu python3 shot.py
```
(크로미움은 `/workspace/.cache/ms-playwright`에, 필요한 시스템 라이브러리는
`/workspace/.libs/root`에 풀어 두었습니다. 새 환경이라면 `python3 -m playwright install chromium`
후 libnspr4·libnss3 등 deb를 풀어 `LD_LIBRARY_PATH`로 연결해야 합니다.)

## 6차 수정 (2026-11-25, 사장님 지시)
1. **히어로 About the CEO**: 이름 `clamp(17~20px)` → `clamp(24~34px)`, `대표` 11.5 → `clamp(14~18px)`, 역할 라인 13 → `clamp(14~15.5px)`, 인용구 14~15.5 → `clamp(19~24px)` 두 줄 가운데 정렬(좌측 보더→중앙 정렬). 대표 사진은 히어로 높이의 90%로 줄여(높이 900px에서 810px, 실제 픽셀 폭 599→539) 글자 자리를 확보. 히어로 한 화면 수용 유지(900/800/768).
2. **경력**: `중개법인 리맥스 아리지파트너스 이사` 삭제(현 6→5항목). li 세로 패딩 9→2px, line-height 1.7→1.45, 점선 보더 제거, h4 아래 18→6px, `.career` margin-top 58→16·padding-top 44→16, 열 간격 54→32px. 경력 높이 476→269px(1440).
3. **섹션 여백**: `.section` 129.6→95px(1440), 칩 아래 36→24, 저서 블록 위 72+44→40+28. About 섹션 1620→1241px(-23.4%), 390에서 2000→1552px.
4. **솔루션 탭**: 버튼형 박스(3칸 그리드, 종이색 배경·1px 테두리·5px 라운드), 활성 탭은 남색 채움+골드 하단선. 라벨 `clamp(17~21px)`/500(활성 600), 배지 13px 600. 탭 위에 `플랜 버튼을 누르면 각 플랜의 메뉴가 열립니다` 안내 한 줄(`.sol-hint`).
5. **솔루션 글씨 진하게**: 카드 본문 `rgba(245,241,233,.96)` → `#FBF7EE`(불투명), 제목 `#FBF8F1` → `#FFF`, weight p 400→500·h3 400→600, 번호/자세히 톤업, `panel__note` `#3A4351`→`#0F1B30`/600, 모달 본문 `--muted`→`--ink`. 명암비는 앰버 5.5→6.15, 세이지 5.96→6.63, 남색 12.78→14.51(본문).
6. **승계 탭**: 2026-11-26 `부동산 현물출자 법인전환` 카드를 `부동산 승계 플랜`으로 이름을 바꿔 이 탭 01번으로 옮겼습니다(기존 3개는 02~04). 탭 이름은 `부동산·가업 승계 플랜`. 긴 설명 블록은 `/plan/in-kind/` 본문으로 갔고, 홈 카드 위 3단계 흐름(`.suc-flow`)은 같은 날 오후 통화 지시로 완전히 제거했습니다(라벨·노드·화살표·CSS·미디어쿼리까지). `/plan/in-kind/`의 `.pkind` 블록은 본문 `#3A4351`→`#16202E`(weight 400→500), 금색 강조 `#7A5B36`→`#5C4018`로 올려 모든 글자가 크림 배경에서 8.5:1 이상이 되게 했습니다. 패널 배경은 `#F2EBDD`(원래) → `#F7F2E8`(글씨 눌림 지적) → 같은 날 15:20 "한 단계 약하게 진하게" 지시로 **`#F0E7D6`**가 최종입니다(글자색·굵기·흰 카드는 그대로, 최저 대비 7.77:1).
7. **CTA 카드**: 세 탭 모두 `어떤 메뉴를 골라야 할지 모르겠다면`(폼 직행). life 07·suc 05·fin 06, 탭 배지도 같이. 색은 세 탭 공통 골드/크림(`--cta-*`).
8. **드로어 메뉴 버그**: `body.is-locked` 때문에 드로어 앵커(`#about` 등)가 홈으로만 가던 문제 — 클릭을 JS로 받아 `closeMenu()`로 잠금을 풀고 rAF 뒤 직접 스크롤(+`history.replaceState`). `prefers-reduced-motion`에서는 즉시 이동. 헤더에 가려지지 않게 `section[id]{scroll-margin-top}` 보정. `verify.py`의 `ANCHORS` 검사가 드로어(390)/헤더(1440) 네 앵커를 확인합니다.

보조 스크립트: `measure_6th.py`(히어로·경력·About 높이), `measure_before_6th.py`(5차 상태 재현 비교), `check_drawer.py`(앵커 이동 단독 점검), `check_contrast_6th.py`(탭·카드 명암비 전/후), `shot_6th.py`(6차 캡처).

### 2026-11-25 7차 (영상 재생·히어로 로고·상담 버튼 문구)
1. **히어로 상단**: `.hero__top`을 모바일(≤900px)에서도 가로 배치로 바꿔 **로고 왼쪽 / 영문 캡션 오른쪽, `align-items:flex-start`** — 로고 윗선 = 캡션 첫 줄 윗선(박스 top 기준 0px 차, 텍스트 첫 줄 기준 2px). 390px에서 캡션 2줄, 360px에서 3줄. 로고 크기는 그대로(41px/143~155px 폭)이고, 좁은 폭에서 자리를 만들려고 **모바일에서만 두 장식 헤어라인**(`.hero__brand::after`, `.hero__eyebrow::before`)을 숨깁니다. 데스크톱은 그대로.
2. **캡션–h1 여백**: 데스크톱 `.hero__top` margin-bottom `clamp(22,3vw,34)` → `+14px`, 모바일 18 → 32px. 늘어난 높이는 히어로 하단 패딩에서 상쇄(`calc(100vh - 828px)`, `calc(100vh - 732px)`)해 1440×900·1366×768에서 히어로 높이 = 뷰포트 유지.
3. **영상 카드**: (10차에서 사이트 안 HTML5 플레이어로 교체 — 아래 10차 항목 참고. 7차의 IFrame API 방식은 폐기) 클릭 시 `youtube-nocookie` iframe 대신 **YouTube IFrame Player API**(`https://www.youtube.com/iframe_api` + `new YT.Player`)로 교체. `onReady`에서 `playVideo()`, `playerVars{autoplay:1,playsinline:1,rel:0}`. 재생이 시작되지 않으면(약 1.5초 뒤 `getPlayerState()≠1`, 버퍼링 3은 한 번 더 대기) 또는 `onError`(101/150/153) 시 카드 아래 `#videoFallback` 안내(→ `https://youtu.be/k9K_hEMHeXk`)를 띄웁니다. 클릭 전 외부 요청 0 유지, 썸네일(`assets/yt-card.jpg`)은 그대로.
4. **상담 2줄 버튼 문구**: `개인 소득세 절세 시뮬레이션` → **`내 소득세 절세 금액 알아보기`**(링크·테두리형 스타일 유지, 모바일 300×56·PC 385×56 한 줄).

보조 스크립트: `test_video.py <url> <prefix>`(영상 카드 클릭 전/후 요청·상태 추이·대체 안내 점검), `exp_hero.py`·`exp_top.py`(히어로 배치 실험용).

### 2026-11-25 8차 (저서 표지·판매처 링크)
- **표지 클릭 = 교보문고 eBook 페이지(새 탭)**. `.book__cover`를 `<span>` → `<a href target="_blank" rel="noopener" aria-label="《제목》 교보문고에서 보기">`로 바꿨습니다. `display:block`·그림자·호버 리프트·`::after` 오버레이는 그대로이고, 키보드 포커스용 `.book__cover:focus-visible` 외곽선만 추가.
  - 1번 책(칼럼 모음집) 교보 `E000011001248` / 2번 책(법인으로 부동산을 움직여라) 교보 `E000012252690`.
- **캡션 아래 링크 줄**(`.book__links`, 12.5px·letter-spacing .04em·muted·hover 골드): 1번 책 `교보문고 ↗ · 알라딘 ↗`(알라딘 `ItemId=357311502`), 2번 책은 `교보문고 ↗`만 — 알라딘 검색 0건(전자책 포함)이라 링크를 넣지 않았습니다. 다시 확인할 때는 알라딘 검색 결과의 `전자책 (0)`을 보세요.
- 390·360에서 링크 줄 한 줄 유지(`white-space:nowrap`), 가로 넘침 0. 점검: `chk_booklinks.py [url] [tag]`(href·target·aria-label·줄 높이·넘침·콘솔 에러 + `shots/booklinks-<tag>-<폭>.png`).

### 2026-11-25 9차 (저서 두 권 순서 맞바꾸기)
- 사장님 요청: "《법인으로 부동산을 움직여라》랑 앞에 있는 《부동산자산관리 마스터 과정 칼럼 모음집》, 이거를 순서를 바꾸면 어떨까?" → **왼쪽(먼저) 《법인으로 부동산을 움직여라》, 오른쪽(뒤) 《부동산자산관리 마스터 과정 칼럼 모음집》**.
- `_index.src.html`의 저서 섹션에서 `<figure class="book">` 블록 두 개를 통째로 맞바꿈(표지 링크·이미지·캡션·`.book__links` 함께 이동). 그리드 CSS·`books__note`·다른 섹션은 손대지 않음.
- 바뀐 DOM 대조로 확인: `_index.src.html` vs 이전 배포본에서 저서 figure 두 개(그리고 그 사이 줄바꿈)만 다르고 나머지 HTML은 동일.
- 검증 `chk_booklinks.py https://bellarich7.github.io/?v=1125j live`: 1번 figure 표지 = `E000012252690`(《법인으로 부동산을 움직여라》), 2번 = `E000011001248`(《부동산자산관리 마스터 과정 칼럼 모음집》). 표지 링크 2개·캡션 링크 3개(교보 2·알라딘 1) href 그대로, 390/1440 링크 줄 한 줄, 가로 넘침 0, 콘솔 에러 0, 실패 요청 0. 세 URL 모두 HTTP 200.
- 커밋 `30df8b2` (main, `bellarich7/bellarich7.github.io`). 캐시 주소 `?v=1125j`.
- 참고: 8차 설명의 "1번 책 = 칼럼 모음집 / 2번 책 = 법인으로 부동산을 움직여라"는 이번 9차로 번호가 뒤집혔습니다(1번 = 법인…).

### 2026-11-25 10차 (소개 영상을 사이트 안에서 재생)
- 사장님: "유튜브 영상 전혀 재생 안 되고, 누르면 까맣게 화면이…" → 유튜브로 나가던 카드를 **사이트 안 HTML5 플레이어**로 바꿨습니다.
- **영상 파일**: 원본 `intro-0718.mp4`(1920×1080, 8분 00초)를 720p H.264/AAC·faststart로 인코딩한 `assets/intro.mp4`(25.4MB)를 사이트에 올렸습니다(moov 앞배치). 라이브: `https://bellarich7.github.io/assets/intro.mp4` → 200, `video/mp4`, `accept-ranges: bytes`.
- **DOM**: `.video-card` 안에 `.video-card__stage`를 두고, 그 안에 ① 썸네일 버튼(`#videoPlay`, 기존 `background-image` 데이터URI·재생 원·호버 그대로) ② `<video id="videoPlayer" controls playsinline preload="none" data-poster="assets/yt-card.jpg?v=…">` + `<source src="assets/intro.mp4?v=…" type="video/mp4">`. 카드 테두리·그림자·캡션 문구·"YouTube에서 보기" 링크는 그대로입니다.
- **동작**: 버튼 클릭 → `.is-playing` 추가(썸네일 숨기고 video 표시, hover 리프트만 끔) → `poster` 지정 → `preload='auto'` → `play()`. 자동재생·음소거 강제 없음(소리 켜진 채 재생). `play()`가 거부되면 네이티브 컨트롤로 재생할 수 있게 둡니다.
- **preload="none"인 이유**: `preload="metadata"`로 두면 크롬이 누르기 전에 **6.9MB를 미리 받아**(readyState 4) 모바일 데이터가 샙니다. 지금은 누르기 전 영상 전송량 **0바이트**, 포스터도 클릭할 때 로드합니다.
- **검증**: `chk_video_range.py <url> <tag>`(Range 지원 서버로 GitHub Pages와 같은 조건 재현, 1440·390·360에서 터치 탭 → duration 480.3·currentTime 5초·프레임 캔버스 분산 확인·스크린샷). `shot_video_final.py`는 보고용 캡처.
- 결과(라이브 `?v=1125k`): 3개 폭 모두 누르기 전 요청 0 → 탭 한 번에 재생(muted=false·volume 1) → 0:05/8:00 프레임 표시, 콘솔 에러 0·실패 요청 0·가로 넘침 0. 커밋 `ac7e0bc`.
- iPhone Safari는 이 환경에 WebKit이 없어 직접 확인하지 못했습니다. `playsinline`+클릭 핸들러 안 `play()`는 iOS에서 한 번에 재생되는 표준 방식입니다. 확인되면 알려 주세요.

### 2026-11-25 11차 (카드 '상담 신청' 링크 · 절세 플랜 상세 페이지)
1. **솔루션 카드 15개 하단**: `— 자세히 · 상담 신청`. '상담 신청'은 버튼 박스 없이 '자세히'와 같은 타이포(12.5px·600·letter-spacing .1em)의 텍스트 링크이고, 색은 카드별 `--card-more`, 호버에 밑줄. 두 링크 모두 `min-height:44px`로 터치 영역을 확보했습니다(390·1440 실측 44px, 같은 줄).
2. **카드 마크업**: `<button class="card" data-plan>` → `<div class="card" data-plan>` + 안쪽 `.card__act`(자세히·구분점·상담 신청). `<a>`를 `<button>` 안에 넣을 수 없어 바꿨고, 카드 본문 클릭 = 모달은 그대로입니다(카드 div의 클릭 핸들러 + `e.target.closest('a')` 가드). 카드 안 '자세히'는 `<button>`, '상담 신청'은 `<a data-contact-link target=_blank>`.
3. **개인소득세 절세 플랜 카드**: `data-href="/plan/tax/"` + '자세히'가 `<a href="/plan/tax/">`. 카드 본문을 눌러도 상세 페이지로 갑니다.
4. **상세 페이지** `/plan/tax/`: 위 “솔루션 상세 페이지” 항목 참고. 문구는 모달(`D['inv5']`)에서 그대로, 모달 하단 CTA만 제외.
5. 검증: `chk_cardlinks.py`(카드 15개 두 링크·한 줄·44px·href), `chk_plan_flow.py`(자세히→상세, 카드 본문→모달/상세, 카드 안 상담 신청→새 탭 폼·모달 안 열림, 상세 상하단 CTA), `chk_scope.py`(메인 DOM 영역별 동일성), `chk_pixscope.py`(히어로·대표소개·철학·솔루션 헤드·탭 픽셀 동일), `shot_plan.py`·`shot_plan.py <live url>`(캡처).

### 2026-11-25 12차 (솔루션 상세 페이지 15개 전체 적용)
- 사장님(통화): "이 세팅으로 나머지도 모든 다 바꿔주고, 풀로 가득 차게 하고, 맨 위에는 색깔로 진하게 해서, 어쨌든 이 세팅은 똑같이 가자." → `/plan/tax/` 틀을 그대로 복제해 **15개 플랜 상세 페이지**를 만들고 메인 카드 '자세히'를 전부 연결했습니다. 커밋 `7323b0b`.
- **한 곳에서 관리**: `build.py`
  - `PLAN_PAGES` — 슬러그·카드번호·갈래(group)·카드 요약·영상 여부. 페이지 추가는 여기 한 줄.
  - `PLAN_ACCENT` / `PLAN_GROUP` — 상단·하단 색과 갈래 이름. 생애주기 `#0B1933`(남색) · 부동산·가업 승계 `#5C3B16`(앰버) · 법인재무·경영지원 `#2F4238`(세이지). 색을 바꾸려면 이 세 줄만.
  - `SUC_NAME` / `SUC_SHORT` — 승계 탭 이름 한 곳(정식 이름 / 내비 짧은 이름). `_index.src.html`의 `__SUC_NAME__`·`__SUC_SHORT__`와 `PLAN_GROUP`이 이 값을 씁니다.
  - `PLAN_EXTRA` — 상세 페이지에만 붙는 본문(현재 `/plan/in-kind/`의 부동산 승계 구조 블록).
  - `PLAN_VIDEO` — 유튜브 ID·제목. **영상 교체는 이 한 곳**(생성 HTML에서는 `data-video-id` 한 곳).
  - 틀은 `_plan.src.html`, 본문은 메인 모달 데이터(`D`)를 그대로 옮깁니다(모달 하단 CTA만 제외). 새 문구를 창작하지 않습니다.
- **주소**: `/plan/office/ · family-corp · retirement · home-for-kids · tax · asset`(생애주기 01~06) `/ in-kind · startup-succession · family-business · trust`(부동산·가업 승계 01~04) `/ credit · governance · incorporation · welfare-fund · ma`(법인재무·경영지원 01~05). 페이지 제목·H1은 방문자가 누른 카드 제목과 같게 맞췄습니다. `in-kind` 슬러그는 카드 제목을 바꾼 뒤에도 주소를 유지하려고 그대로 둡니다.
- **메인 카드**: `<button class="card__more">자세히</button>` → `<a class="card__more" href="/plan/<slug>/">`. 카드 본문 클릭 = 기존 모달 유지. 절세 플랜 카드만 기존처럼 카드 전체가 페이지로 이동.
- **영상(`/plan/tax/`)**: 본문 마지막과 하단 상담 신청 사이. 누르기 전 유튜브 요청 0(썸네일도 받지 않음), 누르면 같은 자리에 `youtube-nocookie.com/embed/<id>` iframe이 16:9로 들어와 재생. 카드 캡션에 원제목 + "YouTube에서 보기".
- **/check/ 수정**: 카카오 공유 `imageUrl`이 없는 `og-image.svg`(404)를 가리키던 한 줄 → `og-image.png`.
- **검증**: `chk_plan_all.py`(15개 페이지 ×1440·390 — 가로 넘침·상단/하단 색·상담 버튼 2개·영상 클릭 전 요청 0 → iframe·16:9·콘솔). 라이브: 15개 모두 200, 카드 링크 15개 정확, 390 가로 넘침 0, 영상 실제 재생(11:44) 확인.

## 확인된 사항 (2026-11-24 4차 수정 후)

## 확인된 사항 (2026-11-24 4차 수정 후)
- 1440·1280·1024·820·390px 모두 가로 스크롤 없음 (마퀴 밴드는 의도된 overflow)
- Hero: 1440×900·1366×768·1280×800·1150×800·1024×768·1024×900에서 `.hero__cred`(인용구) 줄까지 한 화면에 들어옴
  - 인용구 하단 y: 850 / 719 / 730 / 715 / 714 / 797 (뷰포트 900·768·800·800·768·900)
- 카드 17개 모달 전부 열림/ESC 닫힘, 3탭 전환·키보드(←→/Home)·모바일 세로 탭 정상
- JS 콘솔 에러 0, 중복 id 0, 빈 링크 0, 이미지 대체텍스트 누락 0, 상담 링크 22곳 모두 폼 응답 주소(`/viewform`)로 동일
- 대표소개 저서 카드: 두 표지 252×356 동일 크기·상단 정렬, 캡션 한 줄 유지
- 보조 스크립트: `check_hero_fit.py`(첫 화면 수용), `measure_hero.py`(히어로 요소 y), `check_contrast.py`(카드 대비), `career_variants.py`(A/B/C)
