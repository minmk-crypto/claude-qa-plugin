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
Phase 2.8: 디자인 정책 문서 생성 (이 스킬에서 직접)
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

## Phase 2.8: 디자인 정책 문서 생성

Phase 2~2.7의 모든 분석 결과를 종합하여, **기능 명세 수준의 정책 문서**를 wiki에 자동 저장한다.

> 이 단계의 목적은 TC의 근거가 되는 정책을 영구 문서로 보존하여 추적 가능성과 재사용성을 확보하는 것.
> 정책 문서는 **정책 → 유저 스토리 → TC**의 3단계 추적 구조를 제공한다.

### 저장 경로

`wiki/guides/{project}/qa-design-policy.md`

- `{project}`: Phase 1에서 사용자가 제공한 프로젝트명, 또는 검증 대상 URL의 도메인에서 추론 (예: `piyonna-fr.com` → `piyonna`)
- **프로젝트명 결정 규칙**: 동일 프로젝트의 정책 문서가 이미 `wiki/guides/` 하위에 존재하면 해당 폴더명을 재사용한다

### Frontmatter

```yaml
---
type: wiki
category: guide
tags: [qa, design-policy, {project}]
date_created: YYYY-MM-DD
last_compiled: YYYY-MM-DD
figma_file_key: "{file_key}"
figma_last_modified: "YYYY-MM-DDTHH:MM:SSZ"
sources:
  - "figma:{figma_file_url}"
  - "prd:{prd_url}"
related: []
---
```

- `figma_file_key`: Figma API 응답의 파일 키
- `figma_last_modified`: Figma API `/v1/files/{key}` 응답의 `lastModified` 값

### 반복 실행 시 merge 전략

기존 정책 문서가 있을 때의 업데이트 규칙:

1. **source 마커**: 정책 문서의 모든 항목(테이블 행)은 `source` 열로 출처를 표시한다
   - `figma` — Figma API에서 자동 추출
   - `prd` — PRD에서 자동 추출
   - `site` — Phase 2.7 사이트 탐색에서 자동 발견
   - `manual` — 사용자가 직접 추가
2. **재실행 시 동작**:
   - `figma` / `prd` / `site` 소스 항목: 새 분석 결과로 **덮어쓰기** (재생성)
   - `manual` 소스 항목: **보존** (삭제하지 않음)
   - 새로 추출된 항목이 기존 `manual` 항목과 같은 요소를 다루면: 양쪽 모두 유지하고, 대화에 충돌을 알림
3. **frontmatter 갱신**: `last_compiled`, `figma_last_modified`를 최신값으로 업데이트

### 문서 구조 (7개 섹션)

#### 1. 디자인 정책
**데이터 소스**: Phase 2 `figma_design_values` (qa-analyze 출력)

시각적 수치를 카테고리별로 정리:

```markdown
## 1. 디자인 정책

### 레이아웃
| 요소 | 속성 | 값 | Figma 노드 | source |
|------|------|-----|-----------|--------|
| 상품 이미지 | ratio | 1:1 | {node_id} | figma |
| 캐러셀 카드 | width | 212px | {node_id} | figma |

### 타이포그래피
| 요소 | font-size | font-weight | line-height | source |
|------|-----------|-------------|-------------|--------|

### 컬러
| 용도 | 값 | 적용 요소 | source |
|------|-----|----------|--------|

### 간격
| 요소 간 | margin/padding | 값 | source |
|--------|---------------|-----|--------|
```

#### 2. 동작 정책
**데이터 소스**: Phase 2 `figma_policies` 중 인터랙션 항목 (qa-analyze 분류)

"트리거 → 결과" 형태로 명세. 각 항목에 ID 부여 (TC에서 근거로 참조):

```markdown
## 2. 동작 정책

| ID | 트리거 | 기대 동작 | 조건 | 예외(Edge Case) | source |
|----|--------|----------|------|----------------|--------|
| B-01 | 검색어 입력 + 엔터 | 검색 결과 페이지 이동 | - | 빈 검색어: 미동작 / 특수문자만: 결과 없음 표시 | figma |
| B-02 | 필터 선택 | 목록 필터링 + 카운트 업데이트 | - | 결과 0건: "결과 없음" 메시지 | prd |
| B-03 | ATC 버튼 클릭 | 장바구니 추가 + 카운트 +1 | 재고 있음 | 품절: 비활성 / 최대수량 초과: 안내 메시지 | figma |
```

> **예외 열 작성 규칙**: "네트워크 끊김", "데이터 없음", "권한 없음" 등 극단 상황을 각 동작별로 기록. 단, 프론트엔드 QA 범위 내의 예외만 포함 (서버 에러 등은 제외).

