# QA Automation Plugin for Claude Code

웹 QA 자동화 플러그인. URL + Figma + PRD를 기반으로 TC를 자동 생성하고 Playwright로 검증합니다.

## 설치

```bash
claude /plugin install https://github.com/minmk-crypto/claude-qa-plugin
```

## 사전 조건

- **Playwright MCP** 연결 필수 (`/mcp`에서 확인)
- **Notion MCP** (선택) — PRD 자동 읽기용

## 스킬 목록

| 명령어 | 용도 | 단독 사용 |
|--------|------|----------|
| `/qa` | **전체 플로우** — 인풋 수집 → 분석 → TC 생성 → 검증 → 리포트 → Jira | - |
| `/qa-analyze` | 소스 분석 — Figma API, Notion PRD, 사이트 구조 | O |
| `/qa-report` | 리포트 생성 — 결과 JSON → 엑셀 + md | O |
| `/qa-jira` | Jira 티켓 — FAIL → 서브태스크 + 스크린샷 첨부 | O |

## 사용법

### 전체 QA (한 번에)
```
/qa
```
→ URL/Figma/PRD 질문 → TC 생성 → 검증 → 리포트 → "Jira 올릴까요?"

### URL 직접 지정
```
/qa https://example.com
```

### 분석만
```
/qa-analyze https://example.com
```

### 리포트 재생성
```
/qa-report output/reports/2026-04-09-qa-results.json
```

### Jira만 (나중에 티켓 올리기)
```
/qa-jira output/reports/2026-04-09-qa-results.json --project FP --parent FP-413
```

## 구조

```
claude-qa-plugin/
├── .claude-plugin/plugin.json
├── README.md
└── skills/
    ├── qa/                          # 메인 오케스트레이터
    │   ├── SKILL.md
    │   └── reference/
    │       └── priority-guide.md    # 우선순위 기준
    ├── qa-analyze/                  # 소스 분석
    │   └── SKILL.md
    ├── qa-report/                   # 리포트 생성
    │   ├── SKILL.md
    │   └── scripts/
    │       └── generate-report.py
    └── qa-jira/                     # Jira 티켓
        ├── SKILL.md
        └── scripts/
            └── jira-tickets.py
```

## 결과물

- `output/reports/YYYY-MM-DD-qa-{페이지}.xlsx` — TC 시트 (색상 코딩)
- `output/reports/YYYY-MM-DD-qa-{페이지}.md` — 리포트
- `output/reports/YYYY-MM-DD-qa-results.json` — 결과 데이터 (재사용 가능)
- 스크린샷 (FAIL 건)
