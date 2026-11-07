"""Public, read-only connectivity probe. No keys, accounts or trading APIs."""
import datetime as dt
import html
import json
import os
from pathlib import Path
import time
import urllib.error
import urllib.request

ENDPOINTS = [
    ('gamma-control', 'https://gamma-api.polymarket.com/events?limit=1'),
    ('xtracker-user', 'https://xtracker.polymarket.com/api/users/elonmusk?platform=X'),
    ('xtracker-trackings', 'https://xtracker.polymarket.com/api/users/elonmusk/trackings?platform=X&activeOnly=true'),
]
ALLOWED_HEADERS = {'date', 'content-type', 'x-vercel-id', 'x-vercel-mitigated', 'cf-ray', 'retry-after', 'cache-control'}

def probe(name, url):
    start = time.time()
    row = {'name': name, 'url': url, 'requested_at': dt.datetime.now(dt.UTC).isoformat()}
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    request = urllib.request.Request(url, headers={'User-Agent': 'PostScope-Research/1.0 (public read-only)', 'Accept': 'application/json'})
    try:
        try:
            response = opener.open(request, timeout=20)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            raw = response.read(2_000_001)
            row.update(status=response.status, headers={k.lower(): v for k, v in response.headers.items() if k.lower() in ALLOWED_HEADERS})
        if len(raw)>2_000_000:
            row['error']='Response exceeds probe size limit'
        else:
            try:
                payload=json.loads(raw)
                row['json_type']=type(payload).__name__
                if isinstance(payload,dict):
                    row['success']=payload.get('success')
                    data=payload.get('data')
                    row['data_type']=type(data).__name__
                    if isinstance(data,list):row['items']=len(data)
                    if isinstance(data,dict):row['data_keys']=list(data)[:30]
                    if row['status']!=200:row['error_response']=payload
                else:
                    row['items']=len(payload) if isinstance(payload,list) else None
            except ValueError:
                row['body_preview']=raw.decode('utf-8',errors='replace')[:250]
    except Exception as error:
        row['status']=None
        row['error']=f'{type(error).__name__}: {error}'[:250]
    row['elapsed_ms']=round((time.time()-start)*1000)
    row['received_at']=dt.datetime.now(dt.UTC).isoformat()
    print(json.dumps(row,ensure_ascii=False),flush=True)
    return row

def write_report(rows):
    checks=[x for x in rows if x['name'].startswith('xtracker-')]
    ok=bool(checks) and all(x.get('status')==200 and x.get('success') is True for x in checks)
    repository=os.getenv('GITHUB_REPOSITORY','local')
    run_id=os.getenv('GITHUB_RUN_ID','')
    result={'generated_at':dt.datetime.now(dt.UTC).isoformat(),'xtracker_accessible':ok,'origin':'GitHub Actions hosted runner' if run_id else 'local verification','repository':repository,'run_id':run_id,'commit':os.getenv('GITHUB_SHA'),'checks':rows}
    output=Path('site');output.mkdir(exist_ok=True)
    (output/'report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    escape=html.escape
    cards=''.join(f'''<article><div class="row"><h2>{escape(r['name'])}</h2><span class="status">HTTP {r.get('status') or '连接失败'}</span></div><p class="url">{escape(r['url'])}</p><p>{escape(r['received_at'])} · {r['elapsed_ms']} ms</p><pre>{escape(json.dumps({k:v for k,v in r.items() if k not in ['url','name']},ensure_ascii=False,indent=2))}</pre></article>''' for r in rows)
    run_url=f'https://github.com/{repository}/actions/runs/{run_id}'
    title='XTracker 接口可访问' if ok else 'XTracker 接口未通过访问测试'
    page=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>PostScope · GitHub 出口测试</title><style>
    :root{{font:15px/1.7 system-ui,sans-serif;color:#253047;background:#f5f6f8}}*{{box-sizing:border-box}}body{{margin:0}}main{{max-width:960px;margin:50px auto;padding:0 22px}}header{{margin-bottom:30px}}small{{color:#71819b;letter-spacing:2px}}h1{{font-size:28px;margin:12px 0}}h2{{font-size:17px;margin:0}}p{{color:#708099}}.result{{padding:18px 22px;border-radius:9px;background:{'#e8f6ed' if ok else '#fff5e5'};border:1px solid {'#c5e4d0' if ok else '#ead5ae'};margin:25px 0}}article{{background:#fff;border:1px solid #e0e6ef;border-radius:10px;margin:18px 0;padding:24px}}.row{{display:flex;justify-content:space-between;gap:10px}}.status{{font-size:13px;font-weight:600}}.url{{overflow-wrap:anywhere;font-size:12px}}pre{{font:12px/1.6 ui-monospace,monospace;white-space:pre-wrap;overflow-wrap:anywhere;background:#f7f9fc;padding:16px;border-radius:6px;color:#53637c}}a{{color:#3869cf}}footer{{margin:25px 0 40px;color:#8b96a9;font-size:12px}}@media(max-width:600px){{main{{margin-top:25px}}h1{{font-size:24px}}article{{padding:17px}}}}
    </style></head><body><main><header><small>POSTSCOPE / NETWORK DIAGNOSTICS</small><h1>GitHub Actions → XTracker</h1><p>由 GitHub 托管 runner 发出公开 GET 请求，GitHub Pages 只展示静态测试结果。</p></header><section class="result"><strong>{title}</strong><div>{escape(result['generated_at'])}</div></section><p>这是一次性诊断快照，不是实时行情。工作流完成或 Pages 发布成功，不代表上游接口可用。</p><p><a href="report.json">原始 JSON</a> · <a href="{escape(run_url)}">GitHub Actions 运行记录</a></p>{cards}<footer>没有账户凭据、交易操作或自动定时任务。{escape(repository)}</footer></main></body></html>'''
    (output/'index.html').write_text(page)
    (output/'.nojekyll').touch()
    summary=os.getenv('GITHUB_STEP_SUMMARY')
    if summary:
        with open(summary,'a') as f:
            f.write(f'## {title}\n\n')
            for row in rows:f.write(f"- {row['name']}: HTTP {row.get('status')}\n")
            f.write('\nPages publication success is separate from upstream accessibility.\n')
    return result

if __name__=='__main__':
    write_report([probe(name,url) for name,url in ENDPOINTS])
