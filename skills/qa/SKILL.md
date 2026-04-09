---
name: qa
description: "Web QA 자동화. Figma/PRD를 기반으로 TC 생성 → Playwright로 실제 사이트 검증 → 리포트 → Jira 티켓까지 한 번에 실행."
allowed-tools: Bash Read Write Grep Glob Agent mcp__playwright__browser_navigate mcp__playwright__browser_snapshot mcp__playwright__browser_take_screenshot mcp__playwright__browser_resize mcp__playwright__browser_click mcp__playwright__browser_type mcp__playwright__browser_evaluate mcp__playwright__browser_press_key mcp__playwright__browser_hover mcp__playwright__browser_wait_for mcp__playwright__browser_close
argument-hint: "[url]"
---

# Web QA 자동화

어떤 웹 페이지든 TC를 자동 생성하고 Playwright로 검증하는 메인 오케스트레이터.
하위 스킬들을 순서대로 호출한다.

**사용법:**
- `/qa` — 범용. 인풋 질문 후 전체 플로우
- `/qa [URL]` — URL 지정하여 바로 시작

---

## 플로우

```
Phase 0: 환경 체크 (이 스킬에서 직접)
    ↓
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

## Phase 0: 환경 체크

스킬 실행 전에 필요한 환경이 갖추어져 있는지 확인한다. 하나라도 없으면 설치 안내 후 스킬을 중단한다.

### 필수 (없으면 중단)

**1. Playwright MCP**
- 확인: `mcp__playwright__browser_navigate` 도구가 사용 가능한지 확인
- 없으면 다음을 안내하고 중단:
  ```
  ⚠ Playwright MCP가 연결되어 있지 않습니다.

  설치 방법:
  1. /mcp 입력
  2. "Playwright" 검색하여 연결
  3. 연결 완료 후 다시 /qa 실행

  Playwright MCP가 없으면 브라우저 자동 검증이 불가능합니다.
  ```

**2. Python 3**
- 확인: `python3 --version` 실행
- 없으면 안내하고 중단:
  ```
  ⚠ Python 3이 설치되어 있지 않습니다.

  설치 방법:
  - macOS: brew install python3
  - 기타: https://www.python.org/downloads/

  Python은 리포트 생성(엑셀)과 Jira 연동에 필요합니다.
  ```

**3. openpyxl (Python 패키지)**
- 확인: `python3 -c "import openpyxl"` 실행
- 없으면 안내:
  ```
  ⚠ openpyxl 패키지가 없습니다. 엑셀 리포트 생성에 필요합니다.

  설치:
  pip3 install openpyxl

  설치 후 다시 /qa 실행해주세요.
  ```

### 선택 (없으면 안내 후 계속 진행)

**4. Notion MCP**
- 확인: `mcp__claude_ai_Notion__notion-fetch` 도구가 사용 가능한지 확인
- 없으면 안내하되 **계속 진행**:
  ```
  ℹ Notion MCP가 연결되어 있지 않습니다.
  PRD를 Notion URL로 제공하려면 /mcp에서 Notion을 연결해주세요.
  대신 로컬 md 파일이나 대화에서 직접 입력으로 PRD를 제공할 수 있습니다.
  ```

**5. Jira API 접속**
- Phase 0에서는 체크하지 않음 — Phase 6(Jira 올릴까요?)에서 필요할 때 물어봄

### 환경 체크 통과 시
```
✅ 환경 체크 완료
  - Playwright MCP: 연결됨
  - Python 3: 설치됨 (3.x.x)
  - openpyxl: 설치됨
  - Notion MCP: 연결됨 / 미연결 (PRD 직접 입력 가능)

