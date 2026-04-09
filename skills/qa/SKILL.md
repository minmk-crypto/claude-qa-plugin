---
name: qa
description: "Web QA 자동화. URL/Figma/PRD를 기반으로 TC 생성 → Playwright 검증 → 리포트 → Jira 티켓까지 한 번에 실행."
allowed-tools: Bash Read Write Grep Glob Agent
argument-hint: "[url]"
---

# Web QA 자동화

어떤 웹 페이지든 TC를 자동 생성하고 Playwright로 검증하는 메인 오케스트레이터.
하위 스킬들을 순서대로 호출한다.

**사용법:**
- `/qa` — 범용. 인풋 질문 후 전체 플로우
- `/qa [URL]` — URL 지정하여 바로 시작

**사전 조건:** Playwright MCP 연결 필요. `/mcp`에서 확인.

---

## 플로우

```
Phase 1: 인풋 수집 (이 스킬에서 직접)
    ↓
Phase 2: /qa-analyze 호출 (소스 분석)
    ↓
Phase 3: TC 생성 + 사용자 리뷰 (이 스킬에서 직접)
    ↓
Phase 4: Playwright 검증 (이 스킬에서 직접)
    ↓
Phase 5: /qa-report 호출 (리포트 생성)
    ↓
Phase 6: 사용자에게 묻기 "Jira에 올릴까요?"
    ↓ (승인 시)
Phase 7: /qa-jira 호출 (티켓 생성)
```

---

## Phase 1: 인풋 수집

$ARGUMENTS에 URL이 있으면 바로 사용. 없으면 AskUserQuestion으로 수집.

### 필수
1. **검증 대상 URL** — 실제 서비스 URL (복수 가능). 비밀번호 보호 시 비밀번호도.

### 선택
2. **Figma** — 파일 URL + API 토큰. 또는 로컬 정책 md 경로.
3. **PRD** — Notion URL (MCP 연결 시). 또는 로컬 md 경로.
4. **Jira** — 프로젝트 키 + 부모 이슈 + API 토큰 (나중에 Phase 6에서 물어도 됨)

### 기본값
- 우선순위 커버: 매우높음 + 높음
- 해상도: 390×844 / 768×1024 / 1280×800
- 우선순위 기준: [reference/priority-guide.md](reference/priority-guide.md)

---

## Phase 2: 소스 분석

`/qa-analyze`를 호출하거나, 해당 스킬의 로직을 직접 수행.
인풋으로 URL, Figma 정보, PRD 정보를 전달.

결과물: `정책 목록` + `요구사항 목록` + `컴포넌트 맵`

---

## Phase 3: TC 생성

Phase 2 결과를 종합하여 TC를 자동 생성.

### 기본 TC (사이트 기반, 항상)
- 모든 img: broken 없음 (naturalWidth > 0)
- 모든 h1~h6: 비어있지 않음
- 가격: € + 숫자 (이커머스)
- 모든 button: 클릭 가능
- 모든 a[href]: 404 아님
- GNB: 검색/장바구니/메뉴 동작
- 3해상도에서 주요 요소 존재 + 레이아웃 전환

### 정책 TC (Figma/PRD 있을 때)
정책을 TC로 변환. 조건/예외별 TC 생성.

### 우선순위 분류
[reference/priority-guide.md](reference/priority-guide.md) 기준 자동 분류.

### 사용자 리뷰
TC 초안을 보여주고 승인받은 후 Phase 4.

---

## Phase 4: Playwright 검증

```
for each viewport in [390, 768, 1280]:
  browser_resize(viewport)
  for each url in urls:
    browser_navigate(url)
    // 정적: browser_evaluate (DOM 검증)
    // 인터랙션: browser_click/type
    // 디자인: getComputedStyle
    // FAIL → browser_take_screenshot
```

결과를 JSON으로 저장: `output/reports/YYYY-MM-DD-qa-results.json`

---

## Phase 5: 리포트

`/qa-report`를 호출하거나 직접 스크립트 실행:
```bash
python3 skills/qa-report/scripts/generate-report.py \
  --input output/reports/YYYY-MM-DD-qa-results.json \
  --output-dir output/reports \
  --name {페이지명}
```

대화에 FAIL 요약 출력.

---

## Phase 6~7: Jira (선택)

FAIL이 있으면: **"Jira에 티켓을 올릴까요?"**

승인 시 `/qa-jira`를 호출하거나 직접 스크립트 실행:
```bash
python3 skills/qa-jira/scripts/jira-tickets.py \
  --input output/reports/YYYY-MM-DD-qa-results.json \
  --jira-url https://{org}.atlassian.net \
  --email {email} --token {token} \
  --project {key} --parent {parent}
```
