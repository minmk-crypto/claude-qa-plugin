---
name: qa-analyze
description: "QA용 소스 분석. Figma API에서 정책 추출, Notion에서 PRD 추출, Playwright로 사이트 구조 분석."
allowed-tools: Bash Read Write Grep
argument-hint: "[url] [--figma URL:TOKEN] [--notion URL]"
---

# QA 소스 분석

검증 대상 페이지의 디자인 정책, PRD 요구사항, 실제 사이트 구조를 분석하여 TC 생성의 기반 데이터를 만든다.

**사용법:**
- `/qa-analyze https://example.com` — 사이트만 분석
- `/qa-analyze https://example.com --figma URL:TOKEN` — Figma도 분석
- `/qa-analyze` — 인풋을 질문 받음

**단독 사용 가능.** `/qa`에서 호출되기도 하고, 독립적으로 "이 페이지 구조 분석해줘"로도 사용.

---

## 분석 대상

### A. Figma (URL + 토큰 제공 시)

```bash
curl -s "https://api.figma.com/v1/files/{file_key}/nodes?ids={node_id}&depth=5" \
  -H "X-Figma-Token: {token}"
```

추출:
- TEXT 노드 → 정책 설명, 규칙, 주석
- FRAME 이름(20자+) → 정책 제목
- 수치 → 마진, 패딩, 너비, 비율

### B. Notion PRD (URL 제공 + Notion MCP 연결 시)

```
notion-fetch(id: URL)
```

추출:
- 기능 요구사항
- 노출 정책/조건
- 예외 케이스
- 비즈니스 규칙

### C. 실제 사이트 (항상)

Playwright로:
1. `browser_navigate` → URL 접속
2. `browser_snapshot` → 페이지 구조
3. `browser_evaluate` → DOM 요소 수집:
   - 모든 button, a[href], img, input, form, dialog
4. 3개 해상도(390/768/1280)에서 레이아웃 측정

---

## 출력

분석 결과를 JSON으로 저장:
```json
{
  "figma_policies": [...],
  "prd_requirements": [...],
  "site_structure": {
    "components": [...],
    "interactive_elements": [...],
    "layout_by_viewport": {...}
  }
}
```

대화에도 요약 출력.