#### 3. 데이터 정책
**데이터 소스**: Phase 2 `figma_policies` + `prd_requirements`

데이터 노출 조건을 명세:

```markdown
## 3. 데이터 정책

| ID | 데이터 항목 | 노출 조건 | 미충족 시 | 출처 | source |
|----|-----------|----------|----------|------|--------|
| D-01 | 가격 비교 카드 | 가격 우위 시 | 미노출 | Figma + PRD | figma |
| D-02 | 할인율 배지 | 할인 상품 | 미노출 | Figma | figma |
| D-03 | 재고 경고 | 재고 5개 이하 | 미노출 | PRD | prd |
| D-04 | ⚠ TBD: 리뷰 정렬 기준 | 미정 | - | PRD (모호 문구) | prd |
```

#### 4. 상태 정의 & 예외 케이스
**데이터 소스**: Phase 2 `figma_policies` + `prd_requirements`에서 상태/예외 항목 분류

서비스의 각 상태를 정의하고, 상태 간 전이 조건과 예외를 명세한다.

```markdown
## 4. 상태 정의 & 예외 케이스

### 상태 전이
| ID | 영역 | 상태 | 전이 조건 | 다음 상태 | source |
|----|------|------|----------|----------|--------|
| ST-01 | 장바구니 | 비어있음 | ATC | 상품 있음 | figma |
| ST-02 | 장바구니 | 상품 있음 | 마지막 상품 제거 | 비어있음 | figma |
| ST-03 | 상품 | 판매중 | 재고 소진 | 품절 | prd |

### 비즈니스 제약
| ID | 제약 | 조건 | 초과 시 동작 | source |
|----|------|------|------------|--------|
| BC-01 | 장바구니 최대 수량 | 100개 | 안내 메시지 노출 | prd |
| BC-02 | 쿠폰 중복 적용 | 불가 | 기존 쿠폰 해제 후 적용 | prd |

### 예외 케이스 (공통)
| ID | 상황 | 기대 동작 | source |
|----|------|----------|--------|
| EX-01 | 네트워크 오류 | 에러 메시지 + 재시도 버튼 | manual |
| EX-02 | 데이터 로딩 실패 | 스켈레톤/스피너 → 에러 상태 | manual |
| EX-03 | 빈 데이터 (0건) | "결과 없음" 안내 메시지 | manual |
```

#### 5. 컴포넌트 정보
**데이터 소스**: Phase 2 Figma API `componentId`/`name` + Phase 2.3/2.7 사이트 탐색 결과

Figma 컴포넌트와 실제 DOM 요소의 매핑:

```markdown
## 5. 컴포넌트 정보

| Figma 컴포넌트명 | 사이트 대응 | Selector Hint | 비고 | source |
|-----------------|-----------|---------------|------|--------|
| ProductCard | .product-card | [data-testid="product-card"] | PLP 상품 카드 | figma |
| AddToCartBtn | button.atc | button[name="add"] | PDP ATC | site |
| PriceDisplay | .price-wrap | [class*="price"] | 가격 영역 | figma |
```

- **Selector Hint**: Phase 2.3/2.7에서 `browser_evaluate`로 수집한 실제 DOM selector
- Figma 컴포넌트명은 API 응답의 `name` + `componentId`에서 추출
- Figma에만 있고 사이트에 매핑되지 않는 컴포넌트도 기록 (Selector Hint = `미확인`)

#### 6. 유저 스토리
**데이터 소스**: 섹션 2(동작 정책) + 섹션 3(데이터 정책) + 섹션 4(상태 정의)에서 자동 도출

정책에서 바로 TC로 점프하지 않고, **유저 스토리 + 인수 조건(AC)**을 중간 단계로 생성한다.
인수 조건이 Phase 3 TC의 기대결과로 직결된다.

```markdown
## 6. 유저 스토리

### US-01: 장바구니 담기
**As a** 구매자, **I want to** 마음에 드는 상품을 장바구니에 담아, **So that** 나중에 한꺼번에 결제할 수 있다.

**Acceptance Criteria:**
1. 상품 상세에서 '장바구니' 버튼 클릭 → 장바구니에 추가 (근거: B-03)
2. 동일 상품 재추가 → 수량 합산 (근거: B-03)
3. 최대 수량 초과 → 안내 메시지 (근거: BC-01)
4. 품절 상품 → ATC 비활성 (근거: B-03 예외)

### US-02: 상품 검색
**As a** 방문자, **I want to** 원하는 상품을 검색하여, **So that** 빠르게 상품을 찾을 수 있다.

**Acceptance Criteria:**
1. 검색어 입력 + 엔터 → 검색 결과 페이지 이동 (근거: B-01)
2. 빈 검색어 → 미동작 (근거: B-01 예외)
3. 결과 없는 검색어 → "결과 없음" 메시지 (근거: B-01 예외)
```

