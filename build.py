#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Builds bellarich-site/index.html from _index.src.html + assets + plan data."""
import base64, json, os, re, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '_index.src.html')
OUT = os.path.join(HERE, 'index.html')

# 승계 탭 이름 — 사이트 여러 자리(탭 버튼·솔루션 lead·상세 페이지 갈래 표기·상단 내비)가
# 이 두 값 하나를 씁니다. 이름을 바꾸려면 여기만 고치고 다시 빌드하면 됩니다.
SUC_NAME = '부동산·가업 승계 플랜'      # 탭 버튼·갈래 표기의 정식 이름
SUC_SHORT = '부동산·가업 승계'          # 상단 내비·모바일 메뉴의 짧은 이름

FORM = 'https://docs.google.com/forms/d/1pvpYq1jJblmrxjHUQeo-nbmB_C3n87T8OCYVzhN5aZE/viewform'
CTA = ('<div class="m-cta"><p>이 플랜이 궁금하시다면 상담을 신청해 주세요.</p>'
       '<a class="btn btn--navy" href="%s" target="_blank" rel="noopener">상담 신청 <span>→</span></a></div>' % FORM)

# 표 안 문장 앞 작은 점(◆ 대신): 본문 첫 줄과 나란히 서도록 인라인 표시
DOT = '<span style="font-size:0.9em;vertical-align:0.1em;margin-right:1px">•</span>'

def rows(*items):
    return '<div class="m-rows">' + ''.join(
        f'<div class="m-row"><b>{k}</b><span>{v}</span></div>' for k, v in items) + '</div>'

def points(*items):
    return '<div class="m-points">' + ''.join(
        f'<p><b>Point {i+1}</b>{t}</p>' for i, t in enumerate(items)) + '</div>'

def ul(*items):
    return '<ul>' + ''.join(f'<li>{t}</li>' for t in items) + '</ul>'

def concerns(*items):
    return '<div class="m-concerns">' + ''.join(f'<p>{t}</p>' for t in items) + '</div>'

def table(caption, head, body, first_left=True):
    th = ''.join(f'<th>{h}</th>' for h in head)
    cls = 'm-table m-table--kv' if len(head) == 2 else 'm-table'
    tr = ''
    for row in body:
        cells = ''
        for i, c in enumerate(row):
            cc = ' class="hl"' if i == 0 else ''
            cells += f'<td{cc}>{c}</td>'
        tr += f'<tr>{cells}</tr>'
    return (f'<div class="table-wrap"><table class="{cls}"><caption>{caption}</caption>'
            f'<thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>')

def flow(*steps):
    out = '<div class="m-flow">'
    for b, t in steps:
        out += f'<div><b>{b}</b>{t}</div>'
    return out + '</div>'

D = {}

# ---------------- 투자플랜 ----------------
D['inv1'] = dict(cat='생애주기 플랜', title='사옥/공장 만들기 플랜', html=
  '<p class="m-lead">투자유망한 건물, 지식산업센터, 공장, 토지 등을 매입하여 사옥으로 사용하면서 향후 부동산의 자본이득도 함께 영위할 수 있습니다.</p>'
  + rows(('매입', '매매, 분양, 경매, 개발 등'),
         ('전략', '사옥갖기 마스터플랜 수립(PM) 및 자산운용 전략 병행'))
  + '<h4>Point</h4>'
  + points('법인 재무적 분석 및 맞춤 투자전략 수립 (시기, 방법, 종류 등)',
           '자녀법인, 주식이동, 자금계획 등 법인컨설팅 활용')
  + CTA)

D['inv2'] = dict(cat='생애주기 플랜', title='가족법인 부동산 플랜', html=
  '<p class="m-lead">꼬마빌딩 건물주의 꿈을 이제 자녀들과 나눌 수 있습니다. 가족법인을 만들어 향후 시세차익은 자녀들에게, 안정적인 월세는 직접 사용하면서 투자와 자산이전을 함께 영위할 수 있습니다.</p>'
  + rows(('매입', '매매, 분양, 경매, 개발 등'),
         ('전략', '사옥갖기 마스터플랜 수립(PM) 및 자산운용 전략 병행'))
  + '<h4>Point</h4>'
  + points('개인 재무적 분석 및 맞춤 투자전략 수립 (시기, 방법, 종류 등)',
           '가족법인 설립, 특정법인, 차등배당 등 법인컨설팅 활용')
  + CTA)

