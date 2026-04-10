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
Phase 2: /qa-analyze 호출 (소스 분석 — Figma 구조 + 정책 추출)
    ↓
Phase 2.3: Figma↔사이트 매핑 (이 스킬에서 직접)
    ↓
Phase 2.7: 인터랙티브 요소 자동 탐색 (이 스킬에서 직접)
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
Figma 정보, PRD 정보를 전달.

이 단계는 **2단계**로 나뉜다:

### 2-A. Figma 파일 구조 분석 (전체 지도 그리기)

Figma 파일 하나에는 여러 카테고리(대분류)와 개별 화면이 포함되어 있다.
**TC를 생성하기 전에 먼저 전체 구조를 파악**해야 한다.

**방법**:
1. Figma API `/v1/files/{file_key}?depth=3`으로 파일 트리 조회
2. 최상위 구조 파악:
   - **CANVAS** (페이지) = 대분류 카테고리 (예: PDP, PLP, Home, Cart, Checkout 등)
   - **SECTION / FRAME** = 개별 화면 또는 컴포넌트 그룹
3. 각 CANVAS/SECTION별로:
   - 이름에서 카테고리 추출 (예: `[FR] PDP`, `홈`, `상품 목록` 등)
   - 하위 FRAME 수 = 화면 복잡도 추정
   - 언어/지역 태그 추출 (예: `[FR]`, `[KR]`, `[EN]`)
4. 심화 분석이 필요한 노드는 `/v1/files/{file_key}/nodes?ids={node_ids}&depth=10`으로 상세 조회

**출력 형식**:
```
📐 Figma 파일 구조 분석:

  파일: {파일명}
  ┌─────────────────────────────────────────────┐
  │ 카테고리        │ 화면 수 │ 언어/지역          │
  ├─────────────────┼─────────┼───────────────────┤
  │ PDP             │ 20개    │ [FR]              │
  │ PLP (Collection)│ 12개    │ [FR]              │
  │ Home            │ 8개     │ [FR]              │
  │ Cart            │ 5개     │ [FR]              │
  │ 리뷰            │ 107개   │ -                 │
  │ 너비 가이드      │ 10개    │ -                 │
  └─────────────────┴─────────┴───────────────────┘
```

### 2-B. 카테고리별 정책/요구사항 추출

Figma 구조 분석 후, **사용자가 선택한 카테고리** (또는 전체)에 대해 상세 정책을 추출한다.

1. 각 카테고리의 FRAME/TEXT 노드에서 정책, 조건, 수치 추출
2. PRD가 있으면 PRD 요구사항도 함께 추출
3. **카테고리별로 묶어서** 결과 정리

**결과물**: `카테고리 구조` + `카테고리별 정책 목록` + `요구사항 목록` + `디자인 수치`

### 사용자 확인 (Phase 2 완료 시)

전체 구조를 보여주고, 이번 검증에서 다룰 범위를 사용자에게 확인:
```
📐 Figma에서 6개 카테고리를 발견했습니다.
  이번 검증에서 어떤 카테고리를 검증할까요?
  (기본: 전체 / 또는 특정 카테고리 선택)
```

---

## Phase 2.3: Figma↔사이트 매핑

Phase 2에서 파악한 Figma 카테고리/화면 구조를, 사용자가 제공한 **실제 사이트 URL과 매핑**한다.

> 이 단계의 목적은 "Figma의 어떤 화면이 실제 사이트의 어떤 페이지/영역에 해당하는지"를 확정하는 것.

### 방법

1. **사이트 탐색**: 사용자가 제공한 URL(주로 메인 페이지)에서 `browser_navigate` → `browser_snapshot` + `browser_evaluate`로 사이트 구조 파악
   - GNB/메뉴에서 주요 섹션 링크 추출 (Home, Collections, Products, Cart 등)
   - 현재 페이지의 영역 구분 (헤더, 본문 섹션들, 푸터)
   - 내부 링크에서 페이지 유형 추론 (`/products/*` → PDP, `/collections/*` → PLP 등)

