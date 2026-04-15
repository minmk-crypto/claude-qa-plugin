---
name: qa-analyze
description: "QA용 소스 분석. Figma API에서 디자인 정책 추출, Notion에서 PRD 요구사항 추출. TC 생성의 기반 데이터를 만든다."
allowed-tools: Bash Read Write Grep
argument-hint: "[--figma URL:TOKEN] [--notion URL]"
---

# QA 소스 분석

디자인 정책(Figma)과 요구사항(PRD)을 분석하여 TC 생성의 기반 데이터를 만든다.

> **이 스킬은 "어떻게 되어야 하는가"를 정의하는 소스만 분석한다.**
> 실제 사이트는 분석하지 않는다 — 사이트는 검증 대상이지 TC의 기준이 아니다.

**사용법:**
- `/qa-analyze --figma URL:TOKEN` — Figma 분석
- `/qa-analyze --notion URL` — PRD 분석
- `/qa-analyze` — 인풋을 질문 받음

**단독 사용 가능.** `/qa`에서 호출되기도 하고, "이 Figma 정책 추출해줘"로도 사용.

---

## 분석 대상

### A. Figma (URL + 토큰 제공 시)

```bash
curl -s "https://api.figma.com/v1/files/{file_key}/nodes?ids={node_id}&depth=5" \
  -H "X-Figma-Token: {token}"
```

추출:
- TEXT 노드 → 정책 설명, 규칙, 주석, 조건, 예외
- FRAME 이름(20자+) → 정책 제목/섹션
- 수치 → 마진, 패딩, 너비, 비율, 폰트 크기
- 상태 정의 → 서비스 상태 목록과 전이 조건 (예: "결제 완료 → 배송 중 → 배송 완료")
- 예외 케이스 → 극단적 상황에 대한 처리 (예: "데이터 없음", "네트워크 오류", "권한 없음")
- 비즈니스 제약 → 수량 제한, 사용자 등급별 차이, 시간 제한 등의 비즈니스 로직

### B. Notion PRD (URL 제공 + Notion MCP 연결 시)

```
notion-fetch(id: URL)
```

추출:
- 기능 요구사항
- 노출 정책/조건
- 예외 케이스
- 비즈니스 규칙
- 스펙아웃/TBD 항목 (제외 대상으로 표시)
- 상태 전이 다이어그램 (명시적 상태 흐름이 있는 경우)
- 모호한 문구 식별 → "적절히 처리", "추후 구현" 등 → 대화에 경고 출력

---

## 출력

분석 결과를 JSON으로 저장:
```json
{
  "figma_policies": [
    {"section": "가격비교", "rule": "가격 우위 시에만 노출", "conditions": [...], "exceptions": [...]},
    ...
  ],
  "figma_design_values": [
    {"element": "이미지", "property": "ratio", "value": "1:1"},
    {"element": "캐러셀 카드", "property": "width", "value": "212px"},
    ...
  ],
  "prd_requirements": [
    {"id": "B-1", "feature": "타사 가격 비교", "condition": "가격 우위 시", "expected": "비교 카드 노출"},
    ...
  ]
}
```

대화에도 요약 출력: 정책 N개, 요구사항 N개, 디자인 수치 N개.

---

## 정책 문서용 데이터 (Phase 2.8 연동)

`/qa` 플로우에서 호출될 때, 위 JSON 출력 외에 Phase 2.8이 정책 문서를 생성하기 위한 **구조화된 데이터**를 함께 전달한다.

> **단독 호출 시**: JSON 출력만 생성. 정책 문서 파일은 생성하지 않는다.
> **`/qa` 플로우 내 호출 시**: JSON + 아래 데이터를 Phase 2.8에 전달. 파일 생성은 Phase 2.8이 수행.

### 전달 데이터 (5개 카테고리)

| 카테고리 | 소스 | 내용 |
|---------|------|------|
| **디자인 정책** | `figma_design_values` | 레이아웃, 컬러, 타이포, 간격 수치 + Figma 노드 ID |
| **동작 정책** | `figma_policies` 중 인터랙션 항목 | "트리거 → 결과" 형태의 동작 명세 |
| **데이터 정책** | `figma_policies` + `prd_requirements` | 데이터 노출 조건 + 미충족 시 동작 |
| **상태 & 예외** | `figma_policies` + `prd_requirements` | 상태 정의, 전이 조건, 예외 케이스, 비즈니스 제약 |
| **컴포넌트 정보** | Figma API `componentId`, `name` 필드 | 컴포넌트명 + Figma 노드 ID |

> **일반 UX 동작 정책 (정책 문서 섹션 7)은 Phase 2.7의 `discovered_elements`에서 생성되며, qa-analyze의 범위가 아니다.**
> **유저 스토리 (정책 문서 섹션 6)는 Phase 2.8에서 위 데이터를 기반으로 자동 생성하며, qa-analyze의 범위가 아니다.**

### 인터랙션 항목 분류 기준

`figma_policies`에서 다음 키워드가 포함된 항목을 "동작 정책"으로 분류:
- 동사: 클릭, 탭, 스와이프, 입력, 선택, 스크롤, 호버, 토글, 열기, 닫기
- 결과: 이동, 노출, 숨김, 변경, 업데이트, 필터링, 정렬, 전환
- 조건: ~하면, ~시, ~때, if, when

### 상태/예외 항목 분류 기준

다음 패턴이 포함된 항목을 "상태 & 예외"로 분류:
- 상태: 완료, 대기, 진행 중, 취소, 만료, 활성, 비활성, 품절, 재고
- 예외: ~없으면, ~실패 시, ~오류, ~불가, 0개, 초과, 제한, timeout
- 제약: 최대, 최소, ~까지, ~이상, ~이하, 등급, 권한

나머지는 "데이터 정책" 또는 "디자인 정책"으로 분류.

### 모호 문구 감지

PRD에서 다음 패턴 발견 시 대화에 `⚠ 모호 문구 감지` 경고 출력:
- "적절히 처리", "추후 구현", "나중에", "TBD", "미정", "검토 필요"
- 정책 문서의 데이터 정책 섹션에 `⚠ TBD` 태그와 함께 기록
