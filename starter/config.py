"""Validate non-secret project configuration before generating any files."""
import ipaddress
import json
import re
from urllib.parse import urlparse


def validate(config):
    c = dict(config)
    required = {'name', 'description', 'profile', 'host', 'warehouse_id', 'catalog',
                'schema', 'volume', 'mode', 'tables', 'agents', 'models', 'checks', 'allowed_hosts'}
    if set(c) != required:
        raise ValueError(f'Expected configuration fields: {sorted(required)}; missing/extra: {sorted(required ^ set(c))}')
    for key in ('name', 'description', 'profile', 'host', 'warehouse_id', 'catalog', 'schema', 'volume'):
        if not isinstance(c[key], str) or not c[key].strip() or '${' in c[key]:
            raise ValueError(f'{key} must be a nonempty literal string')
    if not re.fullmatch(r'[a-z][a-z0-9-]{2,17}', c['name']):
        raise ValueError('name must be 3–18 lowercase letters/digits/hyphens, starting with a letter')
    for key in ('catalog', 'schema', 'volume'):
        if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', c[key]):
            raise ValueError(f'{key} must be a simple SQL identifier')
    u = urlparse(c['host'])
    if u.scheme != 'https' or not u.hostname or u.username or u.password or u.path not in ('', '/') or u.query or u.fragment:
        raise ValueError('host must be a plain HTTPS workspace URL')
    if c['mode'] not in ('csv', 'existing'):
        raise ValueError('mode must be csv or existing')
    if not isinstance(c['agents'], list) or not c['agents'] or any(a not in ('SQL', 'ETL', 'KNOWLEDGE') for a in c['agents']) or len(set(c['agents'])) != len(c['agents']):
        raise ValueError('agents must contain unique SQL, ETL and/or KNOWLEDGE entries')
    if not isinstance(c['tables'], list):
        raise ValueError('tables must be a list')
    names = []
    for t in c['tables']:
        if set(t) != {'name', 'description'} or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', t['name']) or not isinstance(t['description'], str):
            raise ValueError('Each table needs a simple name and description')
        names.append(t['name'].lower())
    if len(set(names)) != len(names) or 'product_docs' in names:
        raise ValueError('Table names must be unique; product_docs is reserved for parsed documents')
    if 'SQL' in c['agents'] and not names:
        raise ValueError('SQL requires at least one table')
    if set(c['models']) != {'low', 'medium', 'high'} or not all(isinstance(v,str) and v and '${' not in v for v in c['models'].values()):
        raise ValueError('models must specify low, medium and high endpoint names')
    if not isinstance(c['allowed_hosts'], list):
        raise ValueError('allowed_hosts must be a list')
    for host in c['allowed_hosts']:
        if not isinstance(host, str) or not re.fullmatch(r'[a-z0-9][a-z0-9.-]*\.[a-z]{2,}', host) or host.endswith(('.local', '.internal')):
            raise ValueError('ETL hosts must be explicit public DNS names, without URLs or wildcards')
        try:
            ipaddress.ip_address(host)
        except ValueError:
            pass
        else:
            raise ValueError('IP addresses are not permitted in allowed_hosts')
    if 'ETL' in c['agents'] and not c['allowed_hosts']:
        raise ValueError('ETL requires an explicit API hostname allowlist')
    if not isinstance(c['checks'], list) or not c['checks']:
        raise ValueError('At least one user-defined verification check is required')
    for check in c['checks']:
        if set(check) != {'question', 'contains'} or not isinstance(check['question'], str) or not check['question'].strip() or not isinstance(check['contains'], list) or not check['contains'] or not all(isinstance(v,str) and v for v in check['contains']):
            raise ValueError('Checks require a question and nonempty expected substrings')
    return c


def read(path):
    with open(path, encoding='utf-8') as f:
        return validate(json.load(f))