D['inv3'] = dict(cat='생애주기 플랜', title='CEO 은퇴 플랜', html=
  '<p class="m-lead">부동산 채권 금융 상품,&nbsp; 상가, 지식산업센터, 오피스텔, 공장 등 수익성 부동산을 활용하여 은퇴 후 안정적인 생활을 위한 수입원, 노후소득을 마련할 수 있습니다.</p>'
  + rows(('매입', '매매, 분양, 경매, 개발 등'),
         ('수익', DOT + ' 안전한 부동산 채권을 통한 확정 이자 수익'),
         ('', DOT + ' 공유 비즈니스센터 등 개발 및 공간분석을 통한 임대차 확보, 상권분석 리테일'))
  + '<h4>Point</h4>'
  + points('CEO 급여/상여 및 퇴직금 설계, 은퇴 후 필요한 목적자금 설계',
           '소득세율을 고려한 명의자 선정 및 그에 따른 법인 주식 자본거래를 통한 자금확보 등 법인컨설팅 활용')
  + CTA)

D['inv4'] = dict(cat='생애주기 플랜', title='CEO 자녀 보금자리 플랜', html=
  "<p class=\"m-lead\">‘청약통장 없이 서울에서 반값에 내 집 갖기’ — 서울·수도권에서 투자 유망한 지역의 소규모재개발, 재건축 물건을 활용하는 등 CEO 자녀들의 내 집 마련 전략을 제시합니다.</p>"
  + rows(('매입', '매매, 분양, 경매, 개발 등'),
         ('수익', '소규모재개발, 재건축, 저평가아파트 등 투자'))
  + '<h4>Point</h4>'
  + points('청약통장, 소득, 주택소유, 사전증여 유무 등 고려',
           '법인자산 운용 전략, 법인 자본거래 전략 함께 활용')
  + CTA)

D['inv5'] = dict(cat='생애주기 플랜', title='개인소득세 절세 플랜', html=
  '<p class="m-lead">벤처투자 소득공제를 활용하는 구조입니다. 개인투자조합 출자로 소득공제를 받고, 그 자금이 벤처기업의 부동산 직·간접투자로 이어지며 추가수익을 만듭니다.</p>'
  + '<h4>구조</h4>'
  + flow(('01 · 개인투자조합 출자', '개인투자자들이 조합에 출자합니다.'),
         ('02 · 회사채 발행 (CB/RCPS 등)', '조합이 벤처기업 A사의 회사채에 10억을 투자합니다.'),
         ('03 · 벤처기업 A사', '부동산 직·간접투자로 추가수익이 발생합니다.'),
         ('04 · 개인투자자', '추가수익과 함께 투자소득공제를 받습니다.'))
  + '<h4>구간별 소득공제율</h4>'
  + table('투자구간에 따른 소득공제율', ['투자구간', '소득공제율'], [
      ['3,000만원 이하', '100%'],
      ['3,000만원 ~ 5,000만원', '70%'],
      ['5,000만원 초과', '30%'],
    ])
  + '<p class="m-note" style="margin-top:0">※ 연금종합소득 중 공제한도는 해당 과세연도의 종합소득금액의 50%입니다.</p>'
  + '<h4>3천만원 투자 시 예상 소득공제금액</h4>'
  + table('과세표준 구간별 예상 소득공제금액', ['과세표준', '세율(시행세 포함)', '예상 소득공제금액'], [
      ['10억원 초과', '49.5%', '1,485만원'],
      ['5억원 초과 ~ 10억원 이하', '46.2%', '1,386만원'],
      ['3억원 초과 ~ 5억원 이하', '44%', '1,320만원'],
      ['1억 5천만원 초과 ~ 3억원 이하', '41.8%', '1,254만원'],
      ['8,800만원 초과 ~ 1억 5,000만원 이하', '38.5%', '1,155만원'],
      ['5,000만원 초과 ~ 8,800만원 이하', '26.4%', '792만원'],
      ['1,400만원 ~ 5,000만원 이하', '16.5%', '495만원'],
    ])
  + '<h4>투자금액에 따른 소득공제액</h4>'
  + table('투자금액별 소득공제액', ['투자금액', '소득공제액'], [
      ['1억원', '5,900만원'], ['7,000만원', '5,000만원'],
      ['5,000만원', '4,400만원'], ['3,000만원', '3,000만원'],
    ])
  + '<p class="m-note">※ 상기 소득공제율·세율 및 금액은 제도를 이해하기 위한 예시이며, 세법 개정과 개인의 과세표준·투자상황에 따라 달라질 수 있습니다. 실제 적용은 세무 검토를 거쳐 확정됩니다.</p>'
  + CTA)