**유저 스토리 생성 규칙**:
1. 동작 정책(B-xx)의 각 주요 인터랙션을 사용자 목적 단위로 그룹핑
2. 데이터 정책(D-xx)에서 노출 조건이 있는 항목을 AC로 포함
3. 상태 정의(섹션 4)의 비즈니스 제약을 AC의 경계 조건으로 포함
4. 예외 케이스를 AC의 부정 시나리오로 포함
5. 각 AC에 근거 정책 ID를 명시 (TC 추적용)
6. 이커머스 사이트에서는 핵심 유저 스토리를 우선 생성: 상품 탐색, 상품 상세 조회, 장바구니, 결제

#### 7. 일반 UX 동작 정책
**데이터 소스**: Phase 2.7 `discovered_elements` (qa-analyze 범위 아님, 사이트 탐색 결과)

Figma/PRD에 명시되지 않았지만 사이트 탐색에서 발견한 인터랙션 패턴:

```markdown
## 7. 일반 UX 동작 정책

Phase 2.7 사이트 탐색에서 발견한 인터랙션 패턴. Figma/PRD에 명시되지 않았지만 검증 대상.

| 카테고리 | 요소 | Selector | 동작 | 기대 결과 | source |
|---------|------|----------|------|----------|--------|
| 필터 | Sort by select | select.sort-by | 옵션 변경 | 목록 순서 변경 | site |
| 아코디언 | FAQ details | details.faq | 클릭 | expand/collapse | site |
| 탭 | Reviews tab | [role="tab"]:nth(2) | 클릭 | 리뷰 패널 전환 | site |
```

### 생성 프로세스

1. Phase 2의 JSON 결과 (`figma_policies`, `figma_design_values`, `prd_requirements`)를 **섹션 1-3**으로 변환
   - qa-analyze가 제공하는 카테고리 데이터 사용
   - 인터랙션 항목 분류 기준에 따라 동작/데이터 정책 분리
2. Phase 2의 상태/예외 데이터를 **섹션 4**로 변환 (상태 정의 & 예외)
3. Phase 2.3의 Figma-사이트 매핑 결과에서 컴포넌트 대응 정보를 **섹션 5**로 변환
4. 섹션 2+3+4를 기반으로 **섹션 6**을 자동 생성 (유저 스토리)
5. Phase 2.7의 `discovered_elements`에서 Figma/PRD 미언급 요소를 **섹션 7**로 변환
6. 기존 정책 문서가 있으면 merge 전략 적용 (`manual` 항목 보존)
7. frontmatter 생성/갱신 + wiki 저장
8. `_index/MASTER_INDEX.md` 업데이트: `| [[wiki/guides/{project}/qa-design-policy]] | {project} QA 디자인 정책 — 동작/데이터/컴포넌트/유저 스토리 명세 |` 형식으로 추가
9. 대화에 요약 출력:
   ```
   📋 디자인 정책 문서 생성 완료:
     wiki/guides/{project}/qa-design-policy.md
     - 디자인 정책: N개 수치
     - 동작 정책: N개 명세
     - 데이터 정책: N개 조건
     - 상태 & 예외: 상태 N개, 제약 N개, 예외 N개
     - 컴포넌트: N개 매핑
     - 유저 스토리: N개 (AC 총 N개)
     - UX 동작: N개 패턴
     - 수동 항목 보존: N개
   ```

---

## Phase 3: TC 생성

### Phase 3 시작 전: 정책 문서 로드

1. `wiki/guides/{project}/qa-design-policy.md`가 존재하면 Read로 로드
2. frontmatter의 `figma_last_modified`와 현재 실행의 Figma 응답 `lastModified`를 비교
   - 불일치 시: `⚠ 정책 문서가 Figma 최신 버전과 다릅니다. Phase 2.8에서 갱신된 버전을 사용합니다.`
3. 정책 문서가 없으면 Phase 2 JSON 결과를 직접 참조

다음을 종합하여 TC를 생성:
- **Phase 2.8 정책 문서** — 1차 참조:
  - 유저 스토리(US-xx)의 Acceptance Criteria → TC의 기대결과
  - 동작 정책(B-xx), 데이터 정책(D-xx) → TC 근거
  - 상태 정의(섹션 4) → 분기 TC의 사전조건
  - 컴포넌트 정보(섹션 5) → Selector Hint로 Playwright 검증 활용