QA 자동화를 시작합니다.
```

---

## Phase 1: 인풋 수집

AskUserQuestion으로 수집. TC 생성의 기준이 되는 소스와 검증 대상을 분리하여 받는다.

### TC 생성 소스 (최소 1개 필수)
1. **Figma** — 파일 URL + API 토큰. 또는 로컬 정책 md 경로.
2. **PRD** — Notion URL (MCP 연결 시). 또는 로컬 md 경로. 또는 대화에서 직접 입력.

> **중요:** TC는 "어떻게 되어야 하는가"(Figma/PRD)를 기준으로 생성한다.
> 실제 사이트는 TC 생성에 사용하지 않는다 — 검증 대상일 뿐이다.
> Figma/PRD 없이 사이트 URL만 제공하면 TC 생성 불가. 소스를 요청한다.

### 검증 대상
3. **검증 대상 URL** — 실제 서비스 URL (복수 가능). 비밀번호 보호 시 비밀번호도.

### 선택
4. **Jira** — 프로젝트 키 + 부모 이슈 + API 토큰 (나중에 Phase 6에서 물어도 됨)

### 기본값
- 우선순위 커버: 매우높음 + 높음
- 해상도: 390×844 / 768×1024 / 1280×800
- 우선순위 기준: [reference/priority-guide.md](reference/priority-guide.md)

---

## Phase 2: 소스 분석

`/qa-analyze`를 호출하거나, 해당 스킬의 로직을 직접 수행.
Figma 정보, PRD 정보를 전달. **사이트 URL은 여기서 사용하지 않는다.**

결과물: `정책 목록` + `요구사항 목록` + `디자인 수치`

---

## Phase 3: TC 생성

Phase 2의 정책/요구사항을 기반으로 TC를 생성. 기준은 항상 **"어떻게 되어야 하는가"**.

### 정책 TC (Figma 기반)
Figma에서 추출된 정책을 TC로 변환:
```
정책: "가격 우위 시에만 비교 카드 노출"
→ TC: 가격 우위 상품 → 비교카드 존재
→ TC: 가격 열위 상품 → 비교카드 미노출

정책: "이미지 1:1 정방형"
→ TC: 이미지 ratio 0.95~1.05

정책: "품절 시 Épuisé 표기 + 가격 미노출"
→ TC: 품절 상품 → "Épuisé" 텍스트 + 가격 영역 없음
```

### 요구사항 TC (PRD 기반)
PRD 요구사항별 TC:
```
요구사항: "리뷰 텍스트 3개 미만 시 AI 요약 비노출"
→ TC: 리뷰 3개+ 상품 → AI Summary 존재
→ TC: 리뷰 <3개 상품 → AI Summary 없음
```

### 공통 TC (항상 포함)
Figma/PRD와 무관하게 웹 QA 기본 항목:
- 필수 정보 노출 (상품명, 가격, 이미지)
- 핵심 버튼 동작 (ATC, 검색, 장바구니)
- 링크 정상 여부
- 반응형 레이아웃 전환 (3해상도)

### 우선순위 분류
[reference/priority-guide.md](reference/priority-guide.md) 기준 자동 분류.

### 사용자 리뷰
TC 초안을 보여주고 승인받은 후 Phase 4.

---

## Phase 4: Playwright 검증

**진행 상황 표시:** 각 상품/해상도 전환 시, 그리고 TC 그룹(매우높음/높음/보통) 시작 시 대화에 진행 상황을 출력한다.
```
예시:
📱 모바일 (390px) — peach-glow-makeup-base
  [매우높음] TC-A01~A09 검증 중...
  ✓ 9/9 PASS
  [높음] TC-B01~B36 검증 중...
  ✓ 25 PASS, ✗ 2 FAIL
  ...
📱 태블릿 (768px) — peach-glow-makeup-base
  ...
```

**실행:**
```
for each viewport in [390, 768, 1280]:
  browser_resize(viewport)
  대화에 "📱 {뷰포트} 검증 시작" 출력
  for each url in urls:
    browser_navigate(url)
    대화에 "  {상품명} 검증 중..." 출력
    // 정적: browser_evaluate (DOM 검증)
    // 인터랙션: browser_click/type
    // 디자인: getComputedStyle
    // FAIL → browser_take_screenshot
    대화에 "  ✓ N PASS, ✗ N FAIL" 출력
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