D['inv6'] = dict(cat='생애주기 플랜', title='부동산 자산운용 플랜', html=
  '<p class="m-lead">부동산과 현금, 두 축의 자산운용. 자산 규모와 투자기간에 맞춰 실물운용과 대체투자를 함께 설계합니다.</p>'
  + '<h4>부동산 / 현금 자산운용</h4>'
  + table('서비스 개요', ['구분', '내용'], [
      ['투자기간', '연단위 / 3년'],
      ['자산범위', '5억 이상'],
      ['서비스비용', '자산 0.5~1%'],
      ['투자성과수수료', '10~30%'],
    ])
  + '<h4>운용대상</h4>'
  + table('실물운용 · 현금운용', ['구분', '운용대상'], [
      ['실물운용 / 부동산투자', '경공매 · 매매 · 개발'],
      ['현금운용 / 대체투자', 'NPL · P2P · 재개발재건축 · 부동산 공간개발 · 부동산 시행개발 · 기타 부동산관련 자산운용'],
    ])
  + '<h4>현금 자산운용 (대체투자)</h4>'
  + table('서비스 개요', ['구분', '내용'], [
      ['투자기간', '연단위'],
      ['자산범위', '0.3억 이상'],
      ['서비스비용', '자산 0.6~3%'],
      ['투자성과수수료', '10~30%'],
    ])
  + table('운용대상', ['구분', '운용대상'], [
      ['투자방식', '개별투자 · 공동투자 · 벤처투자 · 사모펀드'],
      ['운용대상', 'NPL · P2P · 재개발재건축 · 부동산 공간개발 · 부동산 시행개발 · 기타 부동산관련 자산운용'],
    ])
  + '<p class="m-note">※ 투자기간·자산범위·비용·성과수수료는 자산과 전략에 따라 달라지며, 개별 상담에서 확정됩니다. 투자에는 원금 손실 위험이 있습니다.</p>'
  + CTA)

# ---------------- 가업승계 ----------------
D['suc1'] = dict(cat='부동산·가업 승계', title='부동산 승계 플랜', html=
  '<p class="m-lead">현물출자·법인전환 등 법인 활용 전문. 개인 명의 부동산을 법인으로 옮기고, 그 법인을 자녀에게 넘기는 구조를 부동산과 법인 양쪽에서 설계합니다.</p>'
  + '<h4>주요 내용</h4>'
  + ul('개인부동산의 <b>현물출자·법인전환</b> 구조 검토',
       '양도차익·취득세·법인세를 함께 보는 <b>절세 시나리오</b>',
       '<b>자녀법인 지분 이전</b>을 통한 단계적 승계 설계',
       '승계 후 부동산 <b>활용(임대·개발)</b> 전략 연계')
  + '<h4>Point</h4>'
  + points('부동산 가치평가와 세부담 시뮬레이션을 먼저 진행합니다.',
           '법인전환·자녀법인·주식이동 등 법인컨설팅을 병행합니다.')
  + CTA)

D['suc2'] = dict(cat='가업승계', title='자녀 창업법인으로 가업승계', html=
  '<p class="m-lead">자녀 창업법인을 활용한 승계. 요건 진단부터 지분·경영권 이전까지, 가업을 이어가는 로드맵을 만듭니다.</p>'
  + '<h4>주요 내용</h4>'
  + ul('자녀 명의 <b>창업법인 설립</b> 및 사업 연계 구조',
       '<b>가업승계 증여특례</b> 요건 사전 점검',
       '<b>지분·경영권 이전</b> 로드맵과 시점 설계',
       '승계 후 <b>가족법인 자산운용</b>')
  + '<h4>Point</h4>'
  + points('업종·매출·고용 등 사전 요건을 먼저 진단합니다.',
           '증여·상속 시점과 재원 마련을 함께 설계합니다.')
  + CTA)

D['suc3'] = dict(cat='가업승계', title='가업상속공제 · 증여특례', html=
  '<p class="m-lead">가업상속공제와 가업승계 증여특례는 요건 충족이 핵심입니다. 사후관리까지 감당할 수 있는 구조인지 먼저 따져봅니다.</p>'
  + '<h4>주요 내용</h4>'
  + ul('가업상속공제 <b>요건(업종·기간·고용·자산)</b> 진단',
       '<b>가업승계 증여특례</b>를 활용한 사전증여 설계',
       '사후관리 요건 <b>체크리스트</b>와 이행 점검',
       '승계 후 <b>지배구조</b> 정리')
  + '<h4>Point</h4>'
  + points('공제·특례의 사후관리 요건까지 미리 확인합니다.',
           '가업용 자산과 비사업용 자산을 구분해 설계합니다.')
  + CTA)