- **Phase 2.3**: Figma↔사이트 매핑 (카테고리별 검증 URL + 영역 구조 + 불일치 목록)
- **Phase 2.5**: 분기 요인별 테스트 대상 URL
- **Phase 2.7**: 자동 탐색된 인터랙티브 요소
- **Phase 2 JSON**: 정책 문서 미생성 시 fallback

기준은 항상 **"어떻게 되어야 하는가"**.

> **카테고리별 TC 생성**: TC는 Phase 2.3에서 매핑된 카테고리 단위로 구분하여 생성한다.
> 예: `[PDP] TC-01`, `[PLP] TC-01`, `[Cart] TC-01` 등.
> 분기 TC, 인터랙션 TC, 시나리오 TC, 공통 TC 모두 **카테고리별로 각각** 생성한다.

### TC 구조

```
TC ID | 사전조건 | 시나리오 | 동작 | 기대결과 | 검증 대상 URL | 검증 레벨 | 근거
```

- **사전조건**: 어떤 상태의 상품/페이지에서 테스트하는지 (Phase 2.5에서 확보)
- **검증 레벨**: L1(정적) / L2(단일 인터랙션) / L3(시나리오 플로우)
- **근거**: 유저 스토리 AC 또는 정책 문서 항목 ID (예: `US-01.AC-2`, `B-03`, `D-01`). 공통 TC(3-4)는 `공통` 표기

### TC 설계 기법

정책 문서의 유저 스토리(AC)에서 TC를 도출할 때, 다음 기법을 적용하여 커버리지를 확보한다.

#### Happy Path → Abnormal Path 순서

각 유저 스토리별로 **정상 시나리오(Happy Path)를 먼저** 작성한 후, 비정상 시나리오(Abnormal Path)를 확장한다:
1. Happy Path: AC의 정상 조건 → 정상 결과 (사전조건 충족, 정상 입력)
2. Abnormal Path: AC의 예외/경계 조건 → 예외 결과 (품절, 빈 값, 초과 등)

#### 경계값 분석 (BVA)

수량, 길이, 금액 등 **수치 제한이 있는 AC**에 적용:
- 제한이 1~N이면: 0, 1, N, N+1을 TC로 생성
- 예: 장바구니 최대 100개 → TC: 0개(빈 상태), 1개, 100개(최대), 101개(초과)

#### 동등 분할 (EP)

**입력 유형이 여러 그룹으로 나뉘는 AC**에 적용:
- 유효 그룹과 무효 그룹에서 대표값 하나씩 선정
- 예: 검색어 입력 → 유효(일반 텍스트), 무효(빈 문자열), 무효(특수문자만)

#### 결정 테이블 (Decision Table)

**여러 조건이 복합적으로 얽힌 AC**에 적용:
- 조건 2개 이상이 교차하면 조합표를 생성하여 모든 경우를 커버
- 예: (쿠폰 적용 여부) × (회원 등급) × (할인 상품 여부) → 조합별 TC

> 모든 TC에 기법을 강제하지 않는다. 단순 존재 확인(L1)은 기법 불필요.
> 수치가 있으면 BVA, 입력 유형이 있으면 EP, 조건이 복합적이면 Decision Table을 적용한다.

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

### 피드백 루프: 정책 오류 → 정책 문서 반영

Phase 4 검증 중 **정책 문서 자체의 오류**가 발견되면, Phase 5 리포트 전에 정책 문서를 업데이트한다:

1. **정책 불일치 발견**: TC FAIL 원인이 "정책이 틀렸다" (사이트가 맞고 정책이 잘못된 경우)
   - 예: 정책 문서에 "가격 비교 카드는 가격 우위 시에만 노출"이라 했는데, 실제로는 항상 노출
2. **업데이트 동작**:
   - 해당 정책 항목에 `⚠ 검증 결과 불일치` 태그 추가
   - TC 결과를 FAIL이 아닌 `REVIEW` (정책 검토 필요)로 변경
   - **하류 스킬 호환**: REVIEW는 qa-report에서 기존 `확인필요` (주황)로 렌더링. qa-jira에서는 REVIEW 항목 제외 (결함이 아닌 정책 검토 사항)
   - 대화에 알림: `⚠ 정책 불일치 발견: D-01 "가격 비교 카드 노출 조건" — 실제 사이트와 정책이 다릅니다. 정책 문서에 검토 태그를 추가했습니다.`
3. **판단 기준**: 사이트의 동작이 명백히 의도된 것(일관되게 동작)이고, 정책/Figma가 업데이트되지 않은 것으로 추정되는 경우에만 적용

> 이 피드백은 자동이 아닌 **반자동**: 불일치를 감지하고 태그만 추가. 정책의 실제 수정은 사용자 확인 후.

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
