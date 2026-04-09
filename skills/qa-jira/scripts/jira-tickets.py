#!/usr/bin/env python3
"""
FAIL TC → Jira 서브태스크 생성 + 스크린샷 첨부

사용법:
  python3 jira-tickets.py \
    --input results.json \
    --jira-url https://your-org.atlassian.net \
    --email user@company.com \
    --token ATATT3x... \
    --project FP \
    --parent FP-413

입력 JSON: generate-report.py와 동일한 형식.
FAIL 항목만 추출하여 Jira 서브태스크로 생성.
"""

import json
import sys
import argparse
import base64
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

def jira_request(url, email, token, method='GET', data=None):
    auth = base64.b64encode(f'{email}:{token}'.encode()).decode()
    headers = {
        'Authorization': f'Basic {auth}',
        'Content-Type': 'application/json',
    }
    req = Request(url, headers=headers, method=method)
    if data:
        req.data = json.dumps(data).encode()
    try:
        with urlopen(req) as resp:
            return json.loads(resp.read())
    except HTTPError as e:
        body = e.read().decode()
        print(f'Jira API error {e.code}: {body}', file=sys.stderr)
        return None

def jira_upload(url, email, token, filepath):
    """Multipart file upload for Jira attachments"""
    import mimetypes
    boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
    filename = Path(filepath).name
    content_type = mimetypes.guess_type(filepath)[0] or 'application/octet-stream'

    with open(filepath, 'rb') as f:
        file_data = f.read()

    body = (
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f'Content-Type: {content_type}\r\n\r\n'
    ).encode() + file_data + f'\r\n--{boundary}--\r\n'.encode()

    auth = base64.b64encode(f'{email}:{token}'.encode()).decode()
    headers = {
        'Authorization': f'Basic {auth}',
        'Content-Type': f'multipart/form-data; boundary={boundary}',
        'X-Atlassian-Token': 'no-check',
    }
    req = Request(url, headers=headers, method='POST', data=body)
    try:
        with urlopen(req) as resp:
            return json.loads(resp.read())
    except HTTPError as e:
        print(f'Upload error {e.code}: {e.read().decode()}', file=sys.stderr)
        return None

def make_description(tc, fail_info):
    """ADF(Atlassian Document Format) description 생성"""
    content = [
        {"type": "heading", "attrs": {"level": 3}, "content": [
            {"type": "text", "text": f'{tc["id"]}: {tc["scenario"]}'}
        ]},
        {"type": "paragraph", "content": [
            {"type": "text", "text": f'카테고리: {tc["category"]} | 우선순위: {tc["priority"]}'}
        ]},
        {"type": "heading", "attrs": {"level": 4}, "content": [
            {"type": "text", "text": "동작"}
        ]},
        {"type": "paragraph", "content": [
            {"type": "text", "text": tc["action"]}
        ]},
        {"type": "heading", "attrs": {"level": 4}, "content": [
            {"type": "text", "text": "기대결과"}
        ]},
        {"type": "paragraph", "content": [
            {"type": "text", "text": tc["expected"]}
        ]},
        {"type": "heading", "attrs": {"level": 4}, "content": [
            {"type": "text", "text": "실제 결과 (FAIL)"}
        ]},
    ]

    for f in fail_info:
        content.append({"type": "paragraph", "content": [
            {"type": "text", "text": f'[{f["key"]}] {f["note"]}', "marks": [{"type": "strong"}]}
        ]})

    # 해상도 재현 정보
    viewports = list(set(f['key'].split('|')[1] if '|' in f['key'] else '' for f in fail_info))
    if viewports:
        content.append({"type": "paragraph", "content": [
            {"type": "text", "text": f'재현 해상도: {", ".join(viewports)}'}
        ]})

    return {"version": 1, "type": "doc", "content": content}

def main():
    parser = argparse.ArgumentParser(description='FAIL TC → Jira 티켓 생성')
    parser.add_argument('--input', required=True, help='결과 JSON 파일')
    parser.add_argument('--jira-url', required=True, help='Jira URL (https://org.atlassian.net)')
    parser.add_argument('--email', required=True, help='Atlassian 이메일')
    parser.add_argument('--token', required=True, help='Atlassian API 토큰')
    parser.add_argument('--project', required=True, help='프로젝트 키 (예: FP)')
    parser.add_argument('--parent', required=True, help='부모 이슈 키 (예: FP-413)')
    parser.add_argument('--dry-run', action='store_true', help='실제 생성 없이 미리보기')
    args = parser.parse_args()

    with open(args.input) as f:
        data = json.load(f)

    tcs = {tc['id']: tc for tc in data.get('tcs', [])}
    results = data.get('results', {})
    screenshots = data.get('screenshots', {})

    # FAIL 항목 수집 (TC별로 그룹화)
    fails_by_tc = {}
    for tc_id, tc_results in results.items():
        for key, r in tc_results.items():
            if r.get('status') == 'FAIL':
                if tc_id not in fails_by_tc:
                    fails_by_tc[tc_id] = []
                fails_by_tc[tc_id].append({
                    'key': key,
                    'note': r.get('note', ''),
                    'screenshot': screenshots.get(f'{tc_id}|{key}', '')
                })

    if not fails_by_tc:
        print('FAIL 항목 없음. 티켓 생성 불필요.')
        return

    print(f'FAIL {len(fails_by_tc)}개 TC → Jira 티켓 생성')

    # 우선순위 매핑
    prio_map = {'매우높음': '1', '높음': '3', '보통': '4', '낮음': '10003'}

    api_base = f'{args.jira_url}/rest/api/3/issue'
    created = []

    for tc_id, fail_info in fails_by_tc.items():
        tc = tcs.get(tc_id)
        if not tc:
            print(f'  SKIP: {tc_id} — TC 정의 미발견')
            continue

        # 제목
        summary = f'[QA] {tc["scenario"]}'
        if len(summary) > 100:
            summary = summary[:97] + '...'

        payload = {
            "fields": {
                "project": {"key": args.project},
                "parent": {"key": args.parent},
                "issuetype": {"id": "10003"},  # 하위 작업
                "summary": summary,
                "priority": {"id": prio_map.get(tc['priority'], '4')},
                "description": make_description(tc, fail_info)
            }
        }

        if args.dry_run:
            print(f'  [DRY] {tc_id} → {summary} (우선순위: {tc["priority"]})')
            for f in fail_info:
                print(f'    - {f["key"]}: {f["note"]}')
                if f['screenshot']:
                    print(f'    - screenshot: {f["screenshot"]}')
            continue

        result = jira_request(api_base, args.email, args.token, method='POST', data=payload)
        if result and 'key' in result:
            issue_key = result['key']
            print(f'  ✓ {tc_id} → {issue_key}: {summary}')
            created.append(issue_key)

            # 스크린샷 첨부
            for f in fail_info:
                if f['screenshot'] and Path(f['screenshot']).exists():
                    attach_url = f'{api_base}/{issue_key}/attachments'
                    attach_result = jira_upload(attach_url, args.email, args.token, f['screenshot'])
                    if attach_result:
                        print(f'    📎 {Path(f["screenshot"]).name} 첨부 완료')
                    else:
                        print(f'    ⚠ {Path(f["screenshot"]).name} 첨부 실패')
        else:
            print(f'  ✗ {tc_id} → 생성 실패')

    print(f'\n완료: {len(created)}개 티켓 생성')
    if created:
        print(f'티켓: {", ".join(created)}')

if __name__ == '__main__':
    main()