D['suc4'] = dict(cat='가업승계', title='상속 / 증여 신탁', html=
  '<p class="m-lead">세무만으로는 완성되지 않는 승계. 유언·신탁 등 법적 수단을 함께 설계합니다.</p>'
  + '<h4>주요 내용</h4>'
  + ul('<b>유언·신탁</b> 등 법적 수단을 통한 승계 설계',
       '<b>신탁</b>을 통한 재산 관리와 권한 유보 구조',
       '상속인 간 <b>분쟁 예방</b> 구조',
       '<b>법무법인 서초 자산관리센터</b> 협업')
  + '<h4>Point</h4>'
  + points('세무 설계와 법률 설계를 한 흐름으로 맞춥니다.',
           '가족 구성과 사업 구조에 맞는 신탁 활용 방안을 검토합니다.')
  + CTA)

# ---------------- 법인재무 · 경영지원 ----------------
D['fin1'] = dict(cat='법인재무·경영지원', title='재무구조개선 / 신용등급 개선', html=
  '<p class="m-lead">부동산과 법인 재무는 서로를 끌어당깁니다. 보유부동산을 활용해 기업의 재무구조와 신용등급을 개선하는 전략을 설계합니다.</p>'
  + '<h4>주요 내용</h4>'
  + ul('<b>재무제표·부채구조</b> 진단 및 개선안',
       '<b>가지급금 정리</b>와 자본확충 시나리오',
       '<b>신용등급 개선</b>을 위한 재무지표 관리',
       '금융기관 협의를 통한 <b>자금조달 구조</b>')
  + '<h4>Point</h4>'
  + points('개인·법인 자산을 함께 놓고 개선 여지를 찾습니다.',
           '개선안이 세무·지분에 미치는 영향까지 검토합니다.')
  + CTA)

D['fin2'] = dict(cat='법인재무·경영지원', title='사내근로복지기금 도입 및 운용', html=
  '<p class="m-lead">기업에 쌓인 자산을 근로자 복지로, 다시 기업의 안정으로. 사내근로복지기금의 도입과 운용을 함께 설계합니다.</p>'
  + '<h4>주요 내용</h4>'
  + ul('<b>도입 요건·절차</b>와 출연 구조',
       '기금 <b>운용 전략</b>(부동산 포함)',
       '<b>세제 혜택</b>과 회계 처리 검토',
       '근로자 복지·인력 유지 효과')
  + '<h4>Point</h4>'
  + points('출연 재원과 손금 인정 범위를 먼저 확인합니다.',
           '기금 운용자산의 취득·처분 절차를 함께 설계합니다.')
  + CTA)

D['fin3'] = dict(cat='법인재무·경영지원', title='주주이익 환원 · 지배구조 개선', html=
  '<p class="m-lead">법인에 쌓인 잉여금을 어떻게 꺼내고, 차명주식과 지분을 어떻게 바로 세울 것인가. 두 가지를 한 번에 설계합니다.</p>'
  + '<h4>주요 내용</h4>'
  + ul('잉여금 처리 방안 <b>비교</b>(배당·급여·퇴직금 등)',
       '<b>CEO 보수·퇴직금</b> 설계와 절세',
       '<b>차명주식·명의신탁</b> 정리와 주식 이동·지분 조정',
       '<b>경영권 안정화</b>와 특수관계자 거래 정비')
  + '<h4>Point</h4>'
  + points('회사에 남길 자금과 개인에게 옮길 자금을 구분합니다.',
           '정리 과정의 증여·양도세 이슈와 향후 승계 순서를 함께 봅니다.')
  + CTA)


D['fin5'] = dict(cat='법인재무·경영지원', title='개인사업자 법인전환', html=
  '<p class="m-lead">개인사업자에서 법인으로. 사업은 그대로 두고, 세제와 자산 구조만 바꿉니다.</p>'
  + '<h4>주요 내용</h4>'
  + ul('개인사업자 → <b>법인전환</b> 절차와 세제',
       '<b>자산·부채 이전</b> 방식',
       '업종·사업구조에 맞는 <b>법인 형태</b> 선택',
       '전환 후 <b>세무·회계</b> 정착 지원')
  + '<h4>Point</h4>'
  + points('부동산 보유 사업자의 전환은 취득세·양도세를 함께 봅니다.',
           '전환 후 대표 보수·배당 구조까지 설계합니다.')
  + CTA)