2. **자동 매핑**: Figma 카테고리명과 사이트 섹션/URL 패턴을 매칭
   - `PDP` ↔ `/products/*`
   - `PLP` / `Collection` ↔ `/collections/*`
   - `Home` ↔ `/` (루트)
   - `Cart` ↔ `/cart` 또는 cart drawer
   - `Header` / `Footer` ↔ 공통 영역
   - 매칭 실패 시 사용자에게 확인

3. **카테고리별 대표 URL 확보**: 각 카테고리에 대해 실제 검증할 URL을 1개 이상 확보
   - PDP → 재고/품절/할인 등 조건별 상품 URL (Phase 2.5에서 상세 탐색)
   - PLP → 컬렉션 페이지 URL
   - Home → 메인 페이지 URL

### 출력 형식
```
🔗 Figma↔사이트 매핑 결과:

  Figma 카테고리      │ 사이트 URL/영역                      │ 매칭
  ────────────────────┼──────────────────────────────────────┼───────
  PDP                 │ /products/{handle}                   │ ✅ 자동
  PLP (Collection)    │ /collections/{handle}                │ ✅ 자동
  Home                │ /                                    │ ✅ 자동
  Cart                │ Cart Drawer (dialog)                 │ ✅ 자동
  리뷰                 │ PDP 내 Reviews 섹션                   │ ✅ 자동
  너비 가이드           │ (디자인 참고용, 검증 불필요)             │ ⏭ 스킵
```

### 사이트 영역 상세 분석

매핑된 각 카테고리 URL에 대해 **사이트의 실제 영역 구조**를 분석:

1. `browser_navigate(카테고리 대표 URL)` → `browser_snapshot`
2. 페이지의 주요 섹션 식별:
   - 헤더/네비게이션
   - 상품 이미지 영역
   - 상품 정보 영역 (가격, 옵션 등)
   - 콘텐츠 탭/아코디언
   - 리뷰 영역
   - 추천/관련 상품
   - 푸터
3. Figma의 FRAME/SECTION 순서와 사이트의 섹션 순서를 대응시킴
4. **Figma에는 있지만 사이트에 없는 영역**, **사이트에는 있지만 Figma에 없는 영역** 식별 → TC 또는 경고 대상

**결과물**: `카테고리-URL 매핑` + `카테고리별 사이트 영역 구조` + `불일치 목록`

---

## Phase 2.5: 분기 요인 탐색

Phase 2의 정책/요구사항 중 **조건 분기가 있는 것**을 추출하고, Phase 2.3에서 매핑된 URL을 기반으로 각 조건에 해당하는 **실제 테스트 대상을 사이트에서 자동 탐색**한다.

> 이 단계의 목적은 TC 생성이 아니라, TC에 필요한 **사전조건별 테스트 대상 URL을 확보**하는 것.

### 방법

1. 정책/PRD에서 "~인 경우 / ~가 아닌 경우", "~시 노출 / ~시 미노출" 패턴을 추출
2. Phase 2.3에서 매핑된 카테고리별 URL을 기반으로, 각 분기 조건에 해당하는 상품/페이지를 Playwright로 탐색:
   - Shopify: `/products.json` API로 상품 목록 조회 → 조건별 필터링
   - 일반 사이트: 상품 목록 페이지 탐색 → 조건별 상품 선별
3. 조건별로 최소 1개 테스트 대상 URL 확보
4. 확보 불가 시 사용자에게 안내 ("품절 상품을 찾지 못했습니다. URL을 직접 알려주세요")

### 출력 형식
```
🔍 분기 요인 탐색 결과:
  [PDP] 재고 있음      ──── /products/peach-glow-makeup-base
  [PDP] 품절           ──── /products/hanskin-code-on-dd-cream
  [PDP] 할인 있음      ──── /products/bbia-last-velvet-tint
  [PLP] 필터 적용 전    ──── /collections/face-care
  [PLP] 필터 적용 후    ──── /collections/face-care?filter=...
  ...
```

---

## Phase 2.7: 인터랙티브 요소 자동 탐색

