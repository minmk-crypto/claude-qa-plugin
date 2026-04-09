---
name: qa-report
description: "QA 검증 결과 JSON을 엑셀(TC 시트) + md 리포트로 변환."
allowed-tools: Bash Read Write
argument-hint: "[results.json 경로] [--name 페이지명]"
---

# QA 리포트 생성

검증 결과 JSON을 엑셀(TC 시트) + md 리포트로 변환한다.

**사용법:**
- `/qa-report output/reports/2026-04-09-qa-results.json` — 지정 파일로 리포트
- `/qa-report` — 가장 최근 results.json을 자동 탐색
- `/qa-report --name pdp` — 파일명에 페이지명 지정

**단독 사용 가능.** 결과 JSON이 이미 있으면 리포트만 재생성할 수 있음.

---

## 실행

```bash
python3 scripts/generate-report.py \
  --input {results.json 경로} \
  --output-dir output/reports \
  --name {페이지명}
```

---

## 출력물

### 엑셀 (.xlsx)
- TC 목록 + URL×해상도 결과 매트릭스
- 셀 색상: PASS(초록), FAIL(빨강), SKIP(파랑), N/A(회색), 확인필요(주황)
- 비고 컬럼: FAIL 상세 설명

### md 리포트
- 요약: 총 TC / PASS / FAIL / SKIP
- FAIL 목록: TC ID, 우선순위, 상품, 해상도, 설명
- 스크린샷 링크

### 대화 출력
FAIL 건 요약 테이블.

---

## 입력 JSON 형식

[scripts/generate-report.py](scripts/generate-report.py) 상단 docstring 참조.