D['fin6'] = dict(cat='법인재무·경영지원', title='M&A · 분할합병 · 법인설립·창업지원', html=
  '<p class="m-lead">사업이 커지거나 흔들릴 때, 그리고 새로 시작할 때. 조직과 자금의 구조를 함께 짭니다.</p>'
  + '<h4>주요 내용</h4>'
  + ul('<b>M&amp;A·분할·합병</b> 구조 검토와 <b>회생·워크아웃</b> 대응',
       '조직·자산 <b>재배치</b>와 거래 리스크 점검',
       '<b>법인 설립</b>과 사업 구조 선택, 창업자금·정책자금 연계',
       '<b>기업부설연구소·벤처인증</b> 등 인증 지원')
  + '<h4>Point</h4>'
  + points('부동산 자산이 있는 법인의 분할·합병은 세제 요건을 먼저 봅니다.',
           '자녀 창업법인은 가업승계 구조와 함께 설계합니다.')
  + CTA)

# ---------------- 부동산 승계 구조 블록 (상세 페이지 본문 전용) ----------------
# 홈페이지 '생애주기' 탭 아래에 있던 부동산승계 법인컨설팅 블록을 /plan/in-kind/ 본문으로
# 옮겼습니다(2026-11-26). 문장은 홈에 있던 그대로이고, 밝은 상세 페이지 배경에 맞게
# 클래스(pkind)만 새로 붙였습니다. 홈에는 3단계 흐름만 축약해 남깁니다.
PLAN_EXTRA = {}
PLAN_EXTRA['in-kind'] = '''<section class="pkind" aria-labelledby="pkindTitle">
          <p class="eyebrow">부동산 승계 구조</p>
          <h3 id="pkindTitle">부동산승계 <em>법인컨설팅</em></h3>
          <p class="pkind__lead">부동산 자산이전의 가격기준이 기준시가나 공시지가가 아닌 실거래가로 바뀌고 있어, 상속과 증여를 통한 부(富)의 세대 간 이동시 부담해야 하는 개인의 세금이 감당하기 힘든 수준으로 올라가고 있습니다. 부동산 자산의 세대이전에 대한 절세계획 솔루션으로 <b>법인활용 전략</b>은 필수입니다.</p>

          <div class="pkind__pair">
            <div>
              <b>부동산 전문가</b>
              <p>부동산 현황분석, 미래가치 검토에 따른 부동산승계전략 수립 및 향후 부동산 활용전략</p>
            </div>
            <div>
              <b>법인 전문가</b>
              <p>상법 및 세법 등 검토를 통한 법인활용전략 수립, 자녀법인 등 활용한 세대간 자산이동 절세승계 및 상속 전략</p>
            </div>
          </div>

          <div class="pkind__flow">
            <div class="pkind__node">
              <span class="pkind__idx">STEP 01 · 개인</span>
              <em>A&#8242;</em><b>부모님 개인부동산</b><small>개인 명의 자산</small>
            </div>
            <div class="pkind__arw" aria-hidden="true">→</div>
            <div class="pkind__node">
              <span class="pkind__idx">STEP 02 · 법인화</span>
              <em>(주)A&#8242;</em><b>부모님 100%</b><small>법인 전환</small>
            </div>
            <div class="pkind__arw" aria-hidden="true">→</div>
            <div class="pkind__node">
              <span class="pkind__idx">STEP 03 · 승계</span>
              <em>(주)B</em><b>자녀법인 100%</b><small>지분 이전</small>
            </div>
          </div>

          <div class="pkind__cols">
            <div class="pkind__col">
              <h4><i>01</i>개인자산 법인화</h4>
              <p>개인부동산 형태로 자산이전시 50%까지 최대세율이 적용됩니다. 개인부동산을 법인화하여 주식으로 자녀법인 등에 자산이전하는 전략을 통해 가문의 부동산을 형성합니다.</p>
            </div>
            <div class="pkind__col">
              <h4><i>02</i>상속·증여시 장점</h4>
              <ol>
                <li><b>자녀법인에 재산을 증여</b><br>자녀법인은 증여재산에 대해 법인세를 납부 — 2억원까지 9%, 200억원까지 19%</li>
                <li><b>5년이 경과하면 상속재산에 합산하지 않는다</b><br>상속인에게 미리 증여한 재산은 10년 이내 합산, 상속인 아닌 자(손자·자녀법인 등)에게 미리 증여한 재산은 5년 이내 합산</li>
              </ol>
            </div>
            <div class="pkind__col">
              <h4><i>03</i>신탁활용</h4>
              <p>자녀에게 사전증여를 통한 절세전략과 더불어 법적제도를 통해 그 재산에 관련된 모든 권한을 부모가 관리할 수 있는 신탁제도를 활용합니다.</p>
            </div>
          </div>
        </section>'''