Phase 2.5 이후, TC 생성 전에 실행. 검증 대상 URL에서 **페이지에 존재하는 모든 인터랙티브 요소를 자동으로 탐색**하여, Figma/PRD에 언급되지 않은 요소도 TC 생성 대상에 포함시킨다.

> 이 단계의 목적은 Figma/PRD에 명시되지 않았지만 사용자가 당연히 기대하는 기본 동작(필터, 정렬, 체크박스, 아코디언, 폼 입력 등)을 빠짐없이 검증하기 위함.

### 방법

1. 각 대상 URL에서 `browser_navigate` → `browser_evaluate`로 DOM 스캔
2. 탐색 대상 셀렉터:
   ```
   button, a[href], input, select, textarea,
   [role="button"], [role="tab"], [role="checkbox"], [role="switch"], [role="combobox"],
   details > summary, [data-toggle], [aria-expanded], [onclick]
   ```
3. 각 요소에서 수집:
   - 태그, type, 보이는 텍스트 (50자 제한), aria-label
   - 현재 상태 (checked/expanded/selected/disabled)
   - 바운딩 박스 (위치, 크기)
4. 필터링:
   - 숨김 요소 제외 (`display:none`, `visibility:hidden`, 0 크기)
   - 중복 제거 (같은 텍스트+태그)
   - 본문 영역 우선, 헤더/푸터 기본 요소(로고, 메뉴, SNS 등)는 별도 표시
5. 카테고리 분류:
   - **버튼**: `button`, `[role="button"]`
   - **링크**: `a[href]` (내부/외부 구분)
   - **필터/정렬**: `select`, `[role="combobox"]`, 필터/정렬 관련 텍스트 포함 요소
   - **토글/아코디언**: `details > summary`, `[aria-expanded]`, `[data-toggle]`
   - **탭**: `[role="tab"]`
   - **폼 입력**: `input`, `textarea`, `select` (폼 컨텍스트)
   - **기타**: 위에 해당하지 않는 인터랙티브 요소
6. Phase 2의 정책/요구사항 텍스트와 대조하여 **Figma/PRD에 없는 요소** 식별

### 출력 형식
```
🔎 인터랙티브 요소 자동 탐색:
  버튼: N개 | 링크: N개 | 필터/정렬: N개 | 토글/아코디언: N개 | 탭: N개 | 폼: N개
  Figma/PRD 미언급 요소: N개 → 자동 TC 생성 대상
```

### 노이즈 제한
- 자동 생성 TC는 **최대 20개**로 제한
- 본문(main) 영역 요소 우선
- 반복 요소(상품 카드 내 동일 버튼 등)는 대표 1개만

### 이커머스 감지
장바구니 아이콘, `/cart` URL, ATC 버튼, 수량 조절 등이 발견되면 `ecommerce_detected = true`로 표시. Phase 3-4-G 장바구니 심화 TC 생성에 사용.

결과물: `discovered_elements` (카테고리별 요소 목록 + Figma/PRD 매칭 여부)

---

## Phase 3: TC 생성

다음을 종합하여 TC를 생성:
- **Phase 2**: 카테고리별 정책/요구사항 + 디자인 수치
- **Phase 2.3**: Figma↔사이트 매핑 (카테고리별 검증 URL + 영역 구조 + 불일치 목록)
- **Phase 2.5**: 분기 요인별 테스트 대상 URL
- **Phase 2.7**: 자동 탐색된 인터랙티브 요소

기준은 항상 **"어떻게 되어야 하는가"**.

> **카테고리별 TC 생성**: TC는 Phase 2.3에서 매핑된 카테고리 단위로 구분하여 생성한다.
> 예: `[PDP] TC-01`, `[PLP] TC-01`, `[Cart] TC-01` 등.
> 분기 TC, 인터랙션 TC, 시나리오 TC, 공통 TC 모두 **카테고리별로 각각** 생성한다.

### TC 구조

```
TC ID | 사전조건 | 시나리오 | 동작 | 기대결과 | 검증 대상 URL | 검증 레벨
```

