#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""1분 진단 동의 화면을 이메일 → 휴대폰 번호·카카오톡으로 바꾼다.

기준본은 배포된 bellarich-deploy/check/index.html (canonical·og·share imageUrl 이
bellarich.co.kr 로 고쳐진 판본). bellarich-site/check/index.html 사본은 그 수정이
빠져 있었으므로, 이 스크립트가 배포본에 수정을 적용한 뒤 두 파일에 같은 결과를 쓴다.
"""
import pathlib
import sys

BASE = pathlib.Path('/workspace')
SRC_DEPLOY = BASE / 'bellarich-deploy/check/index.html'
OUT_SITE = BASE / 'bellarich-site/check/index.html'
OUT_DEPLOY = BASE / 'bellarich-deploy/check/index.html'

EDITS = [
    # 1) 상단 데이터 안내 박스
    (
        '<li>✓ <strong>결과 발송 시</strong> — 이름, 이메일 주소 (진단 결과 리포트 전달용)</li>',
        '<li>✓ <strong>결과 발송 시</strong> — 이름, 휴대폰 번호 (진단 결과 리포트 전달용)</li>',
    ),
    (
        '✕ <strong>수집하지 않음</strong>: 연락처(전화번호), 주민등록번호, IP 주소, 정확한 위치 (이름·이메일은 결과 발송 동의 시에만 수집)<br>',
        '✕ <strong>수집하지 않음</strong>: 주민등록번호, IP 주소, 정확한 위치 (이름·휴대폰 번호는 결과 발송 동의 시에만 수집)<br>',
    ),
    (
        '📋 <strong>용도</strong>: 진단 결과 이메일 발송, 진단 품질 개선, B2B 트렌드 연구',
        '📋 <strong>용도</strong>: 진단 결과 카카오톡 발송, 진단 품질 개선, B2B 트렌드 연구',
    ),
    # 2) 동의 화면
    ('<!-- ========== CONSENT SCREEN (이메일 + 동의) ========== -->',
     '<!-- ========== CONSENT SCREEN (휴대폰 번호 + 동의) ========== -->'),
    ('<h2 class="consent-title">진단 결과를 <em>이메일</em>로 보내드릴게요</h2>',
     '<h2 class="consent-title">진단 결과를 <em>카카오톡</em>으로 보내드릴게요</h2>'),
    ('<p class="consent-desc">입력하신 이메일로 등급, 핵심 포인트, 문항별 진단 의견을 보내드립니다.',
     '<p class="consent-desc">입력하신 휴대폰 번호로 등급, 핵심 포인트, 문항별 진단 의견을 보내드립니다.'),
    ('<span class="consent-label">이메일 주소 <em class="req">*</em></span>\n          <input type="email" id="consent-email" class="consent-input" placeholder="example@company.com" required autocomplete="email" />',
     '<span class="consent-label">휴대폰 번호 <em class="req">*</em></span>\n          <input type="tel" id="consent-phone" class="consent-input" placeholder="010-1234-5678"\n                 inputmode="tel" autocomplete="tel" maxlength="13" required />'),
    ('<span class="consent-meta">수집 항목: 이름, 이메일 / 보유 기간: 결과 발송 후 1년 / 이용 목적: 진단 결과 발송</span>',
     '<span class="consent-meta">수집 항목: 이름, 휴대폰 번호 / 보유 기간: 결과 발송 후 1년 / 이용 목적: 진단 결과 발송</span>'),
    ('onclick="submitConsent()">진단 결과 메일로 받기 →</button>',
     'onclick="submitConsent()">진단 결과 카카오톡 받기 →</button>'),
    ('<p class="consent-foot">벨라리치는 발송 외 용도로 이메일을 사용하지 않으며, 관련 법령에 따라 안전하게 관리합니다.</p>',
     '<p class="consent-foot">벨라리치는 발송 외 용도로 휴대폰 번호를 사용하지 않으며, 관련 법령에 따라 안전하게 관리합니다.</p>'),
    # 3) 결과 화면 안내
    ('<span class="result-mail-icon" aria-hidden="true">📧</span>',
     '<span class="result-mail-icon" aria-hidden="true">💬</span>'),
    ('<strong>자세한 결과는 <span id="result-email-display">입력하신 이메일</span>로 보내드렸어요</strong>',
     '<strong>자세한 결과는 <span id="result-email-display">입력하신 휴대폰 번호</span>(카카오톡)로 보내드릴게요</strong>'),
    # 4) 주석
    ('/* ========== CONSENT (이메일 + 동의) ========== */',
     '/* ========== CONSENT (휴대폰 번호 + 동의) ========== */'),
    ('/* 이메일 칸 아래 상담 신청 번호. 휴대폰에서는 눌러서 바로 걸 수 있다. */',
     '/* 휴대폰 번호 입력칸 아래 상담 신청 번호. 휴대폰에서는 눌러서 바로 걸 수 있다. */'),
    ('/* ========== RESULT - 메일 발송 안내 ========== */',
     '/* ========== RESULT - 결과 발송 안내 ========== */'),
    ("CONSENT:   [11, '이메일 입력 화면'],", "CONSENT:   [11, '휴대폰 번호 입력 화면'],"),
    # 5) 전송 페이로드
    ("      name: currentName || '',\n      email: currentEmail || '',",
     "      name: currentName || '',\n      // 결과 발송 연락처. 시트·Apps Script 는 email 칸을 발송 주소로 쓰므로 같은 값을\n      // email 에도 담고(기존 수신처 호환), 휴대폰 번호임을 구분할 수 있게 phone 도 함께 보낸다.\n      email: currentPhone || '',\n      phone: currentPhone || '',"),
    ("    currentName = '';\n    currentEmail = '';", "    currentName = '';\n    currentPhone = '';"),
    ('  // ====== CONSENT (이메일 수집 동의) ======\n  let currentName = \'\';\n  let currentEmail = \'\';',
     '  // ====== CONSENT (휴대폰 번호 수집 동의) ======\n  let currentName = \'\';\n  let currentPhone = \'\';'),
    ("      btnConsent.textContent = '진단 결과 메일로 받기 →';",
     "      btnConsent.textContent = '진단 결과 카카오톡 받기 →';"),
    ("    // 이어하기로 다른 카테고리를 푸는 경우에는 앞서 적은 이메일을 다시 채워 둔다.",
     "    // 이어하기로 다른 카테고리를 푸는 경우에는 앞서 적은 휴대폰 번호를 다시 채워 둔다."),
    ("    document.getElementById('consent-email').value = currentEmail || '';",
     "    document.getElementById('consent-phone').value = currentPhone || '';"),
    ("      const el = document.getElementById('consent-name') || document.getElementById('consent-email');",
     "      const el = document.getElementById('consent-name') || document.getElementById('consent-phone');"),
    # 6) 검증
    ("""    const nameEl  = document.getElementById('consent-name');
    const emailEl = document.getElementById('consent-email');
    const collEl  = document.getElementById('consent-collection');
    const errEl   = document.getElementById('consent-error');
    const btnConsent = document.getElementById('btn-consent');
    const name  = (nameEl ? nameEl.value : '').trim();
    const email = (emailEl ? emailEl.value : '').trim();
    const coll  = collEl ? collEl.checked : false;

    // 간단한 이름·이메일 검증
    if (!name) {
      errEl.textContent = '이름을 입력해 주세요.';
      errEl.style.display = 'block';
      if (nameEl) nameEl.focus();
      return;
    }
    if (!email) {
      errEl.textContent = '이메일 주소를 입력해 주세요.';
      errEl.style.display = 'block';
      if (emailEl) emailEl.focus();
      return;
    }
    if (!/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(email)) {
      errEl.textContent = '이메일 형식이 올바르지 않습니다.';
      errEl.style.display = 'block';
      if (emailEl) emailEl.focus();
      return;
    }""",
     """    const nameEl  = document.getElementById('consent-name');
    const phoneEl = document.getElementById('consent-phone');
    const collEl  = document.getElementById('consent-collection');
    const errEl   = document.getElementById('consent-error');
    const btnConsent = document.getElementById('btn-consent');
    const name  = (nameEl ? nameEl.value : '').trim();
    const phoneRaw = (phoneEl ? phoneEl.value : '').trim();
    const phoneDigits = phoneRaw.replace(/[^0-9]/g, '');
    const coll  = collEl ? collEl.checked : false;

    // 간단한 이름·휴대폰 번호 검증
    if (!name) {
      errEl.textContent = '이름을 입력해 주세요.';
      errEl.style.display = 'block';
      if (nameEl) nameEl.focus();
      return;
    }
    if (!phoneDigits) {
      errEl.textContent = '휴대폰 번호를 입력해 주세요.';
      errEl.style.display = 'block';
      if (phoneEl) phoneEl.focus();
      return;
    }
    // 010·011·016·017·018·019 로 시작하는 10~11자리만 받는다.
    if (!/^01[016789]\\d{7,8}$/.test(phoneDigits)) {
      errEl.textContent = '올바른 휴대폰 번호를 입력해 주세요. (예: 010-1234-5678)';
      errEl.style.display = 'block';
      if (phoneEl) phoneEl.focus();
      return;
    }"""),
    ("    currentName = name;\n    currentEmail = email;",
     "    currentName = name;\n    // 하이픈을 넣어 010-1234-5678 형태로 맞춰 둔다. 시트·결과지에서 그대로 쓰기 위함이다.\n    currentPhone = phoneDigits.replace(/(\\d{3})(\\d{3,4})(\\d{4})/, '$1-$2-$3');"),
    # 7) 결과 화면 마스킹
    ("""    // 메일 발송 안내 (이메일 마스킹)
    if (currentEmail) {
      const masked = currentEmail.replace(/(^.).+(@.+)/, '$1***$2');
      const emailEl = document.getElementById('result-email-display');
      if (emailEl) emailEl.textContent = masked;
    }""",
     """    // 결과 발송 안내 (휴대폰 번호 가운데 자리 마스킹 → 010-****-5678)
    if (currentPhone) {
      const masked = currentPhone.replace(/^(\\d{3})-?(\\d{3,4})-?(\\d{4})$/, (m, a, b, c) => a + '-****-' + c);
      const phoneEl2 = document.getElementById('result-email-display');
      if (phoneEl2) phoneEl2.textContent = masked;
    }"""),
    ("    // 화면에는 등급 + 한 줄 멘트 + 점수만 표시 (findings는 이메일에만)",
     "    // 화면에는 등급 + 한 줄 멘트 + 점수만 표시 (findings는 결과지에만)"),
    ("    // Send completed data (email + kakao_channel + group 포함)",
     "    // Send completed data (phone + kakao_channel + group 포함)"),
    ("  // 이메일은 지우지 않는다. 동의 화면에서 다시 채워져 두 번 입력하지 않아도 된다.",
     "  // 이메일 대신 휴대폰 번호를 지우지 않는다. 동의 화면에서 다시 채워져 두 번 입력하지 않아도 된다."),
    # 8) 카카오 클릭 페이로드
    ("      email: currentEmail || '',\n      category: currentCategory || '',\n      grade: lastResult ? lastResult.grade : ''",
     "      email: currentPhone || '',\n      phone: currentPhone || '',\n      category: currentCategory || '',\n      grade: lastResult ? lastResult.grade : ''"),
]


def main() -> None:
    html = SRC_DEPLOY.read_text(encoding='utf-8')
    for old, new in EDITS:
        n = html.count(old)
        if n != 1:
            sys.exit(f'치환 대상이 정확히 1곳이 아님({n}곳): {old[:70]!r}')
        html = html.replace(old, new)

    for p in ('currentEmail', 'consent-email', '진단 결과 메일로 받기'):
        if p in html:
            sys.exit(f'남은 참조: {p}')

    OUT_SITE.write_text(html, encoding='utf-8')
    OUT_DEPLOY.write_text(html, encoding='utf-8')
    print(f'적용 완료 · {len(EDITS)}개 치환')
    print(f'  {OUT_SITE}')
    print(f'  {OUT_DEPLOY}')


if __name__ == '__main__':
    main()