# ---------------- build ----------------
def b64(path, mime):
    with open(path, 'rb') as f:
        return 'data:%s;base64,%s' % (mime, base64.b64encode(f.read()).decode('ascii'))

html = open(SRC, encoding='utf-8').read()
ceo = b64(os.path.join(HERE, 'assets', 'ceo-hero.webp'), 'image/webp')
book1 = b64(os.path.join(HERE, 'assets', 'book-1.jpg'), 'image/jpeg')
book2 = b64(os.path.join(HERE, 'assets', 'book-2.jpg'), 'image/jpeg')
yt_thumb = b64(os.path.join(HERE, 'assets', 'yt-card.jpg'), 'image/jpeg')
logo_symbol = open(os.path.join(HERE, 'assets', 'logo-symbol.html'), encoding='utf-8').read()

html = html.replace('__SUC_NAME__', SUC_NAME).replace('__SUC_SHORT__', SUC_SHORT)
html = html.replace('__LOGO__', logo_symbol)
html = html.replace('__BOOK1__', book1).replace('__BOOK2__', book2)
html = html.replace('__YT_THUMB__', yt_thumb)
# hero portrait (studio cut-out) injected as CSS var
html = html.replace(':root{', ':root{\n  --ceo-img:url("%s");' % ceo, 1)

data_js = json.dumps(D, ensure_ascii=False, indent=1)
html = html.replace('__DATA__', data_js)

leftover = re.findall(r'__[A-Z_]+__', html)
if leftover:
    raise SystemExit('unreplaced placeholder(s): %s' % sorted(set(leftover)))
if 'docs.google.com/forms/d/1pvpYq1jJblmrxjHUQeo-nbmB_C3n87T8OCYVzhN5aZE/edit' in html:
    raise SystemExit('google form EDIT link present — use the /viewform response URL')
if FORM not in html:
    raise SystemExit('consultation form link missing')

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)

print('written', OUT, len(html.encode('utf-8')), 'bytes')
print('ceo b64', len(ceo), '| logo symbol', len(logo_symbol))

# ============================================================
#  솔루션 상세 페이지  /plan/{slug}/index.html
#  _plan.src.html 틀에 메인 페이지와 같은 CSS + 모달 문구를 넣어 만듭니다.
#  구조가 확정된 플랜은 PLAN_PAGES 에 한 줄씩 추가하면 됩니다.
# ============================================================
PLAN_SRC = os.path.join(HERE, '_plan.src.html')
PLAN_DIR = os.path.join(HERE, 'plan')

# 상단·하단 색 — 플랜 갈래별로 한 곳에서 관리합니다(메인 카드 색 계열의 진한 톤).
#   life : 생애주기 플랜(남색)  suc : 가업승계 플랜(앰버)  fin : 법인재무·경영지원 플랜(세이지그린)
PLAN_ACCENT = {
    'life': dict(bg='#0B1933', glow='rgba(29,49,82,.9)'),
    'suc':  dict(bg='#5C3B16', glow='rgba(110,72,30,.92)'),
    'fin':  dict(bg='#2F4238', glow='rgba(70,96,80,.92)'),
}
PLAN_GROUP = {
    'life': '생애주기 플랜',
    'suc':  SUC_NAME,
    'fin':  '법인재무·경영지원 플랜',
}

# 플랜 영상 — 사이트 안에서 바로 재생하는 자체 호스팅 mp4(assets/tax-venture.mp4, 33MB, 11분 43초).
# 유튜브 임베드·새 창 이동 없이 모바일·PC 모두 이 자리에서 재생됩니다.
# 다른 영상으로 바꿀 때는 아래 src 파일과 제목, v 값만 고치면 됩니다.
PLAN_VIDEO = dict(
    id='D5EWmyd_X8Y',                      # 원본 유튜브 링크(캡션의 작은 텍스트 링크에만 씁니다)
    src='../../assets/tax-venture.mp4',    # 자체 호스팅 mp4 — moov 앞배치(faststart) 확인됨
    title='[똑똑한 벤처투자소득공제] 소득세 폭탄 피하고, 내 원금은 ‘아파트’가 지켜준대요',
)
# 재생 전 표지 — 이 영상의 썸네일(assets/yt-tax.jpg, 1280x648).
# 메인 소개 영상 카드와 같은 방식(background-image + center/cover)으로 깝니다.
# 파일을 바꾸면 아래 v 값만 올리면 브라우저 캐시가 갱신됩니다.
PLAN_VIDEO_V = '1127b'
PLAN_VIDEO_THUMB = '../../assets/yt-tax.jpg?v=' + PLAN_VIDEO_V

