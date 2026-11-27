import sys

path = sys.argv[1]
s = open(path, encoding='utf-8').read()

EDITS = [
("  .container {\n    max-width: 720px; margin: 0 auto;\n    padding: 0 20px 80px;\n  }",
 "  .container {\n    max-width: 720px; margin: 0 auto;\n    padding: 0 20px 80px;\n  }\n\n  /* ===== 2026-11-25: 랜딩 세로 리듬 조정 (섹션 사이 유격 축소 + 구분선) ===== */\n  #screen-intro > .container { padding-bottom: 24px; }\n  .positioning > .container,\n  .intro > .container { padding-bottom: 0; }\n  .section-rule {\n    height: 1px; width: auto;\n    background: #ffffff;\n  }\n  .section-rule::before {\n    content: ''; display: block; height: 1px;\n    background: #ececec;\n    margin-inline: max(20px, calc((100% - 680px) / 2));\n  }"),

("  .hero-inner {\n    max-width: 720px; margin: 0 auto;\n    padding: 56px 24px 48px;\n    text-align: center;\n  }",
 "  .hero-inner {\n    max-width: 720px; margin: 0 auto;\n    padding: 36px 24px 28px;\n    text-align: center;\n  }"),

("  .hero-sub {\n    font-size: 16px; color: #5a6478; margin: 0 0 32px;\n    line-height: 1.65;\n  }",
 "  .hero-sub {\n    font-size: 16px; color: #5a6478; margin: 0 0 32px;\n    line-height: 1.65;\n  }\n  /* 통계 아래 '법인 특화 부동산 자산관리' 한 줄 — 크게·진하게 */\n  .hero-sub--emphasis {\n    font-size: clamp(19px, 5vw, 21px);\n    font-weight: 800;\n    color: #0f2547;\n    letter-spacing: -0.4px;\n    line-height: 1.4;\n    margin: 0;\n  }"),

("  .hero-stat-label {\n    font-size: 11.5px; color: #8a93a8; margin-top: 4px;\n    letter-spacing: 0.3px;\n  }",
 "  .hero-stat-label {\n    font-size: 11.5px; color: #8a93a8; margin-top: 4px;\n    letter-spacing: 0.3px;\n  }\n  /* '국제공인재무설계사'가 '사'만 다음 줄로 떨어지지 않도록 */\n  .hero-stat-label--nowrap { white-space: nowrap; }"),

("  .intro {\n    background: #ffffff;\n    padding: 64px 0 56px;\n    border-top: 1px solid #ececec;\n  }",
 "  .intro {\n    background: #ffffff;\n    padding: 48px 0 40px;\n  }"),

("  .footer {\n    text-align: center; margin-top: 32px;",
 "  .footer {\n    text-align: center; margin-top: 24px;"),

("  .positioning {\n    background: linear-gradient(180deg, #f6f7f9 0%, #ffffff 100%);\n    padding: 64px 0 56px;\n    border-top: 1px solid #ececec;\n  }",
 "  .positioning {\n    background: linear-gradient(180deg, #f6f7f9 0%, #ffffff 100%);\n    padding: 44px 0 32px;\n    border-top: 1px solid #ececec;\n  }"),

("    margin: 0 auto 24px;\n    background: #ffffff;\n    padding: 16px;",
 "    margin: 0 auto 20px;\n    background: #ffffff;\n    padding: 16px;"),

("    .positioning { padding: 48px 0 40px; }",
 "    .positioning { padding: 32px 0 28px; }\n    .intro { padding: 40px 0 32px; }\n    .hero-inner { padding: 28px 20px 24px; }\n    .hero-stat-label--nowrap { font-size: 11px; letter-spacing: 0.1px; }"),

('      <p class="hero-sub">법인 특화 부동산 자산관리</p>',
 '      <p class="hero-sub hero-sub--emphasis">법인 특화 부동산 자산관리</p>'),

('          <div class="hero-stat-label">국제공인재무설계사</div>',
 '          <div class="hero-stat-label hero-stat-label--nowrap">국제공인재무설계사</div>'),

('  <div class="intro">\n    <div class="container">',
 '  <div class="section-rule" aria-hidden="true"></div>\n\n  <div class="intro">\n    <div class="container">'),

('  <div class="footer">\n    <strong>벨라리치(BELLARICH)㈜</strong> · 서울 서대문구 이화여대길 38, 201-51<br>',
 '  <div class="section-rule" aria-hidden="true"></div>\n\n  <div class="footer">\n    <strong>벨라리치(BELLARICH)㈜</strong> · 서울 서대문구 이화여대길 38, 201-51<br>'),
]

for old, new in EDITS:
    n = s.count(old)
    if n != 1:
        print(f'ERROR: expected 1 match, got {n} for: {old[:60]!r}')
        sys.exit(1)
    s = s.replace(old, new)

open(path, 'w', encoding='utf-8').write(s)
print('applied', len(EDITS), 'edits to', path)
