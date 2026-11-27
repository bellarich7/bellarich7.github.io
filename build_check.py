#!/usr/bin/env python3
"""Build bellarich-site/check/index.html from the original BellaRich diagnostic page.

The original page lives at https://drtardis123.github.io/BellaRich/ (third-party account).
This script makes a self-hosted copy that can be served from
https://bellarich7.github.io/check/ :

  1. inlines quiz-data.js and venn-diagram.png so the page needs no sibling files
     (og-image.png stays a sibling file, only for social preview meta tags),
  2. points canonical / og / twitter / JSON-LD / Kakao share image at the new path,
  3. points the data-collection endpoint at SUBMIT_ENDPOINT. It is set to the
     1분 진단 backend Apps Script web app (bellarichtest@gmail.com, deployed for
     "anyone"), so result/exit/rating/kakao payloads are sent there; with '' every
     send function returns early and nothing leaves the browser.

Run:  python3 bellarich-site/build_check.py <raw.html> <source-dir>
      raw.html     – saved copy of https://drtardis123.github.io/BellaRich/?v=2
      source-dir   – directory holding quiz-data.js and venn-diagram.png

Output: bellarich-site/check/index.html (next to this script).
"""
import base64
import pathlib
import re
import sys

NEW_BASE = "https://bellarich7.github.io/check/"
OLD_BASE_RE = re.compile(r"https?://(?:drtardis123|DrTardis123)\.github\.io/BellaRich/")

ENDPOINT_BLOCK_OLD = """  // ====== DATA COLLECTION CONFIG ======
  // Google Apps Script Web App URL — replace with your deployed URL.
  // Setup guide: see user guide provided
  // Leave empty string '' to disable data collection (test still works).
  const APPS_SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbwDYShx9JqX1H86FroITA1yd-b8w-F-OMdFNMuOLF7Os4dSB0M-wPQFmcUTRJUDNkjz/exec';
"""

ENDPOINT_BLOCK_NEW = """  // ====== DATA COLLECTION CONFIG ======
  // 결과·이탈·만족도·카카오 클릭 데이터를 받을 곳. 자영님 소유의 수신처가 정해지면
  // 아래 SUBMIT_ENDPOINT 에 주소를 넣으면 그때부터 전송이 시작된다.
  //
  //   SUBMIT_ENDPOINT = ''                 → 아무것도 전송하지 않음
  //   SUBMIT_ENDPOINT = 'https://script.google.com/macros/s/..../exec'
  //                                        → Google Apps Script 웹앱(JSON POST, no-cors)
  //   SUBMIT_ENDPOINT = 'https://docs.google.com/forms/d/e/.../formResponse'
  //                                        → Google Form 이면 필드명(q1, email …)이
  //                                          buildPayload() 의 키와 맞아야 한다.
  //
  // 수신 형식: JSON 본문(Content-Type: application/json 또는 text/plain).
  //   type: 'result' | 'exit' | 'rating' | 'kakao' 구분 필드가 들어 있다.
  //
  // 수신처: bellarichtest@gmail.com 계정의 1분 진단 백엔드 Apps Script 웹앱
  //   (실행 계정 bellarichtest@gmail.com, 액세스 '모든 사용자', 배포 URL 고정)
  //   자료는 그 계정의 스프레드시트에 쌓이고, 신청자에게 결과 메일이 나간다.
  const SUBMIT_ENDPOINT = 'https://script.google.com/macros/s/AKfycbwDYShx9JqX1H86FroITA1yd-b8w-F-OMdFNMuOLF7Os4dSB0M-wPQFmcUTRJUDNkjz/exec';
"""


def inline_quiz_data(html: str, source_dir: pathlib.Path) -> str:
    quiz = (source_dir / "quiz-data.js").read_text(encoding="utf-8")
    if "</script" in quiz.lower():
        raise SystemExit("quiz-data.js contains </script>; cannot inline safely")
    tag = '<script src="quiz-data.js"></script>'
    if tag not in html:
        raise SystemExit("quiz-data.js script tag not found")
    return html.replace(tag, "<script>\n" + quiz + "\n</script>")


def inline_venn(html: str, source_dir: pathlib.Path) -> str:
    png = base64.b64encode((source_dir / "venn-diagram.png").read_bytes()).decode("ascii")
    marker = 'src="venn-diagram.png"'
    if marker not in html:
        raise SystemExit("venn-diagram.png img tag not found")
    return html.replace(marker, 'src="data:image/png;base64,' + png + '"')


def rewrite_endpoint(html: str) -> str:
    if ENDPOINT_BLOCK_OLD not in html:
        raise SystemExit("endpoint config block not found verbatim")
    html = html.replace(ENDPOINT_BLOCK_OLD, ENDPOINT_BLOCK_NEW)
    # every guard and fetch call site follows the same shape
    html = html.replace(
        "if (!APPS_SCRIPT_URL || APPS_SCRIPT_URL === 'YOUR_APPS_SCRIPT_WEB_APP_URL') return;",
        "if (!SUBMIT_ENDPOINT) return;   // 수신처 미설정 — 전송 건너뜀",
    )
    html = html.replace(
        "if (!APPS_SCRIPT_URL || APPS_SCRIPT_URL === 'YOUR_APPS_SCRIPT_WEB_APP_URL') {",
        "if (!SUBMIT_ENDPOINT) {   // 수신처 미설정 — 전송 건너뜀",
    )
    html = html.replace("APPS_SCRIPT_URL", "SUBMIT_ENDPOINT")
    return html


def rewrite_metadata(html: str) -> str:
    html = OLD_BASE_RE.sub(NEW_BASE, html)
    # JSON-LD used og-image.svg / favicon.svg, neither of which exists; point the
    # structured-data image at the real preview file.
    html = html.replace('"logo": "' + NEW_BASE + 'favicon.svg"',
                        '"logo": "' + NEW_BASE + 'og-image.png"')
    html = html.replace('"image": "' + NEW_BASE + 'og-image.svg"',
                        '"image": "' + NEW_BASE + 'og-image.png"')
    return html


def main() -> None:
    raw_path = pathlib.Path(sys.argv[1])
    source_dir = pathlib.Path(sys.argv[2])
    html = raw_path.read_text(encoding="utf-8")

    html = rewrite_endpoint(html)
    html = rewrite_metadata(html)
    html = inline_quiz_data(html, source_dir)
    html = inline_venn(html, source_dir)

    # AKfycb…(수신처 웹앱 URL)는 이제 의도적으로 들어 있으므로 검사 대상이 아니다.
    leftovers = [p for p in ('src="quiz-data.js"', "APPS_SCRIPT_URL", "drtardis123", "DrTardis123",
                             'src="venn-diagram.png"') if p in html]
    if leftovers:
        raise SystemExit(f"leftover third-party/local references: {leftovers}")

    out = pathlib.Path(__file__).resolve().parent / "check" / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"wrote {out} ({len(html):,} chars)")


if __name__ == "__main__":
    main()