#   key   : DATA 키 — 그 플랜 모달의 문구를 본문으로 그대로 옮깁니다
#   slug  : 주소 /plan/{slug}/
#   no    : 메인 카드 번호(탭 안에서 보이는 번호)
#   group : PLAN_ACCENT / PLAN_GROUP 키 — 상단·하단 색과 갈래 이름
#   lead  : 메인 카드의 한 줄 요약(카드 문구와 같게 유지)
#   video : True 면 본문 마지막과 하단 상담 신청 사이에 유튜브 영상 카드를 넣습니다
PLAN_PAGES = [
    # ---- 생애주기 플랜 (01~06)
    dict(key='inv1', slug='office', no='01', group='life',
         title='사옥/공장 만들기 플랜',
         lead='건물·지식산업센터·공장·토지를 매입해 사옥으로 사용하며 자본이득까지 함께 영위합니다.'),
    dict(key='inv2', slug='family-corp', no='02', group='life',
         title='가족법인 부동산 플랜',
         lead='꼬마빌딩 건물주의 꿈을 자녀와 나눕니다. 시세차익은 자녀에게, 월세는 직접.'),
    dict(key='inv3', slug='retirement', no='03', group='life',
         title='CEO 은퇴 플랜',
         lead='안전한 부동산 채권, 수익형 부동산으로 은퇴 후 노후소득을 설계합니다.'),
    dict(key='inv4', slug='home-for-kids', no='04', group='life',
         title='CEO 자녀 보금자리 플랜',
         lead='청약통장 없이도 서울에서 내 집 마련. 소규모재개발·재건축·저평가 아파트 전략.'),
    dict(key='inv5', slug='tax', no='05', group='life', video=True,
         title='개인소득세 절세 플랜',
         lead='벤처투자 소득공제 구조로 투자구간별 공제율과 소득공제액을 함께 설계합니다.'),
    dict(key='inv6', slug='asset', no='06', group='life',
         title='부동산 자산운용 플랜',
         lead='부동산·현금 두 축의 자산운용. 투자기간과 자산범위에 맞춘 실물·대체투자.'),
    # ---- 부동산·가업 승계 플랜 (01~04) — 01 은 부동산, 02~04 는 가업 승계
    dict(key='suc1', slug='in-kind', no='01', group='suc',
         title='부동산 승계 플랜',
         lead='개인 명의 부동산을 현물출자로 법인에 옮기고, 그 법인 지분을 자녀에게 — 부동산과 법인 양쪽에서 승계를 설계합니다.'),
    dict(key='suc2', slug='startup-succession', no='02', group='suc',
         title='자녀 창업법인으로 가업승계',
         lead='자녀 창업법인을 활용한 승계. 요건 진단부터 지분·경영권 이전까지 로드맵을 만듭니다.'),
    dict(key='suc3', slug='family-business', no='03', group='suc',
         title='가업상속공제 · 증여특례',
         lead='가업상속공제와 가업승계 증여특례 요건을 사전에 진단하고, 사후관리까지 설계합니다.'),
    dict(key='suc4', slug='trust', no='04', group='suc',
         title='상속 · 증여 신탁',
         lead='유언·신탁 등 법적 수단을 통한 승계 구조. 법무법인 서초 자산관리센터와 협업합니다.'),
    # ---- 법인재무·경영지원 플랜 (01~05)
    dict(key='fin1', slug='credit', no='01', group='fin',
         title='재무구조·신용등급 개선',
         lead='부채구조·가지급금·자본확충을 진단하고 신용등급 개선안을 설계합니다.'),
    dict(key='fin3', slug='governance', no='02', group='fin',
         title='주주이익 환원 · 지배구조',
         lead='잉여금의 절세 환원과 차명주식·지분 정리로 경영권을 함께 세웁니다.'),
    dict(key='fin5', slug='incorporation', no='03', group='fin',
         title='개인사업자 법인전환',
         lead='사업은 그대로 두고 자산·부채 이전과 세제까지 — 부동산을 가진 개인사업자가 법인 구조로 옮겨가는 핵심 플랜입니다.'),
    dict(key='fin2', slug='welfare-fund', no='04', group='fin',
         title='사내근로복지기금',
         lead='도입 요건과 출연 구조, 기금 운용(부동산 포함)까지 함께 설계합니다.'),
    dict(key='fin6', slug='ma', no='05', group='fin',
         title='M&A·분할합병 · 법인설립',
         lead='조직 재편과 회생 대응, 설립·창업자금·벤처인증까지 한 번에 설계합니다.'),
]

