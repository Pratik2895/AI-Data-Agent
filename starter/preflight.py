"""Read-only configuration and workspace checks before deployment."""
import argparse
import json
import subprocess
from .config import read


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config', required=True)
    p.add_argument('--online', action='store_true')
    args=p.parse_args()
    c=read(args.config)
    print('Configuration valid; enabled workflows: '+', '.join(c['agents']))
    if not args.online:
        return
    from databricks.sdk import WorkspaceClient
    credentials=json.loads(subprocess.check_output(['databricks','auth','token',c['profile']],text=True))
    w=WorkspaceClient(host=c['host'],token=credentials['access_token'],auth_type='pat')
    w.current_user.me()
    w.warehouses.get(c['warehouse_id'])
    w.schemas.get(f"{c['catalog']}.{c['schema']}")
    if c['mode']=='csv' or 'KNOWLEDGE' in c['agents']:
        w.volumes.read(f"{c['catalog']}.{c['schema']}.{c['volume']}")
    if c['mode']=='existing':
        for t in c['tables']:
            w.tables.get(f"{c['catalog']}.{c['schema']}.{t['name']}")
    for endpoint in set(c['models'].values()):
        w.serving_endpoints.get(endpoint)
    print('Identity and configured resources are accessible. Create/execute privileges and serving capacity are confirmed during deployment, not by this read-only check.')

if __name__=='__main__':
    main()
