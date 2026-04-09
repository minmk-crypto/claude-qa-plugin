---
name: qa
description: "Web QA 자동화. URL + Figma + PRD를 기반으로 TC를 생성하고 Playwright로 자동 검증한다. /qa로 범용 실행, /qa-pdp로 PDP 프리셋 실행."
allowed-tools: Bash Read Write Grep Glob Agent
argument-hint: "[url] 또는 프리셋명 (예: pdp)"
---

# Web QA 자동화

어떤 웹 페이지든 TC를 자동 생성하고 Playwright로 검증하는 QA 스킬.

**사용법:**
- `/qa` — 범용. 인풋을 질문 받은 후 실행
- `/qa pdp` — PDP 프리셋. [presets/pdp.md](presets/pdp.md) 참조
- `/qa [URL]` — 해당 URL 바로 분석

**사전 조건:** Playwright MCP 연결 필요. `/mcp`에서 확인.

---

## Phase 1: 인풋 수집

$ARGUMENTS가 비어있거나 URL만 있으면 아래를 질문한다.
$ARGUMENTS에 프리셋명(예: `pdp`)이 있으면 [presets/](presets/) 폴더에서 해당 프리셋을 로드하고 Phase 2로 건너뛴다.

AskUserQuestion으로 수집:

### 필수
1. **검증 대상 URL** — 실제 서비스 URL (복수 가능). 비밀번호 보호 시 비밀번호도 함께.

### 선택
2. **Figma 디자인 스펙** — 다음 중 하나:
   - Figma 파일 URL + API 토큰 → API로 정책 자동 추출
   - 로컬 스크린샷/PNG 경로
   - 이미 추출된 정책 md 파일 경로
3. **PRD / 정책 문서** — 다음 중 하나:
   - Notion 페이지 URL (Notion MCP 연결 시)
   - 로컬 md/txt 파일 경로
   - 대화에서 직접 입력
4. **Jira 연동** — 프로젝트 키 + 부모 이슈 + API 토큰 (FAIL 시 자동 티켓)

### 기본값
- 우선순위 커버: 매우높음 + 높음 (변경 가능)
- 해상도: 390×844 / 768×1024 / 1280×800
- 우선순위 기준: [reference/priority-guide.md](reference/priority-guide.md) 참조

---

## Phase 2: 소스 분석

수집된 인풋에 따라 분석. 없는 소스는 건너뜀.

### 2-A. Figma 분석 (URL + 토큰 있을 때)

```
curl -s "https://api.figma.com/v1/files/{file_key}/nodes?ids={node_id}&depth=5" \
  -H "X-Figma-Token: {token}"
```

추출:
- TEXT 노드 → 정책 설명, 규칙, 주석
- FRAME 이름(20자+) → 정책 제목
- 수치 → 마진, 패딩, 너비, 비율

정리 → `정책 목록` + `디자인 수치 목록`

### 2-B. Notion PRD 분석 (URL 있을 때)

Notion MCP `notion-fetch`로 페이지 콘텐츠 추출.
없으면 건너뜀.

추출:
- 기능 요구사항 (테이블, 리스트)
- 노출 정책/조건
- 예외 케이스
- 비즈니스 규칙

정리 → `요구사항 목록`

### 2-C. 실제 사이트 분석 (항상)

Playwright로:
1. `browser_navigate` → URL 접속 (비밀번호 있으면 자동 입력)
2. `browser_snapshot` → 페이지 구조
3. `browser_evaluate` → DOM 요소 수집:
   - 모든 button (텍스트, aria-label, disabled 여부)
   - 모든 a[href] (링크)
   - 모든 img (alt, naturalWidth)
   - 모든 input/select/form
   - 주요 텍스트 영역
4. 3개 해상도에서 레이아웃 측정

정리 → `컴포넌트 맵` + `인터랙티브 요소 목록`

---

## Phase 3: TC 자동 생성

### 3-1. 기본 TC (항상, 사이트 기반)

**구조/콘텐츠:**
- 모든 img: naturalWidth > 0 (broken 없음)
- h1~h6: 비어있지 않음
- 가격: € + 숫자 (이커머스)

**인터랙션:**
- 모든 button: 클릭 가능 (의도적 disabled 제외)
- 모든 a[href]: 404 아님
- GNB(검색/장바구니/메뉴): 동작

**반응형:**
- 3해상도에서 주요 요소 존재
- 레이아웃 전환

### 3-2. 정책 TC (Figma/PRD 있을 때)

정책을 TC로 변환. 예:
```
정책: "가격 우위 시에만 비교 노출"
→ TC: 우위 상품 → 비교카드 있음
→ TC: 열위 상품 → 비교카드 없음
```

### 3-3. 우선순위 분류

[reference/priority-guide.md](reference/priority-guide.md) 기준으로 자동 분류.

### 3-4. 사용자 리뷰

TC 초안을 사용자에게 보여준다:
- TC 개수, 우선순위 분포
- 추가/수정/삭제 요청 반영
- 승인 후 Phase 4

---

## Phase 4: TC 실행

Playwright로 자동화:

```
for each viewport in [390, 768, 1280]:
  browser_resize(viewport)
  for each url in urls:
    browser_navigate(url)
    // 정적 TC: browser_evaluate
    // 인터랙션 TC: browser_click/type
    // 디자인 TC: getComputedStyle
    // FAIL → browser_take_screenshot
```

판정:
- **PASS**: 기대결과 일치
- **FAIL**: 불일치 + 설명 + 스크린샷
- **SKIP**: 미실행 (인터랙션, 다른 해상도)
- **N/A**: 해당 없음
- **확인필요**: 자동 판정 어려움

---

## Phase 5: 리포트

Phase 4에서 수집한 결과를 JSON으로 저장한 뒤, 스크립트로 리포트를 생성한다.

### 5-1. 결과 JSON 저장
Phase 4 결과를 `output/reports/YYYY-MM-DD-qa-{페이지명}-results.json`에 저장.
형식은 [scripts/generate-report.py](scripts/generate-report.py) 상단 docstring 참조.

### 5-2. 리포트 생성 (엑셀 + md)
```bash
python3 scripts/generate-report.py \
  --input output/reports/YYYY-MM-DD-qa-{페이지명}-results.json \
  --output-dir output/reports \
  --name {페이지명}
```
→ 엑셀 (.xlsx) + md 리포트 자동 생성.
→ 엑셀: TC 목록 + URL×해상도 결과 매트릭스 + 셀 색상(PASS 초록/FAIL 빨강) + 비고
→ md: 요약 + FAIL 목록 + 스크린샷 링크

### 5-3. 대화 출력
FAIL 건 요약을 대화에 출력. 매우높음/높음 강조.

### 5-4. Jira 티켓 (사용자 선택)
FAIL이 있으면 사용자에게 묻는다: **"Jira에 티켓을 올릴까요?"**

승인하면:
```bash
python3 scripts/jira-tickets.py \
  --input output/reports/YYYY-MM-DD-qa-{페이지명}-results.json \
  --jira-url https://{org}.atlassian.net \
  --email {email} \
  --token {token} \
  --project {project-key} \
  --parent {parent-issue}
```

동작:
- FAIL TC별 서브태스크 자동 생성
- 스크린샷 자동 첨부
- 재현 절차 + 기대 동작 + 해상도별 재현 정보 기술
- `--dry-run`으로 미리보기 가능