VIDEO_TMPL = '''  <!-- 영상 — 본문 마지막과 하단 상담 신청 사이. 누르기 전에는 유튜브·영상 파일 요청이 0(preload="none")이고,
       누르면 같은 자리에서 사이트 안 <video>가 열려 모바일·PC 모두 페이지 안에서 바로 재생됩니다.
       원본 유튜브 주소는 캡션 옆 작은 텍스트 링크로만 남깁니다. -->
  <section class="pvideo" id="video">
    <div class="wrap">
      <p class="eyebrow">Video</p>
      <h2>%(title)s <em>영상</em></h2>
      <div class="video-card" id="videoCard" data-video-title="%(vtitle)s">
        <div class="video-card__stage">
          <button class="video-card__thumb" id="videoPlay" type="button"
                  style="background-image:url(%(thumb)s)"
                  aria-label="%(title)s 영상 재생 — 누르면 이 자리에서 바로 재생됩니다">
            <span class="video-card__play" aria-hidden="true"></span>
          </button>
          <video class="video-card__player" id="videoPlayer" controls playsinline preload="none"
                 poster="%(thumb)s" width="1280" height="720"
                 title="%(vtitle)s" aria-label="%(vtitle)s">
            <source src="%(src)s?v=%(v)s" type="video/mp4">
            이 브라우저에서는 영상이 재생되지 않습니다. <a href="%(src)s?v=%(v)s">영상 파일 내려받기</a>
          </video>
        </div>
        <p class="video-card__cap"><span class="video-card__cap-t">%(vtitle)s</span>
          <a class="video-card__yt" href="https://youtu.be/%(vid)s" target="_blank" rel="noopener">YouTube에서 보기 <i>↗</i></a>
        </p>
      </div>
    </div>
  </section>
'''


def plan_video(pg, title):
    if not pg.get('video'):
        return ''
    import html as _html
    return VIDEO_TMPL % dict(
        title=title,
        vid=PLAN_VIDEO['id'],
        src=PLAN_VIDEO['src'],
        v=PLAN_VIDEO_V,
        vtitle=_html.escape(PLAN_VIDEO['title'], quote=True),
        thumb=PLAN_VIDEO_THUMB)


def build_plan_pages(css, logo):
    tpl = open(PLAN_SRC, encoding='utf-8').read()
    made = []
    for pg in PLAN_PAGES:
        d = D[pg['key']]
        title = pg.get('title') or d['title']
        head, _, last = title.rpartition(' ')
        h1 = ('%s <em>%s</em>' % (head, last)) if head else title
        body = d['html']
        if body.endswith(CTA):          # 모달 하단 CTA는 상세 페이지의 두 버튼으로 대신합니다
            body = body[:-len(CTA)]
        body += PLAN_EXTRA.get(pg['slug'], '')   # 상세 페이지에만 붙는 본문(부동산 승계 구조 블록 등)
        accent = PLAN_ACCENT[pg['group']]
        accent_css = ':root{--phero-bg:%s;--phero-glow:%s}' % (accent['bg'], accent['glow'])
        page = (tpl
                .replace('__CSS__', css)
                .replace('__LOGO__', logo)
                .replace('__FORM__', FORM)
                .replace('__ACCENT__', accent_css)
                .replace('__SLUG__', pg['slug'])
                .replace('__TITLE__', title)
                .replace('__LEAD__', pg['lead'])
                .replace('__H1__', h1)
                .replace('__NO__', pg['no'])
                .replace('__CAT__', PLAN_GROUP[pg['group']])
                .replace('__BODY__', body)
                .replace('__VIDEO__', plan_video(pg, title)))
        left = re.findall(r'__[A-Z0-9_]+__', page)
        if left:
            raise SystemExit('plan %s: unreplaced placeholder(s): %s' % (pg['slug'], sorted(set(left))))
        path = os.path.join(PLAN_DIR, pg['slug'], 'index.html')
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(page)
        made.append(path)
        print('written', path, len(page.encode('utf-8')), 'bytes')
    return made


m = re.search(r'<style>(.*?)</style>', open(SRC, encoding='utf-8').read(), re.S)
plan_files = build_plan_pages(m.group(1), logo_symbol)

# ---- 배포 폴더(bellarich-deploy)가 있으면 그대로 복사 ----
DEPLOY = os.path.join(os.path.dirname(HERE), 'bellarich-deploy')
if os.path.isdir(DEPLOY):
    files = [OUT] + plan_files
    for path in files:
        dst = os.path.join(DEPLOY, os.path.relpath(path, HERE))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(path, dst)
    print('copied to', DEPLOY, ':', len(files), 'file(s)')
else:
    print('deploy folder not found — skipped copy')
