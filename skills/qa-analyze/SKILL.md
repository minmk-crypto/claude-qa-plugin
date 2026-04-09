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
