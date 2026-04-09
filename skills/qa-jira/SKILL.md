---
name: qa-jira
description: "QA FAIL 항목을 Jira 서브태스크로 생성하고 스크린샷을 첨부한다."
allowed-tools: Bash Read Write
argument-hint: "[results.json 경로] [--project KEY] [--parent ISSUE]"
---

# QA → Jira 티켓 생성

FAIL TC를 Jira 서브태스크로 자동 생성한다. 스크린샷도 함께 첨부.

**사용법:**
- `/qa-jira output/reports/2026-04-09-qa-results.json --project FP --parent FP-413` — 지정 파일
- `/qa-jira` — 가장 최근 results.json + Jira 정보 질문

**단독 사용 가능.** 검증은 이미 끝나고 나중에 티켓만 올리고 싶을 때.

---

## 사전 조건

Jira API 접속 정보가 필요. 없으면 질문한다:
1. Jira URL (예: https://croquis.atlassian.net)
2. 이메일
3. API 토큰
4. 프로젝트 키 (예: FP)
5. 부모 이슈 키 (예: FP-413)

---

## 실행

### 미리보기 (dry-run)
```bash
python3 scripts/jira-tickets.py \
  --input {results.json} \
  --jira-url {url} --email {email} --token {token} \
  --project {key} --parent {parent} \
  --dry-run
```

### 실제 생성
```bash
python3 scripts/jira-tickets.py \
  --input {results.json} \
  --jira-url {url} --email {email} --token {token} \
  --project {key} --parent {parent}
```

---

## 동작

FAIL TC별로:
1. **서브태스크 생성** — 제목: `[QA] {시나리오}`, 우선순위 자동 매핑
2. **설명 작성** — 재현 절차 + 기대 동작 + 실제 결과 + 해상도별 재현 정보
3. **스크린샷 첨부** — results.json의 screenshots 경로에서 자동 업로드

---

## 입력 JSON

[scripts/jira-tickets.py](scripts/jira-tickets.py) 상단 docstring 참조.
`generate-report.py`와 동일한 JSON 형식.