- **사전조건**: 어떤 상태의 상품/페이지에서 테스트하는지 (Phase 2.5에서 확보)
- **검증 레벨**: L1(정적) / L2(단일 인터랙션) / L3(시나리오 플로우)

### 3-1. 분기 TC

정책에 조건이 있으면 **양쪽 TC를 모두 생성**한다. 한쪽만 만들지 않는다.

**규칙**: 정책에서 "~인 경우 A / 아닌 경우 B"가 있으면:
```
TC-{N}a: [조건 충족] → 기대결과 A
  URL: Phase 2.5에서 확보한 조건 충족 URL | L1

TC-{N}b: [조건 미충족] → 기대결과 B
  URL: Phase 2.5에서 확보한 조건 미충족 URL | L1
```

조건이 3개 이상이면 (예: 상태 A/B/C) 각각에 대한 TC를 모두 생성.

### 3-2. 인터랙션 TC

단순 존재 확인이 아니라 **클릭 전후 상태 변화**를 검증:

**규칙**: 인터랙티브 요소(버튼, 링크, 필터, 정렬, 토글 등)에 대해:
```
TC-{N}: [사전조건] {요소} 클릭/입력 → {기대되는 상태 변화} | L2
```

상태 변화 확인 방식:
- 목록 변경: 클릭 전 항목 목록 캡처 → 클릭 후 재캡처 → 차이 비교
- 순서 변경: 클릭 전 순서 → 클릭 후 순서 → 순서 변화 여부
- 노출 변경: 클릭 전 높이/display → 클릭 후 변화
- 카운트 변경: 클릭 전 숫자 → 클릭 후 숫자
- 페이지 이동: 클릭 전 URL → 클릭 후 URL

### 3-3. 시나리오 플로우 TC

Figma/PRD에서 도출된 **핵심 사용자 플로우**를 여러 단계 순차 인터랙션으로 검증:

**규칙**: 정책/PRD에서 사용자의 주요 목적(구매, 탐색, 비교 등)을 식별하고, 각 목적을 달성하기 위한 단계별 플로우를 시나리오로 구성.
```
SN-{N}: {플로우 이름} [사전조건]
  1. {동작} → {기대결과}
  2. {동작} → {기대결과}
  ...
  URL: Phase 2.5에서 확보한 적합 URL | L3
```

시나리오는 의존성이 있다: 한 단계 FAIL → 이후 단계 SKIP.

### 3-4. 공통 TC — 표준 UX 패턴 (항상 포함)

Figma/PRD와 무관하게, 사용자가 당연히 기대하는 기본 동작을 검증한다.
Phase 2.7의 `discovered_elements` 결과를 활용하여 자동 생성.

#### 3-4-A. 기본 검증 (기존)

- 필수 정보 노출: 페이지 제목, 핵심 콘텐츠, 이미지 로드 | L1 | 매우높음
- 핵심 인터랙티브 요소: 주요 버튼/링크 동작 | L2 | 매우높음
- 링크 정상 여부: 404 없음 | L1 | 매우높음
- 반응형: 3해상도에서 주요 요소 존재 + 레이아웃 전환 | L1 | 보통

#### 3-4-B. 상태 전환 무결성 | L2 | 높음

상태를 변경하는 모든 액션에서, 관련 UI가 **동시에 일관되게** 업데이트되는지 확인.
중간에 불일치 상태(고스트 UI)가 사용자에게 노출되면 안 된다.

**TC 패턴**:
```
TC-{N}: {요소} 클릭 → 관련 UI(카운트, 합계, 배지, 섹션)가 동시 업데이트 또는 로딩 표시 | L2
```

**필수 검증 항목**:
- 아이템 추가/제거 → 카운트, 합계, 관련 배지가 동시 업데이트 또는 로딩 표시
- 토글/필터 변경 → 목록과 카운트가 동시 반영
- 마지막 아이템 제거 → 빈 상태로 깨끗하게 전환 (잔여 UI 없음)
  - 예: 장바구니에서 마지막 상품 삭제 시, 상품은 사라졌는데 Discount/Checkout UI가 남아있으면 FAIL

