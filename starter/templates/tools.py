# Databricks notebook source
config = PROJECT_CONFIG_LITERAL
import time
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import StatementState
client = WorkspaceClient()
prefix = f"{config['catalog']}.{config['schema']}"
def execute(sql):
    r=client.statement_execution.execute_statement(warehouse_id=config['warehouse_id'], statement=sql, wait_timeout='30s')
    deadline=time.monotonic()+120
    while r.status.state in (StatementState.PENDING, StatementState.RUNNING):
        if time.monotonic()>deadline:
            client.statement_execution.cancel_execution(r.statement_id)
            raise TimeoutError('SQL tool setup timed out')
        time.sleep(2)
        r=client.statement_execution.get_statement(r.statement_id)
    if r.status.state != StatementState.SUCCEEDED:
        raise RuntimeError(str(r.status.error))
if 'SQL' in config['agents']:
    context=[]
    for t in config['tables']:
        table=client.tables.get(f"{prefix}.{t['name']}")
        context.append(f"Table: {prefix}.{t['name']} | {t['description']} | Columns: " + ', '.join(f'{c.name} ({c.type_text})' for c in table.columns))
    literal='\n'.join(context).replace("'", "''")
    execute(f"CREATE OR REPLACE FUNCTION {prefix}.get_schema_info() RETURNS STRING LANGUAGE SQL RETURN '{literal}'")
if 'KNOWLEDGE' in config['agents']:
    execute(f"""CREATE OR REPLACE FUNCTION {prefix}.search_product_docs(query STRING)
RETURNS STRING LANGUAGE SQL RETURN (
 SELECT coalesce(nullif(concat_ws(' | ', collect_list(concat(file_name, ': ', content))), ''), 'No documentation found')
 FROM (SELECT file_name, substring(array_join(text_content, ' '), 1, 8000) AS content
 FROM {prefix}.product_docs
 WHERE exists(split(lower(query), ' '), term -> length(term)>3 AND instr(lower(concat(file_name, ' ', array_join(text_content, ' '))), term)>0)
 ORDER BY file_name LIMIT 4))""")
print('Only configured tools were created')
