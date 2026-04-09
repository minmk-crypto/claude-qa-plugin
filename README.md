# QA Automation Plugin for Claude Code

웹 QA 자동화 플러그인. URL + Figma + PRD를 기반으로 TC를 자동 생성하고 Playwright로 검증합니다.

## 설치

```bash
claude /plugin install /path/to/claude-qa-plugin
```

또는 GitHub에서:
```bash
claude /plugin install https://github.com/your-org/claude-qa-plugin
```

## 사전 조건

- **Playwright MCP** 연결 필수. Claude Code에서 `/mcp` → Playwright 연결.
- **Notion MCP** (선택). PRD 자동 읽기용.

## 사용법

### 범용 QA
```
/qa
```
URL, Figma, PRD를 질문 받은 후 TC 생성 → 검증 → 리포트.

### URL 직접 지정
```
/qa https://example.com
```

### 프리셋 사용
```
/qa pdp
```
사전 설정된 상품/Figma/PRD로 즉시 실행. 프리셋은 `skills/qa/presets/`에 추가 가능.

## 플로우

```
인풋 수집 → 소스 분석(Figma/PRD/사이트) → TC 생성 → 사용자 리뷰 → Playwright 실행 → 리포트
```

## 결과물

- `output/reports/YYYY-MM-DD-qa-{페이지}.xlsx` — TC 시트
- `output/reports/YYYY-MM-DD-qa-{페이지}.md` — 리포트
- FAIL 건 스크린샷
- (Jira 연동 시) 자동 티켓 생성

## 프리셋 추가

`skills/qa/presets/`에 md 파일 추가:

```markdown
# 홈 프리셋
## 접속
- URL: https://example.com
## 검증 대상
| URL | 케이스 |
|---|---|
| / | 홈페이지 |
```

`/qa home`으로 실행.

## 구조

```
claude-qa-plugin/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   └── qa/
│       ├── SKILL.md           # 메인 스킬
│       ├── presets/
│       │   └── pdp.md         # PDP 프리셋
│       └── reference/
│           └── priority-guide.md
└── README.md
```