**판정**: Phase 4의 전환 품질 측정에서 자동 감지 (100ms 이상 불일치 → 경고, 500ms 이상 → FAIL)

#### 3-4-C. 자동 탐색 인터랙션 | L2 | 높음

Phase 2.7에서 발견되었으나 **Phase 3-1/3-2/3-3 TC에 포함되지 않은** 인터랙티브 요소에 대해 자동 생성.

**TC 패턴**:
```
TC-{N}: [자동탐색] {요소 종류} "{텍스트}" 클릭 → 상태 변화 발생 | L2
```

**요소별 기대 동작**:
- **필터/정렬(select, checkbox)**: 선택 → 목록 콘텐츠 또는 순서 변경
- **아코디언/토글([aria-expanded])**: 클릭 → expand/collapse 상태 전환
- **탭([role="tab"])**: 클릭 → 연결된 패널 콘텐츠 전환
- **버튼(button)**: 클릭 → 관찰 가능한 반응 (네비게이션, 모달, DOM 변경)
- **내부 링크(a[href])**: 클릭 → 유효한 페이지 이동

**제한**: 최대 20개. 기능 요소(필터, 정렬, 탭 등) 우선, 장식 요소 후순위.

#### 3-4-D. 폼 & 입력 검증 | L2 | 높음

Phase 2.7에서 `input`, `select`, `textarea`, `form` 요소가 발견된 경우에만 생성.

**TC 패턴**:
```
TC-{N}: {입력 필드} 잘못된 값 입력 → 에러/검증 메시지 노출 | L2
TC-{N}: {필수 필드} 빈 값 제출 → 검증 메시지 노출 | L2
```

**필수 검증 항목**:
- 이메일 필드 → 잘못된 형식 입력 ("abc") → 에러 메시지 또는 HTML5 validation
- 필수 필드 → 빈 값으로 폼 제출 시도 → 검증 메시지
- 검색 필드 → 빈 검색 / 유효한 검색어 / 결과 없는 검색어 → 각각 적절한 피드백
- 숫자 입력(수량 등) → 범위 밖 값(0, 음수, 9999) → 적절한 제한 또는 에러

#### 3-4-E. 로딩 & 에러 상태 | L1/L2 | 보통

비동기 작업 시 사용자에게 적절한 피드백이 제공되는지 확인.

**TC 패턴**:
```
TC-{N}: {비동기 액션} 실행 → 로딩 인디케이터/스피너 노출 | L2
TC-{N}: 페이지 초기 로드 → 스켈레톤/스피너 후 콘텐츠 전환 | L1
```

**검증 방법**:
- 의도적 네트워크 지연 시뮬레이션은 하지 않음
- 자연 발생하는 로딩 상태를 캡처하여, 로딩 UI가 존재하는지 확인
- 필터/정렬 변경, 페이지네이션, 검색 등 비동기 액션 시 확인

#### 3-4-F. 네비게이션 일관성 | L2 | 보통

페이지 내 네비게이션이 예상대로 동작하는지 확인.

**TC 패턴**:
```
TC-{N}: 모달/드로어 닫기 → 페이지 상태 유지 (스크롤, 필터 등) | L2
TC-{N}: 뒤로가기 → 이전 페이지 상태 복원 | L2
TC-{N}: 앵커 링크 → 해당 섹션으로 스크롤 | L2
```

#### 3-4-G. 장바구니 심화 | L3 | 매우높음

**Phase 2.7에서 `ecommerce_detected = true`인 경우에만 생성.**

장바구니의 핵심 조작이 정상 동작하는지 E2E로 검증:

```
SN-{N}: 장바구니 조작 심화 플로우
  1. 상품 ATC → 장바구니 열기 → 상품 존재 확인
  2. 수량 증가(+) → 합계 즉시 반영
  3. 수량 감소(-) → 합계 즉시 반영
  4. 아이템 제거(Remove) → 목록 업데이트 + 합계 반영 + 전환 품질 검증
  5. (마지막 아이템이면) 빈 상태 전환 → "빈 장바구니" 메시지 즉시 노출, 고스트 UI 없음
```

