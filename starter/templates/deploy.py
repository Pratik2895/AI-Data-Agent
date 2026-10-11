# Databricks notebook source
# MAGIC %pip install mlflow==3.6.0 databricks-langchain==0.3.0 langgraph==1.2.12 databricks-agents sqlglot==30.21.0 pandas==2.3.3 requests==2.34.2
# COMMAND ----------
dbutils.library.restartPython()
# COMMAND ----------
config = PROJECT_CONFIG_LITERAL
import json
import os
import sys
import time
import mlflow
from databricks import agents
from databricks.sdk import WorkspaceClient
from mlflow.models.resources import DatabricksServingEndpoint, DatabricksFunction, DatabricksSQLWarehouse, DatabricksTable
source = dbutils.widgets.get('agent_source')
endpoint = dbutils.widgets.get('endpoint_name')
prefix = f"{config['catalog']}.{config['schema']}"
model_name = prefix + '.data_agent'
env = {'CATALOG': config['catalog'], 'SCHEMA': config['schema'], 'DATABRICKS_WAREHOUSE_ID': config['warehouse_id'],
       'PROJECT_DESCRIPTION': config['description'], 'ENABLED_AGENTS': ','.join(config['agents']),
       'AGENT_TABLES': json.dumps([t['name'] for t in config['tables']]), 'ETL_ALLOWED_HOSTS': ','.join(config['allowed_hosts']),
       **{f'LLM_{k.upper()}': v for k,v in config['models'].items()}}
os.environ.update(env)
sys.path.insert(0, os.path.dirname(source))
resources = [DatabricksServingEndpoint(endpoint_name=n) for n in sorted(set(config['models'].values()))]
if set(config['agents']) & {'SQL','KNOWLEDGE'}:
    resources.append(DatabricksSQLWarehouse(warehouse_id=config['warehouse_id']))
if 'SQL' in config['agents']:
    resources.extend(DatabricksTable(table_name=f"{prefix}.{t['name']}") for t in config['tables'])
    resources.append(DatabricksFunction(function_name=prefix+'.get_schema_info'))
if 'KNOWLEDGE' in config['agents']:
    resources.extend([DatabricksTable(table_name=prefix+'.product_docs'), DatabricksFunction(function_name=prefix+'.search_product_docs')])
mlflow.set_registry_uri('databricks-uc')
with mlflow.start_run(run_name=config['name']):
    info=mlflow.pyfunc.log_model(name='agent', python_model=source, resources=resources,
        code_paths=[os.path.join(os.path.dirname(source),'runtime.py')],
        pip_requirements=['mlflow==3.6.0','databricks-langchain==0.3.0','langgraph==1.2.12','databricks-agents','sqlglot==30.21.0','pandas==2.3.3','requests==2.34.2'],
        input_example={'input':[{'role':'user','content':config['checks'][0]['question']}]}, registered_model_name=model_name)
agents.deploy(model_name, model_version=int(info.registered_model_version), endpoint_name=endpoint, scale_to_zero=True, environment_vars=env)
client=WorkspaceClient()
deadline=time.monotonic()+1800
while time.monotonic()<deadline:
    status=client.serving_endpoints.get(endpoint)
    if status.state.config_update.value == 'UPDATE_FAILED':
        raise RuntimeError('Serving update failed; inspect endpoint logs and capacity')
    if status.state.ready.value == 'READY' and status.state.config_update.value == 'NOT_UPDATING':
        entities={x.name: x for x in status.config.served_entities}
        routes=[r for r in status.config.traffic_config.routes if r.traffic_percentage]
        if len(routes)==1 and routes[0].traffic_percentage==100 and str(entities[routes[0].served_entity_name].entity_version)==str(info.registered_model_version):
            print(f'Ready: {endpoint}, version {info.registered_model_version}')
            break
        raise RuntimeError('Ready endpoint does not route 100% to the new version')
    time.sleep(20)
else:
    raise TimeoutError('Serving did not become ready in 30 minutes; inspect before retrying')
