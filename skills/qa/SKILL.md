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

## Phase 2.5: 분기 요인 탐색

Phase 2에서 도출된 정책/요구사항 중 **조건 분기가 있는 것**을 추출하고, 각 조건에 해당하는 **실제 테스트 대상을 사이트에서 자동 탐색**한다.

> 이 단계의 목적은 TC 생성이 아니라, TC에 필요한 **사전조건별 테스트 대상 URL을 확보**하는 것.

### 방법

1. 정책/PRD에서 "~인 경우 / ~가 아닌 경우", "~시 노출 / ~시 미노출" 패턴을 추출
2. 각 분기 조건에 해당하는 상품/페이지를 Playwright로 탐색:
   - Shopify: `/products.json` API로 상품 목록 조회 → 조건별 필터링
   - 일반 사이트: 상품 목록 페이지 탐색 → 조건별 상품 선별
3. 조건별로 최소 1개 테스트 대상 URL 확보
4. 확보 불가 시 사용자에게 안내 ("품절 상품을 찾지 못했습니다. URL을 직접 알려주세요")

### 출력 예시
```
🔍 분기 요인 탐색 결과:
  품절 상품 ──── /products/lucky-shine-tint
  판매중 상품 ── /products/peach-glow-makeup-base
  할인 상품 ──── /products/bbia-last-velvet-tint
  비할인 상품 ── /products/deep-clean-master
  리뷰 다수 ──── /products/peach-glow-makeup-base (5 reviews)
  리뷰 0개 ──── /products/deep-clean-master (0 reviews)
  다수 옵션 ──── /products/bbia-last-velvet-tint (36 variants)
  단일 옵션 ──── /products/peach-glow-makeup-base (1 variant)
  가격비교 있음 ─ /products/peach-glow-makeup-base
  가격비교 없음 ─ (탐색 중...)
```

---

## Phase 3: TC 생성

Phase 2의 정책/요구사항 + Phase 2.5의 분기 요인을 기반으로 TC를 생성.
기준은 항상 **"어떻게 되어야 하는가"**.

### TC 구조

```
TC ID | 사전조건 | 시나리오 | 동작 | 기대결과 | 검증 대상 URL | 검증 레벨
```

- **사전조건**: 어떤 상태의 상품/페이지에서 테스트하는지 (Phase 2.5에서 확보)
- **검증 레벨**: L1(정적) / L2(단일 인터랙션) / L3(시나리오 플로우)

### 3-1. 분기 TC (핵심 개선)

정책에 조건이 있으면 **양쪽 TC를 모두 생성**한다. 한쪽만 만들지 않는다.

```
정책: "품절 시 Épuisé 표기 + 가격 미노출"

TC-A03a: [품절 상품] → "Épuisé" + ATC 비활성화 + 가격 미노출
  URL: /products/lucky-shine-tint | L1

TC-A03b: [판매중 상품] → 가격 노출 + ATC 활성화
  URL: /products/peach-glow-makeup-base | L1
```

```
정책: "가격 우위 시에만 비교 카드 노출"

TC-B09a: [가격 우위] → Piyonna + 타사 + Save + 날짜 노출
  URL: /products/peach-glow-makeup-base | L1

TC-B09b: [가격 열위] → 비교 카드 미노출
  URL: (Phase 2.5에서 확보) | L1
```

```
정책: "텍스트 리뷰 3개 미만 시 AI 요약 비노출"

TC-B16a: [리뷰 3개+] → AI Summary 노출
  URL: /products/peach-glow-makeup-base | L1

TC-B16b: [리뷰 <3개] → AI Summary 미노출
  URL: /products/deep-clean-master | L1
```

### 3-2. 인터랙션 TC

단순 존재 확인이 아니라 **클릭 후 결과**를 검증:

```
TC-B13: [판매중] Description 클릭 → 드로어 열림, 내용 비어있지 않음 | L2
TC-D04: [리뷰 있음] Needs 필터 선택 → 리뷰 목록 실제 변경 | L2
TC-D06: [리뷰 있음] Most recent 선택 → 리뷰 순서 실제 변경 | L2
TC-B21: [리뷰 있음] "See the original" → 한국어 표시 → "See the translation" → FR 복귀 | L2
```

### 3-3. 시나리오 플로우 TC

여러 인터랙션을 순서대로 실행하여 E2E 플로우 검증:

```
SN-01: 구매 플로우 [판매중 + 옵션 있음]
  1. PDP 진입
  2. 옵션 선택 (스와치 클릭)
  3. 이미지 변경 확인
  4. Add to Cart 클릭
  5. 장바구니 카운트 +1 확인
  6. 장바구니 버튼 클릭
  7. 장바구니 드로어에 상품 존재 확인
  URL: /products/bbia-last-velvet-tint | L3

SN-02: 리뷰 탐색 플로우 [리뷰 3개+]
  1. 별점 클릭 → 리뷰 섹션 스크롤
  2. See more reviews → 드로어 열림
  3. Needs 필터 선택 → 리뷰 목록 변경 확인
  4. Most recent 정렬 → 순서 변경 확인
  5. 원문 토글 → 한국어 표시
  6. 번역 토글 → FR 복귀
  URL: /products/peach-glow-makeup-base | L3

SN-03: 품절 상품 플로우 [품절]
  1. PDP 진입
  2. Épuisé 표기 확인
  3. ATC 클릭 불가 확인
  4. 가격 미노출 확인
  URL: /products/lucky-shine-tint | L3
```

### 3-4. 공통 TC (항상 포함)

Figma/PRD와 무관하게 웹 QA 기본:
- 필수 정보 노출 (상품명, 가격, 이미지) | L1
- 핵심 버튼 동작 (ATC, 검색, 장바구니) | L2
- 링크 정상 여부 | L1
- 반응형 레이아웃 전환 (3해상도) | L1

### 우선순위 분류
[reference/priority-guide.md](reference/priority-guide.md) 기준 자동 분류.

### 사용자 리뷰
TC 초안을 보여줄 때 다음을 포함:
- 분기 TC 쌍 목록 (양쪽 모두 있는지 확인)
- 시나리오 플로우 목록
- 각 TC의 검증 대상 URL
승인받은 후 Phase 4.

---

## Phase 4: Playwright 검증

3단계 레벨로 검증을 수행한다. 진행 상황을 실시간 출력.

### Level 1: 정적 검증
- `browser_evaluate`로 DOM 요소 존재/텍스트/속성 일괄 확인
- 분기 TC: 사전조건에 맞는 URL에서 실행 (Phase 2.5에서 확보한 URL)
- 가장 빠름. 한 번의 evaluate로 여러 TC를 묶어서 실행 가능.

### Level 2: 단일 인터랙션
- `browser_click` → `browser_evaluate`로 결과 확인
- 각 인터랙션 TC를 순차 실행
- **클릭 전후 상태를 비교**하여 실제 동작 여부 판정:
  - 아코디언: 클릭 전 숨김 → 클릭 후 노출 (높이 변화 or display 변화)
  - 필터: 선택 전 목록 → 선택 후 목록 (항목 수 or 순서 변화)
  - 정렬: 변경 전 순서 → 변경 후 순서 (날짜/텍스트 비교)
  - ATC: 클릭 전 카운트 → 클릭 후 카운트 (+1)
  - 토글: 클릭 전 언어 → 클릭 후 언어 (한글/FR 감지)

### Level 3: 시나리오 플로우
- 여러 인터랙션을 **순서대로** 실행하여 E2E 검증
- 한 단계가 FAIL이면 이후 단계도 FAIL 처리 (의존성)
- 각 단계마다 기대 결과 확인
- FAIL 발생 시 즉시 스크린샷

### 실행 순서

```
for each viewport in [390, 768, 1280]:
  browser_resize(viewport)
  대화에 "📱 {뷰포트} 검증 시작" 출력

  // 분기 조건별 URL 순회
  for each (precondition, url) in test_targets:
    browser_navigate(url)
    대화에 "  [{사전조건}] {상품명}" 출력

    // Level 1: 정적 TC 일괄
    대화에 "    L1 정적 검증..." 출력
    results += browser_evaluate(해당 URL의 L1 TC들)
    대화에 "    ✓ N PASS, ✗ N FAIL" 출력

    // Level 2: 인터랙션 TC 순차
    대화에 "    L2 인터랙션 검증..." 출력
    for each interaction_tc:
      before = browser_evaluate(사전 상태)
      browser_click(대상)
      after = browser_evaluate(사후 상태)
      result = compare(before, after)
      대화에 "    {TC-ID}: {PASS/FAIL}" 출력
      if FAIL: browser_take_screenshot

    // Level 3: 시나리오 플로우 (해당 URL에 매칭되는 시나리오만)
    for each scenario matching this url:
      대화에 "    L3 시나리오: {시나리오명}" 출력
      for each step in scenario:
        execute(step)
        if step.FAIL:
          browser_take_screenshot
          대화에 "    ✗ Step {N} FAIL: {설명}" 출력
          break  // 이후 단계 SKIP
        대화에 "    ✓ Step {N} PASS" 출력
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