**마지막 아이템 제거 전환 검증** (핵심):
- Remove 클릭 후 MutationObserver로 DOM 변화 추적
- 상품 행 제거 후 ~ 빈 상태 메시지 노출 사이에 **불필요한 중간 UI**(Discount, Checkout 버튼, 이전 수량/합계 등)가 보이면 FAIL
- 판정 기준: 상품 제거 후 300ms 이내에 빈 상태 또는 로딩 표시가 나와야 함

### 자동 분류 우선순위 (3-4 전용)

[reference/priority-guide.md](reference/priority-guide.md) 기준에 추가:

| 항목 | 우선순위 |
|------|---------|
| 상태 전환 불일치 > 500ms (고스트 UI) | 높음 |
| 상태 전환 불일치 100~500ms | 보통 (경고) |
| 자동 탐색된 기능 요소 미동작 | 높음 |
| 폼 검증 누락 | 높음 |
| 장바구니 고스트 상태 | 매우높음 |
| 로딩 인디케이터 미노출 | 보통 |
| 네비게이션 불일치 | 보통 |

### 우선순위 분류
[reference/priority-guide.md](reference/priority-guide.md) 기준 + 위 자동 분류 기준 적용.

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

#### 전환 품질 측정 (Transition Quality Check)

모든 L2 TC 실행 시, 클릭 전후의 **DOM 변경 타이밍**을 자동 측정하여 중간 불일치 상태를 감지한다.

**사전 상태 캡처 시 (browser_evaluate) — MutationObserver 설치**:
```javascript
// browser_evaluate 내에서 사전 상태 캡처와 함께 실행
window.__qa_transition = { clickTime: performance.now(), mutations: [] };
const observer = new MutationObserver((muts) => {
  window.__qa_transition.mutations.push({
    time: performance.now() - window.__qa_transition.clickTime,
    count: muts.length
  });
});
observer.observe(document.body, { childList: true, subtree: true, attributes: true });
window.__qa_transition.observer = observer;
```

**사후 상태 수집 시 (browser_evaluate) — 전환 품질 데이터 수집**:
```javascript
window.__qa_transition.observer.disconnect();
const muts = window.__qa_transition.mutations;
// 변경 배치 간 100ms 이상 간격이 있으면 다단계 업데이트 감지
let maxGap = 0;
for (let i = 1; i < muts.length; i++) {
  maxGap = Math.max(maxGap, muts[i].time - muts[i-1].time);
}
return { maxGapMs: maxGap, batchCount: muts.length };
```

**판정 기준**:

| 배치 간 최대 간격 | 판정 | 결과 |
|------------------|------|------|
| < 100ms | 정상 | PASS |
| 100~500ms | 경고 | PASS + `⚠ 전환 품질: {N}ms 간격 다단계 업데이트` 메모 |
| > 500ms | 소프트 FAIL | FAIL (높음) + 스크린샷 + `❌ 전환 품질: {N}ms 불일치 상태 노출` |

이 측정은 모든 L2 TC에 자동 적용되며, 특히 3-4-B(상태 전환 무결성)와 3-4-G(장바구니 심화) TC에서 핵심적으로 활용된다.

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

    // Level 2: 인터랙션 TC 순차 (전환 품질 측정 포함)
    대화에 "    L2 인터랙션 검증..." 출력
    for each interaction_tc:
      before = browser_evaluate(사전 상태 + MutationObserver 설치)
      browser_click(대상)
      browser_wait_for(500ms 또는 DOM 안정)
      after = browser_evaluate(사후 상태 + 전환 품질 데이터 수집)
      result = compare(before, after)
      transition = after.transitionQuality
      if transition.maxGap > 500ms:
        result = FAIL
        browser_take_screenshot
        대화에 "    {TC-ID}: FAIL ❌ 전환 품질: {maxGap}ms 불일치 상태" 출력
      elif transition.maxGap > 100ms:
        대화에 "    {TC-ID}: {PASS/FAIL} ⚠ 전환 {maxGap}ms 다단계 업데이트" 출력
      else:
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
