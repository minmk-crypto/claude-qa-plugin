# gb-tf: QA Automation Plugin for Claude Code

Global Beauty TF의 웹 QA 자동화 플러그인.
Figma/PRD 기반으로 TC 자동 생성 → Playwright 검증 → 엑셀 리포트 → Jira 티켓(스크린샷 포함)까지 한 번에 실행합니다.

## 설치

```bash
git clone https://github.com/minmk-crypto/claude-qa-plugin
claude --plugin-dir ./claude-qa-plugin
```

그다음 `/mcp`에서 Playwright 연결 확인 후 `/qa` 실행.

### 사전 조건

- **Claude Code** 설치
- **Playwright MCP** 연결 필수 (`/mcp`에서 확인)
- **Notion MCP** (선택) — PRD 자동 읽기용

## 명령어

| 명령어 | 용도 | 단독 사용 |
|--------|------|----------|
| `/qa` | **전체 플로우** — Figma/PRD 링크 주면 TC 생성 → 검증 → 리포트 → Jira | - |
| `/qa-analyze` | Figma/PRD 분석만 | O |
| `/qa-report` | 기존 결과로 엑셀 재생성 | O |
| `/qa-jira` | FAIL 건 Jira 티켓 (스크린샷 포함) | O |

## 사용법

### 전체 QA
```
/qa
```
→ Figma URL/PRD 링크 + 검증 대상 URL 질문 → TC 자동 생성 → 사용자 리뷰 → Playwright 검증 → 리포트 → "Jira에 올릴까요?"

> **TC는 Figma/PRD("어떻게 되어야 하는가")를 기준으로 생성됩니다.**
> 사이트는 TC 생성에 사용하지 않습니다 — 검증 대상일 뿐입니다.

### 분석만
```
/qa-analyze --figma [URL:TOKEN]
```

### 리포트 재생성
```
/qa-report output/reports/2026-04-09-qa-results.json
```

### Jira만 (나중에 티켓 올리기)
```
/qa-jira output/reports/2026-04-09-qa-results.json --project FP --parent FP-413
```

## 실행 중 화면

검증 진행 시 터미널에 실시간 표시:
```
📱 모바일 (390px) — peach-glow-makeup-base
  [매우높음] TC-A01~A09 검증 중...
  ✓ 9/9 PASS
  [높음] TC-B01~B36 검증 중...
  ✓ 25 PASS, ✗ 2 FAIL
📱 태블릿 (768px) — peach-glow-makeup-base
  ...
```

Playwright 도구는 사전 승인되어 있어 매번 "Yes" 누를 필요 없이 자동 실행됩니다.

## 결과물

- `output/reports/YYYY-MM-DD-qa-{페이지}.xlsx` — TC 시트 (PASS 초록/FAIL 빨강 색상 코딩)
- `output/reports/YYYY-MM-DD-qa-{페이지}.md` — 리포트
- `output/reports/YYYY-MM-DD-qa-results.json` — 결과 데이터 (리포트 재생성, Jira 등록에 재사용)
- 스크린샷 (FAIL 건 자동 캡처)

## 구조

```
claude-qa-plugin/
├── .claude-plugin/plugin.json       # name: "gb-tf"
├── README.md
└── skills/
    ├── qa/                          # /qa — 메인 오케스트레이터
    │   ├── SKILL.md
    │   └── reference/
    │       └── priority-guide.md    # 우선순위 자동 분류 기준
    ├── qa-analyze/                  # /qa-analyze — Figma/PRD 분석
    │   └── SKILL.md
    ├── qa-report/                   # /qa-report — 엑셀 + md 리포트
    │   ├── SKILL.md
    │   └── scripts/
    │       └── generate-report.py
    └── qa-jira/                     # /qa-jira — Jira 티켓 + 스크린샷
        ├── SKILL.md
        └── scripts/
            └── jira-tickets.py
```

## 업데이트

플러그인 업데이트 시:
```bash
cd claude-qa-plugin && git pull
```
다음 `claude --plugin-dir ./claude-qa-plugin` 세션부터 적용.
