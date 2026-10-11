"""Verify a generated project with user-defined checks; never changes permissions."""
import argparse
import json
import subprocess
import time
from pathlib import Path
from urllib.parse import quote


def check_answer(answer, expected):
    if not answer or any(x.casefold() not in answer.casefold() for x in expected):
        raise AssertionError(f'Answer did not contain expected values {expected!r}: {answer}')


def main():
    from databricks.sdk import WorkspaceClient
    from gradio_client import Client
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config', default='project.json')
    p.add_argument('--endpoint', required=True)
    p.add_argument('--app', required=True)
    p.add_argument('--wait-seconds', type=int, default=1800)
    p.add_argument('--output', default='verification.json')
    args=p.parse_args()
    c=json.loads(Path(args.config).read_text(encoding='utf-8'))
    credentials=json.loads(subprocess.check_output(['databricks','auth','token',c['profile']],text=True))
    w=WorkspaceClient(host=c['host'], token=credentials['access_token'], auth_type='pat')
    deadline=time.monotonic()+args.wait_seconds
    while True:
        ep=w.serving_endpoints.get(args.endpoint)
        if ep.state.config_update.value=='UPDATE_FAILED':
            raise RuntimeError('Serving update failed; inspect endpoint logs')
        if ep.state.ready.value=='READY' and ep.state.config_update.value=='NOT_UPDATING':
            break
        if time.monotonic()>=deadline:
            raise TimeoutError('Serving readiness deadline exceeded')
        time.sleep(10)
    app=w.apps.get(args.app)
    if not app.app_status or app.app_status.state.value!='RUNNING':
        raise RuntimeError('App is not running; deploy/start it before verification')
    ui=Client(app.url, headers={'Authorization':'Bearer '+credentials['access_token']},verbose=False)
    results=[]
    for check in c['checks']:
        response=w.api_client.do('POST',f'/serving-endpoints/{quote(args.endpoint,safe="")}/invocations',body={'input':[{'role':'user','content':check['question']}]})
        answer='\n'.join(p.get('text','') for item in response.get('output',[]) for p in item.get('content',[]) if p.get('type')=='output_text')
        check_answer(answer,check['contains'])
        app_answer=ui.predict(check['question'],[],api_name='/respond')
        check_answer(app_answer,check['contains'])
        results.append({'question':check['question'],'endpoint_answer':answer,'app_answer':app_answer})
    Path(args.output).write_text(json.dumps({'endpoint':args.endpoint,'checks':results},indent=2),encoding='utf-8')
    print(f'All {len(results)} configured checks passed through endpoint AND app')

if __name__=='__main__':
    main()
